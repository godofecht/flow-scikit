#!/usr/bin/env python3
"""Fail when an artifact derived from the canonical headline result is stale.

Canonical input: benchmarks/headline_result_v2.json. Every artifact below must
have been generated from exactly those bytes:

  optimization_roadmap.json, native_hotspot_audit.json,
  whole_estimator_experiments.json, architecture_performance_map.json
      carry provenance.result_sha256 and provenance.environment_id
  architecture_performance_map.json
      its joined rows and substrate summary are recomputed from the result
  ARCHITECTURE_PERFORMANCE_MAP.md
      its table rows match the map
  whole_estimator_experiments.json
      its embedded headline rows equal the result's rows
  disparity_report.json
      its environment_id equals the result's
  docs/*.json (the Pages copies, when present)
      are byte-identical to their benchmarks/ source

Stdlib only. Exit 1 on any drift. Regenerate with
`python benchmarks/refresh_derived_evidence.py`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

PROVENANCE_ARTIFACTS = [
    "optimization_roadmap.json",
    "native_hotspot_audit.json",
    "whole_estimator_experiments.json",
    "architecture_performance_map.json",
]
PAGES_COPIES = {
    "headline_result_v2.json": "headline-result-v2.json",
    "architecture_performance_map.json": "architecture-performance-map.json",
    "disparity_report.json": "disparity-report.json",
    "disparity_history.json": "disparity-history.json",
    "scaled_ci_history.json": "scaled-ci-history.json",
    "estimator_comparison.json": "estimator-comparison.json",
}
VERIFIED = {"parity verified", "approximately equivalent"}


def headline_speedup(row: dict):
    """Same rule architecture_performance_report.py applies."""
    if row.get("speedup") is not None:
        return float(row["speedup"])
    if row.get("flow_ms", 0) and row.get("sklearn_ms") is not None:
        return float(row["sklearn_ms"]) / float(row["flow_ms"])
    sk = float(row.get("sklearn_fit_ms", 0) or 0) + float(row.get("sklearn_pred_ms", 0) or 0)
    fl = float(row.get("flow_fit_ms", 0) or 0) + float(row.get("flow_pred_ms", 0) or 0)
    return sk / fl if sk > 0 and fl > 0 else None


def close(a, b) -> bool:
    if a is None or b is None:
        return a is b
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def check(root: Path) -> list[str]:
    bench = root / "benchmarks"
    docs = root / "docs"
    problems: list[str] = []
    result_path = bench / "headline_result_v2.json"
    digest = hashlib.sha256(result_path.read_bytes()).hexdigest()
    result = json.loads(result_path.read_text())
    env = result.get("environment_id")

    for row in result["rows"]:
        if row.get("environment_id") != env:
            problems.append(f"headline row {row['algorithm']}/{row['dataset']} has environment_id {row.get('environment_id')!r}, result has {env!r}")

    docs_by_name: dict[str, dict] = {}
    for name in PROVENANCE_ARTIFACTS:
        path = bench / name
        if not path.exists():
            problems.append(f"{name}: missing")
            continue
        doc = json.loads(path.read_text())
        docs_by_name[name] = doc
        prov = doc.get("provenance")
        if not prov:
            problems.append(f"{name}: carries no provenance block")
            continue
        if prov.get("result_sha256") != digest:
            problems.append(f"{name}: built from result sha256 {str(prov.get('result_sha256'))[:12]}, committed result is {digest[:12]}")
        if prov.get("environment_id") != env:
            problems.append(f"{name}: environment_id {prov.get('environment_id')!r}, committed result is {env!r}")

    disparity = bench / "disparity_report.json"
    if disparity.exists():
        d_env = json.loads(disparity.read_text()).get("environment_id")
        if d_env != env:
            problems.append(f"disparity_report.json: environment_id {d_env!r}, committed result is {env!r}")

    amap = docs_by_name.get("architecture_performance_map.json")
    if amap is not None:
        joined = {(r["algorithm"], r["dataset"]): r for r in amap["joined_headline_rows"]}
        if len(joined) != len(result["rows"]):
            problems.append(f"architecture map joins {len(joined)} rows, result has {len(result['rows'])}")
        for row in result["rows"]:
            key = (row["algorithm"], row["dataset"])
            j = joined.get(key)
            if j is None:
                problems.append(f"architecture map has no row for {key[0]}/{key[1]}")
                continue
            for field, want in (("parity_status", row.get("parity_status")), ("classification", row.get("classification"))):
                if j.get(field) != want:
                    problems.append(f"architecture map {key[0]}/{key[1]} {field} is {j.get(field)!r}, result says {want!r}")
            if not close(j.get("flow_speedup"), headline_speedup(row)):
                problems.append(f"architecture map {key[0]}/{key[1]} flow_speedup is {j.get('flow_speedup')}, result gives {headline_speedup(row)}")
        by_class: dict[str, list[float]] = {}
        for j in amap["joined_headline_rows"]:
            if j["flow_speedup"] is not None and j["parity_status"] in VERIFIED:
                by_class.setdefault(j["fit_execution_class"], []).append(j["flow_speedup"])
        stored = {g["execution_class"]: g for g in amap["speedup_by_execution_substrate"]}
        if set(stored) != set(by_class):
            problems.append("architecture map substrate summary lists different classes than its joined rows")
        for cls, vals in by_class.items():
            g = stored.get(cls)
            if g and (g["n"] != len(vals) or not close(g["mean_flow_speedup"], sum(vals) / len(vals))):
                problems.append(f"architecture map substrate summary for {cls} disagrees with its joined rows")

        md = bench / "ARCHITECTURE_PERFORMANCE_MAP.md"
        text = md.read_text() if md.exists() else ""
        for j in amap["joined_headline_rows"]:
            speed = "" if j["flow_speedup"] is None else f"{j['flow_speedup']:.2f}×"
            line = next((ln for ln in text.splitlines() if ln.startswith(f"| `{j['algorithm']}` |") and f"| {j['dataset']} |" in ln), None)
            if line is None or f"| {speed} |" not in line:
                problems.append(f"ARCHITECTURE_PERFORMANCE_MAP.md row {j['algorithm']}/{j['dataset']} does not show {speed or 'an empty speedup'}")

    whole = docs_by_name.get("whole_estimator_experiments.json")
    if whole is not None:
        for row in whole["rows"]:
            if "flow_rows" not in row:
                continue
            want = [r for r in result["rows"] if r.get("algorithm") == row.get("representative")]
            if row["flow_rows"] != want:
                problems.append(f"whole_estimator_experiments.json embeds stale headline rows for {row.get('representative')}")

    for src, dst in PAGES_COPIES.items():
        copy = docs / dst
        if copy.exists() and copy.read_bytes() != (bench / src).read_bytes():
            problems.append(f"docs/{dst} differs from benchmarks/{src}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = ap.parse_args()
    problems = check(args.root)
    if problems:
        print("Derived evidence disagrees with benchmarks/headline_result_v2.json:")
        for p in problems:
            print("  -", p)
        print("Run: python benchmarks/refresh_derived_evidence.py")
        return 1
    print("derived evidence matches the committed headline result")
    return 0


if __name__ == "__main__":
    sys.exit(main())
