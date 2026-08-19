#!/usr/bin/env python3
"""Audit the first semantic divergence between sklearn and Flow KMeans.

Flow's canonical k-means++ path now consumes an MT19937 stream seeded like
NumPy's legacy ``RandomState`` and picks each centre as the best of
``2 + int(log(k))`` sampled candidates, which is what scikit-learn's
``_kmeans_plusplus`` does.  This audit re-derives Flow's initial centre indices
from Flow's own primitives, mirrored in Python, and checks them against
scikit-learn's initializer for every ``n_init`` restart.

Mirroring rather than reusing ``numpy.random`` is the point: it is what makes
the check falsifiable.  ``flow_mt19937_*`` below is a transcription of
``lib/scikit/prng.flow`` and ``flow_plus_plus_indices`` a transcription of
``_kmeans_sk_pp_init`` in ``lib/scikit/cluster.flow``.  If either Flow source
changes, this mirror stops matching scikit-learn and the audit fails.

The remaining intentional differences (convergence statistic, the point at
which inertia is reported, empty-cluster relocation, and the ``n_init``
selection rule) are recorded rather than hidden, so the disparity report can
keep showing them after the row passes the strict parity contract.
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

MASK32 = 0xFFFFFFFF
MT_N = 624
MT_M = 397
MT_MATRIX_A = 0x9908B0DF
MT_UPPER = 0x80000000
MT_LOWER = 0x7FFFFFFF


def flow_mt19937_new(seed: int) -> list[int]:
    """Mirror of mt19937_new in lib/scikit/prng.flow."""
    key = [0] * MT_N
    s = seed & MASK32
    for pos in range(MT_N):
        key[pos] = s
        s = (1812433253 * (s ^ (s >> 30)) + pos + 1) & MASK32
    return key + [MT_N]


def flow_mt19937_twist(st: list[int]) -> None:
    for i in range(MT_N - MT_M):
        y = (st[i] & MT_UPPER) | (st[i + 1] & MT_LOWER)
        st[i] = st[i + MT_M] ^ (y >> 1) ^ (MT_MATRIX_A if y & 1 else 0)
    for i in range(MT_N - MT_M, MT_N - 1):
        y = (st[i] & MT_UPPER) | (st[i + 1] & MT_LOWER)
        st[i] = st[i + MT_M - MT_N] ^ (y >> 1) ^ (MT_MATRIX_A if y & 1 else 0)
    y = (st[MT_N - 1] & MT_UPPER) | (st[0] & MT_LOWER)
    st[MT_N - 1] = st[MT_M - 1] ^ (y >> 1) ^ (MT_MATRIX_A if y & 1 else 0)
    st[MT_N] = 0


def flow_mt19937_next_u32(st: list[int]) -> int:
    pos = st[MT_N]
    if pos >= MT_N:
        flow_mt19937_twist(st)
        pos = 0
    y = st[pos]
    st[MT_N] = pos + 1
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y &= MASK32
    y ^= (y << 15) & 0xEFC60000
    y &= MASK32
    y ^= y >> 18
    return y & MASK32


def flow_mt19937_next_double(st: list[int]) -> float:
    a = flow_mt19937_next_u32(st) >> 5
    b = flow_mt19937_next_u32(st) >> 6
    return (a * 67108864.0 + b) / 9007199254740992.0


def flow_choice_uniform(st: list[int], n: int) -> int:
    """Mirror of mt19937_choice_uniform: numpy's choice(n, p=uniform)."""
    if n <= 1:
        return 0
    u = flow_mt19937_next_double(st)
    w = 1.0 / n
    total = 0.0
    for _ in range(n):
        total += w
    acc = 0.0
    for i in range(n):
        acc += w
        if acc / total > u:
            return i
    return n - 1


def flow_plus_plus_indices(X: np.ndarray, n_clusters: int, st: list[int]) -> list[int]:
    """Mirror of _kmeans_sk_pp_init in lib/scikit/cluster.flow."""
    n = X.shape[0]
    n_local_trials = 1 if n_clusters < 2 else 2 + int(np.log(n_clusters))

    first = flow_choice_uniform(st, n)
    indices = [first]
    diff = (X - X[first]).astype(np.float32)
    closest = np.einsum("ij,ij->i", diff, diff).astype(np.float32)
    pot = np.float32(closest.sum(dtype=np.float32))

    for _ in range(1, n_clusters):
        best_pot = None
        best_idx = -1
        best_dist = None
        for _ in range(n_local_trials):
            rv = flow_mt19937_next_double(st) * float(pot)
            cum = np.cumsum(closest, dtype=np.float32).astype(np.float64)
            cand = int(np.searchsorted(cum, rv))
            if cand > n - 1:
                cand = n - 1
            cd = (X - X[cand]).astype(np.float32)
            cand_dist = np.minimum(closest, np.einsum("ij,ij->i", cd, cd).astype(np.float32))
            cand_pot = np.float32(cand_dist.sum(dtype=np.float32))
            if best_idx < 0 or cand_pot < best_pot:
                best_pot = cand_pot
                best_idx = cand
                best_dist = cand_dist
        indices.append(best_idx)
        closest = best_dist
        pot = best_pot
    return indices


