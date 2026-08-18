#!/usr/bin/env python3
"""Canonical sklearn side of the 19-row headline benchmark.

This runner consumes persisted split fixtures, measures fit/predict latency with
aggregate timing windows, and emits explicit clustering/decomposition details.
"""
from __future__ import annotations

import json
import platform

import numpy as np
import sklearn
from sklearn.cluster import KMeans
from sklearn.datasets import load_diabetes, load_digits, load_iris
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import Lasso, LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, adjusted_rand_score, mean_squared_error, r2_score
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier

from fixtures import split_arrays
from timing import measure

TIMING_UNIT = "ms"
MODE = "end_to_end"


def emit_result(name, dataset, metric, score, fit_t, pred_t):
    print(
        "RESULT|{}|{}|{}|{:.9g}|{:.9g}|{:.9g}|{:.9g}|{:.9g}|{}|{}".format(
            name,
            dataset,
            metric,
            float(score),
            fit_t.median_ms,
            pred_t.median_ms,
            fit_t.iqr_ms,
            pred_t.iqr_ms,
            fit_t.repeats_per_sample,
            pred_t.repeats_per_sample,
        )
    )


def emit_detail(name, dataset, key, value):
    if isinstance(value, (list, tuple, np.ndarray)):
        rendered = ",".join(f"{float(v):.9g}" for v in value)
    else:
        rendered = f"{float(value):.9g}"
    print(f"DETAIL|{name}|{dataset}|{key}|{rendered}")


def prepared(dataset, X, y):
    X_train, X_test, y_train, y_test = split_arrays(dataset, X, y)
    scaler = StandardScaler().fit(X_train)
    return scaler.transform(X_train), scaler.transform(X_test), y_train, y_test


def supervised(name, dataset, X_train, X_test, y_train, y_test, fit_fn, predict_fn, metric):
    fit_t = measure(lambda: fit_fn(X_train, y_train))
    model = fit_t.value
    pred_t = measure(lambda: predict_fn(model, X_test))
    preds = pred_t.value
    if metric == "accuracy":
        score = accuracy_score(y_test, preds)
    elif metric == "r2":
        score = r2_score(y_test, preds)
    else:
        raise ValueError(metric)
    emit_result(name, dataset, metric, score, fit_t, pred_t)
    return model


def kmeans_row(dataset, X_train, X_test, y_train, y_test, n_clusters):
    fit_t = measure(
        lambda: KMeans(
            n_clusters=n_clusters,
            init="k-means++",
            n_init=10,
            max_iter=100,
            tol=0.001,
            random_state=42,
        ).fit(X_train)
    )
    model = fit_t.value
    pred_t = measure(lambda: model.predict(X_test))
    labels = pred_t.value
    ari = adjusted_rand_score(y_test.astype(int), labels)
    emit_result("KMeans", dataset, "adjusted_rand_index", ari, fit_t, pred_t)
    emit_detail("KMeans", dataset, "inertia", model.inertia_)
    emit_detail("KMeans", dataset, "n_iter", model.n_iter_)
    emit_kmeans_state(dataset, model)


def pca_row(X_train, X_test):
    fit_t = measure(lambda: PCA(n_components=2).fit(X_train))
    model = fit_t.value
    pred_t = measure(lambda: model.transform(X_test))
    transformed = pred_t.value
    reconstructed = model.inverse_transform(transformed)
    score = float(np.sum(model.explained_variance_ratio_))
    emit_result("PCA", "iris", "explained_var_ratio", score, fit_t, pred_t)
    emit_detail("PCA", "iris", "explained_variance_ratio", model.explained_variance_ratio_)
    emit_detail("PCA", "iris", "singular_values", model.singular_values_)
    emit_detail("PCA", "iris", "reconstruction_mse", mean_squared_error(X_test, reconstructed))
    emit_detail("PCA", "iris", "component_0", model.components_[0])
    emit_detail("PCA", "iris", "component_1", model.components_[1])


# ---------------------------------------------------------------------------
# Model-state diagnostics (issue #207).
#
# Each emitter mirrors, key for key, the DETAIL records that
# benchmarks/bench_flow_v2.flow writes for the same canonical row, so
# generate_disparity_report.py can pair them into model_state_diagnostics.
# All of it runs outside the timing windows.
# ---------------------------------------------------------------------------


