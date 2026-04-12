#!/usr/bin/env python3
"""
Targeted deep dive: Why is #pb-canvas-container missing? What does the full page DOM look like?
"""

import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/invitation/"
PASSWORD = "purebrain25"
SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/invitation-audit-2026-02-27"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        console_msgs = []
        page.on("console", lambda m: console_msgs.append({"t": m.type, "msg": m.text}))
        page.on("pageerror", lambda e: console_msgs.append({"t": "pageerror", "msg": str(e)}))

        try:
            await page.goto(URL, wait_until="networkidle", timeout=30000)
        except:
            pass
        await page.wait_for_timeout(2000)

        pw = await page.query_selector("input[type='password']")
        if pw:
            await pw.fill(PASSWORD)
            sub = await page.query_selector("input[type='submit']")
            if sub:
                await sub.click()
            await page.wait_for_timeout(10000)

        await page.wait_for_timeout(3000)

        # CRITICAL: Does #pb-canvas-container exist in the DOM?
        container_check = await page.evaluate("""
        () => {
            const el = document.getElementById('pb-canvas-container');
            if (!el) {
                // Search more broadly
                const any = document.querySelector('[id*="canvas"]');
                return {
                    found: false,
                    alternativeCanvasEl: any ? { id: any.id, tag: any.tagName } : null,
                    bodyStart: document.body.innerHTML.substring(0, 2000)
                };
            }
            return {
                found: true,
                id: el.id,
                tag: el.tagName,
                className: el.className,
                display: window.getComputedStyle(el).display,
                innerHTML: el.innerHTML.substring(0, 200)
            };
        }
        """)
        print("Container check:")
        print(json.dumps(container_check, indent=2))

        # Check the full inline script that runs the 3D
        full_script = await page.evaluate("""
        () => {
            const scripts = Array.from(document.scripts);
            for (const s of scripts) {
                if (!s.src && s.textContent && s.textContent.includes('pb-canvas-container')) {
                    return s.textContent;
                }
            }
            return null;
        }
        """)
        if full_script:
            print(f"\nFull 3D script length: {len(full_script)} chars")
            print("First 2000 chars:")
            print(full_script[:2000])
            print("\n...")
            print("Last 500 chars:")
            print(full_script[-500:])
        else:
            print("No script with pb-canvas-container found!")

        # Check body innerHTML for any canvas-related divs
        body_scan = await page.evaluate("""
        () => {
            // Get all div IDs in the page
            const allIds = Array.from(document.querySelectorAll('[id]')).map(el => ({
                id: el.id,
                tag: el.tagName,
                className: typeof el.className === 'string' ? el.className.substring(0,40) : ''
            }));
            return {
                totalElements: document.querySelectorAll('*').length,
                allIds: allIds.filter(el => el.id.length > 0).slice(0, 50)
            };
        }
        """)
        print(f"\nPage element count: {body_scan['totalElements']}")
        print("All element IDs (first 50):")
        for el in body_scan['allIds']:
            print(f"  #{el['id']} <{el['tag']}> .{el['className']}")

        # Check console for the PureBrain 3D error
        pb3d_messages = [m for m in console_msgs if 'PureBrain 3D' in m['msg'] or 'pb-canvas' in m['msg'].lower()]
        print(f"\nPureBrain 3D console messages: {len(pb3d_messages)}")
        for m in pb3d_messages:
            print(f"  {m['t']}: {m['msg']}")

        # All console errors
        print(f"\nAll console errors ({len([m for m in console_msgs if m['t'] == 'error'])}):")
        for m in [m for m in console_msgs if m['t'] == 'error']:
            print(f"  {m['msg'][:200]}")

        # Also check if the page has the invitation page's HTML structure
        page_structure = await page.evaluate("""
        () => {
            const sections = document.querySelectorAll('section, [class*="pb-"]');
            return Array.from(sections).slice(0, 20).map(el => ({
                tag: el.tagName,
                id: el.id,
                className: typeof el.className === 'string' ? el.className.substring(0, 60) : ''
            }));
        }
        """)
        print("\nPage sections (pb- elements):")
        for el in page_structure:
            print(f"  <{el['tag']}#{el['id']} class='{el['className']}'>")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
