#!/usr/bin/env python3
"""Record real Flow/WASM browser experiments as small documentation GIFs."""

from pathlib import Path
import sys

from PIL import Image
from playwright.sync_api import sync_playwright


RECORDINGS = [
    ("home-price", "#home-area", [45, 85, 130, 185], "#home-area"),
    ("delivery-eta", "#eta-distance", [4, 12, 28, 55], "#eta-distance"),
    ("quality-check", "#quality-measured", [92, 100, 106, 118], "#quality-measured"),
]


def set_value(page, selector, value):
    page.locator(selector).evaluate(
        "(element, value) => { element.value = value; element.dispatchEvent(new Event('input', { bubbles: true })); }",
        str(value),
    )


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
        for name, selector, values, card_selector in RECORDINGS:
            card = page.locator(selector).locator("xpath=ancestor::article")
            card.scroll_into_view_if_needed()
            box = card.bounding_box()
            frames = []
            for value in values:
                set_value(page, selector, value)
                page.wait_for_timeout(200)
                data = page.screenshot(clip=box)
                import io
                frames.append(Image.open(io.BytesIO(data)).convert("P", palette=Image.Palette.ADAPTIVE))
            frames[0].save(output_dir / f"{name}.gif", save_all=True, append_images=frames[1:], duration=850, loop=0, optimize=False)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
