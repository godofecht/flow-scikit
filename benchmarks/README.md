# Performance benchmarks: flow-scikit vs scikit-learn

This directory contains the canonical numerical-parity, timing and execution-architecture evidence used by the repository and Pages site.

## Canonical result

[`headline_result_v2.json`](headline_result_v2.json) is the current competitive source of truth.

The committed result contains **19 total rows, 19 parity-eligible comparisons, 10 Flow wins, 7 scikit-learn wins, 2 ties, 0 parity-unresolved rows and 0 measurement-unresolved rows**.

A competitive speed claim is only emitted when a row has resolved timing, a declared millisecond unit, comparable benchmark semantics and a passing estimator-specific parity contract.

## Timing contract

The benchmark contract is **milliseconds end-to-end**.

The Python v2 runner uses high-resolution `perf_counter_ns()`-backed adaptive measurement and emits explicit `TIMING_UNIT|ms`. Flow emits millisecond timings. [`run_headline.py`](run_headline.py) repeats complete runs and aggregates process-level measurements with medians and IQRs.

Comparison tools do not apply hidden seconds-to-milliseconds conversions. Missing or unexpected timing units are rejected.

Older published data that stored second-valued Python literals in fields labelled `ms` is retained only as historical audit material. It is not part of canonical v2.

## Fixture and parity contract

Canonical v2 consumes persisted train/test fixtures shared by Python and Flow. CI verifies that the JSON split indices and Flow binary split fixtures are byte-for-byte equivalent.

[`parity_contract.json`](parity_contract.json) defines the semantic contract for all 19 rows. Supervised rows compare their declared predictive metric under explicit tolerances. KMeans uses adjusted Rand index plus inertia rather than label-mapped accuracy. PCA additionally checks explained-variance ratios, singular values, reconstruction error and sign-aligned components.

Digits KMeans is classified as `approximately equivalent` under the tolerances declared in `parity_contract.json`, with no estimator-specific exception. [`audit_kmeans_semantics.py`](audit_kmeans_semantics.py) re-derives Flow's initial centre indices from a Python mirror of Flow's own MT19937 and greedy k-means++ and checks them against scikit-learn's initializer for all ten `n_init` restarts. It also records the differences that survive that alignment: the convergence statistic, the point at which inertia is reported, empty-cluster relocation and the `n_init` selection rule. Each was substituted in turn and none moves a canonical row.

## Learned-state diagnostics

A score tolerance says two implementations agree on the answer. It says nothing
about whether they agree on the model. Both runners therefore emit `DETAIL`
records alongside each `RESULT` line:

```
DETAIL|<algorithm>|<dataset>|<field>|<value or comma-separated values>
```

[`generate_disparity_report.py`](generate_disparity_report.py) pairs every field
both runners emitted for a canonical row and writes the deltas into that row's
`model_state_diagnostics`. Scalars give `<field>_abs_diff` and
`<field>_relative_diff`; equal-length vectors give `<field>_max_abs_diff`,
`<field>_max_relative_diff` and `<field>_first_divergent_index`, which is `-1`
when the vectors match elementwise and otherwise points at the first position
they disagree on; a length disagreement is recorded as
`<field>_length_abs_diff`. This runs off the frozen `DETAIL` records rather than
the parity comparison, so a row that misses its score tolerance still keeps its
state evidence. [`model_state_coverage.py`](model_state_coverage.py) audits which
canonical rows have any state evidence at all.

What each estimator emits:

| Row | Learned state |
| --- | --- |
| LogisticRegression, LinearSVC | sorted class labels, coefficient Frobenius norm, per-class row norms, intercepts |
| KernelSVC_RBF | gamma, C, one-vs-one pair labels and sizes, support-vector count per pair, bounded (at-C) support count per pair, summed absolute dual coefficients per pair, intercept per pair |
| DecisionTree | node and leaf counts, realized depth, root split feature/threshold/impurity, both depth-1 splits, node count per depth, split-feature histogram, sample-weighted mean leaf depth, full preorder split feature and threshold vectors |
| RandomForest | per-tree node/leaf counts, depths, root splits and impurities, per-tree bootstrap index checksum and unique-sample fraction, per-tree feature-subsample seed, mean vote margin, mean top-vote fraction, unanimous-vote fraction |
| GaussianNB | sorted class labels, class priors, per-class mean and variance row norms, Frobenius norms, variance min/max |
| KMeans | inertia, iteration count, sorted center norms, sorted training cluster sizes |
| PCA | explained-variance ratios, singular values, reconstruction MSE, first two components |
| Ridge, Lasso, LinearRegression | full coefficient vector, intercept, coefficient L2 norm and absolute sum, zero-coefficient count |
| KernelRidge_RBF | alpha, gamma, training size, dual-coefficient norm, absolute sum, min, max and mean |

