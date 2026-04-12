"""
Targeted zoom screenshots for specific images on both pages.
Uses getBoundingClientRect to find exact positions.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/qa-amplify-deploy")

async def scroll_to_reveal(page):
    height = await page.evaluate("document.body.scrollHeight")
    for y in range(0, height, 300):
        await page.evaluate(f"window.scrollTo(0, {y})")
        await asyncio.sleep(0.04)
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.5)

async def find_and_shoot_image(page, filename_fragment, label, context_px=200):
    """Find image by filename fragment, scroll to it, screenshot the area."""
    result = await page.evaluate(f"""
        (() => {{
            const imgs = Array.from(document.querySelectorAll('img'));
            const img = imgs.find(i => i.src.toLowerCase().includes('{filename_fragment}'));
            if (!img) return null;
            const rect = img.getBoundingClientRect();
            const pageY = rect.top + window.scrollY;
            return {{
                src: img.src,
                width: img.naturalWidth,
                height: img.naturalHeight,
                pageY: pageY,
                rectWidth: rect.width,
                rectHeight: rect.height,
                complete: img.complete
            }};
        }})()
    """)

    if not result:
        print(f"  [FAIL] Image '{filename_fragment}' not found in DOM")
        return None

    print(f"  [FOUND] {label}: {result['src']}")
    print(f"          Natural: {result['width']}x{result['height']}, Rendered: {result['rectWidth']:.0f}x{result['rectHeight']:.0f}")
    print(f"          Page Y position: {result['pageY']:.0f}px")

    # Scroll so image is centered in viewport
    scroll_to = max(0, result['pageY'] - 100)
    await page.evaluate(f"window.scrollTo(0, {scroll_to})")
    await asyncio.sleep(0.8)

    # Take viewport screenshot of the image area
    out_path = OUTPUT_DIR / f"zoom-{label}.png"
    await page.screenshot(path=str(out_path), full_page=False)
    print(f"  [screenshot] {out_path}")
    return result


async def main():
    print("Targeted zoom screenshots for deployed images")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ---- TIM COOK PAGE ----
        print("\nTIM COOK PAGE: Targeting amplify-founder and vc-fomo")
        ctx = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await ctx.new_page()
        await page.goto("https://purebrain.ai/your-ai-tim-cook/", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)
        await scroll_to_reveal(page)
        await asyncio.sleep(1)

        # Amplify founder image
        r1 = await find_and_shoot_image(page, "amplify-founder", "tc-amplify-founder")

        # vc-fomo image
        r2 = await find_and_shoot_image(page, "vc-fomo", "tc-vc-fomo")

        # Also take a wider context: scroll slightly above amplify image
        if r1:
            scroll_above = max(0, r1['pageY'] - 300)
            await page.evaluate(f"window.scrollTo(0, {scroll_above})")
            await asyncio.sleep(0.5)
            await page.screenshot(path=str(OUTPUT_DIR / "zoom-tc-amplify-above.png"), full_page=False)
            print(f"  [screenshot] zoom-tc-amplify-above.png (context above image)")

        if r2:
            scroll_above = max(0, r2['pageY'] - 300)
            await page.evaluate(f"window.scrollTo(0, {scroll_above})")
            await asyncio.sleep(0.5)
            await page.screenshot(path=str(OUTPUT_DIR / "zoom-tc-vcfomo-above.png"), full_page=False)
            print(f"  [screenshot] zoom-tc-vcfomo-above.png (context above image)")

        await ctx.close()

        # ---- PITCH PAGE ----
        print("\nPITCH PAGE: Targeting vc-hero")
        ctx2 = await browser.new_context(viewport={"width": 1280, "height": 900})
        page2 = await ctx2.new_page()
        await page2.goto("https://purebrain.ai/pitch/", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)
        await scroll_to_reveal(page2)
        await asyncio.sleep(1)

        r3 = await find_and_shoot_image(page2, "vc-hero", "pitch-vc-hero")

        if r3:
            scroll_above = max(0, r3['pageY'] - 300)
            await page2.evaluate(f"window.scrollTo(0, {scroll_above})")
            await asyncio.sleep(0.5)
            await page2.screenshot(path=str(OUTPUT_DIR / "zoom-pitch-vchero-above.png"), full_page=False)
            print(f"  [screenshot] zoom-pitch-vchero-above.png (context above image)")

        # Also take full pitch page hero area
        await page2.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        await page2.screenshot(path=str(OUTPUT_DIR / "zoom-pitch-hero-top.png"), full_page=False)
        print(f"  [screenshot] zoom-pitch-hero-top.png")

        # Dept wall targeted
        dept_info = await page2.evaluate("""
            (() => {
                // Find dept grid by looking for grid containers with dept names
                const grids = Array.from(document.querySelectorAll('[class*="dept"], [class*="department"], [class*="team-grid"], [class*="agent-grid"]'));
                if (grids.length > 0) {
                    const rect = grids[0].getBoundingClientRect();
                    return { found: true, pageY: rect.top + window.scrollY };
                }
                // Fallback: search for any element containing 'dept' text
                const allEls = Array.from(document.querySelectorAll('*'));
                for (const el of allEls) {
                    if (el.children.length === 0 && el.textContent.includes('Marketing') &&
                        el.textContent.includes('Sales') && el.textContent.length < 200) {
                        const rect = el.getBoundingClientRect();
                        return { found: true, pageY: rect.top + window.scrollY, text: el.textContent };
                    }
                }
                return { found: false };
            })()
        """)
        print(f"\n  Dept wall info: {dept_info}")

        await ctx2.close()
        await browser.close()

    print("\n" + "="*60)
    print("Zoom screenshots complete.")
    for f in sorted(OUTPUT_DIR.glob("zoom-*.png")):
        print(f"  {f}")


if __name__ == "__main__":
    asyncio.run(main())
