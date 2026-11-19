#!/usr/bin/env python3
"""Operation rows must expose a losing operation that an estimator total hides.

Issue #489. The synthetic result below is a Flow win in total (fit 10x, predict
0.5x), which is the shape of LinearSVC Digits in the frozen headline. The
operation rows must list the loss, link its issue, and treat unresolved timings
and parity as unresolved rather than as wins.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from generate_headline_summary import summarize
from generate_operation_rows import build

BENCH = Path(__file__).resolve().parent


def headline_row(algorithm, dataset, fit_sk, fit_fl, pred_sk, pred_fl, parity="parity verified", measurement="resolved"):
    return {
        "algorithm": algorithm, "dataset": dataset, "metric": "accuracy", "timing_unit": "ms",
        "sklearn_fit_ms": fit_sk, "flow_fit_ms": fit_fl, "sklearn_pred_ms": pred_sk, "flow_pred_ms": pred_fl,
        "sklearn_fit_iqr_ms": 0.1, "flow_fit_iqr_ms": 0.1, "sklearn_pred_iqr_ms": 0.01, "flow_pred_iqr_ms": 0.01,
        "sklearn_ms": fit_sk + pred_sk, "flow_ms": fit_fl + pred_fl,
        "parity_status": parity, "measurement_status": measurement, "comparable": True, "environment_id": "env",
    }


INVENTORY = [
    {"estimator": "LinearSVC", "operation": op} for op in ("fit", "predict", "decision_function")
] + [{"estimator": "PCA", "operation": op} for op in ("fit", "transform")]


def main() -> int:
    failures = 0

    def check(name, ok):
        nonlocal failures
        print(("PASS " if ok else "FAIL ") + name)
        failures += 0 if ok else 1

    rows = [
        headline_row("LinearSVC", "digits", 200.0, 20.0, 0.10, 0.20),
        headline_row("PCA", "iris", 2.0, 1.0, 0.4, 0.2),
        headline_row("LinearSVC", "iris", 3.0, 1.0, 0.1, 0.0),
        headline_row("LinearSVC", "wine", 3.0, 1.0, 0.1, 0.05, parity="parity unresolved"),
    ]
    result = summarize(rows)
    result_bytes = json.dumps(result).encode()
    check("total hides the loss: LinearSVC digits is a total Flow win",
          next(r for r in result["rows"] if r["algorithm"] == "LinearSVC" and r["dataset"] == "digits")["classification"] == "flow win")

    doc = build(result_bytes, INVENTORY, {"LinearSVC/digits/predict": 518})
    by_id = {r["id"]: r for r in doc["rows"]}
    check("fit row is a win", by_id["LinearSVC/digits/fit"]["status"] == "flow win")
    loss = by_id["LinearSVC/digits/predict"]
    check("predict loss is listed", loss["status"] == "sklearn win" and abs(loss["speedup"] - 0.5) < 1e-9)
    check("predict loss links its issue", loss["tracking_issue"] == 518)
    check("PCA prediction stage is transform", "PCA/iris/transform" in by_id and "PCA/iris/predict" not in by_id)
    check("zero-resolution predict is unresolved, not a win", by_id["LinearSVC/iris/predict"]["status"] == "measurement unresolved")
    check("parity-unresolved row gives unresolved operations",
          by_id["LinearSVC/wine/fit"]["status"] == "parity unresolved" and not by_id["LinearSVC/wine/fit"]["prerequisites_met"])
    check("untimed decision_function is listed as not measured", by_id["LinearSVC/digits/decision_function"]["status"] == "not measured")
    check("exit criterion is false while a loss exists", doc["every_measured_operation_wins"] is False)
    check("loss without an issue is counted",
          build(result_bytes, INVENTORY, {})["counts"]["losses_without_tracking_issue"] == 1)
    check("rows carry median and IQR for both sides",
          all(loss[k] is not None for k in ("sklearn_median_ms", "flow_median_ms", "sklearn_iqr_ms", "flow_iqr_ms")))

    # The committed file must match the committed result, and a stale one must fail.
    committed = subprocess.run([sys.executable, str(BENCH / "generate_operation_rows.py"), "--check"], capture_output=True, text=True)
    check("committed operation_rows.json matches the headline result", committed.returncode == 0)
    with tempfile.TemporaryDirectory() as tmp:
        stale = Path(tmp) / "operation_rows.json"
        d = json.loads((BENCH / "operation_rows.json").read_text())
        d["rows"][0]["speedup"] = 123.0
        stale.write_text(json.dumps(d, indent=2) + "\n")
        out = subprocess.run([sys.executable, str(BENCH / "generate_operation_rows.py"), "--check", "--output", str(stale)], capture_output=True, text=True)
        check("an edited operation_rows.json is rejected", out.returncode == 1)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
