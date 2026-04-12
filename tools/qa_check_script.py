"""
Extract and display the full payment script to verify redirect logic.
"""
import asyncio
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/partnered-how-this-levels-you-up/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
        page = await context.new_page()

        try:
            await page.goto(URL, wait_until="networkidle", timeout=30000)
        except Exception:
            await page.goto(URL, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(2)

        scripts = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script:not([src])'));
                return scripts.map(s => s.textContent).filter(t =>
                    t.includes('PAYPAL') || t.includes('paypal') ||
                    t.includes('499') || t.includes('Partnered') ||
                    t.includes('sandbox') || t.includes('redirect')
                );
            }
        """)

        for i, s in enumerate(scripts):
            print(f"\n{'='*60}")
            print(f"SCRIPT {i+1} ({len(s)} chars):")
            print(s)

        await browser.close()

asyncio.run(main())
