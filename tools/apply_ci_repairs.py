#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        return
    text = text.replace(old, new, 1)
    p.write_text(text, encoding="utf-8")


# First-pass SMO bounds repair.
replace_once(
    "lib/scikit/svm.flow",
    """                } else {\n                    L = alpha_i_old - alpha_j_old\n                    H = alpha_i_old - alpha_j_old + C\n                    if L < 0.0 {\n                        L = 0.0\n                    }\n                    if H > C {\n                        H = C\n                    }\n                }\n""",
    """                } else {\n                    # Standard SMO bounds when y_i != y_j:\n                    # L=max(0, a_j-a_i), H=min(C, C+a_j-a_i).\n                    L = alpha_j_old - alpha_i_old\n                    H = alpha_j_old - alpha_i_old + C\n                    if L < 0.0 {\n                        L = 0.0\n                    }\n                    if H > C {\n                        H = C\n                    }\n                }\n""",
)

# Use the largest error-gap partner instead of a pseudo-random SMO partner.
replace_once(
    "lib/scikit/svm.flow",
    """                let mut j: i32 = (iter * 7 + i * 13 + 3) % n\n                if j < 0 {\n                    j = j + n\n                }\n                if j == i {\n                    j = (j + 1) % n\n                }\n\n                let mut ej: f32 = 0.0\n                for k in 0 to n {\n                    ej = ej + alphas[k] * y_dual[k] * matrix_at(K, j, k)\n                }\n                ej = ej + b - y_dual[j]\n""",
    """                # Platt-style second-choice heuristic: choose the partner\n                # with the largest |E_i - E_j| so each step has useful gain.\n                let mut j: i32 = -1\n                let mut best_gap: f32 = -1.0\n                for candidate in 0 to n {\n                    if candidate != i {\n                        let mut candidate_e: f32 = 0.0\n                        for k in 0 to n {\n                            candidate_e = candidate_e + alphas[k] * y_dual[k] * matrix_at(K, candidate, k)\n                        }\n                        candidate_e = candidate_e + b - y_dual[candidate]\n                        let mut gap: f32 = ei - candidate_e\n                        if gap < 0.0 { gap = -gap }\n                        if gap > best_gap {\n                            best_gap = gap\n                            j = candidate\n                        }\n                    }\n                }\n                if j < 0 { continue }\n\n                let mut ej: f32 = 0.0\n                for k in 0 to n {\n                    ej = ej + alphas[k] * y_dual[k] * matrix_at(K, j, k)\n                }\n                ej = ej + b - y_dual[j]\n""",
)

# Do not terminate SMO after a single unchanged pass.
replace_once(
    "lib/scikit/svm.flow",
    """    let mut iter: i32 = 0\n    while iter < max_iter {\n        let mut num_changed: i32 = 0\n""",
    """    let mut iter: i32 = 0\n    let mut passes_without_change: i32 = 0\n    while iter < max_iter && passes_without_change < 5 {\n        let mut num_changed: i32 = 0\n""",
)
replace_once(
    "lib/scikit/svm.flow",
    """        iter = iter + 1\n        if num_changed == 0 {\n            break\n        }\n    }\n\n    let result: SMOResult = SMOResult { alphas: alphas, b: b }\n""",
    """        iter = iter + 1\n        if num_changed == 0 {\n            passes_without_change = passes_without_change + 1\n        } else {\n            passes_without_change = 0\n        }\n    }\n\n    let result: SMOResult = SMOResult { alphas: alphas, b: b }\n""",
)

