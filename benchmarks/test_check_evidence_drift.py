#!/usr/bin/env python3
"""check_evidence_drift.py must accept a refreshed tree and reject each kind of drift.

Each case copies benchmarks/ to a scratch root, refreshes the derived artifacts
there so the starting point is consistent, applies one mutation, and requires a
non-zero exit that names the mutated artifact.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(root: Path, script: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(root / "benchmarks" / script)], cwd=root, capture_output=True, text=True)


def load(path: Path):
    return json.loads(path.read_text())


def store(path: Path, doc) -> None:
    path.write_text(json.dumps(doc, indent=2) + "\n")


def mutate_result_speedup(root: Path) -> None:
    p = root / "benchmarks" / "headline_result_v2.json"
    doc = load(p)
    doc["rows"][0]["speedup"] = doc["rows"][0]["speedup"] * 1.5
    store(p, doc)


def mutate_map_speedup(root: Path) -> None:
    p = root / "benchmarks" / "architecture_performance_map.json"
    doc = load(p)
    doc["joined_headline_rows"][0]["flow_speedup"] *= 1.5
    store(p, doc)


def mutate_map_digest(root: Path) -> None:
    p = root / "benchmarks" / "architecture_performance_map.json"
    doc = load(p)
    doc["provenance"]["result_sha256"] = "0" * 64
    store(p, doc)


def mutate_map_environment(root: Path) -> None:
    p = root / "benchmarks" / "optimization_roadmap.json"
    doc = load(p)
    doc["provenance"]["environment_id"] = "ffffffffffffffff"
    store(p, doc)


def mutate_markdown(root: Path) -> None:
    p = root / "benchmarks" / "ARCHITECTURE_PERFORMANCE_MAP.md"
    p.write_text(p.read_text().replace("× |", "×x |", 1))


def mutate_whole_rows(root: Path) -> None:
    p = root / "benchmarks" / "whole_estimator_experiments.json"
    doc = load(p)
    row = next(r for r in doc["rows"] if r.get("flow_rows"))
    row["flow_rows"][0]["flow_fit_ms"] += 1.0
    store(p, doc)


def mutate_pages_copy(root: Path) -> None:
    docs = root / "docs"
    docs.mkdir(exist_ok=True)
    shutil.copyfile(root / "benchmarks" / "architecture_performance_map.json", docs / "architecture-performance-map.json")
    with (docs / "architecture-performance-map.json").open("a") as f:
        f.write(" ")


def mutate_disparity_environment(root: Path) -> None:
    p = root / "benchmarks" / "disparity_report.json"
    doc = load(p)
    doc["environment_id"] = "ffffffffffffffff"
    store(p, doc)


CASES = [
    ("result changed after the derived files were built", mutate_result_speedup, "built from result sha256"),
    ("map speedup edited", mutate_map_speedup, "flow_speedup"),
    ("map digest replaced", mutate_map_digest, "architecture_performance_map.json: built from result sha256"),
    ("roadmap environment replaced", mutate_map_environment, "optimization_roadmap.json: environment_id"),
    ("map markdown disagrees with map", mutate_markdown, "ARCHITECTURE_PERFORMANCE_MAP.md"),
    ("whole-estimator embedded rows stale", mutate_whole_rows, "stale headline rows"),
    ("Pages copy differs from source", mutate_pages_copy, "docs/architecture-performance-map.json differs"),
    ("disparity report from another environment", mutate_disparity_environment, "disparity_report.json: environment_id"),
]


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "base"
        (base / "docs").mkdir(parents=True)
        shutil.copytree(ROOT / "benchmarks", base / "benchmarks", ignore=shutil.ignore_patterns("__pycache__", "generated"))
        refreshed = run(base, "refresh_derived_evidence.py")
        if refreshed.returncode != 0:
            print("FAIL refresh on a scratch copy:", refreshed.stdout, refreshed.stderr)
            return 1
        if run(base, "check_evidence_drift.py").returncode != 0:
            print("FAIL a freshly refreshed tree must pass")
            return 1
        print("PASS refreshed tree is accepted")

        for name, mutate, expect in CASES:
            case = Path(tmp) / "case"
            if case.exists():
                shutil.rmtree(case)
            shutil.copytree(base, case)
            mutate(case)
            out = run(case, "check_evidence_drift.py")
            if out.returncode == 0 or expect not in out.stdout:
                failures += 1
                print(f"FAIL {name}: exit {out.returncode}, wanted {expect!r}\n{out.stdout}{out.stderr}")
            else:
                print(f"PASS {name} is rejected")

        # A refresh heals the mutated result, which proves the check is about
        # the join and that the single command repairs it.
        case = Path(tmp) / "heal"
        shutil.copytree(base, case)
        mutate_result_speedup(case)
        run(case, "refresh_derived_evidence.py")
        if run(case, "check_evidence_drift.py").returncode != 0:
            failures += 1
            print("FAIL refresh did not repair a changed result")
        else:
            print("PASS refresh repairs a changed result")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
