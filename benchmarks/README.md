# Performance Benchmarks: flow-scikit vs scikit-learn

Comparison of numerical parity and runtime between flow-scikit and scikit-learn.

## Timing contract

The benchmark contract is **milliseconds end-to-end**.

`benchmarks/bench_sklearn.py` converts `time.perf_counter()` deltas to milliseconds before emitting results and prints `TIMING_UNIT|ms`. `benchmarks/bench_flow.flow` converts `clock()` ticks to milliseconds with `elapsed_ms()`. Comparison tools do not apply any implicit seconds-to-milliseconds conversion.

A benchmark result file with an unexpected or missing timing unit is rejected rather than guessed.

The published website still contains a historical 19-row dataset captured when sklearn durations were copied as second-valued literals into fields named `sk_ms`. `benchmarks/normalize_published_timings.py` exists only to normalize that legacy publication artifact during Pages deployment. It is not part of the current benchmark measurement contract.

`docs/benchmark-corrections.js` is idempotent: it converts the legacy checkout data only when it detects the old second-valued 19-row dataset, and leaves the already-normalized Pages build untouched. This prevents the former 1000x double-conversion failure mode.

## Current methodology

The headline dataset benchmark uses Iris, Digits, and Diabetes with the deterministic xorshift32 Fisher-Yates split at seed 42 and an 80/20 train/test partition. Preprocessing occurs before estimator timing. Fit and prediction are reported separately and in milliseconds.

The deterministic per-algorithm parity benchmark is a separate correctness suite. `benchmarks/run_parity.py` can repeat both implementations, verify deterministic outputs, aggregate timings with medians, and write canonical parity artifacts. `benchmarks/compare_parity.py` classifies numerical results as `parity verified`, `approximately equivalent`, `not parity verified`, or `missing` rather than treating all timing rows as automatically comparable.

The historical published timing table should not be treated as the final competitive dataset. Two sklearn rows were stored as `0.000` at the old capture precision, so the historical `10/17` denominator reflects measurement resolution rather than a 17-row benchmark. The benchmark matrix actually contains 19 rows. Issues #168, #175, and #176 track replacement of that historical artifact with repeated, sub-millisecond-safe, parity-gated measurements and a mechanically generated headline.

## Running the benchmarks

```bash
# sklearn dataset benchmark — emits milliseconds
python3 benchmarks/bench_sklearn.py

# Flow dataset benchmark — emits milliseconds
FLOW_HOST=python flow run benchmarks/bench_flow.flow

# unit-safe dataset comparison
python3 benchmarks/compare.py

# repeated deterministic parity benchmark
python3 benchmarks/run_parity.py --repeats 7
```

## Interpretation

A speedup is always `sklearn_ms / flow_ms`. Values above `1x` mean Flow is faster; values below `1x` mean sklearn is faster. A competitive speed claim should only be made for rows whose timing measurement is resolved and whose estimator semantics satisfy the parity contract.
