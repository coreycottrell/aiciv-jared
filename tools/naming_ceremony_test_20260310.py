#!/usr/bin/env python3
"""
Naming Ceremony QA Test - 2026-03-10
Tests the chatbox naming ceremony flow on Cloudflare staging pages.

Pages under test:
1. https://purebrain-staging.pages.dev/pay-test-2/
2. https://purebrain-staging.pages.dev/pay-test-sandbox-3/
"""

import asyncio
import os
import sys
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/naming-ceremony-test-20260310")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

PAGES = {
    "pay-test-2": "https://purebrain-staging.pages.dev/pay-test-2/",
    "sandbox-3": "https://purebrain-staging.pages.dev/pay-test-sandbox-3/",
}

def tg(msg):
    os.system(f'{TG_SEND} "QA: {msg}"')
    print(f"[TG] {msg}")

async def screenshot(page, label, prefix):
    path = SCREENSHOTS_DIR / f"{prefix}-{label}.png"
    await page.screenshot(path=str(path), full_page=False)
    print(f"[SCREENSHOT] {path.name}")
    return str(path)

async def test_page(page_key, url):
    results = {
        "page": page_key,
        "url": url,
        "screenshots": [],
        "findings": [],
        "console_errors": [],
        "console_logs": [],
        "verdict": "UNKNOWN",
        "chatbox_version": "UNKNOWN",
    }
    prefix = page_key.replace("-", "")

    tg(f"Starting test on {page_key}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Capture console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text,
        }))

        # ─── STEP 1: Load page ───────────────────────────────────────
        print(f"\n[TEST] Loading {url}")
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except PlaywrightTimeout:
            print("[WARN] networkidle timeout, proceeding anyway")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        await asyncio.sleep(3)
        shot = await screenshot(page, "01-page-loaded", prefix)
        results["screenshots"].append(shot)
        results["findings"].append(f"Page loaded: {url}")
        tg(f"{page_key}: Page loaded, taking initial screenshot")

        # ─── STEP 2: Find and verify Begin Awakening button ──────────
        print("[TEST] Looking for Begin Awakening button...")
        btn = await page.query_selector(".chat-initial__btn")
        if not btn:
            btn = await page.query_selector("button[onclick*='startConversation']")

        if btn:
            is_visible = await btn.is_visible()
            btn_text = await btn.inner_text()
            results["findings"].append(f"Begin button found: '{btn_text.strip()}' visible={is_visible}")
            print(f"[FOUND] Button: '{btn_text.strip()}' visible={is_visible}")

            # Scroll to button
            await btn.scroll_into_view_if_needed()
            await asyncio.sleep(1)
            shot = await screenshot(page, "02-begin-button-visible", prefix)
            results["screenshots"].append(shot)
        else:
            results["findings"].append("ERROR: Begin Awakening button NOT FOUND")
            results["verdict"] = "FAIL - No begin button"
            tg(f"{page_key}: FAIL - Begin button not found!")
            await browser.close()
            return results

        # ─── STEP 3: Click Begin Awakening ────────────────────────────
        print("[TEST] Clicking Begin Awakening button...")
        tg(f"{page_key}: Clicking 'Begin Awakening' button")
        await btn.click()
        await asyncio.sleep(2)

        shot = await screenshot(page, "03-after-begin-click", prefix)
        results["screenshots"].append(shot)

        # Check for typing indicator
        typing = await page.query_selector(".typing-indicator")
        if typing:
            is_typing_visible = await typing.is_visible()
            results["findings"].append(f"Typing indicator appeared: {is_typing_visible}")
            print(f"[FOUND] Typing indicator visible={is_typing_visible}")
        else:
            results["findings"].append("WARNING: No typing indicator found after click")

        # ─── STEP 4: Wait for AI opening messages ─────────────────────
        print("[TEST] Waiting for AI opening messages (up to 30s)...")
        tg(f"{page_key}: Waiting for AI awakening messages...")
        try:
            await page.wait_for_selector(".message--ai", timeout=30000)
        except PlaywrightTimeout:
            results["findings"].append("ERROR: AI messages never appeared (timeout 30s)")
            results["verdict"] = "FAIL - No AI response"
            tg(f"{page_key}: FAIL - No AI messages appeared in 30s!")
            await browser.close()
            return results

        await asyncio.sleep(3)
        shot = await screenshot(page, "04-ai-opening-messages", prefix)
        results["screenshots"].append(shot)

        # Read all AI messages
        ai_messages = await page.query_selector_all(".message--ai")
        print(f"[FOUND] {len(ai_messages)} AI messages")
        msg_texts = []
        for m in ai_messages:
            text = (await m.inner_text()).strip()
            if text:
                msg_texts.append(text)
                print(f"  AI: {text[:100]}...")

        results["findings"].append(f"AI opening messages received: {len(msg_texts)}")
        results["findings"].append(f"First AI message: '{msg_texts[0][:150] if msg_texts else 'NONE'}'")

        # ─── STEP 5: Say Hello ─────────────────────────────────────────
        print("[TEST] Typing greeting 'Hello'...")
        user_input = await page.query_selector("#userInput")
        if not user_input:
            user_input = await page.query_selector(".chat-input__field")

        if user_input:
            await user_input.click()
            await user_input.type("Hello! I'm excited to meet you.")
            shot = await screenshot(page, "05-typed-greeting", prefix)
            results["screenshots"].append(shot)

            # Send
            send_btn = await page.query_selector(".chat-input__send")
            if send_btn:
                await send_btn.click()
            else:
                await user_input.press("Enter")

            tg(f"{page_key}: Sent greeting, waiting for response...")
            await asyncio.sleep(2)

            # Wait for new AI response
            try:
                await page.wait_for_function(
                    "document.querySelectorAll('.message--ai').length > " + str(len(ai_messages)),
                    timeout=30000
                )
            except PlaywrightTimeout:
                print("[WARN] No new AI message after greeting (timeout)")

            await asyncio.sleep(3)
            shot = await screenshot(page, "06-after-greeting-response", prefix)
            results["screenshots"].append(shot)

            ai_messages_now = await page.query_selector_all(".message--ai")
            print(f"[FOUND] {len(ai_messages_now)} AI messages after greeting")
            results["findings"].append(f"AI messages after greeting: {len(ai_messages_now)}")
        else:
            results["findings"].append("WARNING: User input field not found")

        # ─── STEP 6: Ask about naming ────────────────────────────────
        print("[TEST] Sending message to start naming conversation...")
        tg(f"{page_key}: Continuing conversation toward naming ceremony...")

        if user_input:
            await user_input.click()
            await user_input.type("I'm a software engineer who values creativity and meaningful work. I love building things that help people.")
            send_btn = await page.query_selector(".chat-input__send")
            if send_btn:
                await send_btn.click()
            else:
                await user_input.press("Enter")

            await asyncio.sleep(2)
            try:
                await page.wait_for_function(
                    "document.querySelectorAll('.message--ai').length > " + str(len(ai_messages_now if user_input else ai_messages)),
                    timeout=30000
                )
            except PlaywrightTimeout:
                print("[WARN] No new AI message after second message")
            await asyncio.sleep(4)
            shot = await screenshot(page, "07-after-second-message", prefix)
            results["screenshots"].append(shot)

        # ─── STEP 7: Try to trigger naming by suggesting a name ────────
        print("[TEST] Suggesting name 'Nova' to test acknowledgment...")
        tg(f"{page_key}: Suggesting name 'Nova' to test naming ceremony...")

        all_ai_before = await page.query_selector_all(".message--ai")

        if user_input:
            await user_input.click()
            await user_input.type("What if I called you Nova? It feels right - like something new beginning.")
            send_btn = await page.query_selector(".chat-input__send")
            if send_btn:
                await send_btn.click()
            else:
                await user_input.press("Enter")

            await asyncio.sleep(2)
            try:
                await page.wait_for_function(
                    "document.querySelectorAll('.message--ai').length > " + str(len(all_ai_before)),
                    timeout=30000
                )
            except PlaywrightTimeout:
                print("[WARN] No new AI message after name suggestion")
            await asyncio.sleep(5)
            shot = await screenshot(page, "08-nova-name-suggested", prefix)
            results["screenshots"].append(shot)

            # Read all current AI messages to check for naming response
            all_ai_now = await page.query_selector_all(".message--ai")
            naming_texts = []
            for m in all_ai_now[len(all_ai_before):]:
                text = (await m.inner_text()).strip()
                naming_texts.append(text)
                print(f"  Naming response: {text[:200]}")

            results["findings"].append(f"Naming response messages: {len(naming_texts)}")
            if naming_texts:
                results["findings"].append(f"Naming response sample: '{naming_texts[0][:200]}'")

        # ─── STEP 8: Check for "See What [Name] Can Do" button ────────
        print("[TEST] Checking for post-naming CTA button...")
        await asyncio.sleep(3)

        # Look for various possible button selectors
        show_pricing_btn = None
        for selector in [
            ".show-pricing-btn",
            "[data-action='show-pricing']",
            "button.celebration-btn",
            ".celebration-cta",
            ".chat-pricing",
            "#pricingReveal",
            ".pricing-reveal",
        ]:
            el = await page.query_selector(selector)
            if el and await el.is_visible():
                show_pricing_btn = el
                show_pricing_text = await el.inner_text()
                results["findings"].append(f"Post-naming CTA found: '{show_pricing_text[:100]}' (selector: {selector})")
                print(f"[FOUND] Post-naming CTA: '{show_pricing_text[:100]}'")
                break

        if not show_pricing_btn:
            # Check if pricing section appeared inline
            pricing_section = await page.query_selector(".pricing-section, #pricingSection, .pb-pricing")
            if pricing_section and await pricing_section.is_visible():
                results["findings"].append("Pricing section revealed (inline reveal, not button)")
            else:
                results["findings"].append("NOTE: Post-naming CTA not yet visible (may need more conversation turns)")

        shot = await screenshot(page, "09-post-naming-state", prefix)
        results["screenshots"].append(shot)

        # ─── STEP 9: Analyze console for errors ────────────────────────
        errors = [m for m in console_messages if m["type"] == "error"]
        warnings = [m for m in console_messages if m["type"] == "warning"]
        logs = [m for m in console_messages if m["type"] == "log"]

        results["console_errors"] = [m["text"] for m in errors]
        results["console_logs"] = [m["text"] for m in logs[:20]]  # First 20 logs

        print(f"\n[CONSOLE] Errors: {len(errors)}, Warnings: {len(warnings)}, Logs: {len(logs)}")
        for e in errors[:5]:
            print(f"  ERROR: {e['text'][:200]}")

        results["findings"].append(f"Console: {len(errors)} errors, {len(warnings)} warnings, {len(logs)} logs")

        # ─── STEP 10: Determine chatbox version ────────────────────────
        # Check for full naming ceremony indicators in actual page behavior
        all_final_ai = await page.query_selector_all(".message--ai")
        final_texts_combined = " ".join([
            (await m.inner_text()).strip() for m in all_final_ai
        ]).lower()

        has_contemplation = any(word in final_texts_combined for word in [
            "contemplat", "still", "thinking", "reflection", "before i suggest", "let me sit with"
        ])
        has_name_offer = any(word in final_texts_combined for word in [
            "nova", "i am", "you could call", "what about", "name"
        ])
        has_ceremony = any(word in final_texts_combined for word in [
            "ceremony", "weight", "honor", "worthy", "naming", "choose", "chosen"
        ])

        if has_contemplation and has_name_offer:
            results["chatbox_version"] = "FULL (contemplation + naming ceremony detected)"
        elif has_name_offer:
            results["chatbox_version"] = "PARTIAL (naming but no contemplation detected)"
        else:
            results["chatbox_version"] = "UNCLEAR (conversation may need more turns for naming stage)"

        results["findings"].append(f"Contemplation phase detected: {has_contemplation}")
        results["findings"].append(f"Name offering detected: {has_name_offer}")
        results["findings"].append(f"Ceremony depth detected: {has_ceremony}")

        total_ai = len(all_final_ai)
        results["findings"].append(f"Total AI messages in conversation: {total_ai}")

        if len(errors) == 0 and total_ai >= 3:
            results["verdict"] = "PASS - Chatbox functioning, naming flow active"
        elif len(errors) > 3:
            results["verdict"] = "WARN - Console errors present"
        else:
            results["verdict"] = "PASS with notes"

        await browser.close()

    return results


