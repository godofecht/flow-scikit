#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def key(row: dict) -> tuple[str, str, str]:
    return row["algorithm"], row["dataset"], row["metric"]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--current", type=Path, default=ROOT / "disparity_report.json")
    p.add_argument("--baseline", type=Path, default=ROOT / "disparity_report.baseline.json")
    p.add_argument("--history", type=Path, default=ROOT / "disparity_history.json")
    p.add_argument("--policy", type=Path, default=ROOT / "disparity_regression_policy.json")
    p.add_argument("--commit", default=os.environ.get("GITHUB_SHA", "unknown"))
    args = p.parse_args()

    current = json.loads(args.current.read_text())
    policy = json.loads(args.policy.read_text())
    failures: list[str] = []

    baseline = None
    if args.baseline.exists():
        baseline = json.loads(args.baseline.read_text())
        old = {key(r): r for r in baseline["rows"]}
        same_env = baseline.get("environment_id") == current.get("environment_id")
        for row in current["rows"]:
            previous = old.get(key(row))
            if previous is None:
                continue

            old_frac = previous.get("score_tolerance_fraction")
            new_frac = row.get("score_tolerance_fraction")
            if old_frac is not None and new_frac is not None:
                limit = float(policy["score_tolerance_fraction"]["max_absolute_increase"])
                if new_frac - old_frac > limit:
                    failures.append(f"{key(row)} tolerance fraction regressed {old_frac:.6g} -> {new_frac:.6g}")

            old_abs = previous.get("score_abs_diff")
            new_abs = row.get("score_abs_diff")
            if old_abs is not None and new_abs is not None:
                floor = float(policy["score_abs_diff"]["absolute_noise_floor"])
                rel = float(policy["score_abs_diff"]["max_relative_increase"])
                if new_abs > max(floor, old_abs * (1.0 + rel)):
                    failures.append(f"{key(row)} score |delta| regressed {old_abs:.6g} -> {new_abs:.6g}")

            for field, policy_name in (("configuration_differences", "configuration_difference_count"), ("semantic_differences", "semantic_difference_count")):
                old_n = len(previous.get(field, []))
                new_n = len(row.get(field, []))
                if new_n - old_n > int(policy[policy_name]["max_increase"]):
                    failures.append(f"{key(row)} {field} increased {old_n} -> {new_n}")

            if same_env or not policy["runtime_log2_ratio"].get("same_environment_only", True):
                old_rt = previous.get("runtime_log2_ratio")
                new_rt = row.get("runtime_log2_ratio")
                if old_rt is not None and new_rt is not None:
                    limit = float(policy["runtime_log2_ratio"]["max_absolute_change"])
                    if abs(new_rt - old_rt) > limit:
                        failures.append(f"{key(row)} runtime log2 ratio changed {old_rt:.4f} -> {new_rt:.4f}")

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
            "configuration_difference_count": len(row.get("configuration_differences", [])),
            "semantic_difference_count": len(row.get("semantic_differences", [])),
            "strict_diagnostic_status": row.get("strict_diagnostic_status"),
            "final_parity_status": row.get("final_parity_status"),
        })
    snapshot = {
        "commit": args.commit,
        "environment_id": current.get("environment_id"),
        "rows": compact_rows,
    }
    snapshots = [s for s in history.get("snapshots", []) if not (s.get("commit") == snapshot["commit"] and s.get("environment_id") == snapshot["environment_id"])]
    snapshots.append(snapshot)
    history["snapshots"] = snapshots[-50:]
    args.history.write_text(json.dumps(history, indent=2) + "\n")

    if failures:
        print("Disparity regression gate failed:")
        for failure in failures:
            print(" -", failure)
        return 1
    print(f"disparity regression gate passed; history snapshots={len(history['snapshots'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
