#!/usr/bin/env python3
"""Check navigation on actual single blog posts."""

import sys
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

SINGLE_POST_URLS = [
    "https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/",
    "https://purebrain.ai/why-ai-memory-changes-everything/",
    "https://purebrain.ai/what-i-actually-do-all-day/",
]


def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        page.set_default_timeout(60000)

        for url in SINGLE_POST_URLS:
            slug = url.rstrip('/').split('/')[-1]
            print(f"\n{'='*60}")
            print(f"Testing: {url}")

            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)

            body_classes = page.evaluate("() => document.body.className")
            print(f"  Body classes (first 300): {body_classes[:300]}")

            # Is it single-post?
            has_single = 'single-post' in body_classes
            has_elementor_canvas = 'elementor-template-canvas' in body_classes
            print(f"  single-post class: {has_single}")
            print(f"  elementor-canvas: {has_elementor_canvas}")

            # Check nav
            nav_check = page.evaluate("""
                () => {
                    const selectors = ['nav', 'header', '.navbar', '#masthead', '.elementor-location-header'];
                    const results = {};
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) {
                            const style = getComputedStyle(el);
                            const rect = el.getBoundingClientRect();
                            results[sel] = {
                                display: style.display,
                                height: Math.round(rect.height),
                                visible: rect.height > 0 && style.display !== 'none'
                            };
                        }
                    }

                    // Find visible nav links
                    const allLinks = document.querySelectorAll('a');
                    const navLinks = [];
                    for (const a of allLinks) {
                        const rect = a.getBoundingClientRect();
                        if (rect.top < 100 && rect.height > 0 && rect.width > 0) {
                            navLinks.push({
                                text: a.textContent.trim().substring(0, 40),
                                href: a.href,
                                top: Math.round(rect.top)
                            });
                        }
                    }
                    results['top_links'] = navLinks.slice(0, 10);

                    return results;
                }
            """)

            for sel, info in nav_check.items():
                if sel == 'top_links':
                    print(f"\n  Links in top 100px:")
                    for link in info:
                        print(f"    [{link.get('top')}px] {link.get('text')}: {link.get('href')}")
                elif isinstance(info, dict):
                    vis = "VISIBLE" if info.get('visible') else "HIDDEN"
                    print(f"    {sel}: {vis} (display={info.get('display')}, h={info.get('height')}px)")

            path = f"{SCREENSHOT_DIR}/navcheck_{slug[:30]}_{TIMESTAMP}.png"
            page.screenshot(path=path, timeout=60000)
            print(f"  Screenshot: {path}")

        browser.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
