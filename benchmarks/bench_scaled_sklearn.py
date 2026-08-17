#!/usr/bin/env python3
"""Scaled sklearn benchmark matrix for overhead-to-throughput crossover analysis."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import sklearn
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from timing import measure

DEFAULT_ROWS = [100, 1_000, 10_000, 100_000, 1_000_000]
FEATURE_COUNTS = [8, 32]


def data(n: int, p: int):
    i = np.arange(n, dtype=np.int64)[:, None]
    j = np.arange(p, dtype=np.int64)[None, :]
    raw = (i * 131 + j * 17 + n * 3 + p * 11) % 1000
    X = (raw.astype(np.float32) / 500.0 - 1.0).astype(np.float32)
    weights = (0.25 + np.arange(p, dtype=np.float32) / float(p)).astype(np.float32)
    signal = (X @ weights).astype(np.float32)
    y_class = (signal > 0.0).astype(np.float32)
    y_reg = signal
    return X, y_class, y_reg


def record(rows, algorithm, n, p, fit_t, pred_t, status="ok", reason=None):
    rows.append({
        "implementation": "sklearn",
        "algorithm": algorithm,
        "rows": n,
        "features": p,
        "fit_ms": fit_t.median_ms if fit_t else None,
        "pred_ms": pred_t.median_ms if pred_t else None,
        "fit_iqr_ms": fit_t.iqr_ms if fit_t else None,
        "pred_iqr_ms": pred_t.iqr_ms if pred_t else None,
        "timing_unit": "ms",
        "status": status,
        "reason": reason,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rows", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, default=Path("benchmarks/scaled_sklearn.json"))
    args = parser.parse_args()

    rows = []
    for n in DEFAULT_ROWS:
        if n > args.max_rows:
            continue
        for p in FEATURE_COUNTS:
            X, yc, yr = data(n, p)
            split = max(1, int(n * 0.8))
            Xtr, Xte = X[:split], X[split:]
            yctr = yc[:split]
            yrtr = yr[:split]

            fit_t = measure(lambda: LinearRegression().fit(Xtr, yrtr), min_window_ms=10.0, samples=5)
            pred_t = measure(lambda: fit_t.value.predict(Xte), min_window_ms=10.0, samples=5)
            record(rows, "LinearRegression", n, p, fit_t, pred_t)

            fit_t = measure(lambda: RandomForestClassifier(n_estimators=10, max_depth=8, random_state=42, n_jobs=1).fit(Xtr, yctr), min_window_ms=10.0, samples=5)
            pred_t = measure(lambda: fit_t.value.predict(Xte), min_window_ms=10.0, samples=5)
            record(rows, "RandomForest", n, p, fit_t, pred_t)

            fit_t = measure(lambda: GaussianNB(var_smoothing=1e-9).fit(Xtr, yctr), min_window_ms=10.0, samples=5)
            pred_t = measure(lambda: fit_t.value.predict(Xte), min_window_ms=10.0, samples=5)
            record(rows, "GaussianNB", n, p, fit_t, pred_t)

            fit_t = measure(lambda: KMeans(n_clusters=2, n_init=1, max_iter=50, random_state=42).fit(Xtr), min_window_ms=10.0, samples=5)
            pred_t = measure(lambda: fit_t.value.predict(Xte), min_window_ms=10.0, samples=5)
            record(rows, "KMeans", n, p, fit_t, pred_t)

            if n <= 1_000:
                fit_t = measure(lambda: SVC(C=1.0, gamma=0.1, max_iter=500).fit(Xtr, yctr), min_window_ms=10.0, samples=5)
                pred_t = measure(lambda: fit_t.value.predict(Xte), min_window_ms=10.0, samples=5)
                record(rows, "KernelSVC_RBF", n, p, fit_t, pred_t)
            else:
                record(rows, "KernelSVC_RBF", n, p, None, None, status="unavailable", reason="quadratic-or-worse kernel scaling intentionally capped at 1k rows")

    payload = {
        "schema_version": 1,
        "fixture": "deterministic formula shared with benchmarks/bench_scaled.flow",
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "sklearn": sklearn.__version__, "numpy": np.__version__},
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {len(rows)} scaled sklearn rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
