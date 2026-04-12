#!/usr/bin/env python3
"""
Pay-Test-2 Chatbox Verification Script v3 - 2026-02-27
Uses Playwright's native form submission approach + cookie from requests library.
"""

import asyncio
import subprocess
import urllib.parse
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-verify-20260227")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_URL = "https://purebrain.ai/pay-test-2/"
PASSWORD = "PureBrain.ai253443$"

async def run():
    print("=== Pay-Test-2 Chatbox Verification v3 ===\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
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

        # Step 1: Navigate to the page first to get initial cookies from Cloudflare
        print("Step 1: Initial navigation to get Cloudflare cookies...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Check we see the password form
        pw_field = await page.query_selector("input[id^='pwbox-']")
        if not pw_field:
            print("  No password form found - might already be unlocked!")
            await page.screenshot(path=str(OUTPUT_DIR / "v3-001-no-pw-form.png"))
        else:
            print("  Password form found - submitting via JavaScript fetch...")
            await page.screenshot(path=str(OUTPUT_DIR / "v3-001-password-form.png"))

            # Use JavaScript to submit the password form directly
            # This avoids any encoding issues with fill()
            result = await page.evaluate("""
            async (password) => {
                const formData = new FormData();
                formData.append('post_password', password);
                formData.append('Submit', 'Enter');
                formData.append('redirect_to', window.location.href);

                // Find the form action
                const form = document.querySelector('form.post-password-form');
                if (!form) return { error: 'No form found' };

                const action = form.action;

                try {
                    const response = await fetch(action, {
                        method: 'POST',
                        body: formData,
                        redirect: 'follow',
                        credentials: 'include'
                    });
                    return {
                        status: response.status,
                        url: response.url,
                        ok: response.ok
                    };
                } catch(e) {
                    return { error: e.toString() };
                }
            }
            """, PASSWORD)
            print(f"  Fetch result: {result}")

            # Now try submitting the form natively
            print("\nStep 2: Submitting password form natively...")

            # Type into the field character by character
            await pw_field.click()
            await pw_field.type(PASSWORD, delay=50)

            # Take screenshot to verify the text was entered
            await page.screenshot(path=str(OUTPUT_DIR / "v3-002-password-typed.png"))
            print("  Screenshot v3-002: password typed (field should show dots)")

            # Find and click the submit button
            submit_btn = await page.query_selector("input[name='Submit'], input[type='submit']")
            if submit_btn:
                submit_val = await submit_btn.get_attribute("value")
                print(f"  Submit button found: value='{submit_val}'")

                # Click it
                await submit_btn.click()
                print("  Submit clicked - waiting for redirect...")

                # Wait for navigation
                try:
                    await page.wait_for_url(TARGET_URL, timeout=15000)
                    print("  Navigation completed")
                except:
                    print("  Navigation timeout - continuing...")

                await page.wait_for_load_state("networkidle", timeout=20000)
                await asyncio.sleep(3)
            else:
                print("  No submit button - pressing Enter on field")
                await pw_field.press("Enter")
                await asyncio.sleep(3)
                await page.wait_for_load_state("networkidle", timeout=20000)
                await asyncio.sleep(3)

        # Check current state
        print("\nStep 3: Checking post-submission state...")
        current_url = page.url
        title = await page.title()
        print(f"  URL: {current_url}")
        print(f"  Title: {title}")

        pw_error = await page.query_selector(".post-password-form-invalid-password, #error-pwbox")
        pw_form_still = await page.query_selector("input[id^='pwbox-']")

        if pw_error:
            error_text = await pw_error.inner_text()
            print(f"  PASSWORD ERROR: {error_text}")
        elif pw_form_still:
            print("  STILL SHOWING PASSWORD FORM (no error message visible)")
        else:
            print("  Password accepted! Page content should be visible.")

        await page.screenshot(path=str(OUTPUT_DIR / "v3-003-after-submit.png"))
        await page.screenshot(path=str(OUTPUT_DIR / "v3-004-full-page.png"), full_page=True)
        print("  Screenshots v3-003, v3-004 saved")

        # Wait for page JS
        await asyncio.sleep(5)
        await page.screenshot(path=str(OUTPUT_DIR / "v3-005-js-settled.png"))

        # --- Check for Begin Awakening ---
        print("\nStep 4: Searching for Begin Awakening button...")
        page_text = await page.evaluate("document.body.innerText")

        if "Begin Awakening" in page_text:
            print("  'Begin Awakening' text FOUND!")
        elif "Begin" in page_text:
            import re
            matches = re.findall(r'.{0,30}[Bb]egin.{0,30}', page_text)
            print(f"  'Begin' found in: {matches[:3]}")
        else:
            print("  'Begin Awakening' NOT found in page text")
            print(f"  Page text (first 400 chars): {page_text[:400]}")

        # Look for buttons
        all_buttons = await page.query_selector_all("button, input[type='button'], input[type='submit']")
        print(f"\n  All interactive elements: {len(all_buttons)}")
        for i, btn in enumerate(all_buttons[:15]):
            try:
                tag = await btn.evaluate("el => el.tagName")
                txt = await btn.inner_text() if tag == "BUTTON" else await btn.get_attribute("value") or ""
                cls = await btn.get_attribute("class") or ""
                vis = await btn.is_visible()
                print(f"    [{i+1}] {tag}: '{txt.strip()[:60]}' class='{cls[:40]}' visible={vis}")
            except Exception as e:
                print(f"    [{i+1}] Error: {e}")

        # Check chat elements
        print("\nStep 5: Chat container check...")
        for sel in [".chat-initial", ".chat-initial__btn", "#chatMessages", ".chat-container", "[class*='chat']"]:
            els = await page.query_selector_all(sel)
            if els:
                for el in els[:2]:
                    vis = await el.is_visible()
                    tag = await el.evaluate("el => el.tagName")
                    cls = await el.get_attribute("class") or ""
                    txt = (await el.inner_text())[:100]
                    print(f"  {sel}: {tag} visible={vis} class='{cls}' text='{txt}'")

        # Try clicking Begin if found
        begin_btn = None
        for selector in [".chat-initial__btn", "button:has-text('Begin')", "button:has-text('Awakening')"]:
            el = await page.query_selector(selector)
            if el:
                vis = await el.is_visible()
                txt = await el.inner_text()
                print(f"\n  Found via {selector}: '{txt}' visible={vis}")
                begin_btn = el
                break

        if begin_btn:
            vis = await begin_btn.is_visible()
            if vis:
                print("\nStep 6: Clicking Begin Awakening...")
                await page.screenshot(path=str(OUTPUT_DIR / "v3-006-before-begin.png"))
                await begin_btn.click()

                await asyncio.sleep(3)
                await page.screenshot(path=str(OUTPUT_DIR / "v3-007-after-begin-3s.png"))

                await asyncio.sleep(7)
                await page.screenshot(path=str(OUTPUT_DIR / "v3-008-after-begin-10s.png"))

                await asyncio.sleep(10)
                await page.screenshot(path=str(OUTPUT_DIR / "v3-009-after-begin-20s.png"))
                print("  Screenshots v3-006 through v3-009 saved")

                # Check AI response
                ai_msgs = await page.query_selector_all(".message--ai, .ptc-msg--ai")
                print(f"  AI messages: {len(ai_msgs)}")
                if ai_msgs:
                    txt = await ai_msgs[0].inner_text()
                    print(f"  First AI message: '{txt[:300]}'")

        # Console summary
        print("\n--- Console Summary ---")
        errors = [m for m in console_messages if m["type"] == "error"]
        print(f"  Total errors: {len(errors)}")
        for e in errors[:6]:
            print(f"  ERROR: {e['text'][:250]}")

        # JSON errors specifically
        json_issues = [m for m in console_messages if any(x in m["text"].lower() for x in
                        ["syntaxerror", "json", "unexpected token", "invalid escape", "bad escape"])]
        if json_issues:
            print(f"\n  JSON/Syntax issues ({len(json_issues)}):")
            for j in json_issues:
                print(f"  {j['type'].upper()}: {j['text'][:400]}")

        await browser.close()

        print(f"\n=== Screenshots: {OUTPUT_DIR} ===")
        for f in sorted(OUTPUT_DIR.glob("v3-*.png")):
            print(f"  {f.name}")

if __name__ == "__main__":
    asyncio.run(run())
