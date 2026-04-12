"""
Portal QA - Login test and visual inspection
Goal: Verify login works, then check panels
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-20260316"

# Try multiple tokens - the old one may be expired
TOKENS_TO_TRY = [
    "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ",
]

async def run():
    os.makedirs(SS_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # First, check what's on the portal server to find current valid tokens
        # Let's look at server logs for recent activity
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Navigating to portal...")
        try:
            await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=15000)
        except:
            pass
        await page.wait_for_timeout(2000)

        await page.screenshot(path=f"{SS_DIR}/login-check-001.png")

        # Check DOM state
        dom_state = await page.evaluate("""
            () => {
                return {
                    title: document.title,
                    bodyText: document.body.innerText.substring(0, 500),
                    hasLoginForm: !!document.querySelector('input[type="password"], input[placeholder*="Bearer"]'),
                    hasChatMessages: !!document.querySelector('#chat-messages, .chat-messages, .msg'),
                    hasPortalShell: !!document.querySelector('.sidebar, .portal-container, .pb-portal'),
                    localStorage: Object.keys(localStorage).join(', '),
                    cookieCount: document.cookie.split(';').length
                };
            }
        """)
        print(f"DOM state: {json.dumps(dom_state, indent=2)}")

        # Check localStorage for any saved tokens
        local_storage = await page.evaluate("""
            () => {
                const items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    const val = localStorage.getItem(key);
                    items[key] = val ? val.substring(0, 100) : null;
                }
                return items;
            }
        """)
        print(f"LocalStorage: {json.dumps(local_storage, indent=2)}")

        # Now try to login
        print("\nAttempting login...")
        # Fill token
        for token in TOKENS_TO_TRY:
            pwd = await page.query_selector("input[type='password'], input[placeholder*='Bearer']")
            if pwd:
                await pwd.fill(token)
                print(f"  Trying token: {token[:20]}...")

                # Click login
                for btn_sel in [".pb-signin-btn", "#loginButton", "button[type='submit']", "button"]:
                    btn = await page.query_selector(btn_sel)
                    if btn and await btn.is_visible() and await btn.is_enabled():
                        txt = await btn.inner_text()
                        if any(w in txt.lower() for w in ['access', 'sign', 'login', 'enter', 'submit']):
                            print(f"  Clicking: '{txt}'")
                            await btn.click()
                            break

                await page.wait_for_timeout(5000)
                await page.screenshot(path=f"{SS_DIR}/login-check-002-after-{token[:8]}.png")

                # Check if logged in
                chat = await page.query_selector("#chat-messages, .chat-messages, .msg")
                has_messages = await page.evaluate("() => document.querySelectorAll('.msg, .message').length")
                print(f"  Chat found: {chat is not None}, Messages: {has_messages}")

                dom2 = await page.evaluate("""
                    () => {
                        const localStorage_items = {};
                        for (let i = 0; i < localStorage.length; i++) {
                            const k = localStorage.key(i);
                            localStorage_items[k] = localStorage.getItem(k);
                        }
                        return {
                            url: location.href,
                            bodyText: document.body.innerText.substring(0, 300),
                            localStorage: localStorage_items
                        };
                    }
                """)
                print(f"  After login: {json.dumps(dom2, indent=2)}")

                if chat or has_messages > 0:
                    print(f"  LOGIN SUCCESS with token {token[:20]}")
                    break

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
