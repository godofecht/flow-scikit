#!/usr/bin/env python3
"""Join the wide Flow and scikit-learn estimator timings into one artifact.

This is a breadth measurement, and it says so in its own output. The canonical
19 rows carry a parity contract, declared tolerances and a disparity report;
these rows carry none of that. An estimator here is timed on the same data with
each library's own defaults, which answers "is the Flow implementation in the
same performance league" and does not answer "does it compute the same thing".

`speedup` is `sklearn_ms / flow_ms` over fit plus predict, as everywhere else.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINE = re.compile(r"^ESTIMATOR\|([a-z_0-9]+)\|([0-9.eE+-]+)\|([0-9.eE+-]+)\|(\d+)\|ok$")

# flow_now_ns resolves to about a microsecond through this harness, so a total
# at or below this is a rounding artifact rather than a measurement.
RESOLUTION_MS = 0.00002


def parse_flow(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for line in path.read_text().splitlines():
        m = LINE.match(line.strip())
        if not m:
            continue
        name, fit, pred, reps = m.group(1), float(m.group(2)), float(m.group(3)), int(m.group(4))
        prior = rows.get(name)
        # Repeated runs of the same file: keep the fastest, as every other
        # harness here does.
        if prior is None or fit + pred < prior["fit_ms"] + prior["pred_ms"]:
            rows[name] = {"fit_ms": fit, "pred_ms": pred, "repeats": reps}
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("flow", type=Path, help="captured ESTIMATOR| lines from the generated benchmarks")
    ap.add_argument("--sklearn", type=Path, default=ROOT / "benchmarks" / "estimators_sklearn.json")
    ap.add_argument("--registry", type=Path, default=ROOT / "benchmarks" / "estimator_coverage.json")
    ap.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "estimator_comparison.json")
    ap.add_argument("--note", default="", help="recorded verbatim in the artifact, for measurement conditions")
    args = ap.parse_args()

    flow = parse_flow(args.flow)
    sk = {r["flow_estimator"]: r for r in json.loads(args.sklearn.read_text())["rows"]}
    registry = json.loads(args.registry.read_text())

    rows = []
    for entry in registry["entries"]:
        name = entry["flow_estimator"]
        if entry["bucket"] != "runnable":
            rows.append({"flow_estimator": name, "status": entry["bucket"], "reason": entry.get("reason", "")})
            continue
        f, s = flow.get(name), sk.get(name)
        if f is None:
            rows.append({"flow_estimator": name, "sklearn_estimator": entry["sklearn_estimator"],
                         "status": "flow_missing", "reason": "no ESTIMATOR line in the Flow output"})
            continue
        if s is None or s.get("status") != "ok":
            rows.append({"flow_estimator": name, "sklearn_estimator": entry["sklearn_estimator"],
                         "status": "sklearn_missing", "reason": (s or {}).get("reason", "absent")})
            continue
        flow_ms = f["fit_ms"] + f["pred_ms"]
        sk_ms = s["fit_ms"] + s["pred_ms"]
        # The harness repeats a fast estimator until the clock can see it, so
        # this should not trigger any more. It stays as the backstop it always
        # was: a Flow side at the floor has been rounded rather than measured.
        if flow_ms <= RESOLUTION_MS:
            rows.append({
                "flow_estimator": name,
                "sklearn_estimator": entry["sklearn_estimator"],
                "dataset": s["dataset"],
                "flow_ms": flow_ms,
                "sklearn_ms": sk_ms,
                "speedup": None,
                "timing_unit": "ms",
                "status": "below_resolution",
                "reason": f"Flow side at or under {RESOLUTION_MS} ms, which is the clock's floor here",
            })
            continue
        rows.append({
            "flow_estimator": name,
            "sklearn_estimator": entry["sklearn_estimator"],
            "dataset": s["dataset"],
            "flow_ms": flow_ms,
            "sklearn_ms": sk_ms,
            "speedup": (sk_ms / flow_ms) if flow_ms > 0 else None,
            "flow_repeats": f["repeats"],
            "timing_unit": "ms",
            "status": "ok",
        })

    compared = [r for r in rows if r["status"] == "ok" and r["speedup"] is not None]
    unmeasured = [r for r in rows if r["status"] == "below_resolution"]
    wins = sum(1 for r in compared if r["speedup"] >= 1.0)
    payload = {
        "schema_version": 1,
        "contract": "breadth timing only; no parity contract, no declared tolerances, "
                    "each library on its own defaults over the same data",
        "measurement": "fastest of several rounds per estimator on both sides, which is "
                       "what survives a machine that is not idle",
        "note": args.note,
        "counts": {
            "registry_estimators": len(registry["entries"]),
            "compared": len(compared),
            "flow_wins": wins,
            "sklearn_wins": len(compared) - wins,
            "below_resolution": len(unmeasured),
        },
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"compared {len(compared)} estimators: {wins} Flow wins, {len(compared) - wins} scikit-learn wins")
    if unmeasured:
        print(f"{len(unmeasured)} rows left unranked, Flow side under the clock's resolution:")
        for r in sorted(unmeasured, key=lambda r: r["flow_estimator"]):
            print(f"  {r['flow_estimator']:32s} flow={r['flow_ms']:.4f} sklearn={r['sklearn_ms']:9.3f}")
    losers = sorted((r for r in compared if r["speedup"] < 1.0), key=lambda r: r["speedup"])
    for r in losers:
        print(f"  {r['speedup']:6.2f}x  {r['flow_estimator']:32s} flow={r['flow_ms']:9.3f} sklearn={r['sklearn_ms']:9.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
