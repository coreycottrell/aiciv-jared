"""
Debug the actual JS execution - intercept the startConversation call and catch errors.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/paytest-audit")

async def js_debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        all_console = []
        all_requests = []

        page.on("console", lambda m: all_console.append({"type": m.type, "text": m.text}))
        page.on("request", lambda r: all_requests.append({"url": r.url, "method": r.method}))

        await page.goto("https://purebrain.ai/pay-test/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Scroll to chat
        await page.evaluate("document.getElementById('awakening').scrollIntoView()")
        await asyncio.sleep(1)

        # Instead of clicking, call startConversation directly and catch the error
        result = await page.evaluate("""async () => {
            try {
                await startConversation();
                return {success: true, error: null};
            } catch(e) {
                return {success: false, error: e.toString(), stack: e.stack};
            }
        }""")

        print(f"startConversation result: {result}")

        # Wait for any async activity
        await asyncio.sleep(5)

        # Check what happened
        chat_state = await page.evaluate("""() => {
            const msgs = document.querySelectorAll('.message');
            const typingIndicator = document.querySelector('.typing-indicator');
            return {
                messageCount: msgs.length,
                messages: Array.from(msgs).map(m => ({
                    className: m.className,
                    text: m.textContent.trim().substring(0, 200)
                })),
                hasTypingIndicator: !!typingIndicator,
                conversationStarted: typeof state !== 'undefined' ? state.conversationStarted : 'state not found',
                isTyping: typeof state !== 'undefined' ? state.isTyping : 'state not found',
                consecutiveFailures: typeof state !== 'undefined' ? state.consecutiveFailures : 'state not found',
                lastError: typeof state !== 'undefined' ? state.lastError : 'state not found'
            };
        }""")

        print(f"\nChat state:")
        for k, v in chat_state.items():
            print(f"  {k}: {v}")

        # Try a manual fetch from JS context to verify API works
        api_result = await page.evaluate("""async () => {
            try {
                const SYSTEM_PROMPT_TEST = 'You are PURE BRAIN. Be brief.';
                const messages = [{"role": "user", "content": "Hello test message"}];

                // Try primary endpoint
                const resp = await fetch("https://api.puremarketing.ai/v1/messages", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        model: "claude-sonnet-4-20250514",
                        max_tokens: 100,
                        system: SYSTEM_PROMPT_TEST,
                        messages: messages
                    })
                });
                const data = await resp.json();
                return {
                    success: resp.ok,
                    status: resp.status,
                    hasContent: !!(data.content && data.content.length > 0),
                    text: data.content ? data.content[0]?.text?.substring(0, 100) : 'no text'
                };
            } catch(e) {
                return {success: false, error: e.toString()};
            }
        }""")

        print(f"\nDirect API call from browser: {api_result}")

        # Now try processResponse directly
        result2 = await page.evaluate("""async () => {
            if (typeof state === 'undefined') return {error: 'state not defined'};

            // First mark conversation as started
            state.conversationStarted = true;

            try {
                await processResponse("Hello, is this working?");
                return {success: true};
            } catch(e) {
                return {success: false, error: e.toString(), stack: e.stack};
            }
        }""")

        print(f"\nprocessResponse result: {result2}")

        # Wait for response
        await asyncio.sleep(5)

        final_state = await page.evaluate("""() => {
            const msgs = document.querySelectorAll('.message');
            return {
                messageCount: msgs.length,
                messages: Array.from(msgs).map(m => ({text: m.textContent.trim().substring(0, 200)})),
                lastError: typeof state !== 'undefined' ? state.lastError : 'N/A',
                failures: typeof state !== 'undefined' ? state.consecutiveFailures : 'N/A'
            };
        }""")

        print(f"\nFinal state after processResponse:")
        print(f"  Messages: {final_state['messageCount']}")
        for m in final_state['messages']:
            print(f"    {m['text'][:100]}")
        print(f"  Last error: {final_state['lastError']}")
        print(f"  Failures: {final_state['failures']}")

        print(f"\n=== ALL CONSOLE ===")
        for m in all_console:
            print(f"  [{m['type'].upper()}] {m['text'][:300]}")

        print(f"\n=== CHAT-RELATED REQUESTS ===")
        for r in all_requests:
            if any(kw in r['url'] for kw in ['puremarketing', 'purebrain', 'messages', 'claude', 'api']):
                print(f"  {r['method']} {r['url'][:120]}")

        ss = str(SCREENSHOTS_DIR / "24-js-debug-final.png")
        await page.screenshot(path=ss, full_page=False)
        print(f"\nScreenshot: {ss}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(js_debug())
