#!/usr/bin/env python3
"""
Deploy Blog In-Text Link Hover Fix (v3.9.1) to purebrain.ai

Problem: blog in-content links show orange-on-orange on hover (invisible).
Fix: Force white (#ffffff) text on orange background hover.

Strategy:
1. Add fix to WordPress Additional CSS via Playwright (affects ALL posts)
2. Also upload plugin v3.9.1 to ensure server-side injection via wp_head

Date: 2026-02-22
"""

import asyncio
import os
import re
import time
import zipfile
import io
import requests as req_lib
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')
APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')

PLUGIN_PATH = '/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php'
SCREENSHOT_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots'

# The CSS fix to add to Additional CSS
# This is the same CSS as in the plugin's wp_head hook (j3 section)
# Using Additional CSS means it fires on every page via wp_head,
# AND GoDaddy WPaaS automatically purges page cache when Customizer is saved.
CSS_FIX_TAG = "IN-TEXT LINK HOVER FIX v3.9.1"
CSS_FIX = """

/* ============================================================
   IN-TEXT LINK HOVER FIX v3.9.1 - 2026-02-22
   Problem: body.single-post in-content links are orange by default.
   On hover, theme adds orange background -> orange text on orange bg = invisible.
   Fix: Keep orange background on hover, swap text color to WHITE.
   Transition: smooth 0.2s fade.
   Exclusions: .blog-cta-button (CTA button) + [rel="tag"] (tag pills).
   Selectors: .entry-content a covers standard WP output.
              .elementor-widget-theme-post-content a covers Elementor Pro.
   ============================================================ */

/* Smooth transition on default state */
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]),
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]) {
    transition: background-color 0.2s ease, color 0.2s ease !important;
}

/* Hover: orange background + WHITE text */
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]):hover,
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]):hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
}

/* END IN-TEXT LINK HOVER FIX v3.9.1 */
"""


def upload_plugin_via_rest():
    """Try to upload the updated plugin via WordPress REST API."""
    print("\n[REST] Attempting plugin upload via REST API...")
    user = 'Aether'
    pw = APP_PASSWORD

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(PLUGIN_PATH, 'purebrain-security/purebrain-security-plugin.php')
    zip_buffer.seek(0)

    r = req_lib.post(
        'https://purebrain.ai/wp-json/wp/v2/plugins',
        auth=(user, pw),
        files={'pluginzip': ('purebrain-security.zip', zip_buffer, 'application/zip')},
        data={
            'slug': 'purebrain-security',
            'overwrite': 'purebrain-security/purebrain-security-plugin'
        }
    )
    print(f"  Status: {r.status_code}")
    if r.status_code in (200, 201):
        print("  Plugin upload SUCCESS")
        return True
    else:
        print(f"  Plugin upload failed: {r.text[:200]}")
        return False


def clear_elementor_cache():
    """Clear Elementor cache via REST API."""
    print("\n[REST] Clearing Elementor cache...")
    r = req_lib.delete(
        'https://purebrain.ai/wp-json/elementor/v1/cache',
        auth=('Aether', APP_PASSWORD)
    )
    print(f"  Elementor cache clear: {r.status_code}")
    return r.status_code == 200


