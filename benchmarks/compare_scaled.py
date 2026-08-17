#!/usr/bin/env python3
"""Join Flow and sklearn scaled benchmark artifacts into a competitiveness report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_flow(path: Path) -> dict:
    rows = {}
    unit = None
    for line in path.read_text().splitlines():
        if line.startswith("TIMING_UNIT|"):
            unit = line.split("|", 1)[1]
        elif line.startswith("SCALED|"):
            p = line.split("|")
            key = (p[1], int(p[2]), int(p[3]))
            rows[key] = {
                "implementation": "flow",
                "algorithm": p[1],
                "rows": int(p[2]),
                "features": int(p[3]),
                "fit_ms": float(p[4]),
                "pred_ms": float(p[5]),
                "timing_unit": "ms",
                "status": p[6],
            }
    if unit != "ms":
        raise SystemExit("Flow scaled benchmark must declare TIMING_UNIT|ms")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("flow", type=Path)
    parser.add_argument("sklearn", type=Path)
    parser.add_argument("--output", type=Path, default=Path("benchmarks/scaled_comparison.json"))
    args = parser.parse_args()

    flow = parse_flow(args.flow)
    sklearn_payload = json.loads(args.sklearn.read_text())
    sklearn_rows = {(r["algorithm"], int(r["rows"]), int(r["features"])): r for r in sklearn_payload["rows"]}

    report = []
    for key in sorted(set(flow) | set(sklearn_rows)):
        f = flow.get(key)
        s = sklearn_rows.get(key)
        status = "ok" if f and s and f.get("status") == "ok" and s.get("status") == "ok" else "unavailable"
        row = {"algorithm": key[0], "rows": key[1], "features": key[2], "status": status}
        if status == "ok":
            flow_total = float(f["fit_ms"]) + float(f["pred_ms"])
            sklearn_total = float(s["fit_ms"]) + float(s["pred_ms"])
            row.update({
                "flow_ms": flow_total,
                "sklearn_ms": sklearn_total,
                "speedup": sklearn_total / flow_total if flow_total > 0 else None,
                "timing_unit": "ms",
            })
        else:
            row["reason"] = "one or both implementations unavailable for this scale"
        report.append(row)

    args.output.write_text(json.dumps({"schema_version": 1, "rows": report}, indent=2) + "\n")
    print(f"wrote {len(report)} scaled comparison rows; report is informational only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
