#!/usr/bin/env python3
"""Collect the scaled benchmark matrix across several CI runs into one artifact.

A single run of the scaled matrix is not enough to say a row is won. The rows
at 100 and 1000 samples finish in well under a millisecond, and a shared CI
runner moves them by more than the Flow-versus-sklearn difference: on five
consecutive runs of the same code, Lasso at 1000 rows and 32 features was
measured at 3.83x and at 0.92x.

So the published claim is the spread across runs rather than one run's number.
Feed this the scaled_comparison.json from each run:

    gh run download <id> -n scaled-benchmark-<id> -D /tmp/<id>
    python benchmarks/summarize_scaled_ci.py <id>=/tmp/<id>/scaled_comparison.json

Runs merge by id, so re-running with an id already present replaces it and
adding a new one extends the history.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "benchmarks" / "scaled_ci_history.json"


def row_key(row: dict) -> str:
    return f"{row['algorithm']}/{row['rows']}x{row['features']}"


def load_run(path: Path) -> dict[str, float]:
    payload = json.loads(path.read_text())
    return {
        row_key(r): float(r["speedup"])
        for r in payload["rows"]
        if r.get("status") == "ok" and "speedup" in r
    }


def summarize(runs: dict[str, dict[str, float]]) -> dict:
    keys = sorted({k for run in runs.values() for k in run})
    order = sorted(runs)
    rows = []
    for key in keys:
        observations = [runs[r][key] for r in order if key in runs[r]]
        if not observations:
            continue
        algorithm, shape = key.split("/", 1)
        samples, features = shape.split("x", 1)
        rows.append(
            {
                "algorithm": algorithm,
                "rows": int(samples),
                "features": int(features),
                "observations": [round(v, 4) for v in observations],
                "runs_observed": len(observations),
                "runs_won": sum(1 for v in observations if v >= 1.0),
                "min_speedup": round(min(observations), 4),
                "median_speedup": round(statistics.median(observations), 4),
                "max_speedup": round(max(observations), 4),
            }
        )
    per_run = [
        {
            "run_id": r,
            "rows_compared": len(runs[r]),
            "flow_wins": sum(1 for v in runs[r].values() if v >= 1.0),
        }
        for r in order
    ]
    won_every_run = sum(1 for r in rows if r["runs_won"] == r["runs_observed"])
    return {
        "schema_version": 1,
        "source": "GitHub Actions scaled-benchmark artifacts, godofecht/flow-scikit",
        "runs": per_run,
        "counts": {
            "runs": len(order),
            "rows": len(rows),
            "rows_won_in_every_run": won_every_run,
            "rows_lost_in_at_least_one_run": len(rows) - won_every_run,
        },
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", metavar="RUN_ID=PATH")
    ap.add_argument("--out", type=Path, default=HISTORY)
    args = ap.parse_args()

    existing: dict[str, dict[str, float]] = {}
    if args.out.exists():
        prior = json.loads(args.out.read_text())
        for row in prior.get("rows", []):
            key = f"{row['algorithm']}/{row['rows']}x{row['features']}"
            for run, value in zip([r["run_id"] for r in prior["runs"]], row["observations"]):
                existing.setdefault(run, {})[key] = value

    for spec in args.runs:
        if "=" not in spec:
            raise SystemExit(f"expected RUN_ID=PATH, got {spec!r}")
        run_id, path = spec.split("=", 1)
        existing[run_id] = load_run(Path(path))

    summary = summarize(existing)
    args.out.write_text(json.dumps(summary, indent=2) + "\n")
    counts = summary["counts"]
    print(
        f"wrote {args.out.relative_to(ROOT)}: {counts['rows']} rows over {counts['runs']} runs; "
        f"{counts['rows_won_in_every_run']} won in every run, "
        f"{counts['rows_lost_in_at_least_one_run']} dipped below 1x at least once"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
