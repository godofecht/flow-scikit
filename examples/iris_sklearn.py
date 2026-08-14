#!/usr/bin/env python3
"""Iris classification - scikit-learn (Python).
Requires: python3, scikit-learn, numpy, scipy, joblib, threadpoolctl.
"""
import time
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

t0 = time.perf_counter()

iris = load_iris()
X, y = iris.data.astype(np.float32), iris.target.astype(np.float32)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

t1 = time.perf_counter()

results = []

# GaussianNB
t = time.perf_counter()
gnb = GaussianNB().fit(X_train_s, y_train)
train_time = (time.perf_counter() - t) * 1000
t = time.perf_counter()
preds = gnb.predict(X_test_s)
pred_time = (time.perf_counter() - t) * 1000
acc = accuracy_score(y_test, preds)
results.append(("GaussianNB", acc, train_time, pred_time))

# DecisionTree
t = time.perf_counter()
dt = DecisionTreeClassifier(max_depth=5, random_state=42).fit(X_train_s, y_train)
train_time = (time.perf_counter() - t) * 1000
t = time.perf_counter()
preds = dt.predict(X_test_s)
pred_time = (time.perf_counter() - t) * 1000
acc = accuracy_score(y_test, preds)
results.append(("DecisionTree", acc, train_time, pred_time))

# KNN
t = time.perf_counter()
knn = KNeighborsClassifier(n_neighbors=5).fit(X_train_s, y_train)
train_time = (time.perf_counter() - t) * 1000
t = time.perf_counter()
preds = knn.predict(X_test_s)
pred_time = (time.perf_counter() - t) * 1000
acc = accuracy_score(y_test, preds)
results.append(("KNN(k=5)", acc, train_time, pred_time))

# LinearSVC
t = time.perf_counter()
lsvc = LinearSVC(C=1.0, max_iter=200, dual='auto').fit(X_train_s, y_train)
train_time = (time.perf_counter() - t) * 1000
t = time.perf_counter()
preds = lsvc.predict(X_test_s)
pred_time = (time.perf_counter() - t) * 1000
acc = accuracy_score(y_test, preds)
results.append(("LinearSVC(OVR)", acc, train_time, pred_time))

# RandomForest
t = time.perf_counter()
rf = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42).fit(X_train_s, y_train)
train_time = (time.perf_counter() - t) * 1000
t = time.perf_counter()
preds = rf.predict(X_test_s)
pred_time = (time.perf_counter() - t) * 1000
acc = accuracy_score(y_test, preds)
results.append(("RandomForest(10)", acc, train_time, pred_time))

t_end = time.perf_counter()

print("=== Iris Classification - scikit-learn (Python) ===\n")
print(f"Dataset: iris (150 samples, 4 features, 3 classes)")
print(f"Train/test split: {len(X_train)} / {len(X_test)}\n")

print(f"{'Algorithm':<20} {'Accuracy':<12} {'Train(ms)':<12} {'Predict(ms)':<12}")
print(f"{'--------------------':<20} {'------------':<12} {'------------':<12} {'------------':<12}")
for name, acc, tr, pr in results:
    print(f"{name:<20} {acc:<12.4f} {tr:<12.3f} {pr:<12.3f}")

print(f"\nTotal time including data load: {(t_end - t0) * 1000:.3f} ms")
