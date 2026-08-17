#!/usr/bin/env python3
"""Build flow-scikit's browser runtime through Flow's direct MLIR wasm32 target."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


BROWSER_EXPORTS = (
    "browser_accuracy",
    "browser_precision",
    "browser_recall",
    "browser_f1",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--flow-repo",
        default=os.environ.get("FLOW_REPO", "../flow"),
        help="Path to a Flow checkout containing flow.wasm_compiler",
    )
    parser.add_argument("-o", "--output", default="docs/wasm/browser_mlir.wasm")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    flow_repo = Path(args.flow_repo).resolve()
    flow_src = flow_repo / "src"
    if not flow_src.exists():
        raise SystemExit(f"Flow source tree not found: {flow_src}")

    sys.path.insert(0, str(flow_src))
    previous_pythonpath = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(flow_src), previous_pythonpath) if part
    )

    from flow.wasm_compiler import flow_to_wasm

    source = root / "docs" / "wasm" / "browser_mlir.flow"
    output = (root / args.output).resolve()
    previous = Path.cwd()
    try:
        os.chdir(root)
        flow_to_wasm(source, output, exports=BROWSER_EXPORTS, optimize="O2")
    finally:
        os.chdir(previous)
        if previous_pythonpath is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = previous_pythonpath

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
