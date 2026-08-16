#!/usr/bin/env python3
"""Benchmark real scikit-learn on iris, digits, diabetes.
Outputs results in parseable format for comparison with flow-scikit.
Uses the same xorshift32 PRNG split as the Flow benchmark for exact parity.
"""
import time
import numpy as np
from sklearn.datasets import load_iris, load_digits, load_diabetes
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, r2_score

def xorshift32_split(n, n_test, seed=42):
    """Replicate Flow's split_data: Fisher-Yates shuffle with xorshift32 PRNG."""
    indices = list(range(n))
    state = seed & 0xFFFFFFFF
    if state == 0:
        state = 1
    for i in range(n - 1, 0, -1):
        x = state
        x = (x ^ ((x << 13) & 0xFFFFFFFF)) & 0xFFFFFFFF
        x = (x ^ (x >> 17)) & 0xFFFFFFFF
        x = (x ^ ((x << 5) & 0xFFFFFFFF)) & 0xFFFFFFFF
        state = x
        j = (x & 0x7FFFFFFF) % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    n_train = n - n_test
    return np.array(indices[:n_train]), np.array(indices[n_train:])

results = []

def bench(name, dataset_name, X, y, fit_fn, predict_fn, is_classification=True):
    n = len(X)
    n_test = n // 5
    train_idx, test_idx = xorshift32_split(n, n_test)
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    t0 = time.perf_counter()
    model = fit_fn(X_train, y_train)
    fit_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    preds = predict_fn(model, X_test)
    pred_time = time.perf_counter() - t0

    if is_classification:
        score = accuracy_score(y_test, preds)
        metric = "accuracy"
    else:
        score = r2_score(y_test, preds)
        metric = "r2"

    results.append((name, dataset_name, metric, score, fit_time, pred_time))
    print(f"RESULT|{name}|{dataset_name}|{metric}|{score:.6f}|{fit_time:.6f}|{pred_time:.6f}")

# Load datasets
iris = load_iris()
digits = load_digits()
diabetes = load_diabetes()

# ---- Iris (classification) ----
X_iris = iris.data.astype(np.float32)
y_iris = iris.target.astype(np.float32)

from sklearn.linear_model import LogisticRegression
bench("LogisticRegression", "iris", X_iris, y_iris,
      lambda X, y: LogisticRegression(max_iter=1000, C=1.0).fit(X, y),
      lambda m, X: m.predict(X))

from sklearn.svm import LinearSVC
bench("LinearSVC", "iris", X_iris, y_iris,
      lambda X, y: LinearSVC(max_iter=1000, C=1.0, dual='auto').fit(X, y),
      lambda m, X: m.predict(X))

from sklearn.svm import SVC
bench("KernelSVC_RBF", "iris", X_iris, y_iris,
      lambda X, y: SVC(C=1.0, gamma=0.25, max_iter=1000).fit(X, y),
      lambda m, X: m.predict(X))

from sklearn.tree import DecisionTreeClassifier
bench("DecisionTree", "iris", X_iris, y_iris,
      lambda X, y: DecisionTreeClassifier(max_depth=5, random_state=42).fit(X, y),
      lambda m, X: m.predict(X))

from sklearn.ensemble import RandomForestClassifier
bench("RandomForest", "iris", X_iris, y_iris,
      lambda X, y: RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42).fit(X, y),
      lambda m, X: m.predict(X))

from sklearn.naive_bayes import GaussianNB
bench("GaussianNB", "iris", X_iris, y_iris,
      lambda X, y: GaussianNB().fit(X, y),
      lambda m, X: m.predict(X))

from sklearn.cluster import KMeans
# KMeans: use best-match cluster labeling like Flow
def kmeans_bench(name, ds, X, y, n_clusters):
    n = len(X)
    n_test = n // 5
    train_idx, test_idx = xorshift32_split(n, n_test)
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    t0 = time.perf_counter()
    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42).fit(X_train)
    fit_time = time.perf_counter() - t0
    t0 = time.perf_counter()
    preds = km.predict(X_test)
    pred_time = time.perf_counter() - t0
    # Best-match: for each cluster, find most common true label
    from collections import Counter
    cluster_map = {}
    for c in range(n_clusters):
        labels = y_test[preds == c]
        if len(labels) > 0:
            cluster_map[c] = Counter(labels.astype(int)).most_common(1)[0][0]
        else:
            cluster_map[c] = 0
    mapped = np.array([cluster_map[p] for p in preds])
    score = accuracy_score(y_test, mapped.astype(float))
    results.append((name, ds, "accuracy", score, fit_time, pred_time))
    print(f"RESULT|{name}|{ds}|accuracy|{score:.6f}|{fit_time:.6f}|{pred_time:.6f}")
