from __future__ import annotations

import os
import sys
from pathlib import Path

from setuptools import Extension, setup


HERE = Path(__file__).resolve().parent
GENERATED = HERE / "generated" / "flow_scikit_native.c"

if not GENERATED.exists():
    raise RuntimeError(
        "generated Flow C source is missing; run "
        "`python tools/build_python_package.py --skip-wheel` from the repository root first"
    )

libraries: list[str] = []
extra_link_args: list[str] = []

override = os.environ.get("FLOW_SCIKIT_BLAS_LIB")
if override:
    libraries.extend(name.strip() for name in override.split(",") if name.strip())
elif sys.platform == "darwin":
    extra_link_args.extend(["-framework", "Accelerate"])
elif os.name == "nt":
    libraries.append("openblas")
else:
    libraries.extend(["openblas", "m"])

extension = Extension(
    "flow_scikit._flow_scikit_native",
    sources=[
        str(HERE / "src" / "flow_scikit" / "_native.c"),
        str(GENERATED),
    ],
    libraries=libraries,
    extra_compile_args=["-O3"],
    extra_link_args=extra_link_args,
)

setup(ext_modules=[extension])
