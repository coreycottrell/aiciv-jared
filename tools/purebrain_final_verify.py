#!/usr/bin/env python3
"""
Final verification of PureBrain styling
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOT_DIR = "/tmp"

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("=" * 60)
        print("PUREBRAIN FINAL VERIFICATION")
        print("=" * 60)

        await page.goto("https://purebrain.ai", wait_until="networkidle", timeout=90000)
        await asyncio.sleep(5)  # Wait for all assets

        screenshots = []

        # Full page at different scroll positions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("\n[1] Hero section...")
        path = f"/tmp/purebrain-verify-{timestamp}-01-hero.png"
        await page.screenshot(path=path)
        screenshots.append(path)
        print(f"  Saved: {path}")

        print("\n[2] Features section...")
        await page.evaluate("window.scrollTo(0, 800)")
        await asyncio.sleep(1)
        path = f"/tmp/purebrain-verify-{timestamp}-02-features.png"
        await page.screenshot(path=path)
        screenshots.append(path)
        print(f"  Saved: {path}")

        print("\n[3] Three layers section...")
        await page.evaluate("window.scrollTo(0, 1600)")
        await asyncio.sleep(1)
        path = f"/tmp/purebrain-verify-{timestamp}-03-layers.png"
        await page.screenshot(path=path)
        screenshots.append(path)
        print(f"  Saved: {path}")

        print("\n[4] Capabilities section...")
        await page.evaluate("window.scrollTo(0, 2400)")
        await asyncio.sleep(1)
        path = f"/tmp/purebrain-verify-{timestamp}-04-capabilities.png"
        await page.screenshot(path=path)
        screenshots.append(path)
        print(f"  Saved: {path}")

        print("\n[5] Begin Awakening section...")
        await page.evaluate("window.scrollTo(0, 3200)")
        await asyncio.sleep(1)
        path = f"/tmp/purebrain-verify-{timestamp}-05-awakening.png"
        await page.screenshot(path=path)
        screenshots.append(path)
        print(f"  Saved: {path}")

        print("\n[6] What you get section...")
        await page.evaluate("window.scrollTo(0, 4000)")
        await asyncio.sleep(1)
        path = f"/tmp/purebrain-verify-{timestamp}-06-whatyouget.png"
        await page.screenshot(path=path)
        screenshots.append(path)
        print(f"  Saved: {path}")

        print("\n[7] Footer area...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        path = f"/tmp/purebrain-verify-{timestamp}-07-footer.png"
        await page.screenshot(path=path)
        screenshots.append(path)
        print(f"  Saved: {path}")

        # Full page
        print("\n[8] Full page screenshot...")
        path = f"/tmp/purebrain-verify-{timestamp}-full.png"
        await page.screenshot(path=path, full_page=True)
        screenshots.append(path)
        print(f"  Saved: {path}")

        # Now check colors
        print("\n[9] Checking actual colors of key elements...")

        colors = await page.evaluate(r'''
            () => {
                const elements = [
                    {sel: 'body', name: 'Body'},
                    {sel: 'p.hero__description', name: 'Hero Description'},
                    {sel: '.section__badge', name: 'Section Badge'},
                    {sel: '.feature-card', name: 'Feature Card'},
                    {sel: '.capability-item', name: 'Capability Item'},
                    {sel: '.chat-header__name', name: 'Chat Header Name'},
                    {sel: '#value-pyramid .section__title', name: 'Pyramid Title'},
                    {sel: '.text-orange', name: 'Text Orange (accent)'},
                    {sel: 'label.waitlist-form__label', name: 'Form Label'}
                ];

                const results = [];
                elements.forEach(e => {
                    const el = document.querySelector(e.sel);
                    if (el) {
                        const style = window.getComputedStyle(el);
                        results.push({
                            name: e.name,
                            selector: e.sel,
                            color: style.color,
                            backgroundColor: style.backgroundColor
                        });
                    }
                });
                return results;
            }
        ''')

        print("\n  Element Colors:")
        for c in colors:
            is_orange = '241' in c['color']
            status = "ORANGE!" if is_orange else "OK"
            print(f"    {c['name']}: {c['color']} [{status}]")

        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETE")
        print("=" * 60)
        for s in screenshots:
            print(f"  {s}")

        await browser.close()
        return screenshots

if __name__ == "__main__":
    asyncio.run(verify())
