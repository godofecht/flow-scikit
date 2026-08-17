from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from . import _flow_scikit_native as _native


Float32Array = npt.NDArray[np.float32]


def _matrix(value: Any) -> Float32Array:
    array = np.asarray(value, dtype=np.float32, order="C")
    if array.ndim != 2:
        raise ValueError("X must be a 2D array")
    if array.shape[0] == 0 or array.shape[1] == 0:
        raise ValueError("X must contain at least one sample and one feature")
    if not array.flags.c_contiguous:
        array = np.ascontiguousarray(array, dtype=np.float32)
    return array


def _target(value: Any, rows: int) -> Float32Array:
    array = np.asarray(value, dtype=np.float32, order="C")
    if array.ndim != 1:
        raise ValueError("y must be a 1D array")
    if array.shape[0] != rows:
        raise ValueError("X and y have inconsistent sample counts")
    if not array.flags.c_contiguous:
        array = np.ascontiguousarray(array, dtype=np.float32)
    return array


def _output(value: Any, rows: int) -> Float32Array:
    array = np.asarray(value)
    if array.dtype != np.float32:
        raise TypeError("out must have dtype float32")
    if array.ndim != 1 or array.shape[0] != rows:
        raise ValueError("out must be a 1D float32 array with one value per sample")
    if not array.flags.c_contiguous:
        raise ValueError("out must be C-contiguous")
    if not array.flags.writeable:
        raise ValueError("out must be writeable")
    return array


def _address(array: Float32Array) -> int:
    return int(array.ctypes.data)


def _check_status(status: int) -> None:
    if status != 0:
        raise RuntimeError(f"flow-scikit native call failed with status {status}")


class LinearRegression:
    def __init__(self) -> None:
        self.coef_: Float32Array | None = None
        self.intercept_: float | None = None
        self.n_features_in_: int | None = None

    def fit(self, X: Any, y: Any) -> "LinearRegression":
        x = _matrix(X)
        target = _target(y, x.shape[0])
        coef = np.empty(x.shape[1], dtype=np.float32)
        bias = np.empty(1, dtype=np.float32)

        status = _native.linear_fit(
            _address(x),
            _address(target),
            x.shape[0],
            x.shape[1],
            _address(coef),
            _address(bias),
        )
        _check_status(status)

        self.coef_ = coef
        self.intercept_ = float(bias[0])
        self.n_features_in_ = x.shape[1]
        return self

    def predict(self, X: Any) -> Float32Array:
        x = _matrix(X)
        out = np.empty(x.shape[0], dtype=np.float32)
        return self.predict_into(x, out)

    def predict_into(self, X: Any, out: Any) -> Float32Array:
        x = _matrix(X)
        output = _output(out, x.shape[0])
        coef, intercept = self._model_state(x.shape[1])

        status = _native.linear_predict(
            _address(x),
            x.shape[0],
            x.shape[1],
            _address(coef),
            intercept,
            _address(output),
        )
        _check_status(status)
        return output

    def get_params(self, deep: bool = True) -> dict[str, Any]:
        del deep
        return {}

    def set_params(self, **params: Any) -> "LinearRegression":
        if params:
            names = ", ".join(sorted(params))
            raise ValueError(f"Invalid parameter(s) for LinearRegression: {names}")
        return self

    def _model_state(self, n_features: int) -> tuple[Float32Array, float]:
        if self.coef_ is None or self.intercept_ is None or self.n_features_in_ is None:
            raise RuntimeError("estimator is not fitted")
        if n_features != self.n_features_in_:
            raise ValueError(
                f"X has {n_features} features, expected {self.n_features_in_}"
            )
        return self.coef_, self.intercept_


class Ridge(LinearRegression):
    def __init__(self, alpha: float = 1.0) -> None:
        super().__init__()
        if alpha < 0.0:
            raise ValueError("alpha must be non-negative")
        self.alpha = float(alpha)

    def fit(self, X: Any, y: Any) -> "Ridge":
        x = _matrix(X)
        target = _target(y, x.shape[0])
        coef = np.empty(x.shape[1], dtype=np.float32)
        bias = np.empty(1, dtype=np.float32)

        status = _native.ridge_fit(
            _address(x),
            _address(target),
            x.shape[0],
            x.shape[1],
            self.alpha,
            _address(coef),
            _address(bias),
        )
        _check_status(status)

        self.coef_ = coef
        self.intercept_ = float(bias[0])
        self.n_features_in_ = x.shape[1]
        return self

    def get_params(self, deep: bool = True) -> dict[str, Any]:
        del deep
        return {"alpha": self.alpha}

    def set_params(self, **params: Any) -> "Ridge":
        unknown = set(params) - {"alpha"}
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"Invalid parameter(s) for Ridge: {names}")
        if "alpha" in params:
            alpha = float(params["alpha"])
            if alpha < 0.0:
                raise ValueError("alpha must be non-negative")
            self.alpha = alpha
        return self
