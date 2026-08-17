from __future__ import annotations

import numpy as np
import pytest

from flow_scikit import LinearRegression, Ridge


def regression_fixture() -> tuple[np.ndarray, np.ndarray]:
    X = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
            [2.0, 1.0],
            [1.0, 2.0],
        ],
        dtype=np.float32,
    )
    y = 4.0 + 2.0 * X[:, 0] - 3.0 * X[:, 1]
    return X, y.astype(np.float32)


def test_linear_regression_fit_and_predict() -> None:
    X, y = regression_fixture()
    model = LinearRegression().fit(X, y)

    np.testing.assert_allclose(model.coef_, [2.0, -3.0], rtol=1e-4, atol=1e-4)
    assert model.intercept_ == pytest.approx(4.0, rel=1e-4, abs=1e-4)
    np.testing.assert_allclose(model.predict(X), y, rtol=1e-4, atol=1e-4)


def test_predict_into_reuses_caller_buffer() -> None:
    X, y = regression_fixture()
    model = LinearRegression().fit(X, y)
    out = np.empty(X.shape[0], dtype=np.float32)

    returned = model.predict_into(X, out)

    assert returned is out
    np.testing.assert_allclose(out, y, rtol=1e-4, atol=1e-4)


def test_float64_input_is_normalized_at_boundary() -> None:
    X, y = regression_fixture()
    model = LinearRegression().fit(X.astype(np.float64), y.astype(np.float64))

    prediction = model.predict(X.astype(np.float64))

    assert prediction.dtype == np.float32
    np.testing.assert_allclose(prediction, y, rtol=1e-4, atol=1e-4)


def test_ridge_uses_same_native_prediction_surface() -> None:
    X, y = regression_fixture()
    model = Ridge(alpha=0.25).fit(X, y)
    out = model.predict(X)

    assert out.shape == y.shape
    assert np.isfinite(out).all()


def test_feature_count_is_checked() -> None:
    X, y = regression_fixture()
    model = LinearRegression().fit(X, y)

    with pytest.raises(ValueError, match="features"):
        model.predict(np.ones((2, 3), dtype=np.float32))
