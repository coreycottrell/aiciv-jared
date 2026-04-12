#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v1.4.0 in a single Playwright session.

Workflow (all in ONE browser session):
  1. Open WP Admin (redirects to login)
  2. Click SSO toggle to show the standard form
  3. Fill username + password
  4. Screenshot the CAPTCHA + save it
  5. Pause and write the CAPTCHA image path to a temp file
  6. Wait for external process to write the answer to /tmp/plugin_captcha_answer.txt
  7. Read the answer, fill CAPTCHA field, submit
  8. Open plugin editor, paste new content, save

Run this script, then in another terminal read the CAPTCHA image and write:
    echo "captcha_text" > /tmp/plugin_captcha_answer.txt

The script polls /tmp/plugin_captcha_answer.txt every 2 seconds (timeout: 60s).

Author: full-stack-developer
Date: 2026-02-20
"""

import os
import sys
import time
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
load_dotenv(AETHER_ROOT / ".env")

PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security-plugin.php"
WP_USER = "Aether"
WP_PASSWORD = os.environ.get("PUREBRAIN_WP_PASSWORD", "")
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
SS_DIR = str(AETHER_ROOT / "exports/screenshots")

CAPTCHA_IMAGE_PATH = "/tmp/plugin_deploy_captcha_live.png"
CAPTCHA_ANSWER_FILE = "/tmp/plugin_captcha_answer.txt"

PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)


def crop_captcha(full_screenshot_path: str, output_path: str):
    """Crop the CAPTCHA from full login screenshot."""
    img = Image.open(full_screenshot_path)
    # Login form centered, CAPTCHA at roughly x=1400-2200, y=750-1100 in 3840x2160
    captcha = img.crop((1400, 750, 2200, 1100))
    captcha.save(output_path)
    return output_path


def wait_for_captcha_answer(timeout_secs: int = 120) -> str:
    """Poll for answer file written by external reader."""
    # Clean up old answer
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        os.remove(CAPTCHA_ANSWER_FILE)

    print(f"\n>>> CAPTCHA IMAGE SAVED: {CAPTCHA_IMAGE_PATH}")
    print(f">>> Open that image, read it, then write the answer:")
    print(f">>> echo 'YOUR_CAPTCHA_ANSWER' > {CAPTCHA_ANSWER_FILE}")
    print(f">>> Waiting up to {timeout_secs} seconds...")

    deadline = time.time() + timeout_secs
    while time.time() < deadline:
        if os.path.exists(CAPTCHA_ANSWER_FILE):
            answer = Path(CAPTCHA_ANSWER_FILE).read_text().strip()
            if answer:
                print(f">>> Got answer: {answer}")
                return answer
        time.sleep(2)
        remaining = int(deadline - time.time())
        if remaining % 10 == 0:
            print(f"  Still waiting... {remaining}s remaining")

    return ""


def main():
    # Validate plugin
    if not PLUGIN_FILE.exists():
        print(f"ERROR: {PLUGIN_FILE} not found")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    assert "1.4.0" in new_content, "Plugin must be version 1.4.0"
    assert "api.purebrain.ai" in new_content, "Must contain api.purebrain.ai"
    print(f"Plugin validated: {len(new_content)} chars, v1.4.0")

    os.makedirs(SS_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
        )
        page = context.new_page()

        # ============================================================
        # Step 1: Navigate to WP Admin -> redirects to login
        # ============================================================
        print("\nStep 1: Opening WP Admin login...")
        page.goto(f"{WP_ADMIN_URL}/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # ============================================================
        # Step 2: Click SSO toggle
        # ============================================================
        try:
            sso = page.locator("text=Log in with username and password")
            if sso.is_visible(timeout=3000):
                sso.click()
                time.sleep(2)
                print("Clicked SSO toggle.")
        except Exception:
            print("No SSO toggle (standard form shown directly).")

        # ============================================================
        # Step 3: Fill username + password
        # ============================================================
        page.wait_for_selector('#user_login', state='visible', timeout=20000)
        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASSWORD)
        print("Username + password filled.")

        # ============================================================
        # Step 4: Screenshot and crop CAPTCHA
        # ============================================================
        full_ss = f"{SS_DIR}/plugin_deploy_login_with_captcha.png"
        page.screenshot(path=full_ss)
        crop_captcha(full_ss, CAPTCHA_IMAGE_PATH)
        print(f"CAPTCHA cropped and saved: {CAPTCHA_IMAGE_PATH}")

        # ============================================================
        # Step 5: Wait for human to read CAPTCHA and write answer
        # ============================================================
        captcha_answer = wait_for_captcha_answer(timeout_secs=120)

        if not captcha_answer:
            print("ERROR: No CAPTCHA answer received within timeout.")
            browser.close()
            sys.exit(1)

        # ============================================================
        # Step 6: Fill CAPTCHA and submit
        # ============================================================
        captcha_input = page.locator('input[name="wpsec_captcha_answer"]')
        if captcha_input.count() > 0:
            captcha_input.fill(captcha_answer)
            print(f"CAPTCHA filled: {captcha_answer}")
        else:
            print("WARNING: CAPTCHA input field not found, submitting without it.")

        page.click('#wp-submit')
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(4)

        current_url = page.url
        print(f"After login URL: {current_url}")

        if "wp-login.php" in current_url:
            ss = f"{SS_DIR}/plugin_deploy_login_fail2.png"
            page.screenshot(path=ss)
            print(f"ERROR: Login failed. Screenshot: {ss}")
            browser.close()
            sys.exit(1)

        print("LOGIN SUCCESS!")

        # ============================================================
        # Step 7: Open Plugin Editor
        # ============================================================
        print("\nStep 7: Opening Plugin Editor...")
        page.goto(PLUGIN_EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        ss = f"{SS_DIR}/plugin_deploy_editor.png"
        page.screenshot(path=ss)
        print(f"Editor screenshot: {ss}")

        body = page.inner_text("body")
        if "not allowed to edit" in body.lower() or "higher level of permission" in body.lower():
            print("ERROR: Plugin editor access denied.")
            browser.close()
            sys.exit(1)

        # Dismiss "Heads up!" warning dialog if present
        # WordPress shows a modal warning about direct plugin editing
        heads_up = page.locator("text=I understand")
        if heads_up.count() > 0 and heads_up.is_visible(timeout=3000):
            print("Dismissing 'Heads up!' dialog...")
            heads_up.click()
            time.sleep(2)
            print("Dialog dismissed.")

        # ============================================================
        # Step 8: Set content
        # ============================================================
        print("Step 8: Setting plugin content...")
        if page.locator(".CodeMirror").count() > 0:
            page.evaluate(
                "var cm = document.querySelector('.CodeMirror').CodeMirror; cm.setValue(arguments[0]);",
                new_content
            )
            print("Content set via CodeMirror.")
        else:
            page.evaluate(
                "document.getElementById('newcontent').value = arguments[0];",
                new_content
            )
            print("Content set via textarea.")

        # ============================================================
        # Step 9: Save
        # ============================================================
        print("Step 9: Clicking Save...")
        page.locator("#submit").click()
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(3)

        ss = f"{SS_DIR}/plugin_deploy_saved.png"
        page.screenshot(path=ss)
        print(f"Post-save screenshot: {ss}")

        body = page.inner_text("body")
        if "File edited successfully" in body or "successfully" in body.lower():
            print("\nSUCCESS: Plugin file saved!")
        elif "syntax error" in body.lower() or "parse error" in body.lower():
            print("\nERROR: PHP syntax error - file NOT saved.")
            browser.close()
            sys.exit(1)
        else:
            print(f"\nUNCERTAIN: {body[:200]}")

        browser.close()

    # ============================================================
    # Step 10: Verify live CSP
    # ============================================================
    print("\nVerifying live CSP header...")
    import urllib.request
    try:
        req = urllib.request.Request("https://purebrain.ai", headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        csp = resp.headers.get("Content-Security-Policy-Report-Only", "")
        if "api.purebrain.ai" in csp:
            print("VERIFIED: api.purebrain.ai is LIVE in CSP!")
        else:
            print(f"Not yet live. Current CSP: {csp[:300]}")
    except Exception as e:
        print(f"Verification error: {e}")


if __name__ == "__main__":
    main()