def _bootstrap_indices(random_state, n_samples):
    """Reproduce sklearn.ensemble._forest._generate_sample_indices without the
    private import: check_random_state(seed).randint(0, n, n)."""
    return np.random.RandomState(random_state).randint(0, n_samples, n_samples)


def _tree_depths(tree):
    depths = np.zeros(tree.node_count, dtype=np.int64)
    for i in range(tree.node_count):
        left = tree.children_left[i]
        right = tree.children_right[i]
        if left != -1:
            depths[left] = depths[i] + 1
        if right != -1:
            depths[right] = depths[i] + 1
    return depths


def _is_leaf(tree):
    return tree.children_left == -1


def _root_split(tree):
    """(feature, threshold) of the root, using -1/0.0 when the root is a leaf."""
    if tree.node_count == 0 or tree.children_left[0] == -1:
        return -1, 0.0
    return int(tree.feature[0]), float(tree.threshold[0])


def emit_ovr_state(name, dataset, coef, intercept, classes):
    """Coefficient-block state shared by LogisticRegression and LinearSVC."""
    order = np.argsort(classes)
    coef = np.asarray(coef, dtype=np.float64)[order]
    intercept = np.atleast_1d(np.asarray(intercept, dtype=np.float64))[order]
    row_norms = np.linalg.norm(coef, axis=1)
    emit_detail(name, dataset, "classes", np.asarray(classes, dtype=np.float64)[order])
    emit_detail(name, dataset, "coef_frobenius_norm", float(np.linalg.norm(coef)))
    emit_detail(name, dataset, "coef_abs_sum", float(np.abs(coef).sum()))
    emit_detail(name, dataset, "coef_row_l2_norms", row_norms)
    emit_detail(name, dataset, "intercepts", intercept)


def emit_linear_state(name, dataset, model):
    coef = np.asarray(model.coef_, dtype=np.float64).ravel()
    emit_detail(name, dataset, "coef", coef)
    emit_detail(name, dataset, "intercept", float(np.ravel(model.intercept_)[0]))
    emit_detail(name, dataset, "coef_l2_norm", float(np.linalg.norm(coef)))
    emit_detail(name, dataset, "coef_abs_sum", float(np.abs(coef).sum()))
    emit_detail(name, dataset, "n_zero_coefs", int((coef == 0.0).sum()))


def emit_gnb_state(dataset, model):
    order = np.argsort(model.classes_)
    theta = np.asarray(model.theta_, dtype=np.float64)[order]
    var = np.asarray(model.var_, dtype=np.float64)[order]
    emit_detail("GaussianNB", dataset, "classes", np.asarray(model.classes_, dtype=np.float64)[order])
    emit_detail("GaussianNB", dataset, "class_priors", np.asarray(model.class_prior_, dtype=np.float64)[order])
    emit_detail("GaussianNB", dataset, "theta_row_l2_norms", np.linalg.norm(theta, axis=1))
    emit_detail("GaussianNB", dataset, "var_row_l2_norms", np.linalg.norm(var, axis=1))
    emit_detail("GaussianNB", dataset, "theta_frobenius_norm", float(np.linalg.norm(theta)))
    emit_detail("GaussianNB", dataset, "var_frobenius_norm", float(np.linalg.norm(var)))
    emit_detail("GaussianNB", dataset, "var_min", float(var.min()))
    emit_detail("GaussianNB", dataset, "var_max", float(var.max()))


