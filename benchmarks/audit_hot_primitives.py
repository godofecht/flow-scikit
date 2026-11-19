#!/usr/bin/env python3
"""Inventory the hot-loop call sites in lib/scikit and which ones use a shared primitive.

Scans every function body in lib/scikit/*.flow (datasets_real.flow, which is
data, is skipped) for these loop shapes:

  squared-distance   acc = acc + d * d, with d defined as a difference
  dot                acc = acc + x[..] * y[..] in a scalar loop
  sum-reduction      acc = acc + x[..] in a scalar loop
  rbf                exp() applied to gamma or length scale times a distance
  row-partition      functions that gather, split, sample or select rows

A site is "shared" when its function is itself a shared primitive or calls one
(sqdist_f32, array_dot, blas_dot, cblas_sdot and the like). Everything else is
"inline". Static scan only, so the output is deterministic. `--check` fails
when the committed audit differs from a fresh scan.

This finds loop shapes by text. It does not prove two loops have the same
semantics, so each consolidation still needs the bit-exactness check in
tests/test_shared_primitives.flow.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "lib" / "scikit"
SKIP = {"datasets_real.flow"}

SHARED_PRIMITIVES = {
    "sqdist_f32": "squared-distance",
    "sqdist_f32_acc_f64": "squared-distance",
    "array_dot": "dot",
    "dot_product": "dot",
    "blas_dot": "dot",
    "cblas_sdot": "dot",
    "cblas_ddot": "dot",
    "blas_dot_strided_f64": "dot",
    "blas_matvec": "dot",
    "cblas_sgemm": "dot",
    "cblas_dgemm": "dot",
}
# Functions that define the primitives; their own loop is the implementation.
PRIMITIVE_DEFINITIONS = {"sqdist_f32", "sqdist_f32_acc_f64", "array_dot", "blas_dot", "blas_dot_strided_f64"}

FUNC = re.compile(r"^\s*(?:export\s+)?function\s+([A-Za-z_0-9]+)\s*\(")
ACC_SQ = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*\1\s*\+\s*([A-Za-z_]\w*)\s*\*\s*\2\s*$")
ACC_PROD = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*\1\s*\+\s*(.+?\S)\s*\*\s*(.+\S)\s*$")
ACC_SUM = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*\1\s*\+\s*([A-Za-z_]\w*\[[^\]]+\]|matrix_at\([^)]*\))\s*$")
DIFF = re.compile(r"^\s*let\s+(?:mut\s+)?([A-Za-z_]\w*)\s*:\s*f(?:32|64)\s*=\s*.*\s-\s.*$")
RBF = re.compile(r"\bexp\(.*(gamma|length_scale|neg_gamma)", re.I)
PARTITION_NAME = re.compile(r"(split|partition|gather|take_rows|select_rows|subset|bootstrap|subsample|sample_rows)", re.I)
INDEXED = re.compile(r"\[[^\]]+\]|matrix_at\(")


def functions(text: str):
    """Yield (name, start_line, [(line_no, line), ...]) for each function."""
    lines = text.splitlines()
    starts = [(i, FUNC.match(ln).group(1)) for i, ln in enumerate(lines) if FUNC.match(ln)]
    for k, (i, name) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        yield name, i + 1, [(j + 1, lines[j]) for j in range(i, end)]


def scan_function(name: str, body: list[tuple[int, str]]) -> list[dict]:
    sites: list[dict] = []
    calls = {p for p in SHARED_PRIMITIVES if re.search(rf"\b{p}\s*\(", "\n".join(b for _, b in body[1:]))}
    shared_calls = {SHARED_PRIMITIVES[p] for p in calls}
    diffs: dict[str, int] = {}
    for no, line in body:
        stripped = line.split("#", 1)[0]
        m = DIFF.match(stripped)
        if m:
            diffs[m.group(1)] = no
        sq = ACC_SQ.match(stripped)
        if sq and sq.group(2) in diffs and no - diffs[sq.group(2)] <= 4:
            sites.append({"line": no, "category": "squared-distance"})
            continue
        pr = ACC_PROD.match(stripped)
        if pr and INDEXED.search(pr.group(2)) and INDEXED.search(pr.group(3)):
            sites.append({"line": no, "category": "dot"})
            continue
        if ACC_SUM.match(stripped):
            sites.append({"line": no, "category": "sum-reduction"})
            continue
        if RBF.search(stripped):
            sites.append({"line": no, "category": "rbf"})
    if PARTITION_NAME.search(name):
        sites.append({"line": body[0][0], "category": "row-partition"})
    for s in sites:
        if name in PRIMITIVE_DEFINITIONS and s["category"] == SHARED_PRIMITIVES.get(name):
            s["status"] = "primitive"
        elif s["category"] in shared_calls:
            s["status"] = "shared"
        else:
            s["status"] = "inline"
    return sites


def audit() -> dict:
    rows = []
    for path in sorted(LIB.glob("*.flow")):
        if path.name in SKIP:
            continue
        text = path.read_text()
        for name, _start, body in functions(text):
            for s in scan_function(name, body):
                rows.append({"file": f"lib/scikit/{path.name}", "function": name, **s})
    categories = ["squared-distance", "dot", "sum-reduction", "rbf", "row-partition"]
    summary = {c: {"primitive": 0, "shared": 0, "inline": 0, "inline_functions": []} for c in categories}
    for r in rows:
        entry = summary[r["category"]]
        entry[r["status"]] += 1
        if r["status"] == "inline" and r["function"] not in entry["inline_functions"]:
            entry["inline_functions"].append(r["function"])
    for entry in summary.values():
        entry["inline_functions"].sort()
    primitives = sorted(
        {r["function"] for r in rows if r["status"] == "primitive"}
        | {p for p in SHARED_PRIMITIVES if any(re.search(rf"function\s+{p}\s*\(", pth.read_text()) for pth in LIB.glob("*.flow") if pth.name not in SKIP)}
    )
    call_sites = {}
    for name in sorted(SHARED_PRIMITIVES):
        n = 0
        for pth in LIB.glob("*.flow"):
            if pth.name in SKIP:
                continue
            for ln in pth.read_text().splitlines():
                code = ln.split("#", 1)[0]
                if re.search(rf"\b{name}\s*\(", code) and not FUNC.match(code) and "function " not in code:
                    n += 1
        if n:
            call_sites[name] = n
    return {"schema_version": 1, "defined_primitives": primitives, "primitive_call_sites": call_sites,
            "summary": summary, "sites": rows}


def render_markdown(doc: dict) -> str:
    out = ["# Hot primitive audit", "",
           "Generated by `benchmarks/audit_hot_primitives.py`. A static scan of `lib/scikit` for hot-loop shapes.",
           "A site is `shared` when its function calls a shared primitive and `inline` otherwise.", "",
           "Defined primitives: " + ", ".join(f"`{p}`" for p in doc["defined_primitives"]), "",
           "Call sites per primitive: " + ", ".join(f"`{k}` {v}" for k, v in doc["primitive_call_sites"].items()), "",
           "| Category | Primitive definitions | Shared call sites | Inline sites | Functions with inline sites |",
           "|---|---:|---:|---:|---|"]
    for cat, e in doc["summary"].items():
        funcs = ", ".join(f"`{f}`" for f in e["inline_functions"][:12])
        more = len(e["inline_functions"]) - 12
        if more > 0:
            funcs += f" and {more} more"
        out.append(f"| {cat} | {e['primitive']} | {e['shared']} | {e['inline']} | {funcs} |")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=ROOT / "benchmarks" / "hot_primitive_audit.json")
    ap.add_argument("--markdown", type=Path, default=ROOT / "benchmarks" / "HOT_PRIMITIVE_AUDIT.md")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    doc = audit()
    text = json.dumps(doc, indent=2) + "\n"
    md = render_markdown(doc)
    if args.check:
        if not args.json.exists() or args.json.read_text() != text or not args.markdown.exists() or args.markdown.read_text() != md:
            print("hot primitive audit is stale. Run: python benchmarks/audit_hot_primitives.py")
            return 1
        print("hot primitive audit matches lib/scikit")
        return 0
    args.json.write_text(text)
    args.markdown.write_text(md)
    for cat, e in doc["summary"].items():
        print(f"{cat:18} primitive {e['primitive']:3} shared {e['shared']:3} inline {e['inline']:4}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
