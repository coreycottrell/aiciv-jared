#!/usr/bin/env python3
"""
Investigate the massive orange block covering all content sections below the hero.
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

        # Find what element is causing the orange block
        orange_investigation = await page.evaluate("""
        () => {
            // Get all elements with orange background
            const all = document.querySelectorAll('*');
            const orangeEls = [];
            for (const el of all) {
                const computed = window.getComputedStyle(el);
                const bg = computed.backgroundColor;
                // Orange in RGB is roughly r>200, g<120, b<50
                const match = bg.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/);
                if (match) {
                    const r = parseInt(match[1]);
                    const g = parseInt(match[2]);
                    const b = parseInt(match[3]);
                    if (r > 180 && g < 120 && b < 60) {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 500 && rect.height > 500) {
                            orangeEls.push({
                                tag: el.tagName,
                                id: el.id,
                                className: typeof el.className === 'string' ? el.className.substring(0, 80) : '',
                                bg: bg,
                                width: rect.width,
                                height: rect.height,
                                top: rect.top,
                                left: rect.left,
                                scrollTop: el.scrollTop,
                                offsetTop: el.offsetTop,
                                offsetHeight: el.offsetHeight
                            });
                        }
                    }
                }
            }
            return orangeEls.slice(0, 20);
        }
        """)
        print("Large orange elements:")
        print(json.dumps(orange_investigation, indent=2))

        # Check #pb-page specifically
        pb_page_check = await page.evaluate("""
        () => {
            const el = document.getElementById('pb-page');
            if (!el) return { found: false };
            const computed = window.getComputedStyle(el);
            return {
                found: true,
                className: el.className,
                backgroundColor: computed.backgroundColor,
                backgroundImage: computed.backgroundImage.substring(0, 200),
                color: computed.color,
                display: computed.display,
                position: computed.position,
                width: el.offsetWidth,
                height: el.offsetHeight,
                scrollHeight: el.scrollHeight,
                innerHTML_length: el.innerHTML.length,
                // Check children
                childCount: el.children.length,
                children: Array.from(el.children).map(c => ({
                    tag: c.tagName,
                    id: c.id,
                    className: typeof c.className === 'string' ? c.className.substring(0, 60) : '',
                    bg: window.getComputedStyle(c).backgroundColor,
                    height: c.offsetHeight,
                    display: window.getComputedStyle(c).display
                }))
            };
        }
        """)
        print("\n#pb-page check:")
        print(json.dumps(pb_page_check, indent=2))

        # Check #pb-what section (the one that should be at y=900)
        pb_what_check = await page.evaluate("""
        () => {
            const el = document.getElementById('pb-what');
            if (!el) return { found: false };
            const computed = window.getComputedStyle(el);
            return {
                found: true,
                backgroundColor: computed.backgroundColor,
                backgroundImage: computed.backgroundImage.substring(0, 300),
                display: computed.display,
                visibility: computed.visibility,
                opacity: computed.opacity,
                position: computed.position,
                zIndex: computed.zIndex,
                offsetTop: el.offsetTop,
                offsetHeight: el.offsetHeight,
                width: el.offsetWidth
            };
        }
        """)
        print("\n#pb-what section check:")
        print(json.dumps(pb_what_check, indent=2))

        # Check body and html background
        body_bg = await page.evaluate("""
        () => {
            const body = document.body;
            const html = document.documentElement;
            const bodyStyle = window.getComputedStyle(body);
            const htmlStyle = window.getComputedStyle(html);
            return {
                body: {
                    bg: bodyStyle.backgroundColor,
                    bgImage: bodyStyle.backgroundImage.substring(0, 200),
                    height: body.scrollHeight
                },
                html: {
                    bg: htmlStyle.backgroundColor,
                    bgImage: htmlStyle.backgroundImage.substring(0, 200)
                }
            };
        }
        """)
        print("\nBody/HTML background:")
        print(json.dumps(body_bg, indent=2))

        # Check CSS custom properties for orange
        css_vars = await page.evaluate("""
        () => {
            // Check what's at position y=1000 (where orange starts)
            const elAtPoint = document.elementFromPoint(720, 1000);
            if (!elAtPoint) return { found: false };
            const computed = window.getComputedStyle(elAtPoint);
            return {
                tag: elAtPoint.tagName,
                id: elAtPoint.id,
                className: typeof elAtPoint.className === 'string' ? elAtPoint.className.substring(0, 80) : '',
                backgroundColor: computed.backgroundColor,
                backgroundImage: computed.backgroundImage.substring(0, 300),
                position: computed.position,
                zIndex: computed.zIndex,
                width: elAtPoint.offsetWidth,
                height: elAtPoint.offsetHeight
            };
        }
        """)
        print("\nElement at position y=1000 (start of orange):")
        print(json.dumps(css_vars, indent=2))

        # Scroll to y=1000 and check what element is under cursor
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        # Check what's covering the sections - look at all fixed/absolute positioned elements
        covering_els = await page.evaluate("""
        () => {
            const all = document.querySelectorAll('*');
            const fixedAbsolute = [];
            for (const el of all) {
                const computed = window.getComputedStyle(el);
                const pos = computed.position;
                if ((pos === 'fixed' || pos === 'absolute') && el.offsetWidth > 400 && el.offsetHeight > 400) {
                    const bg = computed.backgroundColor;
                    const bgImg = computed.backgroundImage;
                    fixedAbsolute.push({
                        tag: el.tagName,
                        id: el.id,
                        className: typeof el.className === 'string' ? el.className.substring(0, 80) : '',
                        position: pos,
                        backgroundColor: bg,
                        backgroundImage: bgImg.substring(0, 100),
                        zIndex: computed.zIndex,
                        top: computed.top,
                        left: computed.left,
                        width: el.offsetWidth,
                        height: el.offsetHeight
                    });
                }
            }
            return fixedAbsolute.slice(0, 20);
        }
        """)
        print("\nLarge fixed/absolute positioned elements:")
        print(json.dumps(covering_els, indent=2))

        # Specifically check #pb-canvas-container styling
        canvas_container_style = await page.evaluate("""
        () => {
            const el = document.getElementById('pb-canvas-container');
            if (!el) return { found: false };
            const computed = window.getComputedStyle(el);
            return {
                found: true,
                inlineStyle: el.getAttribute('style'),
                backgroundColor: computed.backgroundColor,
                backgroundImage: computed.backgroundImage.substring(0, 200),
                position: computed.position,
                zIndex: computed.zIndex,
                top: computed.top,
                left: computed.left,
                width: computed.width,
                height: computed.height,
                display: computed.display,
                overflow: computed.overflow
            };
        }
        """)
        print("\n#pb-canvas-container computed style:")
        print(json.dumps(canvas_container_style, indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
