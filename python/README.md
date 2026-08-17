# flow-scikit Python package

This directory builds a CPython package around the native Flow implementation in `lib/scikit`.

The boundary is intentionally narrow. Python owns contiguous `float32` NumPy buffers, the extension passes their addresses to a small Flow ABI, and Flow executes the estimator work natively. Already-contiguous `float32` inputs are borrowed without a data copy. `predict_into` also lets latency-sensitive callers reuse an output buffer instead of allocating one per prediction.

Build from the repository root with a Flow checkout available at `.flow-toolchain`, through `FLOW_ROOT`, or through `--flow-root`:

```bash
python tools/build_python_package.py --flow-root ../flow
python -m pip install dist/flow_scikit-*.whl
```

The initial package surface is:

```python
import numpy as np
from flow_scikit import LinearRegression, Ridge

X = np.ascontiguousarray([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=np.float32)
y = np.ascontiguousarray([4, 6, 1, 3], dtype=np.float32)

model = LinearRegression().fit(X, y)

out = np.empty(X.shape[0], dtype=np.float32)
model.predict_into(X, out)
```

Wheel users do not need the Flow compiler. Wheel builders need the Flow compiler source and a BLAS implementation; Linux uses OpenBLAS by default and macOS uses Accelerate. `FLOW_SCIKIT_BLAS_LIB` can override the linked BLAS library list for custom toolchains.
