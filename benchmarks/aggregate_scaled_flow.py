#!/usr/bin/env python3
"""Aggregate repeated scaled Flow benchmark text into one median row per case."""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from statistics import median


def aggregate(text: str) -> str:
    unit = None
    coverage: list[str] = []
    samples: dict[tuple[str, int, int, str], list[tuple[float, float]]] = defaultdict(list)
    order: list[tuple[str, int, int, str]] = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("TIMING_UNIT|"):
            declared = line.split("|", 1)[1]
            if unit is None:
                unit = declared
            elif declared != unit:
                raise ValueError(f"mixed timing units: {unit!r} and {declared!r}")
            continue
        if line.startswith("SCALED_COVERAGE|"):
            if line not in coverage:
                coverage.append(line)
            continue
        if not line.startswith("SCALED|"):
            continue

        parts = line.split("|")
        if len(parts) != 7:
            raise ValueError(f"invalid scaled row: {line}")
        key = (parts[1], int(parts[2]), int(parts[3]), parts[6])
        if key not in samples:
            order.append(key)
        samples[key].append((float(parts[4]), float(parts[5])))

    if unit != "ms":
        raise ValueError("scaled Flow output must declare TIMING_UNIT|ms")
    if not samples:
        raise ValueError("no SCALED rows found")

    lines = ["TIMING_UNIT|ms", *coverage]
    for algorithm, rows, features, status in order:
        values = samples[(algorithm, rows, features, status)]
        fit_ms = median(v[0] for v in values)
        pred_ms = median(v[1] for v in values)
        lines.append(
            f"SCALED|{algorithm}|{rows}|{features}|{fit_ms:.9f}|{pred_ms:.9f}|{status}"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(aggregate(args.input.read_text()))
    print(f"wrote median scaled Flow timings to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
