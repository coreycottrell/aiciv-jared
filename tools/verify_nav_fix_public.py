#!/usr/bin/env python3
"""Verify nav fix as a public (not logged in) visitor."""

import sys
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Fresh context - no cookies, not logged in
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        page.set_default_timeout(60000)

        test_pages = [
            ("https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/", "public_single_post"),
            ("https://purebrain.ai/category/for-teams/", "public_category"),
            ("https://purebrain.ai/blog/", "public_blog_index"),
            ("https://purebrain.ai/", "public_homepage"),
            ("https://purebrain.ai/why-ai-memory-changes-everything/", "public_single_post_2"),
        ]

        for url, label in test_pages:
            print(f"\nTesting {label}: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)

            path = f"{SCREENSHOT_DIR}/navpublic_{label}_{TIMESTAMP}.png"
            try:
                page.screenshot(path=path, timeout=60000)
                print(f"  Screenshot: {path}")
            except Exception as e:
                print(f"  Screenshot failed: {e}")

            # Check header/nav
            nav_info = page.evaluate("""
                () => {
                    const header = document.querySelector('header#masthead');
                    const logo = document.querySelector('.navbar-brand img.logo');
                    const body_cls = document.body.className;

                    let headerInfo = null;
                    if (header) {
                        const style = getComputedStyle(header);
                        const rect = header.getBoundingClientRect();
                        headerInfo = {
                            display: style.display,
                            height: Math.round(rect.height),
                            maxHeight: style.maxHeight,
                            visible: rect.height > 0 && style.display !== 'none'
                        };
                    }

                    let logoInfo = null;
                    if (logo) {
                        const rect = logo.getBoundingClientRect();
                        logoInfo = {height: Math.round(rect.height), width: Math.round(rect.width)};
                    }

                    return {
                        header: headerInfo,
                        logo: logoInfo,
                        body_classes: body_cls.substring(0, 150),
                        has_admin_bar: body_cls.includes('admin-bar')
                    };
                }
            """)
            print(f"  Header: {nav_info.get('header')}")
            print(f"  Logo: {nav_info.get('logo')}")
            print(f"  Admin bar: {nav_info.get('has_admin_bar')}")
            print(f"  Classes: {nav_info.get('body_classes')}")

        browser.close()
        print("\nDone!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
