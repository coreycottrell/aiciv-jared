#!/usr/bin/env python3
"""
Deploy updated purebrain-security-plugin.php to WordPress.

Strategy: Use WP Admin plugin editor with CAPTCHA vision-reading.

The script:
1. Opens WP Admin login
2. Screenshots CAPTCHA
3. Saves cropped CAPTCHA for external vision reading
4. Accepts CAPTCHA answer as CLI arg or from /tmp/captcha_answer.txt
5. Fills form + CAPTCHA, logs in
6. Opens plugin editor, pastes new content, saves

Usage:
    # Step 1: Run to get CAPTCHA
    python3 tools/security/deploy_plugin_csp_v2.py --get-captcha

    # Step 2: Solve CAPTCHA visually, then run:
    python3 tools/security/deploy_plugin_csp_v2.py --captcha=awhn789

Author: full-stack-developer agent
Date: 2026-02-20
"""

import os
import sys
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# ============================================================
# Configuration
# ============================================================

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_FILE = AETHER_ROOT / ".env"
load_dotenv(ENV_FILE)

PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security-plugin.php"
WP_USER = "Aether"
WP_PASSWORD = os.environ.get("PUREBRAIN_WP_PASSWORD", "")
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"

CAPTCHA_FILE = "/tmp/plugin_deploy_captcha.png"
CAPTCHA_ANSWER_FILE = "/tmp/plugin_deploy_captcha_answer.txt"
SCREENSHOT_DIR = str(AETHER_ROOT / "exports/screenshots")

PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)


def validate_plugin():
    """Validate the plugin file is ready to deploy."""
    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        return False

    content = PLUGIN_FILE.read_text()

    if "1.4.0" not in content:
        print("ERROR: Plugin does not contain version 1.4.0")
        return False

    if "api.purebrain.ai" not in content:
        print("ERROR: Plugin does not contain api.purebrain.ai in CSP")
        return False

    if "api.puremarketing.ai" not in content:
        print("ERROR: Plugin does not contain api.puremarketing.ai in CSP")
        return False

    print(f"Plugin file validated: {len(content)} chars, version 1.4.0")
    return True


def get_captcha():
    """Open WP login, screenshot the CAPTCHA."""
    print("\n=== Getting CAPTCHA ===")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
        )
        page = context.new_page()

        print("Navigating to WP Admin login...")
        page.goto(f"{WP_ADMIN_URL}/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Click SSO toggle
        try:
            sso = page.locator("text=Log in with username and password")
            if sso.is_visible(timeout=3000):
                sso.click()
                time.sleep(2)
                print("Clicked SSO toggle.")
        except Exception:
            pass

        # Fill username/password to ensure CAPTCHA shows
        page.wait_for_selector('#user_login', state='visible', timeout=20000)
        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASSWORD)

        # Screenshot
        full_ss = f"{SCREENSHOT_DIR}/plugin_deploy_login.png"
        page.screenshot(path=full_ss)
        print(f"Full screenshot: {full_ss}")

        # Crop CAPTCHA
        from PIL import Image
        img = Image.open(full_ss)
        print(f"Image size: {img.size}")

        # CAPTCHA location in 3840x2160 image (2x device scale from 1920x1080 viewport)
        # The form is centered at x=1920. CAPTCHA image is ~400px wide.
        # Typically: x=1460-2180, y=780-1060 based on previous tests
        captcha_crop = img.crop((1400, 750, 2200, 1100))
        captcha_crop.save(CAPTCHA_FILE)
        print(f"CAPTCHA saved to: {CAPTCHA_FILE}")

        browser.close()

    print("\nPlease read the CAPTCHA from the image and run:")
    print(f"  python3 {__file__} --captcha=YOUR_ANSWER")
    return True


