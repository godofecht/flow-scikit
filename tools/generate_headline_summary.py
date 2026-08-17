#!/usr/bin/env python3
"""Compatibility entry point for the canonical v2 headline publisher.

The benchmark headline has a single source of truth:
``benchmarks/headline_result_v2.json``. Older automation referenced this tool
name, so keep the entry point without reintroducing a second classifier or
another set of timing/parity rules.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = ROOT / "benchmarks" / "publish_headline_v2.py"


def main() -> int:
    return subprocess.call(
        [sys.executable, str(PUBLISHER), *sys.argv[1:]],
        cwd=ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
