#!/usr/bin/env python3
"""Pin the behaviour of the disparity regression gate.

Two halves, and both matter:

* Improvements, float32 rounding and runner-to-runner variation must not fail
  the gate. Each of those cases below is a real observed CI failure.
* A genuine parity or runtime regression must still fail it. The synthetic
  slowdown and score-drift cases hold that line.
* An explicit implementation-contract change may establish a fresh baseline for
  that row, but changing a tolerance or any other gate-defining contract field
  must not create the same exemption.
"""
from __future__ import annotations

import io
import json
import contextlib
import sys
import tempfile
from pathlib import Path

import check_disparity_regression

ROOT = Path(__file__).resolve().parent
POLICY = ROOT / "disparity_regression_policy.json"


def row(algorithm="Ridge", dataset="diabetes", metric="r2", score_abs_diff=1.79e-07,
        tolerance=0.02, runtime_log2_ratio=0.9271, config=0, semantic=0):
    return {
        "algorithm": algorithm,
        "dataset": dataset,
        "metric": metric,
        "score_abs_diff": score_abs_diff,
        "declared_score_tolerance": tolerance,
        "effective_score_tolerance": tolerance,
        "score_tolerance_fraction": score_abs_diff / tolerance,
        "runtime_log2_ratio": runtime_log2_ratio,
        "configuration_differences": [{"parameter": f"p{i}"} for i in range(config)],
        "semantic_differences": [{"dimension": f"d{i}"} for i in range(semantic)],
    }


def report(rows, environment_id="env", runtime_environment_id="host-a"):
    return {
        "schema_version": 4,
        "environment_id": environment_id,
        "runtime_environment_id": runtime_environment_id,
        "counts": {"rows": len(rows)},
        "rows": rows,
    }


def contract_row(algorithm="Ridge", dataset="diabetes", metric="r2", tolerance=0.02,
                 flow=None, sklearn=None, parity_level="approximate", timing_comparable=True):
    return {
        "algorithm": algorithm,
        "dataset": dataset,
        "metric": metric,
        "category": "supervised",
        "parity_level": parity_level,
        "score_abs_tolerance": tolerance,
        "timing_comparable": timing_comparable,
        "flow": flow if flow is not None else {"solver": "old"},
        "sklearn": sklearn if sklearn is not None else {"solver": "reference"},
    }


def contract(rows):
    return {"schema_version": 1, "rows": rows}


