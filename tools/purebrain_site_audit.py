#!/usr/bin/env python3
"""
PureBrain.ai Site Audit - Visual Screenshot Capture
Captures screenshots of key pages across multiple viewports
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
SITE_URL = "https://purebrain.ai"
OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots")

# Viewports to test
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 812},
}

# Pages to capture
PAGES = [
    {"name": "homepage", "path": "/"},
    {"name": "blog-listing", "path": "/blog/"},
]


async def capture_page(page, name, path, viewport_name, viewport):
    """Capture screenshot of a page at specific viewport"""
    url = f"{SITE_URL}{path}"
    filename = f"{name}_{viewport_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = OUTPUT_DIR / filename

    await page.set_viewport_size(viewport)
    print(f"Navigating to {url} ({viewport_name}: {viewport['width']}x{viewport['height']})")

    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)  # Wait for animations to settle

        # Capture full page screenshot
        await page.screenshot(path=str(filepath), full_page=True)
        print(f"  Saved: {filepath}")

        # Also capture above-the-fold
        fold_filename = f"{name}_{viewport_name}_fold.png"
        fold_filepath = OUTPUT_DIR / fold_filename
        await page.screenshot(path=str(fold_filepath), full_page=False)
        print(f"  Saved: {fold_filepath}")

        return str(filepath)
    except Exception as e:
        print(f"  Error capturing {url}: {e}")
        return None


async def measure_performance(page, url):
    """Measure basic page performance metrics"""
    await page.goto(url, wait_until="load")

    metrics = await page.evaluate("""() => {
        const timing = performance.timing;
        const paint = performance.getEntriesByType('paint');
        return {
            loadTime: timing.loadEventEnd - timing.navigationStart,
            domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
            firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || null,
            firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || null,
        };
    }""")

    return metrics


async def check_console_errors(page, url):
    """Capture console errors on page"""
    errors = []
    page.on("console", lambda msg: errors.append({"type": msg.type, "text": msg.text}) if msg.type == "error" else None)

    await page.goto(url, wait_until="networkidle")
    await asyncio.sleep(2)

    return errors


async def analyze_accessibility(page, url):
    """Basic accessibility checks"""
    await page.goto(url, wait_until="networkidle")

    results = await page.evaluate("""() => {
        const checks = {
            hasH1: document.querySelectorAll('h1').length,
            hasMetaViewport: !!document.querySelector('meta[name="viewport"]'),
            hasLangAttr: !!document.documentElement.lang,
            imagesWithoutAlt: Array.from(document.images).filter(img => !img.alt).length,
            linksWithoutText: Array.from(document.querySelectorAll('a')).filter(a => !a.textContent.trim() && !a.getAttribute('aria-label')).length,
            buttonsWithoutLabel: Array.from(document.querySelectorAll('button')).filter(b => !b.textContent.trim() && !b.getAttribute('aria-label')).length,
            formInputsWithoutLabels: Array.from(document.querySelectorAll('input:not([type="hidden"])')).filter(i => !i.getAttribute('aria-label') && !document.querySelector(`label[for="${i.id}"]`)).length,
        };
        return checks;
    }""")

    return results


async def main():
    """Main audit function"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("PureBrain.ai Site Audit - Visual Capture")
    print(f"{'='*60}\n")

    results = {
        "screenshots": [],
        "performance": {},
        "accessibility": {},
        "console_errors": {},
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Capture screenshots
        print("CAPTURING SCREENSHOTS")
        print("-" * 40)
        for page_info in PAGES:
            for viewport_name, viewport in VIEWPORTS.items():
                screenshot_path = await capture_page(
                    page,
                    page_info["name"],
                    page_info["path"],
                    viewport_name,
                    viewport
                )
                if screenshot_path:
                    results["screenshots"].append(screenshot_path)

        # Measure performance
        print("\nMEASURING PERFORMANCE")
        print("-" * 40)
        for page_info in PAGES:
            url = f"{SITE_URL}{page_info['path']}"
            metrics = await measure_performance(page, url)
            results["performance"][page_info["name"]] = metrics
            print(f"{page_info['name']}:")
            print(f"  Load time: {metrics['loadTime']}ms")
            print(f"  DOM ready: {metrics['domReady']}ms")
            print(f"  First paint: {metrics['firstPaint']}ms")
            print(f"  FCP: {metrics['firstContentfulPaint']}ms")

        # Check accessibility
        print("\nACCESSIBILITY CHECKS")
        print("-" * 40)
        for page_info in PAGES:
            url = f"{SITE_URL}{page_info['path']}"
            a11y = await analyze_accessibility(page, url)
            results["accessibility"][page_info["name"]] = a11y
            print(f"{page_info['name']}:")
            for check, value in a11y.items():
                status = "OK" if value == 0 or (check in ['hasH1', 'hasMetaViewport', 'hasLangAttr'] and value) else "ISSUE"
                print(f"  {check}: {value} [{status}]")

        # Check console errors
        print("\nCONSOLE ERRORS")
        print("-" * 40)
        for page_info in PAGES:
            url = f"{SITE_URL}{page_info['path']}"
            errors = await check_console_errors(page, url)
            results["console_errors"][page_info["name"]] = errors
            print(f"{page_info['name']}: {len(errors)} errors")
            for error in errors[:5]:  # Show first 5
                print(f"  - {error['text'][:80]}...")

        await browser.close()

    print(f"\n{'='*60}")
    print("AUDIT COMPLETE")
    print(f"Screenshots saved to: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    asyncio.run(main())
