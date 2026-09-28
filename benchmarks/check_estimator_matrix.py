#!/usr/bin/env python3
"""Gate the wide estimator matrix: every ranked row has to favour Flow.

The matrix was measured by hand for a long time, which is why a published
number sat at 145 of 166 while the working tree was at 155. A gate in CI is
what keeps the claim and the code in step: a row that turns slower than
scikit-learn fails the run, and a row that stops reporting fails it too,
because a chunk that dies mid-run is indistinguishable from a chunk with
nothing to say.

Rows the registry marks simplified carry no ratio and are not ranked. Rows
under the clock's floor carry no ratio either. Both are reported and neither
fails the run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("comparison", nargs="?", type=Path,
                    default=ROOT / "benchmarks" / "estimator_comparison.json")
    ap.add_argument("--min-compared", type=int, default=160,
                    help="fail if fewer rows than this produced a ratio")
    ap.add_argument("--tolerance", type=float, default=1.0,
                    help="the ratio a row has to reach, sklearn_ms / flow_ms")
    args = ap.parse_args()

    payload = json.loads(args.comparison.read_text())
    rows = payload["rows"]
    ranked = [r for r in rows if r.get("status") == "ok" and r.get("speedup") is not None]
    losers = sorted((r for r in ranked if r["speedup"] < args.tolerance),
                    key=lambda r: r["speedup"])
    missing = [r for r in rows if r.get("status") in ("flow_missing", "sklearn_missing")]

    print(f"ranked {len(ranked)} rows, {len(ranked) - len(losers)} at or above "
          f"{args.tolerance:.2f}x")
    for r in losers:
        print(f"  SLOWER {r['speedup']:6.3f}x  {r['flow_estimator']:32s} "
              f"flow={r['flow_ms']:9.3f} sklearn={r['sklearn_ms']:9.3f}")
    for r in missing:
        print(f"  MISSING {r['flow_estimator']:32s} {r['status']}: {r.get('reason', '')}")

    failed = False
    if losers:
        print(f"{len(losers)} rows are slower than scikit-learn")
        failed = True
    if missing:
        print(f"{len(missing)} rows reported no timing")
        failed = True
    if len(ranked) < args.min_compared:
        print(f"only {len(ranked)} rows produced a ratio, expected at least {args.min_compared}")
        failed = True
    if failed:
        return 1
    print("every ranked row favours Flow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
