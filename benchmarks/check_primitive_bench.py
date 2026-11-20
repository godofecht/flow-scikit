#!/usr/bin/env python3
"""Gate the shared primitive microbenchmark.

Reads the output of benchmarks/bench_primitives.flow. For every feature count
the checksum of all variants must match to the bit, and the shared primitive
must not be slower than either inline form it replaced by more than --tolerance.
The default tolerance is 10% because a sub-microsecond pair loop moves by a few
percent from run to run on a shared machine.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path


def parse(text: str) -> dict[int, dict[str, tuple[float, str]]]:
    cases: dict[int, dict[str, tuple[float, str]]] = defaultdict(dict)
    for line in text.splitlines():
        if not line.startswith("PRIMITIVE|"):
            continue
        _, variant, n, ns, checksum = line.split("|")
        cases[int(n)][variant] = (float(ns), checksum)
    return cases


def same_checksum(values, rtol: float) -> bool:
    nums = [float(v) for v in values]
    return max(nums) - min(nums) <= rtol * max(abs(x) for x in nums)


def evaluate(cases, tolerance: float, checksum_rtol: float = 0.0) -> list[str]:
    problems = []
    for n, variants in sorted(cases.items()):
        if set(variants) != {"inline_for", "inline_matrix_at", "sqdist_f32"}:
            problems.append(f"n={n}: missing variants {sorted(variants)}")
            continue
        sums = {v: c for v, (_, c) in variants.items()}
        if not same_checksum(sums.values(), checksum_rtol):
            problems.append(f"n={n}: checksums differ {sums}")
        prim = variants["sqdist_f32"][0]
        for ref in ("inline_for", "inline_matrix_at"):
            ratio = prim / variants[ref][0]
            if ratio > 1.0 + tolerance:
                problems.append(f"n={n}: sqdist_f32 is {ratio:.2f}x the time of {ref}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("output", type=Path)
    ap.add_argument("--tolerance", type=float, default=0.10)
    ap.add_argument("--checksum-rtol", type=float, default=0.0,
                    help="allow checksums to differ by this relative amount. Use 1e-6 on a target with fused "
                         "multiply-add, where the vectorized loop rounds the last bit differently from the scalar one")
    args = ap.parse_args()
    cases = parse(args.output.read_text())
    if not cases:
        print("no PRIMITIVE lines found")
        return 1
    for n, v in sorted(cases.items()):
        f, m, p = (v[k][0] for k in ("inline_for", "inline_matrix_at", "sqdist_f32"))
        print(f"n={n:5d}  inline_for {f:9.3f} ns  inline_matrix_at {m:9.3f} ns  sqdist_f32 {p:9.3f} ns  ratio {p / f:.2f} / {p / m:.2f}")
    problems = evaluate(cases, args.tolerance, args.checksum_rtol)
    for p in problems:
        print("FAIL", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
