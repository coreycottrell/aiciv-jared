#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v1.6.0 to WordPress.

Fixed version that waits for CodeMirror to load before injecting content.

Author: full-stack-developer agent
Date: 2026-02-20
"""

import os
import sys
import time
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

SCREENSHOT_PATH = str(AETHER_ROOT / "exports/screenshots/plugin_v160_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v160_verify.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v1.6.0 Deployer (fixed) ===")
    print(f"Plugin file: {PLUGIN_FILE}")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    if "1.6.0" not in new_content:
        print("ERROR: Plugin file does not contain version 1.6.0. Aborting.")
        sys.exit(1)

    if "max-width: 820px" not in new_content:
        print("ERROR: Plugin file does not contain 820px constraint. Aborting.")
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

        page.locator("#user_login").wait_for(state="visible", timeout=15000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASSWORD)
        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")

        current_url = page.url
        print(f"  After login URL: {current_url}")

        if "wp-login.php" in current_url:
            page.screenshot(path=SCREENSHOT_PATH)
            page_text = page.inner_text("body")
            print(f"  ERROR: Login failed. Page: {page_text[:300]}")
            browser.close()
            return False

        print("  Login successful!")

        # Step 2: Plugin Editor
        print("\n[Step 2] Opening Plugin Editor...")
        page.goto(PLUGIN_EDITOR_URL, wait_until="networkidle", timeout=60000)

        # Wait for either CodeMirror or raw textarea to appear
        print("  Waiting for editor to load...")
        time.sleep(3)

        page_text = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
            print("  ERROR: File editing disabled in wp-config.php")
            browser.close()
            return False
        if "You need a higher level" in page_text:
            print("  ERROR: Insufficient permissions")
            browser.close()
            return False

        # Check which editor type is present
        has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_textarea = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

        if not has_codemirror and not has_textarea:
            print("  ERROR: No editor found")
            page.screenshot(path=SCREENSHOT_PATH)
            browser.close()
            return False

        # Step 3: Set content
        print("\n[Step 3] Setting plugin content via JS...")

        if has_codemirror:
            # Use CodeMirror API - most reliable for large content
            print("  Using CodeMirror setValue()...")
            # Escape the content for JS injection
            success = page.evaluate("""(content) => {
                try {
                    const cmEl = document.querySelector('.CodeMirror');
                    if (!cmEl) return 'no_cm_element';
                    const cm = cmEl.CodeMirror;
                    if (!cm) return 'no_cm_instance';
                    cm.setValue(content);
                    // Verify it was set
                    const val = cm.getValue();
                    if (val.includes('1.6.0')) return 'success';
                    return 'set_failed';
                } catch(e) {
                    return 'error: ' + e.message;
                }
            }""", new_content)
            print(f"  CodeMirror result: {success}")

            if success != 'success':
                print("  CodeMirror failed. Trying textarea fallback...")
                # Make textarea visible and use it
                page.evaluate("""() => {
                    const ta = document.querySelector('#newcontent');
                    if (ta) {
                        ta.style.display = 'block';
                        ta.style.visibility = 'visible';
                    }
                }""")
                # Set via JS directly
                page.evaluate("""(content) => {
                    const ta = document.querySelector('#newcontent');
                    if (ta) {
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLTextAreaElement.prototype, 'value').set;
                        nativeInputValueSetter.call(ta, content);
                        ta.dispatchEvent(new Event('input', { bubbles: true }));
                        ta.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""", new_content)
                print("  Textarea fallback set.")
        else:
            # Raw textarea
            print("  Using textarea via JS...")
            page.evaluate("""(content) => {
                const ta = document.querySelector('#newcontent');
                if (ta) {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeInputValueSetter.call(ta, content);
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    ta.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", new_content)
            print("  Textarea content set.")

        time.sleep(1)

        # Step 4: Save
        print("\n[Step 4] Saving plugin file...")

        # Click the submit button
        saved = page.evaluate("""() => {
            const btn = document.querySelector('#submit') ||
                        document.querySelector('input[type="submit"]');
            if (btn) {
                btn.click();
                return 'clicked';
            }
            return 'no_button';
        }""")
        print(f"  Save button click: {saved}")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=45000)
        except Exception:
            pass
        time.sleep(4)

        page.screenshot(path=SCREENSHOT_PATH)
        page_text = page.inner_text("body")

        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin file saved!")
        elif "Parse error" in page_text or "syntax error" in page_text:
            print("  ERROR: PHP syntax error - file NOT saved!")
            print(f"  Page: {page_text[:300]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear. Checking page excerpt:")
            print(f"  {page_text[:400]}")

        # Step 5: Verify on live page
        print("\n[Step 5] Verifying live page CSS...")
        import urllib.request
        req = urllib.request.Request(
            "https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/",
            headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache, no-store"},
        )
        try:
            response = urllib.request.urlopen(req, timeout=30)
            html = response.read().decode("utf-8")
            if "max-width: 820px" in html:
                print("  CONFIRMED: 820px constraint is in live source!")

                # Extract what CSS block is live
                import re
                match = re.search(r'id="purebrain-blog-desktop-padding">(.*?)</style>', html, re.DOTALL)
                if match:
                    css = match.group(1).strip()
                    print(f"\n  Live CSS block ({len(css)} chars):")
                    for line in css.split('\n')[:20]:
                        print(f"  {line}")
                return True
            elif "max-width: 1100px" in html and "5%" in html:
                print("  WARNING: Old v1.5.0 CSS still live (CDN caching)")
                print("  The server may have updated but CDN is caching.")
                print("  Wait 5 minutes or flush CDN cache via GoDaddy dashboard.")
                return False
            else:
                print("  WARNING: Could not confirm CSS in live source.")
                return False
        except Exception as e:
            print(f"  Source verification failed: {e}")
            return False

        browser.close()


def verify_via_playwright():
    """Use Playwright to check computed styles on the live blog post."""
    from playwright.sync_api import sync_playwright
    import time

    print("\n[Computed Style Verification] Loading blog post in Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        page.goto(
            "https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/",
            wait_until="networkidle",
            timeout=60000,
        )
        time.sleep(3)

        computed = page.evaluate("""() => {
            const postContent = document.querySelector('.post-content');
            const postSingleImage = document.querySelector('.post-single-image');
            const container = document.querySelector('.page-single-post .container');
            const row = document.querySelector('.page-single-post .container > .row');

            const getCS = (el, prop) => {
                if (!el) return 'element not found';
                return window.getComputedStyle(el)[prop];
            };

            return {
                viewport_width: window.innerWidth,
                container_maxWidth: getCS(container, 'maxWidth'),
                container_paddingLeft: getCS(container, 'paddingLeft'),
                content_maxWidth: getCS(postContent, 'maxWidth'),
                content_marginLeft: getCS(postContent, 'marginLeft'),
                image_maxWidth: getCS(postSingleImage, 'maxWidth'),
                image_borderRadius: getCS(postSingleImage, 'borderRadius'),
            };
        }""")

        print(f"\n  Viewport: {computed['viewport_width']}px")
        print(f"  .page-single-post .container max-width: {computed['container_maxWidth']}")
        print(f"  .page-single-post .container padding-left: {computed['container_paddingLeft']}")
        print(f"  .post-content max-width: {computed['content_maxWidth']}")
        print(f"  .post-content margin-left: {computed['content_marginLeft']}")
        print(f"  .post-single-image max-width: {computed['image_maxWidth']}")
        print(f"  .post-single-image border-radius: {computed['image_borderRadius']}")

        page.screenshot(path=SCREENSHOT_VERIFY, full_page=True)
        print(f"\n  Screenshot: {SCREENSHOT_VERIFY}")

        browser.close()


if __name__ == "__main__":
    if not WP_PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not set in .env")
        sys.exit(1)

    print(f"Using WP user: {WP_USER}")
    print(f"Password loaded: {'*' * len(WP_PASSWORD)}")

    success = deploy()

    print("\n" + "=" * 60)
    if success:
        print("DEPLOYMENT COMPLETE - v1.6.0 is live!")
        print("\nChanges deployed:")
        print("  - .post-single-image: max-width 820px, 12px rounded corners")
        print("  - .post-content: max-width 820px, centered")
        print("  - .page-single-post .container: max-width 1100px, 40px padding")
        print("  - Bootstrap .row negative margins reset to 0")
        print("  - Desktop only: @media (min-width: 1025px)")
        verify_via_playwright()
    else:
        print("DEPLOYMENT FAILED OR PENDING CDN CACHE FLUSH")
        print("\nManual option:")
        print("  WP Admin > Plugins > Plugin Editor > PureBrain Security")
        print("  Or upload: tools/security/purebrain-security.zip")
        sys.exit(1)
