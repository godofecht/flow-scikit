#!/usr/bin/env python3
"""Create the short, labelled demo GIFs used by the static docs gallery."""

from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEMOS = [
    ("classification-boundary", "Sort support tickets", "Route billing, bug, and access requests"),
    ("logistic-confidence", "Flag risky payments", "Send uncertain cases to human review"),
    ("linear-regression", "Forecast energy use", "Estimate tomorrow's building demand"),
    ("ridge-path", "Price used homes", "Keep noisy listing features under control"),
    ("preprocessing-scale", "Score loan applicants", "Make income and debt comparable"),
    ("onehot-encode", "Predict delivery delays", "Turn carrier and route names into features"),
    ("imputation", "Clean sensor readings", "Repair gaps before the model sees them"),
    ("kmeans", "Group customer behaviour", "Find useful segments without labels"),
    ("dbscan", "Spot GPS anomalies", "Keep dense trips, flag isolated points"),
    ("pca", "Explore lab results", "Compress many correlated measurements"),
    ("tsne", "Inspect product embeddings", "See which items sit near each other"),
    ("decision-tree", "Explain account churn", "Turn patterns into readable rules"),
    ("random-forest", "Predict equipment faults", "Combine many weak signals robustly"),
    ("svm-margin", "Check visual defects", "Separate pass and fail with a margin"),
    ("grid-search", "Tune a spam filter", "Compare settings instead of guessing"),
    ("cross-validation", "Validate a small dataset", "Use every row for an honest check"),
    ("calibration", "Prioritise safety reviews", "Make a 70% score mean roughly 70%"),
    ("feature-selection", "Simplify a health model", "Keep the measurements that add signal"),
    ("gaussian-mixture", "Find audience overlap", "Allow a customer to fit more than one group"),
    ("neural-network", "Recognise handwritten digits", "Learn a non-linear image pattern"),
]

NAVY = "#0c1730"
PAPER = "#f8f2e7"
INDIGO = "#5669e8"
CYAN = "#54b6d3"
CORAL = "#ef8068"
MUTED = "#9eabc6"


def font(size: int, bold: bool = False):
    name = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
    return ImageFont.truetype(name, size)


def draw_scatter(draw: ImageDraw.ImageDraw, step: int, index: int) -> None:
    for point in range(26):
        x = 48 + ((point * 59 + index * 23) % 360)
        y = 84 + ((point * 37 + index * 11) % 136)
        offset = math.sin((step + point) / 6) * 10
        color = (INDIGO, CYAN, CORAL)[point % 3]
        radius = 4 + (point % 3)
        draw.ellipse((x - radius, y + offset - radius, x + radius, y + offset + radius), fill=color)
    if index % 4 == 0:
        x = 35 + step * 11
        draw.line((x, 82, x + 80, 222), fill=CORAL, width=3)


def draw_line(draw: ImageDraw.ImageDraw, step: int, index: int) -> None:
    draw.line((45, 222, 450, 222), fill="#52617f", width=1)
    draw.line((45, 222, 45, 76), fill="#52617f", width=1)
    points = []
    for x in range(50, 451, 16):
        y = 190 - (x - 50) * (0.16 + index % 3 * 0.015) + math.sin((x + step * 9) / 35) * 10
        points.append((x, y))
    draw.line(points, fill=CYAN, width=4)
    current = min(len(points), 3 + step)
    for x, y in points[:current:2]:
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=CORAL)


def draw_grid(draw: ImageDraw.ImageDraw, step: int, index: int) -> None:
    for col in range(6):
        for row in range(4):
            x, y = 58 + col * 63, 91 + row * 32
            active = (col * 3 + row + step // 3 + index) % 7 < 3
            draw.rounded_rectangle((x, y, x + 46, y + 20), radius=4, fill=INDIGO if active else "#26395f")
    draw.line((58, 238, 421, 238), fill=CORAL, width=max(2, step // 4))


def draw_tree(draw: ImageDraw.ImageDraw, step: int, index: int) -> None:
    root = (250, 86)
    nodes = [root, (145, 140), (355, 140), (95, 202), (195, 202), (305, 202), (405, 202)]
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
    for edge_index, (left, right) in enumerate(edges):
        active = edge_index <= step // 5
        draw.line((nodes[left], nodes[right]), fill=CYAN if active else "#31405d", width=3)
    for node_index, (x, y) in enumerate(nodes):
        color = CORAL if node_index <= step // 5 else INDIGO
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=color)


def draw_bars(draw: ImageDraw.ImageDraw, step: int, index: int) -> None:
    for bar in range(10):
        x = 55 + bar * 39
        height = 35 + ((bar * 31 + index * 17 + step * 4) % 110)
        color = CORAL if bar == (step // 4 + index) % 10 else CYAN
        draw.rounded_rectangle((x, 226 - height, x + 23, 226), radius=4, fill=color)


DRAWERS = [draw_scatter, draw_line, draw_grid, draw_tree, draw_bars]


def make_demo(slug: str, title: str, detail: str, index: int, output_dir: Path) -> None:
    frames = []
    for step in range(30):
        image = Image.new("RGB", (480, 270), NAVY)
        draw = ImageDraw.Draw(image)
        draw.text((28, 22), f"FLOW-SCIKIT / {index + 1:02d}", font=font(10, True), fill=MUTED)
        draw.text((28, 39), title, font=font(26, True), fill=PAPER)
        draw.text((29, 70), detail, font=font(13), fill="#c8d4ed")
        DRAWERS[index % len(DRAWERS)](draw, step, index)
        draw.text((29, 244), "flow-scikit example", font=font(10), fill="#8392b0")
        frames.append(image)
    frames[0].save(output_dir / f"{slug}.gif", save_all=True, append_images=frames[1:], duration=65, loop=0, optimize=True, disposal=2)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: generate_demo_gifs.py <output-directory>", file=sys.stderr)
        return 2
    output_dir = Path(sys.argv[1])
    output_dir.mkdir(parents=True, exist_ok=True)
    for index, (slug, title, detail) in enumerate(DEMOS):
        make_demo(slug, title, detail, index, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
