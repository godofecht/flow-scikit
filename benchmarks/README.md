# Performance benchmarks: flow-scikit vs scikit-learn

This directory contains the canonical numerical-parity, timing and execution-architecture evidence used by the repository and Pages site.

## Canonical result

[`headline_result_v2.json`](headline_result_v2.json) is the current competitive source of truth.

The committed result contains **19 total rows, 19 parity-eligible comparisons, 8 Flow wins, 11 scikit-learn wins, 0 ties, 0 parity-unresolved rows and 0 measurement-unresolved rows**.

A competitive speed claim is only emitted when a row has resolved timing, a declared millisecond unit, comparable benchmark semantics and a passing estimator-specific parity contract.

## Timing contract

The benchmark contract is **milliseconds end-to-end**.

The Python v2 runner uses high-resolution `perf_counter_ns()`-backed adaptive measurement and emits explicit `TIMING_UNIT|ms`. Flow emits millisecond timings. [`run_headline.py`](run_headline.py) repeats complete runs and aggregates process-level measurements with medians and IQRs.

Comparison tools do not apply hidden seconds-to-milliseconds conversions. Missing or unexpected timing units are rejected.

Older published data that stored second-valued Python literals in fields labelled `ms` is retained only as historical audit material. It is not part of canonical v2.

## Fixture and parity contract

Canonical v2 consumes persisted train/test fixtures shared by Python and Flow. CI verifies that the JSON split indices and Flow binary split fixtures are byte-for-byte equivalent.

[`parity_contract.json`](parity_contract.json) defines the semantic contract for all 19 rows. Supervised rows compare their declared predictive metric under explicit tolerances. KMeans uses adjusted Rand index plus inertia rather than label-mapped accuracy. PCA additionally checks explained-variance ratios, singular values, reconstruction error and sign-aligned components.

Digits KMeans is classified as `approximately equivalent`. [`audit_kmeans_semantics.py`](audit_kmeans_semantics.py) records that the first trajectory divergence occurs during initialization; the final objective remains closely matched. [`finalize_kmeans_parity.py`](finalize_kmeans_parity.py) applies the explicit clustering-equivalence gate before the row becomes headline-eligible.

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
