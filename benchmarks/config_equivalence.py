#!/usr/bin/env python3
"""Declared equivalences between Flow and scikit-learn configuration vocabularies.

The canonical benchmark records each row's configuration twice, once in Flow's
vocabulary and once in scikit-learn's, in `parity_contract.json`. Comparing the
two dictionaries key by key reports a difference whenever the two projects spell
the same setting differently, whenever one side declares a knob the other's
solver does not have, and whenever one side explicitly turns a feature off that
the other simply lacks. None of those is a configuration difference, and while
they sat in the report the differences that are real were buried in them.

This module holds the equivalences the comparator is allowed to apply. Three
rules, in order:

1. Cross-vocabulary mappings, each verified numerically. `C` on the sklearn side
   and `l2` on the Flow side name the same setting under a conversion, so they
   are equivalent only when the recorded numbers actually satisfy it. A mapping
   that does not hold is still reported, with the expected value attached.
2. Absent against explicitly disabled. A parameter one side records as off and
   the other does not have at all is the same configuration.
3. Solver-private parameters. A knob that belongs to one side's solver and has
   no counterpart in the other's is not comparable.

All three rules apply only to a parameter that appears on exactly one side, or
to a mapped pair each of whose names appears on exactly its own side. When both
sides record the same parameter, the recorded values are compared and any
difference is reported. That is what keeps `max_iter 200 vs 1000` and
`optimizer lbfgs_no_line_search vs lbfgs` visible.

Nothing is discarded: every applied equivalence is returned alongside the
differences so the report can carry it as evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

MISSING = "<missing>"

# Keys under which a row's configuration may name its solver. Used to check that
# a solver-private parameter really is absent from the counterpart's solver
# rather than merely left out of its record.
SOLVER_PARAMETER_KEYS = ("optimizer", "solver")

# String values that declare a feature switched off. `False` is deliberately not
# here: a boolean knob set to false still implies the knob exists, and a boolean
# on one side against nothing on the other is worth looking at.
DISABLED_STRINGS = ("none", "None")

# Relative tolerance for a verified cross-vocabulary conversion.
#
# The contract records converted values rounded to nine significant digits, so
# the recorded 0.000695894 sits 3.2e-07 from the exact 1/1437 it stands for.
# 1e-05 clears that rounding by a decade and a half and still sits far below any
# real mismatch: the disagreement #430 found was 8.3x, not parts per million.
CONVERSION_RELATIVE_TOLERANCE = 1e-5


@dataclass(frozen=True)
class CrossVocabularyMapping:
    """One setting recorded under two names, plus the conversion between them."""

    sklearn_parameter: str
    flow_parameter: str
    # Expected Flow value given the sklearn value and the row's training-set
    # size. Returns None when the inputs cannot produce a conversion.
    convert: Callable[[object, "int | None"], "float | None"]
    relation: str
    why: str


def _alpha_from_c(c_value, n_train):
    """Flow's `l2` strength equivalent to scikit-learn's `C`.

    Established in #430, closing #408. `logistic_regression_fit` minimises
    `(1/m) * sum_i logloss_i + 0.5 * alpha * ||w||^2` while scikit-learn
    minimises `sum_i logloss_i + 0.5 * ||w||^2 / C`. Dividing the second by `m`
    makes the two agree exactly when `alpha = 1 / (C * m)`, so the training-set
    size is part of the conversion and no single constant serves two datasets.
    """
    if n_train is None or n_train <= 0:
        return None
    try:
        c = float(c_value)
    except (TypeError, ValueError):
        return None
    if c <= 0.0:
        return None
    return 1.0 / (c * float(n_train))


CROSS_VOCABULARY_MAPPINGS = (
    CrossVocabularyMapping(
        sklearn_parameter="C",
        flow_parameter="l2",
        convert=_alpha_from_c,
        relation="l2 = 1 / (C * n_train)",
        why=(
            "flow-scikit states regularization as an explicit penalty strength on a "
            "mean-loss objective; scikit-learn states it as the inverse strength C on a "
            "sum-loss objective. #430 derived the conversion and it carries n_train."
        ),
    ),
)


@dataclass(frozen=True)
class SolverPrivateParameter:
    """A knob that exists only for the solver that declares it."""

    parameter: str
    # Solvers that do expose this knob. If the counterpart side names one of
    # these as its solver and still omits the parameter, the omission is a real
    # difference and stays reported.
    owned_by: frozenset
    why: str


SOLVER_PRIVATE_PARAMETERS = {
    entry.parameter: entry
    for entry in (
        SolverPrivateParameter(
            parameter="learning_rate",
            owned_by=frozenset({"gradient_descent", "sgd", "adam"}),
            why=(
                "a step size exists only for a first-order iterative solver. Every "
                "scikit-learn counterpart in the canonical set solves without one: "
                "LogisticRegression uses line-searched lbfgs, Ridge a direct "
                "factorization, Lasso coordinate descent."
            ),
        ),
        SolverPrivateParameter(
            parameter="dual",
            owned_by=frozenset({"liblinear"}),
            why=(
                "scikit-learn's LinearSVC picks between the primal and dual liblinear "
                "formulations. flow-scikit implements one formulation and has no such "
                "switch, so there is nothing on its side for the value to disagree with."
            ),
        ),
    )
}

# `max_iter` is deliberately absent from the table above. scikit-learn's Ridge
# does take a max_iter, and an iteration budget is exactly the kind of setting
# #469 asks to keep visible, so a one-sided max_iter stays reported.


def _declared_solver(config):
    for solver_key in SOLVER_PARAMETER_KEYS:
        value = config.get(solver_key)
        if isinstance(value, str):
            return value
    return None


def _is_disabled(value) -> bool:
    if isinstance(value, bool):
        return False
    if value is None:
        return True
    return isinstance(value, str) and value in DISABLED_STRINGS


def _relative_difference(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


def compare_configs(flow: dict, sklearn: dict, n_train=None):
    """Compare two configuration records under the declared equivalences.

    Returns `(differences, equivalences)`. `differences` keeps the historical
    `{"parameter", "flow", "sklearn"}` shape, sorted by parameter name; entries
    produced by a cross-vocabulary mapping that failed verification carry an
    extra `equivalence` field naming the relation that should have held.
    """
    flow = dict(flow or {})
    sklearn = dict(sklearn or {})
    differences = []
    equivalences = []
    resolved = set()

    # Rule 1: cross-vocabulary mappings, verified numerically.
    for mapping in CROSS_VOCABULARY_MAPPINGS:
        flow_key = mapping.flow_parameter
        sklearn_key = mapping.sklearn_parameter
        # Applies only when each name sits on exactly its own side. If either
        # project also records the other's name the two vocabularies are
        # directly comparable and the plain key comparison below handles them.
        if flow_key in sklearn or sklearn_key in flow:
            continue
        if flow_key not in flow or sklearn_key not in sklearn:
            continue

        flow_value = flow[flow_key]
        sklearn_value = sklearn[sklearn_key]
        expected = mapping.convert(sklearn_value, n_train)
        relative = None
        if expected is not None:
            try:
                relative = _relative_difference(float(flow_value), expected)
            except (TypeError, ValueError):
                relative = None
        holds = relative is not None and relative <= CONVERSION_RELATIVE_TOLERANCE

        resolved.add(flow_key)
        resolved.add(sklearn_key)

        if holds:
            equivalences.append({
                "rule": "cross-vocabulary mapping",
                "parameter": flow_key,
                "flow_parameter": flow_key,
                "flow": flow_value,
                "sklearn_parameter": sklearn_key,
                "sklearn": sklearn_value,
                "relation": mapping.relation,
                "n_train": n_train,
                "expected_flow_value": expected,
                "relative_difference": relative,
                "why": mapping.why,
            })
            continue

        if expected is None:
            note = (
                f"{mapping.relation} could not be evaluated "
                f"(n_train={n_train}, {sklearn_key}={sklearn_value!r})"
            )
        else:
            note = (
                f"{mapping.relation} does not hold: n_train={n_train} and "
                f"{sklearn_key}={sklearn_value!r} give {flow_key}={expected!r}, "
                f"recorded {flow_value!r}"
            )
        differences.append({
            "parameter": flow_key,
            "flow": flow_value,
            "sklearn": MISSING,
            "equivalence": note,
        })
        differences.append({
            "parameter": sklearn_key,
            "flow": MISSING,
            "sklearn": sklearn_value,
            "equivalence": note,
        })

    for key in sorted((set(flow) | set(sklearn)) - resolved):
        flow_value = flow.get(key, MISSING)
        sklearn_value = sklearn.get(key, MISSING)
        if flow_value == sklearn_value:
            continue

        if (key in flow) != (key in sklearn):
            present_side = "flow" if key in flow else "sklearn"
            present_value = flow_value if key in flow else sklearn_value
            counterpart = sklearn if key in flow else flow

            # Rule 2: absent against explicitly disabled.
            if _is_disabled(present_value):
                equivalences.append({
                    "rule": "absent equals explicitly disabled",
                    "parameter": key,
                    "declared_by": present_side,
                    "value": present_value,
                    "why": (
                        f"{present_side} records {key}={present_value!r}, which declares the "
                        "feature off; the other side has no such parameter. Same configuration."
                    ),
                })
                continue

            # Rule 3: solver-private parameters.
            private = SOLVER_PRIVATE_PARAMETERS.get(key)
            if private is not None:
                counterpart_solver = _declared_solver(counterpart)
                if counterpart_solver is None or counterpart_solver not in private.owned_by:
                    equivalences.append({
                        "rule": "solver-private parameter",
                        "parameter": key,
                        "declared_by": present_side,
                        "value": present_value,
                        "counterpart_solver": counterpart_solver,
                        "why": private.why,
                    })
                    continue

        differences.append({"parameter": key, "flow": flow_value, "sklearn": sklearn_value})

    differences.sort(key=lambda entry: entry["parameter"])
    equivalences.sort(key=lambda entry: entry.get("parameter", ""))
    return differences, equivalences
