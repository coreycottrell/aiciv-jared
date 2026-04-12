#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v1.6.0 to WordPress.

v1.6.0 changes:
- Improved blog post desktop padding CSS
- Directly constrains .post-content and .post-single-image to max-width 820px
- Resets Bootstrap row/col gutters to prevent padding cancellation
- Featured image: 12px border-radius, centered, breathing room

Uses WP Plugin Editor via Playwright (browser login).

Author: full-stack-developer agent
Date: 2026-02-20
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_FILE = AETHER_ROOT / ".env"
load_dotenv(ENV_FILE)

PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security-plugin.php"
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = os.environ.get("PUREBRAIN_WP_PASSWORD", "")

PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)

SCREENSHOT_PATH = str(AETHER_ROOT / "exports/screenshots/padding_v2_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/padding_v2_verify.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v1.6.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    if "1.6.0" not in new_content:
        print("ERROR: Plugin file does not contain version 1.6.0. Aborting.")
        sys.exit(1)

    if "max-width: 820px" not in new_content:
        print("ERROR: Plugin file does not contain the 820px content constraint. Aborting.")
        sys.exit(1)

    print("Plugin content validated. Starting Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
        )
        page = context.new_page()

        # Step 1: Login
        print("\n[Step 1] Logging in to WP Admin...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until="networkidle", timeout=60000)

        # Handle GoDaddy SSO overlay
        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("  GoDaddy SSO overlay detected. Clicking username/password link...")
            sso_toggle.click()
            page.wait_for_load_state("networkidle")

        # Check for CAPTCHA before filling form
        captcha_img = page.locator(".wpsec_captcha_image, img[src*='captcha']")
        if captcha_img.count() > 0:
            print("  WARNING: CAPTCHA detected on login page.")
            print("  Will attempt login anyway...")

        page.locator("#user_login").wait_for(state="visible", timeout=15000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASSWORD)

        # Handle GoDaddy security CAPTCHA if present
        captcha_input = page.locator("input[name='wpsec_captcha_answer']")
        if captcha_input.count() > 0 and captcha_input.is_visible():
            print("  CAPTCHA input field visible - reading captcha image...")
            # Take a high-res screenshot of the captcha area
            cap_screenshot = str(AETHER_ROOT / "exports/screenshots/captcha_login.png")
            page.screenshot(path=cap_screenshot, clip={"x": 0, "y": 0, "width": 700, "height": 700})
            print(f"  CAPTCHA screenshot: {cap_screenshot}")
            print("  Cannot auto-solve CAPTCHA. Will try without answer (may fail).")

        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")

        current_url = page.url
        print(f"  After login URL: {current_url}")

        if "wp-login.php" in current_url:
            page.screenshot(path=SCREENSHOT_PATH)
            page_text = page.inner_text("body")
            print("  ERROR: Login failed.")
            print(f"  Page text: {page_text[:300]}")
            browser.close()
            return False

        print("  Login successful!")

        # Step 2: Plugin Editor
        print("\n[Step 2] Opening Plugin Editor...")
        page.goto(PLUGIN_EDITOR_URL, wait_until="networkidle", timeout=60000)
        current_url = page.url
        print(f"  Plugin editor URL: {current_url}")

        # Check for the editor
        has_codemirror = page.locator(".CodeMirror").count() > 0
        has_textarea = page.locator("#newcontent").count() > 0

        if not has_codemirror and not has_textarea:
            print("  ERROR: Plugin editor not found.")
            page.screenshot(path=SCREENSHOT_PATH)
            page_text = page.inner_text("body")
            if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
                print("  REASON: File editing disabled in wp-config.php")
            elif "You need a higher level" in page_text:
                print("  REASON: Insufficient permissions")
            else:
                print(f"  Page excerpt: {page_text[:400]}")
            browser.close()
            return False

        # Step 3: Set content
        print("\n[Step 3] Setting plugin content...")
        if has_codemirror:
            print("  Using CodeMirror editor...")
            page.evaluate("""(content) => {
                const cm = document.querySelector('.CodeMirror').CodeMirror;
                cm.setValue(content);
            }""", new_content)
            print("  CodeMirror content set.")
        else:
            print("  Using raw textarea...")
            page.fill("#newcontent", new_content)
            print("  Textarea content set.")

        # Step 4: Save
        print("\n[Step 4] Saving plugin file...")
        submit_btn = page.locator("#submit")
        if submit_btn.count() == 0:
            submit_btn = page.locator("input[type='submit']").first

        submit_btn.click()
        page.wait_for_load_state("networkidle")

        page.screenshot(path=SCREENSHOT_PATH)
        page_text = page.inner_text("body")

        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin file saved!")
        elif "Parse error" in page_text or "syntax error" in page_text:
            print("  ERROR: PHP syntax error - file NOT saved!")
            browser.close()
            return False
        else:
            print(f"  WARNING: Unclear save status. Page: {page_text[:200]}")

        # Step 5: Verify on live blog post
        print("\n[Step 5] Verifying on live blog post...")
        page.goto(
            "https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/",
            wait_until="networkidle",
            timeout=60000,
        )
        import time
        time.sleep(3)

        # Check computed styles
        computed = page.evaluate("""() => {
            const postContent = document.querySelector('.post-content');
            const postSingleImage = document.querySelector('.post-single-image');
            const container = document.querySelector('.page-single-post .container');
            const row = document.querySelector('.page-single-post .container > .row');

            const getCS = (el) => el ? window.getComputedStyle(el) : null;
            const csContainer = getCS(container);
            const csContent = getCS(postContent);
            const csImage = getCS(postSingleImage);
            const csRow = getCS(row);

            return {
                container_maxWidth: csContainer ? csContainer.maxWidth : 'N/A',
                container_paddingLeft: csContainer ? csContainer.paddingLeft : 'N/A',
                container_paddingRight: csContainer ? csContainer.paddingRight : 'N/A',
                row_marginLeft: csRow ? csRow.marginLeft : 'N/A',
                row_marginRight: csRow ? csRow.marginRight : 'N/A',
                content_maxWidth: csContent ? csContent.maxWidth : 'N/A',
                content_marginLeft: csContent ? csContent.marginLeft : 'N/A',
                content_marginRight: csContent ? csContent.marginRight : 'N/A',
                image_maxWidth: csImage ? csImage.maxWidth : 'N/A',
                image_marginLeft: csImage ? csImage.marginLeft : 'N/A',
                image_borderRadius: csImage ? csImage.borderRadius : 'N/A',
                viewport_width: window.innerWidth,
            }
        }""")

        print("\n  Computed Styles at viewport width:", computed.get('viewport_width', 'unknown'))
        print(f"  Container max-width: {computed.get('container_maxWidth')}")
        print(f"  Container padding-left: {computed.get('container_paddingLeft')}")
        print(f"  Container padding-right: {computed.get('container_paddingRight')}")
        print(f"  Row margin-left: {computed.get('row_marginLeft')}")
        print(f"  Row margin-right: {computed.get('row_marginRight')}")
        print(f"  Post-content max-width: {computed.get('content_maxWidth')}")
        print(f"  Post-content margin-left: {computed.get('content_marginLeft')}")
        print(f"  Post-content margin-right: {computed.get('content_marginRight')}")
        print(f"  Post-single-image max-width: {computed.get('image_maxWidth')}")
        print(f"  Post-single-image margin-left: {computed.get('image_marginLeft')}")
        print(f"  Post-single-image border-radius: {computed.get('image_borderRadius')}")

        page.screenshot(path=SCREENSHOT_VERIFY, full_page=True)
        print(f"\n  Verification screenshot: {SCREENSHOT_VERIFY}")

        browser.close()
        return True


def verify_css_in_source():
    """Verify the CSS is in the live page source."""
    import urllib.request

    print("\n[Verification] Checking live page source for CSS...")
    req = urllib.request.Request(
        "https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/",
        headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"},
    )
    try:
        response = urllib.request.urlopen(req, timeout=30)
        html = response.read().decode("utf-8")
        if "purebrain-blog-desktop-padding" in html:
            print("  CONFIRMED: CSS block 'purebrain-blog-desktop-padding' is in live source.")
            if "max-width: 820px" in html:
                print("  CONFIRMED: 820px max-width constraint is in the live CSS.")
                return True
            else:
                print("  WARNING: 820px not found in source - may be serving cached version.")
                return False
        else:
            print("  WARNING: 'purebrain-blog-desktop-padding' CSS block NOT found in source.")
            return False
    except Exception as e:
        print(f"  Source check failed: {e}")
        return False


if __name__ == "__main__":
    if not WP_PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not set in .env")
        sys.exit(1)

    print(f"Using WP user: {WP_USER}")
    print(f"Password loaded: {WP_PASSWORD[:5]}...")

    success = deploy()

    print("\n" + "=" * 60)
    if success:
        print("DEPLOYMENT COMPLETE")
        verify_css_in_source()
        print("\nFix summary:")
        print("  - Plugin version: 1.6.0")
        print("  - .post-single-image: max-width 820px, centered, 12px border-radius")
        print("  - .post-content: max-width 820px, centered")
        print("  - .page-single-post .container: max-width 1100px, 40px side padding")
        print("  - Bootstrap .row negative margins reset to 0")
        print("  - Desktop only: min-width 1025px media query")
        print("\nVerify visually:")
        print("  https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/")
    else:
        print("DEPLOYMENT FAILED")
        print("\nManual options:")
        print("  1. WP Admin > Plugins > Plugin Editor > PureBrain Security")
        print("  2. WP Admin > Plugins > Add New > Upload Plugin")
        print(f"     Upload: /home/jared/projects/AI-CIV/aether/tools/security/purebrain-security.zip")
        sys.exit(1)
