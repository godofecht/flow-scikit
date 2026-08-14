#!/usr/bin/env python3
"""Compare per-algorithm parity between scikit-learn (Python) and scikit-learn (Flow).

Checks if outputs match within a tolerance and reports timing.
Outputs JSON for the benchmarks page.
"""
import json
import sys

TOLERANCE = 0.01  # 0.01 absolute tolerance for float comparison

def main():
    with open("benchmarks/python_parity_results.json") as f:
        py_results = {r["algorithm"]: r for r in json.load(f)}
    with open("benchmarks/flow_parity_results.json") as f:
        fl_results = {r["algorithm"]: r for r in json.load(f)}

    all_algos = sorted(set(list(py_results.keys()) + list(fl_results.keys())))

    print(f"{'Algorithm':<35} {'Values':<8} {'Match':<8} {'MaxDiff':<12} {'Python ms':<12} {'Flow ms':<12} {'Speedup':<10}")
    print("=" * 100)

    parity_data = []
    exact_matches = 0
    total = 0

    for algo in all_algos:
        py = py_results.get(algo)
        fl = fl_results.get(algo)

        if not py or not fl:
            print(f"{algo:<35} {'MISSING':<8}")
            continue

        py_out = py["output"]
        fl_out = fl["output"]
        n = min(len(py_out), len(fl_out))

        if len(py_out) != len(fl_out):
            print(f"{algo:<35} {len(py_out)}/{len(fl_out)} {'LEN MISMATCH':<8}")
            continue

        max_diff = 0.0
        all_match = True
        for a, b in zip(py_out, fl_out):
            diff = abs(a - b)
            if diff > max_diff:
                max_diff = diff
            if diff > TOLERANCE:
                all_match = False

        py_ms = py["total_ms"]
        fl_ms = fl["total_ms"]
        speedup = py_ms / fl_ms if fl_ms > 0 else 0

        match_str = "EXACT" if all_match else "DIFF"
        if all_match:
            exact_matches += 1
        total += 1

        speedup_str = f"{speedup:.1f}x" if speedup > 1 else f"{speedup:.2f}x"
        print(f"{algo:<35} {n:<8} {match_str:<8} {max_diff:<12.6f} {py_ms:<12.4f} {fl_ms:<12.4f} {speedup_str:<10}")

        parity_data.append({
            "algorithm": algo,
            "n_values": n,
            "match": all_match,
            "max_diff": round(max_diff, 6),
            "python_ms": py_ms,
            "flow_ms": fl_ms,
            "speedup": round(speedup, 2)
        })

    print("=" * 100)
    print(f"\n{exact_matches}/{total} algorithms produce identical output (tolerance={TOLERANCE})")

    with open("benchmarks/parity_comparison.json", "w") as f:
        json.dump(parity_data, f, indent=2)

    print(f"Results saved to benchmarks/parity_comparison.json")

if __name__ == "__main__":
    main()
