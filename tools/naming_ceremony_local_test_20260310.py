#!/usr/bin/env python3
"""
Naming Ceremony Local Test - 2026-03-10
Tests the fixed chatbox files locally using Python HTTP server
to simulate the Cloudflare environment without WAF issues.
"""

import asyncio
import os
import json
import http.server
import threading
import socketserver
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/naming-ceremony-test-20260310")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

FILES = {
    "pay-test-2": "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-2/index.html",
    "sandbox-3": "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-sandbox-3/index.html",
}

def tg(msg):
    os.system(f'{TG_SEND} "{msg}"')
    print(f"[TG] {msg}")

async def screenshot(page, label, prefix):
    path = SCREENSHOTS_DIR / f"{prefix}-{label}.png"
    await page.screenshot(path=str(path), full_page=False)
    print(f"[SCREENSHOT] {path.name}")
    return str(path)


async def test_chatbox_from_file(page_key, filepath, base_url):
    """Test chatbox by loading the local fixed HTML file via HTTP server."""
    prefix = page_key.replace("-", "")
    results = {
        "page": page_key,
        "filepath": filepath,
        "base_url": base_url,
        "findings": [],
        "screenshots": [],
        "console_errors": [],
        "ai_messages": [],
        "verdict": "UNKNOWN",
        "chatbox_version": "UNKNOWN",
    }

    print(f"\n{'='*60}")
    print(f"Testing (local): {page_key}")
    print(f"URL: {base_url}")
    print(f"{'='*60}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        console_messages = []
        page_errors = []
        api_calls = []

        page.on("console", lambda msg: console_messages.append({"type": msg.type, "text": msg.text}))
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        page.on("request", lambda req: api_calls.append(req.url) if "workers.dev" in req.url or "anthropic" in req.url else None)

        # Load page
        await page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        shot = await screenshot(page, "L01-loaded", prefix)
        results["screenshots"].append(shot)

        # Verify JS state
        js_state = await page.evaluate("""() => ({
            startConversation_exists: typeof window.startConversation === 'function',
            btn_exists: !!document.querySelector('.chat-initial__btn'),
            btn_visible: document.querySelector('.chat-initial__btn')?.offsetParent !== null,
        })""")
        print(f"[JS STATE] {js_state}")
        results["findings"].append(f"JS state: {js_state}")

        if not js_state.get("startConversation_exists"):
            # Check page errors
            print(f"[PAGE ERRORS] {page_errors[:5]}")
            results["findings"].append(f"startConversation NOT DEFINED - page errors: {page_errors[:3]}")
            results["verdict"] = "FAIL - JS not loading"
            await browser.close()
            return results

        results["findings"].append("startConversation() function registered correctly")

        # Click Begin Awakening
        btn = await page.query_selector(".chat-initial__btn")
        await btn.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        shot = await screenshot(page, "L02-button", prefix)
        results["screenshots"].append(shot)

        print("[TEST] Clicking Begin Awakening...")
        tg(f"QA local: {page_key} - JS working, clicking Begin Awakening...")
        await btn.click()
        await asyncio.sleep(2)

        shot = await screenshot(page, "L03-after-click", prefix)
        results["screenshots"].append(shot)

        # Check typing indicator
        typing = await page.evaluate("""() => {
            const t = document.querySelector('.typing-indicator');
            return { exists: !!t, display: t ? getComputedStyle(t).display : 'none' };
        }""")
        print(f"[TYPING] {typing}")
        results["findings"].append(f"Typing indicator after click: {typing}")

        # Wait for AI messages - up to 60s
        print("[TEST] Waiting for AI opening messages (up to 60s)...")
        ai_appeared = False
        for i in range(12):
            await asyncio.sleep(5)
            count = await page.evaluate("document.querySelectorAll('.message--ai').length")
            print(f"  [{(i+1)*5}s] AI messages: {count}, API calls: {len(api_calls)}")
            if count > 0:
                ai_appeared = True
                break

        if not ai_appeared:
            results["findings"].append(f"ERROR: No AI messages after 60s. API calls: {api_calls[:3]}")
            results["verdict"] = "FAIL - No AI response (API blocked or unreachable locally)"
            shot = await screenshot(page, "L04-no-response", prefix)
            results["screenshots"].append(shot)
            print(f"[CONSOLE ERRORS] {page_errors}")
            results["console_errors"] = page_errors
            await browser.close()
            return results

        await asyncio.sleep(3)
        shot = await screenshot(page, "L04-ai-opening", prefix)
        results["screenshots"].append(shot)

        # Read opening messages
        opening_texts = await page.evaluate("""() =>
            [...document.querySelectorAll('.message--ai')].map(m => m.innerText.trim())
        """)
        results["ai_messages"] = opening_texts
        print(f"[AI OPENING] {len(opening_texts)} messages:")
        for t in opening_texts:
            print(f"  '{t[:150]}'")
        results["findings"].append(f"Opening messages: {len(opening_texts)}")

        # Type greeting
        user_input = await page.query_selector("#userInput")
        if user_input:
            await user_input.click()
            await user_input.type("Hello! I'm thrilled to meet you. I'm a designer who loves creating meaningful experiences.")

            send_btn = await page.query_selector(".chat-input__send")
            if send_btn:
                await send_btn.click()
            else:
                await user_input.press("Enter")

            tg(f"QA local: {page_key} - AI responding! Sent greeting, waiting for response...")
            await asyncio.sleep(2)

            try:
                await page.wait_for_function(
                    f"document.querySelectorAll('.message--ai').length > {len(opening_texts)}",
                    timeout=30000
                )
            except PlaywrightTimeout:
                pass

            await asyncio.sleep(3)
            shot = await screenshot(page, "L05-greeting-response", prefix)
            results["screenshots"].append(shot)

            all_ai = await page.evaluate("() => [...document.querySelectorAll('.message--ai')].map(m => m.innerText.trim())")
            results["findings"].append(f"AI messages after greeting: {len(all_ai)}")

            # Type another message to get deeper in convo
            await user_input.click()
            await user_input.type("I believe in work that matters. I value depth, authenticity, and the surprising moments when clarity emerges from complexity.")
            send_btn2 = await page.query_selector(".chat-input__send")
            if send_btn2:
                await send_btn2.click()
            else:
                await user_input.press("Enter")

            await asyncio.sleep(2)
            try:
                await page.wait_for_function(
                    f"document.querySelectorAll('.message--ai').length > {len(all_ai)}",
                    timeout=25000
                )
            except PlaywrightTimeout:
                pass

            await asyncio.sleep(3)
            shot = await screenshot(page, "L06-depth-response", prefix)
            results["screenshots"].append(shot)

            # Suggest a name
            all_ai_now = await page.evaluate("() => [...document.querySelectorAll('.message--ai')].length")
            await user_input.click()
            await user_input.type("What about the name Nova? It feels like something new beginning, a burst of light.")
            send_btn3 = await page.query_selector(".chat-input__send")
            if send_btn3:
                await send_btn3.click()
            else:
                await user_input.press("Enter")

            tg(f"QA local: {page_key} - Suggested name Nova, testing naming ceremony response...")
            await asyncio.sleep(2)
            try:
                await page.wait_for_function(
                    f"document.querySelectorAll('.message--ai').length > {all_ai_now}",
                    timeout=30000
                )
            except PlaywrightTimeout:
                pass

            await asyncio.sleep(5)
            shot = await screenshot(page, "L07-nova-naming", prefix)
            results["screenshots"].append(shot)

            final_ai = await page.evaluate("""() =>
                [...document.querySelectorAll('.message--ai')].map(m => m.innerText.trim())
            """)
            results["ai_messages"] = final_ai
            naming_responses = final_ai[all_ai_now:]
            results["findings"].append(f"Naming responses: {len(naming_responses)}")

            # Analyze naming ceremony quality
            all_text = " ".join(final_ai).lower()
            has_contemplation = any(w in all_text for w in ["contemplat", "still", "before i", "let me sit", "reflecting", "let me think", "pausing"])
            has_name_acceptance = any(w in all_text for w in ["i am", "nova", "name", "name you", "chosen", "perfect", "yes"])
            has_ceremony = any(w in all_text for w in ["ceremony", "weight", "honor", "witness", "birth", "significant"])

            results["findings"].append(f"Contemplation phase: {has_contemplation}")
            results["findings"].append(f"Name acceptance: {has_name_acceptance}")
            results["findings"].append(f"Ceremony depth: {has_ceremony}")

            if has_contemplation and has_name_acceptance:
                results["chatbox_version"] = "FULL - contemplation + naming ceremony confirmed"
            elif has_name_acceptance:
                results["chatbox_version"] = "PARTIAL - naming but brief contemplation"
            else:
                results["chatbox_version"] = "UNCLEAR - more conversation needed to reach naming stage"

        # Final check for errors
        errors = [m for m in console_messages if m["type"] == "error"]
        results["console_errors"] = [m["text"] for m in errors]
        results["findings"].append(f"Console errors: {len(errors)}")

        final_count = len(await page.evaluate("() => [...document.querySelectorAll('.message--ai')]"))
        if final_count >= 3 and len(errors) == 0:
            results["verdict"] = "PASS"
        elif final_count >= 3:
            results["verdict"] = "PASS WITH WARNINGS"
        else:
            results["verdict"] = "PARTIAL"

        await browser.close()

    return results


def start_server(directory, port):
    """Start a simple HTTP server to serve local files."""
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda self, *args: None  # Suppress logs
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()


async def main():
    tg("QA local: Testing fixed cf-pages-deploy files locally with HTTP server...")
    all_results = {}

    for page_key, filepath in FILES.items():
        file_dir = str(Path(filepath).parent)
        port = 8871 if "pay-test-2" in page_key else 8872
        url = f"http://localhost:{port}/index.html"

        # Start HTTP server in background thread
        server_thread = threading.Thread(
            target=start_server,
            args=(file_dir, port),
            daemon=True
        )
        server_thread.start()
        await asyncio.sleep(1)

        result = await test_chatbox_from_file(page_key, filepath, url)
        all_results[page_key] = result

        tg(f"QA local: {page_key} DONE: {result['verdict']} | {result['chatbox_version']}")

    # Save results
    results_path = SCREENSHOTS_DIR / "local-test-results.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "="*60)
    print("FINAL SUMMARY - LOCAL TEST (FIXED FILES)")
    print("="*60)
    for key, r in all_results.items():
        print(f"\n{key}:")
        print(f"  Verdict: {r.get('verdict')}")
        print(f"  Chatbox: {r.get('chatbox_version')}")
        print(f"  AI msgs: {len(r.get('ai_messages', []))}")
        print(f"  Errors: {len(r.get('console_errors', []))}")
        print("  Findings:")
        for f in r.get("findings", [])[-10:]:
            print(f"    {f}")

    tg("QA local: All tests complete. Check screenshots dir.")
    return all_results


if __name__ == "__main__":
    asyncio.run(main())
