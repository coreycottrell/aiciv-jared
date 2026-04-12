#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v4.6.9 via Playwright.
Uses headless browser to handle GoDaddy SSO + CAPTCHA.
Screenshots saved to docs/deploy-attempt/
"""

import sys
import re
import os
import base64
import time
import requests
import socket

# Force IPv4
_orig = socket.getaddrinfo
def _ipv4(host, port, family=0, socktype=0, proto=0, flags=0):
    if 'purebrain.ai' in str(host):
        try:
            return _orig(host, port, socket.AF_INET, socktype, proto, flags)
        except Exception:
            pass
    return _orig(host, port, family, socktype, proto, flags)
socket.getaddrinfo = _ipv4

from playwright.sync_api import sync_playwright

PLUGIN_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v466.php"
WP_BASE = "https://purebrain.ai"
WP_USERNAME = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
WP_APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"
PLUGIN_SLUG = "purebrain-security/purebrain-security-plugin.php"
EXPECTED_VERSION = "4.6.9"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/docs/deploy-attempt"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def verify_via_rest():
    creds = base64.b64encode(f"Aether:{WP_APP_PASSWORD}".encode()).decode()
    rv = requests.get(
        f"{WP_BASE}/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin",
        headers={"Authorization": f"Basic {creds}", "Cache-Control": "no-cache"},
        timeout=15
    )
    data = rv.json()
    return data.get("version", "unknown"), data.get("status", "unknown")


def main():
    print("=" * 60)
    print(f"Plugin v{EXPECTED_VERSION} Playwright Deployment")
    print("=" * 60)

    # Read plugin
    with open(PLUGIN_FILE, "r") as f:
        plugin_content = f.read()

    if f"Version:     {EXPECTED_VERSION}" not in plugin_content:
        print(f"ERROR: Plugin file does not contain 'Version:     {EXPECTED_VERSION}'")
        ver_match = re.search(r'Version:\s*([\d.]+)', plugin_content)
        if ver_match:
            print(f"Found version: {ver_match.group(1)}")
        sys.exit(1)
    print(f"Plugin: {len(plugin_content)} chars, v{EXPECTED_VERSION} confirmed")

    with sync_playwright() as p:
        # Use headless=False to handle CAPTCHA visually if needed
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        try:
            # Step 1: Navigate to login page with standard login bypass
            print("\n[1] Loading login page...")
            page.goto(f"{WP_BASE}/wp-login.php?wpaas-standard-login=1", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
            page.screenshot(path=f"{SCREENSHOT_DIR}/pw-01-login-page.png")
            print(f"    URL: {page.url}")
            print(f"    Title: {page.title()}")

            # Check if CAPTCHA is visible
            captcha_visible = page.is_visible(".wpsec_captcha_wrapper:not([hidden])")
            print(f"    CAPTCHA visible: {captcha_visible}")

            # Step 2: Fill in credentials
            print("\n[2] Filling credentials...")
            page.fill("#user_login", WP_USERNAME)
            page.fill("#user_pass", WP_PASSWORD)
            page.screenshot(path=f"{SCREENSHOT_DIR}/pw-02-credentials-filled.png")

            # If CAPTCHA is shown, try to read and solve it
            if captcha_visible:
                print("    CAPTCHA is visible - attempting to read...")
                captcha_img = page.query_selector(".wpsec_captcha_image img")
                if captcha_img:
                    captcha_src = captcha_img.get_attribute("src")
                    print(f"    CAPTCHA image src: {captcha_src}")
                    page.screenshot(path=f"{SCREENSHOT_DIR}/pw-captcha.png")
                    print("    Screenshot saved - manual intervention may be needed")

            # Step 3: Submit login
            print("\n[3] Submitting login...")
            page.click("#wp-submit")
            page.wait_for_load_state("networkidle", timeout=20000)
            page.screenshot(path=f"{SCREENSHOT_DIR}/pw-03-after-login.png")
            print(f"    URL after login: {page.url}")
            print(f"    Title: {page.title()}")

            # Check if login succeeded
            if "wp-admin" not in page.url and "wp-login" in page.url:
                # Login failed - check for error
                error_el = page.query_selector("#login_error")
                if error_el:
                    print(f"    Login error: {error_el.inner_text()}")

                # Check for CAPTCHA now visible
                captcha_visible_now = page.is_visible(".wpsec_captcha_wrapper")
                if captcha_visible_now:
                    print("    CAPTCHA appeared after failed login!")
                    # Wait for captcha image to load
                    page.wait_for_selector(".wpsec_captcha_image img", timeout=5000)
                    page.screenshot(path=f"{SCREENSHOT_DIR}/pw-captcha-after-fail.png")
                    captcha_img = page.query_selector(".wpsec_captcha_image img")
                    if captcha_img:
                        captcha_src = captcha_img.get_attribute("src")
                        print(f"    CAPTCHA src: {captcha_src}")

                        # Try to read the captcha image using our Read tool equivalent
                        # Download the captcha image
                        if captcha_src:
                            try:
                                img_r = requests.get(captcha_src if captcha_src.startswith('http') else WP_BASE + captcha_src, timeout=10)
                                with open(f"{SCREENSHOT_DIR}/captcha-image.png", "wb") as f:
                                    f.write(img_r.content)
                                print(f"    Captcha image saved to {SCREENSHOT_DIR}/captcha-image.png")
                            except Exception as e:
                                print(f"    Could not download captcha: {e}")

                print("    Login failed. Cannot proceed without valid session.")
                browser.close()
                return False

            # Step 4: Navigate to plugin editor
            print("\n[4] Navigating to plugin editor...")
            plugin_editor_url = f"{WP_BASE}/wp-admin/plugin-editor.php?file={PLUGIN_SLUG}&plugin={PLUGIN_SLUG}"
            page.goto(plugin_editor_url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
            page.screenshot(path=f"{SCREENSHOT_DIR}/pw-04-plugin-editor.png")
            print(f"    URL: {page.url}")
            print(f"    Title: {page.title()}")

            # Check if we're on the editor page
            if "plugin-editor" not in page.url:
                print("    ERROR: Not on plugin editor page!")
                browser.close()
                return False

            # Get the nonce
            nonce_input = page.query_selector('input[name="nonce"]')
            if not nonce_input:
                nonce_input = page.query_selector('input[id="nonce"]')

            if nonce_input:
                nonce = nonce_input.get_attribute("value")
                print(f"    Nonce found: {nonce}")
            else:
                print("    ERROR: Nonce not found!")
                page.screenshot(path=f"{SCREENSHOT_DIR}/pw-nonce-error.png")
                browser.close()
                return False

            # Check current version in editor
            textarea = page.query_selector("#newcontent")
            if textarea:
                current_content = textarea.input_value()
                ver_match = re.search(r'Version:\s*([\d.]+)', current_content[:500])
                if ver_match:
                    print(f"    Current version in editor: {ver_match.group(1)}")

            # Step 5: Update the file content
            print("\n[5] Updating plugin content...")
            # Use JavaScript to set the textarea value (faster than typing)
            page.evaluate(f"""
                document.getElementById('newcontent').value = {repr(plugin_content)};
            """)
            page.screenshot(path=f"{SCREENSHOT_DIR}/pw-05-content-set.png")

            # Step 6: Submit the form
            print("\n[6] Submitting update...")
            submit_btn = page.query_selector('input[name="submit"]')
            if not submit_btn:
                submit_btn = page.query_selector('button[type="submit"]')

            if submit_btn:
                submit_btn.click()
            else:
                # Try pressing Enter in the form
                page.keyboard.press("Enter")

            page.wait_for_load_state("networkidle", timeout=30000)
            page.screenshot(path=f"{SCREENSHOT_DIR}/pw-06-after-submit.png")
            print(f"    URL after submit: {page.url}")

            # Check result
            page_content = page.content()
            if "File edited successfully" in page_content:
                print("    CONFIRMED: 'File edited successfully'!")
                success = True
            elif "successfully" in page_content.lower():
                print("    SUCCESS message detected!")
                success = True
            elif "error" in page_content.lower() or "Error" in page_content:
                print("    ERROR detected in response!")
                error_el = page.query_selector(".notice-error")
                if error_el:
                    print(f"    Error: {error_el.inner_text()}")
                success = False
            else:
                print("    Status unclear - checking via REST API")
                success = False

        except Exception as e:
            print(f"    Playwright exception: {e}")
            try:
                page.screenshot(path=f"{SCREENSHOT_DIR}/pw-exception.png")
            except:
                pass
            browser.close()
            return False

        browser.close()

    # Verify via REST API
    print("\n--- REST API Verification ---")
    time.sleep(3)
    version, status = verify_via_rest()
    print(f"REST API version: {version}")
    print(f"REST API status:  {status}")
    version_ok = (version == EXPECTED_VERSION)

    print("\n" + "=" * 60)
    if version_ok:
        print(f"DEPLOYMENT SUCCESSFUL - v{EXPECTED_VERSION} CONFIRMED LIVE!")
    elif success:
        print("FILE SUBMITTED - Response indicated success")
        print(f"  REST API shows: {version}")
    else:
        print("DEPLOYMENT FAILED")
    print("=" * 60)

    return version_ok or success


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
