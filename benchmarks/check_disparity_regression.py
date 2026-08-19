#!/usr/bin/env python3
"""Gate disparity regressions between a frozen baseline and the current report.

Two properties this gate has to hold at once:

* A genuine regression must fail. A row whose parity delta grows materially, or
  whose runtime moves materially towards sklearn, is a defect and must be
  visible immediately.
* Nothing else may fail. Every rule here is one-sided and every threshold sits
  above the measured run-to-run and machine-to-machine spread of the metric it
  guards, so a rerun of unchanged code produces the same verdict.

Runtime is wall-clock, so it is only comparable within one measurement host.
`runtime_environment_id` in the report covers CPU and BLAS thread configuration
as well as the software stack; `environment_id` covers only the software stack
and cannot tell two runner machines apart.

A row whose declared implementation contract (`flow` or `sklearn`) changes is
not comparable to its old disparity numbers: the new implementation is expected
to move score, model state and runtime. Such a row gets one baseline reset only
when every gate-defining contract field outside `flow`/`sklearn` is unchanged.
The workflow advances the contract baseline only after this gate and the 19/19
parity gate succeed, so unrelated rows remain protected and tolerance changes do
not create an automatic escape hatch.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def key(row: dict) -> tuple[str, str, str]:
    return row["algorithm"], row["dataset"], row["metric"]


def score_noise_floor(policy: dict, row: dict) -> float:
    """Smallest score delta worth gating for this row."""
    floor = float(policy["score_abs_diff"].get("absolute_noise_floor", 0.0))
    fraction = policy["score_abs_diff"].get("tolerance_fraction_floor")
    if fraction is not None:
        tolerance = row.get("effective_score_tolerance") or row.get("declared_score_tolerance")
        if tolerance:
            floor = max(floor, float(fraction) * float(tolerance))
    return floor


def runtime_limit(policy: dict, same_software_env: bool, same_host: bool) -> tuple[float | None, str]:
    """Return (max tolerated slowdown in log2 units, reason) or (None, reason)."""
    runtime = policy["runtime_log2_ratio"]
    if runtime.get("same_environment_only", True) and not same_software_env:
        return None, "software environment differs from the baseline"
    if same_host:
        limit = runtime.get("max_slowdown_log2", runtime.get("max_absolute_change"))
        return (None if limit is None else float(limit)), "same measurement host"
    limit = runtime.get("cross_environment_max_slowdown_log2")
    return (None if limit is None else float(limit)), "different measurement host"


def implementation_contract_resets(baseline_path: Path, current_path: Path) -> set[tuple[str, str, str]]:
    """Rows allowed to establish a fresh disparity baseline after a real contract change.

    Only `flow` and/or `sklearn` may differ. A tolerance, parity level, timing
    comparability, dataset identity, or any other contract field change disables
    the reset so the normal disparity gate still applies.
    """
    if not baseline_path.exists() or not current_path.exists():
        return set()

    baseline = json.loads(baseline_path.read_text())
    current = json.loads(current_path.read_text())
    old = {key(r): r for r in baseline.get("rows", [])}
    resets: set[tuple[str, str, str]] = set()

    for row in current.get("rows", []):
        row_key = key(row)
        previous = old.get(row_key)
        if previous is None:
            continue

        old_impl = (previous.get("flow"), previous.get("sklearn"))
        new_impl = (row.get("flow"), row.get("sklearn"))
        if old_impl == new_impl:
            continue

        old_guarded = {k: v for k, v in previous.items() if k not in {"flow", "sklearn"}}
        new_guarded = {k: v for k, v in row.items() if k not in {"flow", "sklearn"}}
        if old_guarded == new_guarded:
            resets.add(row_key)

    return resets


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--current", type=Path, default=ROOT / "disparity_report.json")
    p.add_argument("--baseline", type=Path, default=ROOT / "disparity_report.baseline.json")
    p.add_argument("--history", type=Path, default=ROOT / "disparity_history.json")
    p.add_argument("--policy", type=Path, default=ROOT / "disparity_regression_policy.json")
    p.add_argument("--baseline-contract", type=Path, default=ROOT / "parity_contract.baseline.json")
    p.add_argument("--current-contract", type=Path, default=ROOT / "parity_contract.json")
    p.add_argument("--commit", default=os.environ.get("GITHUB_SHA", "unknown"))
    args = p.parse_args()

    current = json.loads(args.current.read_text())
    policy = json.loads(args.policy.read_text())
    failures: list[str] = []
    notices: list[str] = []
    contract_resets = implementation_contract_resets(args.baseline_contract, args.current_contract)

    baseline = None
    if args.baseline.exists():
        baseline = json.loads(args.baseline.read_text())
        old = {key(r): r for r in baseline["rows"]}
        same_env = baseline.get("environment_id") == current.get("environment_id")
        base_host = baseline.get("runtime_environment_id")
        cur_host = current.get("runtime_environment_id")
        same_host = base_host is not None and base_host == cur_host
        limit_rt, host_reason = runtime_limit(policy, same_env, same_host)
        improvement_notice = policy["runtime_log2_ratio"].get("improvement_notice_log2")

        if limit_rt is None:
            notices.append(
                f"runtime comparison skipped ({host_reason}); "
                f"baseline runtime_environment_id={base_host} current={cur_host}"
            )
        else:
            print(
                f"runtime rule: {host_reason}; a row fails when it slows by more than "
                f"{limit_rt:.4g} log2 units ({2 ** limit_rt:.2f}x) relative to sklearn"
            )

        for row in current["rows"]:
            row_key = key(row)
            previous = old.get(row_key)
            if previous is None:
                continue

            if row_key in contract_resets:
                notices.append(
                    f"{row_key} implementation contract changed with gate-defining fields unchanged; "
                    "establishing a fresh disparity baseline for this row"
                )
                continue

            old_frac = previous.get("score_tolerance_fraction")
            new_frac = row.get("score_tolerance_fraction")
            if old_frac is not None and new_frac is not None:
                limit = float(policy["score_tolerance_fraction"]["max_absolute_increase"])
                if new_frac - old_frac > limit:
                    failures.append(f"{row_key} tolerance fraction regressed {old_frac:.6g} -> {new_frac:.6g}")

            old_abs = previous.get("score_abs_diff")
            new_abs = row.get("score_abs_diff")
            if old_abs is not None and new_abs is not None:
                floor = score_noise_floor(policy, row)
                rel = float(policy["score_abs_diff"]["max_relative_increase"])
                if new_abs > max(floor, old_abs * (1.0 + rel)):
                    failures.append(f"{row_key} score |delta| regressed {old_abs:.6g} -> {new_abs:.6g}")

            for field, policy_name in (("configuration_differences", "configuration_difference_count"), ("semantic_differences", "semantic_difference_count")):
                old_n = len(previous.get(field, []))
                new_n = len(row.get(field, []))
                if new_n - old_n > int(policy[policy_name]["max_increase"]):
                    failures.append(f"{row_key} {field} increased {old_n} -> {new_n}")

            old_rt = previous.get("runtime_log2_ratio")
            new_rt = row.get("runtime_log2_ratio")
            if old_rt is None or new_rt is None:
                continue
            change = new_rt - old_rt
            if limit_rt is not None and -change > limit_rt:
                failures.append(
                    f"{row_key} runtime log2 ratio regressed {old_rt:.4f} -> {new_rt:.4f} "
                    f"({2 ** -change:.2f}x slower relative to sklearn)"
                )
            elif improvement_notice is not None and change >= float(improvement_notice):
                notices.append(
                    f"{row_key} runtime log2 ratio improved {old_rt:.4f} -> {new_rt:.4f} "
                    f"({2 ** change:.2f}x faster relative to sklearn); "
                    "re-freeze the baseline on main to keep the gate tight"
                )

    history = {"schema_version": 1, "snapshots": []}
    if args.history.exists():
        history = json.loads(args.history.read_text())
    compact_rows = []
    for row in current["rows"]:
        compact_rows.append({
            "algorithm": row["algorithm"],
            "dataset": row["dataset"],
            "metric": row["metric"],
            "score_abs_diff": row.get("score_abs_diff"),
            "score_tolerance_fraction": row.get("score_tolerance_fraction"),
            "runtime_log2_ratio": row.get("runtime_log2_ratio"),
            "flow_total_ms": row.get("flow_total_ms"),
            "sklearn_total_ms": row.get("sklearn_total_ms"),
            "configuration_difference_count": len(row.get("configuration_differences", [])),
            "semantic_difference_count": len(row.get("semantic_differences", [])),
            "strict_diagnostic_status": row.get("strict_diagnostic_status"),
            "final_parity_status": row.get("final_parity_status"),
        })
    snapshot = {
        "commit": args.commit,
        "environment_id": current.get("environment_id"),
        "runtime_environment_id": current.get("runtime_environment_id"),
        "rows": compact_rows,
    }
    snapshots = [s for s in history.get("snapshots", []) if not (s.get("commit") == snapshot["commit"] and s.get("environment_id") == snapshot["environment_id"])]
    snapshots.append(snapshot)
    history["snapshots"] = snapshots[-50:]
    args.history.write_text(json.dumps(history, indent=2) + "\n")

    if notices:
        print("Disparity notices (not blocking):")
        for notice in notices:
            print(" *", notice)

    if failures:
        print("Disparity regression gate failed:")
        for failure in failures:
            print(" -", failure)
        return 1
    print(f"disparity regression gate passed; history snapshots={len(history['snapshots'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
