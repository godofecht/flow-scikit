#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    rows = []
    unit = None
    for raw in args.input.read_text().splitlines():
        line = raw.strip()
        if line.startswith("TIMING_UNIT|"):
            unit = line.split("|", 1)[1]
        elif line.startswith("SCALED|"):
            p = line.split("|")
            rows.append({
                "implementation": "flow",
                "algorithm": p[1],
                "rows": int(p[2]),
                "features": int(p[3]),
                "fit_ms": float(p[4]),
                "pred_ms": float(p[5]),
                "timing_unit": "ms",
                "status": p[6],
            })
    if unit != "ms":
        raise SystemExit("scaled Flow output must declare TIMING_UNIT|ms")
    args.output.write_text(json.dumps({"schema_version": 1, "rows": rows}, indent=2) + "\n")
    print(f"wrote {len(rows)} Flow rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
