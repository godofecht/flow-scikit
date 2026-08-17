#!/usr/bin/env python3
"""Normalize legacy sklearn timing literals in docs/benchmarks.js to milliseconds.

The historical BENCH object copied Python ``perf_counter`` durations in seconds
into ``sk_ms``, ``sk_fit`` and ``sk_pred`` fields.  Flow fields were already ms.
This transform is intentionally narrow and idempotent; it is used by Pages until
the benchmark site is generated directly from benchmark artifacts.
"""
from __future__ import annotations

import re
from pathlib import Path

PATH = Path("docs/benchmarks.js")
MARKER = "// SKLEARN_TIMINGS_NORMALIZED_TO_MS\n"
FIELD_RE = re.compile(r"\b(sk_(?:ms|fit|pred)):\s*(-?\d+(?:\.\d+)?)")


def normalize_text(text: str) -> tuple[str, int]:
    if MARKER.strip() in text:
        return text, 0

    # Only the dataset benchmark block uses these three field names. Android
    # uses mac_ms/and_ms and is therefore deliberately untouched.
    replacements = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal replacements
        field, raw = match.groups()
        value = float(raw) * 1000.0
        replacements += 1
        if value == 0:
            rendered = "0.000"
        elif value < 1:
            rendered = f"{value:.3f}"
        elif value < 100:
            rendered = f"{value:.3f}".rstrip("0").rstrip(".")
        else:
            rendered = f"{value:.3f}".rstrip("0").rstrip(".")
        return f"{field}: {rendered}"

    normalized = FIELD_RE.sub(repl, text)
    if replacements == 0:
        raise RuntimeError("no legacy sklearn timing fields found")
    return MARKER + normalized, replacements


def main() -> None:
    original = PATH.read_text()
    normalized, count = normalize_text(original)
    PATH.write_text(normalized)
    print(f"normalized {count} sklearn timing literals to milliseconds")


if __name__ == "__main__":
    main()
