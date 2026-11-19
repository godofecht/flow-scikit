#!/usr/bin/env python3
"""Prediction-only scaling benchmark for the RBF SVC, scikit-learn side.

Builds the same float32 inputs as bench_predict_kernel_svc.flow, times
``SVC.predict`` alone with the shared adaptive timer, and optionally joins the
Flow output into one table.

    python benchmarks/bench_predict_kernel_svc.py --flow flow_predict_ksvc.txt
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.svm import SVC

from timing import measure

N_CLASSES = 3

# The canonical KernelSVC rows are approximately equivalent under an accuracy
# tolerance of 0.03 (parity_contract.json). The same tolerance applies here.
ACCURACY_TOLERANCE = 0.03

# (axis, n_query, n_train, features), in the order the Flow benchmark emits.
CASES = (
    [("batch", n, 300, 16) for n in (1, 10, 100, 1000, 10000)]
    + [("train", 1000, n, 16) for n in (60, 120, 1000)]
    + [("features", 1000, 300, p) for p in (4, 64, 256)]
)


def make(first_row: int, n: int, p: int):
    i = np.arange(first_row, first_row + n, dtype=np.int64)[:, None]
    j = np.arange(p, dtype=np.int64)[None, :]
    cls = i % N_CLASSES
    raw = ((i * 37 + j * 19 + cls * 7) % 128) + cls * (8 + ((j * 5) % 7) * 2)
    # Integers below 2**24 over a power of two: exact in float32.
    X = (raw / 64.0).astype(np.float32)
    return X, cls[:, 0].astype(np.float32)


def parse_flow(path: Path) -> dict:
    rows = {}
    unit = None
    for line in path.read_text().splitlines():
        if line.startswith("TIMING_UNIT|"):
            unit = line.split("|", 1)[1].strip()
        elif line.startswith("PREDICT|KernelSVC_RBF|"):
            p = line.strip().split("|")
            rows[(p[2], int(p[3]), int(p[4]), int(p[5]))] = {
                "median_ms": float(p[6]),
                "iqr_ms": float(p[7]),
                "repeats": int(p[8]),
                "n_support": int(p[9]),
                "correct": int(p[10]),
            }
    if unit != "ms":
        raise SystemExit("Flow predict benchmark must declare TIMING_UNIT|ms")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", type=Path, help="output of bench_predict_kernel_svc.flow to join")
    parser.add_argument("--output", type=Path, help="write the joined rows as JSON")
    args = parser.parse_args()

    flow = parse_flow(args.flow) if args.flow else {}
    rows = []
    mismatches = 0
    for axis, n_query, n_train, p in CASES:
        X, y = make(0, n_train, p)
        Q, yq = make(n_train, n_query, p)
        with warnings.catch_warnings():
            # Both sides cap the solver at max_iter=1000, as the canonical rows
            # do. The cap binding on one case is expected and is not an error.
            warnings.simplefilter("ignore", ConvergenceWarning)
            model = SVC(C=1.0, kernel="rbf", gamma=1.0 / p, max_iter=1000).fit(X, y)
        timing = measure(lambda: model.predict(Q), min_window_ms=10.0, samples=7)
        pred = timing.value
        row = {
            "estimator": "KernelSVC_RBF",
            "axis": axis,
            "n_query": n_query,
            "n_train": n_train,
            "features": p,
            "sklearn_ms": timing.median_ms,
            "sklearn_iqr_ms": timing.iqr_ms,
            "sklearn_n_support": int(model.support_.size),
            "sklearn_accuracy": float((pred == yq).mean()),
            "timing_unit": "ms",
        }
        f = flow.get((axis, n_query, n_train, p))
        if f:
            flow_accuracy = f["correct"] / n_query
            row.update({
                "flow_ms": f["median_ms"],
                "flow_iqr_ms": f["iqr_ms"],
                "flow_n_support": f["n_support"],
                "flow_accuracy": flow_accuracy,
                "speedup": timing.median_ms / f["median_ms"] if f["median_ms"] > 0 else None,
                "accuracy_abs_diff": abs(flow_accuracy - row["sklearn_accuracy"]),
            })
            # One query row cannot carry an accuracy tolerance of 0.03.
            row["within_tolerance"] = n_query < 34 or row["accuracy_abs_diff"] <= ACCURACY_TOLERANCE
            if not row["within_tolerance"]:
                mismatches += 1
        rows.append(row)

    if flow:
        print("| axis | queries | train rows | features | support (sklearn / Flow) | sklearn ms | Flow ms | speedup | accuracy (sklearn / Flow) |")
        print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for r in rows:
            if "flow_ms" not in r:
                continue
            print(
                f"| {r['axis']} | {r['n_query']} | {r['n_train']} | {r['features']} | "
                f"{r['sklearn_n_support']} / {r['flow_n_support']} | "
                f"{r['sklearn_ms']:.4f} | {r['flow_ms']:.4f} | {r['speedup']:.2f}x | "
                f"{r['sklearn_accuracy']:.3f} / {r['flow_accuracy']:.3f} |"
            )
    else:
        for r in rows:
            print(f"PREDICT|KernelSVC_RBF|{r['axis']}|{r['n_query']}|{r['n_train']}|{r['features']}|{r['sklearn_ms']:.9f}|{r['sklearn_iqr_ms']:.9f}|{r['sklearn_n_support']}")

    if args.output:
        args.output.write_text(json.dumps({"timing_unit": "ms", "benchmark_mode": "predict_only", "rows": rows}, indent=2) + "\n")

    if mismatches:
        print(f"{mismatches} case(s) where accuracy differs by more than {ACCURACY_TOLERANCE}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
