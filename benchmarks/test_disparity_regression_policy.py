#!/usr/bin/env python3
"""Pin the behaviour of the disparity regression gate.

Two halves, and both matter:

* Improvements, float32 rounding and runner-to-runner variation must not fail
  the gate. Each of those cases below is a real observed CI failure.
* A genuine parity or runtime regression must still fail it. The synthetic
  slowdown and score-drift cases hold that line.
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
        "schema_version": 3,
        "environment_id": environment_id,
        "runtime_environment_id": runtime_environment_id,
        "counts": {"rows": len(rows)},
        "rows": rows,
    }


def run_gate(baseline, current):
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
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                code = check_disparity_regression.main()
        finally:
            sys.argv = argv
        return code, buffer.getvalue()


def expect_pass(name, baseline, current, must_contain=None):
    code, out = run_gate(baseline, current)
    assert code == 0, f"{name}: expected pass, gate failed:\n{out}"
    if must_contain:
        assert must_contain in out, f"{name}: expected {must_contain!r} in output:\n{out}"
    print(f"  pass  {name}")


def expect_fail(name, baseline, current, must_contain=None):
    code, out = run_gate(baseline, current)
    assert code == 1, f"{name}: expected failure, gate passed:\n{out}"
    if must_contain:
        assert must_contain in out, f"{name}: expected {must_contain!r} in output:\n{out}"
    print(f"  fail  {name}")


def main():
    print("improvements must not fail the gate (issue #351)")
    # Every case here is a real speedup that failed the old symmetric rule.
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
    # Observed on identical code across GitHub runners: the score delta moves by
    # ~10 float32 ulps while staying 5 orders of magnitude inside the contract.
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
    # 3.30 log2 units is the largest swing observed between runner machines on
    # unchanged code (LogisticRegression/digits, 1.0785 -> -2.2255).
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
