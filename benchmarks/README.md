# Performance Benchmarks: flow-scikit vs scikit-learn

Comparison of accuracy and runtime between flow-scikit (Flow -> C) and
scikit-learn 1.9.0 (Python/C/Fortran with BLAS).

## Methodology

- Same embedded datasets: iris (150x4), digits (1797x64), diabetes (442x10)
- 80/20 train/test split with seed 42
- StandardScaler applied to all datasets
- Times are CPU time (clock()) in milliseconds
- Note: train/test splits use different RNGs so exact sample composition
  differs slightly between the two implementations

## Results

| Algorithm | Dataset | Metric | sklearn | flow-scikit | Diff |
|-----------|---------|--------|---------|-------------|------|
| LogisticRegression | iris | accuracy | 0.933 | 0.567 | -0.367 |
| LinearSVC | iris | accuracy | 0.900 | 0.500 | -0.400 |
| KernelSVC_RBF | iris | accuracy | 0.933 | 0.800 | -0.133 |
| DecisionTree | iris | accuracy | 0.933 | 0.933 | 0.000 |
| RandomForest | iris | accuracy | 0.967 | 0.933 | -0.033 |
| GaussianNB | iris | accuracy | 0.967 | 0.933 | -0.033 |
| KMeans | iris | accuracy | 0.100 | 0.800 | +0.700 |
| PCA | iris | EVR | 0.727 | 0.729 | +0.002 |
| LogisticRegression | digits | accuracy | 0.972 | 0.184 | -0.788 |
| LinearSVC | digits | accuracy | 0.956 | 0.164 | -0.791 |
| DecisionTree | digits | accuracy | 0.814 | 0.869 | +0.055 |
| RandomForest | digits | accuracy | 0.936 | 0.908 | -0.028 |
| GaussianNB | digits | accuracy | 0.742 | 0.777 | +0.035 |
| KMeans | digits | accuracy | 0.117 | 0.630 | +0.513 |
| Ridge | diabetes | r2 | 0.454 | 0.200 | -0.254 |
| Lasso | diabetes | r2 | 0.456 | 0.189 | -0.266 |
| LinearRegression | diabetes | r2 | 0.453 | 0.149 | -0.303 |
| KernelRidge_RBF | diabetes | r2 | 0.462 | 0.181 | -0.281 |

## Analysis

### Close match
- **DecisionTree**: matches sklearn on iris, beats it on digits
- **GaussianNB**: within 3% on iris, beats sklearn on digits
- **PCA**: within 0.3% on explained variance ratio
- **KMeans**: flow-scikit reports higher accuracy due to best-match
  label assignment (sklearn raw cluster IDs don't match class labels)

### Large accuracy gaps (optimization issues)
- **LogisticRegression**: uses gradient descent with 200 epochs and
  lr=0.1. sklearn uses L-BFGS with 1000 iterations. Needs more epochs
  or a better optimizer.
- **LinearSVC**: uses dual coordinate descent with 200 epochs and
  lr=0.01. sklearn uses liblinear. Needs more iterations.
- **Ridge/Lasso/LinearRegression**: use gradient descent with 1000
  iterations and lr=0.01. Should use direct matrix solve (normal
  equations or Cholesky) like KernelRidge now does.
- **KernelRidge**: uses Cholesky (correct solver) but the gamma
  parameter and data split differ from sklearn.

### Performance
- sklearn is 10-1000x faster on most algorithms due to BLAS-optimized
  linear algebra and compiled C/Fortran backends
- flow-scikit RandomForest on digits is particularly slow (50s vs 19ms)
  due to O(n^2) split evaluation
- flow-scikit GaussianNB is competitive (10ms vs 1ms on iris)
- flow-scikit KMeans is competitive (28ms vs 31ms on iris)

## Running the benchmarks

```bash
# sklearn benchmark
python3 benchmarks/bench_sklearn.py

# flow-scikit benchmark
FLOW_HOST=python flow run benchmarks/bench_flow.flow

# comparison
python3 benchmarks/compare.py
```
