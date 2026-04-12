"""
Deep mobile investigation for Tim Cook page - checking why mid sections appear blank
"""

import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/your-ai-tim-cook/"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/tim-cook-qa-2026-02-27"

async def run_mobile_deep():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Mobile context
        context = await browser.new_context(
            viewport={"width": 375, "height": 667},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        page = await context.new_page()
        await page.goto(URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        # Get all sections with their positions
        section_info = await page.evaluate("""
            () => {
                const results = [];
                const allSections = document.querySelectorAll('section, .tc-section, [class*="tc-"]');
                for (const el of allSections) {
                    const rect = el.getBoundingClientRect();
                    const scrollTop = window.scrollY;
                    results.push({
                        tag: el.tagName,
                        class: el.className ? el.className.toString().substring(0, 80) : '',
                        id: el.id || '',
                        top: rect.top + scrollTop,
                        height: rect.height,
                        display: window.getComputedStyle(el).display,
                        visibility: window.getComputedStyle(el).visibility,
                        opacity: window.getComputedStyle(el).opacity
                    });
                }
                return results;
            }
        """)

        print("\n=== MOBILE SECTION POSITIONS ===")
        for s in section_info:
            print(f"  {s['tag']} .{s['class'][:50]}")
            print(f"    top={s['top']:.0f}px, height={s['height']:.0f}px")
            print(f"    display={s['display']}, vis={s['visibility']}, opacity={s['opacity']}")

        # Scroll through the page taking screenshots at key positions
        total_height = await page.evaluate("document.body.scrollHeight")
        print(f"\nTotal mobile scroll height: {total_height}px")

        positions = [0, 700, 1400, 2100, 2800, 3500, 4200, 4900, 5600, 6300, 7000, 7700, 8400, 9100, 9800]

        for pos in positions:
            if pos > total_height:
                break
            await page.evaluate(f"window.scrollTo(0, {pos})")
            await page.wait_for_timeout(800)
            path = f"{SCREENSHOT_DIR}/mobile-scroll-{pos}.png"
            await page.screenshot(path=path)
            print(f"  Screenshot at y={pos}: {path}")

        # Check if scroll-reveal is hiding elements
        hidden_elements = await page.evaluate("""
            () => {
                const hidden = [];
                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    if (rect.height > 50 && (
                        style.opacity === '0' ||
                        style.visibility === 'hidden' ||
                        style.transform.includes('translateY') && style.opacity === '0'
                    )) {
                        hidden.push({
                            tag: el.tagName,
                            class: el.className ? el.className.toString().substring(0, 60) : '',
                            opacity: style.opacity,
                            visibility: style.visibility,
                            transform: style.transform.substring(0, 60)
                        });
                    }
                });
                return hidden.slice(0, 20);
            }
        """)

        print(f"\n=== HIDDEN/ZERO-OPACITY ELEMENTS (mobile) ===")
        print(f"Count: {len(hidden_elements)}")
        for el in hidden_elements[:10]:
            print(f"  {el['tag']} .{el['class']}")
            print(f"    opacity={el['opacity']}, vis={el['visibility']}, transform={el['transform']}")

        # Check animation states
        anim_states = await page.evaluate("""
            () => {
                const results = [];
                const animEls = document.querySelectorAll('[class*="reveal"], [class*="fade"], [data-aos], [class*="animate"], [class*="sr-"]');
                animEls.forEach(el => {
                    const style = window.getComputedStyle(el);
                    results.push({
                        class: el.className ? el.className.toString().substring(0, 60) : '',
                        opacity: style.opacity,
                        transform: style.transform.substring(0, 50)
                    });
                });
                return results.slice(0, 20);
            }
        """)
        print(f"\n=== ANIMATION ELEMENT STATES ===")
        for el in anim_states[:10]:
            print(f"  .{el['class']}: opacity={el['opacity']}, transform={el['transform']}")

        # Trigger scroll observer by scrolling through (force-reveal)
        print("\n=== FORCE SCROLL THROUGH ===")
        for y in range(0, int(total_height), 200):
            await page.evaluate(f"window.scrollTo(0, {y})")
            await page.wait_for_timeout(50)

        await page.wait_for_timeout(2000)

        # Take full page after forced scroll
        full_path = f"{SCREENSHOT_DIR}/mobile-post-scroll-full.png"
        await page.screenshot(path=full_path, full_page=True)
        print(f"Post-scroll full page: {full_path}")

        await browser.close()

asyncio.run(run_mobile_deep())
print("\nDone")
