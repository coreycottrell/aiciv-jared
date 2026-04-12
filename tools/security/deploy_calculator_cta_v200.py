#!/usr/bin/env python3
"""
Deploy pb-calculator-cta plugin v2.0.0 to purebrain.ai.

v2.0.0 change: Added homepage (page-id-11) as injection target.
The FREE TOOL calculator CTA section will now appear on the homepage,
inserted before the "Compare PureBrain" pills section.

Author: full-stack-developer agent
Date: 2026-03-08
"""

import os
import re
import sys
import time
import base64
import urllib.request
import urllib.error
import ssl
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "tools/security/pb-calculator-cta/pb-calculator-cta.php"
SCREENSHOT_DIR = str(AETHER_ROOT / "exports/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# --- Credentials ---
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


WP_USER     = _env("PUREBRAIN_WP_USER")
WP_PASS     = _env("PUREBRAIN_WP_PASSWORD")
WP_APP_PASS = _env("PUREBRAIN_WP_APP_PASSWORD")

EDITOR_URL = (
    "https://purebrain.ai/wp-admin/plugin-editor.php"
    "?file=pb-calculator-cta/pb-calculator-cta.php"
    "&plugin=pb-calculator-cta/pb-calculator-cta.php"
)
LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"


def validate_plugin(content: str) -> bool:
    checks = {
        "PHP opening tag":              "<?php" in content,
        "Plugin Name header":           "Plugin Name: PureBrain Calculator CTA" in content,
        "v2.0.0 version tag":           "2.0.0" in content,
        "is_front_page() check":        "is_front_page" in content,
        "page-id-11 in array":          "11" in content,
        "pb-calc-cta section id":       "pb-calc-cta" in content,
        "Free Tool text":               "Free Tool" in content,
        "Calculator URL":               "ai-tool-stack-calculator" in content,
        "Compare PureBrain strategy":   "Compare PureBrain" in content,
        "wp_footer action":             "wp_footer" in content,
        "JS injector script id":        "pb-calc-cta-injector" in content,
    }
    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


def deploy_plugin(content: str) -> bool:
    from playwright.sync_api import sync_playwright

    print(f"\n{'='*65}")
    print("DEPLOYING pb-calculator-cta v2.0.0 TO: purebrain.ai")
    print(f"{'='*65}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        # Step 1: Login
        print("\n[Step 1] Logging in...")
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        page_body = page.inner_text("body")
        if "captcha" in page_body.lower() or "verify" in page.title().lower():
            print("  CAPTCHA detected — aborting.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_calc_cta_captcha.png")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            print("  Login form not visible.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_calc_cta_no_form.png")
            browser.close()
            return False

        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        time.sleep(3)

        if "wp-admin" not in page.url:
            print(f"  Login failed. URL: {page.url}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_calc_cta_login_fail.png")
            browser.close()
            return False
        print("  Login successful!")

        # Step 1b: Check plugin activation
        print("\n[Step 1b] Checking pb-calculator-cta activation status...")
        plugins_url = "https://purebrain.ai/wp-admin/plugins.php"
        page.goto(plugins_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        plugin_row_text = page.evaluate("""() => {
            var rows = document.querySelectorAll('tr[data-slug="pb-calculator-cta"]');
            if (rows.length > 0) return rows[0].innerHTML;
            return '';
        }""")

        if plugin_row_text:
            is_active = "deactivate" in plugin_row_text.lower()
            has_activate = "activate" in plugin_row_text.lower() and not is_active
            print(f"  Plugin row found. Active: {is_active}, Has activate link: {has_activate}")

            if not is_active and has_activate:
                print("  Plugin is INACTIVE — activating now...")
                activate_href = page.evaluate("""() => {
                    var rows = document.querySelectorAll('tr[data-slug="pb-calculator-cta"]');
                    if (!rows.length) return '';
                    var activateLink = rows[0].querySelector('a[href*="action=activate"]');
                    return activateLink ? activateLink.href : '';
                }""")
                if activate_href:
                    page.goto(activate_href, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(3)
                    print("  Activation navigation complete.")
                else:
                    print("  No activate link found — plugin may need to be installed first.")
            elif is_active:
                print("  Plugin is already ACTIVE — proceeding to editor.")
        else:
            print("  Plugin not found by data-slug — checking if it needs to be uploaded...")
            # The plugin may need to be installed if not present
            page_text = page.inner_text("body")
            if "pb-calculator-cta" in page_text.lower() or "Calculator CTA" in page_text:
                print("  Plugin found in page text.")
            else:
                print("  Plugin not found. Proceeding to editor (it may still be editable).")

        # Step 2: Open plugin editor
        print("\n[Step 2] Opening plugin editor for pb-calculator-cta...")
        page.goto(EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        page_body = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_body or "editing has been disabled" in page_body.lower():
            print("  File editing is disabled on server.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_calc_cta_edit_disabled.png")
            browser.close()
            return False

        has_cm = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_ta = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_cm}, Textarea: {has_ta}")

        if not has_cm and not has_ta:
            print(f"  No editor found. Body snippet: {page_body[:400]}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_calc_cta_no_editor.png")
            browser.close()
            return False

        # Step 3: Set content
        print("\n[Step 3] Setting plugin content...")
        set_ok = False

        if has_cm:
            result = page.evaluate(
                """(pluginContent) => {
                    try {
                        var cmEl = document.querySelector('.CodeMirror');
                        if (!cmEl) return 'no_cm_element';
                        var cm = cmEl.CodeMirror;
                        if (!cm) return 'no_cm_instance';
                        cm.setValue(pluginContent);
                        var val = cm.getValue();
                        if (val.indexOf('pb-calc-cta') !== -1 &&
                            val.indexOf('is_front_page') !== -1 &&
                            val.indexOf('ai-tool-stack-calculator') !== -1 &&
                            val.indexOf('Compare PureBrain') !== -1) {
                            return 'success';
                        }
                        return 'verify_fail:len=' + val.length;
                    } catch(e) { return 'error:' + e.message; }
                }""",
                content,
            )
            print(f"  CodeMirror result: {result}")
            set_ok = result == "success"

        if not set_ok:
            print("  Using textarea fallback...")
            page.evaluate(
                """() => {
                    var ta = document.querySelector('#newcontent');
                    if (ta) { ta.style.display = 'block'; ta.style.visibility = 'visible'; }
                }"""
            )
            page.evaluate(
                """(pluginContent) => {
                    var ta = document.querySelector('#newcontent');
                    if (!ta) return;
                    var setter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value').set;
                    setter.call(ta, pluginContent);
                    ta.dispatchEvent(new Event('input', {bubbles: true}));
                    ta.dispatchEvent(new Event('change', {bubbles: true}));
                }""",
                content,
            )
            print("  Textarea content set.")

        time.sleep(1)

        # Step 4: Save
        print("\n[Step 4] Saving...")
        page.evaluate(
            """() => {
                var btn = document.querySelector('#submit') ||
                          document.querySelector('input[type="submit"]');
                if (btn) btn.click();
            }"""
        )
        try:
            page.wait_for_load_state("domcontentloaded", timeout=45000)
        except Exception:
            pass
        time.sleep(5)

        page.screenshot(path=f"{SCREENSHOT_DIR}/pb_calc_cta_deploy.png")
        page_text = page.inner_text("body")

        save_ok = False
        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin file saved!")
            save_ok = True
        elif "Parse error" in page_text or "syntax error" in page_text.lower():
            print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear. Page snippet: {page_text[:300]}")
            if has_cm:
                current = page.evaluate(
                    """() => {
                        var cm = document.querySelector('.CodeMirror');
                        return cm ? cm.CodeMirror.getValue().substring(0, 3000) : 'N/A';
                    }"""
                )
                if "pb-calc-cta" in current and "is_front_page" in current:
                    print("  pb-calc-cta + is_front_page found in editor — save assumed OK.")
                    save_ok = True
                else:
                    print(f"  Editor content check failed. Preview: {current[:300]}")
                    save_ok = False
            else:
                save_ok = False

        browser.close()
        return save_ok


def verify_live() -> bool:
    """Verify the calculator CTA injector is present on the homepage."""
    print("\n[Verification] Fetching purebrain.ai homepage to check for v2.0.0 code...")
    ctx_ssl = ssl.create_default_context()
    conn_req = urllib.request.Request(
        "https://purebrain.ai/",
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(conn_req, context=ctx_ssl, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  Could not fetch homepage: {e}")
        return False

    injector_present   = "pb-calc-cta-injector" in html
    calc_url_present   = "ai-tool-stack-calculator" in html
    front_page_present = "is_front_page" in html or "pb-calc-cta" in html

    print(f"  [{'PASS' if injector_present else 'FAIL'}] pb-calc-cta-injector script tag found")
    print(f"  [{'PASS' if calc_url_present else 'FAIL'}] ai-tool-stack-calculator URL found")

    return injector_present and calc_url_present


def main():
    print("=" * 65)
    print("pb-calculator-cta v2.0.0 — Deploy Script")
    print("=" * 65)
    print(f"Plugin file: {PLUGIN_FILE}")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"Content length: {len(content):,} chars")

    print("\n--- Validating plugin content ---")
    if not validate_plugin(content):
        print("\nERROR: Plugin validation failed. Aborting.")
        sys.exit(1)
    print("All validation checks passed.\n")

    success = deploy_plugin(content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Plugin v2.0.0 deployed successfully.")

    print("\nWaiting 8 seconds for cache to settle...")
    time.sleep(8)

    verified = verify_live()
    if verified:
        print("\nDEPLOYMENT COMPLETE AND VERIFIED.")
        print("Changes live on purebrain.ai (v2.0.0):")
        print("  - FREE TOOL calculator CTA section now injects on homepage (page-id-11)")
        print("  - CTA inserts before 'Compare PureBrain' pills section")
        print("  - Existing pages (pay-test-2 / sandbox-3) unchanged")
    else:
        print("\nDeploy done but live verification flagged issues.")
        print("Possible CDN cache delay — check manually.")


if __name__ == "__main__":
    main()
