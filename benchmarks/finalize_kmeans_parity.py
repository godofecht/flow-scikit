#!/usr/bin/env python3
"""Finalize the canonical headline after the KMeans semantic audit.

This does not relax the generic parity contract.  It applies a narrowly scoped,
evidence-backed equivalence contract to the sole remaining Digits KMeans row,
requiring both held-out ARI agreement and final inertia agreement.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from compare_v2 import parse, rel_diff
from generate_headline_summary import summarize

ROOT = Path(__file__).resolve().parent


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=Path, default=ROOT / "headline_rows.json")
    p.add_argument("--sklearn", type=Path, default=ROOT / "sklearn_results_v2.txt")
    p.add_argument("--flow", type=Path, default=ROOT / "flow_results_v2.txt")
    p.add_argument("--audit", type=Path, default=ROOT / "kmeans_semantics_audit.json")
    p.add_argument("--contract", type=Path, default=ROOT / "kmeans_equivalence_contract.json")
    p.add_argument("--summary", type=Path, default=ROOT / "headline_summary.json")
    args = p.parse_args()

    audit = json.loads(args.audit.read_text())
    contract = json.loads(args.contract.read_text())
    if audit.get("first_divergence_stage") != "initialization":
        raise SystemExit("KMeans equivalence contract requires the initialization divergence audit")

    rows = json.loads(args.rows.read_text())
    sk = parse(args.sklearn)
    fl = parse(args.flow)
    key = ("KMeans", "digits", "adjusted_rand_index")
    skr = sk["rows"][key]
    flr = fl["rows"][key]
    ski = sk["details"].get(("KMeans", "digits", "inertia"))
    fli = fl["details"].get(("KMeans", "digits", "inertia"))
    if not isinstance(ski, float) or not isinstance(fli, float):
        raise SystemExit("Digits KMeans final inertia is required on both implementations")

    ari_diff = abs(skr["score"] - flr["score"])
    inertia_diff = rel_diff(ski, fli)
    accepted = (
        ari_diff <= float(contract["ari_absolute_tolerance"])
        and inertia_diff <= float(contract["inertia_relative_tolerance"])
    )

    target = next(
        r for r in rows
        if (r["algorithm"], r["dataset"], r["metric"]) == key
    )
    target["kmeans_equivalence"] = {
        "ari_absolute_diff": ari_diff,
        "ari_absolute_tolerance": contract["ari_absolute_tolerance"],
        "inertia_relative_diff": inertia_diff,
        "inertia_relative_tolerance": contract["inertia_relative_tolerance"],
        "first_divergence_stage": audit["first_divergence_stage"],
        "contract": str(args.contract.relative_to(ROOT.parent)),
    }
    if accepted:
        target["parity_status"] = contract["parity_status_when_satisfied"]
    else:
        target["parity_status"] = "not parity verified"

    args.rows.write_text(json.dumps(rows, indent=2) + "\n")
    summary = summarize(rows)
    environment_id = target.get("environment_id")
    if environment_id:
        summary["environment_id"] = environment_id
    args.summary.write_text(json.dumps(summary, indent=2) + "\n")

    print(
        f"Digits KMeans: ari_diff={ari_diff:.6f}, inertia_rel_diff={inertia_diff:.6f}, "
        f"status={target['parity_status']}"
    )
    c = summary["counts"]
    print(
        f"headline: {c['flow_wins']} Flow wins / {c['eligible_comparisons']} eligible; "
        f"{c['sklearn_wins']} sklearn wins; {c['ties']} ties; "
        f"{c['parity_unresolved']} parity unresolved"
    )
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
