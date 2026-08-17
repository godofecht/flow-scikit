#!/usr/bin/env python3
"""Generate persistent row-level disparity evidence for the canonical benchmark.

Parity eligibility is intentionally not treated as identity. This report keeps
raw numerical differences, contract tolerances, configuration differences,
semantic exceptions and runtime ratios visible after a row becomes eligible.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def config_diff(flow: dict, sklearn: dict) -> list[dict]:
    out = []
    for key in sorted(set(flow) | set(sklearn)):
        fv = flow.get(key, "<missing>")
        sv = sklearn.get(key, "<missing>")
        if fv != sv:
            out.append({"parameter": key, "flow": fv, "sklearn": sv})
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--headline", type=Path, default=ROOT / "headline_result_v2.json")
    p.add_argument("--diagnostics", type=Path, default=ROOT / "parity_diagnostics.json")
    p.add_argument("--contract", type=Path, default=ROOT / "parity_contract.json")
    p.add_argument("--kmeans-audit", type=Path, default=ROOT / "kmeans_semantics_audit.json")
    p.add_argument("--output", type=Path, default=ROOT / "disparity_report.json")
    args = p.parse_args()

    headline = json.loads(args.headline.read_text())
    diagnostics = json.loads(args.diagnostics.read_text())
    contract_doc = json.loads(args.contract.read_text())
    kmeans_audit = json.loads(args.kmeans_audit.read_text()) if args.kmeans_audit.exists() else None

    diag_by_key = {(r["algorithm"], r["dataset"], r["metric"]): r for r in diagnostics}
    contract_by_key = {(r["algorithm"], r["dataset"], r["metric"]): r for r in contract_doc["rows"]}

    rows = []
    for row in headline["rows"]:
        key = (row["algorithm"], row["dataset"], row["metric"])
        diag = diag_by_key.get(key, {})
        contract = contract_by_key[key]
        score_diff = float(diag.get("score_abs_diff", abs(row["sklearn_score"] - row["flow_score"])))
        score_tol = float(contract["score_abs_tolerance"])
        effective_score_tol = score_tol
        semantic = []

        if key == ("KMeans", "digits", "adjusted_rand_index") and kmeans_audit:
            policy = kmeans_audit["canonical_parity_policy"]
            effective_score_tol = float(policy["ari_absolute_tolerance"])
            semantic.extend([
                {
                    "dimension": "initialization",
                    "flow": kmeans_audit["initializers"]["flow"],
                    "sklearn": kmeans_audit["initializers"]["sklearn"],
                    "first_divergence_stage": kmeans_audit["first_divergence_stage"],
                },
                {
                    "dimension": "convergence statistic",
                    "flow": kmeans_audit["convergence"]["flow_statistic"],
                    "sklearn": kmeans_audit["convergence"]["sklearn_statistic"],
                },
            ])

        config = config_diff(contract.get("flow", {}), contract.get("sklearn", {}))
        runtime_ratio = row["sklearn_ms"] / row["flow_ms"] if row["flow_ms"] > 0 else None
        runtime_log2_ratio = math.log2(runtime_ratio) if runtime_ratio and runtime_ratio > 0 else None
        tolerance_fraction = score_diff / effective_score_tol if effective_score_tol > 0 else None

        dimensions = []
        if score_diff > 0:
            dimensions.append("numerical")
        if config:
            dimensions.append("configuration")
        if semantic:
            dimensions.append("semantic")
        if diag.get("parity_status") != row.get("parity_status"):
            dimensions.append("strict-vs-final-parity-decision")
        if runtime_ratio is not None and abs(runtime_ratio - 1.0) > headline.get("tie_relative_threshold", 0.02):
            dimensions.append("runtime")

        rows.append({
            "algorithm": row["algorithm"],
            "dataset": row["dataset"],
            "metric": row["metric"],
            "final_parity_status": row.get("parity_status"),
            "strict_diagnostic_status": diag.get("parity_status"),
            "headline_classification": row.get("classification"),
            "score_abs_diff": score_diff,
            "declared_score_tolerance": score_tol,
            "effective_score_tolerance": effective_score_tol,
            "score_tolerance_fraction": tolerance_fraction,
            "runtime_ratio_sklearn_over_flow": runtime_ratio,
            "runtime_log2_ratio": runtime_log2_ratio,
            "configuration_differences": config,
            "semantic_differences": semantic,
            "diagnostics": {k: v for k, v in diag.items() if k not in {"algorithm", "dataset", "metric", "parity_status", "score_abs_diff"}},
            "disparity_dimensions": dimensions,
            "has_tracked_disparity": bool(dimensions),
        })

    payload = {
        "schema_version": 1,
        "environment_id": headline.get("environment_id"),
        "policy": "headline eligibility never erases disparity evidence; strict diagnostics and final eligibility decisions are both retained",
        "counts": {
            "rows": len(rows),
            "rows_with_tracked_disparity": sum(r["has_tracked_disparity"] for r in rows),
            "rows_with_configuration_difference": sum(bool(r["configuration_differences"]) for r in rows),
            "rows_with_semantic_difference": sum(bool(r["semantic_differences"]) for r in rows),
            "strict_final_status_disagreements": sum(r["strict_diagnostic_status"] != r["final_parity_status"] for r in rows),
        },
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
