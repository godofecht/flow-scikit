#!/usr/bin/env python3
"""Write one row per estimator operation from the canonical headline result.

headline_result_v2.json classifies an estimator and dataset from fit plus
prediction time. A total can be a Flow win while one of its operations loses,
so this file lists each timed operation on its own: median, IQR, speedup and
status for both implementations. Totals stay in the headline result as the
secondary view.

Timed operations: `fit` for every row, and the prediction stage, which is
`predict` for every estimator except PCA where it is `transform`.
`predict_proba` and `decision_function` (and `transform` or `predict` where an
estimator has both) are not timed by the headline benchmark. They are listed
with status "not measured" so no operation of a benchmarked estimator is
silently absent.

An operation row is eligible when the headline row's parity status is eligible.
The prediction stage is timed on the model that each implementation fitted in
the same process, so it needs the fit state to be parity-eligible too, and the
one parity status covers both.

Each operation that loses carries a tracking issue from
operation_loss_issues.json. `--check` fails when the committed file differs
from what the committed headline result produces.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from generate_headline_summary import ELIGIBLE_PARITY, TIE_RELATIVE_THRESHOLD
from rank_optimization_opportunities import HEADLINE_TO_SKLEARN

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
UNTIMED_OPERATIONS = ("predict", "transform", "predict_proba", "decision_function")
UNTIMED_REASON = "not timed separately by the headline benchmark; shares the prediction stage kernel"


def prediction_operation(algorithm: str) -> str:
    return "transform" if algorithm == "PCA" else "predict"


def status_of(row: dict, sklearn_ms, flow_ms) -> tuple[str, float | None]:
    if row.get("parity_status") not in ELIGIBLE_PARITY:
        return "parity unresolved", None
    sk = float(sklearn_ms or 0.0)
    fl = float(flow_ms or 0.0)
    if row.get("measurement_status") != "resolved" or sk <= 0.0 or fl <= 0.0:
        return "measurement unresolved", None
    speedup = sk / fl
    if abs(sk - fl) / max(sk, fl) <= TIE_RELATIVE_THRESHOLD:
        return "tie", speedup
    return ("flow win" if fl < sk else "sklearn win"), speedup


def build(result_bytes: bytes, inventory: list[dict], issues: dict[str, int]) -> dict:
    result = json.loads(result_bytes)
    rows: list[dict] = []
    for h in result["rows"]:
        algorithm, dataset = h["algorithm"], h["dataset"]
        estimator = HEADLINE_TO_SKLEARN.get(algorithm, algorithm)
        timed = (
            ("fit", "fit", "sklearn_fit_ms", "flow_fit_ms", "sklearn_fit_iqr_ms", "flow_fit_iqr_ms"),
            (prediction_operation(algorithm), "prediction", "sklearn_pred_ms", "flow_pred_ms",
             "sklearn_pred_iqr_ms", "flow_pred_iqr_ms"),
        )
        for operation, stage, sk_key, fl_key, sk_iqr, fl_iqr in timed:
            status, speedup = status_of(h, h.get(sk_key), h.get(fl_key))
            key = f"{algorithm}/{dataset}/{operation}"
            rows.append({
                "id": key,
                "algorithm": algorithm,
                "sklearn_estimator": estimator,
                "dataset": dataset,
                "operation": operation,
                "stage": stage,
                "sklearn_median_ms": h.get(sk_key),
                "flow_median_ms": h.get(fl_key),
                "sklearn_iqr_ms": h.get(sk_iqr),
                "flow_iqr_ms": h.get(fl_iqr),
                "speedup": speedup,
                "status": status,
                "parity_status": h.get("parity_status"),
                "prerequisites_met": h.get("parity_status") in ELIGIBLE_PARITY and h.get("measurement_status") == "resolved",
                "tracking_issue": issues.get(key) if status == "sklearn win" else None,
            })
        timed_ops = {r["operation"] for r in rows if r["algorithm"] == algorithm and r["dataset"] == dataset}
        available = {r["operation"] for r in inventory if r["estimator"] == estimator}
        for operation in UNTIMED_OPERATIONS:
            if operation in available and operation not in timed_ops:
                rows.append({
                    "id": f"{algorithm}/{dataset}/{operation}",
                    "algorithm": algorithm,
                    "sklearn_estimator": estimator,
                    "dataset": dataset,
                    "operation": operation,
                    "stage": "prediction",
                    "sklearn_median_ms": None,
                    "flow_median_ms": None,
                    "sklearn_iqr_ms": None,
                    "flow_iqr_ms": None,
                    "speedup": None,
                    "status": "not measured",
                    "parity_status": h.get("parity_status"),
                    "prerequisites_met": False,
                    "tracking_issue": None,
                    "note": UNTIMED_REASON,
                })

    measured = [r for r in rows if r["status"] != "not measured"]
    by_status = {s: sum(r["status"] == s for r in rows) for s in
                 ("flow win", "sklearn win", "tie", "parity unresolved", "measurement unresolved", "not measured")}
    losses = [r for r in rows if r["status"] == "sklearn win"]
    by_operation: dict[str, dict] = {}
    for r in rows:
        c = by_operation.setdefault(r["operation"], {"rows": 0, "flow_wins": 0, "sklearn_wins": 0, "ties": 0, "not_measured": 0})
        c["rows"] += 1
        c["flow_wins"] += r["status"] == "flow win"
        c["sklearn_wins"] += r["status"] == "sklearn win"
        c["ties"] += r["status"] == "tie"
        c["not_measured"] += r["status"] == "not measured"
    counts = {
        "operation_rows": len(rows),
        "measured_operations": len(measured),
        "flow_wins": by_status["flow win"],
        "sklearn_wins": by_status["sklearn win"],
        "ties": by_status["tie"],
        "parity_unresolved": by_status["parity unresolved"],
        "measurement_unresolved": by_status["measurement unresolved"],
        "not_measured": by_status["not measured"],
        "losses_without_tracking_issue": sum(r["tracking_issue"] is None for r in losses),
        "by_operation": by_operation,
    }
    return {
        "schema_version": 1,
        "timing_unit": "ms",
        "tie_relative_threshold": TIE_RELATIVE_THRESHOLD,
        "source_result_sha256": hashlib.sha256(result_bytes).hexdigest(),
        "environment_id": result.get("environment_id"),
        "exit_criterion": "every measured operation row is a Flow win; totals do not count",
        "every_measured_operation_wins": bool(measured) and len(measured) == by_status["flow win"],
        "counts": counts,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", type=Path, default=BENCH / "headline_result_v2.json")
    ap.add_argument("--inventory", type=Path, default=BENCH / "sklearn_execution_inventory.json")
    ap.add_argument("--issues", type=Path, default=BENCH / "operation_loss_issues.json")
    ap.add_argument("--output", type=Path, default=BENCH / "operation_rows.json")
    ap.add_argument("--check", action="store_true", help="fail when the committed output differs from a fresh build")
    args = ap.parse_args()

    inventory = json.loads(args.inventory.read_text())["rows"]
    issues = json.loads(args.issues.read_text())["issues"]
    doc = build(args.result.read_bytes(), inventory, issues)
    text = json.dumps(doc, indent=2) + "\n"
    c = doc["counts"]
    if args.check:
        if not args.output.exists() or args.output.read_text() != text:
            print(f"{args.output.name} does not match {args.result.name}. Run: python benchmarks/generate_operation_rows.py")
            return 1
        print(f"operation rows match the headline result: {c['flow_wins']} wins, {c['sklearn_wins']} losses, "
              f"{c['ties']} ties over {c['measured_operations']} measured operations")
        return 0
    args.output.write_text(text)
    print(f"{c['flow_wins']} wins, {c['sklearn_wins']} losses, {c['ties']} ties over {c['measured_operations']} measured "
          f"operations; {c['not_measured']} untimed; {c['losses_without_tracking_issue']} losses without an issue")
    return 0


if __name__ == "__main__":
    sys.exit(main())
