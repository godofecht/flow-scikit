#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        return
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "lib/scikit/svm.flow",
    """    let w64: ptr<f64> = array_new_f64(n_features)\n    let alpha: ptr<f64> = array_new_f64(n_samples)\n""",
    """    let w64: ptr<f64> = array_new_f64(n_features)\n    let mut bias64: f64 = 0.0\n    let alpha: ptr<f64> = array_new_f64(n_samples)\n""",
)
replace_once(
    "lib/scikit/svm.flow",
    """            # Q_ii = x_i^T x_i (only non-zero entries contribute)\n            let mut Q_ii: f64 = 0.0\n""",
    """            # Augment sparse samples with the same constant bias feature\n            # used by the dense solver.\n            let mut Q_ii: f64 = 1.0\n""",
)
replace_once(
    "lib/scikit/svm.flow",
    """            let mut w_dot_x: f64 = 0.0\n            k = start\n""",
    """            let mut w_dot_x: f64 = bias64\n            k = start\n""",
)
replace_once(
    "lib/scikit/svm.flow",
    """                while k < end {\n                    w64[S.indices[k]] = w64[S.indices[k]] + delta * (S.data[k]) as f64\n                    k = k + 1\n                }\n\n                alpha[i] = alpha_new\n""",
    """                while k < end {\n                    w64[S.indices[k]] = w64[S.indices[k]] + delta * (S.data[k]) as f64\n                    k = k + 1\n                }\n                bias64 = bias64 + delta\n\n                alpha[i] = alpha_new\n""",
)
replace_once(
    "lib/scikit/svm.flow",
    """    # Compute bias from free support vectors\n    let mut bias_sum: f64 = 0.0\n    let mut n_sv: i32 = 0\n    for i in 0 to n_samples {\n        if alpha[i] > 0.0 and alpha[i] < C64 {\n            let mut w_dot_x: f64 = 0.0\n            let start2: i32 = S.indptr[i]\n            let end2: i32 = S.indptr[i + 1]\n            let mut k2: i32 = start2\n            while k2 < end2 {\n                w_dot_x = w_dot_x + w64[S.indices[k2]] * (S.data[k2]) as f64\n                k2 = k2 + 1\n            }\n            bias_sum = bias_sum + ((y_dual[i]) as f64 - w_dot_x)\n            n_sv = n_sv + 1\n        }\n    }\n    if n_sv > 0 {\n        bias = (bias_sum / (n_sv as f64)) as f32\n    }\n""",
    """    # Bias is optimized jointly as the augmented constant feature.\n    bias = bias64 as f32\n""",
)
