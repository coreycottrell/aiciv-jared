#!/usr/bin/env python3
"""
Deploy updated purebrain-security-plugin.php to WordPress via Admin plugin editor.

Uses Playwright to navigate WP Admin > Plugin Editor, paste the new file content,
and save. This is the only reliable way to update a plugin file's content directly.

Usage:
    python3 tools/security/deploy_plugin_update.py

Author: full-stack-developer agent
Date: 2026-02-20
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# Configuration
# ============================================================

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_FILE = AETHER_ROOT / ".env"
load_dotenv(ENV_FILE)

PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security-plugin.php"
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
# PUREBRAIN_WP_PASSWORD is the actual WP admin login password (for browser/UI login)
# PUREBRAIN_WP_APP_PASSWORD is the Application Password (for REST API only)
WP_PASSWORD = os.environ.get("PUREBRAIN_WP_PASSWORD", "")

# The plugin editor URL for our specific plugin file
# Format: plugin-editor.php?file=plugin-folder/plugin-file.php&plugin=plugin-folder/plugin-file.php
PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)

SCREENSHOT_PATH = str(AETHER_ROOT / "exports/screenshots/plugin_editor_deploy.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")

    # Read the updated plugin content
    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars, version 1.4.0")

    if "1.4.0" not in new_content:
        print("ERROR: Plugin file does not contain version 1.4.0. Aborting.")
        sys.exit(1)

    if "api.purebrain.ai" not in new_content:
        print("ERROR: Plugin file does not contain api.purebrain.ai in CSP. Aborting.")
        sys.exit(1)

    print("Plugin content validated. Starting Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
        )
        page = context.new_page()

        # ============================================================
        # Step 1: Log in to WP Admin
        # ============================================================
        print("\nStep 1: Logging in to WP Admin...")
        # Load login page - GoDaddy SSO overlay may show first
        page.goto("https://purebrain.ai/wp-login.php", wait_until="networkidle", timeout=60000)

        # If SSO overlay is showing, click "Log in with username and password" link
        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("GoDaddy SSO overlay detected. Clicking 'Log in with username and password'...")
            sso_toggle.click()
            page.wait_for_load_state("networkidle")

        # Fill login form
        page.locator("#user_login").wait_for(state="visible", timeout=15000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASSWORD)
        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")

        current_url = page.url
        print(f"After login, URL: {current_url}")

        if "wp-login.php" in current_url:
            print("ERROR: Login failed. Check credentials.")
            page.screenshot(path=SCREENSHOT_PATH)
            print(f"Screenshot saved: {SCREENSHOT_PATH}")
            browser.close()
            sys.exit(1)

        print("Login successful.")

        # ============================================================
        # Step 2: Navigate to Plugin Editor
        # ============================================================
        print("\nStep 2: Opening Plugin Editor...")
        page.goto(PLUGIN_EDITOR_URL, wait_until="networkidle")

        # Check if we got the plugin editor
        current_url = page.url
        print(f"Plugin editor URL: {current_url}")

        # Check for the CodeMirror editor or textarea
        editor_present = page.locator("#newcontent").count() > 0 or \
                         page.locator(".CodeMirror").count() > 0

        if not editor_present:
            print("ERROR: Plugin editor textarea not found. Plugin editor may be disabled.")
            page.screenshot(path=SCREENSHOT_PATH)
            print(f"Screenshot: {SCREENSHOT_PATH}")
            # Try alternate approach - check page content
            page_text = page.inner_text("body")
            if "You need a higher level of permission" in page_text:
                print("REASON: Insufficient permissions.")
            elif "plugin editing has been disabled" in page_text.lower():
                print("REASON: Plugin editing is disabled (DISALLOW_FILE_EDIT in wp-config.php).")
            else:
                print(f"Page excerpt: {page_text[:500]}")
            browser.close()
            return False

        # ============================================================
        # Step 3: Set the new content in the editor
        # ============================================================
        print("\nStep 3: Setting new plugin content...")

        # Check if CodeMirror is present (modern WP)
        if page.locator(".CodeMirror").count() > 0:
            print("Using CodeMirror editor...")
            # Set value via JavaScript
            page.evaluate(f"""
                var cm = document.querySelector('.CodeMirror').CodeMirror;
                cm.setValue({repr(new_content)});
            """)
            print("CodeMirror content set via JS.")
        else:
            # Use the raw textarea
            print("Using raw textarea...")
            page.fill("#newcontent", new_content)
            print("Textarea content set.")

        # ============================================================
        # Step 4: Save the file
        # ============================================================
        print("\nStep 4: Saving the plugin file...")

        # Click the "Update File" button
        submit_btn = page.locator("#submit")
        if submit_btn.count() == 0:
            submit_btn = page.locator("input[type='submit']").first

        submit_btn.click()
        page.wait_for_load_state("networkidle")

        # ============================================================
        # Step 5: Verify save success
        # ============================================================
        print("\nStep 5: Verifying save...")
        page.screenshot(path=SCREENSHOT_PATH)

        page_text = page.inner_text("body")
        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("SUCCESS: Plugin file saved successfully!")
            browser.close()
            return True
        elif "Parse error" in page_text or "syntax error" in page_text:
            print("ERROR: PHP parse/syntax error detected. The file was NOT saved.")
            print("Check the plugin PHP syntax.")
            browser.close()
            return False
        else:
            print("WARNING: Could not confirm save success. Check screenshot.")
            print(f"Page excerpt: {page_text[:300]}")
            browser.close()
            # Check the current URL for clues
            return "updated" in current_url.lower()


def verify_csp_deployed():
    """Verify the new CSP header is live on the site."""
    import urllib.request
    import urllib.error

    print("\nVerifying live CSP header...")
    try:
        req = urllib.request.Request(
            "https://purebrain.ai",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response = urllib.request.urlopen(req, timeout=15)
        csp_header = response.headers.get("Content-Security-Policy-Report-Only", "")

        if "api.purebrain.ai" in csp_header:
            print("VERIFIED: api.purebrain.ai is in the live CSP header!")
            print(f"CSP header: {csp_header[:300]}...")
            return True
        elif csp_header:
            print(f"WARNING: CSP header found but api.purebrain.ai NOT in it yet.")
            print(f"Current CSP: {csp_header[:200]}...")
            return False
        else:
            print("WARNING: No CSP-Report-Only header found in response.")
            return False
    except Exception as e:
        print(f"Verification request failed: {e}")
        return False


if __name__ == "__main__":
    if not WP_PASSWORD:
        print("ERROR: PUREBRAIN_WP_APP_PASSWORD not set in .env")
        sys.exit(1)

    success = deploy()

    if success:
        print("\n" + "="*50)
        print("Deployment complete. Verifying live header...")
        verify_csp_deployed()
    else:
        print("\n" + "="*50)
        print("Deployment via plugin editor failed.")
        print("The plugin file has been updated locally at:")
        print(f"  {PLUGIN_FILE}")
        print("\nManual deployment options:")
        print("  1. WP Admin > Plugins > Plugin Editor > Select 'PureBrain Security'")
        print("     Paste content from: tools/security/purebrain-security-plugin.php")
        print("  2. WP Admin > Plugins > Add New > Upload Plugin")
        print("     Upload: tools/security/purebrain-security.zip")
        print("     (Will show 'replace current version' prompt - confirm)")
        print("  3. Use WP File Manager plugin (already installed):")
        print("     Navigate to wp-content/plugins/purebrain-security/")
        print("     Edit purebrain-security-plugin.php directly")
        sys.exit(1)
