#!/usr/bin/env python3
"""
Fix Blog Page Loader Color
Captures the preloader on purebrain.ai/blog and fixes the green to orange/blue

Issue: The loading animation has GREEN arcs that should be ORANGE (#f1420b) and BLUE (#2a93c1)
"""

import sys
import time
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
BLOG_URL = "https://purebrain.ai/blog"
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/blog-loader-fix"

# Brand Colors
ORANGE = "#f1420b"
BLUE = "#2a93c1"

def ensure_screenshot_dir():
    """Create screenshot directory if it doesn't exist"""
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

def take_screenshot(page, name):
    """Take a screenshot with timestamp"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=path)
    print(f"Screenshot saved: {path}")
    return path

async def capture_loader():
    """Capture the blog page loader to see current state"""
    ensure_screenshot_dir()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        print("\n=== CAPTURING BLOG PAGE LOADER ===")

        # Navigate with network throttling to see loader
        print("[1] Navigating to blog page...")

        # Start navigation but capture quickly to see loader
        await page.goto(BLOG_URL, wait_until='domcontentloaded')
        await page.screenshot(path=f"{SCREENSHOT_DIR}/01_initial_load.png")
        print(f"Screenshot: {SCREENSHOT_DIR}/01_initial_load.png")

        # Wait a bit and capture again
        await asyncio.sleep(0.5)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/02_loading.png")
        print(f"Screenshot: {SCREENSHOT_DIR}/02_loading.png")

        # Get the loader HTML
        print("\n[2] Analyzing loader structure...")
        loader_html = await page.evaluate('''() => {
            const selectors = [
                '.theme-preloader',
                '.preloader',
                '.awaiken-preloader',
                '#awaiken-preloader',
                '[class*="preloader"]',
                '[class*="loader"]',
                '.loading',
                '.starter-templates-loader'
            ];

            let results = [];
            for (const sel of selectors) {
                const elements = document.querySelectorAll(sel);
                for (const el of elements) {
                    results.push({
                        selector: sel,
                        outerHTML: el.outerHTML.substring(0, 2000),
                        classes: el.className,
                        id: el.id
                    });
                }
            }
            return results;
        }''')

        print(f"\nFound {len(loader_html)} loader elements:")
        for item in loader_html:
            print(f"\n  Selector: {item['selector']}")
            print(f"  Classes: {item['classes']}")
            print(f"  ID: {item['id']}")
            print(f"  HTML: {item['outerHTML'][:500]}...")

        # Check for SVG elements specifically
        print("\n[3] Checking for SVG loaders...")
        svg_info = await page.evaluate('''() => {
            const svgs = document.querySelectorAll('svg');
            let results = [];
            for (const svg of svgs) {
                const circles = svg.querySelectorAll('circle');
                const paths = svg.querySelectorAll('path');
                if (circles.length > 0 || paths.length > 0) {
                    results.push({
                        outerHTML: svg.outerHTML.substring(0, 1000),
                        parent: svg.parentElement ? svg.parentElement.className : 'none',
                        computedStyle: window.getComputedStyle(svg)
                    });
                }
            }
            return results;
        }''')

        print(f"Found {len(svg_info)} SVG elements with circles/paths")
        for i, svg in enumerate(svg_info[:5]):  # Limit to first 5
            print(f"\n  SVG {i+1}:")
            print(f"    Parent class: {svg['parent']}")
            print(f"    HTML: {svg['outerHTML'][:300]}...")

        # Wait for full page load and capture final state
        await page.wait_for_load_state('networkidle')
        await page.screenshot(path=f"{SCREENSHOT_DIR}/03_loaded.png")
        print(f"\nScreenshot: {SCREENSHOT_DIR}/03_loaded.png")

        # Get all CSS that mentions preloader/loader colors
        print("\n[4] Checking CSS for loader styles...")
        css_info = await page.evaluate('''() => {
            const styleSheets = document.styleSheets;
            let loaderStyles = [];

            for (const sheet of styleSheets) {
                try {
                    const rules = sheet.cssRules || sheet.rules;
                    for (const rule of rules) {
                        if (rule.cssText && (
                            rule.cssText.includes('preloader') ||
                            rule.cssText.includes('loader') ||
                            rule.cssText.includes('loading') ||
                            rule.cssText.includes('spinner')
                        )) {
                            loaderStyles.push(rule.cssText.substring(0, 500));
                        }
                    }
                } catch (e) {
                    // Cross-origin stylesheet
                }
            }
            return loaderStyles;
        }''')

        print(f"Found {len(css_info)} CSS rules related to loaders:")
        for rule in css_info[:20]:  # Limit output
            print(f"  {rule[:200]}...")

        await browser.close()
        print("\n=== CAPTURE COMPLETE ===")
        return True

async def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == 'capture':
        await capture_loader()
    else:
        print("Usage: python fix_blog_loader.py capture")
        print("       python fix_blog_loader.py fix")

if __name__ == "__main__":
    asyncio.run(main())
