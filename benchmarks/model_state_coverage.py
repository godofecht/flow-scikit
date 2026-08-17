#!/usr/bin/env python3
"""Audit learned-state diagnostic coverage for every canonical benchmark row."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def row_key(row: dict) -> tuple[str, str, str]:
    return row["algorithm"], row["dataset"], row["metric"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headline", type=Path, default=ROOT / "headline_result_v2.json")
    parser.add_argument("--disparity", type=Path, default=ROOT / "disparity_report.json")
    parser.add_argument("--output", type=Path, default=ROOT / "model_state_coverage.json")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    headline = json.loads(args.headline.read_text())
    disparity = json.loads(args.disparity.read_text())
    disparity_by_key = {row_key(row): row for row in disparity["rows"]}

    rows = []
    for canonical in headline["rows"]:
        key = row_key(canonical)
        if key not in disparity_by_key:
            raise SystemExit(f"disparity report missing canonical row: {key}")
        state = disparity_by_key[key].get("model_state_diagnostics", {})
        rows.append({
            "algorithm": key[0],
            "dataset": key[1],
            "metric": key[2],
            "status": "covered" if state else "missing",
            "diagnostic_keys": sorted(state),
        })

    covered = sum(row["status"] == "covered" for row in rows)
    payload = {
        "schema_version": 1,
        "policy": "every canonical estimator row must eventually expose at least one learned-state diagnostic in addition to its final score",
        "counts": {
            "canonical_rows": len(rows),
            "covered_rows": covered,
            "missing_rows": len(rows) - covered,
        },
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")

    print(json.dumps(payload["counts"], sort_keys=True))
    if args.require_complete and covered != len(rows):
        missing = [f"{r['algorithm']}:{r['dataset']}:{r['metric']}" for r in rows if r["status"] == "missing"]
        print("missing learned-state diagnostics:")
        for item in missing:
            print(" -", item)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
