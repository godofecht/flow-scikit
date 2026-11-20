#!/usr/bin/env python3
"""Join execution inventory, runtime attribution and Flow benchmark evidence.

The score is deliberately decomposed into visible factors.  It ranks where Flow
work is most likely to matter while penalizing mature external/native kernels
that should normally be retained.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from evidence_provenance import provenance

ROOT = Path(__file__).resolve().parents[1]

SUBSTRATE_OPPORTUNITY = {
    "python-bound": 1.0, "mixed": 0.8, "numpy-bound": 0.55,
    "scipy-bound": 0.45, "cython-bound": 0.65, "c-bound": 0.55,
    "cpp-bound": 0.55, "blas-lapack-bound": 0.25,
    "external-native-bound": 0.15,
}

HEADLINE_TO_SKLEARN = {
    "KernelSVC_RBF": "SVC",
    "DecisionTree": "DecisionTreeClassifier",
    "RandomForest": "RandomForestClassifier",
    "KernelRidge_RBF": "KernelRidge",
}


def disposition(substrate, python_share, flow_status):
    if substrate in {"external-native-bound", "blas-lapack-bound"}:
        return "reuse optimized native kernel"
    if substrate in {"cython-bound", "c-bound", "cpp-bound"}:
        return "replace Cython/native sklearn code" if flow_status == "present" else "compile whole estimator"
    if substrate == "python-bound" or python_share >= 0.35:
        return "rewrite first"
    if substrate in {"mixed", "numpy-bound", "scipy-bound"}:
        return "compile whole estimator"
    return "low performance value"


# Which stage of a headline row is evidence for which estimator operation.
#
# A headline row times fit and prediction separately. Its end-to-end speedup is
# dominated by fit wherever fit is the slower stage, so reading that one number
# as evidence for `predict` reports the fit result under the wrong name. Issue
# #481 found `SVC.predict` listed at 2.20x from end-to-end totals while the
# prediction stage of the same rows ran at 6.87x and 3.33x.
#
# The prediction stage is `predict` for every canonical row except PCA, where
# it is `transform`. `predict_proba` and `decision_function` are not timed by
# the headline benchmark. They share the prediction stage's kernel, so they
# take its ratio, and the basis field says which stage a number came from.
FIT_OPERATIONS = frozenset({"fit"})
PREDICT_OPERATIONS = frozenset({"predict", "predict_proba", "decision_function", "transform"})

BASIS_FIT = "fit stage"
BASIS_PREDICT = "prediction stage"


def operation_basis(operation):
    """Return the headline stage that measures ``operation``, or None."""
    if operation in FIT_OPERATIONS:
        return BASIS_FIT
    if operation in PREDICT_OPERATIONS:
        return BASIS_PREDICT
    return None


def _ratio(sklearn_ms, flow_ms):
    sk = float(sklearn_ms or 0)
    fl = float(flow_ms or 0)
    return sk / fl if sk > 0 and fl > 0 else None


def row_speedup(row):
    """End-to-end speedup of one headline row, fit plus prediction."""
    if row.get("speedup") is not None:
        return float(row["speedup"])
    sk = float(row.get("sklearn_fit_ms", 0) or 0) + float(row.get("sklearn_pred_ms", 0) or 0)
    fl = float(row.get("flow_fit_ms", 0) or 0) + float(row.get("flow_pred_ms", 0) or 0)
    return sk / fl if sk > 0 and fl > 0 else None


def row_stage_speedup(row, basis):
    """Speedup of one stage of a headline row.

    Returns None when the stage has no resolved timing on either side. A stage
    faster than the clock resolution records 0 ms and is treated as unresolved
    instead of as an infinite speedup.
    """
    if basis == BASIS_FIT:
        return _ratio(row.get("sklearn_fit_ms"), row.get("flow_fit_ms"))
    if basis == BASIS_PREDICT:
        return _ratio(row.get("sklearn_pred_ms"), row.get("flow_pred_ms"))
    return None


def collect_speedups(headline_rows):
    """Group parity-eligible headline speedups by sklearn estimator and stage.

    Returns ``{estimator: {basis: [speedup, ...]}}`` with the bases
    ``"fit stage"``, ``"prediction stage"`` and ``"end to end"``.
    """
    speed = {}
    for r in headline_rows:
        if r.get("parity_status") not in {"parity verified", "approximately equivalent"}:
            continue
        name = HEADLINE_TO_SKLEARN.get(r["algorithm"], r["algorithm"])
        by_basis = speed.setdefault(name, {})
        for basis, value in (
            (BASIS_FIT, row_stage_speedup(r, BASIS_FIT)),
            (BASIS_PREDICT, row_stage_speedup(r, BASIS_PREDICT)),
            ("end to end", row_speedup(r)),
        ):
            if value is not None:
                by_basis.setdefault(basis, []).append(value)
    return speed


def observed_speedup(speed, estimator, operation):
    """Mean observed speedup for one estimator operation, with its basis.

    Returns ``(speedup, basis)``. Both are None when the headline benchmark
    does not time the stage that the operation belongs to.
    """
    basis = operation_basis(operation)
    values = speed.get(estimator, {}).get(basis, []) if basis else []
    if not values:
        return None, None
    return sum(values) / len(values), basis


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inventory", type=Path, default=ROOT / "benchmarks" / "sklearn_execution_inventory.json")
    p.add_argument("--profiles", type=Path, default=ROOT / "benchmarks" / "sklearn_runtime_attribution.json")
    p.add_argument("--headline", type=Path, default=ROOT / "benchmarks" / "headline_result_v2.json")
    p.add_argument("--json", type=Path, default=ROOT / "benchmarks" / "optimization_roadmap.json")
    p.add_argument("--markdown", type=Path, default=ROOT / "benchmarks" / "OPTIMIZATION_ROADMAP.md")
    args = p.parse_args()

    inv = json.loads(args.inventory.read_text())["rows"]
    profiles = json.loads(args.profiles.read_text())["rows"]
    headline = json.loads(args.headline.read_text()) if args.headline.exists() else {"rows": []}
    prof = {}
    for r in profiles:
        if r.get("status") != "ok":
            continue
        key = (r["estimator"], r["operation"])
        if key not in prof or r["rows"] > prof[key]["rows"]:
            prof[key] = r

    speed = collect_speedups(headline.get("rows", []))

    rows = []
    for r in inv:
        pr = prof.get((r["estimator"], r["operation"]))
        python_share = float(pr.get("python_visible_self_share", 0.0)) if pr else 0.0
        crossings = int(pr.get("python_to_native_call_count_proxy", 0)) if pr else 0
        crossing_factor = min(1.0, crossings / 5000.0)
        alloc_factor = min(1.0, float(pr.get("python_peak_alloc_bytes", 0)) / 8_000_000.0) if pr else 0.0
        substrate_factor = SUBSTRATE_OPPORTUNITY.get(r["execution_class"], 0.5)
        native_reuse_penalty = 0.35 if r["execution_class"] in {"external-native-bound", "blas-lapack-bound"} else 0.0
        observed_factor = 0.5
        observed, basis = observed_speedup(speed, r["estimator"], r["operation"])
        if observed is not None:
            observed_factor = min(1.0, max(0.0, observed / 3.0))
        end_to_end = speed.get(r["estimator"], {}).get("end to end", [])
        implementation_factor = 1.0 if r["flow_scikit_status"] == "present" else 0.35
        complexity_penalty = 0.25 if r["execution_class"] in {"cython-bound", "external-native-bound"} else 0.1

        score = (
            30 * substrate_factor + 25 * python_share + 10 * crossing_factor
            + 10 * alloc_factor + 15 * observed_factor + 10 * implementation_factor
            - 20 * native_reuse_penalty - 10 * complexity_penalty
        )
        disp = disposition(r["execution_class"], python_share, r["flow_scikit_status"])
        hypothesis = {
            "rewrite first": "remove Python control/validation and specialize the complete operation",
            "compile whole estimator": "retain useful numerical kernels while fusing validation, allocation and orchestration",
            "replace Cython/native sklearn code": "compare a Flow-native hot loop under identical algorithmic semantics",
            "reuse optimized native kernel": "retain the mature backend and optimize boundary, layout and dispatch overhead around it",
            "low performance value": "prioritize correctness/API coverage unless profiling finds material runtime",
        }[disp]
        rows.append({
            "module": r["module"], "estimator": r["estimator"], "operation": r["operation"],
            "execution_class": r["execution_class"], "flow_scikit_status": r["flow_scikit_status"],
            "priority_score": round(score, 3), "disposition": disp, "hypothesis": hypothesis,
            "observed_flow_speedup": observed,
            "observed_flow_speedup_basis": basis,
            "end_to_end_flow_speedup": sum(end_to_end) / len(end_to_end) if end_to_end else None,
            "factors": {
                "substrate": substrate_factor, "python_share": python_share,
                "crossing_cost_proxy": crossing_factor, "allocation_proxy": alloc_factor,
                "observed_flow_speed": observed_factor, "implementation_readiness": implementation_factor,
                "native_reuse_penalty": native_reuse_penalty, "complexity_penalty": complexity_penalty,
            },
        })
    rows.sort(key=lambda x: x["priority_score"], reverse=True)
    args.json.write_text(json.dumps({"schema_version": 1, "provenance": provenance(args.headline), "rows": rows}, indent=2) + "\n")
    md = ["# Flow optimization roadmap", "", "Generated from committed inventory/profile/benchmark evidence.", "", "Observed Flow speedup is the mean over the estimator's canonical rows of the stage that times the operation: the fit stage for `fit`, the prediction stage for `predict`, `predict_proba`, `decision_function` and `transform`. The Basis column names the stage. End-to-end totals are kept in the JSON as `end_to_end_flow_speedup` and are not used for ranking.", "", "| Rank | Estimator | Operation | Substrate | Score | Disposition | Observed Flow speedup | Basis | Hypothesis |", "|---:|---|---|---|---:|---|---:|---|---|"]
    for i, r in enumerate(rows[:100], 1):
        observed = "" if r["observed_flow_speedup"] is None else f"{r['observed_flow_speedup']:.2f}×"
        basis = r["observed_flow_speedup_basis"] or ""
        md.append(f"| {i} | `{r['estimator']}` | `{r['operation']}` | {r['execution_class']} | {r['priority_score']:.1f} | {r['disposition']} | {observed} | {basis} | {r['hypothesis']} |")
    args.markdown.write_text("\n".join(md) + "\n")
    print(f"ranked {len(rows)} estimator operations; top={rows[0]['estimator']}.{rows[0]['operation'] if rows else 'n/a'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
