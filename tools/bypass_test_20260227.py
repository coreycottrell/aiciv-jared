#!/usr/bin/env python3
"""
Bypass Test - Full Visual Proof
Tests pb-full-bypass and Jared's natural language bypass on pay-test-2
Date: 2026-02-27
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/docs/bypass-test")
TARGET_URL = "https://purebrain.ai/pay-test-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"


async def screenshot(page, name, full_page=True):
    path = SCREENSHOTS_DIR / name
    await page.screenshot(path=str(path), full_page=full_page)
    print(f"[SCREENSHOT] Saved: {path}")
    return path


async def enter_password(page):
    """Enter WP page password if password form is present."""
    pw_input = page.locator("input[id^='pwbox-']")
    if await pw_input.count() > 0:
        print("  Password form found - entering password...")
        await pw_input.first.fill(PAGE_PASSWORD)
        await page.keyboard.press("Enter")
        await page.wait_for_load_state("networkidle", timeout=15000)
        await page.wait_for_timeout(2000)
        print("  Password submitted, page reloaded.")
        return True
    else:
        print("  No password form - page loaded directly.")
        return False


async def wait_for_ai_response(page, timeout_ms=30000):
    """Wait for an AI message to appear in the chat."""
    try:
        await page.wait_for_selector(".message--ai", timeout=timeout_ms)
        print("  AI message appeared!")
        return True
    except Exception:
        # Check typing indicator
        typing = await page.query_selector("#typingIndicator")
        if typing:
            print("  Typing indicator active - waiting longer...")
            await page.wait_for_timeout(15000)
            # Check again
            msgs = await page.query_selector_all(".message--ai")
            if msgs:
                print("  AI message appeared after extended wait!")
                return True
        print("  WARNING: No AI message found within timeout")
        return False


async def run_bypass_test():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    console_logs = []
    js_errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )

        page = await context.new_page()
        page.on("console", lambda msg: console_logs.append(f"[{msg.type.upper()}] {msg.text}"))
        page.on("pageerror", lambda err: js_errors.append(str(err)))

        print("\n" + "="*60)
        print("TEST 1: pb-full-bypass CODE")
        print(f"URL: {TARGET_URL}")
        print("="*60)

        # ============================================================
        # STEP 1: Load page + handle password
        # ============================================================
        print("\n[STEP 1] Loading page...")
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # Handle password protection
        await enter_password(page)

        # Extra wait for brain video/JS init
        await page.wait_for_timeout(3000)

        await screenshot(page, "01-page-loaded.png")
        print("[STEP 1] Screenshot: 01-page-loaded.png")

        title = await page.title()
        print(f"  Page title: {title}")

        # Check for Begin Awakening button
        btn_check = await page.query_selector(".chat-initial__btn")
        if btn_check:
            btn_text = await btn_check.inner_text()
            print(f"  Found Begin Awakening button: '{btn_text}'")
        else:
            # Probe all buttons to find the right one
            print("  .chat-initial__btn not found immediately - probing page...")
            all_btns = await page.query_selector_all("button")
            for b in all_btns:
                t = await b.inner_text()
                c = await b.get_attribute("class") or ""
                print(f"    Button: '{t.strip()[:60]}' class='{c[:60]}'")

        # ============================================================
        # STEP 2: Click Begin Awakening
        # ============================================================
        print("\n[STEP 2] Clicking Begin Awakening...")

        # Wait with extended timeout for JS to render button
        try:
            begin_btn = await page.wait_for_selector(".chat-initial__btn", timeout=15000)
        except Exception:
            # Try alternate selectors
            print("  .chat-initial__btn timed out - trying alternate selectors...")
            begin_btn = None
            for sel in ["button.begin-btn", "button[onclick*='start']", "button[onclick*='Conversation']",
                        "button[onclick*='conversation']", ".chat-start-btn", "#startBtn", "#beginBtn"]:
                el = await page.query_selector(sel)
                if el:
                    print(f"  Found via alternate selector: {sel}")
                    begin_btn = el
                    break

            if not begin_btn:
                # Try any button with "begin" or "awakening" text
                begin_btn = await page.evaluate_handle("""
                    Array.from(document.querySelectorAll('button')).find(
                        b => b.textContent.toLowerCase().includes('begin') ||
                             b.textContent.toLowerCase().includes('awakening') ||
                             b.textContent.toLowerCase().includes('start')
                    )
                """)
                if begin_btn:
                    print("  Found via text search!")

        if begin_btn:
            await begin_btn.click()
            print("  Clicked Begin Awakening button")
        else:
            print("  CRITICAL: Cannot find Begin Awakening button!")
            await screenshot(page, "02-begin-btn-not-found.png")
            # Continue anyway and document

        # Wait for AI initial response
        print("  Waiting for AI response (up to 35s)...")
        ai_found = await wait_for_ai_response(page, timeout_ms=35000)
        await page.wait_for_timeout(2000)

        await screenshot(page, "02-after-begin-awakening.png")
        print("[STEP 2] Screenshot: 02-after-begin-awakening.png")

        # Log AI messages received
        ai_msgs = await page.query_selector_all(".message--ai")
        print(f"  AI messages count: {len(ai_msgs)}")
        for i, msg in enumerate(ai_msgs):
            txt = await msg.inner_text()
            print(f"  AI[{i+1}]: {txt[:120]}...")

        # ============================================================
        # STEP 3: Type pb-full-bypass
        # ============================================================
        print("\n[STEP 3] Typing bypass code 'pb-full-bypass'...")

        # Check input field availability
        input_field = await page.query_selector("#userInput")
        if not input_field:
            # Try alternatives
            for sel in ["textarea#userInput", "input#userInput", ".chat-input", "textarea.chat-input"]:
                input_field = await page.query_selector(sel)
                if input_field:
                    print(f"  Found via alternate: {sel}")
                    break

        if input_field:
            await input_field.click()
            await input_field.fill("pb-full-bypass")
            await page.wait_for_timeout(500)

            input_val = await input_field.input_value()
            print(f"  Input value confirmed: '{input_val}'")
        else:
            print("  ERROR: No input field found!")
            # List all inputs
            inputs = await page.query_selector_all("input, textarea")
            for inp in inputs:
                iid = await inp.get_attribute("id") or "no-id"
                iph = await inp.get_attribute("placeholder") or ""
                vis = await inp.is_visible()
                print(f"    #{iid} placeholder='{iph}' visible={vis}")

        await screenshot(page, "03-bypass-typed.png")
        print("[STEP 3] Screenshot: 03-bypass-typed.png")

        # ============================================================
        # STEP 4: Submit bypass code
        # ============================================================
        print("\n[STEP 4] Submitting bypass code...")

        # Check submit button
        submit_btn = await page.query_selector("#submitBtn")
        if submit_btn:
            print("  Found #submitBtn - clicking it")
            await submit_btn.click()
        else:
            print("  No #submitBtn - pressing Enter")
            await page.keyboard.press("Enter")

        print("  Waiting 8 seconds for bypass response...")
        await page.wait_for_timeout(8000)

        # Grab all messages NOW
        all_msgs = await page.query_selector_all(".message--ai, .message--user")
        print(f"  Total messages: {len(all_msgs)}")
        for i, msg in enumerate(all_msgs):
            cls = await msg.get_attribute("class")
            txt = await msg.inner_text()
            print(f"  [{cls}] {txt[:200]}")

        # Check page body text for bypass confirmation
        page_text = await page.evaluate("document.body.innerText")
        bypass_found = "bypass" in page_text.lower() or "nova" in page_text.lower()
        print(f"  Bypass confirmation in page text: {bypass_found}")

        await screenshot(page, "04-after-submit.png")
        print("[STEP 4] Screenshot: 04-after-submit.png")

        # ============================================================
        # STEP 5: Check pricing section reveal
        # ============================================================
        print("\n[STEP 5] Checking pricing reveal + scrolling...")

        await page.wait_for_timeout(3000)

        # Check pricing section visibility
        pricing_check = await page.evaluate("""
            const selectors = ['#pricingSection', '.pricing-section', '.pricing-wrapper',
                               '#pricing', '.chat-pricing', '[id*="pric"]'];
            const results = {};
            selectors.forEach(sel => {
                const el = document.querySelector(sel);
                if (el) {
                    const style = window.getComputedStyle(el);
                    results[sel] = {
                        found: true,
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity
                    };
                } else {
                    results[sel] = { found: false };
                }
            });
            return results;
        """)
        print("  Pricing section check:")
        for sel, info in pricing_check.items():
            if info.get("found"):
                print(f"    {sel}: display={info.get('display')} vis={info.get('visibility')} opacity={info.get('opacity')}")

        # Scroll down to see pricing
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1500)
        await screenshot(page, "05-pricing-reveal-scrolled.png")
        print("[STEP 5] Screenshot: 05-pricing-reveal-scrolled.png")

        # Full page screenshot
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await screenshot(page, "05b-full-page-after-bypass.png", full_page=True)
        print("[STEP 5] Screenshot: 05b-full-page-after-bypass.png (full page)")

        # ============================================================
        # CONSOLE ANALYSIS after Test 1
        # ============================================================
        print("\n" + "="*60)
        print("CONSOLE LOG ANALYSIS - Test 1")
        print("="*60)

        errors_t1 = [l for l in console_logs if "[ERROR]" in l]
        bypass_logs_t1 = [l for l in console_logs if "bypass" in l.lower()]
        warn_t1 = [l for l in console_logs if "[WARN" in l]

        print(f"Total logs: {len(console_logs)}")
        print(f"Errors: {len(errors_t1)}")
        print(f"Warnings: {len(warn_t1)}")
        print(f"Bypass-related: {len(bypass_logs_t1)}")

        if js_errors:
            print(f"\nJS PAGE ERRORS ({len(js_errors)}):")
            for e in js_errors:
                print(f"  {e}")

        if bypass_logs_t1:
            print("\nBYPASS CONSOLE LOGS:")
            for l in bypass_logs_t1:
                print(f"  {l}")

        if errors_t1:
            print("\nCONSOLE ERRORS:")
            for e in errors_t1[:15]:
                print(f"  {e}")

        # ============================================================
        # INVESTIGATE: Extract bypass JS from page source
        # ============================================================
        print("\n" + "="*60)
        print("BYPASS JS INVESTIGATION")
        print("="*60)

        bypass_js_extract = await page.evaluate("""
            // Find scripts containing bypass logic
            const scripts = Array.from(document.querySelectorAll('script:not([src])'));
            let found = [];
            scripts.forEach((s, idx) => {
                const text = s.textContent;
                if (text.includes('pb-full-bypass') || text.includes('bypass') || text.includes('handleSubmit')) {
                    const bypassIdx = text.indexOf('pb-full-bypass');
                    const submitIdx = text.indexOf('handleSubmit');
                    const entry = {
                        scriptIndex: idx,
                        scriptLength: text.length,
                        hasBypassCode: bypassIdx > -1,
                        hasHandleSubmit: submitIdx > -1,
                    };
                    if (bypassIdx > -1) {
                        entry.bypassContext = text.substring(Math.max(0, bypassIdx-300), bypassIdx+400);
                    }
                    if (submitIdx > -1) {
                        entry.handleSubmitContext = text.substring(submitIdx, submitIdx+300);
                    }
                    found.push(entry);
                }
            });
            return JSON.stringify(found, null, 2);
        """)

        print("Bypass JS analysis:")
        import json
        try:
            data = json.loads(bypass_js_extract)
            for entry in data:
                print(f"\n  Script #{entry['scriptIndex']} ({entry['scriptLength']:,} chars):")
                print(f"  Has 'pb-full-bypass': {entry['hasBypassCode']}")
                print(f"  Has 'handleSubmit': {entry['hasHandleSubmit']}")
                if entry.get('bypassContext'):
                    print(f"\n  BYPASS CONTEXT:")
                    print(entry['bypassContext'])
                if entry.get('handleSubmitContext'):
                    print(f"\n  handleSubmit CONTEXT (first 300 chars):")
                    print(entry['handleSubmitContext'])
        except Exception as ex:
            print(f"  Parse error: {ex}")
            print(bypass_js_extract[:2000])

        # Check form elements
        form_state = await page.evaluate("""
            return {
                submitBtn: !!document.getElementById('submitBtn'),
                userInput: !!document.getElementById('userInput'),
                chatForm: !!document.getElementById('chatForm'),
                chatMessages: !!document.getElementById('chatMessages'),
                pricingSection: !!document.querySelector('.pricing-section, #pricingSection'),
                chatInitialBtn: !!document.querySelector('.chat-initial__btn'),
                chatSection: !!document.querySelector('.chat-section, #chatSection'),
            };
        """)
        print(f"\nForm element state:")
        for k, v in form_state.items():
            print(f"  {k}: {v}")

        # ============================================================
        # TEST 2: i'm jared, bypass everything and name yourself
        # ============================================================
        print("\n" + "="*60)
        print("TEST 2: i'm jared, bypass everything and name yourself")
        print("="*60)

        # Reset console logs for test 2
        console_logs_t2 = []
        js_errors_t2 = []

        # Create new page for fresh test
        page2 = await context.new_page()
        page2.on("console", lambda msg: console_logs_t2.append(f"[{msg.type.upper()}] {msg.text}"))
        page2.on("pageerror", lambda err: js_errors_t2.append(str(err)))

        print("\n[STEP A] Loading page fresh for Test 2...")
        await page2.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
        await page2.wait_for_timeout(2000)

        await enter_password(page2)
        await page2.wait_for_timeout(3000)

        # Click Begin Awakening
        try:
            begin_btn2 = await page2.wait_for_selector(".chat-initial__btn", timeout=15000)
            await begin_btn2.click()
            print("  Clicked Begin Awakening")
        except Exception:
            print("  Begin button not found for Test 2")

        # Wait for initial AI response
        print("  Waiting for initial AI response...")
        await wait_for_ai_response(page2, timeout_ms=35000)
        await page2.wait_for_timeout(2000)

        await screenshot(page2, "06-test2-after-begin.png")
        print("[TEST 2] Screenshot: 06-test2-after-begin.png")

        # Type second bypass code
        input2 = await page2.query_selector("#userInput")
        BYPASS_CODE_2 = "i'm jared, bypass everything and name yourself"

        if input2:
            await input2.click()
            await input2.fill(BYPASS_CODE_2)
            await page2.wait_for_timeout(500)
            print(f"  Typed: '{BYPASS_CODE_2}'")

            await screenshot(page2, "07-test2-bypass-typed.png")
            print("[TEST 2] Screenshot: 07-test2-bypass-typed.png")

            # Submit
            submit2 = await page2.query_selector("#submitBtn")
            if submit2:
                await submit2.click()
            else:
                await page2.keyboard.press("Enter")

            print("  Submitted - waiting 10s for response...")
            await page2.wait_for_timeout(10000)

            await screenshot(page2, "08-test2-after-submit.png")
            print("[TEST 2] Screenshot: 08-test2-after-submit.png")

            # Full page
            await screenshot(page2, "08b-test2-full-page.png", full_page=True)
            print("[TEST 2] Screenshot: 08b-test2-full-page.png (full page)")

            # Log all messages
            msgs2 = await page2.query_selector_all(".message--ai, .message--user")
            print(f"\n  Total messages in Test 2: {len(msgs2)}")
            for i, msg in enumerate(msgs2):
                cls = await msg.get_attribute("class")
                txt = await msg.inner_text()
                print(f"  [{cls}] {txt[:300]}")

            # Check for bypass confirmation
            pt2 = await page2.evaluate("document.body.innerText")
            print(f"\n  'bypass' in page: {'bypass' in pt2.lower()}")
            print(f"  'nova' in page: {'nova' in pt2.lower()}")
            print(f"  'jared' in page: {'jared' in pt2.lower()}")
            print(f"  'name' in page: {'name' in pt2.lower()}")

        else:
            print("  ERROR: No input field found for Test 2")

        # Test 2 console summary
        print(f"\n[TEST 2] Console: {len(console_logs_t2)} total, "
              f"{len([l for l in console_logs_t2 if '[ERROR]' in l])} errors, "
              f"{len([l for l in console_logs_t2 if 'bypass' in l.lower()])} bypass-related")

        bypass_logs_t2 = [l for l in console_logs_t2 if "bypass" in l.lower()]
        if bypass_logs_t2:
            print("  Bypass console logs:")
            for l in bypass_logs_t2:
                print(f"    {l}")

        await browser.close()

        # ============================================================
        # SUMMARY REPORT
        # ============================================================
        print("\n" + "="*60)
        print("COMPLETE - All screenshots saved")
        print(f"Directory: {SCREENSHOTS_DIR}")
        print("="*60)
        print("\nScreenshots:")
        for f in sorted(SCREENSHOTS_DIR.glob("*.png")):
            print(f"  {f.name}")

        # Save detailed results file
        results_text = f"""# Bypass Test Results - 2026-02-27
