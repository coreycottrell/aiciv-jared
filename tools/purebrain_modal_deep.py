#!/usr/bin/env python3
"""
PureBrain Modal Deep Dive
Specifically capture the modal/popup with form fields
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOT_DIR = "/tmp"

async def save_screenshot(page, label):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"purebrain-modal-deep-{timestamp}-{label}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    await page.screenshot(path=filepath, full_page=False)
    print(f"Saved: {filepath}")
    return filepath

async def deep_modal_investigation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("=" * 60)
        print("PUREBRAIN MODAL DEEP INVESTIGATION")
        print("=" * 60)

        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        screenshots = []

        # Look at the hero section first
        print("\n[1] Hero section...")
        screenshots.append(await save_screenshot(page, "01-hero"))

        # Find and click the "Awaken Your PURE BRAIN" button
        print("\n[2] Looking for primary CTA button...")

        # Try clicking the first visible button with "Awaken"
        awaken_btns = await page.locator("a:has-text('Awaken'), button:has-text('Awaken')").all()
        print(f"  Found {len(awaken_btns)} Awaken buttons")

        for i, btn in enumerate(awaken_btns):
            try:
                if await btn.is_visible():
                    text = await btn.inner_text()
                    print(f"  Clicking: {text[:50]}")
                    await btn.click()
                    await asyncio.sleep(2)
                    screenshots.append(await save_screenshot(page, f"02-after-awaken-click-{i}"))
                    break
            except:
                continue

        # Now scroll down to the "BEGIN YOUR AWAKENING" section
        print("\n[3] Scrolling to BEGIN YOUR AWAKENING...")
        await page.evaluate("window.scrollTo(0, 2700)")
        await asyncio.sleep(2)
        screenshots.append(await save_screenshot(page, "03-begin-awakening-section"))

        # Find and click "Begin Awakening" button
        print("\n[4] Looking for Begin Awakening button...")
        begin_btn = page.locator("button:has-text('Begin Awakening'), a:has-text('Begin Awakening')").first
        if await begin_btn.is_visible():
            print("  Found Begin Awakening button, clicking...")
            await begin_btn.click()
            await asyncio.sleep(3)
            screenshots.append(await save_screenshot(page, "04-modal-opened"))

            # Now look at the modal content
            print("\n[5] Modal is open, checking for form fields...")

            # Wait a bit more for modal animations
            await asyncio.sleep(2)
            screenshots.append(await save_screenshot(page, "05-modal-content"))

            # Check for input fields in the modal
            inputs = await page.locator(".chat-container input, .awakening-container input, [class*='modal'] input, [role='dialog'] input").all()
            print(f"  Found {len(inputs)} inputs in modal area")

            # Try to interact with the modal
            # Look for an input to type in
            input_field = page.locator("input[type='text'], input:not([type='hidden'])").first
            if await input_field.is_visible():
                print("  Clicking input field...")
                await input_field.click()
                await asyncio.sleep(1)
                screenshots.append(await save_screenshot(page, "06-input-focused"))

            # Type something
            await page.keyboard.type("Test")
            await asyncio.sleep(1)
            screenshots.append(await save_screenshot(page, "07-after-typing"))

        # Now look at the waitlist form specifically
        print("\n[6] Looking for waitlist/signup form with labels...")

        # Navigate away and check if there's a waitlist page
        await page.goto("https://purebrain.ai/waitlist", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        screenshots.append(await save_screenshot(page, "08-waitlist-page"))

        # Check for elementor popup triggers
        print("\n[7] Checking for Elementor popups...")
        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        # Look for all form labels on the main page
        labels = await page.locator("label").all()
        print(f"\n  All labels on page:")
        for label in labels:
            try:
                text = await label.inner_text()
                if text.strip():
                    # Get computed style
                    color = await label.evaluate("el => window.getComputedStyle(el).color")
                    print(f"    '{text.strip()}' - color: {color}")
            except:
                pass

        # Get all orange-colored text elements
        print("\n[8] Finding all orange-colored text...")
        orange_text = await page.evaluate('''
            () => {
                const results = [];
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );

                let node;
                while (node = walker.nextNode()) {
                    const text = node.textContent.trim();
                    if (text && text.length > 1 && text.length < 100) {
                        const parent = node.parentElement;
                        if (parent) {
                            const style = window.getComputedStyle(parent);
                            const color = style.color;
                            // Check if it's orangish (high red, medium green, low blue)
                            const match = color.match(/rgb\\((\d+), (\d+), (\d+)\\)/);
                            if (match) {
                                const [_, r, g, b] = match.map(Number);
                                if (r > 200 && g < 100 && b < 50) {
                                    results.push({
                                        text: text.substring(0, 50),
                                        color: color,
                                        tag: parent.tagName,
                                        classes: parent.className
                                    });
                                }
                            }
                        }
                    }
                }
                return results.slice(0, 50);
            }
        ''')

        print(f"\n  Found {len(orange_text)} orange text elements:")
        for item in orange_text:
            print(f"    {item['tag']}: '{item['text']}' [{item['color']}]")

        print("\n" + "=" * 60)
        print("DEEP INVESTIGATION COMPLETE")
        print("=" * 60)
        for s in screenshots:
            print(f"  {s}")

        await browser.close()
        return screenshots

if __name__ == "__main__":
    asyncio.run(deep_modal_investigation())
