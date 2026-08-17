#!/usr/bin/env python3
"""Profile representative sklearn estimator operations across Python/native layers.

This uses cProfile for Python-visible self time, wall time for the full operation,
tracemalloc for Python allocation pressure, and threadpoolctl to record native
BLAS/OpenMP backends.  Native time is reported conservatively as wall time not
explained by Python self time; the report labels that attribution as estimated.
"""
from __future__ import annotations

import argparse
import cProfile
import io
import json
import platform
import pstats
import time
import tracemalloc
from pathlib import Path

import numpy as np
import scipy
import sklearn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_info, threadpool_limits

ROOT = Path(__file__).resolve().parents[1]


def make_data(n, p=16):
    rng = np.random.default_rng(42 + n + p)
    X = rng.standard_normal((n, p), dtype=np.float32)
    w = np.linspace(0.25, 1.25, p, dtype=np.float32)
    s = X @ w
    yc = (s > np.median(s)).astype(np.int32)
    yr = (s + rng.standard_normal(n, dtype=np.float32) * 0.05).astype(np.float32)
    return X, yc, yr


def cases(n):
    X, yc, yr = make_data(n)
    split = max(2, int(n * 0.8))
    Xtr, Xte = X[:split], X[split:]
    yctr, yrtr = yc[:split], yr[:split]
    specs = []
    for name, model, y in [
        ("GaussianNB", GaussianNB(), yctr),
        ("LinearRegression", LinearRegression(), yrtr),
        ("LogisticRegression", LogisticRegression(max_iter=300), yctr),
        ("PCA", PCA(n_components=min(8, X.shape[1])), None),
        ("RandomForest", RandomForestClassifier(n_estimators=10, max_depth=8, random_state=42, n_jobs=1), yctr),
        ("KMeans", KMeans(n_clusters=2, n_init=1, max_iter=50, random_state=42), None),
        ("SVC", SVC(C=1.0, gamma="scale", max_iter=500), yctr),
        ("PipelineScalerLogReg", make_pipeline(StandardScaler(), LogisticRegression(max_iter=300)), yctr),
    ]:
        fit_call = (lambda m=model, y=y: m.fit(Xtr, y) if y is not None else m.fit(Xtr))
        fitted = fit_call()
        specs.append((name, "fit", fit_call))
        if hasattr(fitted, "predict"):
            specs.append((name, "predict", lambda m=fitted: m.predict(Xte)))
        elif hasattr(fitted, "transform"):
            specs.append((name, "transform", lambda m=fitted: m.transform(Xte)))
    return specs


def profile_call(fn):
    fn()  # warmup
    pr = cProfile.Profile()
    tracemalloc.start()
    t0 = time.perf_counter()
    pr.enable(); fn(); pr.disable()
    wall = time.perf_counter() - t0
    current, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()

    stats = pstats.Stats(pr, stream=io.StringIO())
    python_self = 0.0
    native_calls = 0
    calls = 0
    top = []
    for (filename, line, func), (cc, nc, tt, ct, callers) in stats.stats.items():
        calls += nc
        is_python = filename.endswith(".py") or filename.endswith(".pyx")
        if filename.endswith(".py"):
            python_self += tt
        else:
            native_calls += nc
        top.append((ct, filename, line, func, nc))
    top.sort(reverse=True)
    py_share = min(1.0, python_self / wall) if wall > 0 else 0.0
    return {
        "total_wall_ms": wall * 1000.0,
        "python_self_ms": python_self * 1000.0,
        "python_visible_self_share": py_share,
        "estimated_native_or_wait_share": max(0.0, 1.0 - py_share),
        "python_to_native_call_count_proxy": native_calls,
        "profiled_call_count": calls,
        "python_peak_alloc_bytes": peak,
        "dominant_symbols": [
            {"cum_ms": ct * 1000.0, "file": file, "line": line, "function": func, "calls": nc}
            for ct, file, line, func, nc in top[:12]
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", default="100,1000,10000")
    p.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "sklearn_runtime_attribution.json")
    args = p.parse_args()
    sizes = [int(v) for v in args.sizes.split(",") if v]
    rows = []
    with threadpool_limits(limits=1):
        for n in sizes:
            for name, op, fn in cases(n):
                # Avoid pathological quadratic CI cost while keeping the absence explicit.
                if name == "SVC" and n > 1000:
                    rows.append({"estimator": name, "operation": op, "rows": n, "status": "unavailable", "reason": "kernel SVC profiling capped at 1k rows"})
                    continue
                result = profile_call(fn)
                result.update({"estimator": name, "operation": op, "rows": n, "features": 16, "status": "ok", "attribution_confidence": "estimated-mixed-stack"})
                rows.append(result)
    payload = {
        "schema_version": 1,
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "sklearn": sklearn.__version__, "numpy": np.__version__, "scipy": scipy.__version__, "threadpools": threadpool_info()},
        "methodology": {"python_time": "cProfile Python .py self time", "native_time": "wall minus Python .py self time; estimate, not symbol-level native sampling", "allocation": "tracemalloc Python-managed peak bytes", "thread_limit": 1},
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"profiled {sum(r.get('status') == 'ok' for r in rows)} operations")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