def emit_tree_state(dataset, model, n_features, depth_cap):
    tree = model.tree_
    depths = _tree_depths(tree)
    leaf = _is_leaf(tree)
    internal_features = tree.feature[~leaf]

    per_depth = np.zeros(depth_cap + 1, dtype=np.int64)
    for d in depths:
        if 0 <= d <= depth_cap:
            per_depth[d] += 1

    hist = np.zeros(n_features, dtype=np.int64)
    for f in internal_features:
        if 0 <= f < n_features:
            hist[f] += 1

    leaf_samples = tree.n_node_samples[leaf].astype(np.float64)
    child_split = [-1.0, 0.0, -1.0, 0.0]
    if tree.node_count > 0 and tree.children_left[0] != -1:
        for slot, child in ((0, tree.children_left[0]), (2, tree.children_right[0])):
            if tree.children_left[child] != -1:
                child_split[slot] = float(tree.feature[child])
                child_split[slot + 1] = float(tree.threshold[child])

    root_feature, root_threshold = _root_split(tree)
    emit_detail("DecisionTree", dataset, "n_nodes", int(tree.node_count))
    emit_detail("DecisionTree", dataset, "n_leaves", int(leaf.sum()))
    emit_detail("DecisionTree", dataset, "max_depth_reached", int(depths.max()) if tree.node_count else 0)
    emit_detail("DecisionTree", dataset, "root_split_feature", root_feature)
    emit_detail("DecisionTree", dataset, "root_split_threshold", root_threshold)
    emit_detail("DecisionTree", dataset, "root_impurity", float(tree.impurity[0]))
    emit_detail("DecisionTree", dataset, "depth1_splits", child_split)
    emit_detail("DecisionTree", dataset, "nodes_per_depth", per_depth)
    emit_detail("DecisionTree", dataset, "split_feature_histogram", hist)
    mean_leaf_depth = 0.0
    if leaf_samples.sum() > 0:
        mean_leaf_depth = float((depths[leaf] * leaf_samples).sum() / leaf_samples.sum())
    emit_detail("DecisionTree", dataset, "mean_leaf_depth", mean_leaf_depth)
    emit_detail("DecisionTree", dataset, "preorder_split_features",
                np.where(leaf, -1.0, tree.feature.astype(np.float64)))
    emit_detail("DecisionTree", dataset, "preorder_split_thresholds",
                np.where(leaf, 0.0, tree.threshold.astype(np.float64)))


def emit_forest_state(dataset, model, X_test, n_train):
    estimators = model.estimators_
    node_counts = [int(e.tree_.node_count) for e in estimators]
    leaf_counts = [int(_is_leaf(e.tree_).sum()) for e in estimators]
    max_depths = [int(e.tree_.max_depth) for e in estimators]
    roots = [_root_split(e.tree_) for e in estimators]
    root_impurities = [float(e.tree_.impurity[0]) for e in estimators]

    boot_sums = []
    boot_unique = []
    for e in estimators:
        idx = _bootstrap_indices(e.random_state, n_train)
        boot_sums.append(float(idx.sum()))
        boot_unique.append(float(np.unique(idx).size) / float(n_train))

    votes = np.stack([e.predict(X_test) for e in estimators])
    classes = model.classes_
    counts = np.stack([(votes == c).sum(axis=0) for c in classes]).T.astype(np.float64)
    counts /= float(len(estimators))
    ordered = np.sort(counts, axis=1)
    top = ordered[:, -1]
    second = ordered[:, -2] if counts.shape[1] > 1 else np.zeros_like(top)

    emit_detail("RandomForest", dataset, "n_trees", len(estimators))
    emit_detail("RandomForest", dataset, "max_features_per_split", int(getattr(model, "max_features_", int(np.sqrt(model.n_features_in_)))))
    emit_detail("RandomForest", dataset, "tree_node_counts", node_counts)
    emit_detail("RandomForest", dataset, "tree_leaf_counts", leaf_counts)
    emit_detail("RandomForest", dataset, "tree_max_depths", max_depths)
    emit_detail("RandomForest", dataset, "tree_root_features", [r[0] for r in roots])
    emit_detail("RandomForest", dataset, "tree_root_thresholds", [r[1] for r in roots])
    emit_detail("RandomForest", dataset, "tree_root_impurities", root_impurities)
    emit_detail("RandomForest", dataset, "bootstrap_index_sums", boot_sums)
    emit_detail("RandomForest", dataset, "bootstrap_unique_fractions", boot_unique)
    emit_detail("RandomForest", dataset, "tree_feature_seeds", [int(e.random_state) for e in estimators])
    emit_detail("RandomForest", dataset, "mean_vote_margin", float(np.mean(top - second)))
    emit_detail("RandomForest", dataset, "mean_top_vote_fraction", float(np.mean(top)))
    emit_detail("RandomForest", dataset, "unanimous_vote_fraction", float(np.mean(top >= 0.999999)))


