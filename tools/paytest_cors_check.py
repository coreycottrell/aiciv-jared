"""
Check CORS and actual network behavior of chat from browser context.
Captures the actual XHR/fetch response.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/paytest-audit")

async def cors_check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        console_all = []
        request_log = []
        response_log = []
        failed_log = []

        page.on("console", lambda m: console_all.append({"type": m.type, "text": m.text}))

        async def on_req(request):
            if 'messages' in request.url or 'puremarketing' in request.url or 'purebrain.workers' in request.url:
                try:
                    body = request.post_data
                except:
                    body = None
                request_log.append({
                    "url": request.url,
                    "method": request.method,
                    "headers": dict(request.headers),
                    "body": body
                })

        async def on_resp(response):
            if 'messages' in response.url or 'puremarketing' in response.url or 'purebrain.workers' in response.url:
                try:
                    body = await response.text()
                except:
                    body = "could not read"
                response_log.append({
                    "url": response.url,
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": body[:1000]
                })

        page.on("request", on_req)
        page.on("response", on_resp)
        page.on("requestfailed", lambda r: failed_log.append({"url": r.url, "failure": r.failure}))

        await page.goto("https://purebrain.ai/pay-test/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Scroll to chat
        await page.evaluate("document.getElementById('awakening').scrollIntoView()")
        await asyncio.sleep(1)

        # Begin
        begin_btn = await page.query_selector('.chat-initial__btn')
        if begin_btn:
            await begin_btn.click()
            await asyncio.sleep(1)

        # Type
        user_input = await page.query_selector('#userInput')
        if user_input:
            await user_input.click()
            await user_input.type("Hello test")
            await asyncio.sleep(0.5)

        # Submit
        submit_btn = await page.query_selector('#submitBtn')
        if submit_btn:
            await submit_btn.click()

        # Wait generously for response
        await asyncio.sleep(10)

        print("=== CHAT API REQUESTS ===")
        for r in request_log:
            print(f"\n  URL: {r['url']}")
            print(f"  Method: {r['method']}")
            print(f"  Body: {r['body']}")
            print(f"  Headers: {r['headers']}")

        print("\n=== CHAT API RESPONSES ===")
        for r in response_log:
            print(f"\n  URL: {r['url']}")
            print(f"  Status: {r['status']}")
            print(f"  Response headers: {r['headers']}")
            print(f"  Body: {r['body'][:500]}")

        print(f"\n=== FAILED REQUESTS (relevant) ===")
        for r in failed_log:
            if 'puremarketing' in r['url'] or 'purebrain' in r['url'] or 'messages' in r['url']:
                print(f"  FAILED: {r['url']}")
                print(f"  Reason: {r['failure']}")

        print(f"\n=== ALL CONSOLE MESSAGES ===")
        for m in console_all:
            print(f"  [{m['type'].upper()}] {m['text'][:300]}")

        # Try executing the API call directly from browser to check CORS
        cors_test = await page.evaluate("""async () => {
            try {
                const response = await fetch("https://api.puremarketing.ai/v1/messages", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        model: "claude-sonnet-4-20250514",
                        max_tokens: 100,
                        system: "You are a test.",
                        messages: [{"role": "user", "content": "CORS test"}]
                    })
                });
                const text = await response.text();
                return {
                    status: response.status,
                    ok: response.ok,
                    corsHeaders: response.headers.get('access-control-allow-origin'),
                    body: text.substring(0, 500)
                };
            } catch(e) {
                return {error: e.toString(), type: e.name};
            }
        }""")

        print(f"\n=== CORS TEST (api.puremarketing.ai from browser) ===")
        print(cors_test)

        cors_test2 = await page.evaluate("""async () => {
            try {
                const response = await fetch("https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        model: "claude-sonnet-4-20250514",
                        max_tokens: 100,
                        system: "You are a test.",
                        messages: [{"role": "user", "content": "CORS test workers.dev"}]
                    })
                });
                const text = await response.text();
                return {
                    status: response.status,
                    ok: response.ok,
                    corsHeaders: response.headers.get('access-control-allow-origin'),
                    body: text.substring(0, 500)
                };
            } catch(e) {
                return {error: e.toString(), type: e.name};
            }
        }""")

        print(f"\n=== CORS TEST (workers.dev from browser) ===")
        print(cors_test2)

        # Check the actual chat state
        chat_state = await page.evaluate("""() => {
            const msgs = document.querySelectorAll('.message');
            return {
                messages: Array.from(msgs).map(m => ({
                    className: m.className,
                    text: m.textContent.trim().substring(0, 200)
                })),
                loading: !!document.querySelector('.typing-indicator, .loading, [class*="typing"]'),
                inputValue: document.querySelector('#userInput') ? document.querySelector('#userInput').value : 'not found'
            };
        }""")

        print(f"\n=== CHAT STATE AFTER 10s ===")
        print(f"  Messages: {len(chat_state['messages'])}")
        for m in chat_state['messages']:
            print(f"    [{m['className'][:40]}]: {m['text'][:100]}")
        print(f"  Loading: {chat_state['loading']}")

        ss = str(SCREENSHOTS_DIR / "23-cors-check-final.png")
        await page.screenshot(path=ss, full_page=False)
        print(f"\nScreenshot: {ss}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(cors_check())
