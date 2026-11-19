#!/usr/bin/env python3
"""Pin which headline stage the optimization roadmap reads for each operation.

Issue #481: the roadmap gave every operation of an estimator the same
end-to-end speedup, so a slow fit showed up as a slow ``predict``. These checks
hold three things:

* ``fit`` reads the fit stage, and ``predict``, ``predict_proba``,
  ``decision_function`` and ``transform`` read the prediction stage.
* A row that is not parity-eligible contributes to no stage.
* A stage with no resolved timing yields no evidence. A prediction too fast
  for the clock records 0 ms and must never read as an infinite speedup.

The last check runs the generator on the committed inputs and confirms the
``SVC.predict`` row carries the prediction-stage ratio of the two KernelSVC
headline rows.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from rank_optimization_opportunities import (
    BASIS_FIT,
    BASIS_PREDICT,
    collect_speedups,
    observed_speedup,
    operation_basis,
)

BENCH = Path(__file__).resolve().parent
FAILURES: list[str] = []


def check(name: str, actual, expected) -> None:
    if actual == expected:
        print(f"  ok   {name}")
        return
    FAILURES.append(name)
    print(f"  FAIL {name}\n         expected {expected!r}\n         actual   {actual!r}")


def close(name: str, actual, expected, tolerance: float = 1e-12) -> None:
    if actual is not None and abs(actual - expected) <= tolerance * max(1.0, abs(expected)):
        print(f"  ok   {name}")
        return
    FAILURES.append(name)
    print(f"  FAIL {name}\n         expected {expected!r}\n         actual   {actual!r}")


def row(algorithm, sk_fit, fl_fit, sk_pred, fl_pred, parity="approximately equivalent"):
    return {
        "algorithm": algorithm,
        "parity_status": parity,
        "sklearn_fit_ms": sk_fit,
        "flow_fit_ms": fl_fit,
        "sklearn_pred_ms": sk_pred,
        "flow_pred_ms": fl_pred,
    }


def main() -> int:
    print("operation to stage")
    check("fit reads the fit stage", operation_basis("fit"), BASIS_FIT)
    for operation in ("predict", "predict_proba", "decision_function", "transform"):
        check(f"{operation} reads the prediction stage", operation_basis(operation), BASIS_PREDICT)
    check("an unknown operation has no stage", operation_basis("score"), None)

    print("stage separation")
    # Fit loses at 0.5x and prediction wins at 4x. End to end is 0.55x.
    rows = [row("KernelSVC_RBF", 10.0, 20.0, 4.0, 1.0)]
    speed = collect_speedups(rows)
    value, basis = observed_speedup(speed, "SVC", "predict")
    close("predict takes the prediction-stage ratio", value, 4.0)
    check("predict names its basis", basis, BASIS_PREDICT)
    value, basis = observed_speedup(speed, "SVC", "fit")
    close("fit takes the fit-stage ratio", value, 0.5)
    check("fit names its basis", basis, BASIS_FIT)
    close("end to end is kept separately", speed["SVC"]["end to end"][0], 14.0 / 21.0)
    value, _ = observed_speedup(speed, "SVC", "decision_function")
    close("decision_function takes the prediction-stage ratio", value, 4.0)

    print("averaging across datasets")
    rows = [
        row("KernelSVC_RBF", 10.0, 20.0, 4.0, 1.0),
        row("KernelSVC_RBF", 30.0, 10.0, 6.0, 3.0),
    ]
    speed = collect_speedups(rows)
    close("predict is the mean of the prediction-stage ratios", observed_speedup(speed, "SVC", "predict")[0], 3.0)
    close("fit is the mean of the fit-stage ratios", observed_speedup(speed, "SVC", "fit")[0], 1.75)

    print("rows that carry no evidence")
    speed = collect_speedups([row("KernelSVC_RBF", 10.0, 20.0, 4.0, 1.0, parity="parity unresolved")])
    check("a parity-unresolved row is ignored", observed_speedup(speed, "SVC", "predict"), (None, None))
    # A prediction faster than the clock resolution is recorded as 0 ms.
    speed = collect_speedups([row("LinearRegression", 1.0, 0.5, 0.02, 0.0)])
    check("an unresolved prediction stage yields no predict evidence", observed_speedup(speed, "LinearRegression", "predict"), (None, None))
    close("its fit stage is still read", observed_speedup(speed, "LinearRegression", "fit")[0], 2.0)
    check("an estimator outside the headline has no evidence", observed_speedup(speed, "Birch", "predict"), (None, None))

    print("generator on the committed inputs")
    headline = json.loads((BENCH / "headline_result_v2.json").read_text())
    ksvc = [r for r in headline["rows"] if r["algorithm"] == "KernelSVC_RBF"]
    expected_predict = sum(r["sklearn_pred_ms"] / r["flow_pred_ms"] for r in ksvc) / len(ksvc)
    expected_fit = sum(r["sklearn_fit_ms"] / r["flow_fit_ms"] for r in ksvc) / len(ksvc)
    with tempfile.TemporaryDirectory() as tmp:
        out_json = Path(tmp) / "roadmap.json"
        out_md = Path(tmp) / "ROADMAP.md"
        subprocess.run(
            [sys.executable, str(BENCH / "rank_optimization_opportunities.py"), "--json", str(out_json), "--markdown", str(out_md)],
            check=True, stdout=subprocess.DEVNULL,
        )
        generated = {(r["estimator"], r["operation"]): r for r in json.loads(out_json.read_text())["rows"]}
        markdown = out_md.read_text()
    check("two KernelSVC headline rows feed the check", len(ksvc), 2)
    close("SVC.predict carries the prediction-stage mean", generated[("SVC", "predict")]["observed_flow_speedup"], expected_predict, 1e-9)
    check("SVC.predict names its basis", generated[("SVC", "predict")]["observed_flow_speedup_basis"], BASIS_PREDICT)
    close("SVC.fit carries the fit-stage mean", generated[("SVC", "fit")]["observed_flow_speedup"], expected_fit, 1e-9)
    check("the two stages are different numbers", generated[("SVC", "predict")]["observed_flow_speedup"] != generated[("SVC", "fit")]["observed_flow_speedup"], True)
    check("the markdown table has a Basis column", "| Basis |" in markdown, True)

    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed")
        return 1
    print("\nall roadmap stage checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
