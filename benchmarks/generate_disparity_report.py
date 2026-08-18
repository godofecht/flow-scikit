#!/usr/bin/env python3
"""Generate persistent row-level disparity evidence for the canonical benchmark.

Parity eligibility is intentionally not treated as identity. This report keeps
raw numerical differences, contract tolerances, configuration differences,
semantic exceptions, learned-state diagnostics and runtime ratios visible after
a row becomes eligible.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE_DIAGNOSTIC_FIELDS = {"algorithm", "dataset", "metric", "parity_status", "score_abs_diff"}


def config_diff(flow: dict, sklearn: dict) -> list[dict]:
    out = []
    for key in sorted(set(flow) | set(sklearn)):
        fv = flow.get(key, "<missing>")
        sv = sklearn.get(key, "<missing>")
        if fv != sv:
            out.append({"parameter": key, "flow": fv, "sklearn": sv})
    return out


def model_state_diagnostics(diag: dict) -> dict:
    """Return learned-state deltas already produced by the parity comparison."""
    return {
        key: value
        for key, value in diag.items()
        if key not in BASE_DIAGNOSTIC_FIELDS and key.endswith("_diff")
    }


def parse_details(path: Path) -> dict[tuple[str, str, str], float | list[float]]:
    """Read DETAIL records directly so failed score gates cannot erase state."""
    out: dict[tuple[str, str, str], float | list[float]] = {}
    if not path.exists():
        return out
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line.startswith("DETAIL|"):
            continue
        parts = line.split("|", 4)
        if len(parts) != 5:
            continue
        value: float | list[float]
        if "," in parts[4]:
            value = [float(v) for v in parts[4].split(",") if v]
        else:
            value = float(parts[4])
        out[(parts[1], parts[2], parts[3])] = value
    return out


def relative_diff(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), 1e-12)


def enrich_state_from_raw_details(
    key: tuple[str, str, str],
    state: dict,
    sklearn_details: dict,
    flow_details: dict,
) -> dict:
    """Derive learned-state deltas from the frozen DETAIL records.

    compare_v2.py stops at the first failed gate, so a row whose score misses
    its tolerance never reaches the estimator-specific state comparison and its
    evidence is lost. This pass works straight off the DETAIL records instead,
    pairing every field both runners emitted for the row.

    Scalars produce `<field>_abs_diff` and `<field>_relative_diff`. Equal-length
    vectors produce `<field>_max_abs_diff` and `<field>_max_relative_diff`.
    Length disagreement is itself evidence and is recorded as
    `<field>_length_abs_diff`. Anything compare_v2 already computed wins, so the
    existing KMeans and PCA key names are unchanged.
    """
    algorithm, dataset, _ = key
    for (algo, ds, field), sk_value in sorted(sklearn_details.items()):
        if algo != algorithm or ds != dataset:
            continue
        fl_value = flow_details.get((algo, ds, field))
        if fl_value is None:
            continue
        if isinstance(sk_value, list) or isinstance(fl_value, list):
            if not (isinstance(sk_value, list) and isinstance(fl_value, list)):
                continue
            if len(sk_value) != len(fl_value):
                state.setdefault(f"{field}_length_abs_diff", float(abs(len(sk_value) - len(fl_value))))
                continue
            pairs = list(zip(sk_value, fl_value))
            state.setdefault(f"{field}_max_abs_diff", max((abs(a - b) for a, b in pairs), default=0.0))
            state.setdefault(f"{field}_max_relative_diff", max((relative_diff(a, b) for a, b in pairs), default=0.0))
        else:
            state.setdefault(f"{field}_abs_diff", abs(sk_value - fl_value))
            state.setdefault(f"{field}_relative_diff", relative_diff(sk_value, fl_value))
    return state


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--headline", type=Path, default=ROOT / "headline_result_v2.json")
    p.add_argument("--diagnostics", type=Path, default=ROOT / "parity_diagnostics.json")
    p.add_argument("--contract", type=Path, default=ROOT / "parity_contract.json")
    p.add_argument("--kmeans-audit", type=Path, default=ROOT / "kmeans_semantics_audit.json")
    p.add_argument("--sklearn-raw", type=Path, default=ROOT / "sklearn_results_v2.txt")
    p.add_argument("--flow-raw", type=Path, default=ROOT / "flow_results_v2.txt")
    p.add_argument("--output", type=Path, default=ROOT / "disparity_report.json")
    args = p.parse_args()

    headline = json.loads(args.headline.read_text())
    diagnostics = json.loads(args.diagnostics.read_text())
    contract_doc = json.loads(args.contract.read_text())
    kmeans_audit = json.loads(args.kmeans_audit.read_text()) if args.kmeans_audit.exists() else None
    sklearn_details = parse_details(args.sklearn_raw)
    flow_details = parse_details(args.flow_raw)

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
        state = enrich_state_from_raw_details(
            key,
            model_state_diagnostics(diag),
            sklearn_details,
            flow_details,
        )
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
        if state:
            dimensions.append("model-state")
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
            "model_state_diagnostics": state,
            "diagnostics": {k: v for k, v in diag.items() if k not in BASE_DIAGNOSTIC_FIELDS},
            "disparity_dimensions": dimensions,
            "has_tracked_disparity": bool(dimensions),
        })

    payload = {
        "schema_version": 2,
        "environment_id": headline.get("environment_id"),
        "policy": "headline eligibility never erases disparity evidence; strict diagnostics, learned-state diagnostics and final eligibility decisions are retained separately",
        "counts": {
            "rows": len(rows),
            "rows_with_tracked_disparity": sum(r["has_tracked_disparity"] for r in rows),
            "rows_with_configuration_difference": sum(bool(r["configuration_differences"]) for r in rows),
            "rows_with_semantic_difference": sum(bool(r["semantic_differences"]) for r in rows),
            "rows_with_model_state_diagnostics": sum(bool(r["model_state_diagnostics"]) for r in rows),
            "strict_final_status_disagreements": sum(r["strict_diagnostic_status"] != r["final_parity_status"] for r in rows),
        },
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
