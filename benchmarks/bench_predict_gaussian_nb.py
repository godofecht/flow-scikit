#!/usr/bin/env python3
"""Prediction-only scaling benchmark for GaussianNB, scikit-learn side.

Builds the same float32 inputs as bench_predict_gaussian_nb.flow, times
``GaussianNB.predict`` alone with the shared adaptive timer, and optionally
joins the Flow output into one table.

    python benchmarks/bench_predict_gaussian_nb.py --flow flow_predict_gnb.txt
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.naive_bayes import GaussianNB

from timing import measure

N_TRAIN = 2000

# (axis, n_query, features, classes), in the order the Flow benchmark emits.
CASES = (
    [("batch", n, 64, 10) for n in (1, 10, 100, 360, 1000, 10000)]
    + [("features", 1000, p, 10) for p in (4, 8, 16, 32, 128, 256)]
    + [("classes", 1000, 64, c) for c in (2, 3, 5, 20, 50)]
)


def make(first_row: int, n: int, p: int, n_classes: int):
    i = np.arange(first_row, first_row + n, dtype=np.int64)[:, None]
    j = np.arange(p, dtype=np.int64)[None, :]
    cls = i % n_classes
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
        elif line.startswith("PREDICT|GaussianNB|"):
            p = line.strip().split("|")
            rows[(p[2], int(p[3]), int(p[4]), int(p[5]))] = {
                "median_ms": float(p[6]),
                "iqr_ms": float(p[7]),
                "repeats": int(p[8]),
                "correct": int(p[9]),
                "label_sum": int(p[10]),
            }
    if unit != "ms":
        raise SystemExit("Flow predict benchmark must declare TIMING_UNIT|ms")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", type=Path, help="output of bench_predict_gaussian_nb.flow to join")
    parser.add_argument("--output", type=Path, help="write the joined rows as JSON")
    args = parser.parse_args()

    flow = parse_flow(args.flow) if args.flow else {}
    rows = []
    mismatches = 0
    for axis, n_query, p, n_classes in CASES:
        X, y = make(0, N_TRAIN, p, n_classes)
        Q, yq = make(N_TRAIN, n_query, p, n_classes)
        model = GaussianNB(var_smoothing=1e-9).fit(X, y)
        timing = measure(lambda: model.predict(Q), min_window_ms=10.0, samples=7)
        pred = timing.value
        row = {
            "estimator": "GaussianNB",
            "axis": axis,
            "n_query": n_query,
            "features": p,
            "classes": n_classes,
            "sklearn_ms": timing.median_ms,
            "sklearn_iqr_ms": timing.iqr_ms,
            "sklearn_correct": int((pred == yq).sum()),
            "sklearn_label_sum": int(pred.astype(np.int64).sum()),
            "timing_unit": "ms",
        }
        f = flow.get((axis, n_query, p, n_classes))
        if f:
            row.update({
                "flow_ms": f["median_ms"],
                "flow_iqr_ms": f["iqr_ms"],
                "flow_correct": f["correct"],
                "flow_label_sum": f["label_sum"],
                "speedup": timing.median_ms / f["median_ms"] if f["median_ms"] > 0 else None,
                "predictions_agree": f["correct"] == row["sklearn_correct"] and f["label_sum"] == row["sklearn_label_sum"],
            })
            if not row["predictions_agree"]:
                mismatches += 1
        rows.append(row)

    if flow:
        print("| axis | queries | features | classes | sklearn ms | Flow ms | speedup | predictions agree |")
        print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
        for r in rows:
            if "flow_ms" not in r:
                continue
            print(
                f"| {r['axis']} | {r['n_query']} | {r['features']} | {r['classes']} | "
                f"{r['sklearn_ms']:.4f} | {r['flow_ms']:.4f} | {r['speedup']:.2f}x | "
                f"{'yes' if r['predictions_agree'] else 'no'} |"
            )
    else:
        for r in rows:
            print(f"PREDICT|GaussianNB|{r['axis']}|{r['n_query']}|{r['features']}|{r['classes']}|{r['sklearn_ms']:.9f}|{r['sklearn_iqr_ms']:.9f}")

    if args.output:
        args.output.write_text(json.dumps({"timing_unit": "ms", "benchmark_mode": "predict_only", "rows": rows}, indent=2) + "\n")

    if mismatches:
        print(f"{mismatches} case(s) where the two sides predicted different labels")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
