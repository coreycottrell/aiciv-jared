#!/usr/bin/env python3
"""
Test: purebrain.ai/training/ password gate
Steps:
  1. Screenshot initial page
  2. Type "brainiac2026" into password input
  3. Click submit / press Enter
  4. Screenshot result
  5. Check console for JS errors
  6. Detect WordPress vs custom JS gate
"""

import sys
import time
import json
import os
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots/training-page-test-2026-02-28"
URL = "https://purebrain.ai/training/"
PASSWORD = "brainiac2026"

def take_screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    page.screenshot(path=path, full_page=False)
    print(f"[SCREENSHOT] {path}")
    return path

def run_test():
    console_logs = []
    console_errors = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()

        # Capture console logs
        def on_console(msg):
            entry = {"type": msg.type, "text": msg.text}
            console_logs.append(entry)
            if msg.type == "error":
                console_errors.append(entry)
                print(f"[CONSOLE ERROR] {msg.text}")
            elif msg.type == "warning":
                print(f"[CONSOLE WARN] {msg.text}")
            else:
                print(f"[CONSOLE {msg.type.upper()}] {msg.text}")

        page.on("console", on_console)

        # ── STEP 1: Navigate to training page ──────────────────────────────
        print("\n=== STEP 1: Navigate to https://purebrain.ai/training/ ===")
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)  # Let JS settle

        # Inspect page structure immediately
        page_title = page.title()
        page_url = page.url
        print(f"[PAGE TITLE] {page_title}")
        print(f"[CURRENT URL] {page_url}")

        # Check for WordPress post-password-form
        wp_pw_form = page.query_selector(".post-password-form")
        custom_pw_input = page.query_selector("#training-password, .training-password, input[placeholder*='password'], input[placeholder*='Password'], input[placeholder*='Enter password'], input[name='training_password']")
        any_pw_input = page.query_selector("input[type='password']")

        print(f"[WP post-password-form present?] {wp_pw_form is not None}")
        print(f"[Custom password input present?] {custom_pw_input is not None}")
        print(f"[Any password input present?] {any_pw_input is not None}")

        # Get full HTML structure of password form area
        pw_form_html = page.evaluate("""() => {
            var wpForm = document.querySelector('.post-password-form');
            var customForm = document.querySelector('form');
            var anyInput = document.querySelector('input[type="password"]');
            return {
                wp_form_html: wpForm ? wpForm.outerHTML.substring(0, 500) : null,
                first_form_html: customForm ? customForm.outerHTML.substring(0, 500) : null,
                password_input_html: anyInput ? anyInput.outerHTML : null,
                all_forms: Array.from(document.querySelectorAll('form')).map(f => ({
                    action: f.action,
                    id: f.id,
                    className: f.className,
                    html: f.outerHTML.substring(0, 300)
                })),
                all_password_inputs: Array.from(document.querySelectorAll('input[type="password"]')).map(i => ({
                    id: i.id,
                    name: i.name,
                    placeholder: i.placeholder,
                    className: i.className
                })),
                all_submit_buttons: Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"]')).map(b => ({
                    tag: b.tagName,
                    type: b.type || '',
                    id: b.id,
                    text: b.textContent.substring(0, 100),
                    value: b.value || '',
                    className: b.className
                }))
            };
        }""")

        print(f"\n[PAGE STRUCTURE ANALYSIS]")
        print(f"  WordPress form HTML: {pw_form_html.get('wp_form_html', 'None')}")
        print(f"  All forms found: {len(pw_form_html.get('all_forms', []))}")
        for i, form in enumerate(pw_form_html.get('all_forms', [])):
            print(f"    Form {i}: action={form['action']}, id={form['id']}, class={form['className']}")
            print(f"      HTML: {form['html'][:200]}")
        print(f"  Password inputs: {pw_form_html.get('all_password_inputs', [])}")
        print(f"  Submit buttons: {pw_form_html.get('all_submit_buttons', [])}")

        # ── STEP 1: Screenshot initial state ──────────────────────────────
        take_screenshot(page, "01-initial-state")
        print("[DONE] Step 1: Initial screenshot taken")

        # ── STEP 2: Type password ──────────────────────────────────────────
        print(f"\n=== STEP 2: Type '{PASSWORD}' into password field ===")

        pw_input_selector = None
        # Try WP selector first
        if page.query_selector("input[id^='pwbox-']"):
            pw_input_selector = "input[id^='pwbox-']"
            print("[SELECTOR] WordPress pwbox input detected")
        elif page.query_selector("input[type='password']"):
            pw_input_selector = "input[type='password']"
            print("[SELECTOR] Generic password input detected")
        else:
            print("[WARNING] No password input found!")

        if pw_input_selector:
            # Click + fill the input
            page.click(pw_input_selector)
            page.fill(pw_input_selector, PASSWORD)
            time.sleep(0.5)

            # Screenshot after typing
            take_screenshot(page, "02-after-typing-password")
            print("[DONE] Step 2: Password typed and screenshot taken")

            # ── STEP 3: Submit form ────────────────────────────────────────
            print("\n=== STEP 3: Submit the form ===")

            # Check if there's a submit button with "Access Training Library" text
            submit_btn = page.query_selector("input[type='submit'], button[type='submit']")
            access_btn = page.query_selector("button:has-text('Access Training Library'), input[value*='Access']")

            if access_btn:
                print("[SUBMIT] Found 'Access Training Library' button - clicking it")
                try:
                    access_btn.click()
                except Exception as e:
                    print(f"[SUBMIT CLICK FAILED] {e} - trying JS form submit")
                    page.evaluate("() => { var f = document.querySelector('form'); if(f) f.submit(); }")
            elif submit_btn:
                print(f"[SUBMIT] Found submit button: {submit_btn.get_attribute('value') or 'button'} - clicking")
                try:
                    submit_btn.click()
                except Exception as e:
                    print(f"[SUBMIT CLICK FAILED] {e} - trying JS form submit")
                    page.evaluate("() => { var f = document.querySelector('.post-password-form'); if(f) f.submit(); else { var f2 = document.querySelector('form'); if(f2) f2.submit(); } }")
            else:
                print("[SUBMIT] No button found - pressing Enter on password field")
                page.keyboard.press("Enter")

            # Wait for navigation/response
            print("[WAITING] 5 seconds for page response...")
            time.sleep(5)

            # Check new state
            new_url = page.url
            new_title = page.title()
            print(f"[POST-SUBMIT URL] {new_url}")
            print(f"[POST-SUBMIT TITLE] {new_title}")

            # Check for error messages
            error_check = page.evaluate("""() => {
                var visibleText = document.body.innerText.substring(0, 2000);
                var errorElements = Array.from(document.querySelectorAll('.error, .wp-password-error, [class*="error"], [class*="wrong"], [class*="invalid"]'))
                    .map(el => el.textContent.trim()).filter(t => t.length > 0);
                var wrongPass = document.querySelector('.post-password-required, #wrong_pass');
                return {
                    visible_text_preview: visibleText,
                    error_elements: errorElements,
                    wrong_pass_element: wrongPass ? wrongPass.outerHTML : null,
                    page_still_has_password_form: !!document.querySelector('.post-password-form, input[type="password"]')
                };
            }""")

            print(f"\n[POST-SUBMIT ANALYSIS]")
            print(f"  Still has password form: {error_check['page_still_has_password_form']}")
            print(f"  Error elements: {error_check['error_elements']}")
            print(f"  Wrong pass element: {error_check['wrong_pass_element']}")
            print(f"  Page text preview: {error_check['visible_text_preview'][:500]}")

            # ── STEP 4: Screenshot result ──────────────────────────────────
            take_screenshot(page, "03-after-submit-result")
            print("[DONE] Step 4: Post-submit screenshot taken")

            # ── Additional: Check if page content is now visible ───────────
            print("\n=== STEP 5: Check console errors ===")
            print(f"[TOTAL CONSOLE LOGS] {len(console_logs)}")
            print(f"[TOTAL CONSOLE ERRORS] {len(console_errors)}")
            for err in console_errors:
                print(f"  ERROR: {err['text']}")

            # Full page screenshot after waiting more
            time.sleep(2)
            take_screenshot(page, "04-full-page-final")

            # Get any training content visible
            training_content = page.evaluate("""() => {
                return {
                    has_training_videos: !!document.querySelector('video, iframe[src*="youtube"], iframe[src*="vimeo"]'),
                    has_training_content: !!document.querySelector('.training-content, .course-content, .lesson-content'),
                    page_heading: document.querySelector('h1, h2') ? document.querySelector('h1, h2').textContent.trim() : 'none',
                    full_text_preview: document.body.innerText.substring(0, 1000)
                };
            }""")

            print(f"\n[TRAINING CONTENT VISIBLE?]")
            print(f"  Has video elements: {training_content['has_training_videos']}")
            print(f"  Has training content divs: {training_content['has_training_content']}")
            print(f"  Page heading: {training_content['page_heading']}")
            print(f"  Full page text: {training_content['full_text_preview']}")

        else:
            print("[ERROR] Could not find password input - check initial screenshot for page structure")
            take_screenshot(page, "02-no-password-input-found")

        # ── Save console log ───────────────────────────────────────────────
        log_path = os.path.join(SCREENSHOTS_DIR, "console.log")
        with open(log_path, "w") as f:
            json.dump(console_logs, f, indent=2)
        print(f"\n[CONSOLE LOG SAVED] {log_path}")

        browser.close()

    print("\n=== TEST COMPLETE ===")
    print(f"Screenshots saved to: {SCREENSHOTS_DIR}")

if __name__ == "__main__":
    run_test()
