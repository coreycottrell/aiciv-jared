"""
Force all scroll-reveal elements visible, then screenshot the images.
Disables all opacity/transform animations before capture.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/qa-amplify-deploy")

FORCE_VISIBLE_JS = """
    // Override ALL opacity and transform on ALL elements
    const style = document.createElement('style');
    style.id = 'force-visible-override';
    style.textContent = `
        * {
            opacity: 1 !important;
            transform: none !important;
            transition: none !important;
            animation: none !important;
            visibility: visible !important;
        }
    `;
    document.head.appendChild(style);
    console.log('Force-visible override applied');
"""

async def scroll_and_reveal(page):
    height = await page.evaluate("document.body.scrollHeight")
    for y in range(0, height, 400):
        await page.evaluate(f"window.scrollTo(0, {y})")
        await asyncio.sleep(0.03)
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.3)

async def find_image_and_shoot(page, fragment, label):
    result = await page.evaluate(f"""
        (() => {{
            const imgs = Array.from(document.querySelectorAll('img'));
            const img = imgs.find(i => i.src.toLowerCase().includes('{fragment}'));
            if (!img) return null;
            const rect = img.getBoundingClientRect();
            const pageY = rect.top + window.scrollY;
            return {{
                src: img.src,
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight,
                renderedWidth: rect.width,
                renderedHeight: rect.height,
                pageY: pageY,
                complete: img.complete
            }};
        }})()
    """)
    if not result:
        print(f"  [NOT FOUND] {fragment}")
        return

    print(f"\n  Image: {fragment}")
    print(f"  URL: {result['src']}")
    print(f"  Natural size: {result['naturalWidth']}x{result['naturalHeight']}")
    print(f"  Rendered size: {result['renderedWidth']:.0f}x{result['renderedHeight']:.0f}")
    print(f"  Page Y: {result['pageY']:.0f}px")
    print(f"  Complete/loaded: {result['complete']}")

    # Scroll image to center of viewport
    scroll_y = max(0, result['pageY'] - 130)
    await page.evaluate(f"window.scrollTo(0, {scroll_y})")
    await asyncio.sleep(0.5)

    out = OUTPUT_DIR / f"fv-{label}.png"
    await page.screenshot(path=str(out), full_page=False)
    print(f"  [screenshot] {out}")

    # Also take 300px above to show context
    scroll_y2 = max(0, result['pageY'] - 400)
    await page.evaluate(f"window.scrollTo(0, {scroll_y2})")
    await asyncio.sleep(0.3)
    out2 = OUTPUT_DIR / f"fv-{label}-ctx.png"
    await page.screenshot(path=str(out2), full_page=False)
    print(f"  [screenshot] {out2} (context)")


async def main():
    print("Force-visible image verification")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ---- TIM COOK ----
        print("\nTIM COOK PAGE")
        ctx = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await ctx.new_page()
        await page.goto("https://purebrain.ai/your-ai-tim-cook/", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)

        # Scroll first to trigger lazy loading
        await scroll_and_reveal(page)
        await asyncio.sleep(0.5)

        # Now force everything visible
        await page.evaluate(FORCE_VISIBLE_JS)
        await asyncio.sleep(0.5)

        # Screenshot full page with everything visible
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.3)
        await page.screenshot(path=str(OUTPUT_DIR / "fv-tc-full.png"), full_page=True)
        print("  [screenshot] fv-tc-full.png (full page, all visible)")

        await find_image_and_shoot(page, "amplify-founder", "tc-amplify")
        await find_image_and_shoot(page, "vc-fomo", "tc-vcfomo")

        await ctx.close()

        # ---- PITCH ----
        print("\nPITCH PAGE")
        ctx2 = await browser.new_context(viewport={"width": 1280, "height": 900})
        page2 = await ctx2.new_page()
        await page2.goto("https://purebrain.ai/pitch/", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)

        await scroll_and_reveal(page2)
        await asyncio.sleep(0.5)
        await page2.evaluate(FORCE_VISIBLE_JS)
        await asyncio.sleep(0.5)

        await page2.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.3)
        await page2.screenshot(path=str(OUTPUT_DIR / "fv-pitch-full.png"), full_page=True)
        print("  [screenshot] fv-pitch-full.png (full page, all visible)")

        await find_image_and_shoot(page2, "vc-hero", "pitch-vchero")

        # Also grab dept wall area
        await page2.evaluate("window.scrollTo(0, 4300)")
        await asyncio.sleep(0.4)
        await page2.screenshot(path=str(OUTPUT_DIR / "fv-pitch-deptwall.png"), full_page=False)
        print("  [screenshot] fv-pitch-deptwall.png")

        # Pricing area
        await page2.evaluate("window.scrollTo(0, 6000)")
        await asyncio.sleep(0.4)
        await page2.screenshot(path=str(OUTPUT_DIR / "fv-pitch-pricing.png"), full_page=False)
        print("  [screenshot] fv-pitch-pricing.png")

        await ctx2.close()
        await browser.close()

    print("\n" + "="*60)
    print("Done. Screenshots:")
    for f in sorted(OUTPUT_DIR.glob("fv-*.png")):
        print(f"  {f}")


if __name__ == "__main__":
    asyncio.run(main())