def emit_ksvc_state(dataset, model, y_train):
    """One-vs-one state, unpacked from the libsvm dual_coef_ block layout.

    dual_coef_ has shape (n_classes - 1, n_SV) with support vectors grouped by
    class. For the pair (i, j) with i < j, the class-i coefficients live in row
    j-1 of that class's slice and the class-j coefficients in row i.
    """
    classes = model.classes_
    n_class = len(classes)
    n_sup = np.asarray(model.n_support_, dtype=np.int64)
    starts = np.concatenate([[0], np.cumsum(n_sup)])[:-1]
    dual = np.asarray(model.dual_coef_, dtype=np.float64)
    C = float(model.C)
    bound = C - 1e-6

    pair_a, pair_b, sizes, n_support, n_bounded, abs_sums = [], [], [], [], [], []
    for i in range(n_class):
        for j in range(i + 1, n_class):
            block = np.concatenate([
                dual[j - 1, starts[i]:starts[i] + n_sup[i]],
                dual[i, starts[j]:starts[j] + n_sup[j]],
            ])
            nonzero = block[np.abs(block) > 1e-6]
            pair_a.append(float(classes[i]))
            pair_b.append(float(classes[j]))
            sizes.append(int(np.sum(y_train == classes[i]) + np.sum(y_train == classes[j])))
            n_support.append(int(nonzero.size))
            n_bounded.append(int((np.abs(nonzero) >= bound).sum()))
            abs_sums.append(float(np.abs(nonzero).sum()))

    emit_detail("KernelSVC_RBF", dataset, "gamma", float(getattr(model, "_gamma", model.gamma)))
    emit_detail("KernelSVC_RBF", dataset, "C", C)
    emit_detail("KernelSVC_RBF", dataset, "n_pairs", len(pair_a))
    emit_detail("KernelSVC_RBF", dataset, "n_support_total", int(sum(n_support)))
    emit_detail("KernelSVC_RBF", dataset, "pair_class_a", pair_a)
    emit_detail("KernelSVC_RBF", dataset, "pair_class_b", pair_b)
    emit_detail("KernelSVC_RBF", dataset, "pair_train_sizes", sizes)
    emit_detail("KernelSVC_RBF", dataset, "n_support_per_pair", n_support)
    emit_detail("KernelSVC_RBF", dataset, "n_bounded_support_per_pair", n_bounded)
    emit_detail("KernelSVC_RBF", dataset, "dual_coef_abs_sum_per_pair", abs_sums)
    emit_detail("KernelSVC_RBF", dataset, "intercept_per_pair", np.asarray(model.intercept_, dtype=np.float64))


def emit_krr_state(dataset, model):
    dual = np.asarray(model.dual_coef_, dtype=np.float64).ravel()
    emit_detail("KernelRidge_RBF", dataset, "alpha", float(model.alpha))
    emit_detail("KernelRidge_RBF", dataset, "gamma", float(model.gamma))
    emit_detail("KernelRidge_RBF", dataset, "n_train_samples", int(dual.size))
    emit_detail("KernelRidge_RBF", dataset, "dual_coef_l2_norm", float(np.linalg.norm(dual)))
    emit_detail("KernelRidge_RBF", dataset, "dual_coef_abs_sum", float(np.abs(dual).sum()))
    emit_detail("KernelRidge_RBF", dataset, "dual_coef_min", float(dual.min()))
    emit_detail("KernelRidge_RBF", dataset, "dual_coef_max", float(dual.max()))
    emit_detail("KernelRidge_RBF", dataset, "dual_coef_mean", float(dual.mean()))


def emit_kmeans_state(dataset, model):
    norms = np.sort(np.linalg.norm(np.asarray(model.cluster_centers_, dtype=np.float64), axis=1))
    sizes = np.sort(np.bincount(model.labels_, minlength=model.n_clusters))[::-1]
    emit_detail("KMeans", dataset, "center_l2_norms_sorted", norms)
    emit_detail("KMeans", dataset, "train_cluster_sizes_sorted", sizes)


