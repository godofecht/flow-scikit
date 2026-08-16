#!/usr/bin/env python3
"""Run every Flow test and example with a single command.

Usage:
  python tools/run_all.py            # run tests + examples
  python tools/run_all.py tests      # run tests only
  python tools/run_all.py examples   # run examples only
  python tools/run_all.py tests examples   # explicit selection

Each .flow file is compiled and executed via `flow run <file>`. A file
passes when its process exits 0. The runner prints a per-file result line
and a final summary, and exits non-zero if any file failed.

Environment:
  FLOW_HOST, FLOW_CPU_BACKEND, FLOW_SANITIZE, etc. are forwarded to flow.
  FLOW_BIN overrides the flow executable (default: "flow" from PATH).
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests"
EXAMPLES_DIR = ROOT / "examples"

GROUPS = {
    "tests": TESTS_DIR,
    "examples": EXAMPLES_DIR,
}


def discover(group: str) -> list[Path]:
    return sorted(GROUPS[group].glob("*.flow"))


def run_file(flow_cmd: list[str], file: Path) -> tuple[bool, float, str]:
    start = time.perf_counter()
    result = subprocess.run(
        flow_cmd + ["run", str(file)],
        cwd=ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start
    tail = result.stderr.strip() or result.stdout.strip()
    return result.returncode == 0, elapsed, tail


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        selected = list(GROUPS)
    else:
        selected = []
        for a in args:
            if a not in GROUPS:
                print(f"unknown group: {a}", file=sys.stderr)
                print(__doc__.strip(), file=sys.stderr)
                return 2
            selected.append(a)

    flow_bin = os.environ.get("FLOW_BIN", "flow")
    flow_cmd = shlex.split(flow_bin)
    if not flow_cmd:
        print("Error: FLOW_BIN is empty or invalid", file=sys.stderr)
        return 2

    executable = shutil.which(flow_cmd[0])
    if not executable:
        print(f"Error: Executable '{flow_cmd[0]}' not found", file=sys.stderr)
        return 2

    if "flow" not in os.path.basename(executable).lower():
        print(
            f"Error: Executable '{executable}' does not appear to be a flow binary. "
            "For security reasons, the executable name must contain 'flow'.",
            file=sys.stderr,
        )
        return 2

    flow_cmd[0] = executable

    files: list[tuple[str, Path]] = []
    for group in selected:
        for f in discover(group):
            files.append((group, f))

    if not files:
        print("no .flow files found", file=sys.stderr)
        return 2

    total = len(files)
    width = max(len(str(f.relative_to(ROOT))) for _, f in files)

    print(f"Running {total} file(s) with {' '.join(flow_cmd)}")
    print("=" * (width + 18))
    print("")

    passed = 0
    failed = 0
    failures: list[tuple[str, Path, str]] = []

    for index, (group, file) in enumerate(files, start=1):
        rel = str(file.relative_to(ROOT))
        ok, elapsed, tail = run_file(flow_cmd, file)
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
            print(f"  [{index:>3}/{total}] {status}  {rel:<{width}}  {elapsed:5.2f}s")
        else:
            failed += 1
            failures.append((group, file, tail))
            print(f"  [{index:>3}/{total}] {status}  {rel:<{width}}  {elapsed:5.2f}s")

    print("")
    print("=" * (width + 18))
    print(f"  passed {passed}/{total}   failed {failed}/{total}")

    if failures:
        print("")
        print("Failures:")
        for group, file, tail in failures:
            rel = str(file.relative_to(ROOT))
            print(f"  {rel}:")
            for line in tail.splitlines()[-8:]:
                print(f"    {line}")
        print("")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
