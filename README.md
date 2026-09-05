# flow-scikit

A compiled classical machine-learning library for [Flow](https://github.com/flooooooooooow/flow), inspired by scikit-learn's estimator ecosystem while exploring native deployment, whole-estimator compilation and a smaller runtime.

> **Status:** experimental, actively developed, and not affiliated with or endorsed by the scikit-learn project.

[Documentation & benchmarks](https://godofecht.github.io/flow-scikit/) · [Execution architecture](https://godofecht.github.io/flow-scikit/architecture.html) · [Flow language](https://github.com/flooooooooooow/flow) · [Examples](examples/) · [Tests](tests/)

## What this project is

flow-scikit asks a direct systems question: how much of the practical scikit-learn experience can be reproduced in a statically typed compiled language without carrying a Python runtime into deployment?

The goal is not a line-for-line port. The project implements familiar estimators, preprocessing, metrics, model selection and composition in Flow, then uses that implementation to test native deployment, explicit memory/layout choices and whole-estimator optimization against a mature reference ecosystem.

## Why traditional machine learning still matters

A useful practitioner snapshot appears in the r/datascience discussion ["Do people not use sci-kit learn / other traditional libraries anymore?"](https://www.reddit.com/r/datascience/comments/16lu9ni/do_people_not_use_scikit_learn_other_traditional/). It is anecdotal rather than a survey, but the recurring sentiment is clear: regression, trees, SVMs, clustering and other conventional methods remain routine production tools, especially for tabular and business workloads where larger neural models are unnecessary.

The other recurring point is that scikit-learn's value is larger than any individual estimator. Its common estimator interface makes preprocessing, fitting, evaluation, tuning and composition unusually coherent. flow-scikit is interested in preserving that practical model while testing a different runtime boundary.

The thesis is simple:

**Use the least complicated model that solves the problem, and make that model available in the least complicated runtime that satisfies the deployment requirements.**

That makes classical ML particularly interesting for native applications, embedded systems, mobile deployment, low-latency services, command-line tools and constrained environments.

## Evidence first

Performance claims in this repository are generated from committed benchmark artifacts rather than selected examples.

The current canonical v2 result is [`benchmarks/headline_result_v2.json`](benchmarks/headline_result_v2.json): **19 of 19 rows are parity-eligible and measurement-resolved**. In that committed run, **Flow wins 19 of 19 end-to-end fit + predict comparisons and scikit-learn wins 0 of 19**. There are no parity-unresolved or measurement-unresolved rows.

Canonical v2 uses explicit `TIMING_UNIT|ms` markers, persisted identical train/test fixtures, repeated timing aggregation and estimator-specific numerical parity gates. Unsupervised rows are not forced into classifier-style metrics: KMeans uses adjusted Rand index and inertia, while PCA additionally checks explained variance, singular values, reconstruction error and sign-aligned components.

Digits KMeans is classified as **approximately equivalent**, under the same declared tolerances as every other clustering row. Flow's seeded k-means++ consumes an MT19937 stream matching NumPy's `RandomState` and picks each centre as the best of `2 + int(log(k))` candidates, so both implementations start from the same initial centres and reach the same partition. The semantic audit records the differences that remain after that: the convergence statistic, the point at which inertia is reported, empty-cluster relocation and the `n_init` selection rule. None of them moves a canonical row, and all of them stay in the disparity artifact.

The separate deterministic algorithm suite currently records **16/16 output-parity checks passing**. The repository also records a historical **~1.4 MB native executable footprint** and **~65× cold-start advantage** in a separate deployment comparison. Those deployment figures are not mixed into the canonical estimator timing denominator.

See the [full canonical benchmark report](https://godofecht.github.io/flow-scikit/benchmarks.html).

## What sklearn actually executes

"Python versus compiled" is too crude a performance model for scikit-learn. Its public API is Python, but estimator hot paths may execute in Python orchestration, NumPy/SciPy, BLAS/LAPACK, sklearn-owned Cython/native code or external native libraries such as liblinear and libsvm.

flow-scikit now maintains a generated execution map rather than inferring opportunity from file extensions. The current committed evidence contains:

- **491 estimator-operation inventory rows** across the pinned sklearn public estimator surface
- **32 dynamic runtime-attribution rows**
- **491 generated optimization-roadmap rows**
- **146 compiled/mixed native-hotspot dispositions**
- **8 whole-estimator experiments**
- substrate and speedup joins for **all 19 canonical benchmark rows**

The current grouped headline evidence is descriptive rather than causal: Flow wins every row in all three substrate groups, at a mean of 20.99x on Python-bound rows, 6.84x on mixed rows and 3.96x on external-native-bound rows in the committed architecture map.

Two earlier readings of this table were wrong, and both were artifacts of how Flow was built rather than of the substrate. While the Flow side was compiled unoptimized, external-native-bound rows all lost, which read as sklearn-owned compiled code being out of reach. The grouping is a guide to where the Python boundary costs most. It is not a ceiling.

One row is not a like-for-like comparison, and the disparity report records it. Flow fits a forest's trees concurrently; scikit-learn's default is one worker, and the benchmark leaves it at its default. Both RandomForest rows therefore carry a declared `n_jobs` difference. Single-threaded, RandomForest on digits runs at 1.82x rather than 5.01x, so the row wins either way. Asking scikit-learn for all cores does not close the gap on this workload: at `n_jobs=-1` its own fit measured slower than at `n_jobs=1`, because joblib's pool costs more than ten small trees save.

Detailed artifacts:

- [`benchmarks/SKLEARN_EXECUTION_INVENTORY.md`](benchmarks/SKLEARN_EXECUTION_INVENTORY.md)
- [`benchmarks/ARCHITECTURE_PERFORMANCE_MAP.md`](benchmarks/ARCHITECTURE_PERFORMANCE_MAP.md)
- [`benchmarks/OPTIMIZATION_ROADMAP.md`](benchmarks/OPTIMIZATION_ROADMAP.md)
- [`benchmarks/NATIVE_HOTSPOT_AUDIT.md`](benchmarks/NATIVE_HOTSPOT_AUDIT.md)

## Why Flow?

Flow is a statically typed compiled language with a C backend, algebraic effects and autodiff. For this project that enables native binaries, explicit memory/layout decisions, cross-compilation and no mandatory Python interpreter.

flow-scikit is therefore both a library experiment and a systems experiment: it tests which parts of the scikit-learn programming model are fundamental and which parts are consequences of Python, NumPy, native-library boundaries and historical compatibility constraints.

## Scope

The implementation under `lib/scikit/` includes preprocessing, linear models, neighbors, SVMs, trees and ensembles, clustering, decomposition, model selection, metrics, feature selection, Gaussian processes, mixture models, neural networks, covariance, imputation, manifold learning, kernel approximation, multi-output learning and related utilities.

The source tree is the authoritative API inventory; coverage changes quickly while the project is under active development.

## Quick start

```bash
git clone https://github.com/flooooooooooow/flow.git
git clone https://github.com/godofecht/flow-scikit.git
cd flow-scikit

# BLAS linkage is required. Without FLOW_LDFLAGS the build fails at the
# link step with undefined cblas_* symbols.
export FLOW_HOST=python
export FLOW_OPT_LEVEL=0
export FLOW_LDFLAGS="-framework Accelerate lib/scikit/flow_time.c lib/scikit/flow_parallel.c"   # macOS
# export FLOW_LDFLAGS="-lm -lopenblas lib/scikit/flow_time.c lib/scikit/flow_parallel.c"        # Linux, matching CI

python tools/run_all.py
```

Benchmarks are compiled at `-O3` and link the timing shim:

```bash
export FLOW_OPT_LEVEL=3
export FLOW_LDFLAGS="-framework Accelerate lib/scikit/flow_time.c lib/scikit/flow_parallel.c"   # macOS
# export FLOW_LDFLAGS="-lm -lopenblas lib/scikit/flow_time.c lib/scikit/flow_parallel.c"        # Linux, matching CI

python benchmarks/run_headline.py --repeats 7
```

scikit-learn is measured as a released wheel, which ships optimized. Building
the Flow side at `-O0` measured the two at different optimization levels and
understated every row; the canonical contract now compiles both sides
optimized. `lib/scikit/flow_time.c` supplies the monotonic clock every timing
harness uses, and must be linked for the tests as well as the benchmarks.

`tools/run_all.py` is what the full CI suite exercises. A single file runs with
`flow run tests/test_new_features.flow` under the same environment.

## Testing and reproducibility

CI performs syntax/import validation and runs the Flow test/example suite. The benchmark pipeline additionally verifies JSON/binary split-fixture identity, validates the 19-row estimator contract, reruns repeated Flow/sklearn measurements, gates competitive timing on parity, detects sklearn estimator-surface drift and regenerates the architecture evidence and optimization roadmap.

Benchmark claims should be treated as reproducible measurements rather than constants: compiler revisions, optimization settings, BLAS implementations, hardware and estimator implementations can all move the numbers.

BLAS implementations differ in more than speed. Results verified bit-identical under one BLAS have been observed to differ in the last float32 digit under another, which matters wherever a threshold turns that difference into a different answer. Parity work should be verified on the platform CI runs on.

See [`AGENTS.md`](AGENTS.md) for the full build, measurement and concurrency notes, including why timings taken on a loaded machine are not usable and why BLAS substitutions need a small-input work threshold.

## Relationship to scikit-learn

flow-scikit is an independent project. It takes substantial inspiration from scikit-learn's estimator vocabulary and public API discussions, but it is not an official port, fork or subproject.

Where the two libraries differ deliberately in API design, the reasoning is recorded in the [design rationale](https://godofecht.github.io/flow-scikit/design-rationale.html) ([source](docs/design-rationale.md)), along with the gaps that remain open.

During development, an automated coding agent that was intended to submit work to the upstream Flow repository mis-targeted submissions to a scikit-related upstream repository. Those submissions were unintended automation output. The incident led to stronger repository allow-lists, publication checks, bounded automation and explicit human-visible CI/review gates in this project.

The technical comparisons here are intended to stand or fall on reproducible code and measurements rather than project politics.

## Contributing

Contributions are welcome, particularly when they improve correctness, parity, benchmarks, tests, documentation or reproducibility. Performance changes should include a correctness check and measurements against an appropriate baseline.

Automated contributions are welcome only when they have been reviewed for repository scope and can pass the same validation expected of human-authored changes.

## License

See [LICENSE](LICENSE) for the repository's license terms.
