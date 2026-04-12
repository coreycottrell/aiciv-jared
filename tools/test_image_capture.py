"""Capture amplify-founder and vc-fomo with proper force-visible."""
import asyncio, os
from playwright.async_api import async_playwright

OUT = "/home/jared/projects/AI-CIV/aether/exports/qa-infographic"
URL = "https://purebrain.ai/your-ai-tim-cook/"

FORCE_CSS = """() => {
    const s = document.createElement('style');
    s.id = 'qa-force';
    s.textContent = 'html body * { opacity: 1 !important; transform: none !important; transition: none !important; animation: none !important; visibility: visible !important; }';
    document.head.appendChild(s);
}"""

SCROLL_INTO_AMP = """() => {
    const imgs = Array.from(document.querySelectorAll('img'));
    const img = imgs.find(i => i.src.includes('amplify-founder'));
    if (img) { img.scrollIntoView({behavior: 'instant', block: 'center'}); return 'scrolled'; }
    return 'not found';
}"""

SCROLL_INTO_FOMO = """() => {
    const imgs = Array.from(document.querySelectorAll('img'));
    const img = imgs.find(i => i.src.includes('vc-fomo'));
    if (img) { img.scrollIntoView({behavior: 'instant', block: 'center'}); return 'scrolled'; }
    return 'not found';
}"""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await ctx.new_page()
        await page.goto(URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # Scroll full page to trigger lazy loads
        total_h = await page.evaluate("document.body.scrollHeight")
        for y in range(0, total_h, 200):
            await page.evaluate(f"window.scrollTo(0, {y})")
            await page.wait_for_timeout(60)
        await page.wait_for_timeout(1000)

        # Inject force-visible
        await page.evaluate(FORCE_CSS)
        await page.wait_for_timeout(800)

        # Verify
        check = await page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll('img'));
            const amp = imgs.find(i => i.src.includes('amplify-founder'));
            if (!amp) return {found: false};
            const parent = amp.parentElement;
            return {
                found: true,
                imgOpacity: window.getComputedStyle(amp).opacity,
                parentOpacity: window.getComputedStyle(parent).opacity,
                parentClass: String(parent.className || '').substring(0, 50)
            };
        }""")
        print(f"Image check: {check}")

        # amplify-founder
        r1 = await page.evaluate(SCROLL_INTO_AMP)
        print(f"Scroll to amplify: {r1}")
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(OUT, "9f-amplify-final.png"))
        print("9f saved")

        # vc-fomo
        r2 = await page.evaluate(SCROLL_INTO_FOMO)
        print(f"Scroll to vc-fomo: {r2}")
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(OUT, "10f-vcfomo-final.png"))
        print("10f saved")

        await browser.close()

asyncio.run(main())
