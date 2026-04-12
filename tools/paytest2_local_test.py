#!/usr/bin/env python3
"""
Pay-Test-2 Local Chatbox Test - 2026-02-27
Serves the page locally to test UI without WAF interference.
Tests: Begin Awakening button renders, is clickable, chatbox starts.
"""

import asyncio
import http.server
import threading
import time
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-verify-20260227")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOCAL_HTML_PATH = "/tmp/paytest2_local.html"
LOCAL_PORT = 8742

def start_local_server():
    """Start a simple HTTP server for the local test."""
    import os
    os.chdir("/tmp")

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress logs

    server = http.server.HTTPServer(('127.0.0.1', LOCAL_PORT), QuietHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

async def run():
    print("=== Pay-Test-2 Local Chatbox Test ===\n")

    # Start local server
    print(f"Step 1: Starting local HTTP server on port {LOCAL_PORT}...")
    server = start_local_server()
    time.sleep(0.5)
    print("  Server running")

    local_url = f"http://127.0.0.1:{LOCAL_PORT}/paytest2_local.html"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",  # Allow cross-origin for local testing
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )

        page = await context.new_page()

        # Capture console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text
        }))

        # Capture JS errors
        js_errors = []
        page.on("pageerror", lambda err: js_errors.append(str(err)))

        print(f"\nStep 2: Navigating to local test page...")
        response = await page.goto(local_url, wait_until="domcontentloaded", timeout=30000)
        print(f"  HTTP status: {response.status}")

        await asyncio.sleep(3)

        await page.screenshot(path=str(OUTPUT_DIR / "local-001-initial.png"))
        print("  Screenshot local-001 saved: initial page state")

        # Wait for JS initialization
        await asyncio.sleep(2)

        # Full page screenshot
        await page.screenshot(path=str(OUTPUT_DIR / "local-002-full.png"), full_page=True)
        print("  Screenshot local-002 saved: full page")

        # --- Check page content ---
        print("\nStep 3: Checking page structure...")
        page_text = await page.evaluate("document.body.innerText")
        print(f"  Page text (first 200): {page_text[:200]}")

        if "Begin Awakening" in page_text:
            print("  'Begin Awakening' text FOUND in rendered page!")
        else:
            print("  'Begin Awakening' NOT in rendered text")

        # Check specific elements
        print("\nStep 4: Element inventory...")

        # Chat initial container
        chat_initial = await page.query_selector(".chat-initial, #chatInitial")
        if chat_initial:
            is_vis = await chat_initial.is_visible()
            print(f"  .chat-initial: FOUND (visible={is_vis})")
        else:
            print("  .chat-initial: NOT FOUND")

        # Begin Awakening button
        begin_btn = await page.query_selector(".chat-initial__btn")
        if begin_btn:
            is_vis = await begin_btn.is_visible()
            txt = await begin_btn.inner_text()
            cls = await begin_btn.get_attribute("class")
            print(f"  .chat-initial__btn: FOUND (visible={is_vis}, text='{txt.strip()}', class='{cls}')")
        else:
            # Try alternative
            begin_btn = await page.query_selector("button:has-text('Begin Awakening')")
            if begin_btn:
                is_vis = await begin_btn.is_visible()
                print(f"  button:has-text('Begin Awakening'): FOUND (visible={is_vis})")
            else:
                print("  .chat-initial__btn: NOT FOUND")
                print("  button:has-text('Begin Awakening'): NOT FOUND")

        # Chat messages container
        chat_msgs = await page.query_selector("#chatMessages")
        if chat_msgs:
            is_vis = await chat_msgs.is_visible()
            print(f"  #chatMessages: FOUND (visible={is_vis})")
        else:
            print("  #chatMessages: NOT FOUND")

        # User input
        user_input = await page.query_selector("#userInput")
        if user_input:
            is_vis = await user_input.is_visible()
            print(f"  #userInput: FOUND (visible={is_vis})")
        else:
            print("  #userInput: NOT FOUND")

        # Typing indicator
        typing_ind = await page.query_selector("#typingIndicator, .typing-indicator")
        if typing_ind:
            is_vis = await typing_ind.is_visible()
            print(f"  typingIndicator: FOUND (visible={is_vis})")
        else:
            print("  typingIndicator: NOT FOUND")

        # All buttons
        all_buttons = await page.query_selector_all("button")
        print(f"\n  Total buttons: {len(all_buttons)}")
        for i, btn in enumerate(all_buttons[:10]):
            try:
                txt = await btn.inner_text()
                vis = await btn.is_visible()
                cls = await btn.get_attribute("class") or ""
                print(f"    [{i+1}] '{txt.strip()[:60]}' visible={vis} class='{cls[:40]}'")
            except:
                pass

        # --- Test: Click the Begin Awakening button ---
        print("\nStep 5: Testing Begin Awakening click...")

        if begin_btn:
            is_vis = await begin_btn.is_visible()
            if is_vis:
                print("  Button is visible - clicking...")
                await page.screenshot(path=str(OUTPUT_DIR / "local-003-before-begin.png"))

                await begin_btn.click()
                print("  Clicked! Waiting for typing indicator...")
                await asyncio.sleep(2)

                await page.screenshot(path=str(OUTPUT_DIR / "local-004-after-begin-2s.png"))
                print("  Screenshot local-004 saved: 2s after click")

                # Check typing indicator
                typing_el = await page.query_selector("#typingIndicator, .typing-indicator")
                if typing_el:
                    vis = await typing_el.is_visible()
                    print(f"  Typing indicator visible: {vis}")

                # Wait for AI response (API call)
                print("  Waiting for AI response (up to 20s)...")
                await asyncio.sleep(10)

                await page.screenshot(path=str(OUTPUT_DIR / "local-005-after-10s.png"))
                print("  Screenshot local-005 saved: 10s after click")

                await asyncio.sleep(10)
                await page.screenshot(path=str(OUTPUT_DIR / "local-006-after-20s.png"))
                print("  Screenshot local-006 saved: 20s after click")

                # Check for AI messages
                ai_msgs = await page.query_selector_all(".message--ai")
                print(f"\n  AI messages found: {len(ai_msgs)}")
                if ai_msgs:
                    for i, msg in enumerate(ai_msgs[:3]):
                        txt = await msg.inner_text()
                        print(f"    AI msg {i+1}: '{txt[:200]}'")
                else:
                    print("  No AI messages found - checking why...")
                    # Check console for errors
                    api_errors = [m for m in console_messages if "error" in m["type"].lower()]
                    print(f"  Console errors: {len(api_errors)}")
                    for e in api_errors[:5]:
                        print(f"    {e['text'][:200]}")

                # Check user messages (should show the initial prompt)
                user_msgs = await page.query_selector_all(".message--user")
                print(f"\n  User messages: {len(user_msgs)}")

                # Check if chat input appeared
                chat_input_active = await page.query_selector(".chat-input.active, #chatInput.active")
                print(f"  Chat input active: {chat_input_active is not None}")

            else:
                print("  Button found but NOT VISIBLE")
                await page.screenshot(path=str(OUTPUT_DIR / "local-003-btn-not-visible.png"))
        else:
            print("  BEGIN BUTTON NOT FOUND ON LOCAL PAGE")
            # Dump structure
            body = await page.content()
            (OUTPUT_DIR / "local-page-content.txt").write_text(body[:10000])
            print("  Page content saved to local-page-content.txt")

        # Final console log summary
        print("\n--- Console Summary (Local Test) ---")
        errors = [m for m in console_messages if m["type"] == "error"]
        warnings = [m for m in console_messages if m["type"] == "warning"]
        logs = [m for m in console_messages if m["type"] == "log"]

        print(f"  Errors: {len(errors)}")
        for e in errors[:8]:
            print(f"    ERROR: {e['text'][:300]}")

        print(f"  Warnings: {len(warnings)}")
        for w in warnings[:5]:
            print(f"    WARN: {w['text'][:200]}")

        print(f"  Logs: {len(logs)}")
        for l in logs[:10]:
            print(f"    LOG: {l['text'][:200]}")

        if js_errors:
            print(f"\n  JS Page Errors: {len(js_errors)}")
            for e in js_errors[:5]:
                print(f"    {e[:300]}")

        await browser.close()
        server.shutdown()

    print(f"\n=== Done. Screenshots in: {OUTPUT_DIR} ===")
    for f in sorted(OUTPUT_DIR.glob("local-*.png")):
        print(f"  {f.name}")

if __name__ == "__main__":
    asyncio.run(run())