kmeans_bench("KMeans", "iris", X_iris, y_iris, 3)

from sklearn.decomposition import PCA
def pca_fit(X, y):
    return PCA(n_components=2).fit(X)
def pca_transform(m, X):
    return m.transform(X)
# PCA is transform, not predict - measure explained variance ratio instead
n_iris = len(X_iris)
train_idx_i, test_idx_i = xorshift32_split(n_iris, n_iris // 5)
X_train_i = scaler_fit_i = StandardScaler().fit(X_iris[train_idx_i])
X_train_i_s = scaler_fit_i.transform(X_iris[train_idx_i])
X_test_i_s = scaler_fit_i.transform(X_iris[test_idx_i])
t0 = time.perf_counter()
pca = PCA(n_components=2).fit(X_train_i_s)
fit_time = time.perf_counter() - t0
t0 = time.perf_counter()
_ = pca.transform(X_test_i_s)
pred_time = time.perf_counter() - t0
evr = pca.explained_variance_ratio_[0]
results.append(("PCA", "iris", "explained_var_ratio", evr, fit_time, pred_time))
print(f"RESULT|PCA|iris|explained_var_ratio|{evr:.6f}|{fit_time:.6f}|{pred_time:.6f}")

# ---- Digits (classification, larger) ----
X_dig = digits.data.astype(np.float32)
y_dig = digits.target.astype(np.float32)

bench("LogisticRegression", "digits", X_dig, y_dig,
      lambda X, y: LogisticRegression(max_iter=1000, C=1.0).fit(X, y),
      lambda m, X: m.predict(X))

bench("LinearSVC", "digits", X_dig, y_dig,
      lambda X, y: LinearSVC(max_iter=1000, C=1.0, dual='auto').fit(X, y),
      lambda m, X: m.predict(X))

bench("KernelSVC_RBF", "digits", X_dig, y_dig,
      lambda X, y: SVC(C=1.0, gamma=0.001, max_iter=1000).fit(X, y),
      lambda m, X: m.predict(X))

bench("DecisionTree", "digits", X_dig, y_dig,
      lambda X, y: DecisionTreeClassifier(max_depth=10, random_state=42).fit(X, y),
      lambda m, X: m.predict(X))

bench("RandomForest", "digits", X_dig, y_dig,
      lambda X, y: RandomForestClassifier(n_estimators=10, max_depth=10, random_state=42).fit(X, y),
      lambda m, X: m.predict(X))

bench("GaussianNB", "digits", X_dig, y_dig,
      lambda X, y: GaussianNB().fit(X, y),
      lambda m, X: m.predict(X))

kmeans_bench("KMeans", "digits", X_dig, y_dig, 10)

# ---- Diabetes (regression) ----
X_dia = diabetes.data.astype(np.float32)
y_dia = diabetes.target.astype(np.float32)

from sklearn.linear_model import Ridge, Lasso, LinearRegression
bench("Ridge", "diabetes", X_dia, y_dia,
      lambda X, y: Ridge(alpha=1.0).fit(X, y),
      lambda m, X: m.predict(X), is_classification=False)

bench("Lasso", "diabetes", X_dia, y_dia,
      lambda X, y: Lasso(alpha=0.1, max_iter=1000).fit(X, y),
      lambda m, X: m.predict(X), is_classification=False)

bench("LinearRegression", "diabetes", X_dia, y_dia,
      lambda X, y: LinearRegression().fit(X, y),
      lambda m, X: m.predict(X), is_classification=False)

from sklearn.kernel_ridge import KernelRidge
bench("KernelRidge_RBF", "diabetes", X_dia, y_dia,
      lambda X, y: KernelRidge(alpha=1.0, kernel='rbf', gamma=0.1).fit(X, y),
      lambda m, X: m.predict(X), is_classification=False)

print("\n--- Summary ---")
print(f"{'Algorithm':<25} {'Dataset':<12} {'Metric':<20} {'Score':<12} {'FitTime':<12} {'PredTime':<12}")
for name, ds, metric, score, ft, pt in results:
    print(f"{name:<25} {ds:<12} {metric:<20} {score:<12.6f} {ft:<12.6f} {pt:<12.6f}")