Large structures are summarised rather than dumped, with one exception. A single
decision tree emits its full preorder split vectors, because node ids are
assigned parent-before-children and left-subtree-first on both sides, so index
`i` names the same position in both trees and `first_divergent_index` is then a
literal pointer at the first structurally different node. Forests emit per-tree
scalars and a bootstrap checksum instead of every bootstrap index; kernel SVMs
emit per-pair aggregates instead of every dual coefficient. Per-class and
per-pair vectors are ordered by class label so they line up with sklearn
regardless of the order Flow discovered the classes in.

Emission happens outside the timing windows and reads only fitted state, so it
does not move any canonical metric or timing.

### When a diagnostic differs from the committed snapshot

Both runners read the same fixture bytes. A `DETAIL` field that disagrees
between a local run and the committed evidence therefore means one side computed
a different number from the same input.

Issue #461 recorded one such disagreement.
`DETAIL|RandomForest|digits|unanimous_vote_fraction` is `0.197222222` in the
committed `sklearn_results_v2.txt` and was observed as `0.205556` locally, three
of 360 test rows, with the per-tree node counts matching exactly. Summation order
in the scaler was the suspected cause. It turns out to be the dtype the sklearn
side scales in.

`standard_scaler_fit` accumulates the mean and the variance in f64 and uses the
two-pass form, mean first and then squared deviations. On the digits fixture its
f32 `mean` and `std` are bit-identical in all 64 columns to the values obtained
from exact rational arithmetic over the integer pixel data. The tightest column's
exact std sits 4.9e-10 (relative) from an f32 rounding boundary, roughly four
orders of magnitude above the error an f64 sum over 1437 rows can carry, so no
reassociation of that sum can move the rounded f32 result. The margin is not
generous. An f32 two-pass over the same data moves the rounded std in 61 of 64
columns, and an f32 E[x^2] - E[x]^2 moves it in 23 of 64.

`bench_sklearn_v2.py` casts the digits matrix to float32 before fitting, so
`StandardScaler.transform` evaluates `(x - mean_) / scale_` in float32 with a
single rounding, and the forest then votes unanimously on 71 of 360 rows:
`0.197222222`, the committed value. Scaling the same split in float64 and
rounding to float32 afterwards changes 7412 of the 23040 test cells in their
last bits, three rows flip, and the fraction becomes `0.205555556`. Both are
reproducible on demand and neither depends on the platform. `mean_` and `scale_`
themselves are float64 in both cases and agree bit for bit.

So the committed snapshot is correct as recorded. A local run that disagrees
with it should be checked first for the dtype of the array it scaled.

## Running the canonical benchmark

```bash
FLOW_HEADLINE_COMMAND="flow run benchmarks/bench_flow_v2.flow" \
python benchmarks/run_headline.py --repeats 7
```

The runner writes the raw Python/Flow result files, environment metadata, row-level comparison output and generated headline summary.

## Execution architecture

The benchmark result is joined to a separate sklearn execution-architecture pipeline so a Flow win or loss can be interpreted against what sklearn actually executes.

The committed evidence currently contains:

- 491 estimator-operation inventory rows
- 32 runtime-attribution rows
- 491 optimization-roadmap rows
- 146 native/mixed hotspot dispositions
- 8 whole-estimator experiments
- substrate and speedup evidence for all 19 canonical rows

[`run_architecture_pipeline.py`](run_architecture_pipeline.py) regenerates the inventory, profiles, optimization ranking, native-hotspot audit and architecture/performance map against the pinned sklearn dependency set in [`requirements-architecture.txt`](requirements-architecture.txt).

CI detects estimator-surface drift: newly added or removed sklearn estimator operations must be reflected in the committed generated inventory rather than silently changing the analysis.

The main generated views are:

- [`SKLEARN_EXECUTION_INVENTORY.md`](SKLEARN_EXECUTION_INVENTORY.md)
- [`ARCHITECTURE_PERFORMANCE_MAP.md`](ARCHITECTURE_PERFORMANCE_MAP.md)
- [`OPTIMIZATION_ROADMAP.md`](OPTIMIZATION_ROADMAP.md)
- [`NATIVE_HOTSPOT_AUDIT.md`](NATIVE_HOTSPOT_AUDIT.md)

## Interpretation

A speedup is `sklearn_ms / flow_ms`. Values above `1x` mean Flow is faster; values below `1x` mean scikit-learn is faster.

The current architecture map shows a useful but non-causal pattern: Flow wins 75% of headline rows classified Python-bound, about 45% of mixed rows and 0% of external-native-bound rows. This is evidence for prioritization, not proof that execution substrate alone determines performance.

Mature BLAS/LAPACK, liblinear, libsvm and other native backends are treated as native competitors. The optimization roadmap deliberately prefers retaining those kernels unless benchmark and parity evidence justify replacement.

## Pages publication

[`publish_headline_v2.py`](publish_headline_v2.py) validates the committed canonical benchmark and architecture map, then copies the JSON artifacts into `docs/` for the static site. The public benchmark and architecture pages render those artifacts directly instead of embedding hand-maintained timing claims.