def main() -> int:
    env = {
        "impl": "sklearn",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "sklearn": sklearn.__version__,
        "numpy": np.__version__,
    }
    print(f"TIMING_UNIT|{TIMING_UNIT}")
    print(f"BENCHMARK_MODE|{MODE}")
    print("FIXTURE_SOURCE|benchmarks/split_indices.json")
    print("BENCHMARK_ENV|" + json.dumps(env, sort_keys=True, separators=(",", ":")))

    iris = load_iris()
    X_i = iris.data.astype(np.float32)
    y_i = iris.target.astype(np.float32)
    Xi_tr, Xi_te, yi_tr, yi_te = prepared("iris", X_i, y_i)

    model = supervised("LogisticRegression", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: LogisticRegression(max_iter=1000, C=1.0).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_ovr_state("LogisticRegression", "iris", model.coef_, model.intercept_, model.classes_)
    model = supervised("LinearSVC", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: LinearSVC(max_iter=1000, C=1.0, dual="auto").fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_ovr_state("LinearSVC", "iris", model.coef_, model.intercept_, model.classes_)
    model = supervised("KernelSVC_RBF", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: SVC(C=1.0, gamma=0.25, max_iter=1000).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_ksvc_state("iris", model, yi_tr)
    model = supervised("DecisionTree", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: DecisionTreeClassifier(max_depth=5, random_state=42).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_tree_state("iris", model, Xi_tr.shape[1], 5)
    model = supervised("RandomForest", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_forest_state("iris", model, Xi_te, Xi_tr.shape[0])
    model = supervised("GaussianNB", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: GaussianNB(var_smoothing=1e-9).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_gnb_state("iris", model)
    kmeans_row("iris", Xi_tr, Xi_te, yi_tr, yi_te, 3)
    pca_row(Xi_tr, Xi_te)

    digits = load_digits()
    X_d = digits.data.astype(np.float32)
    y_d = digits.target.astype(np.float32)
    Xd_tr, Xd_te, yd_tr, yd_te = prepared("digits", X_d, y_d)
    model = supervised("LogisticRegression", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: LogisticRegression(max_iter=1000, C=1.0).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_ovr_state("LogisticRegression", "digits", model.coef_, model.intercept_, model.classes_)
    model = supervised("LinearSVC", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: LinearSVC(max_iter=1000, C=1.0, dual="auto").fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_ovr_state("LinearSVC", "digits", model.coef_, model.intercept_, model.classes_)
    model = supervised("KernelSVC_RBF", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: SVC(C=1.0, gamma=0.001, max_iter=1000).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_ksvc_state("digits", model, yd_tr)
    model = supervised("DecisionTree", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: DecisionTreeClassifier(max_depth=10, random_state=42).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_tree_state("digits", model, Xd_tr.shape[1], 10)
    model = supervised("RandomForest", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: RandomForestClassifier(n_estimators=10, max_depth=10, random_state=42).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_forest_state("digits", model, Xd_te, Xd_tr.shape[0])
    model = supervised("GaussianNB", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: GaussianNB(var_smoothing=1e-9).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    emit_gnb_state("digits", model)
    kmeans_row("digits", Xd_tr, Xd_te, yd_tr, yd_te, 10)

    diabetes = load_diabetes()
    X_r = diabetes.data.astype(np.float32)
    y_r = diabetes.target.astype(np.float32)
    Xr_tr, Xr_te, yr_tr, yr_te = prepared("diabetes", X_r, y_r)
    model = supervised("Ridge", "diabetes", Xr_tr, Xr_te, yr_tr, yr_te,
               lambda X, y: Ridge(alpha=1.0).fit(X, y),
               lambda m, X: m.predict(X), "r2")
    emit_linear_state("Ridge", "diabetes", model)
    model = supervised("Lasso", "diabetes", Xr_tr, Xr_te, yr_tr, yr_te,
               lambda X, y: Lasso(alpha=0.1, max_iter=1000).fit(X, y),
               lambda m, X: m.predict(X), "r2")
    emit_linear_state("Lasso", "diabetes", model)
    model = supervised("LinearRegression", "diabetes", Xr_tr, Xr_te, yr_tr, yr_te,
               lambda X, y: LinearRegression().fit(X, y),
               lambda m, X: m.predict(X), "r2")
    emit_linear_state("LinearRegression", "diabetes", model)
    model = supervised("KernelRidge_RBF", "diabetes", Xr_tr, Xr_te, yr_tr, yr_te,
               lambda X, y: KernelRidge(alpha=1.0, kernel="rbf", gamma=0.1).fit(X, y),
               lambda m, X: m.predict(X), "r2")
    emit_krr_state("diabetes", model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
