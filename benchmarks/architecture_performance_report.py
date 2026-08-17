#!/usr/bin/env python3
"""Join substrate, profiling, parity, benchmark and roadmap evidence."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ESTIMATOR_ALIASES = {
    "KernelSVC_RBF": "SVC",
    "DecisionTree": "DecisionTreeClassifier",
    "RandomForest": "RandomForestClassifier",
    "KernelRidge_RBF": "KernelRidge",
}


def inventory_name(algorithm: str) -> str:
    return ESTIMATOR_ALIASES.get(algorithm, algorithm)


def headline_speedup(row: dict):
    if row.get("speedup") is not None:
        return float(row["speedup"])
    if row.get("flow_ms", 0) and row.get("sklearn_ms") is not None:
        return float(row["sklearn_ms"]) / float(row["flow_ms"])
    sk = float(row.get("sklearn_fit_ms", 0) or 0) + float(row.get("sklearn_pred_ms", 0) or 0)
    fl = float(row.get("flow_fit_ms", 0) or 0) + float(row.get("flow_pred_ms", 0) or 0)
    return sk / fl if sk > 0 and fl > 0 else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inventory", type=Path, default=ROOT / "benchmarks" / "sklearn_execution_inventory.json")
    p.add_argument("--profiles", type=Path, default=ROOT / "benchmarks" / "sklearn_runtime_attribution.json")
    p.add_argument("--roadmap", type=Path, default=ROOT / "benchmarks" / "optimization_roadmap.json")
    p.add_argument("--hotspots", type=Path, default=ROOT / "benchmarks" / "native_hotspot_audit.json")
    p.add_argument("--whole", type=Path, default=ROOT / "benchmarks" / "whole_estimator_experiments.json")
    p.add_argument("--headline", type=Path, default=ROOT / "benchmarks" / "headline_result_v2.json")
    p.add_argument("--json", type=Path, default=ROOT / "benchmarks" / "architecture_performance_map.json")
    p.add_argument("--markdown", type=Path, default=ROOT / "benchmarks" / "ARCHITECTURE_PERFORMANCE_MAP.md")
    args = p.parse_args()

    inventory = json.loads(args.inventory.read_text())["rows"]
    profiles = json.loads(args.profiles.read_text())["rows"]
    roadmap = json.loads(args.roadmap.read_text())["rows"]
    hotspots = json.loads(args.hotspots.read_text())["rows"]
    whole = json.loads(args.whole.read_text())["rows"]
    headline = json.loads(args.headline.read_text()) if args.headline.exists() else {"rows": []}

    inv_by_estimator = defaultdict(list)
    for r in inventory:
        inv_by_estimator[r["estimator"]].append(r)
    prof_by_estimator = defaultdict(list)
    for r in profiles:
        if r.get("status") == "ok":
            prof_by_estimator[r["estimator"]].append(r)

    joined = []
    for h in headline.get("rows", []):
        algorithm = h["algorithm"]
        estimator = inventory_name(algorithm)
        inv = inv_by_estimator.get(estimator, [])
        fit_inv = next((r for r in inv if r["operation"] == "fit"), inv[0] if inv else None)
        prof = prof_by_estimator.get(estimator, [])
        fit_prof = max((r for r in prof if r["operation"] == "fit"), key=lambda r: r["rows"], default=None)
        joined.append({
            "algorithm": algorithm,
            "sklearn_estimator": estimator,
            "dataset": h["dataset"],
            "parity_status": h.get("parity_status"),
            "classification": h.get("classification"),
            "flow_speedup": headline_speedup(h),
            "fit_execution_class": fit_inv.get("execution_class") if fit_inv else "unmapped",
            "inventory_confidence": fit_inv.get("confidence") if fit_inv else None,
            "python_visible_self_share": fit_prof.get("python_visible_self_share") if fit_prof else None,
            "python_to_native_crossing_proxy": fit_prof.get("python_to_native_call_count_proxy") if fit_prof else None,
        })

    by_substrate = defaultdict(list)
    for r in joined:
        if r["flow_speedup"] is not None and r["parity_status"] in {"parity verified", "approximately equivalent"}:
            by_substrate[r["fit_execution_class"]].append(r["flow_speedup"])
    substrate_summary = []
    for cls, vals in sorted(by_substrate.items()):
        substrate_summary.append({
            "execution_class": cls,
            "n": len(vals),
            "mean_flow_speedup": sum(vals) / len(vals),
            "flow_win_fraction": sum(v > 1 for v in vals) / len(vals),
        })

    payload = {
        "schema_version": 1,
        "joined_headline_rows": joined,
        "speedup_by_execution_substrate": substrate_summary,
        "coverage": {
            "inventory_operations": len(inventory),
            "profile_rows": len(profiles),
            "roadmap_rows": len(roadmap),
            "native_hotspot_rows": len(hotspots),
            "whole_estimator_rows": len(whole),
            "headline_rows": len(headline.get("rows", [])),
            "headline_rows_with_substrate": sum(r["fit_execution_class"] != "unmapped" for r in joined),
            "headline_rows_with_speedup": sum(r["flow_speedup"] is not None for r in joined),
        },
        "interpretation_rule": "substrate is predictive evidence only when grouped results contain multiple parity-eligible rows; do not infer causality from one estimator",
    }
    args.json.write_text(json.dumps(payload, indent=2) + "\n")
    md = [
        "# sklearn execution architecture × Flow performance", "",
        "This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.", "",
        "## Headline rows", "",
        "| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |",
        "|---|---|---|---|---|---:|---:|",
    ]
    for r in joined:
        speed = "" if r["flow_speedup"] is None else f"{r['flow_speedup']:.2f}×"
        ps = "" if r["python_visible_self_share"] is None else f"{100*r['python_visible_self_share']:.1f}%"
        md.append(f"| `{r['algorithm']}` | `{r['sklearn_estimator']}` | {r['dataset']} | {r['fit_execution_class']} | {r['parity_status']} | {speed} | {ps} |")
    md += ["", "## Speedup grouped by execution substrate", "", "| Substrate | Rows | Mean speedup | Flow win fraction |", "|---|---:|---:|---:|"]
    for r in substrate_summary:
        md.append(f"| {r['execution_class']} | {r['n']} | {r['mean_flow_speedup']:.2f}× | {100*r['flow_win_fraction']:.0f}% |")
    args.markdown.write_text("\n".join(md) + "\n")
    print(json.dumps(payload["coverage"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
