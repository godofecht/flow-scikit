#!/usr/bin/env python3
"""Audit the first semantic divergence between sklearn and Flow KMeans.

The canonical Flow implementation intentionally uses Flow's xorshift32 PRNG,
whereas sklearn's ``random_state=42`` is consumed by NumPy's legacy
RandomState/MT19937 inside greedy k-means++.  This audit makes that difference
explicit and also records the convergence-statistic mismatch so benchmark
parity can distinguish algorithmic equivalence from bit-identical execution.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.cluster import kmeans_plusplus
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler

from fixtures import split_arrays

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "kmeans_semantics_audit.json"


def xorshift32(state: int) -> int:
    state &= 0xFFFFFFFF
    if state == 0:
        state = 1
    state ^= (state << 13) & 0xFFFFFFFF
    state ^= state >> 17
    state ^= (state << 5) & 0xFFFFFFFF
    return state & 0xFFFFFFFF


def flow_rand_int(state: int, max_value: int) -> tuple[int, int]:
    state = xorshift32(state)
    return state, (state & 0x7FFFFFFF) % max_value


def flow_kmeans_plus_plus_indices(X: np.ndarray, n_clusters: int, seed: int) -> list[int]:
    """Mirror the current Flow initializer, including its single-trial picks."""
    state = seed & 0xFFFFFFFF or 1
    state, first = flow_rand_int(state, len(X))
    chosen = [first]
    dist_sq = np.sum((X - X[first]) ** 2, axis=1, dtype=np.float64)

    for _ in range(1, n_clusters):
        total = float(dist_sq.sum())
        if total <= 0.0:
            state, idx = flow_rand_int(state, len(X))
        else:
            state, raw = flow_rand_int(state, 2_147_483_647)
            threshold = raw / 2_147_483_647.0 * total
            idx = int(np.searchsorted(np.cumsum(dist_sq), threshold, side="left"))
            idx = min(idx, len(X) - 1)
        chosen.append(idx)
        new_dist = np.sum((X - X[idx]) ** 2, axis=1, dtype=np.float64)
        dist_sq = np.minimum(dist_sq, new_dist)
    return chosen


def nearest_indices(X: np.ndarray, centers: np.ndarray) -> list[int]:
    # kmeans_plusplus returns exact rows for the unweighted canonical dataset.
    result = []
    for center in centers:
        result.append(int(np.argmin(np.sum((X - center) ** 2, axis=1))))
    return result


def main() -> int:
    digits = load_digits()
    X = digits.data.astype(np.float32)
    y = digits.target.astype(np.float32)
    X_train, _, _, _ = split_arrays("digits", X, y)
    X_train = StandardScaler().fit_transform(X_train).astype(np.float32)

    rng = np.random.RandomState(42)
    sk_centers, sk_indices = kmeans_plusplus(
        X_train,
        n_clusters=10,
        random_state=rng,
    )
    # Preserve an independently-derived index check so an upstream API change
    # that stops returning indices is obvious rather than silently accepted.
    sk_indices = [int(v) for v in np.asarray(sk_indices).tolist()]
    nearest = nearest_indices(X_train, np.asarray(sk_centers))
    flow_indices = flow_kmeans_plus_plus_indices(X_train, 10, 42)

    first_center_divergence = next(
        (i for i, (a, b) in enumerate(zip(sk_indices, flow_indices)) if a != b),
        None,
    )

    sklearn_effective_tol = float(np.mean(np.var(X_train, axis=0)) * 0.001)
    report = {
        "schema_version": 1,
        "dataset": "digits",
        "random_state": 42,
        "n_clusters": 10,
        "first_divergence_stage": "initialization" if first_center_divergence is not None else "post-initialization",
        "first_divergent_center": first_center_divergence,
        "sklearn_initial_indices": sk_indices,
        "sklearn_initial_indices_nearest_row_check": nearest,
        "flow_initial_indices": flow_indices,
        "initializers": {
            "sklearn": "NumPy RandomState/MT19937 + greedy k-means++ local trials",
            "flow": "xorshift32 + one weighted candidate per center",
        },
        "convergence": {
            "sklearn_parameter_tol": 0.001,
            "sklearn_effective_tol": sklearn_effective_tol,
            "sklearn_statistic": "sum of squared L2 center shifts",
            "flow_parameter_tol": 0.001,
            "flow_statistic": "maximum absolute coordinate shift",
        },
        "canonical_parity_policy": {
            "status": "approximately equivalent",
            "reason": "random-state and convergence trajectories are not bit-identical; compare permutation-invariant ARI and final inertia",
            "ari_absolute_tolerance": 0.07,
            "inertia_relative_tolerance": 0.10,
        },
    }

    assert report["first_divergence_stage"] == "initialization", report
    assert sk_indices == nearest, "sklearn kmeans++ centers are expected to be training rows"
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
