#!/usr/bin/env python3
"""Quick verification of blog navigation fix - test pages without login."""

import sys
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

TEST_PAGES = [
    ("https://purebrain.ai/blog/", "blog_index"),
    ("https://purebrain.ai/", "homepage"),
    ("https://purebrain.ai/category/for-teams/", "category_for_teams"),
    # Test a single blog post - find one from the blog
    ("https://purebrain.ai/ceo-vs-employee-the-two-lenses-on-ai-transformation/", "single_post"),
]


def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    print(f"Blog Navigation Fix Verification - {datetime.now()}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        page.set_default_timeout(60000)

        for url, label in TEST_PAGES:
            print(f"\n{'='*40}")
            print(f"Testing: {label}")
            print(f"URL: {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(5)
            except Exception as e:
                print(f"  Failed to load: {e}")
                continue

            # Screenshot
            path = f"{SCREENSHOT_DIR}/navverify_{label}_{TIMESTAMP}.png"
            try:
                page.screenshot(path=path, timeout=60000)
                print(f"  Screenshot: {path}")
            except:
                print(f"  Screenshot failed")

            # Check body classes
            body_classes = page.evaluate("() => document.body.className")
            print(f"  Body classes: {body_classes[:200]}")

            # Check nav visibility
            nav_check = page.evaluate("""
                () => {
                    const results = {};
                    const selectors = [
                        'nav', 'header', '.navbar', '.site-header',
                        '.main-navigation', '.elementor-location-header',
                        '.ehf-header', '#masthead', '#site-navigation',
                        '.nav-menu', '.menu-toggle', '.primary-menu'
                    ];
                    for (const sel of selectors) {
                        const els = document.querySelectorAll(sel);
                        if (els.length > 0) {
                            const el = els[0];
                            const style = getComputedStyle(el);
                            const rect = el.getBoundingClientRect();
                            results[sel] = {
                                display: style.display,
                                visibility: style.visibility,
                                opacity: parseFloat(style.opacity),
                                height: rect.height,
                                visible: rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden',
                                tagName: el.tagName,
                                id: el.id || '',
                                classes: el.className.substring(0, 100)
                            };
                        }
                    }

                    // Also check for any visible navigation links
                    const navLinks = document.querySelectorAll('nav a, header a, .navbar a, .menu a, .nav-menu a');
                    const visibleLinks = [];
                    navLinks.forEach(link => {
                        const rect = link.getBoundingClientRect();
                        const style = getComputedStyle(link);
                        if (rect.height > 0 && rect.width > 0 && style.display !== 'none' && style.visibility !== 'hidden') {
                            visibleLinks.push({
                                text: link.textContent.trim().substring(0, 50),
                                href: link.href
                            });
                        }
                    });
                    results['visible_nav_links'] = visibleLinks.slice(0, 10);

                    return results;
                }
            """)

            print(f"\n  Nav element check:")
            for sel, info in nav_check.items():
                if sel == 'visible_nav_links':
                    print(f"\n  Visible navigation links ({len(info)}):")
                    for link in info:
                        print(f"    - {link.get('text', '?')}: {link.get('href', '?')}")
                else:
                    visible = info.get('visible', False)
                    marker = "VISIBLE" if visible else "HIDDEN"
                    print(f"    {sel}: {marker} (display={info.get('display')}, h={info.get('height', 0):.0f}px)")

        browser.close()
        print(f"\n{'='*60}")
        print("Verification complete!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