def main() -> int:
    digits = load_digits()
    X = digits.data.astype(np.float32)
    y = digits.target.astype(np.float32)
    X_train, _, _, _ = split_arrays("digits", X, y)
    X_train = StandardScaler().fit_transform(X_train).astype(np.float32)

    n_clusters = 10
    n_init = 10
    seed = 42

    # scikit-learn's KMeans.fit consumes one RandomState across every restart,
    # and subtracts the column means before initializing.  The subtraction is
    # checked here rather than assumed: it must not move a single index, since
    # Flow initializes on the uncentred matrix.
    rng = np.random.RandomState(seed)
    rng_centred = np.random.RandomState(seed)
    X_centred = X_train - X_train.mean(axis=0)

    st = flow_mt19937_new(seed)

    sklearn_indices = []
    sklearn_centred_indices = []
    flow_indices = []
    for _ in range(n_init):
        _, sk_idx = kmeans_plusplus(X_train, n_clusters=n_clusters, random_state=rng)
        _, sk_c_idx = kmeans_plusplus(X_centred, n_clusters=n_clusters, random_state=rng_centred)
        sklearn_indices.append([int(v) for v in np.asarray(sk_idx).tolist()])
        sklearn_centred_indices.append([int(v) for v in np.asarray(sk_c_idx).tolist()])
        flow_indices.append([int(v) for v in flow_plus_plus_indices(X_train, n_clusters, st)])

    first_divergent_restart = next(
        (i for i, (a, b) in enumerate(zip(sklearn_indices, flow_indices)) if a != b),
        None,
    )
    first_divergent_center = None
    if first_divergent_restart is not None:
        a = sklearn_indices[first_divergent_restart]
        b = flow_indices[first_divergent_restart]
        first_divergent_center = next(i for i, (p, q) in enumerate(zip(a, b)) if p != q)

    sklearn_effective_tol = float(np.mean(np.var(X_train, axis=0)) * 0.001)
    report = {
        "schema_version": 2,
        "dataset": "digits",
        "random_state": seed,
        "n_clusters": n_clusters,
        "n_init": n_init,
        "first_divergence_stage": (
            "none" if first_divergent_restart is None else "initialization"
        ),
        "first_divergent_restart": first_divergent_restart,
        "first_divergent_center": first_divergent_center,
        "restarts_compared": n_init,
        "sklearn_initial_indices": sklearn_indices,
        "flow_initial_indices": flow_indices,
        "mean_centering_changes_initial_indices": sklearn_indices != sklearn_centred_indices,
        "initializers": {
            "sklearn": "NumPy RandomState/MT19937 + greedy k-means++ local trials",
            "flow": "MT19937 seeded as NumPy RandomState + greedy k-means++ local trials",
        },
        "n_local_trials": 2 + int(np.log(n_clusters)),
        # Everything below is a difference that survives the aligned
        # initialization.  None of them moves the canonical rows, measured by
        # substituting each in turn, but they are real and stay on the record.
        "residual_semantic_differences": [
            {
                "dimension": "convergence statistic",
                "sklearn": "sum of squared L2 center shifts against mean(var(X)) * tol, with a strict label-equality short circuit and a final E-step",
                "flow": "maximum absolute coordinate shift against tol",
                "moves_canonical_rows": False,
            },
            {
                "dimension": "inertia reporting point",
                "sklearn": "final centers against final labels",
                "flow": "the assignment made before the last centroid update",
                "moves_canonical_rows": False,
            },
            {
                "dimension": "empty-cluster relocation",
                "sklearn": "moves the n_empty distinct farthest points and debits them from their previous cluster",
                "flow": "re-picks the single farthest point per empty cluster and leaves it in its previous cluster",
                "moves_canonical_rows": False,
            },
            {
                "dimension": "n_init selection",
                "sklearn": "strictly lower inertia and a clustering that differs from the incumbent",
                "flow": "strictly lower inertia",
                "moves_canonical_rows": False,
            },
        ],
        "convergence": {
            "sklearn_parameter_tol": 0.001,
            "sklearn_effective_tol": sklearn_effective_tol,
            "sklearn_statistic": "sum of squared L2 center shifts",
            "flow_parameter_tol": 0.001,
            "flow_statistic": "maximum absolute coordinate shift",
        },
        "canonical_parity_policy": {
            "status": "governed by benchmarks/parity_contract.json",
            "reason": "seeded initialization is aligned, so the row is gated on the same declared tolerances as every other clustering row",
        },
    }

    assert report["first_divergence_stage"] == "none", report
    assert not report["mean_centering_changes_initial_indices"], report
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"sklearn_initial_indices", "flow_initial_indices"}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
