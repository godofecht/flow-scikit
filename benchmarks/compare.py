#!/usr/bin/env python3
"""Compare flow-scikit vs scikit-learn benchmark results."""

# sklearn results (from bench_sklearn.py)
# bench_sklearn.py emits perf_counter durations in seconds.
sklearn_results = {}
with open("benchmarks/sklearn_results.txt") as f:
    for line in f:
        line = line.strip()
        if line.startswith("RESULT|"):
            parts = line.split("|")
            key = (parts[1], parts[2], parts[3])
            sklearn_results[key] = (float(parts[4]), float(parts[5]), float(parts[6]))

# Flow results (from bench_flow.flow output).
# bench_flow.flow emits fit/predict durations in milliseconds.
flow_results = {}
with open("benchmarks/flow_results.txt") as f:
    for line in f:
        line = line.strip()
        if line.startswith("RESULT|"):
            parts = line.split("|")
            key = (parts[1], parts[2], parts[3])
            flow_results[key] = (float(parts[4]), float(parts[5]), float(parts[6]))

print("=" * 100)
print(f"{'Algorithm':<25} {'Dataset':<12} {'Metric':<20} {'sklearn':<12} {'flow-scikit':<12} {'Diff':<12} {'sklearn_ms':<12} {'flow_ms':<12} {'Speedup':<10}")
print("=" * 100)

all_keys = sorted(set(list(sklearn_results.keys()) + list(flow_results.keys())))
for key in all_keys:
    algo, dataset, metric = key
    sk_score, sk_fit_s, sk_pred_s = sklearn_results.get(key, (None, None, None))
    fl_score, fl_fit_ms, fl_pred_ms = flow_results.get(key, (None, None, None))

    if sk_score is not None and fl_score is not None:
        diff = fl_score - sk_score
        sk_total_ms = (sk_fit_s + sk_pred_s) * 1000.0
        fl_total_ms = fl_fit_ms + fl_pred_ms
        speedup = sk_total_ms / fl_total_ms if fl_total_ms > 0 else 0
        print(f"{algo:<25} {dataset:<12} {metric:<20} {sk_score:<12.6f} {fl_score:<12.6f} {diff:<+12.6f} {sk_total_ms:<12.3f} {fl_total_ms:<12.3f} {speedup:<10.2f}x")
    elif sk_score is not None:
        print(f"{algo:<25} {dataset:<12} {metric:<20} {sk_score:<12.6f} {'N/A':<12} {'N/A':<12}")
    else:
        print(f"{algo:<25} {dataset:<12} {metric:<20} {'N/A':<12} {fl_score:<12.6f} {'N/A':<12}")

print("=" * 100)
print("\nNotes:")
print("- Displayed times are milliseconds (fit + predict combined)")
print("- Python perf_counter seconds are converted to milliseconds before comparison")
print("- Flow benchmark durations are already emitted in milliseconds")
print("- Speedup > 1x means flow-scikit is faster")
print("- Score diff > 0 means flow-scikit scores higher")
print("- Datasets: iris (150 samples, 4 features), digits (1797 samples, 64 features), diabetes (442 samples, 10 features)")
print("- Both use the same embedded datasets and 80/20 train/test split with seed=42")
