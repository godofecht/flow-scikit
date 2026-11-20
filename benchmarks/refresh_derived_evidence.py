#!/usr/bin/env python3
"""Regenerate every artifact derived from headline_result_v2.json in one step.

Reads the committed headline result and rebuilds the optimization roadmap, the
native hotspot audit, the architecture map, and the headline rows embedded in
whole_estimator_experiments.json. All outputs are staged in a temporary
directory first and moved into place together, then check_evidence_drift.py
runs over the result. Needs only the standard library, so it can run on the
freeze job after the canonical result is promoted.

whole_estimator_experiments.json also holds timed kernel experiments. Those
are kept as measured; only its provenance and its copy of the headline rows are
refreshed here.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from evidence_provenance import provenance

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"


def run(script: str, *args: object) -> None:
    subprocess.run([sys.executable, str(BENCH / script), *map(str, args)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def main() -> int:
    headline_path = BENCH / "headline_result_v2.json"
    headline = json.loads(headline_path.read_text())
    with tempfile.TemporaryDirectory(dir=BENCH, prefix=".refresh-") as tmp:
        tmp = Path(tmp)
        roadmap, roadmap_md = tmp / "optimization_roadmap.json", tmp / "OPTIMIZATION_ROADMAP.md"
        hotspots, hotspots_md = tmp / "native_hotspot_audit.json", tmp / "NATIVE_HOTSPOT_AUDIT.md"
        whole = tmp / "whole_estimator_experiments.json"
        amap, amap_md = tmp / "architecture_performance_map.json", tmp / "ARCHITECTURE_PERFORMANCE_MAP.md"

        run("rank_optimization_opportunities.py", "--headline", headline_path, "--json", roadmap, "--markdown", roadmap_md)
        run("audit_native_hotspots.py", "--roadmap", roadmap, "--json", hotspots, "--markdown", hotspots_md)

        doc = json.loads((BENCH / "whole_estimator_experiments.json").read_text())
        doc["provenance"] = provenance(headline_path)
        for row in doc["rows"]:
            if "flow_rows" in row:
                row["flow_rows"] = [r for r in headline["rows"] if r.get("algorithm") == row["representative"]]
        whole.write_text(json.dumps(doc, indent=2) + "\n")

        run("architecture_performance_report.py", "--headline", headline_path, "--roadmap", roadmap,
            "--hotspots", hotspots, "--whole", whole, "--json", amap, "--markdown", amap_md)

        for src in (roadmap, roadmap_md, hotspots, hotspots_md, whole, amap, amap_md):
            os.replace(src, BENCH / src.name)
    return subprocess.run([sys.executable, str(BENCH / "check_evidence_drift.py")], cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
