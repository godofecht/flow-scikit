#!/usr/bin/env python3
"""Time the scikit-learn counterpart of every runnable registry entry.

Reads `estimator_coverage.json` so the two sides cannot drift apart: an
estimator is raced here exactly when the Flow generator emitted a block for it.

Each estimator is constructed with its own defaults rather than a translation
of the Flow hyperparameters. The Flow side passes a fixed set of small values,
and matching them one by one across 172 estimators would be a second source of
error without making the comparison more honest: this measures each library
doing its own default thing on the same data, and the per-estimator parameter
contract stays the canonical benchmark's job.
"""
from __future__ import annotations

import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
from sklearn.datasets import load_diabetes, load_iris
from sklearn.utils import all_estimators

# IterativeImputer is behind an experimental flag.
from sklearn.experimental import enable_iterative_imputer  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "benchmarks" / "estimator_coverage.json"

# Meta-estimators need a base estimator, and a few refuse their own defaults on
# this data. A shallow tree keeps the wrapper's own overhead visible rather than
# burying it under the base estimator's work.
def _constructors() -> dict:
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.preprocessing import FunctionTransformer, StandardScaler
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    import numpy as np

    tree_c = lambda: DecisionTreeClassifier(max_depth=3)
    tree_r = lambda: DecisionTreeRegressor(max_depth=3)
    return {
        "ClassifierChain": lambda c: c(tree_c()),
        "MultiOutputClassifier": lambda c: c(tree_c()),
        "MultiOutputRegressor": lambda c: c(tree_r()),
        "OneVsOneClassifier": lambda c: c(tree_c()),
        "OneVsRestClassifier": lambda c: c(tree_c()),
        "OutputCodeClassifier": lambda c: c(tree_c()),
        "RegressorChain": lambda c: c(tree_r()),
        "RFE": lambda c: c(tree_c()),
        "RFECV": lambda c: c(tree_c()),
        "SequentialFeatureSelector": lambda c: c(tree_c(), n_features_to_select=2),
        "StackingClassifier": lambda c: c(estimators=[("t", tree_c())]),
        "StackingRegressor": lambda c: c(estimators=[("r", Ridge())]),
        "VotingClassifier": lambda c: c(estimators=[("t", tree_c())]),
        "VotingRegressor": lambda c: c(estimators=[("r", Ridge())]),
        "SparseCoder": lambda c: c(dictionary=np.eye(4)),
        # nu=0.5 is infeasible for this class balance.
        "NuSVC": lambda c: c(nu=0.1),
        # A selector needs something to read importances from.
        "SelectFromModel": lambda c: c(tree_c(), threshold=-np.inf, max_features=2),
        # The composed rows, built to match what the Flow harness composes:
        # a scaler and a logistic regression, a scaler over the columns, and a
        # scaler beside a passthrough.
        "Pipeline": lambda c: c([("scaler", StandardScaler()),
                                 ("classifier", LogisticRegression(max_iter=50))]),
        "ColumnTransformer": lambda c: c([("scaler", StandardScaler(), [0, 1, 2, 3])]),
        "FeatureUnion": lambda c: c([("scaler", StandardScaler()),
                                     ("passthrough", FunctionTransformer())]),
    }


CLASSIFICATION = {"classification"}


def dataset_kind(entry: dict) -> str:
    names = [p["name"] for p in entry["fit"]["parameters"]]
    types = {p["name"]: p["type"] for p in entry["fit"]["parameters"]}
    if "y" not in names and "Y" not in names:
        return "unsupervised"
    if "Y" in names:
        return "multioutput_class" if "classifier" in entry["flow_estimator"] or "chain" in entry["flow_estimator"] else "multioutput"
    if "n_classes" in names or types.get("y") == "ptr<i32>":
        return "classification"
    return "regression"