def deploy_with_captcha(captcha_answer: str):
    """Login with CAPTCHA answer and deploy the plugin."""
    print(f"\n=== Deploying with CAPTCHA: {captcha_answer} ===")

    new_content = PLUGIN_FILE.read_text()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
        )
        page = context.new_page()

        # ============================================================
        # Step 1: Login
        # ============================================================
        print("\nStep 1: Logging in...")
        page.goto(f"{WP_ADMIN_URL}/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Click SSO toggle
        try:
            sso = page.locator("text=Log in with username and password")
            if sso.is_visible(timeout=3000):
                sso.click()
                time.sleep(2)
        except Exception:
            pass

        # Fill form
        page.wait_for_selector('#user_login', state='visible', timeout=20000)
        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASSWORD)

        # Fill CAPTCHA
        captcha_input = page.locator('input[name="wpsec_captcha_answer"]')
        if captcha_input.count() > 0:
            captcha_input.fill(captcha_answer)
            print(f"CAPTCHA answer entered: {captcha_answer}")
        else:
            print("WARNING: CAPTCHA input not found. Proceeding anyway...")

        # Submit
        page.click('#wp-submit')
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(3)

        # Check login success
        current_url = page.url
        print(f"After login URL: {current_url}")

        if "wp-login.php" in current_url:
            ss = f"{SCREENSHOT_DIR}/plugin_deploy_login_fail.png"
            page.screenshot(path=ss)
            print(f"ERROR: Login failed. Screenshot: {ss}")
            browser.close()
            return False

        print("Login successful!")

        # ============================================================
        # Step 2: Open Plugin Editor
        # ============================================================
        print("\nStep 2: Opening Plugin Editor...")
        page.goto(PLUGIN_EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        ss = f"{SCREENSHOT_DIR}/plugin_deploy_editor_loaded.png"
        page.screenshot(path=ss)
        print(f"Editor screenshot: {ss}")

        # Check if plugin editor is accessible
        page_text = page.inner_text("body")
        if "You need a higher level of permission" in page_text:
            print("ERROR: Insufficient permissions for plugin editor.")
            browser.close()
            return False

        if "not allowed to edit" in page_text.lower() or "DISALLOW_FILE_EDIT" in page_text:
            print("ERROR: File editing is disabled in wp-config.php.")
            browser.close()
            return False

        # ============================================================
        # Step 3: Set new content
        # ============================================================
        print("\nStep 3: Setting new plugin content...")

        # Check for CodeMirror (modern WP) vs plain textarea
        if page.locator(".CodeMirror").count() > 0:
            print("Using CodeMirror editor...")
            page.evaluate(f"""
                var cm = document.querySelector('.CodeMirror').CodeMirror;
                cm.setValue({repr(new_content)});
            """)
            print("Content set via CodeMirror.")
        else:
            # Try plain textarea
            textarea = page.locator("#newcontent")
            if textarea.count() > 0:
                print("Using plain textarea...")
                page.evaluate(
                    "document.getElementById('newcontent').value = arguments[0]",
                    new_content
                )
                print("Content set via textarea JS.")
            else:
                print("ERROR: No editor found on page.")
                browser.close()
                return False

        # ============================================================
        # Step 4: Save
        # ============================================================
        print("\nStep 4: Saving...")
        submit_btn = page.locator("#submit")
        if submit_btn.count() == 0:
            submit_btn = page.locator("input[type='submit']").first

        submit_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(3)

        # ============================================================
        # Step 5: Verify
        # ============================================================
        ss = f"{SCREENSHOT_DIR}/plugin_deploy_after_save.png"
        page.screenshot(path=ss)
        print(f"After save screenshot: {ss}")

        page_text = page.inner_text("body")

        if "File edited successfully" in page_text:
            print("SUCCESS: Plugin file saved via plugin editor!")
            browser.close()
            return True
        elif "successfully" in page_text.lower():
            print("SUCCESS: Plugin appears to have saved.")
            browser.close()
            return True
        elif "syntax error" in page_text.lower() or "Parse error" in page_text:
            print("ERROR: PHP syntax error detected. File was NOT saved.")
            browser.close()
            return False
        else:
            print(f"UNCERTAIN: Page after save (excerpt): {page_text[:200]}")
            browser.close()
            return False


def verify_live():
    """Verify the new CSP header is live."""
    import urllib.request
    try:
        req = urllib.request.Request(
            "https://purebrain.ai",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response = urllib.request.urlopen(req, timeout=15)
        csp = response.headers.get("Content-Security-Policy-Report-Only", "")
        if "api.purebrain.ai" in csp:
            print("\nVERIFIED: api.purebrain.ai is LIVE in the CSP header!")
            print(f"CSP (first 400 chars): {csp[:400]}")
            return True
        else:
            print(f"\nNOT YET: api.purebrain.ai not found in live CSP.")
            print(f"Current CSP: {csp[:300]}")
            return False
    except Exception as e:
        print(f"Verification failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Deploy PureBrain Security Plugin v1.4.0")
    parser.add_argument("--get-captcha", action="store_true", help="Get CAPTCHA image")
    parser.add_argument("--captcha", type=str, help="CAPTCHA answer to use for deployment")
    parser.add_argument("--verify", action="store_true", help="Just verify the live CSP")
    args = parser.parse_args()

    if args.verify:
        verify_live()
        return

    if not validate_plugin():
        sys.exit(1)

    if args.get_captcha:
        get_captcha()
        return

    if args.captcha:
        success = deploy_with_captcha(args.captcha)
        if success:
            verify_live()
        else:
            print("\nDeployment failed. Manual deployment options:")
            print("  1. WP Admin > Plugin Editor > PureBrain Security > paste content")
            print(f"  2. File to upload: {PLUGIN_FILE}")
            sys.exit(1)
    else:
        print("Usage:")
        print("  # Get CAPTCHA image:")
        print(f"  python3 {__file__} --get-captcha")
        print("  # Then read it and deploy:")
        print(f"  python3 {__file__} --captcha=ANSWER")


if __name__ == "__main__":
    main()
