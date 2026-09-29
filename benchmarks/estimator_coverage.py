#!/usr/bin/env python3
"""Inventory every exported Flow estimator and say whether it can be raced.

The canonical benchmark covers 12 estimators. `lib/scikit` exports far more
than that, and a claim about Flow beating scikit-learn means very little while
the rest are unmeasured. This builds the registry the wider benchmark runs
from: every exported `*_fit`, its companion predict/transform, the arguments
to call it with, and the scikit-learn class to race it against.

An estimator lands in one of these buckets, and every one carries a reason:

  runnable   arguments resolved and a scikit-learn counterpart exists
  shaped     raced through a written out call, because its fit does not begin
             with a feature matrix
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

# Flow functions whose scikit-learn namesake does more than they do. Timing
# them against that class would compare a part against the whole, which is the
# same objection the simplified rows carry. The wording says which part.
DIFFERENT_JOB: dict[str, str] = {
    "stacking_classifier": "takes the base estimators' predictions as input, so it is the "
                           "meta-learner alone. stacking_classifier_full_fit does the whole "
                           "job and is the row that races StackingClassifier",
    "self_training_classifier": "takes class probabilities as input, so it is the labelling "
                                "loop alone. self_training_classifier_full_fit refits the base "
                                "estimator every round and is the row that races the class",
    "voting_classifier": "takes trees that are already fitted, so its fit is the vote alone. "
                         "voting_classifier_full_fit fits the ensemble and is the row that "
                         "races VotingClassifier",
    "voting_regressor": "takes regressors that are already fitted, so its fit is the average "
                        "alone. voting_regressor_full_fit fits the ensemble and is the row "
                        "that races VotingRegressor",
    "incremental_pca_partial": "one partial_fit step over one batch. incremental_pca_fit walks "
                               "the whole design in batches and is the row that races "
                               "IncrementalPCA",
}

# One corpus for the two text vectorizers, read by the Flow generator and by
# the scikit-learn harness, so the two sides cannot drift apart.
CORPUS: list[str] = [
    "the quick brown fox jumps over the lazy dog",
    "a lazy dog sleeps in the warm sun",
    "quick brown foxes are rare in the city",
    "the dog and the fox share a field",
    "warm sun and a cold river run together",
    "a field of brown grass in the sun",
    "the city river runs past the old field",
    "old dogs sleep through a quick storm",
    "a storm over the city wakes the dog",
    "foxes hunt in the cold river valley",
    "the valley holds a warm field of grass",
    "grass grows where the river meets the sun",
    "a rare fox crosses the old stone bridge",
    "the stone bridge over the cold river",
    "dogs and foxes keep their distance here",
    "here the field the river and the city meet",
]

# Estimators whose fit does not begin with a feature matrix, and which race
# scikit-learn perfectly well once the call is written out. Thirteen rows sat
# in different_shape only because the generic path builds one call shape.
#
# `flow_fit` and `flow_work` are argument expressions in terms of the variables
# the generated harness declares (X_c, y_c, n_c, f_c and the regression pair).
# `sklearn_input` says what the scikit-learn side fits and transforms: the
# feature matrix, the target vector, or the first column of the matrix as a
# one-dimensional x. `sklearn_ctor` overrides the constructor where the default
# would measure a different size of problem, as it would for a random
# projection whose n_components is chosen by Johnson-Lindenstrauss.
SHAPED: dict[str, dict] = {
    "additive_chi2_sampler": {
        "dataset": "classification",
        "flow_fit": ["n_c", "f_c", "2"],
        "flow_work": ["X_c"],
        "sklearn_input": "X",
    },
    "gaussian_random_projection": {
        "dataset": "classification",
        "flow_fit": ["f_c", "2", "42"],
        "flow_work": ["X_c"],
        "sklearn_input": "X",
        "sklearn_ctor": "n_components=2, random_state=42",
    },
    "polynomial_count_sketch": {
        "dataset": "classification",
        "flow_fit": ["f_c", "2", "2"],
        "flow_work": ["X_c"],
        "sklearn_input": "X",
        "sklearn_ctor": "n_components=2, degree=2, random_state=42",
    },
    "polynomial_features": {
        "dataset": "classification",
        "flow_fit": ["f_c", "2", "false", "true"],
        "flow_work": ["X_c"],
        "sklearn_input": "X",
    },
    "rbf_sampler": {
        "dataset": "classification",
        "flow_fit": ["f_c", "0.1", "2", "42"],
        "flow_work": ["X_c"],
        "sklearn_input": "X",
        "sklearn_ctor": "gamma=0.1, n_components=2, random_state=42",
    },
    "skewed_chi2_sampler": {
        "dataset": "classification",
        "flow_fit": ["f_c", "1.0", "2", "42"],
        "flow_work": ["X_c"],
        "sklearn_input": "X",
        "sklearn_ctor": "skewedness=1.0, n_components=2, random_state=42",
    },
    "sparse_random_projection": {
        "dataset": "classification",
        "flow_fit": ["f_c", "2", "0.3", "42"],
        "flow_work": ["X_c"],
        "sklearn_input": "X",
        "sklearn_ctor": "n_components=2, density=0.3, random_state=42",
    },
    "select_from_model": {
        "dataset": "classification",
        "flow_fit": ["w_f", "f_c", "0.5"],
        "flow_work": ["X_c"],
        "sklearn_input": "X",
    },
    "dummy_classifier": {
        "dataset": "classification",
        "flow_fit": ["y_c", "n_c", "3", "0", "0.0", "42"],
        "flow_work": ["n_c"],
        "sklearn_input": "X",
    },
    "dummy_regressor": {
        "dataset": "regression",
        "flow_fit": ["y_r", "n_r", "0", "0.0"],
        "flow_work": ["n_r"],
        "sklearn_input": "X",
    },
    "label_encoder": {
        "dataset": "classification",
        "flow_fit": ["y_c", "n_c"],
        "flow_work": ["y_c", "n_c"],
        "sklearn_input": "y",
    },
    "label_binarizer": {
        "dataset": "classification",
        "flow_fit": ["y_c", "n_c", "0.0", "1.0"],
        "flow_work": ["y_c", "n_c"],
        "sklearn_input": "y",
    },
    "isotonic": {
        "dataset": "regression",
        "flow_fit": ["x1d_r", "y_r", "n_r", "true"],
        "flow_work": ["x1d_r", "n_r"],
        "sklearn_input": "x1d",
    },
    # Two rows whose work function is named for what it returns rather than
    # predict or transform, so the generic path found nothing to time and the
    # fit alone fell under the clock's floor.
    "voting_classifier_full": {
        "dataset": "classification",
        "flow_fit": ["X_c", "y_c", "3", "3", "3", "42", "0"],
        "flow_work": ["X_c"],
        "flow_work_fn": "voting_classifier_predict",
        "flow_work_returns": "ptr<f32>",
        "flow_free_fn": "voting_classifier_free",
        "sklearn_input": "X",
    },
    "voting_regressor_full": {
        "dataset": "regression",
        "flow_fit": ["X_r", "y_r", "3", "3", "42"],
        "flow_work": ["X_r"],
        "flow_work_fn": "voting_regressor_predict",
        "flow_work_returns": "ptr<f32>",
        "flow_free_fn": "voting_regressor_free",
        "sklearn_input": "X",
    },
    "stacking_classifier_full": {
        "dataset": "classification",
        "flow_fit": ["X_c", "y_c", "3", "3", "3", "42", "0.01", "50"],
        "flow_work": ["X_c"],
        "flow_work_fn": "stacking_classifier_full_predict",
        "flow_work_returns": "ptr<f32>",
        "flow_free_fn": "stacking_classifier_full_free",
        "sklearn_input": "X",
    },
    "self_training_classifier_full": {
        # Every third row keeps its label and the rest are unlabelled, on both
        # sides, which is the shape the estimator exists for.
        "dataset": "classification",
        "flow_preamble": [
            "let st_labels: ptr<i32> = malloc((n_c as i64) * 4 + 64) as ptr<i32>",
            "for i in 0 to n_c {",
            "    if i % 3 == 0 { st_labels[i] = yi_c[i] }",
            "    else { st_labels[i] = 0 - 1 }",
            "}",
        ],
        "flow_fit": ["X_c", "st_labels", "3", "0.7", "10", "50", "0.1"],
        "sklearn_input": "semi_labels",
    },
    "kernel_density": {
        "dataset": "classification",
        "flow_fit": ["X_c", "0.5", "0"],
        "flow_work": ["X_c"],
        "flow_work_fn": "kernel_density_score_samples",
        "flow_work_returns": "ptr<f32>",
        "sklearn_input": "X",
        "sklearn_work": "score_samples",
    },
    "nearest_neighbors": {
        "dataset": "classification",
        "flow_fit": ["X_c", "5"],
        "flow_work": ["X_c"],
        "flow_work_fn": "nearest_neighbors_kneighbors",
        "flow_work_returns": "ptr<NeighborResult>",
        "flow_work_release": "nearest_neighbors_free_results({var}, n_c)",
        "sklearn_input": "X",
        "sklearn_work": "kneighbors",
    },
    "multilabel_binarizer": {
        # The label rows, so the scikit-learn side gets sets of labels rather
        # than one label per sample.
        "dataset": "multioutput_class",
        "flow_preamble": [
            "let mlb_counts: ptr<i32> = malloc((n_c as i64) * 4) as ptr<i32>",
            "for i in 0 to n_c { mlb_counts[i] = 2 }",
        ],
        "flow_fit": ["Y_label_rows", "n_c", "mlb_counts", "3"],
        "flow_work": ["Y_label_rows", "n_c", "mlb_counts"],
        "sklearn_input": "labelsets",
    },
    "dict_vectorizer": {
        "dataset": "classification",
        "flow_preamble": [
            "let dv_counts: ptr<i32> = malloc((n_c as i64) * 4) as ptr<i32>",
            "let dv_keys: ptr<ptr<i32> > = malloc((n_c as i64) * 8) as ptr<ptr<i32> >",
            "let dv_vals: ptr<ptr<f32> > = malloc((n_c as i64) * 8) as ptr<ptr<f32> >",
            "for i in 0 to n_c {",
            "    dv_counts[i] = f_c",
            "    let dv_kk: ptr<i32> = malloc((f_c as i64) * 4) as ptr<i32>",
            "    let dv_vv: ptr<f32> = array_new_f32(f_c)",
            "    for j in 0 to f_c {",
            "        dv_kk[j] = j",
            "        dv_vv[j] = matrix_at(X_c, i, j)",
            "    }",
            "    dv_keys[i] = dv_kk",
            "    dv_vals[i] = dv_vv",
            "}",
        ],
        "flow_fit": ["dv_keys", "dv_vals", "n_c", "dv_counts"],
        "flow_work": ["dv_keys", "dv_vals", "n_c", "dv_counts"],
        "sklearn_input": "dicts",
    },
    "count_vectorizer": {
        "dataset": "classification",
        "corpus": CORPUS,
        "flow_fit": ["count_vectorizer_docs", "16", "50"],
        "flow_work": ["count_vectorizer_docs", "16"],
        "sklearn_input": "docs",
    },
    "tfidf_vectorizer": {
        "dataset": "classification",
        "corpus": CORPUS,
        "flow_fit": ["tfidf_vectorizer_docs", "16", "50"],
        "flow_work": ["tfidf_vectorizer_docs", "16"],
        "sklearn_input": "docs",
    },
    "pipeline": {
        "dataset": "classification",
        "flow_preamble": [
            "let pipe_steps: array<PipelineStep, 2> = [",
            '    step_standard_scaler("scaler"),',
            '    step_logistic_regression("classifier", 3, 50, 0.5, penalty_none())',
            "]",
            "let pipe_obj: Pipeline = pipeline_new(pipe_steps, 2)",
        ],
        "flow_fit": ["pipe_obj", "X_c", "y_c"],
        "flow_work": ["X_c"],
        "flow_free": "after",
        "sklearn_input": "X",
    },
    "column_transformer": {
        "dataset": "classification",
        "flow_preamble": [
            "let ct_cols: ptr<i32> = malloc((f_c as i64) * 4) as ptr<i32>",
            "for i in 0 to f_c { ct_cols[i] = i }",
            "let ct_obj: ColumnTransformer = column_transformer_init(1)",
            "# 0 is TRANSFORMER_STANDARD_SCALER. The constant is written out",
            "# because an export const is not visible through the umbrella import.",
            "column_transformer_set_spec(ct_obj, 0, 0, ct_cols, f_c)",
        ],
        "flow_fit": ["ct_obj", "X_c"],
        "flow_work": ["X_c"],
        "flow_free": "after",
        "sklearn_input": "X",
    },
    "feature_union": {
        "dataset": "classification",
        "flow_preamble": [
            "let fu_obj: FeatureUnion = feature_union_init(2)",
            "# 0 is FU_TRANSFORMER_STANDARD_SCALER and 2 is FU_TRANSFORMER_PASSTHROUGH,",
            "# written out for the reason the column transformer above gives.",
            "feature_union_set_transformer(fu_obj, 0, 0, 0)",
            "feature_union_set_transformer(fu_obj, 1, 2, 0)",
        ],
        "flow_fit": ["fu_obj", "X_c"],
        "flow_work": ["X_c"],
        "flow_free": "after",
        "sklearn_input": "X",
    },
}

# Parameters whose value depends on the dataset rather than on a constant.
DATASET_ARGS = {"n_classes", "n_samples", "n_features"}

# Flow names whose scikit-learn counterpart is not a case change away.
ALIASES: dict[str, str] = {
    # The full fits, which do what the scikit-learn class does rather than the
    # part of it the older function covers. Both entries stay in the registry:
    # the older one keeps its reason for not being raced.
    "voting_classifier_full": "VotingClassifier",
    "voting_regressor_full": "VotingRegressor",
    "stacking_classifier_full": "StackingClassifier",
    "self_training_classifier_full": "SelfTrainingClassifier",
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
    if base in SHAPED and sk is not None:
        entry.update(bucket="shaped", sklearn_estimator=sk, shape=SHAPED[base])
        return entry
    if base in DIFFERENT_JOB:
        entry.update(bucket="different_shape", reason=DIFFERENT_JOB[base], sklearn_estimator=sk)
        return entry
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
    ap.add_argument("--show", choices=["blocked", "flow_only", "runnable", "shaped", "simplified",
                                       "different_shape"], help="list one bucket and exit")
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
    for bucket in ("runnable", "shaped", "simplified", "different_shape", "flow_only", "blocked"):
        print(f"  {bucket:10s} {counts.get(bucket, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
