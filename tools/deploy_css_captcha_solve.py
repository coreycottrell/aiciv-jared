#!/usr/bin/env python3
"""
Deploy CSS - Single session CAPTCHA solve
Captures CAPTCHA, saves for reading, then waits for input or reads from file.
"""

import sys
import time
import os
import json
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai"
USERNAME = "Aether"
PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css"
SCREENSHOT_DIR = "/tmp/purebrain-css-fix-2026-02-18"
CAPTCHA_FILE = f"{SCREENSHOT_DIR}/captcha_current.png"
CAPTCHA_ANSWER_FILE = f"{SCREENSHOT_DIR}/captcha_answer.txt"


def main():
    with open(CSS_FILE, 'r') as f:
        new_css = f.read()
    print(f"CSS loaded: {len(new_css)} chars")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Check if captcha answer file exists (from previous run)
    captcha_answer = None
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        with open(CAPTCHA_ANSWER_FILE, 'r') as f:
            captcha_answer = f.read().strip()
        print(f"Found captcha answer from file: {captcha_answer}")
        os.remove(CAPTCHA_ANSWER_FILE)

    # Also check command line
    if len(sys.argv) > 1:
        captcha_answer = sys.argv[1]
        print(f"Captcha answer from CLI: {captcha_answer}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Navigate to login
        print("\n=== LOGIN ===")
        page.goto(f"{WP_URL}/wp-admin", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Click "Log in with username and password"
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=3000):
                login_link.click()
                time.sleep(2)
        except:
            pass

        # Fill credentials
        page.locator("input#user_login").fill(USERNAME)
        page.locator("input#user_pass").fill(PASSWORD)

        # Find CAPTCHA field
        # The CAPTCHA plugin creates an input field - find it
        # Look for any text input that's not username
        captcha_field = None
        all_text_inputs = page.locator("input[type='text']")
        for i in range(all_text_inputs.count()):
            inp = all_text_inputs.nth(i)
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            if "user_login" not in id_attr and "log" != name:
                captcha_field = inp
                print(f"CAPTCHA field found: name='{name}', id='{id_attr}'")
                break

        if captcha_field is None:
            print("No CAPTCHA field found - trying login directly")
        else:
            if captcha_answer:
                captcha_field.fill(captcha_answer)
                print(f"Filled CAPTCHA with: {captcha_answer}")
            else:
                # Save the CAPTCHA image and exit
                # Crop just the CAPTCHA area
                page.screenshot(path=CAPTCHA_FILE)
                print(f"\nCAPTCHA saved to: {CAPTCHA_FILE}")
                print(f"Write answer to: {CAPTCHA_ANSWER_FILE}")
                print("Then re-run this script.")
                browser.close()
                return 2

        time.sleep(1)
        page.screenshot(path=f"{SCREENSHOT_DIR}/before_submit.png")

        # Submit login
        print("Submitting login form...")
        page.locator("input#wp-submit, input[type='submit']").first.click()
        time.sleep(5)

        page.screenshot(path=f"{SCREENSHOT_DIR}/after_submit.png")
        current_url = page.url
        print(f"After login URL: {current_url}")

        if "wp-login" in current_url:
            # Check for error
            error_el = page.locator("#login_error")
            if error_el.count() > 0:
                error_text = error_el.first.inner_text()
                print(f"Login ERROR: {error_text}")
            else:
                print("Login failed (still on login page)")
            browser.close()
            return 1

        print("LOGIN SUCCESS!")

        # === DEPLOY CSS ===
        print("\n=== DEPLOYING CSS ===")
        print("Navigating to Customizer > Additional CSS...")

        page.goto(
            f"{WP_URL}/wp-admin/customize.php?autofocus[section]=custom_css",
            wait_until="domcontentloaded",
            timeout=60000
        )
        time.sleep(12)  # Customizer is SLOW

        page.screenshot(path=f"{SCREENSHOT_DIR}/customizer_loaded.png")

        # Check if customizer loaded properly
        is_customizer = page.evaluate("() => typeof wp !== 'undefined' && wp.customize ? 'yes' : 'no'")
        print(f"Customizer API available: {is_customizer}")

        # Replace CSS
        escaped_css = new_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

        result = page.evaluate(f"""
            () => {{
                // Method 1: CodeMirror
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {{
                    cm.CodeMirror.setValue(`{escaped_css}`);
                    cm.CodeMirror.refresh();
                    return 'codemirror_chars_' + cm.CodeMirror.getValue().length;
                }}

                // Method 2: wp.customize API
                if (typeof wp !== 'undefined' && wp.customize) {{
                    try {{
                        const keys = Object.keys(wp.customize.settings.settings);
                        const cssKey = keys.find(k => k.includes('custom_css'));
                        if (cssKey) {{
                            wp.customize(cssKey).set(`{escaped_css}`);
                            return 'wp_customize_' + cssKey + '_chars_' + `{escaped_css}`.length;
                        }}
                        return 'no_css_key_found_keys_' + keys.filter(k => k.includes('css')).join(',');
                    }} catch(e) {{
                        return 'error_' + e.message;
                    }}
                }}

                // Method 3: textarea
                const ta = document.querySelector('textarea');
                if (ta) {{
                    ta.value = `{escaped_css}`;
                    ta.dispatchEvent(new Event('change', {{bubbles: true}}));
                    return 'textarea_chars_' + ta.value.length;
                }}

                return 'failed_no_editor';
            }}
        """)
        print(f"CSS update result: {result}")

        if 'failed' in str(result):
            page.screenshot(path=f"{SCREENSHOT_DIR}/css_deploy_failed.png")
            browser.close()
            return 1

        time.sleep(3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/css_set.png")

        # Publish
        print("Publishing...")
        publish_btn = page.locator("#save, button#save")
        if publish_btn.count() > 0:
            publish_btn.first.click()
            print("Clicked Publish button")
        else:
            # Try text-based
            pub2 = page.locator("button:has-text('Publish'), input:has-text('Publish'), input[value='Publish']")
            if pub2.count() > 0:
                pub2.first.click()
                print("Clicked Publish (text match)")
            else:
                page.keyboard.press("Control+s")
                print("Used Ctrl+S")

        time.sleep(5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/after_publish.png")

        # Check if published successfully
        saved_check = page.evaluate("""
            () => {
                const btn = document.querySelector('#save');
                if (btn) {
                    return {
                        text: btn.textContent || btn.value,
                        disabled: btn.disabled,
                        class: btn.className
                    };
                }
                return 'no_save_btn';
            }
        """)
        print(f"Save button state: {saved_check}")

        # === VERIFY ===
        print("\n=== VERIFICATION ===")
        vp = context.new_page()

        # Homepage
        print("Verifying homepage...")
        vp.goto(f"{WP_URL}", wait_until="domcontentloaded", timeout=30000)
        time.sleep(8)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/FINAL_homepage.png", full_page=False)

        body_bg = vp.evaluate("() => getComputedStyle(document.body).backgroundColor")
        print(f"  Body background: {body_bg}")
        if body_bg == "rgb(241, 66, 11)":
            print("  WARNING: Body still has orange background!")
        else:
            print("  OK: Body background is not orange")

        # Check CTA arrow
        arrow = vp.evaluate("""
            () => {
                const svgs = document.querySelectorAll('.btn__icon--arrow, .btn--primary svg');
                return Array.from(svgs).map(e => ({
                    tag: e.tagName,
                    stroke: getComputedStyle(e).stroke,
                    color: getComputedStyle(e).color
                }));
            }
        """)
        print(f"  CTA arrows: {json.dumps(arrow)}")

        # Blog page
        print("Verifying blog...")
        vp.goto(f"{WP_URL}/blog/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/FINAL_blog.png", full_page=False)

        # Blog post
        print("Verifying blog post...")
        vp.goto(f"{WP_URL}/why-ai-memory-changes-everything/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/FINAL_blogpost.png", full_page=False)

        social = vp.evaluate("""
            () => {
                const c = document.querySelectorAll('.post-social-sharing, [class*="social-share"]:not(footer *)');
                return Array.from(c).map(e => ({
                    class: e.className,
                    display: getComputedStyle(e).display,
                    visibility: getComputedStyle(e).visibility,
                    height: getComputedStyle(e).height
                }));
            }
        """)
        print(f"  Social sharing: {json.dumps(social)}")

        # Scroll to social area
        vp.evaluate("() => window.scrollTo(0, document.body.scrollHeight * 0.7)")
        time.sleep(2)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/FINAL_blogpost_scrolled.png", full_page=False)

        browser.close()

        print(f"\n=== ALL SCREENSHOTS IN: {SCREENSHOT_DIR}/ ===")
        for f in sorted(os.listdir(SCREENSHOT_DIR)):
            if f.startswith("FINAL"):
                print(f"  {SCREENSHOT_DIR}/{f}")

        return 0


if __name__ == "__main__":
    sys.exit(main())
