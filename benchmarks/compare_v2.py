#!/usr/bin/env python3
"""Compare canonical Flow/sklearn headline artifacts under parity_contract.json."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from generate_headline_summary import summarize

ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "parity_contract.json"


def _number_or_list(raw: str):
    if "," in raw:
        return [float(v) for v in raw.split(",") if v]
    try:
        return float(raw)
    except ValueError:
        return raw


def parse(path: Path) -> dict:
    out = {
        "unit": None,
        "mode": None,
        "fixture": None,
        "environment": None,
        "rows": {},
        "details": {},
    }
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("TIMING_UNIT|"):
            out["unit"] = line.split("|", 1)[1]
        elif line.startswith("BENCHMARK_MODE|"):
            out["mode"] = line.split("|", 1)[1]
        elif line.startswith("FIXTURE_SOURCE|"):
            out["fixture"] = line.split("|", 1)[1]
        elif line.startswith("BENCHMARK_ENV|"):
            out["environment"] = line.split("|", 1)[1]
        elif line.startswith("RESULT|"):
            p = line.split("|")
            if len(p) < 7:
                raise ValueError(f"{path}: malformed result line: {line}")
            key = (p[1], p[2], p[3])
            row = {
                "algorithm": p[1],
                "dataset": p[2],
                "metric": p[3],
                "score": float(p[4]),
                "fit_ms": float(p[5]),
                "pred_ms": float(p[6]),
                "fit_iqr_ms": float(p[7]) if len(p) > 7 else None,
                "pred_iqr_ms": float(p[8]) if len(p) > 8 else None,
                "fit_repeats": int(p[9]) if len(p) > 9 else None,
                "pred_repeats": int(p[10]) if len(p) > 10 else None,
            }
            out["rows"][key] = row
        elif line.startswith("DETAIL|"):
            p = line.split("|", 4)
            if len(p) != 5:
                raise ValueError(f"{path}: malformed detail line: {line}")
            out["details"][(p[1], p[2], p[3])] = _number_or_list(p[4])
    return out


def rel_diff(a: float, b: float) -> float:
    denom = max(abs(a), abs(b), 1e-12)
    return abs(a - b) / denom


def list_abs_diff(a, b) -> float:
    if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b):
        return math.inf
    return max((abs(x - y) for x, y in zip(a, b)), default=0.0)


def list_rel_diff(a, b) -> float:
    if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b):
        return math.inf
    return max((rel_diff(x, y) for x, y in zip(a, b)), default=0.0)


def signed_component_diff(a, b) -> float:
    if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b):
        return math.inf
    same = max((abs(x - y) for x, y in zip(a, b)), default=0.0)
    flipped = max((abs(x + y) for x, y in zip(a, b)), default=0.0)
    return min(same, flipped)


def parity_status(contract: dict, sk: dict, fl: dict, sk_details: dict, fl_details: dict):
    score_diff = abs(sk["score"] - fl["score"])
    diagnostics = {"score_abs_diff": score_diff}
    if score_diff > float(contract["score_abs_tolerance"]):
        return "not parity verified", diagnostics

    algo = contract["algorithm"]
    dataset = contract["dataset"]

    if algo == "KMeans":
        ski = sk_details.get((algo, dataset, "inertia"))
        fli = fl_details.get((algo, dataset, "inertia"))
        if not isinstance(ski, float) or not isinstance(fli, float):
            diagnostics["missing_detail"] = "inertia"
            return "not parity verified", diagnostics
        inertia_diff = rel_diff(ski, fli)
        diagnostics["inertia_relative_diff"] = inertia_diff
        if inertia_diff > float(contract["inertia_relative_tolerance"]):
            return "not parity verified", diagnostics

    if algo == "PCA":
        ev_sk = sk_details.get((algo, dataset, "explained_variance_ratio"))
        ev_fl = fl_details.get((algo, dataset, "explained_variance_ratio"))
        sv_sk = sk_details.get((algo, dataset, "singular_values"))
        sv_fl = fl_details.get((algo, dataset, "singular_values"))
        mse_sk = sk_details.get((algo, dataset, "reconstruction_mse"))
        mse_fl = fl_details.get((algo, dataset, "reconstruction_mse"))
        c0_sk = sk_details.get((algo, dataset, "component_0"))
        c0_fl = fl_details.get((algo, dataset, "component_0"))
        c1_sk = sk_details.get((algo, dataset, "component_1"))
        c1_fl = fl_details.get((algo, dataset, "component_1"))
        diagnostics.update({
            "explained_variance_ratio_abs_diff": list_abs_diff(ev_sk, ev_fl),
            "singular_values_relative_diff": list_rel_diff(sv_sk, sv_fl),
            "reconstruction_mse_abs_diff": abs(float(mse_sk) - float(mse_fl)) if isinstance(mse_sk, float) and isinstance(mse_fl, float) else math.inf,
            "component_0_sign_aligned_abs_diff": signed_component_diff(c0_sk, c0_fl),
            "component_1_sign_aligned_abs_diff": signed_component_diff(c1_sk, c1_fl),
        })
        if diagnostics["explained_variance_ratio_abs_diff"] > float(contract["score_abs_tolerance"]):
            return "not parity verified", diagnostics
        if diagnostics["singular_values_relative_diff"] > float(contract["singular_value_relative_tolerance"]):
            return "not parity verified", diagnostics
        if diagnostics["reconstruction_mse_abs_diff"] > float(contract["reconstruction_mse_abs_tolerance"]):
            return "not parity verified", diagnostics
        component_tol = float(contract["component_abs_tolerance_after_sign_alignment"])
        if diagnostics["component_0_sign_aligned_abs_diff"] > component_tol or diagnostics["component_1_sign_aligned_abs_diff"] > component_tol:
            return "not parity verified", diagnostics

    if contract["parity_level"] == "verified":
        return "parity verified", diagnostics
    return "approximately equivalent", diagnostics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sklearn", type=Path, default=ROOT / "sklearn_results_v2.txt")
    parser.add_argument("--flow", type=Path, default=ROOT / "flow_results_v2.txt")
    parser.add_argument("--rows-output", type=Path, default=ROOT / "headline_rows.json")
    parser.add_argument("--summary-output", type=Path, default=ROOT / "headline_summary.json")
    parser.add_argument("--diagnostics-output", type=Path, default=ROOT / "parity_diagnostics.json")
    parser.add_argument("--environment-id", default=None)
    args = parser.parse_args()

    sk = parse(args.sklearn)
    fl = parse(args.flow)
    if sk["unit"] != "ms" or fl["unit"] != "ms":
        raise SystemExit(f"both benchmark artifacts must declare TIMING_UNIT|ms; got {sk['unit']!r}/{fl['unit']!r}")
    if sk["mode"] != fl["mode"]:
        raise SystemExit(f"benchmark mode mismatch: {sk['mode']!r} vs {fl['mode']!r}")

    contract_doc = json.loads(CONTRACT_PATH.read_text())
    contracts = {(r["algorithm"], r["dataset"], r["metric"]): r for r in contract_doc["rows"]}
    rows = []
    diagnostics = []

    for key, contract in contracts.items():
        skr = sk["rows"].get(key)
        flr = fl["rows"].get(key)
        if skr is None or flr is None:
            rows.append({
                "algorithm": key[0], "dataset": key[1], "metric": key[2],
                "flow_ms": 0.0, "sklearn_ms": 0.0, "timing_unit": "ms",
                "parity_status": "not parity verified", "measurement_status": "failed",
                "comparable": bool(contract.get("timing_comparable", True)),
                "failure_reason": "missing benchmark row",
                "environment_id": args.environment_id,
            })
            continue

        status, diag = parity_status(contract, skr, flr, sk["details"], fl["details"])
        sk_ms = skr["fit_ms"] + skr["pred_ms"]
        fl_ms = flr["fit_ms"] + flr["pred_ms"]
        measurement_status = "resolved" if sk_ms > 0 and fl_ms > 0 else "unresolved"
        row = {
            "algorithm": key[0],
            "dataset": key[1],
            "metric": key[2],
            "category": contract["category"],
            "sklearn_score": skr["score"],
            "flow_score": flr["score"],
            "sklearn_fit_ms": skr["fit_ms"],
            "sklearn_pred_ms": skr["pred_ms"],
            "flow_fit_ms": flr["fit_ms"],
            "flow_pred_ms": flr["pred_ms"],
            "sklearn_fit_iqr_ms": skr["fit_iqr_ms"],
            "sklearn_pred_iqr_ms": skr["pred_iqr_ms"],
            "flow_fit_iqr_ms": flr["fit_iqr_ms"],
            "flow_pred_iqr_ms": flr["pred_iqr_ms"],
            "sklearn_ms": sk_ms,
            "flow_ms": fl_ms,
            "timing_unit": "ms",
            "benchmark_mode": sk["mode"],
            "fixture_source": "benchmarks/split_indices.json + split_*.bin",
            "parity_status": status,
            "measurement_status": measurement_status,
            "comparable": bool(contract.get("timing_comparable", True)),
            "environment_id": args.environment_id,
        }
        rows.append(row)
        diagnostics.append({"algorithm": key[0], "dataset": key[1], "metric": key[2], "parity_status": status, **diag})

    args.rows_output.write_text(json.dumps(rows, indent=2) + "\n")
    summary = summarize(rows)
    if args.environment_id:
        summary["environment_id"] = args.environment_id
    args.summary_output.write_text(json.dumps(summary, indent=2) + "\n")
    args.diagnostics_output.write_text(json.dumps(diagnostics, indent=2) + "\n")

    c = summary["counts"]
    print(f"headline: {c['flow_wins']} Flow wins / {c['eligible_comparisons']} eligible; {c['ties']} ties; {c['parity_unresolved']} parity unresolved; {c['measurement_unresolved']} measurement unresolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
