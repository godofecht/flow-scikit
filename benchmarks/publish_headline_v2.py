#!/usr/bin/env python3
"""Validate and publish committed evidence artifacts into the static Pages tree."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
DOCS = ROOT / "docs"
RESULT = BENCH / "headline_result_v2.json"
ARCH = BENCH / "architecture_performance_map.json"
DISPARITY = BENCH / "disparity_report.json"
HISTORY = BENCH / "disparity_history.json"
DOC_RESULT = DOCS / "headline-result-v2.json"
DOC_ARCH = DOCS / "architecture-performance-map.json"
DOC_DISPARITY = DOCS / "disparity-report.json"
DOC_HISTORY = DOCS / "disparity-history.json"


def validate_headline(result: dict) -> None:
    counts = result["counts"]
    rows = result["rows"]
    if counts["total_rows"] != len(rows):
        raise SystemExit("headline result row count does not match counts.total_rows")
    if counts["eligible_comparisons"] != counts["flow_wins"] + counts["sklearn_wins"] + counts["ties"]:
        raise SystemExit("eligible headline count is internally inconsistent")
    if any(r.get("timing_unit") != "ms" for r in rows):
        raise SystemExit("all committed v2 rows must be milliseconds")
    if counts["parity_unresolved"] != 0 or counts["measurement_unresolved"] != 0:
        raise SystemExit("canonical public result must not contain unresolved rows")


def validate_architecture(architecture: dict, total_rows: int) -> None:
    coverage = architecture["coverage"]
    if coverage["headline_rows"] != total_rows or coverage["headline_rows_with_substrate"] != total_rows or coverage["headline_rows_with_speedup"] != total_rows:
        raise SystemExit("architecture map does not cover every canonical row")
    if not architecture.get("speedup_by_execution_substrate"):
        raise SystemExit("architecture map has no substrate/speedup aggregation")


def validate_disparity(disparity: dict, total_rows: int) -> None:
    if disparity["counts"]["rows"] != total_rows:
        raise SystemExit("disparity report does not cover every canonical row")
    if disparity["counts"]["rows_with_tracked_disparity"] <= 0:
        raise SystemExit("disparity report unexpectedly contains no tracked disparities")
    keys = {(r["algorithm"], r["dataset"], r["metric"]) for r in disparity["rows"]}
    if len(keys) != total_rows:
        raise SystemExit("disparity report row keys are incomplete or duplicated")


def validate_history(history: dict, total_rows: int) -> None:
    snapshots = history.get("snapshots", [])
    if not snapshots:
        raise SystemExit("disparity history has no snapshots")
    for snapshot in snapshots:
        if len(snapshot.get("rows", [])) != total_rows:
            raise SystemExit("disparity history snapshot does not cover every canonical row")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = json.loads(RESULT.read_text())
    architecture = json.loads(ARCH.read_text())
    validate_headline(result)
    validate_architecture(architecture, result["counts"]["total_rows"])

    disparity = json.loads(DISPARITY.read_text()) if DISPARITY.exists() else None
    history = json.loads(HISTORY.read_text()) if HISTORY.exists() else None
    if disparity is not None:
        validate_disparity(disparity, result["counts"]["total_rows"])
    elif not args.check:
        raise SystemExit("disparity_report.json must be generated before Pages publication")
    if history is not None:
        validate_history(history, result["counts"]["total_rows"])
    elif not args.check:
        raise SystemExit("disparity_history.json must be generated before Pages publication")

    if not args.check:
        shutil.copyfile(RESULT, DOC_RESULT)
        shutil.copyfile(ARCH, DOC_ARCH)
        shutil.copyfile(DISPARITY, DOC_DISPARITY)
        shutil.copyfile(HISTORY, DOC_HISTORY)
        counts = result["counts"]
        print(f"published evidence: {counts['flow_wins']}/{counts['eligible_comparisons']} Flow wins; {disparity['counts']['rows_with_tracked_disparity']} rows with tracked disparities; {len(history['snapshots'])} history snapshots")
    else:
        print("canonical benchmark, architecture, disparity, and available history evidence are internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
