#!/usr/bin/env python3
"""Build whole-estimator experiments that separate API orchestration from kernels.

The report combines direct sklearn measurements, stable NumPy/SciPy kernel
baselines where a meaningful public equivalent exists, mixed-stack profiling,
and committed Flow benchmark rows.  Missing kernel baselines are explicit.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]


def median_ms(fn, repeats=7):
    values = []
    for _ in range(repeats):
        t0 = time.perf_counter(); fn(); values.append((time.perf_counter() - t0) * 1000.0)
    return float(np.median(values))


def direct_kernel_experiments():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((10_000, 16), dtype=np.float32)
    y = (X @ np.linspace(0.2, 1.0, 16, dtype=np.float32)).astype(np.float32)
    rows = []

    lr = LinearRegression()
    public = median_ms(lambda: lr.fit(X, y))
    X1 = np.column_stack([np.ones(len(X), dtype=X.dtype), X])
    kernel = median_ms(lambda: np.linalg.lstsq(X1, y, rcond=None))
    rows.append({"estimator": "LinearRegression", "operation": "fit", "execution_class": "blas-lapack-bound", "sklearn_end_to_end_ms": public, "isolated_kernel_ms": kernel, "kernel": "numpy.linalg.lstsq", "orchestration_overhead_ms": max(0.0, public-kernel)})

    pca = PCA(n_components=8)
    public = median_ms(lambda: pca.fit(X))
    centered = X - X.mean(axis=0)
    kernel = median_ms(lambda: np.linalg.svd(centered, full_matrices=False))
    rows.append({"estimator": "PCA", "operation": "fit", "execution_class": "blas-lapack-bound", "sklearn_end_to_end_ms": public, "isolated_kernel_ms": kernel, "kernel": "numpy.linalg.svd", "orchestration_overhead_ms": max(0.0, public-kernel)})

    pipe = make_pipeline(StandardScaler(), LinearRegression())
    public = median_ms(lambda: pipe.fit(X, y))
    def fused_reference():
        mean = X.mean(axis=0); std = X.std(axis=0); std = np.where(std == 0, 1, std)
        Z = (X - mean) / std
        Z1 = np.column_stack([np.ones(len(Z), dtype=Z.dtype), Z])
        np.linalg.lstsq(Z1, y, rcond=None)
    kernel = median_ms(fused_reference)
    rows.append({"estimator": "Pipeline(StandardScaler,LinearRegression)", "operation": "fit", "execution_class": "mixed", "sklearn_end_to_end_ms": public, "isolated_kernel_ms": kernel, "kernel": "fused NumPy scaling + lstsq reference", "orchestration_overhead_ms": max(0.0, public-kernel)})
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--profiles", type=Path, default=ROOT / "benchmarks" / "sklearn_runtime_attribution.json")
    p.add_argument("--headline", type=Path, default=ROOT / "benchmarks" / "headline_result_v2.json")
    p.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "whole_estimator_experiments.json")
    args = p.parse_args()
    profiles = json.loads(args.profiles.read_text())["rows"]
    headline = json.loads(args.headline.read_text()) if args.headline.exists() else {"rows": []}
    direct = direct_kernel_experiments()

    reps = {
        "python-bound": "GaussianNB",
        "numpy-bound": "GaussianNB",
        "scipy-bound": "LogisticRegression",
        "blas-lapack-bound": "LinearRegression",
        "cython-bound": "RandomForest",
        "external-native-bound": "SVC",
        "mixed": "PipelineScalerLogReg",
    }
    rows = []
    for substrate, estimator in reps.items():
        prof = [r for r in profiles if r.get("estimator") == estimator and r.get("status") == "ok"]
        largest = max(prof, key=lambda r: r["rows"], default=None)
        h = [r for r in headline.get("rows", []) if r.get("algorithm") == estimator]
        row = {"execution_class": substrate, "representative": estimator, "profile": largest, "flow_rows": h}
        kernel = next((d for d in direct if d["estimator"] == estimator), None)
        if kernel:
            row["kernel_baseline"] = kernel
        else:
            row["kernel_baseline"] = {"status": "unavailable", "reason": "no stable public isolated kernel exposes identical estimator semantics"}
        rows.append(row)
    rows.append({"execution_class": "mixed", "representative": "Pipeline(StandardScaler,LinearRegression)", "kernel_baseline": direct[-1], "profile": None, "flow_rows": [], "hypothesis": "whole-program fusion can eliminate intermediate standardized arrays and repeated validation"})
    args.output.write_text(json.dumps({"schema_version": 1, "question": "does whole-estimator compilation reduce orchestration/allocation overhead beyond kernel speed?", "rows": rows, "direct_kernel_experiments": direct}, indent=2) + "\n")
    print(f"wrote {len(rows)} whole-estimator experiment rows")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
