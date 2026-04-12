#!/usr/bin/env python3
"""Dump the actual live wp-custom-css content to a file for inspection."""
import time
from playwright.sync_api import sync_playwright

JS_CODE = """() => {
    const style = document.querySelector('style#wp-custom-css');
    if (!style) return '';
    return style.textContent;
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto("https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    css = page.evaluate(JS_CODE)

    with open("/tmp/purebrain-live-css.css", "w") as f:
        f.write(css)

    print(f"Saved {len(css)} chars to /tmp/purebrain-live-css.css")
    print(f"Lines: {len(css.splitlines())}")

    # Check specifically around the 'body.single-post a' rule
    lines = css.splitlines()
    for i, line in enumerate(lines):
        if 'body.single-post a' in line and ':hover' not in line and 'a[' not in line and 'a.' not in line and 'a i' not in line and 'a svg' not in line:
            print(f"\nLine {i}: {line}")
            if i+1 < len(lines): print(f"Line {i+1}: {lines[i+1]}")
            if i+2 < len(lines): print(f"Line {i+2}: {lines[i+2]}")

    # Count total rules
    import re
    # Simple count of { } blocks
    rule_count = css.count('{')
    print(f"\nEstimated rule count: {rule_count}")

    # Check if the CSS is truncated
    print(f"\nLast 200 chars: {css[-200:]}")

    browser.close()