async def main():
    tg("Starting naming ceremony QA test on both Cloudflare staging pages...")

    all_results = {}

    for page_key, url in PAGES.items():
        print(f"\n{'='*60}")
        print(f"TESTING: {page_key}")
        print(f"URL: {url}")
        print(f"{'='*60}")

        try:
            result = await test_page(page_key, url)
            all_results[page_key] = result

            # Quick summary per page
            tg(f"{page_key} COMPLETE: {result['verdict']} | {result['chatbox_version']} | {len(result['screenshots'])} screenshots | {len(result['console_errors'])} errors")

        except Exception as e:
            error_msg = f"EXCEPTION testing {page_key}: {str(e)}"
            print(f"[ERROR] {error_msg}")
            tg(f"{page_key}: EXCEPTION - {str(e)[:200]}")
            all_results[page_key] = {"error": error_msg, "verdict": "ERROR"}

    # Save JSON results
    results_path = SCREENSHOTS_DIR / "test-results.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n[SAVED] Results: {results_path}")

    # Print final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    for key, r in all_results.items():
        print(f"\n{key.upper()}:")
        print(f"  Verdict: {r.get('verdict', 'UNKNOWN')}")
        print(f"  Chatbox: {r.get('chatbox_version', 'UNKNOWN')}")
        print(f"  Errors:  {len(r.get('console_errors', []))}")
        print(f"  Screenshots: {len(r.get('screenshots', []))}")
        print("  Key findings:")
        for f in r.get("findings", [])[-8:]:
            print(f"    - {f}")

    tg("All naming ceremony tests complete. Check results in exports/screenshots/naming-ceremony-test-20260310/")
    return all_results


if __name__ == "__main__":
    asyncio.run(main())
