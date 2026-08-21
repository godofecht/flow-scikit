#!/usr/bin/env python3
"""Pin the behaviour of the configuration comparator.

Two halves, and both matter:

* A setting recorded under two vocabularies must stop being reported as a
  difference. That is #469.
* A real divergence must still be reported. The unverified conversion, the
  two-sided value mismatch and the solver that does own the knob hold that line.
  #430 exists because a silent regularization mismatch survived unnoticed, so a
  mapping that does not hold numerically has to come back as a difference.
"""
from __future__ import annotations

import json
from pathlib import Path

from config_equivalence import compare_configs

ROOT = Path(__file__).resolve().parent
FAILURES: list[str] = []

IRIS_N_TRAIN = 120
DIGITS_N_TRAIN = 1437


def check(name: str, actual, expected) -> None:
    if actual == expected:
        print(f"  ok   {name}")
        return
    FAILURES.append(name)
    print(f"  FAIL {name}\n         expected {expected!r}\n         actual   {actual!r}")


def parameters(entries) -> list[str]:
    return [e["parameter"] for e in entries]


def rules(entries) -> dict[str, str]:
    return {e["parameter"]: e["rule"] for e in entries}


def test_cross_vocabulary_mapping() -> None:
    print("cross-vocabulary mapping C <-> l2")

    for n_train, l2 in ((IRIS_N_TRAIN, 0.008333333), (DIGITS_N_TRAIN, 0.000695894)):
        diff, equiv = compare_configs({"l2": l2}, {"C": 1.0}, n_train)
        check(f"verified conversion at n_train={n_train} reports nothing", diff, [])
        check(f"verified conversion at n_train={n_train} is recorded", rules(equiv),
              {"l2": "cross-vocabulary mapping"})

    diff, equiv = compare_configs({"l2": 0.01}, {"C": 1.0}, IRIS_N_TRAIN)
    check("a conversion that does not hold is reported", parameters(diff), ["C", "l2"])
    check("the failed conversion is not recorded as an equivalence", equiv, [])
    check("the failure names the relation",
          all("l2 = 1 / (C * n_train)" in e["equivalence"] for e in diff), True)

    # The strength #430 found in the benchmark before the fix: 0.001 against
    # C=1.0 on iris, 8.3x weaker than the sklearn model beside it.
    diff, _ = compare_configs({"l2": 0.001}, {"C": 1.0}, IRIS_N_TRAIN)
    check("the pre-#430 mismatch is reported", parameters(diff), ["C", "l2"])

    diff, equiv = compare_configs({"l2": 0.008333333}, {"C": 1.0}, None)
    check("an unknown n_train leaves the conversion unverifiable", parameters(diff), ["C", "l2"])
    check("an unverifiable conversion is not an equivalence", equiv, [])

    diff, equiv = compare_configs({"l2": 0.008333333}, {"C": 1.0}, DIGITS_N_TRAIN)
    check("the wrong dataset's n_train does not verify", parameters(diff), ["C", "l2"])

    # Both sides speak the same vocabulary: compare the values directly.
    diff, equiv = compare_configs({"l2": 0.5, "C": 1.0}, {"C": 1.0, "l2": 0.25}, IRIS_N_TRAIN)
    check("a two-sided l2 is compared directly", parameters(diff), ["l2"])
    check("a two-sided l2 applies no mapping", equiv, [])


def test_absent_equals_explicitly_disabled() -> None:
    print("absent equals explicitly disabled")

    diff, equiv = compare_configs({"penalty": "none"}, {}, None)
    check("penalty=none against nothing reports nothing", diff, [])
    check("penalty=none is recorded", rules(equiv), {"penalty": "absent equals explicitly disabled"})

    diff, _ = compare_configs({"penalty": "l2"}, {}, None)
    check("a penalty that is on is still reported", parameters(diff), ["penalty"])

    diff, _ = compare_configs({"fit_intercept": False}, {}, None)
    check("a false boolean is not an absent knob", parameters(diff), ["fit_intercept"])

    diff, _ = compare_configs({"penalty": "none"}, {"penalty": "l2"}, None)
    check("a two-sided penalty is compared directly", parameters(diff), ["penalty"])


def test_solver_private_parameters() -> None:
    print("solver-private parameters")

    diff, equiv = compare_configs(
        {"optimizer": "lbfgs_no_line_search", "learning_rate": 0.1},
        {"optimizer": "lbfgs"},
        None,
    )
    check("learning_rate against an lbfgs counterpart reports only the optimizer",
          parameters(diff), ["optimizer"])
    check("learning_rate is recorded as solver-private",
          rules(equiv), {"learning_rate": "solver-private parameter"})

    diff, _ = compare_configs(
        {"optimizer": "gradient_descent"},
        {"optimizer": "gradient_descent", "learning_rate": 0.1},
        None,
    )
    check("a solver that does own the knob keeps the omission visible",
          parameters(diff), ["learning_rate"])

    diff, equiv = compare_configs({"C": 1.0}, {"C": 1.0, "dual": "auto"}, None)
    check("dual against a side with no such switch reports nothing", diff, [])
    check("dual is recorded as solver-private", rules(equiv), {"dual": "solver-private parameter"})

    diff, _ = compare_configs({"learning_rate": 0.1}, {"learning_rate": 0.01}, None)
    check("a two-sided learning_rate is compared directly", parameters(diff), ["learning_rate"])

    diff, _ = compare_configs({"max_iter": 1000}, {}, None)
    check("a one-sided max_iter is still reported", parameters(diff), ["max_iter"])

    diff, _ = compare_configs({"max_iter": 200}, {"max_iter": 1000}, None)
    check("a two-sided max_iter mismatch is still reported", parameters(diff), ["max_iter"])
    check("the reported max_iter carries both values",
          diff, [{"parameter": "max_iter", "flow": 200, "sklearn": 1000}])


def test_canonical_contract() -> None:
    """What survives on the real canonical rows."""
    print("canonical parity_contract.json rows")

    contract = json.loads((ROOT / "parity_contract.json").read_text())
    splits = json.loads((ROOT / "split_indices.json").read_text())
    sizes = {name: row["n_train"] for name, row in splits.items()}

    expected = {
        ("LogisticRegression", "iris"): ["max_iter", "optimizer"],
        ("LogisticRegression", "digits"): ["max_iter", "optimizer"],
        ("KernelSVC_RBF", "iris"): ["max_iter"],
        ("PCA", "iris"): ["solver"],
        ("Ridge", "diabetes"): ["max_iter"],
        ("LinearSVC", "iris"): [],
        ("LinearSVC", "digits"): [],
        ("Lasso", "diabetes"): [],
        ("LinearRegression", "diabetes"): [],
    }

    actual = {}
    for row in contract["rows"]:
        diff, _ = compare_configs(row.get("flow", {}), row.get("sklearn", {}),
                                  sizes.get(row["dataset"]))
        key = (row["algorithm"], row["dataset"])
        if key in expected or diff:
            actual[key] = parameters(diff)

    check("surviving configuration differences on the canonical rows", actual, expected)

    unresolved = sum(1 for key, params in actual.items() if params)
    check("rows still carrying a configuration difference", unresolved, 5)


def main() -> int:
    test_cross_vocabulary_mapping()
    test_absent_equals_explicitly_disabled()
    test_solver_private_parameters()
    test_canonical_contract()

    if FAILURES:
        print(f"config equivalence fixtures: FAIL ({len(FAILURES)})")
        for name in FAILURES:
            print(" -", name)
        return 1
    print("config equivalence fixtures: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
