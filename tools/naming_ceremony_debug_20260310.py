#!/usr/bin/env python3
"""
Naming Ceremony Debug Test - 2026-03-10
Captures detailed console logs, network requests, and JS execution state.
"""

import asyncio
import os
import json
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/naming-ceremony-test-20260310")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

def tg(msg):
    os.system(f'{TG_SEND} "QA: {msg}"')
    print(f"[TG] {msg}")

async def debug_page(page_key, url):
    print(f"\n{'='*60}")
    print(f"DEBUG: {page_key} - {url}")
    print(f"{'='*60}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        # Capture ALL console messages
        console_all = []
        page.on("console", lambda msg: console_all.append({
            "type": msg.type,
            "text": msg.text,
        }))

        # Capture network requests
        network_reqs = []
        page.on("request", lambda req: network_reqs.append({
            "url": req.url[:200],
            "method": req.method,
            "resource_type": req.resource_type,
        }))

        # Capture network responses
        network_resp = []
        page.on("response", lambda resp: network_resp.append({
            "url": resp.url[:200],
            "status": resp.status,
        }))

        # Capture page errors
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # Load page
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"[ERROR] Page load: {e}")

        await asyncio.sleep(4)

        # Take initial screenshot
        path = SCREENSHOTS_DIR / f"{page_key.replace('-','')}-debug-01-loaded.png"
        await page.screenshot(path=str(path))
        print(f"[SCREENSHOT] {path.name}")

        # Check JS availability
        print("[DEBUG] Checking JS state...")
        js_check = await page.evaluate("""() => {
            return {
                startConversation_exists: typeof window.startConversation === 'function',
                startConversation_type: typeof window.startConversation,
                chatInitial_exists: !!document.getElementById('chatInitial'),
                chatMessages_exists: !!document.getElementById('chatMessages'),
                userInput_exists: !!document.getElementById('userInput'),
                btn_exists: !!document.querySelector('.chat-initial__btn'),
                btn_visible: document.querySelector('.chat-initial__btn') ?
                    !document.querySelector('.chat-initial__btn').hidden : null,
                chatInput_exists: !!document.querySelector('.chat-input'),
                API_endpoint: typeof window.CF_WORKER_URL !== 'undefined' ? window.CF_WORKER_URL : 'not found',
                systemPrompt_defined: typeof window.SYSTEM_PROMPT !== 'undefined',
                total_scripts: document.querySelectorAll('script').length,
                all_global_keys: Object.keys(window).filter(k => k.includes('chat') || k.includes('Chat') || k.includes('conversation') || k.includes('start') || k.includes('Start')).slice(0, 20),
            };
        }""")
        print(f"[JS STATE] {json.dumps(js_check, indent=2)}")

        # Try to find the API endpoint in the HTML
        api_check = await page.evaluate("""() => {
            const scripts = [...document.querySelectorAll('script')];
            for (const s of scripts) {
                const text = s.textContent || '';
                if (text.includes('workers.dev') || text.includes('anthropic') || text.includes('claude')) {
                    const match = text.match(/https?:\/\/[^\s'"]+workers\.dev[^\s'"]+/);
                    if (match) return match[0];
                }
            }
            return 'not found in scripts';
        }""")
        print(f"[API ENDPOINT] {api_check}")

        # Click button
        btn = await page.query_selector(".chat-initial__btn")
        if btn:
            print("[DEBUG] Clicking begin button...")
            await btn.click()
            await asyncio.sleep(1)

            # Check immediately after click
            post_click = await page.evaluate("""() => {
                return {
                    typing_indicator: !!document.querySelector('.typing-indicator'),
                    typing_visible: document.querySelector('.typing-indicator') ?
                        getComputedStyle(document.querySelector('.typing-indicator')).display !== 'none' : false,
                    chatInput_active: !!document.querySelector('.chat-input.active'),
                    chatInitial_hidden: document.getElementById('chatInitial') ?
                        document.getElementById('chatInitial').style.display === 'none' ||
                        document.getElementById('chatInitial').hidden : null,
                    messages_count: document.querySelectorAll('.message--ai').length,
                }
            }""")
            print(f"[POST-CLICK STATE] {json.dumps(post_click, indent=2)}")

            # Screenshot after click
            path2 = SCREENSHOTS_DIR / f"{page_key.replace('-','')}-debug-02-after-click.png"
            await page.screenshot(path=str(path2))
            print(f"[SCREENSHOT] {path2.name}")

            # Wait longer for API response - 45 seconds
            print("[DEBUG] Waiting 45s for any API response...")
            for i in range(9):
                await asyncio.sleep(5)
                msg_count = await page.evaluate("document.querySelectorAll('.message--ai').length")
                typing_visible = await page.evaluate("""
                    () => {
                        const t = document.querySelector('.typing-indicator');
                        return t ? getComputedStyle(t).display !== 'none' : false;
                    }
                """)
                print(f"  [{(i+1)*5}s] AI messages: {msg_count}, typing: {typing_visible}")

                if msg_count > 0:
                    print(f"[SUCCESS] Got {msg_count} AI messages at {(i+1)*5}s!")
                    break

            final_count = await page.evaluate("document.querySelectorAll('.message--ai').length")
            print(f"[FINAL] AI message count: {final_count}")

            # Screenshot final state
            path3 = SCREENSHOTS_DIR / f"{page_key.replace('-','')}-debug-03-final.png"
            await page.screenshot(path=str(path3))
            print(f"[SCREENSHOT] {path3.name}")

            if final_count > 0:
                texts = await page.evaluate("""() => {
                    return [...document.querySelectorAll('.message--ai')].map(m => m.innerText.trim()).slice(0, 10);
                }""")
                print(f"[AI MESSAGES]:")
                for t in texts:
                    print(f"  '{t[:200]}'")

        # Print console
        print(f"\n[CONSOLE MESSAGES] Total: {len(console_all)}")
        for m in console_all:
            if m["type"] in ("error", "warning") or any(k in m["text"].lower() for k in ["api", "worker", "fetch", "cors", "fail", "error", "timeout", "attempt"]):
                print(f"  [{m['type'].upper()}] {m['text'][:300]}")

        # Print page errors
        if page_errors:
            print(f"\n[PAGE ERRORS] {len(page_errors)}")
            for e in page_errors:
                print(f"  {e[:300]}")

        # Print relevant network
        print(f"\n[NETWORK] Total requests: {len(network_reqs)}")
        api_requests = [r for r in network_reqs if "worker" in r["url"].lower() or "anthropic" in r["url"].lower() or "claude" in r["url"].lower() or "api" in r["url"].lower()]
        if api_requests:
            print("API-related requests:")
            for r in api_requests[:10]:
                print(f"  [{r['method']}] {r['url']}")

        print(f"\n[NETWORK RESPONSES] API-related:")
        api_responses = [r for r in network_resp if "worker" in r["url"].lower() or "anthropic" in r["url"].lower() or "api" in r["url"].lower()]
        for r in api_responses[:10]:
            print(f"  [{r['status']}] {r['url']}")

        await browser.close()
        return {
            "js_check": js_check,
            "api_endpoint": api_check,
            "console": [m for m in console_all if m["type"] in ("error", "warning")],
            "all_console": console_all,
            "page_errors": page_errors,
            "api_requests": api_requests,
            "api_responses": api_responses,
        }


async def main():
    tg("Running debug test to diagnose why AI messages not appearing...")

    for page_key, url in [
        ("pay-test-2", "https://purebrain-staging.pages.dev/pay-test-2/"),
        ("sandbox-3", "https://purebrain-staging.pages.dev/pay-test-sandbox-3/"),
    ]:
        result = await debug_page(page_key, url)

        # Send summary to TG
        js = result["js_check"]
        tg(f"{page_key} debug: startConversation={js.get('startConversation_exists')}, btn={js.get('btn_exists')}, api={result['api_endpoint'][:80]}, errors={len(result['page_errors'])}")

        # Save debug data
        debug_path = SCREENSHOTS_DIR / f"{page_key.replace('-','')}-debug-data.json"
        with open(debug_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"[SAVED] {debug_path}")

    tg("Debug test complete - check screenshots dir and debug JSON files")


if __name__ == "__main__":
    asyncio.run(main())
