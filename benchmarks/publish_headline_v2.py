#!/usr/bin/env python3
"""Publish the committed v2 benchmark result into the static benchmark site.

This intentionally rewrites generated presentation text at deploy time so the
site headline cannot drift from benchmarks/headline_result_v2.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "benchmarks" / "headline_result_v2.json"
HTML = ROOT / "docs" / "benchmarks.html"
DOC_JSON = ROOT / "docs" / "headline-result-v2.json"

OLD_CARD = '<article class="result-card flow"><span class="label">headline timing wins</span><span class="value">10 / 17</span><p>Flow is faster where the stored Python timing has non-zero millisecond resolution.</p></article>'
OLD_TIMING_PARAGRAPH = '<p>All values below are milliseconds. After converting Python\'s <code>perf_counter()</code> seconds correctly, Flow is faster on 10 of the 17 headline comparisons whose stored Python timing is non-zero at the captured resolution. Python remains faster on several heavier digits workloads, while Flow is substantially faster on multiple small and direct-solver paths.</p>'
OLD_AUDIT = '<strong>Timing-unit audit:</strong> Python uses <code>time.perf_counter()</code>, which returns seconds; Flow\'s\n          benchmark already emits milliseconds. Earlier page data copied the Python second values into fields labelled\n          “ms”. The report now converts Python durations by 1000 before every timing and speedup comparison.'


def generated_strings(result: dict) -> tuple[str, str, str]:
    counts = result["counts"]
    wins = counts["flow_wins"]
    eligible = counts["eligible_comparisons"]
    total = counts["total_rows"]
    unresolved = counts["parity_unresolved"]
    card = (
        '<article class="result-card flow"><span class="label">headline timing wins</span>'
        f'<span class="value">{wins} / {eligible}</span><p>Parity-gated wins from {total} total rows; '
        f'{unresolved} rows are excluded because parity is unresolved.</p></article>'
    )
    paragraph = (
        '<p>All values below are milliseconds. The canonical v2 benchmark contains '
        f'{total} rows; {eligible} currently satisfy the explicit parity and measurement contract. '
        f'Flow wins {wins} of those {eligible} eligible comparisons. The remaining '
        f'{unresolved} rows stay visible but do not contribute to the competitive headline because parity is unresolved.</p>'
    )
    audit = (
        '<strong>Timing-unit audit:</strong> Canonical v2 benchmark artifacts declare '
        '<code>TIMING_UNIT|ms</code> on both sides and are rejected by the comparator if the unit differs. '
        'Legacy second-valued page data is retained only for historical audit; it is not the source of the v2 headline.'
    )
    return card, paragraph, audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = json.loads(RESULT.read_text())
    counts = result["counts"]
    if counts["total_rows"] != len(result["rows"]):
        raise SystemExit("headline result row count does not match counts.total_rows")
    if counts["eligible_comparisons"] != counts["flow_wins"] + counts["sklearn_wins"] + counts["ties"]:
        raise SystemExit("eligible headline count is internally inconsistent")
    if any(r.get("timing_unit") != "ms" for r in result["rows"]):
        raise SystemExit("all committed v2 rows must be milliseconds")

    card, paragraph, audit = generated_strings(result)
    html = HTML.read_text()
    replacements = ((OLD_CARD, card), (OLD_TIMING_PARAGRAPH, paragraph), (OLD_AUDIT, audit))
    for old, new in replacements:
        if old in html:
            html = html.replace(old, new, 1)
        elif new not in html:
            raise SystemExit("benchmark page no longer contains expected generated headline anchor")

    if not args.check:
        HTML.write_text(html)
        DOC_JSON.write_text(json.dumps(result, indent=2) + "\n")
        print(
            f"published headline: {counts['flow_wins']}/{counts['eligible_comparisons']} Flow wins; "
            f"{counts['parity_unresolved']} parity unresolved"
        )
    else:
        print("v2 headline source is internally consistent and publication anchors are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
