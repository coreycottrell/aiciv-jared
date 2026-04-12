"""
Check what network requests the chat is making, and why it's not responding.
Also check the main page's chat for comparison.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/paytest-audit")

async def network_check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        network_log = []
        failed_requests = []
        console_errors = []

        page.on("console", lambda m: console_errors.append({"type": m.type, "text": m.text}))
        page.on("requestfailed", lambda r: failed_requests.append({
            "url": r.url,
            "failure": r.failure
        }))

        async def on_response(response):
            url = response.url
            if any(kw in url.lower() for kw in ['chat', 'api', 'log', 'ai', 'openai', 'purebrain', 'paypal', '89.167', 'send', 'message']):
                try:
                    body = await response.body()
                    network_log.append({
                        "url": url,
                        "status": response.status,
                        "body_preview": body.decode('utf-8', errors='replace')[:500]
                    })
                except:
                    network_log.append({"url": url, "status": response.status, "body_preview": "could not read"})

        page.on("response", on_response)

        await page.goto("https://purebrain.ai/pay-test/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Scroll to chat and interact
        await page.evaluate("document.getElementById('awakening').scrollIntoView()")
        await asyncio.sleep(1)

        begin_btn = await page.query_selector('.chat-initial__btn')
        if begin_btn:
            await begin_btn.click()
            await asyncio.sleep(1)

        user_input = await page.query_selector('#userInput')
        if user_input:
            await user_input.click()
            await user_input.type("Hello test")

        submit_btn = await page.query_selector('#submitBtn')
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(8)  # Wait longer for any async response

        print("=== FAILED REQUESTS ===")
        for r in failed_requests:
            print(f"  FAILED: {r['url']}")
            print(f"  Reason: {r['failure']}")

        print(f"\n=== NETWORK LOG (relevant) - {len(network_log)} entries ===")
        for entry in network_log:
            print(f"\n  URL: {entry['url'][:120]}")
            print(f"  Status: {entry['status']}")
            print(f"  Body: {entry['body_preview'][:200]}")

        print(f"\n=== ALL CONSOLE ({len(console_errors)}) ===")
        for e in console_errors:
            print(f"  [{e['type'].upper()}] {e['text'][:300]}")

        # Also check the chat JS to understand the endpoint it calls
        chat_endpoint = await page.evaluate("""() => {
            // Look at the chat submission function to find the API endpoint
            const scripts = document.querySelectorAll('script:not([src])');
            let endpoints = [];
            scripts.forEach(s => {
                const text = s.textContent || '';
                // Find fetch/XHR/XMLHttpRequest calls
                const fetchMatches = text.match(/fetch\(['"](.*?)['"]/g) || [];
                const xhrMatches = text.match(/\.open\(['"]\w+['"],\s*['"](.*?)['"]/g) || [];
                const urlMatches = text.match(/['"](https?:\/\/[^'"]+api[^'"]*)['"]/g) || [];
                endpoints.push(...fetchMatches, ...xhrMatches, ...urlMatches);
            });
            return [...new Set(endpoints)].slice(0, 20);
        }""")

        print(f"\n=== API ENDPOINTS FOUND IN SCRIPTS ===")
        for ep in chat_endpoint:
            print(f"  {ep}")

        # Check what the chat script actually has as its endpoint
        chat_js = await page.evaluate("""() => {
            const scripts = document.querySelectorAll('script:not([src])');
            for (const s of scripts) {
                const text = s.textContent || '';
                if (text.includes('submitBtn') || text.includes('handleSubmit') || text.includes('#userInput')) {
                    return text.substring(0, 5000);
                }
            }
            return 'Not found';
        }""")

        print(f"\n=== CHAT SUBMISSION SCRIPT ===")
        print(chat_js[:3000])

        # Screenshot current state
        ss = str(SCREENSHOTS_DIR / "22-network-check-final.png")
        await page.screenshot(path=ss, full_page=False)
        print(f"\nFinal screenshot: {ss}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(network_check())
