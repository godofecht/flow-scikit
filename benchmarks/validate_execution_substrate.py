#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
headline = json.loads((ROOT / "headline_result_v2.json").read_text())
substrates = json.loads((ROOT / "execution_substrate.json").read_text())

headline_algorithms = {row["algorithm"] for row in headline["rows"]}
rows = substrates["rows"]
classified_algorithms = {row["algorithm"] for row in rows}

assert len(rows) == len(classified_algorithms), "duplicate algorithm in execution_substrate.json"
missing = headline_algorithms - classified_algorithms
extra = classified_algorithms - headline_algorithms
assert not missing, f"headline algorithms missing execution-substrate appraisal: {sorted(missing)}"
assert not extra, f"execution-substrate rows absent from headline benchmark: {sorted(extra)}"

valid_substrates = set(substrates["classes"])
valid_dispositions = {
    "compile-whole-estimator",
    "retain-or-beat-native-kernel",
    "replace-sklearn-native-where-justified",
    "fuse-vectorized-pipeline",
    "retain-native-kernel-optimize-around-it",
}
for row in rows:
    assert row["fit_substrate"] in valid_substrates, row
    assert row["predict_substrate"] in valid_substrates, row
    assert row["flow_disposition"] in valid_dispositions, row
    assert row["confidence"] in {"low", "medium", "high"}, row
    assert row["native_dependency"].strip(), row
    assert row["note"].strip(), row

print(f"execution substrate contract: {len(rows)} headline algorithms classified; coverage enforced")
