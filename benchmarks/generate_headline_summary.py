#!/usr/bin/env python3
"""Generate a benchmark headline summary from machine-readable rows.

Input is a JSON array. Each row should include:
  algorithm, dataset, flow_ms, sklearn_ms, timing_unit,
  parity_status, measurement_status

Optional fields:
  comparable (default true), failure_reason, environment_id

Rows are eligible only when comparable, measured, in milliseconds, parity is
verified/approximately equivalent, and both runtimes are positive. Eligible
rows within TIE_RELATIVE_THRESHOLD are classified as ties.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TIE_RELATIVE_THRESHOLD = 0.02
ELIGIBLE_PARITY = {"parity verified", "approximately equivalent"}


def classify(row: dict) -> str:
    if row.get("failure_reason"):
        return "failed"
    if not row.get("comparable", True):
        return "not comparable"
    if row.get("timing_unit") != "ms":
        return "measurement unresolved"
    if row.get("measurement_status") != "resolved":
        return "measurement unresolved"
    if row.get("parity_status") not in ELIGIBLE_PARITY:
        return "parity unresolved"

    flow_ms = float(row.get("flow_ms", 0.0))
    sklearn_ms = float(row.get("sklearn_ms", 0.0))
    if flow_ms <= 0.0 or sklearn_ms <= 0.0:
        return "measurement unresolved"

    relative_gap = abs(flow_ms - sklearn_ms) / max(flow_ms, sklearn_ms)
    if relative_gap <= TIE_RELATIVE_THRESHOLD:
        return "tie"
    return "flow win" if flow_ms < sklearn_ms else "sklearn win"


def summarize(rows: list[dict]) -> dict:
    counts = {
        "total_rows": len(rows),
        "eligible_comparisons": 0,
        "flow_wins": 0,
        "sklearn_wins": 0,
        "ties": 0,
        "parity_unresolved": 0,
        "measurement_unresolved": 0,
        "not_comparable": 0,
        "failed": 0,
    }
    classified = []

    for row in rows:
        status = classify(row)
        out = dict(row)
        out["classification"] = status
        if status in {"flow win", "sklearn win", "tie"}:
            counts["eligible_comparisons"] += 1
            if status == "flow win":
                counts["flow_wins"] += 1
            elif status == "sklearn win":
                counts["sklearn_wins"] += 1
            else:
                counts["ties"] += 1
            out["speedup"] = float(row["sklearn_ms"]) / float(row["flow_ms"])
        elif status == "parity unresolved":
            counts["parity_unresolved"] += 1
        elif status == "measurement unresolved":
            counts["measurement_unresolved"] += 1
        elif status == "not comparable":
            counts["not_comparable"] += 1
        elif status == "failed":
            counts["failed"] += 1
        classified.append(out)

    return {
        "schema_version": 1,
        "timing_unit": "ms",
        "tie_relative_threshold": TIE_RELATIVE_THRESHOLD,
        "environment_id": next((r.get("environment_id") for r in rows if r.get("environment_id")), None),
        "counts": counts,
        "rows": classified,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("benchmarks/headline_summary.json"))
    args = parser.parse_args()

    rows = json.loads(args.input.read_text())
    if not isinstance(rows, list):
        raise SystemExit("input must be a JSON array")

    summary = summarize(rows)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    c = summary["counts"]
    print(
        f"{c['flow_wins']} Flow wins / {c['eligible_comparisons']} eligible "
        f"({c['total_rows']} total; {c['ties']} ties; "
        f"{c['parity_unresolved']} parity unresolved; "
        f"{c['measurement_unresolved']} measurement unresolved)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
