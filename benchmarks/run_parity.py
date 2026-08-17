#!/usr/bin/env python3
"""Run the canonical Flow/scikit-learn parity benchmark repeatedly.

Both benchmark programs report fit/predict timings in milliseconds. This
runner repeats each side, verifies deterministic outputs, replaces per-run
timings with medians, writes the canonical result JSON files, and runs the
parity comparison.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
PY_BENCH = BENCH / "bench_per_algorithm.py"
FLOW_BENCH = BENCH / "bench_per_algorithm.flow"
PY_RESULTS = BENCH / "python_parity_results.json"
FLOW_RESULTS = BENCH / "flow_parity_results.json"
COMPARE = BENCH / "compare_parity.py"


def run_json(command: list[str]) -> list[dict]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=None,
    )
    return json.loads(proc.stdout)


def index_results(results: list[dict]) -> dict[str, dict]:
    return {row["algorithm"]: row for row in results}


def aggregate(runs: list[list[dict]]) -> list[dict]:
    indexed = [index_results(run) for run in runs]
    names = list(indexed[0])

    for run in indexed[1:]:
        if set(run) != set(names):
            raise RuntimeError("algorithm set changed between benchmark repetitions")

    aggregated: list[dict] = []
    for name in names:
        reference = indexed[0][name]
        reference_output = reference["output"]
        for run in indexed[1:]:
            if run[name]["output"] != reference_output:
                raise RuntimeError(f"non-deterministic output for {name}")

        fit_values = [float(run[name]["fit_ms"]) for run in indexed]
        pred_values = [float(run[name]["pred_ms"]) for run in indexed]
        fit_ms = statistics.median(fit_values)
        pred_ms = statistics.median(pred_values)

        aggregated.append({
            "algorithm": name,
            "output": reference_output,
            "fit_ms": round(fit_ms, 6),
            "pred_ms": round(pred_ms, 6),
            "total_ms": round(fit_ms + pred_ms, 6),
            "timing_unit": "ms",
            "repeats": len(runs),
        })

    return aggregated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument(
        "--flow-command",
        default=os.environ.get("FLOW_BENCH_COMMAND", f"flow run {FLOW_BENCH}"),
        help="command used to run the Flow parity benchmark",
    )
    args = parser.parse_args()

    if args.repeats < 1:
        parser.error("--repeats must be >= 1")

    python_runs = [run_json([sys.executable, str(PY_BENCH)]) for _ in range(args.repeats)]
    flow_command = shlex.split(args.flow_command)
    flow_runs = [run_json(flow_command) for _ in range(args.repeats)]

    PY_RESULTS.write_text(json.dumps(aggregate(python_runs), indent=2) + "\n")
    FLOW_RESULTS.write_text(json.dumps(aggregate(flow_runs), indent=2) + "\n")

    subprocess.run([sys.executable, str(COMPARE)], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
