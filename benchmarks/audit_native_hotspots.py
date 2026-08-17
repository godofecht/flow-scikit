#!/usr/bin/env python3
"""Audit compiled sklearn hot paths and assign explicit Flow dispositions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def owner(row):
    evidence = " ".join(row.get("evidence", [])).lower()
    source = row.get("source_file", "").lower()
    if "libsvm" in evidence or "liblinear" in evidence:
        return "external"
    if "sklearn" in source or row.get("module", "").startswith("sklearn."):
        return "sklearn"
    return "unknown"


def disposition(row):
    cls = row["execution_class"]
    own = owner(row)
    present = row.get("flow_scikit_status") == "present"
    if own == "external":
        return "retain-native"
    if cls in {"blas-lapack-bound", "scipy-bound"}:
        return "retain-native"
    if cls in {"cython-bound", "c-bound", "cpp-bound"} and own == "sklearn":
        return "already-equivalent" if present else "replace-with-flow"
    if cls == "mixed" and present:
        return "already-equivalent"
    if not present:
        return "low-value"
    return "already-equivalent"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inventory", type=Path, default=ROOT / "benchmarks" / "sklearn_execution_inventory.json")
    p.add_argument("--roadmap", type=Path, default=ROOT / "benchmarks" / "optimization_roadmap.json")
    p.add_argument("--json", type=Path, default=ROOT / "benchmarks" / "native_hotspot_audit.json")
    p.add_argument("--markdown", type=Path, default=ROOT / "benchmarks" / "NATIVE_HOTSPOT_AUDIT.md")
    args = p.parse_args()
    inv = json.loads(args.inventory.read_text())["rows"]
    roadmap = json.loads(args.roadmap.read_text())["rows"] if args.roadmap.exists() else []
    priority = {(r["estimator"], r["operation"]): r["priority_score"] for r in roadmap}
    candidates = [r for r in inv if r["execution_class"] in {"cython-bound","c-bound","cpp-bound","external-native-bound","blas-lapack-bound","mixed"}]
    rows = []
    for r in candidates:
        d = disposition(r)
        rows.append({
            "module": r["module"], "estimator": r["estimator"], "operation": r["operation"],
            "execution_class": r["execution_class"], "ownership": owner(r),
            "source_file": r.get("source_file"), "evidence": r.get("evidence", []),
            "flow_scikit_status": r.get("flow_scikit_status"), "priority_score": priority.get((r["estimator"], r["operation"])),
            "disposition": d,
            "replacement_hypothesis": (
                "Flow-native implementation should be parity-gated against identical algorithm semantics" if d == "replace-with-flow"
                else "retain mature native kernel and optimize orchestration" if d == "retain-native"
                else "Flow implementation already exists; benchmark before further rewrite"
            ),
        })
    rows.sort(key=lambda r: (r["priority_score"] is not None, r["priority_score"] or 0), reverse=True)
    args.json.write_text(json.dumps({"schema_version": 1, "rows": rows}, indent=2) + "\n")
    md = ["# Native hotspot audit", "", "| Estimator | Operation | Class | Owner | Disposition | Priority |", "|---|---|---|---|---|---:|"]
    for r in rows:
        score = "" if r["priority_score"] is None else f"{r['priority_score']:.1f}"
        md.append(f"| `{r['estimator']}` | `{r['operation']}` | {r['execution_class']} | {r['ownership']} | {r['disposition']} | {score} |")
    args.markdown.write_text("\n".join(md) + "\n")
    counts = {}
    for r in rows: counts[r["disposition"]] = counts.get(r["disposition"], 0) + 1
    print(json.dumps(counts, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
