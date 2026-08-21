#!/usr/bin/env python3
"""Generate persistent row-level disparity evidence for the canonical benchmark.

Parity eligibility is intentionally not treated as identity. This report keeps
raw numerical differences, contract tolerances, configuration differences,
semantic exceptions, learned-state diagnostics and runtime ratios visible after
a row becomes eligible.

Configuration is compared through the declared equivalences in
`config_equivalence.py`, so a setting the two projects record under different
names stops reading as a difference. Every applied equivalence is written into
the row's `configuration_equivalences`, which keeps the evidence rather than
dropping it.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from config_equivalence import compare_configs

ROOT = Path(__file__).resolve().parent
BASE_DIAGNOSTIC_FIELDS = {"algorithm", "dataset", "metric", "parity_status", "score_abs_diff"}


def load_train_sizes(path: Path) -> dict[str, int]:
    """Training-set size per dataset, from the canonical split fixture.

    Some cross-vocabulary conversions carry n_train (`l2 = 1 / (C * n_train)`),
    so the comparator needs the real split rather than a constant per dataset
    name. Missing or unreadable fixtures leave the size unknown, which makes
    those conversions unverifiable and keeps the pair reported.
    """
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    sizes: dict[str, int] = {}
    for dataset, row in data.items():
        if not isinstance(row, dict):
            continue
        n_train = row.get("n_train")
        if n_train is None and isinstance(row.get("train_idx"), list):
            n_train = len(row["train_idx"])
        if isinstance(n_train, int):
            sizes[dataset] = n_train
    return sizes


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


def first_divergent_index(pairs: list[tuple[float, float]]) -> int:
    """Index of the first element the two runs disagree on, or -1 if none.

    The tolerance absorbs float32 print rounding so a shared structure emitted
    at slightly different precision does not read as a divergence.
    """
    for index, (a, b) in enumerate(pairs):
        if abs(a - b) > 1e-9 + 1e-6 * max(abs(a), abs(b)):
            return index
    return -1


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
    vectors produce `<field>_max_abs_diff`, `<field>_max_relative_diff` and
    `<field>_first_divergent_index`, which is -1 when the two vectors match
    elementwise and otherwise points at the first position they disagree on.
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
            state.setdefault(f"{field}_first_divergent_index", first_divergent_index(pairs))
        else:
            state.setdefault(f"{field}_abs_diff", abs(sk_value - fl_value))
            state.setdefault(f"{field}_relative_diff", relative_diff(sk_value, fl_value))
    return state




# Relative diffs are scale-free; 1e-5 sits two orders above f32 ulp noise in
# accumulated norms. A relative diff on a near-zero quantity can explode on
# pure noise, so it only counts when its paired absolute diff also clears a
# floor. A non-negative first_divergent_index is exact divergence by
# construction and needs no floor.
_STATE_REL_FLOOR = 1e-5
_STATE_ABS_FLOOR = 1e-7


def _model_state_diverges(state: dict) -> bool:
    if not state:
        return False
    for key, value in state.items():
        if key.endswith("_first_divergent_index"):
            if isinstance(value, (int, float)) and value >= 0:
                return True
        elif key.endswith("_relative_diff"):
            if not isinstance(value, (int, float)) or value <= _STATE_REL_FLOOR:
                continue
            paired = state.get(key[: -len("_relative_diff")] + "_abs_diff")
            if paired is None or (isinstance(paired, (int, float)) and paired > _STATE_ABS_FLOOR):
                return True
    return False

def _total_ms(row: dict, side: str):
    """Fit plus predict for one side of a headline row, or None if unresolved."""
    fit = row.get(f"{side}_fit_ms")
    pred = row.get(f"{side}_pred_ms")
    if fit is None or pred is None:
        return None
    return float(fit) + float(pred)

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--headline", type=Path, default=ROOT / "headline_result_v2.json")
    p.add_argument("--diagnostics", type=Path, default=ROOT / "parity_diagnostics.json")
    p.add_argument("--contract", type=Path, default=ROOT / "parity_contract.json")
    p.add_argument("--kmeans-audit", type=Path, default=ROOT / "kmeans_semantics_audit.json")
    p.add_argument("--sklearn-raw", type=Path, default=ROOT / "sklearn_results_v2.txt")
    p.add_argument("--flow-raw", type=Path, default=ROOT / "flow_results_v2.txt")
    p.add_argument("--host-environment", type=Path, default=ROOT / "headline_environment.json")
    p.add_argument("--splits", type=Path, default=ROOT / "split_indices.json")
    p.add_argument("--output", type=Path, default=ROOT / "disparity_report.json")
    args = p.parse_args()

    headline = json.loads(args.headline.read_text())
    diagnostics = json.loads(args.diagnostics.read_text())
    contract_doc = json.loads(args.contract.read_text())
    kmeans_audit = json.loads(args.kmeans_audit.read_text()) if args.kmeans_audit.exists() else None
    sklearn_details = parse_details(args.sklearn_raw)
    flow_details = parse_details(args.flow_raw)
    host_env = json.loads(args.host_environment.read_text()) if args.host_environment.exists() else {}
    train_sizes = load_train_sizes(args.splits)

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
            # The row is gated on its declared parity_contract.json tolerance
            # now, like every other row: the audit no longer promotes it past a
            # failed strict gate. Older audits carried their own tolerance, so
            # the override is still honoured when one is present.
            policy = kmeans_audit.get("canonical_parity_policy", {})
            if "ari_absolute_tolerance" in policy:
                effective_score_tol = float(policy["ari_absolute_tolerance"])
            # Two dimensions, the same two this report has always carried.
            # The audit's `residual_semantic_differences` holds the full list
            # (empty-cluster relocation, inertia reporting point, n_init
            # selection); it is committed and uploaded as its own artifact.
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
                    "residual_semantic_differences": kmeans_audit.get("residual_semantic_differences", []),
                },
            ])

        config, config_equivalences = compare_configs(
            contract.get("flow", {}),
            contract.get("sklearn", {}),
            train_sizes.get(row["dataset"]),
        )
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
        # Floors, so a dimension means divergence rather than existence.
        # Without them every row was flagged: any nonzero f32 score diff set
        # "numerical" (2.8e-8 against a declared tolerance of 1e-3), and
        # "model-state" tested the diagnostics dict for truthiness, so the
        # moment coverage reached 19/19 every row became "disparate". The
        # numerical floor follows the disparity-gate precedent: noise below
        # max(1e-6, 1% of the row's declared tolerance) is not a finding.
        numerical_floor = max(1e-6, 0.01 * score_tol)
        if score_diff > numerical_floor:
            dimensions.append("numerical")
        if config:
            dimensions.append("configuration")
        if semantic:
            dimensions.append("semantic")
        if _model_state_diverges(state):
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
            # Absolute timings, recorded so a reader can see each implementation's
            # own trajectory. Every other timing field here is a ratio, which hides
            # the case where both sides move and the ratio stays put.
            "flow_total_ms": _total_ms(row, "flow"),
            "sklearn_total_ms": _total_ms(row, "sklearn"),
            "runtime_log2_ratio": runtime_log2_ratio,
            "configuration_differences": config,
            # Settings the two projects record under different names, or that
            # only one side's solver has. Kept rather than dropped so removing
            # them from `configuration_differences` hides nothing.
            "configuration_equivalences": config_equivalences,
            "semantic_differences": semantic,
            "model_state_diagnostics": state,
            "diagnostics": {k: v for k, v in diag.items() if k not in BASE_DIAGNOSTIC_FIELDS},
            "disparity_dimensions": dimensions,
            "has_tracked_disparity": bool(dimensions),
        })

    payload = {
        "schema_version": 4,
        "environment_id": headline.get("environment_id"),
        # Hardware plus BLAS thread configuration. environment_id only covers the
        # software stack, so it cannot tell two runner machines apart; wall-clock
        # comparisons are only meaningful within one runtime_environment_id.
        "runtime_environment_id": host_env.get("runtime_environment_id"),
        "host": host_env.get("host"),
        "policy": "headline eligibility never erases disparity evidence; strict diagnostics, learned-state diagnostics and final eligibility decisions are retained separately",
        "counts": {
            "rows": len(rows),
            "rows_with_tracked_disparity": sum(r["has_tracked_disparity"] for r in rows),
        "rows_with_substantive_disparity": sum(1 for r in rows if any(d != "runtime" for d in r["disparity_dimensions"])),
            "rows_with_configuration_difference": sum(bool(r["configuration_differences"]) for r in rows),
            "rows_with_configuration_equivalence": sum(bool(r["configuration_equivalences"]) for r in rows),
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