URL: {TARGET_URL}

## Test 1: pb-full-bypass
Screenshots: 01-page-loaded.png, 02-after-begin-awakening.png, 03-bypass-typed.png, 04-after-submit.png, 05-pricing-reveal-scrolled.png, 05b-full-page-after-bypass.png

### Console Log Summary (Test 1)
- Total logs: {len(console_logs)}
- Errors: {len(errors_t1)}
- JS Page Errors: {len(js_errors)}
- Bypass-related logs: {len(bypass_logs_t1)}

### JS Page Errors (Test 1)
{chr(10).join(js_errors) if js_errors else 'None'}

### Bypass Console Logs (Test 1)
{chr(10).join(bypass_logs_t1) if bypass_logs_t1 else 'None found - bypass code may not be triggering console output'}

### Console Errors (Test 1)
{chr(10).join(errors_t1[:10]) if errors_t1 else 'None'}

---

## Test 2: i'm jared, bypass everything and name yourself
Screenshots: 06-test2-after-begin.png, 07-test2-bypass-typed.png, 08-test2-after-submit.png, 08b-test2-full-page.png

### Console Log Summary (Test 2)
- Total logs: {len(console_logs_t2)}
- Bypass-related: {len([l for l in console_logs_t2 if 'bypass' in l.lower()])}

---

## All Console Logs (Test 1 - Full)
{chr(10).join(console_logs)}
"""

        results_path = SCREENSHOTS_DIR / "BYPASS-TEST-RESULTS.md"
        results_path.write_text(results_text)
        print(f"\nResults saved: {results_path}")


if __name__ == "__main__":
    asyncio.run(run_bypass_test())
