#!/usr/bin/env python3
"""Provenance carried by every artifact derived from the canonical headline result.

A derived artifact records the sha256 of the exact bytes of
headline_result_v2.json it was joined against, plus that result's
environment_id. check_evidence_drift.py rejects any artifact whose recorded
digest differs from the committed result, so an artifact built from an older
result can no longer pass as current. source_commit is an audit coordinate and
is not compared.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "benchmarks" / "headline_result_v2.json"


def result_digest(path: Path = RESULT) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip() or None


def provenance(path: Path = RESULT) -> dict:
    """Provenance block for an artifact joined against the result at ``path``."""
    if not path.exists():
        return {"result_sha256": None, "environment_id": None, "source_commit": source_commit()}
    result = json.loads(path.read_text())
    return {
        "result_sha256": result_digest(path),
        "environment_id": result.get("environment_id"),
        "source_commit": source_commit(),
    }
