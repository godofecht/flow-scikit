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

    supervised("LogisticRegression", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: LogisticRegression(max_iter=1000, C=1.0).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("LinearSVC", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: LinearSVC(max_iter=1000, C=1.0, dual="auto").fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("KernelSVC_RBF", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: SVC(C=1.0, gamma=0.25, max_iter=1000).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("DecisionTree", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: DecisionTreeClassifier(max_depth=5, random_state=42).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("RandomForest", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("GaussianNB", "iris", Xi_tr, Xi_te, yi_tr, yi_te,
               lambda X, y: GaussianNB(var_smoothing=1e-9).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    kmeans_row("iris", Xi_tr, Xi_te, yi_tr, yi_te, 3)
    pca_row(Xi_tr, Xi_te)

    digits = load_digits()
    X_d = digits.data.astype(np.float32)
    y_d = digits.target.astype(np.float32)
    Xd_tr, Xd_te, yd_tr, yd_te = prepared("digits", X_d, y_d)
    supervised("LogisticRegression", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: LogisticRegression(max_iter=1000, C=1.0).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("LinearSVC", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: LinearSVC(max_iter=1000, C=1.0, dual="auto").fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("KernelSVC_RBF", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: SVC(C=1.0, gamma=0.001, max_iter=1000).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("DecisionTree", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: DecisionTreeClassifier(max_depth=10, random_state=42).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("RandomForest", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: RandomForestClassifier(n_estimators=10, max_depth=10, random_state=42).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    supervised("GaussianNB", "digits", Xd_tr, Xd_te, yd_tr, yd_te,
               lambda X, y: GaussianNB(var_smoothing=1e-9).fit(X, y),
               lambda m, X: m.predict(X), "accuracy")
    kmeans_row("digits", Xd_tr, Xd_te, yd_tr, yd_te, 10)

    diabetes = load_diabetes()
    X_r = diabetes.data.astype(np.float32)
    y_r = diabetes.target.astype(np.float32)
    Xr_tr, Xr_te, yr_tr, yr_te = prepared("diabetes", X_r, y_r)
    supervised("Ridge", "diabetes", Xr_tr, Xr_te, yr_tr, yr_te,
               lambda X, y: Ridge(alpha=1.0).fit(X, y),
               lambda m, X: m.predict(X), "r2")
    supervised("Lasso", "diabetes", Xr_tr, Xr_te, yr_tr, yr_te,
               lambda X, y: Lasso(alpha=0.1, max_iter=1000).fit(X, y),
               lambda m, X: m.predict(X), "r2")
    supervised("LinearRegression", "diabetes", Xr_tr, Xr_te, yr_tr, yr_te,
               lambda X, y: LinearRegression().fit(X, y),
               lambda m, X: m.predict(X), "r2")
    supervised("KernelRidge_RBF", "diabetes", Xr_tr, Xr_te, yr_tr, yr_te,
               lambda X, y: KernelRidge(alpha=1.0, kernel="rbf", gamma=0.1).fit(X, y),
               lambda m, X: m.predict(X), "r2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
