#!/usr/bin/env python3
"""Run the complete sklearn execution-architecture evidence pipeline."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"


def run(name, *args):
    cmd = [sys.executable, str(BENCH / name), *map(str, args)]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--profile-sizes", default="100,1000")
    args = p.parse_args()

    run("execution_inventory.py")
    run("profile_execution.py", "--sizes", args.profile_sizes)
    run("rank_optimization_opportunities.py")
    run("whole_estimator_experiments.py")
    run("audit_native_hotspots.py")
    run("architecture_performance_report.py")

    required = [
        "sklearn_execution_inventory.json",
        "sklearn_execution_inventory.csv",
        "SKLEARN_EXECUTION_INVENTORY.md",
        "sklearn_runtime_attribution.json",
        "optimization_roadmap.json",
        "OPTIMIZATION_ROADMAP.md",
        "whole_estimator_experiments.json",
        "native_hotspot_audit.json",
        "NATIVE_HOTSPOT_AUDIT.md",
        "architecture_performance_map.json",
        "ARCHITECTURE_PERFORMANCE_MAP.md",
    ]
    missing = [name for name in required if not (BENCH / name).exists()]
    if missing:
        raise SystemExit(f"architecture pipeline missing outputs: {missing}")
    print("architecture pipeline: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
