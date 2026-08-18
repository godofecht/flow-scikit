#!/usr/bin/env python3
"""Run, aggregate, and classify the canonical 19-row headline benchmark."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"

# Environment variables that decide how many threads the native BLAS spawns.
# They change both wall-clock and floating-point reduction order, so they are
# part of the measurement environment and are recorded with it.
THREAD_LIMIT_VARS = (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


def cpu_model() -> str:
    """Best-effort CPU identification for the current host."""
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    try:
        out = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    return platform.processor() or platform.machine() or "unknown"


def host_fingerprint() -> dict:
    """Describe the measurement host.

    `environment_id` only covers the software stack, so two runs on different
    GitHub runner hardware share one id even though their wall-clock ratios and
    their float32 results differ. Runtime comparisons need the hardware and the
    BLAS thread configuration as well, which is what this records.
    """
    return {
        "machine": platform.machine(),
        "cpu_model": cpu_model(),
        "logical_cpus": os.cpu_count(),
        "thread_limits": {var: os.environ.get(var) for var in THREAD_LIMIT_VARS},
    }


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    f = pos - lo
    return ordered[lo] * (1 - f) + ordered[hi] * f


def iqr(values: list[float]) -> float:
    return percentile(values, 0.75) - percentile(values, 0.25)


def parse_text(text: str) -> dict:
    out = {"unit": None, "mode": None, "fixture": None, "environment": None, "rows": {}, "details": {}}
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("TIMING_UNIT|"):
            out["unit"] = line.split("|", 1)[1]
        elif line.startswith("BENCHMARK_MODE|"):
            out["mode"] = line.split("|", 1)[1]
        elif line.startswith("FIXTURE_SOURCE|"):
            out["fixture"] = line.split("|", 1)[1]
        elif line.startswith("BENCHMARK_ENV|"):
            out["environment"] = line.split("|", 1)[1]
        elif line.startswith("RESULT|"):
            p = line.split("|")
            key = (p[1], p[2], p[3])
            out["rows"][key] = {
                "score": float(p[4]),
                "fit_ms": float(p[5]),
                "pred_ms": float(p[6]),
                "fit_iqr_ms": float(p[7]) if len(p) > 7 else None,
                "pred_iqr_ms": float(p[8]) if len(p) > 8 else None,
                "fit_repeats": int(p[9]) if len(p) > 9 else 1,
                "pred_repeats": int(p[10]) if len(p) > 10 else 1,
            }
        elif line.startswith("DETAIL|"):
            p = line.split("|", 4)
            value = p[4]
            out["details"][(p[1], p[2], p[3])] = [float(v) for v in value.split(",")] if "," in value else float(value)
    if out["unit"] != "ms":
        raise RuntimeError(f"benchmark did not declare TIMING_UNIT|ms: {out['unit']!r}")
    return out


def run(command: list[str]) -> dict:
    proc = subprocess.run(command, cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE)
    return parse_text(proc.stdout)


def aggregate(runs: list[dict], impl: str) -> tuple[str, dict]:
    first = runs[0]
    keys = set(first["rows"])
    detail_keys = set(first["details"])
    for current in runs[1:]:
        if set(current["rows"]) != keys:
            raise RuntimeError(f"{impl}: benchmark row set changed between repetitions")
        if set(current["details"]) != detail_keys:
            raise RuntimeError(f"{impl}: detail set changed between repetitions")
        if current["mode"] != first["mode"]:
            raise RuntimeError(f"{impl}: benchmark mode changed between repetitions")

    lines = ["TIMING_UNIT|ms", f"BENCHMARK_MODE|{first['mode'] or 'end_to_end'}", f"FIXTURE_SOURCE|{first['fixture'] or 'canonical'}"]
    if first["environment"]:
        lines.append("BENCHMARK_ENV|" + first["environment"])

    aggregated_rows = {}
    for key in sorted(keys):
        scores = [r["rows"][key]["score"] for r in runs]
        fits = [r["rows"][key]["fit_ms"] for r in runs]
        preds = [r["rows"][key]["pred_ms"] for r in runs]
        score_span = max(scores) - min(scores)
        if score_span > 1e-5:
            raise RuntimeError(f"{impl}: non-deterministic score for {key}: span={score_span}")
        fit_ms = statistics.median(fits)
        pred_ms = statistics.median(preds)
        fit_iqr = iqr(fits)
        pred_iqr = iqr(preds)
        # Internal aggregate repetition count when provided; process repetitions
        # are recorded separately and robustly aggregate both implementations.
        fit_inner = max(r["rows"][key]["fit_repeats"] for r in runs)
        pred_inner = max(r["rows"][key]["pred_repeats"] for r in runs)
        lines.append(
            "RESULT|{}|{}|{}|{:.9g}|{:.9g}|{:.9g}|{:.9g}|{:.9g}|{}|{}".format(
                key[0], key[1], key[2], statistics.median(scores), fit_ms, pred_ms,
                fit_iqr, pred_iqr, fit_inner, pred_inner,
            )
        )
        aggregated_rows[key] = {"fit_ms": fit_ms, "pred_ms": pred_ms, "fit_iqr_ms": fit_iqr, "pred_iqr_ms": pred_iqr}

    for key in sorted(detail_keys):
        values = [r["details"][key] for r in runs]
        first_value = values[0]
        if isinstance(first_value, list):
            if any(not isinstance(v, list) or len(v) != len(first_value) for v in values):
                raise RuntimeError(f"{impl}: detail shape changed for {key}")
            agg = [statistics.median([v[i] for v in values]) for i in range(len(first_value))]
            rendered = ",".join(f"{v:.9g}" for v in agg)
        else:
            rendered = f"{statistics.median(values):.9g}"
        lines.append(f"DETAIL|{key[0]}|{key[1]}|{key[2]}|{rendered}")

    metadata = {
        "implementation": impl,
        "process_repeats": len(runs),
        "environment": first["environment"],
        "mode": first["mode"],
        "fixture": first["fixture"],
    }
    return "\n".join(lines) + "\n", metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--python-command", default=f"{shlex.quote(sys.executable)} benchmarks/bench_sklearn_v2.py")
    parser.add_argument("--flow-command", default=os.environ.get("FLOW_HEADLINE_COMMAND", "flow run benchmarks/bench_flow_v2.flow"))
    args = parser.parse_args()
    if args.repeats < 3:
        parser.error("--repeats must be >= 3 for dispersion estimates")

    py_cmd = shlex.split(args.python_command)
    flow_cmd = shlex.split(args.flow_command)
    py_runs = [run(py_cmd) for _ in range(args.repeats)]
    flow_runs = [run(flow_cmd) for _ in range(args.repeats)]

    py_text, py_meta = aggregate(py_runs, "sklearn")
    flow_text, flow_meta = aggregate(flow_runs, "flow")
    py_path = BENCH / "sklearn_results_v2.txt"
    flow_path = BENCH / "flow_results_v2.txt"
    py_path.write_text(py_text)
    flow_path.write_text(flow_text)

    env_payload = json.dumps({"sklearn": py_meta, "flow": flow_meta}, sort_keys=True, separators=(",", ":"))
    environment_id = hashlib.sha256(env_payload.encode()).hexdigest()[:16]
    host = host_fingerprint()
    runtime_payload = json.dumps({"software": env_payload, "host": host}, sort_keys=True, separators=(",", ":"))
    runtime_environment_id = hashlib.sha256(runtime_payload.encode()).hexdigest()[:16]
    (BENCH / "headline_environment.json").write_text(json.dumps({
        "environment_id": environment_id,
        "runtime_environment_id": runtime_environment_id,
        "host": host,
        "metadata": {"sklearn": py_meta, "flow": flow_meta},
    }, indent=2) + "\n")

    subprocess.run(
        [sys.executable, str(BENCH / "compare_v2.py"), "--sklearn", str(py_path), "--flow", str(flow_path), "--environment-id", environment_id],
        cwd=ROOT,
        check=True,
    )
    print(
        f"environment_id={environment_id}; runtime_environment_id={runtime_environment_id}; "
        f"process_repeats={args.repeats}; cpu={host['cpu_model']!r}; logical_cpus={host['logical_cpus']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
