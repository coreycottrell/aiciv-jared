#!/usr/bin/env python3
"""
Pay-Test-2 Chatbox Verification Script - 2026-02-27
Verifies: Begin Awakening button visible, clickable, chatbox responds
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-verify-20260227")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_URL = "https://purebrain.ai/pay-test-2/"
PASSWORD = "PureBrain.ai253443$"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
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

        print("Step 1: Navigating to pay-test-2...")
        response = await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        print(f"  HTTP status: {response.status}")

        await asyncio.sleep(2)
        await page.screenshot(path=str(OUTPUT_DIR / "001-initial-load.png"))
        print("  Screenshot 001 saved: initial page load")

        # Check if password form is present
        pw_field = await page.query_selector("input[id^='pwbox-']")
        if pw_field:
            print("Step 2: Password form detected - entering password...")
            await pw_field.fill(PASSWORD)
            await page.screenshot(path=str(OUTPUT_DIR / "002-password-filled.png"))
            print("  Screenshot 002 saved: password filled")

            # Submit the form
            form = await page.query_selector("form[action*='protectedpage']") or await page.query_selector("input[name='Submit']")
            submit_btn = await page.query_selector("input[name='Submit']") or await page.query_selector("input[type='submit']")

            if submit_btn:
                print("  Found submit button, clicking...")
                await submit_btn.click()
            else:
                print("  No submit button found, pressing Enter...")
                await pw_field.press("Enter")

            print("  Waiting for page to load after password...")
            await page.wait_for_load_state("networkidle", timeout=20000)
            await asyncio.sleep(3)
        else:
            print("Step 2: No password form found (already unlocked or form not detected)")

        await page.screenshot(path=str(OUTPUT_DIR / "003-after-password.png"))
        print("  Screenshot 003 saved: after password submission")

        # Check current URL and page title
        current_url = page.url
        title = await page.title()
        print(f"  Current URL: {current_url}")
        print(f"  Page title: {title}")

        # Wait a bit more for JS to initialize
        await asyncio.sleep(4)

        # Capture full page state
        await page.screenshot(path=str(OUTPUT_DIR / "004-page-loaded.png"), full_page=True)
        print("  Screenshot 004 saved: full page loaded")

        # --- Look for Begin Awakening button ---
        print("\nStep 3: Looking for 'Begin Awakening' button...")

        # Try multiple selectors based on prior knowledge
        begin_btn = None
        selectors_tried = []

        # Primary selector from memory
        for selector in [
            ".chat-initial__btn",
            "button:has-text('Begin Awakening')",
            ".chat-initial button",
            "button[onclick*='startConversation']",
            "button.begin-btn",
            "[class*='initial'] button",
            "button:has-text('Begin')",
        ]:
            el = await page.query_selector(selector)
            selectors_tried.append(f"{selector}: {'FOUND' if el else 'not found'}")
            if el and not begin_btn:
                begin_btn = el
                print(f"  Found Begin button via selector: {selector}")

        print("\n  Selector results:")
        for s in selectors_tried:
            print(f"    {s}")

        # Check chatbox container
        print("\nStep 4: Checking chatbox container...")
        chat_container = None
        for selector in [
            "#chatMessages",
            ".chat-container",
            ".chat-initial",
            "[class*='chat']",
            "#chat-wrapper",
        ]:
            el = await page.query_selector(selector)
            if el:
                is_visible = await el.is_visible()
                print(f"  Found: {selector} (visible: {is_visible})")
                if not chat_container:
                    chat_container = el

        # Check if Begin button is visible
        if begin_btn:
            is_visible = await begin_btn.is_visible()
            btn_text = await begin_btn.inner_text()
            btn_classes = await begin_btn.get_attribute("class")
            print(f"\n  Begin button text: '{btn_text}'")
            print(f"  Begin button classes: {btn_classes}")
            print(f"  Begin button visible: {is_visible}")

            # Take screenshot showing button state
            await page.screenshot(path=str(OUTPUT_DIR / "005-before-click.png"))
            print("  Screenshot 005 saved: before clicking Begin")

            if is_visible:
                print("\nStep 5: Clicking 'Begin Awakening' button...")
                await begin_btn.click()
                print("  Clicked! Waiting for response...")
                await asyncio.sleep(5)  # Wait for typing indicator + response

                await page.screenshot(path=str(OUTPUT_DIR / "006-after-click.png"))
                print("  Screenshot 006 saved: immediately after click")

                await asyncio.sleep(5)  # Wait more for API response
                await page.screenshot(path=str(OUTPUT_DIR / "007-waiting-response.png"))
                print("  Screenshot 007 saved: waiting for chatbox response")

                await asyncio.sleep(8)  # Give more time for Claude to respond
                await page.screenshot(path=str(OUTPUT_DIR / "008-final-state.png"))
                print("  Screenshot 008 saved: final state after response")

                # Check for typing indicator
                typing_indicator = await page.query_selector("#typingIndicator")
                if typing_indicator:
                    is_shown = await typing_indicator.is_visible()
                    print(f"\n  Typing indicator visible: {is_shown}")

                # Check for AI messages
                ai_messages = await page.query_selector_all(".message--ai")
                user_messages = await page.query_selector_all(".message--user")
                print(f"  AI messages found: {len(ai_messages)}")
                print(f"  User messages found: {len(user_messages)}")

                if ai_messages:
                    first_msg = await ai_messages[0].inner_text()
                    print(f"\n  First AI message: '{first_msg[:200]}'")

            else:
                print("  Begin button found but NOT VISIBLE - possible CSS issue")
        else:
            print("\n  WARNING: 'Begin Awakening' button NOT FOUND with any selector")
            # Dump page structure for debugging
            body_html = await page.evaluate("document.body.innerHTML")
            snippet_path = OUTPUT_DIR / "page-body-snippet.txt"
            snippet_path.write_text(body_html[:5000])
            print(f"  Page body snippet saved to: {snippet_path}")

        # Final console log check
        print("\n--- Console Messages ---")
        errors = [m for m in console_messages if m["type"] == "error"]
        warnings = [m for m in console_messages if m["type"] == "warning"]
        infos = [m for m in console_messages if m["type"] == "log"]

        print(f"  Errors: {len(errors)}")
        for e in errors[:5]:
            print(f"    ERROR: {e['text'][:200]}")

        print(f"  Warnings: {len(warnings)}")
        for w in warnings[:3]:
            print(f"    WARN: {w['text'][:200]}")

        print(f"  Logs: {len(infos)}")
        for l in infos[:5]:
            print(f"    LOG: {l['text'][:200]}")

        # Check for specific JSON error patterns
        json_errors = [m for m in console_messages if "json" in m["text"].lower() or "parse" in m["text"].lower() or "syntax" in m["text"].lower()]
        if json_errors:
            print(f"\n  JSON/Syntax related messages: {len(json_errors)}")
            for j in json_errors:
                print(f"    {j['type'].upper()}: {j['text'][:300]}")

        await browser.close()

        print(f"\n--- Screenshots saved to: {OUTPUT_DIR} ---")
        screenshots = list(OUTPUT_DIR.glob("*.png"))
        for s in sorted(screenshots):
            print(f"  {s.name}")

    return str(OUTPUT_DIR)

if __name__ == "__main__":
    asyncio.run(run())
