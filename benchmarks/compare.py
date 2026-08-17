#!/usr/bin/env python3
"""Compare flow-scikit vs scikit-learn benchmark results."""

EXPECTED_TIMING_UNIT = "ms"


def parse_results(path, require_unit=False):
    results = {}
    timing_unit = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("TIMING_UNIT|"):
                timing_unit = line.split("|", 1)[1]
            elif line.startswith("RESULT|"):
                parts = line.split("|")
                key = (parts[1], parts[2], parts[3])
                results[key] = (float(parts[4]), float(parts[5]), float(parts[6]))

    if timing_unit is not None and timing_unit != EXPECTED_TIMING_UNIT:
        raise ValueError(
            f"{path}: expected TIMING_UNIT|{EXPECTED_TIMING_UNIT}, got {timing_unit!r}"
        )
    if require_unit and timing_unit is None:
        raise ValueError(f"{path}: missing TIMING_UNIT|{EXPECTED_TIMING_UNIT}")
    return results


# New sklearn output must declare milliseconds explicitly. Flow's current
# benchmark already computes elapsed_ms() but predates the unit marker.
sklearn_results = parse_results("benchmarks/sklearn_results.txt", require_unit=True)
flow_results = parse_results("benchmarks/flow_results.txt")

print("=" * 100)
print(f"{'Algorithm':<25} {'Dataset':<12} {'Metric':<20} {'sklearn':<12} {'flow-scikit':<12} {'Diff':<12} {'sklearn_ms':<12} {'flow_ms':<12} {'Speedup':<10}")
print("=" * 100)

all_keys = sorted(set(sklearn_results) | set(flow_results))
for key in all_keys:
    algo, dataset, metric = key
    sk_score, sk_fit_ms, sk_pred_ms = sklearn_results.get(key, (None, None, None))
    fl_score, fl_fit_ms, fl_pred_ms = flow_results.get(key, (None, None, None))

    if sk_score is not None and fl_score is not None:
        diff = fl_score - sk_score
        sk_total_ms = sk_fit_ms + sk_pred_ms
        fl_total_ms = fl_fit_ms + fl_pred_ms
        speedup = sk_total_ms / fl_total_ms if fl_total_ms > 0 else 0
        print(f"{algo:<25} {dataset:<12} {metric:<20} {sk_score:<12.6f} {fl_score:<12.6f} {diff:<+12.6f} {sk_total_ms:<12.3f} {fl_total_ms:<12.3f} {speedup:<10.2f}x")
    elif sk_score is not None:
        print(f"{algo:<25} {dataset:<12} {metric:<20} {sk_score:<12.6f} {'N/A':<12} {'N/A':<12}")
    else:
        print(f"{algo:<25} {dataset:<12} {metric:<20} {'N/A':<12} {fl_score:<12.6f} {'N/A':<12}")

print("=" * 100)
print("\nNotes:")
print("- sklearn benchmark input must declare TIMING_UNIT|ms")
print("- Flow output is already milliseconds via elapsed_ms(); an explicit marker is still pending")
print("- Displayed times are milliseconds (fit + predict combined)")
print("- No implicit unit conversion is performed")
print("- Speedup > 1x means flow-scikit is faster")
print("- Score diff > 0 means flow-scikit scores higher")
print("- Datasets: iris (150 samples, 4 features), digits (1797 samples, 64 features), diabetes (442 samples, 10 features)")
print("- Both use the same embedded datasets and 80/20 train/test split with seed=42")
