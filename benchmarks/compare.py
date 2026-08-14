#!/usr/bin/env python3
"""Compare flow-scikit vs scikit-learn benchmark results."""
import sys

# sklearn results (from bench_sklearn.py)
sklearn_results = {}
with open("benchmarks/sklearn_results.txt") as f:
    for line in f:
        line = line.strip()
        if line.startswith("RESULT|"):
            parts = line.split("|")
            key = (parts[1], parts[2], parts[3])
            sklearn_results[key] = (float(parts[4]), float(parts[5]), float(parts[6]))

# flow results (from bench_flow.flow output)
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
    sk_score, sk_fit, sk_pred = sklearn_results.get(key, (None, None, None))
    fl_score, fl_fit, fl_pred = flow_results.get(key, (None, None, None))

    if sk_score is not None and fl_score is not None:
        diff = fl_score - sk_score
        sk_total = sk_fit + sk_pred
        fl_total = fl_fit + fl_pred
        speedup = sk_total / fl_total if fl_total > 0 else 0
        print(f"{algo:<25} {dataset:<12} {metric:<20} {sk_score:<12.6f} {fl_score:<12.6f} {diff:<+12.6f} {sk_total*1000:<12.3f} {fl_total:<12.3f} {speedup:<10.2f}x")
    elif sk_score is not None:
        print(f"{algo:<25} {dataset:<12} {metric:<20} {sk_score:<12.6f} {'N/A':<12} {'N/A':<12}")
    else:
        print(f"{algo:<25} {dataset:<12} {metric:<20} {'N/A':<12} {fl_score:<12.6f} {'N/A':<12}")

print("=" * 100)
print("\nNotes:")
print("- Times are in milliseconds (fit + predict combined)")
print("- Speedup > 1x means flow-scikit is faster")
print("- Score diff > 0 means flow-scikit scores higher")
print("- Datasets: iris (150 samples, 4 features), digits (1797 samples, 64 features), diabetes (442 samples, 10 features)")
print("- Both use the same embedded datasets and 80/20 train/test split with seed=42")
