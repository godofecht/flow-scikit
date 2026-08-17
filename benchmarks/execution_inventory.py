#!/usr/bin/env python3
"""Generate an evidence-backed sklearn estimator operation inventory.

The classifier is intentionally conservative: it records the public entry point,
unwrapped source file, referenced native/numerical symbols and confidence. Rows
with mixed evidence stay ``mixed`` instead of being forced into a native class.
"""
from __future__ import annotations

import argparse
import csv
import inspect
import json
import re
from pathlib import Path

import sklearn
from sklearn.utils import all_estimators

OPS = ("fit", "predict", "predict_proba", "decision_function", "transform")
ROOT = Path(__file__).resolve().parents[1]

NATIVE_PATTERNS = {
    "external-native-bound": ("libsvm", "liblinear"),
    "cython-bound": (
        "_tree", "_forest", "_splitter", "_criterion", "_k_means_lloyd",
        "_k_means_elkan", "_cd_fast", "_sgd_fast", "_hist_gradient_boosting",
        "_loss", "_isotonic", "_pairwise_distances_reduction",
    ),
    "scipy-bound": ("scipy.", "sparse.linalg", "optimize."),
    "blas-lapack-bound": ("linalg.svd", "linalg.solve", "linalg.lstsq", "cho_solve", "cholesky", "lapack", "blas"),
    "numpy-bound": ("np.", "numpy."),
}

HEADLINE_TO_SKLEARN = {
    "KernelSVC_RBF": "SVC",
    "DecisionTree": "DecisionTreeClassifier",
    "RandomForest": "RandomForestClassifier",
    "KernelRidge_RBF": "KernelRidge",
}


def unwrapped(obj):
    try:
        return inspect.unwrap(obj)
    except (ValueError, TypeError):
        return obj


def safe_source(obj):
    try:
        return inspect.getsource(unwrapped(obj))
    except (OSError, TypeError):
        return ""


def safe_file(obj):
    try:
        target = unwrapped(obj)
        return inspect.getsourcefile(target) or inspect.getfile(target) or ""
    except (OSError, TypeError):
        return ""


def flow_status(name: str) -> str:
    needle = name.lower().replace("classifier", "").replace("regressor", "")
    for path in (ROOT / "lib" / "scikit").glob("*.flow"):
        text = path.read_text(errors="ignore").lower()
        if needle and needle in text:
            return "present"
    return "not-found-by-name"


def headline_coverage():
    path = ROOT / "benchmarks" / "headline_result_v2.json"
    coverage = {}
    if not path.exists():
        return coverage
    for row in json.loads(path.read_text()).get("rows", []):
        name = HEADLINE_TO_SKLEARN.get(row["algorithm"], row["algorithm"])
        entry = coverage.setdefault(name, {"datasets": [], "parity": []})
        entry["datasets"].append(row.get("dataset"))
        entry["parity"].append(row.get("parity_status", "unknown"))
    return coverage


def classify(source: str, source_file: str):
    evidence = []
    scores = []
    low = source.lower()
    file_low = source_file.lower()

    if source_file and not source_file.endswith(".py"):
        evidence.append(f"compiled-entry:{source_file}")
        scores.append(("cython-bound", 5))

    for cls, pats in NATIVE_PATTERNS.items():
        hits = sorted({p for p in pats if p.lower() in low or p.lower() in file_low})
        if hits:
            evidence.extend(f"{cls}:{h}" for h in hits)
            scores.append((cls, 4 if cls in {"external-native-bound", "cython-bound"} else 3))

    loop_hits = len(re.findall(r"\b(for|while)\b", source))
    if loop_hits >= 2:
        evidence.append(f"python-control-loops:{loop_hits}")
        scores.append(("python-bound", 2))

    classes = {c for c, _ in scores}
    if not scores:
        return "python-bound", "low", ["python entry point; no recognized native dispatch evidence"]
    if len(classes) > 1:
        strongest = sorted(scores, key=lambda x: x[1], reverse=True)
        if strongest[0][1] == strongest[1][1]:
            return "mixed", "medium", evidence
        if "python-bound" in classes and strongest[0][0] != "python-bound":
            return "mixed", "medium", evidence
        return strongest[0][0], "medium", evidence
    return scores[0][0], "high" if scores[0][1] >= 4 else "medium", evidence


def rows():
    coverage = headline_coverage()
    for name, cls in all_estimators():
        module = cls.__module__
        cov = coverage.get(name)
        for op in OPS:
            method = getattr(cls, op, None)
            if method is None:
                continue
            source = safe_source(method)
            source_file = safe_file(method)
            substrate, confidence, evidence = classify(source, source_file)
            symbols = sorted(set(re.findall(r"(?:np|numpy|scipy|self|[A-Za-z_]\w*)\.([A-Za-z_]\w*)", source)))[:40]
            yield {
                "sklearn_version": sklearn.__version__,
                "module": module,
                "estimator": name,
                "operation": op,
                "source_entry_point": f"{module}.{name}.{op}",
                "source_file": source_file,
                "execution_class": substrate,
                "confidence": confidence,
                "evidence": evidence,
                "referenced_symbols": symbols,
                "flow_scikit_status": flow_status(name),
                "benchmark_coverage": "canonical-headline:" + ",".join(sorted(set(cov["datasets"]))) if cov else "not-in-canonical-headline",
                "parity_coverage": ",".join(sorted(set(cov["parity"]))) if cov else "not-in-canonical-headline",
            }


def markdown(data):
    groups = {}
    for row in data:
        groups.setdefault(row["execution_class"], []).append(row)
    out = [
        "# sklearn execution-substrate inventory", "",
        f"Pinned/generated sklearn: `{sklearn.__version__}`", "",
        "Generated by `benchmarks/execution_inventory.py`; classifications are evidence-backed and conservative.", "",
    ]
    for group in sorted(groups):
        out += [f"## {group}", "", "| Estimator | Operation | Confidence | Benchmark | Evidence |", "|---|---|---|---|---|"]
        for r in groups[group]:
            ev = "; ".join(r["evidence"][:4]).replace("|", "\\|")
            out.append(f"| `{r['module']}.{r['estimator']}` | `{r['operation']}` | {r['confidence']} | {r['benchmark_coverage']} | {ev} |")
        out.append("")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", type=Path, default=ROOT / "benchmarks" / "sklearn_execution_inventory.json")
    p.add_argument("--csv", type=Path, default=ROOT / "benchmarks" / "sklearn_execution_inventory.csv")
    p.add_argument("--markdown", type=Path, default=ROOT / "benchmarks" / "SKLEARN_EXECUTION_INVENTORY.md")
    args = p.parse_args()
    data = list(rows())
    args.json.write_text(json.dumps({"schema_version": 1, "sklearn_version": sklearn.__version__, "rows": data}, indent=2) + "\n")
    with args.csv.open("w", newline="") as f:
        fields = ["sklearn_version","module","estimator","operation","source_entry_point","source_file","execution_class","confidence","flow_scikit_status","benchmark_coverage","parity_coverage","evidence","referenced_symbols"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in data:
            q = dict(r)
            q["evidence"] = json.dumps(q["evidence"])
            q["referenced_symbols"] = json.dumps(q["referenced_symbols"])
            writer.writerow(q)
    args.markdown.write_text(markdown(data) + "\n")
    print(f"inventory: {len(data)} estimator operations across {len({r['estimator'] for r in data})} estimators")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