# First-pass farthest-point GMM seeding.
replace_once(
    "lib/scikit/mixture.flow",
    """    for k in 0 to n_components {\n        means[k] = array_new_f32(n_features)\n        variances[k] = array_new_f32(n_features)\n        let idx: i32 = rand() % n\n        for j in 0 to n_features {\n            means[k][j] = matrix_at(X, idx, j)\n            variances[k][j] = 1.0\n        }\n        weights[k] = 1.0 / (n_components as f32)\n    }\n""",
    """    # Allocate parameters first. Initialize means with farthest-point seeding\n    # so distinct components do not accidentally start in the same cluster.\n    for k in 0 to n_components {\n        means[k] = array_new_f32(n_features)\n        variances[k] = array_new_f32(n_features)\n        for j in 0 to n_features {\n            variances[k][j] = 1.0\n        }\n        weights[k] = 1.0 / (n_components as f32)\n    }\n\n    let first_idx: i32 = rand() % n\n    for j in 0 to n_features {\n        means[0][j] = matrix_at(X, first_idx, j)\n    }\n\n    let mut init_k: i32 = 1\n    while init_k < n_components {\n        let mut best_idx: i32 = 0\n        let mut best_dist: f32 = -1.0\n        for i in 0 to n {\n            let mut min_dist: f32 = 10000000000.0\n            let mut prev_k: i32 = 0\n            while prev_k < init_k {\n                let mut dist: f32 = 0.0\n                for j in 0 to n_features {\n                    let d: f32 = matrix_at(X, i, j) - means[prev_k][j]\n                    dist = dist + d * d\n                }\n                if dist < min_dist { min_dist = dist }\n                prev_k = prev_k + 1\n            }\n            if min_dist > best_dist {\n                best_dist = min_dist\n                best_idx = i\n            }\n        }\n        for j in 0 to n_features {\n            means[init_k][j] = matrix_at(X, best_idx, j)\n        }\n        init_k = init_k + 1\n    }\n""",
)

# Estimate initial diagonal covariance from nearest seeded component instead of
# starting every component at variance 1.0, which can merge separated blobs.
replace_once(
    "lib/scikit/mixture.flow",
    """    let resp: ptr<ptr<f32> > = malloc((n as i64) * 8) as ptr<ptr<f32> >\n""",
    """    let init_counts: ptr<i32> = malloc((n_components as i64) * 4) as ptr<i32>\n    for k in 0 to n_components {\n        init_counts[k] = 0\n        for j in 0 to n_features { variances[k][j] = 0.0 }\n    }\n    for i in 0 to n {\n        let mut nearest: i32 = 0\n        let mut nearest_dist: f32 = 10000000000.0\n        for k in 0 to n_components {\n            let mut dist: f32 = 0.0\n            for j in 0 to n_features {\n                let d: f32 = matrix_at(X, i, j) - means[k][j]\n                dist = dist + d * d\n            }\n            if dist < nearest_dist {\n                nearest_dist = dist\n                nearest = k\n            }\n        }\n        init_counts[nearest] = init_counts[nearest] + 1\n        for j in 0 to n_features {\n            let d: f32 = matrix_at(X, i, j) - means[nearest][j]\n            variances[nearest][j] = variances[nearest][j] + d * d\n        }\n    }\n    for k in 0 to n_components {\n        if init_counts[k] > 0 {\n            weights[k] = (init_counts[k] as f32) / (n as f32)\n            for j in 0 to n_features {\n                variances[k][j] = variances[k][j] / (init_counts[k] as f32)\n                if variances[k][j] < 0.001 { variances[k][j] = 0.001 }\n            }\n        } else {\n            weights[k] = 1.0 / (n_components as f32)\n            for j in 0 to n_features { variances[k][j] = 1.0 }\n        }\n    }\n    free(init_counts as ptr<void>)\n\n    let resp: ptr<ptr<f32> > = malloc((n as i64) * 8) as ptr<ptr<f32> >\n""",
)

# Sparse logistic gradients are allocated with malloc-backed storage; explicitly
# zero them before accumulating a full-batch gradient.
replace_once(
    "lib/scikit/linear.flow",
    """        for epoch in 0 to epochs {\n            let grad_w: ptr<f32> = array_new_f32(n)\n            let mut grad_b: f32 = 0.0\n\n            for i in 0 to n_samples {\n""",
    """        for epoch in 0 to epochs {\n            let grad_w: ptr<f32> = array_new_f32(n)\n            for j in 0 to n { grad_w[j] = 0.0 }\n            let mut grad_b: f32 = 0.0\n\n            for i in 0 to n_samples {\n""",
)

# logistic_predict already returns labels; do not threshold those labels again.
replace_once(
    "tests/test_sparse_estimators.flow",
    """    let probs_lr: ptr<f32> = logistic_predict(model_lr, X)\n    let preds_lr: ptr<f32> = logistic_decide(model_lr, probs_lr, n, 0.5)\n""",
    """    # logistic_predict returns class labels (sklearn-style predict).\n    # Keep a separate buffer because the cleanup below owns both variables.\n    let probs_lr: ptr<f32> = logistic_predict(model_lr, X)\n    let preds_lr: ptr<f32> = array_new_f32(n)\n    for i in 0 to n { preds_lr[i] = probs_lr[i] }\n""",
)
