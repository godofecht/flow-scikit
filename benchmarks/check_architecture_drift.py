#!/usr/bin/env python3
"""Fail when the pinned sklearn public estimator-operation surface drifts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def keys(path: Path):
    doc = json.loads(path.read_text())
    version = doc.get("sklearn_version")
    rows = doc.get("rows", [])
    return version, {(r["module"], r["estimator"], r["operation"]) for r in rows}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("baseline", type=Path)
    p.add_argument("current", type=Path)
    args = p.parse_args()
    old_version, old = keys(args.baseline)
    new_version, new = keys(args.current)
    if old_version != new_version:
        raise SystemExit(f"sklearn version drift: {old_version!r} -> {new_version!r}")
    added = sorted(new - old)
    removed = sorted(old - new)
    if added or removed:
        print("Estimator-operation inventory drift detected")
        if added:
            print("Added:")
            for row in added: print(" +", ".".join(row))
        if removed:
            print("Removed:")
            for row in removed: print(" -", ".".join(row))
        return 1
    print(f"architecture inventory surface stable: {len(new)} operations on sklearn {new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