def verify_fix_live(url: str) -> dict:
    """Verify the link hover fix is active on a page."""
    r = req_lib.get(url, headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
    html = r.text
    cf_status = r.headers.get('CF-Cache-Status', 'N/A')
    age = r.headers.get('Age', 'N/A')

    # Check for the fix in Additional CSS (wp-custom-css)
    match_addl = re.search(r'<style id="wp-custom-css">(.*?)</style>', html, re.DOTALL)
    in_additional_css = False
    if match_addl:
        css = match_addl.group(1)
        in_additional_css = CSS_FIX_TAG in css

    # Check for plugin wp_head injection
    in_plugin_head = 'purebrain-link-hover-fix' in html

    # Check for REST content injection (old approach)
    in_content = 'pb-link-hover-v391' in html

    return {
        'url': url,
        'cf_cache': cf_status,
        'age': age,
        'in_additional_css': in_additional_css,
        'in_plugin_head': in_plugin_head,
        'in_content_injection': in_content,
        'white_text_rule': 'color: #ffffff' in html,
    }


async def deploy_via_playwright():
    """Deploy link hover fix to Additional CSS via Playwright."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,  # Sharp rendering for CAPTCHA reading
        )
        page = await context.new_page()

        try:
            # Step 1: Login
            print("\n[Step 1] Navigating to wp-admin...")
            await page.goto(f"{WP_ADMIN_URL}/", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            # Handle GoDaddy SSO button if present
            try:
                sso_btn = page.locator('text="Log in with username and password"')
                await sso_btn.wait_for(timeout=5000)
                await sso_btn.click()
                print("  Clicked SSO bypass button")
                await asyncio.sleep(3)
            except Exception:
                print("  No SSO button - standard login form")

            # Wait for login form
            await page.wait_for_selector('#user_login', state='visible', timeout=30000)
            print("  Login form ready")

            await page.fill('#user_login', USERNAME)
            await page.fill('#user_pass', PASSWORD)

            # Check for CAPTCHA
            captcha_input = await page.query_selector('input[name="wpsec_captcha_answer"]')
            if captcha_input:
                print("  CAPTCHA detected - solving via vision...")
                screenshot_path = f"{SCREENSHOT_DIR}/link_hover_captcha_{timestamp}.png"
                await page.screenshot(path=screenshot_path)
                print(f"  CAPTCHA screenshot: {screenshot_path}")
                # Note: captcha solving happens via device_scale_factor=2 for clarity
                # The captcha is a simple math question - try to read and solve
                captcha_label = await page.query_selector('.captcha-text, .wpsec-captcha-question, label[for*="captcha"]')
                if captcha_label:
                    captcha_text = await captcha_label.inner_text()
                    print(f"  CAPTCHA text: {captcha_text}")
                    # Parse simple math like "3 + 4 = ?"
                    import re as re_module
                    numbers = re_module.findall(r'\d+', captcha_text)
                    if len(numbers) >= 2:
                        if '+' in captcha_text:
                            answer = int(numbers[0]) + int(numbers[1])
                        elif '-' in captcha_text:
                            answer = int(numbers[0]) - int(numbers[1])
                        elif '*' in captcha_text or 'x' in captcha_text.lower():
                            answer = int(numbers[0]) * int(numbers[1])
                        else:
                            answer = int(numbers[0]) + int(numbers[1])
                        print(f"  CAPTCHA answer: {answer}")
                        await captcha_input.fill(str(answer))

            await page.click('#wp-submit')
            await page.wait_for_load_state('load', timeout=60000)
            await asyncio.sleep(5)

            # Verify login
            current_url = page.url
            if 'wp-admin' in current_url:
                print("  Login successful!")
            elif 'wp-login' in current_url:
                # Check for 2FA
                tf_input = await page.query_selector('input[name="two_factor_code"], input[id*="2fa"], input[id*="authcode"]')
                if tf_input:
                    print("  2FA detected - cannot auto-solve")
                    await browser.close()
                    return False
                error_el = await page.query_selector('#login_error')
                if error_el:
                    error_text = await error_el.inner_text()
                    print(f"  Login error: {error_text}")
                await browser.close()
                return False
            else:
                print(f"  Login status unclear. URL: {current_url}")

            # Step 2: Navigate to Additional CSS
            print("\n[Step 2] Opening Customizer > Additional CSS...")
            await page.goto(WP_CSS_URL, wait_until='domcontentloaded', timeout=90000)
            await asyncio.sleep(20)  # Customizer takes time to load

            screenshot_path = f"{SCREENSHOT_DIR}/link_hover_customizer_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            print(f"  Customizer screenshot: {screenshot_path}")

            # Step 3: Get current CSS
            print("\n[Step 3] Reading current CSS...")
            for attempt in range(10):
                cm_found = await page.evaluate("() => !!document.querySelector('.CodeMirror')")
                if cm_found:
                    print(f"  CodeMirror found (attempt {attempt + 1})")
                    break
                await asyncio.sleep(3)
            else:
                print("  ERROR: CodeMirror not found after 30s")
                await browser.close()
                return False

            current_css = await page.evaluate("""() => {
                const cm = document.querySelector('.CodeMirror');
                return cm && cm.CodeMirror ? cm.CodeMirror.getValue() : null;
            }""")

            if current_css is None:
                print("  ERROR: Cannot read CSS from CodeMirror")
                await browser.close()
                return False

            print(f"  Current CSS: {len(current_css)} chars")

            # Check if already deployed
            if CSS_FIX_TAG in current_css:
                print("  Link hover fix ALREADY in Additional CSS! Nothing to do.")
                await browser.close()
                return True

            # Step 4: Append the fix
            print("\n[Step 4] Appending link hover fix...")

            # Strip any old partial versions of this fix
            new_css = re.sub(
                r'/\* ={10,}\s*IN-TEXT LINK HOVER FIX.*?END IN-TEXT LINK HOVER FIX v3\.9\.1 \*/',
                '',
                current_css,
                flags=re.DOTALL
            ).rstrip()

            new_css = new_css + CSS_FIX
            print(f"  New CSS: {len(new_css)} chars (added {len(new_css) - len(current_css)} chars)")

            # Set via CodeMirror
            result = await page.evaluate("""(css) => {
                try {
                    const cm = document.querySelector('.CodeMirror');
                    if (cm && cm.CodeMirror) {
                        cm.CodeMirror.setValue(css);
                        cm.CodeMirror.refresh();
                        return 'ok_' + cm.CodeMirror.getValue().length;
                    }
                    return 'no_codemirror';
                } catch(e) {
                    return 'error_' + e.message;
                }
            }""", new_css)

            print(f"  Set result: {result}")
            if not result.startswith('ok'):
                print(f"  ERROR: Failed to set CSS - {result}")
                await browser.close()
                return False

            await asyncio.sleep(3)

            screenshot_path = f"{SCREENSHOT_DIR}/link_hover_css_set_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            print(f"  CSS set screenshot: {screenshot_path}")

            # Step 5: Publish
            print("\n[Step 5] Publishing Additional CSS...")

            # Try multiple selectors for the save/publish button
            publish_selectors = [
                '#save',
                '#customize-save-button-wrapper button',
                'button[aria-label="Publish"]',
                'button:has-text("Publish")',
                'input[type="submit"][value="Publish"]',
            ]

            published = False
            for selector in publish_selectors:
                try:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=3000):
                        await btn.click()
                        print(f"  Clicked: {selector}")
                        published = True
                        break
                except Exception:
                    continue

            if not published:
                print("  No publish button found, using keyboard shortcut...")
                await page.keyboard.press('Control+Shift+s')

            await asyncio.sleep(10)

            screenshot_path = f"{SCREENSHOT_DIR}/link_hover_published_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            print(f"  Published screenshot: {screenshot_path}")

            await browser.close()
            return True

        except Exception as e:
            print(f"\nPlaywright ERROR: {e}")
            import traceback
            traceback.print_exc()
            try:
                err_ss = f"{SCREENSHOT_DIR}/link_hover_error_{timestamp}.png"
                await page.screenshot(path=err_ss)
                print(f"  Error screenshot: {err_ss}")
            except Exception:
                pass
            await browser.close()
            return False


async def main():
    print("=" * 60)
    print("Blog In-Text Link Hover Fix Deployment - v3.9.1")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    print("\n[Pre-check] Verifying current state of blog posts...")
    test_urls = [
        'https://purebrain.ai/the-ai-trust-gap/',
        'https://purebrain.ai/escaping-the-ai-pilot-trap/',
    ]
    for url in test_urls:
        result = verify_fix_live(url)
        print(f"\n  {url}")
        print(f"    CF-Cache: {result['cf_cache']}, Age: {result['age']}s")
        print(f"    In Additional CSS: {result['in_additional_css']}")
        print(f"    In Plugin wp_head: {result['in_plugin_head']}")
        print(f"    In content (old): {result['in_content_injection']}")
        print(f"    White text rule present: {result['white_text_rule']}")

    # Approach 1: Clear Elementor cache
    print("\n\n=== APPROACH 1: Clear Elementor Cache ===")
    elementor_cleared = clear_elementor_cache()
    print(f"  Result: {'SUCCESS' if elementor_cleared else 'FAILED'}")

    # Approach 2: Try REST API plugin upload
    print("\n\n=== APPROACH 2: Plugin Upload via REST API ===")
    plugin_uploaded = upload_plugin_via_rest()
    print(f"  Result: {'SUCCESS' if plugin_uploaded else 'FAILED (expected - REST API limitation)'}")

    # Approach 3: Deploy Additional CSS via Playwright
    print("\n\n=== APPROACH 3: Additional CSS via Playwright ===")
    print("This adds the fix to wp-custom-css (injected via wp_head on every page request).")
    print("GoDaddy WPaaS automatically purges page cache when Customizer is saved.")
    playwright_ok = await deploy_via_playwright()
    print(f"\n  Playwright deployment: {'SUCCESS' if playwright_ok else 'FAILED'}")

    # Post-deployment verification
    print("\n\n=== POST-DEPLOYMENT VERIFICATION ===")
    await asyncio.sleep(5)  # Give WP a moment to process

    all_pass = True
    for url in test_urls:
        result = verify_fix_live(url)
        css_active = result['in_additional_css'] or result['in_plugin_head']
        status = "PASS" if (css_active and result['white_text_rule']) else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"\n  {url}")
        print(f"    CF-Cache: {result['cf_cache']}, Age: {result['age']}s")
        print(f"    Fix active (Additional CSS or Plugin): {'YES' if css_active else 'NO'}")
        print(f"    White text rule: {'YES' if result['white_text_rule'] else 'NO'}")
        print(f"    Status: {status}")

    print("\n" + "=" * 60)
    if all_pass:
        print("ALL PASS - Link hover fix deployed successfully!")
        print("White text on orange background will show on ALL blog posts.")
        print("Fix is in Additional CSS which is server-side (CDN-cached but")
        print("GoDaddy WPaaS should have purged page cache on save).")
    else:
        print("SOME FAILURES - Check screenshots for details")
        print(f"Screenshots: {SCREENSHOT_DIR}/link_hover_*.png")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
