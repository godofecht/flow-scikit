#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        return
    text = text.replace(old, new, 1)
    p.write_text(text, encoding="utf-8")


replace_once(
    "lib/scikit/svm.flow",
    """                } else {\n                    L = alpha_i_old - alpha_j_old\n                    H = alpha_i_old - alpha_j_old + C\n                    if L < 0.0 {\n                        L = 0.0\n                    }\n                    if H > C {\n                        H = C\n                    }\n                }\n""",
    """                } else {\n                    # Standard SMO bounds when y_i != y_j:\n                    # L=max(0, a_j-a_i), H=min(C, C+a_j-a_i).\n                    L = alpha_j_old - alpha_i_old\n                    H = alpha_j_old - alpha_i_old + C\n                    if L < 0.0 {\n                        L = 0.0\n                    }\n                    if H > C {\n                        H = C\n                    }\n                }\n""",
)

replace_once(
    "lib/scikit/mixture.flow",
    """    for k in 0 to n_components {\n        means[k] = array_new_f32(n_features)\n        variances[k] = array_new_f32(n_features)\n        let idx: i32 = rand() % n\n        for j in 0 to n_features {\n            means[k][j] = matrix_at(X, idx, j)\n            variances[k][j] = 1.0\n        }\n        weights[k] = 1.0 / (n_components as f32)\n    }\n""",
    """    # Allocate parameters first. Initialize means with farthest-point seeding\n    # so distinct components do not accidentally start in the same cluster.\n    for k in 0 to n_components {\n        means[k] = array_new_f32(n_features)\n        variances[k] = array_new_f32(n_features)\n        for j in 0 to n_features {\n            variances[k][j] = 1.0\n        }\n        weights[k] = 1.0 / (n_components as f32)\n    }\n\n    let first_idx: i32 = rand() % n\n    for j in 0 to n_features {\n        means[0][j] = matrix_at(X, first_idx, j)\n    }\n\n    let mut init_k: i32 = 1\n    while init_k < n_components {\n        let mut best_idx: i32 = 0\n        let mut best_dist: f32 = -1.0\n        for i in 0 to n {\n            let mut min_dist: f32 = 10000000000.0\n            let mut prev_k: i32 = 0\n            while prev_k < init_k {\n                let mut dist: f32 = 0.0\n                for j in 0 to n_features {\n                    let d: f32 = matrix_at(X, i, j) - means[prev_k][j]\n                    dist = dist + d * d\n                }\n                if dist < min_dist { min_dist = dist }\n                prev_k = prev_k + 1\n            }\n            if min_dist > best_dist {\n                best_dist = min_dist\n                best_idx = i\n            }\n        }\n        for j in 0 to n_features {\n            means[init_k][j] = matrix_at(X, best_idx, j)\n        }\n        init_k = init_k + 1\n    }\n""",
)

replace_once(
    "tests/test_sparse_estimators.flow",
    """    let probs_lr: ptr<f32> = logistic_predict(model_lr, X)\n    let preds_lr: ptr<f32> = logistic_decide(model_lr, probs_lr, n, 0.5)\n""",
    """    # logistic_predict returns class labels (sklearn-style predict).\n    # Keep a separate buffer because the cleanup below owns both variables.\n    let probs_lr: ptr<f32> = logistic_predict(model_lr, X)\n    let preds_lr: ptr<f32> = array_new_f32(n)\n    for i in 0 to n { preds_lr[i] = probs_lr[i] }\n""",
)
