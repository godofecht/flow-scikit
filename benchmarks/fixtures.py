#!/usr/bin/env python3
"""Canonical benchmark fixture loading and validation."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SPLITS_PATH = ROOT / "split_indices.json"


def load_split_indices(dataset: str, n_samples: int) -> tuple[np.ndarray, np.ndarray]:
    data = json.loads(SPLITS_PATH.read_text())
    if dataset not in data:
        raise KeyError(f"missing canonical split for {dataset}")
    row = data[dataset]
    train = np.asarray(row["train_idx"], dtype=np.int64)
    test = np.asarray(row["test_idx"], dtype=np.int64)

    if len(train) != int(row["n_train"]) or len(test) != int(row["n_test"]):
        raise ValueError(f"{dataset}: fixture length does not match declared counts")
    if len(train) + len(test) != n_samples:
        raise ValueError(f"{dataset}: fixture contains {len(train) + len(test)} indices for {n_samples} samples")

    combined = np.concatenate([train, test])
    if combined.size != n_samples or not np.array_equal(np.sort(combined), np.arange(n_samples)):
        raise ValueError(f"{dataset}: fixture is not an exact partition of 0..{n_samples - 1}")
    if np.intersect1d(train, test).size:
        raise ValueError(f"{dataset}: train/test fixture overlap")
    return train, test


def split_arrays(dataset: str, X: np.ndarray, y: np.ndarray):
    train_idx, test_idx = load_split_indices(dataset, len(X))
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


def main() -> int:
    expected = {"iris": 150, "digits": 1797, "diabetes": 442}
    for name, n in expected.items():
        train, test = load_split_indices(name, n)
        print(f"{name}: {len(train)} train / {len(test)} test; canonical fixture OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