def timed(fn, repeats: int) -> float:
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        best = min(best, (time.perf_counter() - t0) * 1000.0)
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "estimators_sklearn.json")
    args = ap.parse_args()

    registry = json.loads(REGISTRY.read_text())
    # Matches generate_estimator_bench.py: shaped rows are raced and ranked,
    # simplified rows are timed on both sides and shown without a ratio.
    runnable = [e for e in registry["entries"]
                if e["bucket"] in ("runnable", "shaped", "simplified")]
    classes = dict(all_estimators())
    constructors = _constructors()

    iris = load_iris()
    diabetes = load_diabetes()
    data = {
        "classification": (iris.data.astype(np.float64), iris.target.astype(np.float64)),
        "unsupervised": (iris.data.astype(np.float64), None),
        "regression": (diabetes.data.astype(np.float64), diabetes.target.astype(np.float64)),
    }
    y_multi = np.column_stack([diabetes.target, diabetes.target * 0.5])
    data["multioutput"] = (diabetes.data.astype(np.float64), y_multi)
    y_labels = np.column_stack([iris.target, (iris.target + 1) % 3])
    data["multioutput_class"] = (iris.data.astype(np.float64), y_labels)

    rows = []
    for entry in runnable:
        name = entry["sklearn_estimator"]
        cls = classes.get(name)
        if cls is None:
            rows.append({"flow_estimator": entry["flow_estimator"], "sklearn_estimator": name,
                         "status": "unavailable", "reason": "not in sklearn.utils.all_estimators()"})
            continue
        shape = entry.get("shape")
        kind = shape["dataset"] if shape else dataset_kind(entry)
        X, y = data[kind]
        ctor_kwargs = {}
        if shape and shape.get("sklearn_ctor"):
            # The string is the constructor's own keyword list, kept next to the
            # Flow call it matches so the two cannot drift apart.
            ctor_kwargs = eval(f"dict({shape['sklearn_ctor']})")  # noqa: S307
        # A row whose scikit-learn side fits a target vector or a single ordered
        # variable rather than a design. The Flow side of these is written out
        # in the registry for the same reason.
        fit_input = (shape or {}).get("sklearn_input", "X")
        if fit_input == "y":
            first, second = y, None
        elif fit_input == "x1d":
            first, second = X[:, 0], y
        elif fit_input == "docs":
            # The corpus travels in the registry, so the Flow file and this one
            # read one copy of it.
            first, second = list(shape["corpus"]), None
        elif fit_input == "dicts":
            first = [{f"f{j}": float(v) for j, v in enumerate(row)} for row in X]
            second = None
        elif fit_input == "labelsets":
            first = [tuple(int(v) for v in row) for row in y]
            second = None
        else:
            first, second = X, y
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                build = constructors.get(name)
                model = build(cls) if build else cls(**ctor_kwargs)
                fit_ms = timed(
                    (lambda: model.fit(first)) if second is None
                    else (lambda: model.fit(first, second)),
                    args.repeats,
                )
                pred_ms = 0.0
                # A recipe can name the method to time, for a class whose work
                # is called something other than predict or transform.
                methods = [shape["sklearn_work"]] if shape and shape.get("sklearn_work") \
                    else ["predict", "transform"]
                for method in methods:
                    if hasattr(model, method):
                        try:
                            pred_ms = timed(lambda m=method: getattr(model, m)(first), args.repeats)
                        except Exception:
                            pred_ms = 0.0
                        break
            rows.append({
                "flow_estimator": entry["flow_estimator"],
                "sklearn_estimator": name,
                "dataset": kind,
                "fit_ms": fit_ms,
                "pred_ms": pred_ms,
                "timing_unit": "ms",
                "status": "ok",
            })
        except Exception as exc:  # the estimator refused this data or these defaults
            rows.append({
                "flow_estimator": entry["flow_estimator"],
                "sklearn_estimator": name,
                "dataset": kind,
                "status": "failed",
                "reason": f"{type(exc).__name__}: {exc}"[:200],
            })

    ok = sum(1 for r in rows if r["status"] == "ok")
    args.output.write_text(json.dumps({"schema_version": 1, "repeats": args.repeats,
                                       "counts": {"rows": len(rows), "ok": ok},
                                       "rows": rows}, indent=2) + "\n")
    print(f"timed {ok} of {len(rows)} scikit-learn estimators -> {args.output.name}")
    for r in rows:
        if r["status"] != "ok":
            print(f"  {r['status']}: {r['flow_estimator']} -> {r['sklearn_estimator']}: {r.get('reason','')[:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
