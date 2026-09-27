#!/usr/bin/env python3
"""Compile and run the generated estimator benchmarks, and collect their lines.

The wide matrix used to be driven by a shell loop typed out by hand, which is
how a chunk that died mid-run once passed for a chunk that had no rows. This
does the same work with the failures visible: every chunk's exit status is
checked, and a chunk that dies takes its own row count down with it in the
summary rather than disappearing.

Each chunk prints one `ESTIMATOR|name|fit_ms|pred_ms|reps|ok` line per
estimator and flushes it, so a crash costs only the rows after it.
compare_estimators.py keeps the fastest observation per estimator, so several
rounds of the same chunk are appended to one file and joined there.

The first round compiles through `flow run`. Later rounds re-exec the binary
that left behind, because compiling the library at -O3 costs far more than
running the timings.
"""
from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "benchmarks" / "generated"
LINE = re.compile(r"^ESTIMATOR\|([a-z_0-9]+)\|")

MAC_LDFLAGS = "-framework Accelerate lib/scikit/flow_time.c lib/scikit/flow_parallel.c"
LINUX_LDFLAGS = "-lm -lopenblas lib/scikit/flow_time.c lib/scikit/flow_parallel.c"


def default_ldflags() -> str:
    return MAC_LDFLAGS if platform.system() == "Darwin" else LINUX_LDFLAGS


def flow_binary() -> str:
    explicit = os.environ.get("FLOW_BIN")
    if explicit:
        return explicit
    found = shutil.which("flow")
    if not found:
        raise SystemExit("no flow binary on PATH and FLOW_BIN is unset")
    return found


def built_binary(flow_bin: str, stem: str) -> Path:
    # flow run writes its C and its executable into one build directory next to
    # the compiler, whatever directory the source came from.
    return Path(flow_bin).resolve().parent / "build" / stem


def run(cmd: list[str], env: dict[str, str], cwd: Path, timeout: int) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired as exc:
        return 124, (exc.stdout or "") if isinstance(exc.stdout, str) else ""
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--out", type=Path, default=ROOT / "benchmarks" / "estimator_flow_raw.txt")
    ap.add_argument("--outdir", type=Path, default=GENERATED)
    ap.add_argument("--opt", default="3")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--only", help="one chunk stem, for bisecting a failure")
    args = ap.parse_args()

    chunks = sorted(args.outdir.glob("bench_estimators_*.flow"))
    if args.only:
        chunks = [c for c in chunks if c.stem == args.only]
    if not chunks:
        raise SystemExit(f"no generated benchmarks in {args.outdir}")

    flow_bin = flow_binary()
    env = dict(os.environ)
    env["FLOW_HOST"] = env.get("FLOW_HOST", "python")
    env["FLOW_OPT_LEVEL"] = args.opt
    env["FLOW_LDFLAGS"] = env.get("FLOW_LDFLAGS") or default_ldflags()

    collected: list[str] = []
    seen: set[str] = set()
    failures: list[str] = []

    for round_index in range(args.rounds):
        for chunk in chunks:
            binary = built_binary(flow_bin, chunk.stem)
            if round_index == 0 or not binary.exists():
                cmd = [flow_bin, "run", str(chunk)]
            else:
                cmd = [str(binary)]
            code, output = run(cmd, env, ROOT, args.timeout)
            rows = [l for l in output.splitlines() if LINE.match(l.strip())]
            collected.extend(rows)
            for line in rows:
                seen.add(line.split("|")[1])
            status = "ok" if code == 0 else f"exit={code}"
            if code != 0:
                failures.append(f"round {round_index} {chunk.stem} {status}")
            print(f"round {round_index} {chunk.stem}: {len(rows)} rows {status}", flush=True)

    args.out.write_text("\n".join(collected) + "\n")
    print(f"{len(seen)} estimators, {len(collected)} lines -> {args.out}")
    if failures:
        print("failures:")
        for f in failures:
            print(f"  {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
