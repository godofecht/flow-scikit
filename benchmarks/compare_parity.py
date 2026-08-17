#!/usr/bin/env python3
"""Compare deterministic parity between scikit-learn and flow-scikit.

The generated JSON is the machine-readable parity gate consumed by benchmark
reporting. Timing is reported for context, but parity classification is based
only on output agreement.
"""
import json

VERIFIED_TOLERANCE = 0.01
APPROX_TOLERANCE = 0.05


def classify(max_diff, same_length):
    if not same_length:
        return "not parity verified"
    if max_diff <= VERIFIED_TOLERANCE:
        return "parity verified"
    if max_diff <= APPROX_TOLERANCE:
        return "approximately equivalent"
    return "not parity verified"


def main():
    with open("benchmarks/python_parity_results.json") as f:
        py_results = {r["algorithm"]: r for r in json.load(f)}
    with open("benchmarks/flow_parity_results.json") as f:
        fl_results = {r["algorithm"]: r for r in json.load(f)}

    all_algos = sorted(set(py_results) | set(fl_results))

    print(
        f"{'Algorithm':<35} {'Values':<11} {'Status':<26} "
        f"{'MaxDiff':<12} {'Python ms':<12} {'Flow ms':<12} {'Speedup':<10}"
    )
    print("=" * 125)

    parity_data = []
    counts = {
        "parity verified": 0,
        "approximately equivalent": 0,
        "not parity verified": 0,
        "missing": 0,
    }

    for algo in all_algos:
        py = py_results.get(algo)
        fl = fl_results.get(algo)

        if not py or not fl:
            status = "missing"
            counts[status] += 1
            parity_data.append({
                "algorithm": algo,
                "parity_status": status,
                "eligible_for_competitive_timing": False,
                "reason": "missing Python or Flow parity result",
            })
            print(f"{algo:<35} {'MISSING':<11} {status:<26}")
            continue

        py_out = py["output"]
        fl_out = fl["output"]
        same_length = len(py_out) == len(fl_out)
        n = min(len(py_out), len(fl_out))
        max_diff = max((abs(a - b) for a, b in zip(py_out, fl_out)), default=0.0)
        status = classify(max_diff, same_length)
        counts[status] += 1

        py_ms = py["total_ms"]
        fl_ms = fl["total_ms"]
        speedup = py_ms / fl_ms if fl_ms > 0 else 0.0
        values = str(n) if same_length else f"{len(py_out)}/{len(fl_out)}"
        speedup_str = f"{speedup:.2f}x" if fl_ms > 0 else "N/A"

        print(
            f"{algo:<35} {values:<11} {status:<26} {max_diff:<12.6f} "
            f"{py_ms:<12.4f} {fl_ms:<12.4f} {speedup_str:<10}"
        )

        reason = None
        if not same_length:
            reason = "output length mismatch"
        elif status == "approximately equivalent":
            reason = (
                f"max absolute difference exceeds verified tolerance "
                f"({VERIFIED_TOLERANCE}) but is within approximate tolerance "
                f"({APPROX_TOLERANCE})"
            )
        elif status == "not parity verified":
            reason = f"max absolute difference exceeds {APPROX_TOLERANCE}"

        parity_data.append({
            "algorithm": algo,
            "n_values": n,
            "python_n_values": len(py_out),
            "flow_n_values": len(fl_out),
            "parity_status": status,
            "eligible_for_competitive_timing": status == "parity verified",
            "max_diff": round(max_diff, 6),
            "verified_tolerance": VERIFIED_TOLERANCE,
            "approximate_tolerance": APPROX_TOLERANCE,
            "python_ms": py_ms,
            "flow_ms": fl_ms,
            "speedup": round(speedup, 4) if fl_ms > 0 else None,
            "reason": reason,
        })

    print("=" * 125)
    print(
        "\nParity summary: "
        f"{counts['parity verified']} verified, "
        f"{counts['approximately equivalent']} approximately equivalent, "
        f"{counts['not parity verified']} not verified, "
        f"{counts['missing']} missing"
    )

    with open("benchmarks/parity_comparison.json", "w") as f:
        json.dump(parity_data, f, indent=2)

    print("Results saved to benchmarks/parity_comparison.json")


if __name__ == "__main__":
    main()
