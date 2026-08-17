#!/usr/bin/env python3
"""Fail if the published dataset benchmark contains legacy second-valued sklearn timings."""
from __future__ import annotations

import re
from pathlib import Path

PATH = Path("docs/benchmarks.js")
MARKER = "SKLEARN_TIMINGS_NORMALIZED_TO_MS"
ROW_RE = re.compile(r"\{\s*algo:\s*\"([^\"]+)\"(?P<body>[^\n]+?)\}")
FIELD_RE = re.compile(r"\b(sk_ms|fl_ms):\s*(-?\d+(?:\.\d+)?)")


def main() -> None:
    text = PATH.read_text()
    if MARKER not in text:
        raise SystemExit("published benchmark timings were not normalized to milliseconds")

    usable = 0
    flow_wins = 0
    rows = 0
    for match in ROW_RE.finditer(text):
        body = match.group("body")
        values = {name: float(value) for name, value in FIELD_RE.findall(body)}
        if "sk_ms" not in values or "fl_ms" not in values:
            continue
        rows += 1
        if values["sk_ms"] > 0:
            usable += 1
            if values["fl_ms"] < values["sk_ms"]:
                flow_wins += 1

    if rows != 19:
        raise SystemExit(f"expected 19 dataset benchmark rows, found {rows}")
    if (flow_wins, usable) != (10, 17):
        raise SystemExit(
            "legacy published headline no longer reproduces 10/17 after unit normalization: "
            f"got {flow_wins}/{usable}"
        )

    print(f"published timing audit: {rows} rows, legacy headline {flow_wins}/{usable}")


if __name__ == "__main__":
    main()
