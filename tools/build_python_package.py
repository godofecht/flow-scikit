#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ROOT / "python"
INTEROP = PYTHON_DIR / "interop.flow"
GENERATED = PYTHON_DIR / "generated" / "flow_scikit_native.c"


def resolve_flow_root(explicit: str | None) -> Path:
    candidates = [
        explicit,
        os.environ.get("FLOW_ROOT"),
        str(ROOT / ".flow-toolchain"),
        str(ROOT.parent / "flow"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser().resolve()
        if (path / "src" / "flow" / "transpiler.py").is_file():
            return path
    raise SystemExit(
        "Flow compiler source not found. Pass --flow-root, set FLOW_ROOT, "
        "or check out Flow at .flow-toolchain."
    )


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def generate_native_source(flow_root: Path) -> None:
    GENERATED.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    pythonpath = str(flow_root / "src")
    if env.get("PYTHONPATH"):
        pythonpath = pythonpath + os.pathsep + env["PYTHONPATH"]
    env["PYTHONPATH"] = pythonpath

    run(
        [
            sys.executable,
            "-m",
            "flow.transpiler",
            str(INTEROP),
            "--c",
            "--library",
            "--lenient",
            "--no-bounds-check",
            "-o",
            str(GENERATED),
        ],
        env=env,
    )


def build_wheel(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            str(PYTHON_DIR),
            "--no-deps",
            "--wheel-dir",
            str(output_dir),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the Flow native translation unit and build the flow-scikit wheel."
    )
    parser.add_argument("--flow-root")
    parser.add_argument("--output-dir", default=str(ROOT / "dist"))
    parser.add_argument("--skip-wheel", action="store_true")
    args = parser.parse_args()

    flow_root = resolve_flow_root(args.flow_root)
    generate_native_source(flow_root)

    if not args.skip_wheel:
        build_wheel(Path(args.output_dir).resolve())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
