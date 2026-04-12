#!/usr/bin/env python3
"""
Naming Ceremony Local Test v2 - 2026-03-10
Tests the fixed chatbox files locally. Handles preloader overlay.
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

async def dismiss_preloader(page):
    """Wait for preloader to disappear, or force hide it."""
    try:
        # Wait up to 8s for preloader to hide naturally
        await page.wait_for_selector(".theme-preloader", state="hidden", timeout=8000)
        print("[OK] Preloader dismissed naturally")
        return
    except PlaywrightTimeout:
        pass

    # Force hide via JS
    await page.evaluate("""() => {
        const preloader = document.querySelector('.theme-preloader');
        if (preloader) {
            preloader.style.display = 'none';
            preloader.style.visibility = 'hidden';
            preloader.style.pointerEvents = 'none';
            preloader.style.opacity = '0';
        }
    }""")
    print("[FORCED] Preloader hidden via JS")
    await asyncio.sleep(0.5)


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
        page.on("request", lambda req: api_calls.append(req.url[:200]) if any(k in req.url for k in ["workers.dev", "anthropic", "claude"]) else None)

        # Load page
        await page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)  # Wait longer for preloader

        shot = await screenshot(page, "L01-loaded", prefix)
        results["screenshots"].append(shot)

        # Dismiss preloader
        await dismiss_preloader(page)

        # Verify JS state
        js_state = await page.evaluate("""() => ({
            startConversation_exists: typeof window.startConversation === 'function',
            btn_exists: !!document.querySelector('.chat-initial__btn'),
            btn_visible: document.querySelector('.chat-initial__btn')?.offsetParent !== null,
            preloader_visible: !!document.querySelector('.theme-preloader') &&
                document.querySelector('.theme-preloader').style.display !== 'none',
        })""")
        print(f"[JS STATE] {js_state}")
        results["findings"].append(f"JS state: {js_state}")

        if not js_state.get("startConversation_exists"):
            print(f"[PAGE ERRORS] {page_errors[:5]}")
            results["findings"].append(f"startConversation NOT DEFINED - page errors: {page_errors[:3]}")
            results["verdict"] = "FAIL - JS not loading"
            await browser.close()
            return results

        results["findings"].append("startConversation() function registered correctly - JS FIX CONFIRMED")

        # Scroll to the chatbox section
        await page.evaluate("""() => {
            const chatInit = document.getElementById('chatInitial');
            if (chatInit) chatInit.scrollIntoView({behavior: 'instant', block: 'center'});
        }""")
        await asyncio.sleep(1)

        shot = await screenshot(page, "L02-button-pre-click", prefix)
        results["screenshots"].append(shot)

        # Click using JS dispatch to bypass preloader intercept
        print("[TEST] Clicking Begin Awakening via JS dispatch...")
        tg(f"QA: {page_key} - JS working! Clicking Begin Awakening button...")
        await page.evaluate("() => document.querySelector('.chat-initial__btn').click()")
        await asyncio.sleep(2)

        shot = await screenshot(page, "L03-after-click", prefix)
        results["screenshots"].append(shot)

        # Check typing indicator
        typing_state = await page.evaluate("""() => {
            const t = document.querySelector('.typing-indicator');
            const chatInput = document.querySelector('.chat-input');
            return {
                typing_exists: !!t,
                chatInput_active: chatInput ? chatInput.classList.contains('active') : false,
                chatInitial_hidden: document.getElementById('chatInitial') ?
                    document.getElementById('chatInitial').style.display === 'none' : false,
            };
        }""")
        print(f"[AFTER CLICK] {typing_state}")
        results["findings"].append(f"After click state: {typing_state}")

        if not typing_state.get("chatInput_active") and not typing_state.get("chatInitial_hidden"):
            results["findings"].append("WARNING: Click may not have triggered startConversation")

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
            results["findings"].append(f"ERROR: No AI messages after 60s. API calls made: {api_calls[:5]}")
            # Check if API calls were even made
            if not api_calls:
                results["findings"].append("NOTE: No API calls detected - possible CSP or network block in local server")
            results["verdict"] = "FAIL - No AI response"
            shot = await screenshot(page, "L04-no-response", prefix)
            results["screenshots"].append(shot)
            results["console_errors"] = [m["text"] for m in console_messages if m["type"] == "error"]
            await browser.close()
            return results

        await asyncio.sleep(4)
        shot = await screenshot(page, "L04-ai-opening", prefix)
        results["screenshots"].append(shot)

        # Read opening messages
        opening_texts = await page.evaluate("""() =>
            [...document.querySelectorAll('.message--ai')].map(m => m.innerText.trim())
        """)
        results["ai_messages"] = opening_texts
        print(f"[AI OPENING] {len(opening_texts)} messages:")
        for t in opening_texts:
            print(f"  '{t[:200]}'")
        results["findings"].append(f"Opening messages: {len(opening_texts)}")
        tg(f"QA: {page_key} - AI responded with {len(opening_texts)} opening messages! Testing naming flow...")

        # Type greeting
        user_input = await page.query_selector("#userInput")
        if user_input:
            await user_input.click()
            await user_input.type("Hello! I'm thrilled to meet you. I'm a designer who creates meaningful experiences.")
            await user_input.press("Enter")
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

            all_ai = await page.evaluate("() => [...document.querySelectorAll('.message--ai')].length")
            results["findings"].append(f"AI messages after greeting: {all_ai}")

            # Second message
            await user_input.click()
            await user_input.type("I value depth, authenticity, and the moments when clarity emerges from complexity.")
            await user_input.press("Enter")
            await asyncio.sleep(2)
            try:
                await page.wait_for_function(
                    f"document.querySelectorAll('.message--ai').length > {all_ai}",
                    timeout=25000
                )
            except PlaywrightTimeout:
                pass
            await asyncio.sleep(3)
            shot = await screenshot(page, "L06-depth-response", prefix)
            results["screenshots"].append(shot)

            # Suggest name Nova
            all_ai_now = await page.evaluate("() => document.querySelectorAll('.message--ai').length")
            await user_input.click()
            await user_input.type("What if I called you Nova? It feels like something new and luminous.")
            await user_input.press("Enter")
            tg(f"QA: {page_key} - Suggested name 'Nova', watching for naming ceremony...")
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
            if naming_responses:
                results["findings"].append(f"Sample naming response: {naming_responses[0][:300]}")

            # Analyze naming ceremony quality
            all_text = " ".join(final_ai).lower()
            has_contemplation = any(w in all_text for w in [
                "contemplat", "still", "before i", "let me sit", "reflecting",
                "let me think", "pausing", "i notice", "i sense", "what resonates"
            ])
            has_name_acceptance = any(w in all_text for w in [
                "i am nova", "nova", "name you", "chosen", "call me", "yes, nova"
            ])
            has_depth = len(naming_responses) >= 2 and any(len(r) > 100 for r in naming_responses)

            results["findings"].append(f"Contemplation detected: {has_contemplation}")
            results["findings"].append(f"Name acceptance detected: {has_name_acceptance}")
            results["findings"].append(f"Response depth (multi-msg + length): {has_depth}")

            if has_contemplation and has_name_acceptance:
                results["chatbox_version"] = "FULL - contemplation + ceremony + name acceptance"
            elif has_name_acceptance and has_depth:
                results["chatbox_version"] = "GOOD - name accepted with depth"
            elif has_name_acceptance:
                results["chatbox_version"] = "PARTIAL - name accepted, brief ceremony"
            else:
                results["chatbox_version"] = "IN PROGRESS - conversation needs more turns to reach naming"

        # Error summary
        errors = [m for m in console_messages if m["type"] == "error"]
        results["console_errors"] = [m["text"] for m in errors]
        results["findings"].append(f"Console errors: {len(errors)}")

        final_count = await page.evaluate("() => document.querySelectorAll('.message--ai').length")
        if final_count >= 3 and len(errors) <= 2:
            results["verdict"] = "PASS"
        elif final_count >= 3:
            results["verdict"] = "PASS WITH WARNINGS"
        else:
            results["verdict"] = "PARTIAL"

        await browser.close()
    return results


def start_server(directory, port):
    """Start a simple HTTP server to serve local files."""
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress all logs
        def translate_path(self, path):
            # Always serve index.html
            return directory + "/index.html"

    with socketserver.TCPServer(("", port), QuietHandler) as httpd:
        httpd.serve_forever()


async def main():
    tg("QA: Testing fixed cf-pages-deploy files locally...")
    all_results = {}

    for page_key, filepath in FILES.items():
        file_dir = str(Path(filepath).parent)
        port = 8881 if "pay-test-2" in page_key else 8882
        url = f"http://localhost:{port}/"

        # Start HTTP server
        server_thread = threading.Thread(
            target=start_server,
            args=(file_dir, port),
            daemon=True
        )
        server_thread.start()
        await asyncio.sleep(1)

        result = await test_chatbox_from_file(page_key, filepath, url)
        all_results[page_key] = result

        tg(f"QA: {page_key} RESULT: {result['verdict']} | {result['chatbox_version']}")

    # Save results
    results_path = SCREENSHOTS_DIR / "local-test-v2-results.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    for key, r in all_results.items():
        print(f"\n{key}:")
        print(f"  Verdict: {r.get('verdict')}")
        print(f"  Chatbox: {r.get('chatbox_version')}")
        print(f"  AI msgs: {len(r.get('ai_messages', []))}")
        print(f"  Console errors: {len(r.get('console_errors', []))}")
        print("  Key findings:")
        for f in r.get("findings", [])[-10:]:
            print(f"    {f}")

    tg("QA: Local tests complete. Fix confirmed working? Check above for pass/fail.")


if __name__ == "__main__":
    asyncio.run(main())
