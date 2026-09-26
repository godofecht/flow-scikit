#!/usr/bin/env python3
"""Keep the hand-written win/loss prose in step with the committed artifact.

README.md and benchmarks/README.md quote counts from headline_result_v2.json.
Those numbers change on every freeze, and prose does not. This has drifted
three times, most recently understating the project by two Flow wins.

Run with no arguments to check (non-zero exit on drift). Run with --fix to
rewrite the prose from the artifact.

This deliberately does NOT gate pull requests. The artifact refreezes on main
whenever the benchmark runs, several times a day, so a branch's prose goes
stale against main's newer artifact through no fault of the branch. Gating PRs
on it fails every open PR the moment a freeze lands, which is worse than the
drift it would catch. freeze-results runs --fix and then re-checks, so the
claims self-heal on main and a reworded sentence still surfaces (exit 2) where
someone can act on it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "benchmarks" / "headline_result_v2.json"
ARCH = ROOT / "benchmarks" / "architecture_performance_map.json"

# (path, regex with one group per count, builder for the replacement text)
TARGETS = [
    (
        ROOT / "benchmarks" / "README.md",
        re.compile(
            r"\*\*(\d+) total rows, (\d+) parity-eligible comparisons, (\d+) Flow wins, "
            r"(\d+) scikit-learn wins, (\d+) ties, (\d+) parity-unresolved rows and "
            r"(\d+) measurement-unresolved rows\*\*"
        ),
        lambda c: (
            f"**{c['total_rows']} total rows, {c['eligible_comparisons']} parity-eligible "
            f"comparisons, {c['flow_wins']} Flow wins, {c['sklearn_wins']} scikit-learn wins, "
            f"{c['ties']} ties, {c['parity_unresolved']} parity-unresolved rows and "
            f"{c['measurement_unresolved']} measurement-unresolved rows**"
        ),
    ),
    (
        ROOT / "README.md",
        re.compile(
            r"\*\*Flow wins (\d+) of (\d+) end-to-end fit \+ predict comparisons and "
            r"scikit-learn wins (\d+) of (\d+)\*\*"
        ),
        lambda c: (
            f"**Flow wins {c['flow_wins']} of {c['eligible_comparisons']} end-to-end "
            f"fit + predict comparisons and scikit-learn wins {c['sklearn_wins']} of "
            f"{c['eligible_comparisons']}**"
        ),
    ),
]

# The same drift, from the other artifact: both READMEs quote the mean Flow
# speedup per sklearn execution substrate, and those means move on every
# freeze. They had gone stale by 2x on one group before this was added.
SUBSTRATE_TARGETS = [
    (
        ROOT / "README.md",
        re.compile(
            r"at a mean of ([\d.]+)x on Python-bound rows, ([\d.]+)x on mixed rows "
            r"and ([\d.]+)x on external-native-bound rows"
        ),
        lambda m: (
            f"at a mean of {m['python-bound']:.2f}x on Python-bound rows, "
            f"{m['mixed']:.2f}x on mixed rows and "
            f"{m['external-native-bound']:.2f}x on external-native-bound rows"
        ),
    ),
    (
        ROOT / "benchmarks" / "README.md",
        re.compile(
            r"from a mean of ([\d.]+)x on Python-bound rows down to ([\d.]+)x on "
            r"external-native-bound ones"
        ),
        lambda m: (
            f"from a mean of {m['python-bound']:.2f}x on Python-bound rows down to "
            f"{m['external-native-bound']:.2f}x on external-native-bound ones"
        ),
    ),
]


def substrate_means() -> dict[str, float]:
    groups = json.loads(ARCH.read_text())["speedup_by_execution_substrate"]
    return {g["execution_class"]: float(g["mean_flow_speedup"]) for g in groups}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="rewrite prose from the artifact")
    args = ap.parse_args()

    counts = json.loads(RESULT.read_text())["counts"]
    means = substrate_means()
    drifted: list[str] = []

    for path, pattern, build in TARGETS + [
        (p, r, (lambda b: lambda _c: b(means))(build)) for p, r, build in SUBSTRATE_TARGETS
    ]:
        text = path.read_text()
        match = pattern.search(text)
        rel = path.relative_to(ROOT)
        if match is None:
            print(f"{rel}: could not find the published-claim sentence; update the pattern")
            return 2
        expected = build(counts)
        if match.group(0) == expected:
            continue
        if args.fix:
            path.write_text(text[: match.start()] + expected + text[match.end() :])
            print(f"{rel}: updated")
        else:
            drifted.append(f"{rel}\n    committed: {match.group(0)}\n    artifact:  {expected}")

    if drifted:
        print("Published prose disagrees with the committed artifacts:\n")
        for d in drifted:
            print("  " + d + "\n")
        print("Run: python benchmarks/validate_published_claims.py --fix")
        return 1

    print(f"published claims match the committed artifact: {counts['flow_wins']} Flow wins "
          f"/ {counts['eligible_comparisons']} eligible")
    return 0


if __name__ == "__main__":
    sys.exit(main())
