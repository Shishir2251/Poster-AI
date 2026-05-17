"""
html_renderer.py
Renders an HTML string to a PNG using Playwright.
"""

import io
from playwright.sync_api import sync_playwright


def render_html_to_png(html: str, width: int = 1024, height: int = 1024) -> bytes:
    """
    Takes a complete HTML string, renders it in a headless Chromium browser,
    and returns the screenshot as PNG bytes.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = browser.new_page(viewport={"width": width, "height": height})

        # Set content and wait for Google Fonts + images to load
        page.set_content(html, wait_until="networkidle")

        # Extra wait to ensure fonts are rendered (Hebrew fonts can be slow)
        page.wait_for_timeout(800)

        screenshot_bytes = page.screenshot(
            type="png",
            clip={"x": 0, "y": 0, "width": width, "height": height}
        )
        browser.close()

    return screenshot_bytes