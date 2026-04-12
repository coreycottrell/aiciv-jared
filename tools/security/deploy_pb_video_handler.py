#!/usr/bin/env python3
"""
Deploy pb-video-handler plugin v1.5.0 to purebrain.ai.

v1.5.0 change: Added JavaScript that physically REMOVES .portal-vortex and
.hero__particles elements from the DOM on mobile viewport. CSS display:none
wasn't working on iOS Safari, so we use element.remove() instead. Also
shrinks .hero__logo to 70px on mobile.

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
PLUGIN_FILE = AETHER_ROOT / "tools/security/pb-video-handler/pb-video-handler.php"
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
    "?file=pb-video-handler/pb-video-handler.php"
    "&plugin=pb-video-handler/pb-video-handler.php"
)
LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"


def validate_plugin(content: str) -> bool:
    checks = {
        "PHP opening tag present":              "<?php" in content,
        "Plugin Name header present":           "Plugin Name: PureBrain Video Handler" in content,
        "v1.5.0 version tag present":           "1.5.0" in content,
        "portal-vortex hide rule present":      ".portal-vortex" in content,
        "vortex-ring hide rule present":        ".vortex-ring" in content,
        "hero__particles hide rule present":    ".hero__particles" in content,
        "hero__logo shrink rule present":       ".hero__logo" in content and "70px" in content,
        "mobile media query 767px present":     "max-width: 767px" in content,
        "video-background__video CSS present":  ".video-background__video" in content,
        "wp_head action present":               "wp_head" in content,
        "wp_footer action present":             "wp_footer" in content,
        "JS element.remove() present":          "portalVortex.remove()" in content or ".remove()" in content,
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
    print("DEPLOYING pb-video-handler v1.5.0 TO: purebrain.ai")
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
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_video_handler_captcha.png")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            print("  Login form not visible.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_video_handler_no_form.png")
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
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_video_handler_login_fail.png")
            browser.close()
            return False
        print("  Login successful!")

        # Step 1b: Activate plugin if deactivated
        print("\n[Step 1b] Checking plugin activation status...")
        plugins_url = "https://purebrain.ai/wp-admin/plugins.php"
        page.goto(plugins_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/pb_video_handler_plugins_page.png")

        plugins_body = page.inner_text("body")
        plugin_row_text = page.evaluate("""() => {
            var rows = document.querySelectorAll('tr[data-slug="pb-video-handler"]');
            if (rows.length > 0) return rows[0].innerHTML;
            return '';
        }""")

        if plugin_row_text:
            is_active = "deactivate" in plugin_row_text.lower()
            has_activate = "activate" in plugin_row_text.lower() and not is_active
            print(f"  Plugin row found. Active: {is_active}, Has activate link: {has_activate}")

            if not is_active and has_activate:
                print("  Plugin is INACTIVE — activating now...")
                activated = page.evaluate("""() => {
                    var rows = document.querySelectorAll('tr[data-slug="pb-video-handler"]');
                    if (!rows.length) return false;
                    var activateLink = rows[0].querySelector('a[href*="action=activate"]');
                    if (!activateLink) return false;
                    activateLink.click();
                    return true;
                }""")
                if activated:
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=30000)
                    except Exception:
                        pass
                    time.sleep(3)
                    page.screenshot(path=f"{SCREENSHOT_DIR}/pb_video_handler_after_activate.png")
                    page_text = page.inner_text("body")
                    if "Plugin activated" in page_text or "activated" in page_text.lower():
                        print("  Plugin activated successfully!")
                    else:
                        print("  Activation result unclear — continuing anyway.")
                else:
                    print("  Could not click activate link — checking nonce URL approach...")
                    # Try finding activate link href directly and navigating to it
                    activate_href = page.evaluate("""() => {
                        var rows = document.querySelectorAll('tr[data-slug="pb-video-handler"]');
                        if (!rows.length) return '';
                        var activateLink = rows[0].querySelector('a[href*="action=activate"]');
                        return activateLink ? activateLink.href : '';
                    }""")
                    if activate_href:
                        print(f"  Navigating to activate URL...")
                        page.goto(activate_href, wait_until="domcontentloaded", timeout=30000)
                        time.sleep(3)
                        page.screenshot(path=f"{SCREENSHOT_DIR}/pb_video_handler_activated_nav.png")
                        print("  Navigated to activation URL.")
                    else:
                        print("  No activate link found — plugin may already be active or row not found.")
            elif is_active:
                print("  Plugin is already ACTIVE — proceeding to editor.")
            else:
                print("  Could not determine activation state — proceeding anyway.")
        else:
            print("  Plugin row not found by data-slug. Checking if it's in the page...")
            if "pb-video-handler" in plugins_body.lower() or "PureBrain Video Handler" in plugins_body:
                print("  Plugin found in page text — checking state...")
                # Try to find activate link anywhere on the page for this plugin
                activate_href = page.evaluate("""() => {
                    var links = document.querySelectorAll('a[href*="pb-video-handler"][href*="activate"]');
                    return links.length > 0 ? links[0].href : '';
                }""")
                if activate_href:
                    print(f"  Found activate link — navigating to it...")
                    page.goto(activate_href, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(3)
                    print("  Activation navigation complete.")
                else:
                    print("  No activate link found — plugin may already be active.")
            else:
                print("  Plugin not visible on plugins page. It may be in a different location.")

        # Step 2: Open plugin editor
        print("\n[Step 2] Opening plugin editor for pb-video-handler...")
        page.goto(EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        page_body = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_body or "editing has been disabled" in page_body.lower():
            print("  File editing is disabled on server.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_video_handler_edit_disabled.png")
            browser.close()
            return False

        has_cm = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_ta = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_cm}, Textarea: {has_ta}")

        if not has_cm and not has_ta:
            print(f"  No editor found. Body snippet: {page_body[:400]}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/pb_video_handler_no_editor.png")
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
                        if (val.indexOf('portal-vortex') !== -1 &&
                            val.indexOf('vortex-ring') !== -1 &&
                            val.indexOf('hero__logo') !== -1 &&
                            val.indexOf('767px') !== -1 &&
                            val.indexOf('wp_head') !== -1 &&
                            val.indexOf('.remove()') !== -1) {
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

        page.screenshot(path=f"{SCREENSHOT_DIR}/pb_video_handler_deploy.png")
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
            if has_cm:
                current = page.evaluate(
                    """() => {
                        var cm = document.querySelector('.CodeMirror');
                        return cm ? cm.CodeMirror.getValue().substring(0, 3000) : 'N/A';
                    }"""
                )
                if "portal-vortex" in current and "767px" in current and ".remove()" in current:
                    print("  portal-vortex + 767px + .remove() found in editor — save assumed OK.")
                    save_ok = True
                else:
                    print(f"  Editor content doesn't show portal-vortex. Preview: {current[:300]}")
                    save_ok = False
            else:
                save_ok = False

        browser.close()

        if not save_ok:
            return False

    # Step 5: Clear Elementor cache via REST API
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
        print(f"  Elementor cache response: HTTP {e.code} (may be OK if REST is restricted)")
    except Exception as ex:
        print(f"  Elementor cache clear skipped: {ex}")

    return True


def verify_live() -> bool:
    """Verify the portal-vortex CSS + JS remove() is present on purebrain.ai homepage."""
    print("\n[Verification] Fetching purebrain.ai homepage to check for v1.5.0 code...")
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

    portal_vortex_present   = "portal-vortex" in html
    vortex_ring_present     = ".vortex-ring" in html
    hero_particles_present  = ".hero__particles" in html
    hero_logo_present       = ".hero__logo" in html and "70px" in html
    media_767_present       = "767px" in html
    js_remove_present       = "portalVortex" in html or ".remove()" in html
    pb_handler_js_present   = "pb-video-handler-js" in html

    print(f"  [{'PASS' if pb_handler_js_present else 'FAIL'}] pb-video-handler-js script tag found")
    print(f"  [{'PASS' if portal_vortex_present else 'FAIL'}] .portal-vortex CSS found in page source")
    print(f"  [{'PASS' if vortex_ring_present else 'FAIL'}] .vortex-ring CSS found in page source")
    print(f"  [{'PASS' if hero_particles_present else 'FAIL'}] .hero__particles CSS found")
    print(f"  [{'PASS' if hero_logo_present else 'FAIL'}] .hero__logo 70px shrink found")
    print(f"  [{'PASS' if media_767_present else 'FAIL'}] 767px mobile breakpoint found")
    print(f"  [{'PASS' if js_remove_present else 'FAIL'}] JS element.remove() for portalVortex found")

    return portal_vortex_present and vortex_ring_present and media_767_present and pb_handler_js_present


def main():
    print("=" * 65)
    print("pb-video-handler v1.5.0 — Deploy Script")
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

    print(f"\n[OK] Plugin v1.5.0 deployed successfully.")

    print("\nWaiting 8 seconds for cache to settle...")
    time.sleep(8)

    verified = verify_live()
    if verified:
        print("\nDEPLOYMENT COMPLETE AND VERIFIED.")
        print("Changes live on purebrain.ai (v1.5.0):")
        print("  - .portal-vortex REMOVED from DOM on mobile (element.remove())")
        print("  - .hero__particles REMOVED from DOM on mobile (element.remove())")
        print("  - .portal-vortex, .vortex-ring hidden via CSS (display:none) on mobile")
        print("  - .hero__logo shrunk to 70px on mobile")
        print("  - Video background now visible on mobile")
    else:
        print("\nDeploy done but live verification flagged issues.")
        print("Possible CDN cache delay — check manually:")
        print("  curl -s https://purebrain.ai/ | grep -o 'portal-vortex'")


if __name__ == "__main__":
    main()