def run_gate(baseline, current, baseline_contract=None, current_contract=None):
    """Return (exit_code, stdout) for one baseline/current pair."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "baseline.json").write_text(json.dumps(baseline))
        (tmp / "current.json").write_text(json.dumps(current))
        argv = sys.argv
        sys.argv = [
            "check_disparity_regression.py",
            "--current", str(tmp / "current.json"),
            "--baseline", str(tmp / "baseline.json"),
            "--history", str(tmp / "history.json"),
            "--policy", str(POLICY),
            "--commit", "fixture",
        ]
        if baseline_contract is not None and current_contract is not None:
            (tmp / "baseline-contract.json").write_text(json.dumps(baseline_contract))
            (tmp / "current-contract.json").write_text(json.dumps(current_contract))
            sys.argv.extend([
                "--baseline-contract", str(tmp / "baseline-contract.json"),
                "--current-contract", str(tmp / "current-contract.json"),
            ])
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                code = check_disparity_regression.main()
        finally:
            sys.argv = argv
        return code, buffer.getvalue()


def expect_pass(name, baseline, current, must_contain=None, baseline_contract=None, current_contract=None):
    code, out = run_gate(baseline, current, baseline_contract, current_contract)
    assert code == 0, f"{name}: expected pass, gate failed:\n{out}"
    if must_contain:
        assert must_contain in out, f"{name}: expected {must_contain!r} in output:\n{out}"
    print(f"  pass  {name}")


def expect_fail(name, baseline, current, must_contain=None, baseline_contract=None, current_contract=None):
    code, out = run_gate(baseline, current, baseline_contract, current_contract)
    assert code == 1, f"{name}: expected failure, gate passed:\n{out}"
    if must_contain:
        assert must_contain in out, f"{name}: expected {must_contain!r} in output:\n{out}"
    print(f"  fail  {name}")


def main():
    print("improvements must not fail the gate (issue #351)")
    for name, old_rt, new_rt in (
        ("PR #345 KMeans digits 31.1x slower -> 6.5x slower", -4.9603, -2.6996),
        ("PR #350 PCA 4.8x faster -> 9.6x faster", 2.2513, 3.2666),
        ("PR #347 LogisticRegression 2.1x fit speedup", 1.0785, 2.1566),
        ("PR #376 LinearRegression 2.58x faster -> 9.47x faster", 1.3671, 3.2443),
    ):
        expect_pass(
            name,
            report([row(runtime_log2_ratio=old_rt)]),
            report([row(runtime_log2_ratio=new_rt)]),
            must_contain="improved",
        )

    print("float32 rounding must not fail the gate (issue #373)")
    expect_pass(
        "Ridge/diabetes 1.79e-07 -> 4.77e-07",
        report([row(score_abs_diff=1.79e-07)]),
        report([row(score_abs_diff=4.77e-07)]),
    )
    expect_pass(
        "LinearRegression/diabetes 1.19e-07 -> 1.79e-07",
        report([row(algorithm="LinearRegression", score_abs_diff=1.19e-07, tolerance=0.005)]),
        report([row(algorithm="LinearRegression", score_abs_diff=1.79e-07, tolerance=0.005)]),
    )

    print("runner-to-runner variation must not fail the gate (issue #373)")
    expect_pass(
        "LogisticRegression/digits 3.30 log2 swing on a different host",
        report([row(algorithm="LogisticRegression", runtime_log2_ratio=1.0785)], runtime_environment_id="host-a"),
        report([row(algorithm="LogisticRegression", runtime_log2_ratio=-2.2255)], runtime_environment_id="host-b"),
    )
    expect_pass(
        "an unidentified host falls back to the cross-host threshold",
        report([row(runtime_log2_ratio=0.9271)], runtime_environment_id=None),
        report([row(runtime_log2_ratio=-3.0)], runtime_environment_id="host-b"),
        must_contain="different measurement host",
    )
    expect_pass(
        "a different software stack skips the runtime rule entirely",
        report([row(runtime_log2_ratio=0.9271)], environment_id="sklearn-1.9"),
        report([row(runtime_log2_ratio=-9.0)], environment_id="sklearn-2.0"),
        must_contain="runtime comparison skipped",
    )

    print("declared implementation changes may establish a fresh row baseline")
    old_lr = contract_row(
        algorithm="LogisticRegression", dataset="digits",
        flow={"optimizer": "lbfgs_no_line_search", "multiclass": "native"},
        sklearn={"optimizer": "lbfgs", "multiclass": "native"},
    )
    new_lr = contract_row(
        algorithm="LogisticRegression", dataset="digits",
        flow={"optimizer": "lbfgs_no_line_search", "multiclass": "multinomial_softmax"},
        sklearn={"optimizer": "lbfgs", "multiclass": "multinomial_softmax"},
    )
    expect_pass(
        "PR #434 multinomial contract resets its old score/runtime diagnostics",
        report([row(algorithm="LogisticRegression", dataset="digits", score_abs_diff=1.3e-08,
                    runtime_log2_ratio=2.5127)], runtime_environment_id="host-a"),
        report([row(algorithm="LogisticRegression", dataset="digits", score_abs_diff=0.0027778,
                    runtime_log2_ratio=-1.9765)], runtime_environment_id="host-b"),
        must_contain="fresh disparity baseline",
        baseline_contract=contract([old_lr]),
        current_contract=contract([new_lr]),
    )
    widened_lr = dict(new_lr)
    widened_lr["score_abs_tolerance"] = 0.03
    expect_fail(
        "changing implementation and widening tolerance does not reset the gate",
        report([row(algorithm="LogisticRegression", dataset="digits", score_abs_diff=1.3e-08,
                    runtime_log2_ratio=2.5127)], runtime_environment_id="host-a"),
        report([row(algorithm="LogisticRegression", dataset="digits", score_abs_diff=0.0027778,
                    runtime_log2_ratio=-1.9765)], runtime_environment_id="host-b"),
        must_contain="score |delta| regressed",
        baseline_contract=contract([old_lr]),
        current_contract=contract([widened_lr]),
    )
    expect_fail(
        "a reset on one row does not exempt an unrelated regression",
        report([
            row(algorithm="LogisticRegression", dataset="digits", score_abs_diff=1.3e-08, runtime_log2_ratio=2.5127),
            row(algorithm="Ridge", dataset="diabetes", runtime_log2_ratio=0.9271),
        ]),
        report([
            row(algorithm="LogisticRegression", dataset="digits", score_abs_diff=0.0027778, runtime_log2_ratio=-1.9765),
            row(algorithm="Ridge", dataset="diabetes", runtime_log2_ratio=-0.4),
        ]),
        must_contain="runtime log2 ratio regressed",
        baseline_contract=contract([old_lr, contract_row()]),
        current_contract=contract([new_lr, contract_row()]),
    )

    print("genuine regressions must still fail the gate")
    expect_fail(
        "2.5x runtime slowdown on the same host",
        report([row(runtime_log2_ratio=0.9271)]),
        report([row(runtime_log2_ratio=-0.4)]),
        must_contain="runtime log2 ratio regressed",
    )
    expect_fail(
        "BLAS dispatch regression: 25x slower on the same host",
        report([row(algorithm="KMeans", dataset="digits", runtime_log2_ratio=-2.6996)]),
        report([row(algorithm="KMeans", dataset="digits", runtime_log2_ratio=-7.3)]),
        must_contain="runtime log2 ratio regressed",
    )
    expect_fail(
        "catastrophic slowdown is caught even across hosts",
        report([row(runtime_log2_ratio=0.9271)], runtime_environment_id="host-a"),
        report([row(runtime_log2_ratio=-3.5)], runtime_environment_id="host-b"),
        must_contain="runtime log2 ratio regressed",
    )
    expect_fail(
        "score delta drifts to 1% of the contract tolerance",
        report([row(score_abs_diff=1.79e-07)]),
        report([row(score_abs_diff=2.1e-04)]),
        must_contain="score |delta| regressed",
    )
    expect_fail(
        "score delta grows by half on a row that is already material",
        report([row(algorithm="DecisionTree", dataset="digits", score_abs_diff=0.0194444, tolerance=0.04)]),
        report([row(algorithm="DecisionTree", dataset="digits", score_abs_diff=0.03, tolerance=0.04)]),
        must_contain="score |delta| regressed",
    )
    expect_fail(
        "tolerance fraction jumps by more than 0.1",
        report([row(score_abs_diff=0.001, tolerance=0.02)]),
        report([row(score_abs_diff=0.005, tolerance=0.02)]),
        must_contain="tolerance fraction regressed",
    )
    expect_fail(
        "a new configuration difference appears",
        report([row(config=0)]),
        report([row(config=1)]),
        must_contain="configuration_differences increased",
    )
    expect_fail(
        "a new semantic difference appears",
        report([row(semantic=0)]),
        report([row(semantic=1)]),
        must_contain="semantic_differences increased",
    )

    print("disparity regression policy fixtures: PASS")


if __name__ == "__main__":
    main()
