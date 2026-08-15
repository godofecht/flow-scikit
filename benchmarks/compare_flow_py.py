#!/usr/bin/env python3
"""Compare Flow and Python scikit-learn benchmark results."""
import sys

def parse_results(path):
    results = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("RESULT|"):
                continue
            parts = line.split("|")
            if len(parts) < 7:
                continue
            name, dataset, metric, score, fit_time, pred_time = parts[1:7]
            key = (name, dataset, metric)
            results[key] = (float(score), float(fit_time), float(pred_time))
    return results

flow = parse_results(sys.argv[1])
py = parse_results(sys.argv[2])

print(f"{'Algorithm':<25} {'Dataset':<10} {'Metric':<20} {'Flow':<12} {'Python':<12} {'Delta':<12} {'FlowFit':<10} {'PyFit':<10} {'FlowPred':<10} {'PyPred':<10}")
print("-" * 140)

all_keys = sorted(set(flow.keys()) | set(py.keys()))
for key in all_keys:
    name, dataset, metric = key
    f = flow.get(key, (None, None, None))
    p = py.get(key, (None, None, None))
    f_score = f"{f[0]:.6f}" if f[0] is not None else "N/A"
    p_score = f"{p[0]:.6f}" if p[0] is not None else "N/A"
    delta = f"{f[0] - p[0]:+.6f}" if f[0] is not None and p[0] is not None else "N/A"
    f_fit = f"{f[1]*1000:.1f}ms" if f[1] is not None else "N/A"
    p_fit = f"{p[1]*1000:.1f}ms" if p[1] is not None else "N/A"
    f_pred = f"{f[2]*1000:.2f}ms" if f[2] is not None else "N/A"
    p_pred = f"{p[2]*1000:.2f}ms" if p[2] is not None else "N/A"
    print(f"{name:<25} {dataset:<10} {metric:<20} {f_score:<12} {p_score:<12} {delta:<12} {f_fit:<10} {p_fit:<10} {f_pred:<10} {p_pred:<10}")
