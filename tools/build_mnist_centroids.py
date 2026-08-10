#!/usr/bin/env python3
"""Build a compact nearest-centroid MNIST model for the static browser demo.

Download the original MNIST IDX gzip files first, then run:
  python tools/build_mnist_centroids.py <images.gz> <labels.gz> <output.json>
"""

from __future__ import annotations

import gzip
import json
import struct
import sys
from pathlib import Path

import numpy as np


def read_images(path: Path) -> np.ndarray:
    with gzip.open(path, "rb") as source:
        magic, count, rows, columns = struct.unpack(">IIII", source.read(16))
        if magic != 2051 or rows != 28 or columns != 28:
            raise ValueError("expected MNIST 28x28 image IDX data")
        return np.frombuffer(source.read(), dtype=np.uint8).reshape(count, rows * columns)


def read_labels(path: Path) -> np.ndarray:
    with gzip.open(path, "rb") as source:
        magic, count = struct.unpack(">II", source.read(8))
        if magic != 2049:
            raise ValueError("expected MNIST label IDX data")
        return np.frombuffer(source.read(), dtype=np.uint8).reshape(count)


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    images = read_images(Path(sys.argv[1])).astype(np.float32) / 255.0
    labels = read_labels(Path(sys.argv[2]))
    if len(images) != len(labels):
        raise ValueError("image and label counts do not match")

    centroids = np.stack([images[labels == digit].mean(axis=0) for digit in range(10)])
    payload = {
        "format": "flow-scikit-mnist-centroids-v1",
        "training_examples": int(len(images)),
        "image_shape": [28, 28],
        "classifier": "nearest centroid (squared Euclidean distance)",
        "centroids": centroids.round(6).tolist(),
    }
    Path(sys.argv[3]).write_text(json.dumps(payload, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
