#!/usr/bin/env python3
"""Verify Flow binary split fixtures exactly match canonical JSON indices."""
from __future__ import annotations

import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent


def read_binary(path: Path):
    raw = path.read_bytes()
    if len(raw) < 8 or (len(raw) - 8) % 4:
        raise ValueError(f"{path}: malformed fixture size")
    n_train, n_test = struct.unpack_from("<ii", raw, 0)
    indices = list(struct.unpack_from(f"<{n_train + n_test}i", raw, 8))
    return n_train, n_test, indices[:n_train], indices[n_train:]


def main() -> int:
    canonical = json.loads((ROOT / "split_indices.json").read_text())
    for dataset in ("iris", "digits", "diabetes"):
        n_train, n_test, train, test = read_binary(ROOT / f"split_{dataset}.bin")
        expected = canonical[dataset]
        assert n_train == expected["n_train"], (dataset, n_train, expected["n_train"])
        assert n_test == expected["n_test"], (dataset, n_test, expected["n_test"])
        assert train == expected["train_idx"], f"{dataset}: binary train indices differ from JSON"
        assert test == expected["test_idx"], f"{dataset}: binary test indices differ from JSON"
        print(f"{dataset}: JSON/binary fixture parity OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
