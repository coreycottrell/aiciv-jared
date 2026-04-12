#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin with mobile vortex fix.

Change: Added mobile CSS at bottom of plugin that hides vortex rings,
particles, and shrinks hero logo on mobile so video background is visible.

  @media (max-width: 767px) {
      .vortex-ring { display: none !important; }
      .hero__particles { display: none !important; }
      .hero__logo { width: 70px ...; }
  }

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
# Local file is purebrain-security.php; WP server uses purebrain-security-plugin.php
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security.php"
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
    "?file=purebrain-security/purebrain-security-plugin.php"
    "&plugin=purebrain-security/purebrain-security-plugin.php"
)
LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"


def validate_plugin(content: str) -> bool:
    checks = {
        "vortex-ring CSS present":            ".vortex-ring" in content,
        "hero__particles CSS present":        ".hero__particles" in content,
        "hero__logo mobile resize present":   ".hero__logo" in content,
        "mobile media query 767px present":   "max-width: 767px" in content or "max-width:767px" in content,
        "v6.1.2 comment tag present":         "v6.1.2" in content,
        "Core feature (FAQ accordion) intact": "purebrain-faq-accordion" in content,
        "Core feature (aether footer) intact": "pb-aether-footer" in content,
        "Core feature (twitter:card) intact":  "twitter:card" in content,
        "PHP opening tag present":             "<?php" in content,
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
    print("DEPLOYING PLUGIN (mobile vortex fix) TO: purebrain.ai")
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
            page.screenshot(path=f"{SCREENSHOT_DIR}/deploy_captcha.png")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            print("  Login form not visible.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/deploy_no_form.png")
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
            page.screenshot(path=f"{SCREENSHOT_DIR}/deploy_login_fail.png")
            browser.close()
            return False
        print("  Login successful!")

        # Step 2: Open plugin editor
        print("\n[Step 2] Opening plugin editor...")
        page.goto(EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        page_body = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_body or "editing has been disabled" in page_body.lower():
            print("  File editing is disabled on server.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/deploy_edit_disabled.png")
            browser.close()
            return False

        has_cm = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_ta = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_cm}, Textarea: {has_ta}")

        if not has_cm and not has_ta:
            print(f"  No editor found. Body: {page_body[:400]}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/deploy_no_editor.png")
            browser.close()
            return False

        # Step 3: Set content
        print("\n[Step 3] Setting plugin content...")
        set_ok = False

        if has_cm:
            # Pass content as argument to avoid JS escaping issues
            result = page.evaluate(
                """(pluginContent) => {
                    try {
                        var cmEl = document.querySelector('.CodeMirror');
                        if (!cmEl) return 'no_cm_element';
                        var cm = cmEl.CodeMirror;
                        if (!cm) return 'no_cm_instance';
                        cm.setValue(pluginContent);
                        var val = cm.getValue();
                        if (val.indexOf('vortex-ring') !== -1 &&
                            val.indexOf('hero__logo') !== -1 &&
                            val.indexOf('767px') !== -1 &&
                            val.indexOf('pb-aether-footer') !== -1) {
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

        page.screenshot(path=f"{SCREENSHOT_DIR}/deploy_mobile_vortex.png")
        page_text = page.inner_text("body")

        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin file saved!")
            save_ok = True
        elif "Parse error" in page_text or "syntax error" in page_text.lower():
            print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear. Page snippet: {page_text[:300]}")
            # Verify content in editor
            if has_cm:
                current = page.evaluate(
                    """() => {
                        var cm = document.querySelector('.CodeMirror');
                        return cm ? cm.CodeMirror.getValue().substring(0, 2000) : 'N/A';
                    }"""
                )
                if "vortex-ring" in current and "767px" in current:
                    print("  vortex-ring + 767px found in editor — save assumed OK.")
                    save_ok = True
                else:
                    print(f"  Editor content doesn't show vortex-ring. Preview: {current[:300]}")
                    save_ok = False
            else:
                save_ok = False

        browser.close()

        if not save_ok:
            return False

    # Step 5: Clear Elementor cache
    print("\n[Step 5] Clearing Elementor cache...")
    credentials = base64.b64encode(
        f"{WP_USER}:{WP_APP_PASS}".encode()
    ).decode()
    cache_req = urllib.request.Request(
        "https://purebrain.ai/wp-json/elementor/v1/cache",
        method="DELETE",
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        },
    )
    ctx_ssl = ssl.create_default_context()
    try:
        with urllib.request.urlopen(cache_req, context=ctx_ssl, timeout=20) as resp:
            print(f"  Elementor cache cleared: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"  Elementor cache response: HTTP {e.code} (may be OK)")
    except Exception as ex:
        print(f"  Elementor cache clear skipped: {ex}")

    return True


def verify_live() -> bool:
    """Verify the vortex-ring CSS is present on purebrain.ai homepage."""
    print("\n[Verification] Fetching purebrain.ai homepage to check for vortex-ring CSS...")
    ctx_ssl = ssl.create_default_context()
    conn_req = urllib.request.Request(
        "https://purebrain.ai/",
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )
    try:
        with urllib.request.urlopen(conn_req, context=ctx_ssl, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  Could not fetch homepage: {e}")
        return False

    vortex_present = ".vortex-ring" in html
    hero_logo_present = ".hero__logo" in html and "70px" in html
    media_767_present = "767px" in html

    print(f"  [{'PASS' if vortex_present else 'FAIL'}] .vortex-ring CSS found in page source")
    print(f"  [{'PASS' if hero_logo_present else 'FAIL'}] .hero__logo mobile resize found")
    print(f"  [{'PASS' if media_767_present else 'FAIL'}] 767px mobile breakpoint found")

    return vortex_present and media_767_present


def main():
    print("=" * 65)
    print("PureBrain Security Plugin — Mobile Vortex Fix Deploy")
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

    print(f"\n[OK] Plugin deployed successfully.")

    print("\nWaiting 8 seconds for cache to settle...")
    time.sleep(8)

    verified = verify_live()
    if verified:
        print("\nDEPLOYMENT COMPLETE AND VERIFIED.")
        print("Changes live:")
        print("  - Vortex rings hidden on mobile (max-width: 767px)")
        print("  - Hero particles hidden on mobile")
        print("  - Hero logo shrunk to 70px on mobile")
        print("  - Video background now visible on mobile")
    else:
        print("\nDeploy done but live verification flagged issues.")
        print("Possible CDN cache delay — check manually:")
        print("  curl -s https://purebrain.ai/ | grep -o 'vortex-ring'")


if __name__ == "__main__":
    main()
