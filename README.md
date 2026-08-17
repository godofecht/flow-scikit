# flow-scikit

A compiled machine-learning library for [Flow](https://github.com/flooooooooooow/flow), inspired by scikit-learn's estimator ecosystem while exploring a smaller native runtime, explicit APIs, and deployment beyond Python.

> **Status:** experimental, actively developed, and not affiliated with or endorsed by the scikit-learn project.

[Documentation & benchmarks](https://godofecht.github.io/flow-scikit/) · [Flow language](https://github.com/flooooooooooow/flow) · [Examples](examples/) · [Tests](tests/)

## What this project is

flow-scikit asks a fairly direct question: how much of the practical scikit-learn experience can be reproduced in a statically typed compiled language without carrying a Python runtime into deployment?

The goal is not a line-for-line port. The project implements familiar estimators, preprocessing, metrics, model selection and composition in Flow, then uses the rewrite as an opportunity to test different API decisions and native deployment characteristics.

The repository currently covers classification, regression, clustering, decomposition, preprocessing, feature selection, model selection, ensembles, SVMs, Gaussian processes, mixture models, neural networks, covariance, imputation, manifold learning, kernel approximation, multi-output learning and related utilities.

## Evidence first

The benchmark site contains the complete measured results rather than only selected wins. It reports predictive parity separately from runtime performance and includes fit/predict timings, Iris, Digits and Diabetes workloads, deterministic parity tests, native footprint/startup measurements, and Android results.

A timing-unit error in an earlier version of the benchmark presentation was also corrected: Python `time.perf_counter()` measurements are seconds, while the Flow benchmark reports milliseconds. Comparisons now normalize both sides to milliseconds before calculating speedup. The benchmark tooling was fixed as well as the presentation so regenerated results use the same units.

Current headline evidence includes **16/16 deterministic parity checks passing**, **10/17 usable headline timing comparisons won by Flow**, a recorded **~1.4 MB native footprint**, and a recorded **~65× cold-start advantage** in the published startup comparison. These figures describe the benchmark suite in this repository; they are not a claim that Flow is universally faster than scikit-learn.

See the [full benchmark report](https://godofecht.github.io/flow-scikit/benchmarks.html) for the individual results, methodology and reproduction details.

## Why Flow?

Flow is a statically typed compiled language with a C backend, algebraic effects and autodiff. For this project that makes it possible to investigate ML APIs in a setting with native binaries, explicit memory/layout decisions, small deployment artifacts and no mandatory Python interpreter.

That matters most where startup latency, binary size, embedding, cross-compilation or deployment constraints matter more than access to the enormous Python scientific-computing ecosystem.

flow-scikit is therefore best understood as both a usable library experiment and a systems experiment: it tests which parts of the scikit-learn programming model are fundamental and which parts are consequences of Python, NumPy and historical compatibility constraints.

## Design differences

The project intentionally does not preserve every scikit-learn API decision. Several interfaces are experiments motivated by long-running usability discussions around the ecosystem.

`OneHotEncoder` handles unknown categories without making an unseen category an automatic pipeline failure. Classification APIs distinguish probability-producing prediction from explicit class decisions. Validation follows a consistent `ensure_*` vocabulary. Structured report types avoid dictionary-key collisions. Table ingestion is normalized behind one internal interface. Progress reporting can use Flow's effect system instead of integer verbosity levels. Calibration utilities include minimum-bin support and confidence information. Linear-model APIs can represent terms and penalties explicitly.

These are design choices in flow-scikit, not assertions that upstream scikit-learn must adopt the same solutions.

## Scope

The implementation is organized under `lib/scikit/` and currently includes the following major areas:

| Area | Representative support |
| --- | --- |
| Preprocessing | StandardScaler, MinMaxScaler, RobustScaler, encoders, imputers, polynomial features |
| Linear models | LinearRegression, LogisticRegression, Ridge, Lasso, ElasticNet, SGD, Bayesian and robust models |
| Neighbors | KNN classification/regression, nearest neighbors, radius neighbors, LOF |
| SVM | LinearSVC/SVR, kernel SVC, NuSVC/NuSVR, OneClassSVM |
| Trees & ensembles | Decision trees, random forests, extra trees, boosting, bagging, voting, stacking, isolation forest |
| Clustering | KMeans, MiniBatchKMeans, DBSCAN, agglomerative, spectral, OPTICS, Birch and others |
| Decomposition | PCA, SVD, NMF, ICA, SparsePCA, KernelPCA, factor analysis, dictionary learning |
| Model selection | train/test split, CV, grid/random search, learning and validation curves |
| Metrics | Classification, regression, clustering, ranking and pairwise metrics |
| Feature selection | SelectKBest, variance threshold, RFE/RFECV, sequential selection |
| Additional modules | Gaussian processes, mixture models, neural networks, covariance, manifold, kernels, multi-output, semi-supervised learning |

The source tree is the authoritative inventory; coverage changes quickly while the project is under active development.

## Quick start

Clone Flow and flow-scikit, then point the Flow compiler at an example or test. The repository CI pins the Flow toolchain revision used for validation, which is the safest reference for a reproducible build.

```bash
git clone https://github.com/flooooooooooow/flow.git
git clone https://github.com/godofecht/flow-scikit.git
cd flow-scikit
python tools/run_all.py
```

`tools/run_all.py` respects the repository's Flow toolchain configuration and is also what the full CI suite exercises.

## Testing and reproducibility

CI performs syntax/import validation and runs the complete Flow test/example suite. Benchmark claims should be treated as reproducible measurements rather than constants: compiler revisions, optimization settings, BLAS implementations, hardware and estimator implementations can all move the numbers.

For that reason, performance results live with their methodology and raw benchmark data in the repository. If a result looks surprising, reproduce it before generalizing from it.

## Relationship to scikit-learn

flow-scikit is an independent project. It takes substantial inspiration from scikit-learn's estimator vocabulary and from public discussions about its API, but it is not an official port, fork or subproject.

### Maintainer note on an upstream automation incident

During development, I had an automated coding agent configured to create pull requests. At one point the agent was instructed to submit work to the upstream **Flow language repository**, but it instead submitted pull requests to a **scikit-related upstream repository**. Those submissions were unintended automation output rather than a deliberate attempt to send a stream of changes to that project.

The incident is relevant to this repository's history because it exposed a failure mode that agent-driven open-source development now has to handle: repository targeting can fail, and automated contribution systems need safeguards on both the submitting and receiving sides. I believe a mature contribution workflow should be able to identify a burst of obviously automated, mis-targeted submissions, stop or close them, and establish what happened before escalating an account-level response.

In this case, the maintainers chose to ban my account. I disagree with that response, but this project is not intended as a vehicle for pursuing that disagreement. The practical lesson has been incorporated here: automated contributions need explicit repository allow-lists, validation before publication, bounded submission rates, and human-visible CI/review gates.

That history should also make the relationship unambiguous: **flow-scikit is independent of scikit-learn and its maintainers.** Technical comparisons here should stand or fall on reproducible code and measurements, not on project politics.

## Contributing

Contributions are welcome, particularly when they improve correctness, parity, benchmarks, tests, documentation or reproducibility. Performance changes should include a correctness check and, where performance is the motivation, measurements against an appropriate baseline.

Automated contributions are welcome only when they have been reviewed for repository scope and can pass the same validation expected of human-authored changes.

## License

See [LICENSE](LICENSE) for the repository's license terms.
