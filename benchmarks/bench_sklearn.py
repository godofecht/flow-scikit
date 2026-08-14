#!/usr/bin/env python3
"""Benchmark real scikit-learn on iris, digits, diabetes.
Outputs results in parseable format for comparison with flow-scikit.
"""
import time
import numpy as np
from sklearn.datasets import load_iris, load_digits, load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, r2_score

# Load datasets
iris = load_iris()
digits = load_digits()
diabetes = load_diabetes()

results = []

def bench(name, dataset_name, X, y, fit_fn, predict_fn, is_classification=True):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if is_classification else None
    )
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
      lambda X, y: SVC(C=1.0, gamma=0.5, max_iter=200).fit(X, y),
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
def kmeans_fit(X, y):
    return KMeans(n_clusters=3, n_init=10, random_state=42).fit(X)
def kmeans_predict(m, X):
    return m.predict(X)
bench("KMeans", "iris", X_iris, y_iris, kmeans_fit, kmeans_predict)

from sklearn.decomposition import PCA
def pca_fit(X, y):
    return PCA(n_components=2).fit(X)
def pca_transform(m, X):
    return m.transform(X)
# PCA is transform, not predict - measure explained variance ratio instead
X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(
    X_iris, y_iris, test_size=0.2, random_state=42, stratify=y_iris
)
scaler_i = StandardScaler()
X_train_i = scaler_i.fit_transform(X_train_i)
X_test_i = scaler_i.transform(X_test_i)
t0 = time.perf_counter()
pca = PCA(n_components=2).fit(X_train_i)
fit_time = time.perf_counter() - t0
t0 = time.perf_counter()
_ = pca.transform(X_test_i)
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
      lambda X, y: SVC(C=1.0, gamma=0.001, max_iter=200).fit(X, y),
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

bench("KMeans", "digits", X_dig, y_dig,
      lambda X, y: KMeans(n_clusters=10, n_init=10, random_state=42).fit(X),
      lambda m, X: m.predict(X))

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
