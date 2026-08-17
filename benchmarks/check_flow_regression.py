#!/usr/bin/env python3
"""Fail only on material Flow self-regressions, never on sklearn competitiveness."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def indexed(payload: dict) -> dict:
    return {(r["algorithm"], int(r["rows"]), int(r["features"])): r for r in payload["rows"] if r.get("status") == "ok"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("current", type=Path)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("--relative-tolerance", type=float, default=0.20)
    parser.add_argument("--absolute-tolerance-ms", type=float, default=0.10)
    args = parser.parse_args()

    current = indexed(json.loads(args.current.read_text()))
    baseline = indexed(json.loads(args.baseline.read_text()))
    failures = []

    for key, base in baseline.items():
        row = current.get(key)
        if row is None:
            failures.append(f"missing current Flow row {key}")
            continue
        for field in ("fit_ms", "pred_ms"):
            old = float(base[field])
            new = float(row[field])
            allowed = old * (1.0 + args.relative_tolerance) + args.absolute_tolerance_ms
            if new > allowed:
                failures.append(f"{key} {field}: {new:.6f} ms > allowed {allowed:.6f} ms (baseline {old:.6f})")

    if failures:
        print("Flow performance regression(s):")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(f"Flow self-performance gate passed for {len(baseline)} baseline rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
