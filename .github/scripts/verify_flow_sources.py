#!/usr/bin/env python3
"""Parse every public FLOW entry point and resolve its import graph."""

from __future__ import annotations

import sys
from pathlib import Path

from flow.module_resolver import resolve_modules


ROOT = Path(__file__).resolve().parents[2]


def verify(entrypoint: Path) -> None:
    relative_path = entrypoint.relative_to(ROOT)
    declarations = resolve_modules(str(relative_path))
    print(f"ok {relative_path}: {len(declarations)} declarations")


def main() -> int:
    entrypoints = [ROOT / "lib/scikit/scikit.flow"]
    entrypoints.extend(sorted((ROOT / "tests").glob("*.flow")))
    entrypoints.extend(sorted((ROOT / "examples").glob("*.flow")))
    entrypoints.extend(sorted((ROOT / "docs" / "wasm").glob("*.flow")))

    for entrypoint in entrypoints:
        try:
            verify(entrypoint)
        except Exception as error:
            print(f"error {entrypoint.relative_to(ROOT)}: {error}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
