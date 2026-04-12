#!/usr/bin/env python3
"""
Comprehensive PureBrain Orange Styling Audit
Takes screenshots of entire site, modals, hover states
Saves to /tmp/purebrain-comprehensive-audit-*.png
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOT_DIR = "/tmp"
SCREENSHOT_PREFIX = "purebrain-comprehensive-audit"

async def save_screenshot(page, label):
    """Save screenshot with timestamp and label"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOT_PREFIX}-{timestamp}-{label}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    await page.screenshot(path=filepath, full_page=False)
    print(f"Saved: {filepath}")
    return filepath

async def audit_purebrain():
    """Main audit function"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)  # 60 second timeout

        print("=" * 60)
        print("PUREBRAIN COMPREHENSIVE ORANGE STYLING AUDIT")
        print("=" * 60)

        # Navigate to site
        print("\n[1] Loading PureBrain.ai...")
        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)  # Wait for dynamic content

        screenshots = []

        # Screenshot 1: Above the fold
        screenshots.append(await save_screenshot(page, "01-hero-above-fold"))

        # Screenshot 2: Scroll to features section
        print("\n[2] Scrolling to features section...")
        await page.evaluate("window.scrollTo(0, 800)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "02-features-section"))

        # Screenshot 3: Continue scrolling
        print("\n[3] Scrolling to next section...")
        await page.evaluate("window.scrollTo(0, 1600)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "03-mid-section"))

        # Screenshot 4: More sections
        print("\n[4] Scrolling further...")
        await page.evaluate("window.scrollTo(0, 2400)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "04-mid-section-2"))

        # Screenshot 5: Continue
        print("\n[5] More scrolling...")
        await page.evaluate("window.scrollTo(0, 3200)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "05-lower-section"))

        # Screenshot 6: Continue
        print("\n[6] More scrolling...")
        await page.evaluate("window.scrollTo(0, 4000)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "06-lower-section-2"))

        # Screenshot 7: Near footer
        print("\n[7] Scrolling to footer area...")
        await page.evaluate("window.scrollTo(0, 4800)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "07-footer-area"))

        # Screenshot 8: Bottom of page
        print("\n[8] Scrolling to bottom...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "08-footer"))

        # Go back to top and find waitlist/popup trigger
        print("\n[9] Looking for waitlist/popup triggers...")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Try to find and click CTA buttons that might open modal
        cta_selectors = [
            "text=Get Started",
            "text=Join Waitlist",
            "text=Start Free",
            "text=Try Now",
            "text=Contact",
            "button:has-text('Start')",
            "a:has-text('Waitlist')",
            ".cta-button",
            "[data-elementor-type='popup']",
        ]

        modal_found = False
        for selector in cta_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=1000):
                    print(f"  Found CTA: {selector}")
                    await element.click()
                    await asyncio.sleep(2)
                    screenshots.append(await save_screenshot(page, "09-modal-or-popup"))
                    modal_found = True

                    # Try to close modal by clicking outside or escape
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(0.5)
                    break
            except:
                continue

        if not modal_found:
            print("  No modal/popup found via CTAs")

        # Look for form elements and test hover states
        print("\n[10] Testing hover states on buttons...")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Find all buttons and hover
        buttons = await page.locator("button, .elementor-button, a.btn, .cta").all()
        print(f"  Found {len(buttons)} buttons/CTAs")

        for i, btn in enumerate(buttons[:5]):  # First 5 buttons
            try:
                if await btn.is_visible():
                    await btn.hover()
                    await asyncio.sleep(0.5)
                    screenshots.append(await save_screenshot(page, f"10-button-hover-{i+1}"))
            except:
                continue

        # Look for form and check labels
        print("\n[11] Looking for forms with labels...")
        form_elements = await page.locator("form, .elementor-form").all()
        print(f"  Found {len(form_elements)} forms")

        for i, form in enumerate(form_elements[:3]):
            try:
                if await form.is_visible():
                    # Scroll form into view
                    await form.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    screenshots.append(await save_screenshot(page, f"11-form-{i+1}"))
            except:
                continue

        # Look for navigation and hover on nav items
        print("\n[12] Testing navigation hover states...")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        nav_items = await page.locator("nav a, .menu-item a, header a").all()
        print(f"  Found {len(nav_items)} nav items")

        for i, nav in enumerate(nav_items[:8]):
            try:
                if await nav.is_visible():
                    await nav.hover()
                    await asyncio.sleep(0.3)
            except:
                continue

        screenshots.append(await save_screenshot(page, "12-nav-hover"))

        # Check for arrows/icons
        print("\n[13] Looking for arrows and icons...")
        arrows = await page.locator("[class*='arrow'], [class*='icon'], svg, i.fa, i.fas, .icon").all()
        print(f"  Found {len(arrows)} arrow/icon elements")

        # Full page screenshot
        print("\n[14] Taking full page screenshot...")
        full_path = os.path.join(SCREENSHOT_DIR, f"{SCREENSHOT_PREFIX}-full-page.png")
        await page.screenshot(path=full_path, full_page=True)
        print(f"Saved: {full_path}")
        screenshots.append(full_path)

        # Print all screenshot paths
        print("\n" + "=" * 60)
        print("AUDIT COMPLETE - SCREENSHOTS SAVED")
        print("=" * 60)
        for s in screenshots:
            print(f"  {s}")

        await browser.close()
        return screenshots

if __name__ == "__main__":
    asyncio.run(audit_purebrain())
