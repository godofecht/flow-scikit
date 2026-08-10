#!/usr/bin/env python3
"""Record real Flow/WASM browser experiments as small documentation GIFs."""

from pathlib import Path
import sys

from PIL import Image
from playwright.sync_api import sync_playwright


RECORDINGS = [("home-price", 0), ("delivery-eta", 4), ("quality-check", 7)]


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: record_browser_demos.py <base-url> <output-directory>", file=sys.stderr)
        return 2
    base_url, output_dir = sys.argv[1], Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        page.goto(f"{base_url}/demos.html", wait_until="networkidle")
        for name, index in RECORDINGS:
            card = page.locator(".visual-card").nth(index)
            card.scroll_into_view_if_needed()
            box = card.bounding_box()
            canvas = card.locator("canvas")
            canvas_box = canvas.bounding_box()
            frames = []
            for fraction in (0.16, 0.38, 0.64, 0.86):
                page.mouse.click(canvas_box["x"] + canvas_box["width"] * fraction, canvas_box["y"] + canvas_box["height"] * 0.48)
                page.wait_for_timeout(200)
                data = page.screenshot(clip=box)
                import io
                frames.append(Image.open(io.BytesIO(data)).convert("P", palette=Image.Palette.ADAPTIVE))
            frames[0].save(output_dir / f"{name}.gif", save_all=True, append_images=frames[1:], duration=850, loop=0, optimize=False)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
