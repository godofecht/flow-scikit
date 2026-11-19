#!/usr/bin/env python3
"""Prediction-only scaling benchmark for KernelRidge (RBF), scikit-learn side.

Builds the same float32 inputs as bench_predict_kernel_ridge.flow, times
``KernelRidge.predict`` alone with the shared adaptive timer, and optionally
joins the Flow output into one table.

    python benchmarks/bench_predict_kernel_ridge.py --flow flow_predict_krr.txt
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.kernel_ridge import KernelRidge

from timing import measure

# Agreement tolerance on the prediction checksums, relative to the sum of
# absolute predictions. scikit-learn solves the float32 system in float32 and
# Flow solves it in float64, so the dual coefficients differ in their last
# digits before prediction starts.
CHECKSUM_RELATIVE_TOLERANCE = 1e-3

# (axis, n_query, n_train, features), in the order the Flow benchmark emits.
CASES = (
    [("batch", n, 353, 10) for n in (1, 10, 89, 1000, 10000)]
    + [("train", 1000, n, 10) for n in (100, 1000, 3000)]
    + [("features", 1000, 353, p) for p in (2, 32, 128)]
)


def make(first_row: int, n: int, p: int):
    i = np.arange(first_row, first_row + n, dtype=np.int64)[:, None]
    j = np.arange(p, dtype=np.int64)[None, :]
    # Integers over a power of two: exact in float32.
    X = (((i * 131 + j * 17) % 257) / 128.0 - 1.0).astype(np.float32)
    y = (((i[:, 0] * 29 + 3) % 97) / 8.0).astype(np.float32)
    return X, y


def parse_flow(path: Path) -> dict:
    rows = {}
    unit = None
    for line in path.read_text().splitlines():
        if line.startswith("TIMING_UNIT|"):
            unit = line.split("|", 1)[1].strip()
        elif line.startswith("PREDICT|KernelRidge_RBF|"):
            p = line.strip().split("|")
            rows[(p[2], int(p[3]), int(p[4]), int(p[5]))] = {
                "median_ms": float(p[6]),
                "iqr_ms": float(p[7]),
                "repeats": int(p[8]),
                "pred_sum": float(p[9]),
                "pred_weighted_sum": float(p[10]),
                "pred_abs_sum": float(p[11]),
            }
    if unit != "ms":
        raise SystemExit("Flow predict benchmark must declare TIMING_UNIT|ms")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", type=Path, help="output of bench_predict_kernel_ridge.flow to join")
    parser.add_argument("--output", type=Path, help="write the joined rows as JSON")
    args = parser.parse_args()

    flow = parse_flow(args.flow) if args.flow else {}
    rows = []
    mismatches = 0
    for axis, n_query, n_train, p in CASES:
        X, y = make(0, n_train, p)
        Q, _ = make(n_train, n_query, p)
        model = KernelRidge(alpha=1.0, kernel="rbf", gamma=0.1).fit(X, y)
        timing = measure(lambda: model.predict(Q), min_window_ms=10.0, samples=7)
        pred = np.asarray(timing.value, dtype=np.float64)
        weights = (np.arange(n_query) % 7 + 1).astype(np.float64)
        row = {
            "estimator": "KernelRidge_RBF",
            "axis": axis,
            "n_query": n_query,
            "n_train": n_train,
            "features": p,
            "sklearn_ms": timing.median_ms,
            "sklearn_iqr_ms": timing.iqr_ms,
            "sklearn_pred_sum": float(pred.sum()),
            "sklearn_pred_weighted_sum": float((pred * weights).sum()),
            "sklearn_pred_abs_sum": float(np.abs(pred).sum()),
            "timing_unit": "ms",
        }
        f = flow.get((axis, n_query, n_train, p))
        if f:
            scale = max(row["sklearn_pred_abs_sum"], 1e-12)
            sum_diff = abs(f["pred_sum"] - row["sklearn_pred_sum"]) / scale
            weighted_diff = abs(f["pred_weighted_sum"] - row["sklearn_pred_weighted_sum"]) / (7.0 * scale)
            row.update({
                "flow_ms": f["median_ms"],
                "flow_iqr_ms": f["iqr_ms"],
                "flow_pred_sum": f["pred_sum"],
                "flow_pred_weighted_sum": f["pred_weighted_sum"],
                "speedup": timing.median_ms / f["median_ms"] if f["median_ms"] > 0 else None,
                "checksum_relative_diff": max(sum_diff, weighted_diff),
                "predictions_agree": max(sum_diff, weighted_diff) <= CHECKSUM_RELATIVE_TOLERANCE,
            })
            if not row["predictions_agree"]:
                mismatches += 1
        rows.append(row)

    if flow:
        print("| axis | queries | train rows | features | sklearn ms | Flow ms | speedup | checksum rel. diff |")
        print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for r in rows:
            if "flow_ms" not in r:
                continue
            print(
                f"| {r['axis']} | {r['n_query']} | {r['n_train']} | {r['features']} | "
                f"{r['sklearn_ms']:.4f} | {r['flow_ms']:.4f} | {r['speedup']:.2f}x | "
                f"{r['checksum_relative_diff']:.1e} |"
            )
    else:
        for r in rows:
            print(f"PREDICT|KernelRidge_RBF|{r['axis']}|{r['n_query']}|{r['n_train']}|{r['features']}|{r['sklearn_ms']:.9f}|{r['sklearn_iqr_ms']:.9f}")

    if args.output:
        args.output.write_text(json.dumps({"timing_unit": "ms", "benchmark_mode": "predict_only", "rows": rows}, indent=2) + "\n")

    if mismatches:
        print(f"{mismatches} case(s) where the prediction checksums differ by more than {CHECKSUM_RELATIVE_TOLERANCE:g}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
