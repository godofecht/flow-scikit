#!/usr/bin/env python3
"""Validate and publish committed evidence artifacts into the static Pages tree.

The public site renders the committed JSON directly.  This keeps benchmark and
architecture presentation mechanically coupled to the repository source of
truth instead of patching historical hard-coded HTML.
"""
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
DOC_RESULT = DOCS / "headline-result-v2.json"
DOC_ARCH = DOCS / "architecture-performance-map.json"


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
    if coverage["headline_rows"] != total_rows:
        raise SystemExit("architecture map headline coverage disagrees with canonical result")
    if coverage["headline_rows_with_substrate"] != total_rows:
        raise SystemExit("not every headline row has an execution-substrate classification")
    if coverage["headline_rows_with_speedup"] != total_rows:
        raise SystemExit("not every headline row joins to benchmark speedup evidence")
    if not architecture.get("speedup_by_execution_substrate"):
        raise SystemExit("architecture map has no substrate/speedup aggregation")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = json.loads(RESULT.read_text())
    architecture = json.loads(ARCH.read_text())
    validate_headline(result)
    validate_architecture(architecture, result["counts"]["total_rows"])

    if not args.check:
        shutil.copyfile(RESULT, DOC_RESULT)
        shutil.copyfile(ARCH, DOC_ARCH)
        counts = result["counts"]
        print(
            "published evidence: "
            f"{counts['flow_wins']}/{counts['eligible_comparisons']} Flow wins; "
            f"{counts['parity_unresolved']} parity unresolved; "
            f"{architecture['coverage']['inventory_operations']} estimator-operation inventory rows"
        )
    else:
        print("canonical benchmark and architecture evidence are internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
