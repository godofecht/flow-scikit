#!/usr/bin/env python3
from generate_headline_summary import summarize


def row(**overrides):
    base = {
        "algorithm": "A",
        "dataset": "fixture",
        "flow_ms": 1.0,
        "sklearn_ms": 2.0,
        "timing_unit": "ms",
        "parity_status": "parity verified",
        "measurement_status": "resolved",
        "comparable": True,
        "environment_id": "fixture-env",
    }
    base.update(overrides)
    return base


def main():
    rows = [
        row(algorithm="flow-win"),
        row(algorithm="sklearn-win", flow_ms=2.0, sklearn_ms=1.0),
        row(algorithm="tie", flow_ms=1.0, sklearn_ms=1.01),
        row(algorithm="parity", parity_status="not parity verified"),
        row(algorithm="measurement", flow_ms=0.0),
        row(algorithm="not-comparable", comparable=False),
        row(algorithm="failed", failure_reason="fixture failure"),
    ]
    summary = summarize(rows)
    counts = summary["counts"]
    assert counts == {
        "total_rows": 7,
        "eligible_comparisons": 3,
        "flow_wins": 1,
        "sklearn_wins": 1,
        "ties": 1,
        "parity_unresolved": 1,
        "measurement_unresolved": 1,
        "not_comparable": 1,
        "failed": 1,
    }
    statuses = {r["algorithm"]: r["classification"] for r in summary["rows"]}
    assert statuses["flow-win"] == "flow win"
    assert statuses["sklearn-win"] == "sklearn win"
    assert statuses["tie"] == "tie"
    assert statuses["parity"] == "parity unresolved"
    assert statuses["measurement"] == "measurement unresolved"
    assert statuses["not-comparable"] == "not comparable"
    assert statuses["failed"] == "failed"
    print("headline summary fixture: PASS")


if __name__ == "__main__":
    main()
