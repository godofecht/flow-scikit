#!/usr/bin/env python3
"""Per-algorithm parity benchmark: scikit-learn (Python) on deterministic datasets.

Each algorithm uses fixed data, fixed seed, fixed parameters.
Outputs JSON with algorithm name, output values, and timing.

This is the Python side. The Flow side (bench_per_algorithm.flow) must
produce identical output values for each algorithm.
"""
import time
import json
import numpy as np
from sklearn.datasets import load_iris, load_diabetes

iris = load_iris()
diabetes = load_diabetes()

# Fixed deterministic splits (no shuffle, first 80% train, last 20% test)
def fixed_split(X, y, test_frac=0.2):
    n = len(X)
    n_test = int(n * test_frac)
    n_train = n - n_test
    return X[:n_train], X[n_train:], y[:n_train], y[n_train:]

results = []

def record(name, output, fit_ms, pred_ms):
    """Record a result. output is a list of floats."""
    results.append({
        "algorithm": name,
        "output": [round(float(v), 6) for v in output],
        "fit_ms": round(fit_ms, 4),
        "pred_ms": round(pred_ms, 4),
        "total_ms": round(fit_ms + pred_ms, 4)
    })

def time_call(fn):
    t0 = time.perf_counter()
    result = fn()
    elapsed = (time.perf_counter() - t0) * 1000
    return result, elapsed

# ============================================================
# Classification datasets
# ============================================================
X_iris = iris.data.astype(np.float64)
y_iris = iris.target.astype(np.float64)
X_tr_i, X_te_i, y_tr_i, y_te_i = fixed_split(X_iris, y_iris)

X_dia = diabetes.data.astype(np.float64)
y_dia = diabetes.target.astype(np.float64)
X_tr_d, X_te_d, y_tr_d, y_te_d = fixed_split(X_dia, y_dia)

# ============================================================
# Preprocessing (deterministic, exact match expected)
# ============================================================
from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler, RobustScaler

scaler, t = time_call(lambda: StandardScaler().fit(X_tr_i))
out, t2 = time_call(lambda: scaler.transform(X_te_i))
record("StandardScaler", out.flatten(), t, t2)

scaler, t = time_call(lambda: MinMaxScaler().fit(X_tr_i))
out, t2 = time_call(lambda: scaler.transform(X_te_i))
record("MinMaxScaler", out.flatten(), t, t2)

scaler, t = time_call(lambda: MaxAbsScaler().fit(X_tr_i))
out, t2 = time_call(lambda: scaler.transform(X_te_i))
record("MaxAbsScaler", out.flatten(), t, t2)

# ============================================================
# Naive Bayes (closed form, exact match expected)
# ============================================================
from sklearn.naive_bayes import GaussianNB

model, t = time_call(lambda: GaussianNB().fit(X_tr_i, y_tr_i))
out, t2 = time_call(lambda: model.predict(X_te_i))
record("GaussianNB", out, t, t2)

# ============================================================
# KNN (exact algorithm, exact match expected)
# ============================================================
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor, NearestCentroid

model, t = time_call(lambda: KNeighborsClassifier(n_neighbors=5).fit(X_tr_i, y_tr_i))
out, t2 = time_call(lambda: model.predict(X_te_i))
record("KNNClassifier_k5", out, t, t2)

model, t = time_call(lambda: KNeighborsRegressor(n_neighbors=3).fit(X_tr_d, y_tr_d))
out, t2 = time_call(lambda: model.predict(X_te_d))
record("KNNRegressor_k3", out, t, t2)

model, t = time_call(lambda: NearestCentroid().fit(X_tr_i, y_tr_i))
out, t2 = time_call(lambda: model.predict(X_te_i))
record("NearestCentroid", out, t, t2)

# ============================================================
# Linear Models (closed form, exact match expected for direct solvers)
# ============================================================
from sklearn.linear_model import LinearRegression, Ridge, Lasso

model, t = time_call(lambda: LinearRegression().fit(X_tr_d, y_tr_d))
out, t2 = time_call(lambda: model.predict(X_te_d))
record("LinearRegression", out, t, t2)

model, t = time_call(lambda: Ridge(alpha=1.0).fit(X_tr_d, y_tr_d))
out, t2 = time_call(lambda: model.predict(X_te_d))
record("Ridge_a1", out, t, t2)

model, t = time_call(lambda: Lasso(alpha=0.1, max_iter=5000).fit(X_tr_d, y_tr_d))
out, t2 = time_call(lambda: model.predict(X_te_d))
record("Lasso_a0.1", out, t, t2)

# ============================================================
# Dummy (trivial, exact match expected)
# ============================================================
from sklearn.dummy import DummyClassifier, DummyRegressor

model, t = time_call(lambda: DummyClassifier(strategy="most_frequent").fit(X_tr_i, y_tr_i))
out, t2 = time_call(lambda: model.predict(X_te_i))
record("DummyClassifier_most_frequent", out, t, t2)

model, t = time_call(lambda: DummyRegressor(strategy="mean").fit(X_tr_d, y_tr_d))
out, t2 = time_call(lambda: model.predict(X_te_d))
record("DummyRegressor_mean", out, t, t2)

# ============================================================
# PCA (eigendecomposition, close match expected)
# ============================================================
from sklearn.decomposition import PCA

model, t = time_call(lambda: PCA(n_components=2).fit(X_tr_i))
out, t2 = time_call(lambda: model.transform(X_te_i))
record("PCA_2comp", out.flatten(), t, t2)

# ============================================================
# KMeans (with fixed init, exact match expected)
# ============================================================
from sklearn.cluster import KMeans

# Use fixed cluster centers from first 3 samples
init_centers = X_tr_i[:3].copy()
model, t = time_call(lambda: KMeans(n_clusters=3, init=init_centers, n_init=1, max_iter=100, tol=1e-6).fit(X_tr_i))
out, t2 = time_call(lambda: model.predict(X_te_i))
record("KMeans_k3_fixed_init", out.astype(float), t, t2)

# ============================================================
# LDA (closed form, exact match expected)
# ============================================================
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

model, t = time_call(lambda: LinearDiscriminantAnalysis().fit(X_tr_i, y_tr_i))
out, t2 = time_call(lambda: model.predict(X_te_i))
record("LDA", out, t, t2)

# ============================================================
# QDA (closed form, exact match expected)
# ============================================================
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

model, t = time_call(lambda: QuadraticDiscriminantAnalysis().fit(X_tr_i, y_tr_i))
out, t2 = time_call(lambda: model.predict(X_te_i))
record("QDA", out, t, t2)

# ============================================================
# Output
# ============================================================
print(json.dumps(results, indent=2))
with open("benchmarks/python_parity_results.json", "w") as f:
    json.dump(results, f, indent=2)
