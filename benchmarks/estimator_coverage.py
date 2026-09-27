#!/usr/bin/env python3
"""Inventory every exported Flow estimator and say whether it can be raced.

The canonical benchmark covers 12 estimators. `lib/scikit` exports far more
than that, and a claim about Flow beating scikit-learn means very little while
the rest are unmeasured. This builds the registry the wider benchmark runs
from: every exported `*_fit`, its companion predict/transform, the arguments
to call it with, and the scikit-learn class to race it against.

An estimator lands in one of three buckets, and every one carries a reason:

  runnable   arguments resolved and a scikit-learn counterpart exists
  flow_only  Flow implements it and scikit-learn has no equivalent
  blocked    something about the signature is not resolved yet

Nothing is silently dropped. `blocked` entries name what is missing, so the
coverage number is honest about its own gaps.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "lib" / "scikit"
OUT = ROOT / "benchmarks" / "estimator_coverage.json"

FIT_RE = re.compile(r"^export function ([a-z_0-9]+)\(([^)]*)\)\s*->\s*([^{]+)\{", re.M)

# An implementation that says in its own comments that it is a simplified
# stand-in is not racing scikit-learn's algorithm, and timing it against one
# produces a number that means nothing. spectral_biclustering thresholds row
# and column means where scikit-learn does an SVD and k-means, and came out at
# 25106x. Detected from the source rather than listed here, so the registry
# stays true as the implementations are filled in.
SIMPLIFIED_RE = re.compile(
    r"#[^\n]*\b(simplified|simple approximation|placeholder|stub|not a real)\b", re.I
)

# Values for a hyperparameter, by parameter name. Chosen to be small and valid.
# This measures call cost on a fixed workload, so what matters is that every
# estimator gets arguments it will accept. Tuning them would not make the
# comparison more honest.
ARGS: dict[str, str] = {
    "seed": "42",
    "max_iter": "100",
    "n_components": "2",
    "alpha": "1.0",
    "lr": "0.01",
    "epochs": "50",
    "tol": "0.0001",
    "max_depth": "5",
    "gamma": "0.1",
    "n_trees": "10",
    "C": "1.0",
    "n_alphas": "10",
    "n_iter": "50",
    "n_clusters": "3",
    "degree": "2",
    "learning_rate": "0.1",
    "n_neighbors": "5",
    "batch_size": "32",
    "kernel": "0",
    "kernel_type": "0",
    "min_samples": "5",
    "threshold": "0.5",
    "coef0": "0.0",
    "strategy": "0",
    "n_estimators": "10",
    "nu": "0.5",
    "epsilon": "0.1",
    "n_outputs": "2",
    "criterion": "0",
    "max_features": "2",
    "k": "3",
    "n_features_to_select": "2",
    "radius": "1.0",
    "n_folds": "3",
    "method": "0",
    "eps": "0.5",
    "bandwidth": "1.0",
    "constant_value": "1.0",
    "n_base": "3",
    "n_nonzero_coefs": "3",
    "n_docs": "10",
    "loss": "0",
    "l1_ratio": "0.5",
    "mode": "0",
    "n_hidden": "1",
    "activation": "0",
    "momentum": "0.9",
    "handle_unknown": "0",
    "branching_factor": "50",
    "n_init": "1",
    "quantile": "0.5",
    "power": "1.5",
    "var_smoothing": "0.000000001",
    "shrinkage": "0.1",
    "reg_param": "0.1",
    "n_quantiles": "10",
    "n_bins": "4",
    "leaf_size": "30",
    "p": "2",
    "min_samples_split": "2",
    "min_samples_leaf": "1",
    "subsample": "1.0",
    "verbose": "0",
    "warm_start": "0",
    "n_jobs": "1",
    "cv": "3",
    "perplexity": "5.0",
    "early_exaggeration": "4.0",
    "n_neighbors_out": "5",
    "damping": "0.5",
    "preference": "0.0",
    "linkage": "0",
    "affinity": "0",
    "covariance_type": "0",
    "reg_covar": "0.000001",
    "weight_concentration": "1.0",
    "sample_steps": "2",
    "convergence_iter": "15",
    "contamination": "0.1",
    "n_trials": "10",
    "length_scale": "1.0",
    "min_cluster_size": "5",
    "n_topics": "3",
    "eta": "0.1",
    "n_Cs": "5",
    "h_fraction": "0.75",
    "missing_values": "0.0",
    "features": "0",
    "max_coefs": "3",
    "n_bits": "4",
    "output_distribution": "0",
    "outlier_label": "0.0",
    "max_trials": "10",
    "residual_threshold": "1.0",
    "cv_folds": "3",
    "score_func": "0",
    "percentile": "50",
    "direction": "0",
    "skewedness": "1.0",
    "density": "0.3",
    "n_row_clusters": "2",
    "n_col_clusters": "2",
    "n_knots": "4",
    "smoothing": "1.0",
    "n_subsamples": "10",
    "transformer_type": "0",
    "interaction_only": "false",
    "include_bias": "true",
    "increasing": "true",
    "n_labels": "3",
}

# Where one parameter name carries different meanings at different types,
# the type decides. `weights` is a scheme selector on KNNImputer and a vector
# of per-model weights on VotingRegressor.
TYPED_ARGS: dict[tuple[str, str], str] = {
    ("weights", "i32"): "0",
    ("penalty", "Penalty"): "penalty_none()",
    # Passed as a null callback, which is what lib/scikit's own RFECV does
    # when it calls rfe_fit internally.
    ("importance_fn", "ptr<void>"): "null",
    ("score_fn", "ptr<void>"): "null",
}

# Parameters that need a local built before the call. The generated harness
# emits the declaration, then passes the name.
PREAMBLE_ARGS: dict[str, tuple[str, str]] = {
    "hidden_sizes": ("array<i32, 1>", "[8]"),
    "n_categories": ("array<i32, 4>", "[4, 4, 4, 4]"),
}

# Parameters whose value depends on the dataset rather than on a constant.
DATASET_ARGS = {"n_classes", "n_samples", "n_features"}

# Flow names whose scikit-learn counterpart is not a case change away.
ALIASES: dict[str, str] = {
    # decomposition.flow, and it takes n_topics and eta, so this is Latent
    # Dirichlet Allocation. discriminant_analysis.flow holds the other one.
    "lda": "LatentDirichletAllocation",
    "discriminant_lda": "LinearDiscriminantAnalysis",
    "qda": "QuadraticDiscriminantAnalysis",
    "knn_classifier": "KNeighborsClassifier",
    "knn_regressor": "KNeighborsRegressor",
    "kernel_svc": "SVC",
    "kernel_svc_multi": "SVC",
    "linear_svc_multi": "LinearSVC",
    "lle": "LocallyLinearEmbedding",
    "nca": "NeighborhoodComponentsAnalysis",
    "omp_cv": "OrthogonalMatchingPursuitCV",
    "one_vs_one": "OneVsOneClassifier",
    "one_vs_rest": "OneVsRestClassifier",
    "output_code": "OutputCodeClassifier",
    "pls": "PLSRegression",
    "isotonic": "IsotonicRegression",
    "iterative_imputer": "IterativeImputer",
    "incremental_pca_partial": "IncrementalPCA",
    "ledoit_wolf_estimator": "LedoitWolf",
    "oas_estimator": "OAS",
    "multiclass_logistic": "LogisticRegression",
}

# Flow estimators with no scikit-learn equivalent to race against.
FLOW_ONLY: dict[str, str] = {
    "logistic_inference": "inference summary (coefficient standard errors, Wald tests); statsmodels territory",
    "ols_inference": "inference summary for ordinary least squares; statsmodels territory",
    "lssvm_classifier": "least-squares SVM; not in the scikit-learn public surface",
    "ledoit_wolf_cv": "cross-validated variant scikit-learn does not expose",
    "oas_cv": "cross-validated variant scikit-learn does not expose",
    "graphical_lasso_cv": "scikit-learn spells this GraphicalLassoCV; covered by that entry",
}


def fit_body(text: str, name: str) -> str:
    m = re.search(rf"^export function {re.escape(name)}\(.*?\n\}}", text, re.S | re.M)
    return m.group(0) if m else ""


def parse_exports() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted(LIB.glob("*.flow")):
        text = path.read_text()
        for m in FIT_RE.finditer(text):
            name, raw, ret = m.group(1), m.group(2), m.group(3).strip()
            params = []
            for p in raw.split(","):
                p = p.strip()
                if not p:
                    continue
                pname, _, ptype = p.partition(":")
                params.append({"name": pname.strip(), "type": ptype.strip()})
            entry = {"module": path.name, "params": params, "returns": ret}
            if name.endswith("_fit"):
                found = SIMPLIFIED_RE.search(fit_body(text, name))
                if found:
                    entry["simplified"] = found.group(1).lower()
            out[name] = entry
    return out


def companions(exports: dict[str, dict], base: str) -> dict[str, dict]:
    found = {}
    for suffix in ("predict", "transform", "decision_function", "predict_proba", "free"):
        name = f"{base}_{suffix}"
        if name in exports:
            spec = exports[name]
            found[suffix] = {
                "name": name,
                "returns": spec["returns"],
                "parameters": [{"name": q["name"], "type": q["type"]} for q in spec["params"]],
            }
    return found


def sklearn_name(base: str, known: set[str]) -> str | None:
    if base in ALIASES:
        return ALIASES[base]
    flat = base.replace("_", "")
    for candidate in known:
        if candidate.lower() == flat:
            return candidate
    return None


def classify(base: str, spec: dict, known: set[str], exports: dict[str, dict]) -> dict:
    entry = {
        "flow_estimator": base,
        "module": spec["module"],
        "fit": {
            "name": f"{base}_fit",
            "returns": spec["returns"],
            "parameters": [{"name": p["name"], "type": p["type"]} for p in spec["params"]],
        },
        "companions": companions(exports, base),
        "parameters": [p["name"] for p in spec["params"]],
    }
    if base in FLOW_ONLY:
        entry.update(bucket="flow_only", reason=FLOW_ONLY[base])
        return entry
    if "simplified" in spec:
        entry.update(
            bucket="simplified",
            reason=f"the implementation's own comments call it {spec['simplified']}, "
                   "so timing it against scikit-learn's algorithm compares two different things",
            sklearn_estimator=sklearn_name(base, known),
        )
        return entry

    unresolved = []
    for p in spec["params"][1:]:
        if p["name"] in ("y", "Y", "X"):
            continue
        if p["name"] in DATASET_ARGS:
            continue
        if (p["name"], p["type"]) in TYPED_ARGS or p["name"] in ARGS or p["name"] in PREAMBLE_ARGS:
            continue
        unresolved.append(f"{p['name']}: {p['type']}")
    head = spec["params"][0]["type"] if spec["params"] else "absent"
    sk = sklearn_name(base, known)
    if head != "Matrix":
        entry.update(
            bucket="different_shape",
            reason=f"takes {head} first, so it is not an estimator over a feature matrix and needs its own harness",
            sklearn_estimator=sk,
        )
        return entry
    if unresolved:
        entry.update(bucket="blocked", reason="no value for " + "; ".join(unresolved), sklearn_estimator=sk)
        return entry
    if sk is None:
        entry.update(bucket="blocked", reason="no scikit-learn counterpart found by name; add an alias or a flow_only reason")
        return entry
    entry.update(bucket="runnable", sklearn_estimator=sk)
    return entry


def argument_tables() -> dict:
    return {"ARGS": ARGS, "TYPED_ARGS": TYPED_ARGS, "PREAMBLE_ARGS": PREAMBLE_ARGS, "DATASET_ARGS": sorted(DATASET_ARGS)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--show", choices=["blocked", "flow_only", "runnable", "simplified", "different_shape"], help="list one bucket and exit")
    args = ap.parse_args()

    exports = parse_exports()
    inventory = json.loads((ROOT / "benchmarks" / "sklearn_execution_inventory.json").read_text())
    rows = inventory["rows"] if isinstance(inventory, dict) else inventory
    known = {r["estimator"] for r in rows}

    entries = []
    for name, spec in sorted(exports.items()):
        if not name.endswith("_fit"):
            continue
        entries.append(classify(name[:-4], spec, known, exports))

    counts: dict[str, int] = {}
    for e in entries:
        counts[e["bucket"]] = counts.get(e["bucket"], 0) + 1

    payload = {
        "schema_version": 1,
        "counts": {"estimators": len(entries), **counts},
        "sklearn_surface": len(known),
        "entries": entries,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n")

    if args.show:
        for e in entries:
            if e["bucket"] == args.show:
                print(f"{e['flow_estimator']:34s} {e.get('reason', e.get('sklearn_estimator',''))}")
        return 0

    print(f"{len(entries)} exported Flow estimators against a {len(known)}-estimator scikit-learn surface")
    for bucket in ("runnable", "simplified", "different_shape", "flow_only", "blocked"):
        print(f"  {bucket:10s} {counts.get(bucket, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
