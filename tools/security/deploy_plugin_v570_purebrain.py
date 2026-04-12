#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v5.7.0 to purebrain.ai.

v5.7.0 changes:
  Removed "See Why PureBrain Is Different" homepage banner (was added in v4.6.0).
  This fixed bar was injected at wp_footer priority 99 on the homepage only.
  It was causing mobile overlap with the Aether footer credit bar.
  Redundant since Mission section now serves this purpose.
  Also removes the duplicate body padding-bottom:76px that conflicted with
  the footer bar's own 64px/80px(mobile) padding.

Author: full-stack-developer agent
Date: 2026-02-24
"""

import os
import re
import sys
import time
import base64
import urllib.request
import urllib.error
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"
SCREENSHOT_DIR = str(AETHER_ROOT / "exports/screenshots")

# --- Credentials -----------------------------------------------------------
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


PUREBRAIN_PASSWORD = _env("PUREBRAIN_WP_PASSWORD")
PUREBRAIN_APP_PASS = _env("PUREBRAIN_WP_APP_PASSWORD")

SITE = {
    "name":          "purebrain.ai",
    "admin_url":     "https://purebrain.ai/wp-admin",
    "login_url":     "https://purebrain.ai/wp-login.php",
    "user":          "Aether",
    "password":      PUREBRAIN_PASSWORD,
    "app_password":  PUREBRAIN_APP_PASS,
    "editor_url": (
        "https://purebrain.ai/wp-admin/plugin-editor.php"
        "?file=purebrain-security/purebrain-security-plugin.php"
        "&plugin=purebrain-security/purebrain-security-plugin.php"
    ),
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v570_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v570_verify.png",
}


def validate_plugin_content(content: str) -> bool:
    checks = {
        "v5.7.0 version header":                    "Version:     5.7.0" in content,
        "v5.7.0 changelog entry":                   "v5.7.0 - Removed" in content,
        "pb-why-purebrain-bar ABSENT (removed)":    "pb-why-purebrain-bar" not in content,
        "aether-footer-credit still present":       "pb-aether-footer" in content,
        "Aether footer (v4.5.0) still present":     "pb-footer-credit" in content or "pb-aether-footer" in content,
        "aether-transparency present":              "aether-transparency" in content,
        "magic cursor override present":            "pb-magic-cursor-body-override" in content,
        "FAQ accordion present":                    "purebrain-faq-accordion" in content,
        "IndexNow key present":                     "823869521fbf4f33b93e67c781571e20" in content,
        "pb-inline-cta-template-lock present":      "pb-inline-cta-template-lock" in content,
        "footer logo brand fix present":            "purebrain-footer-logo-brand" in content,
        "mobile footer sep-before-mission present": "pb-footer-sep-before-mission" in content,
        "Mission & Values pill still present":      "pb-footer-mission" in content,
        "body padding-bottom 80px on mobile":       "padding-bottom: 80px !important" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


def deploy_via_plugin_editor(page, site: dict, content: str) -> bool:
    print(f"\n[Step 2] Opening Plugin Editor...")
    page.goto(site["editor_url"], wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)

    page_text = page.inner_text("body")
    if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
        print("  ERROR: File editing is disabled.")
        return False

    has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
    has_textarea   = page.evaluate("() => !!document.querySelector('#newcontent')")
    print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

    if not has_codemirror and not has_textarea:
        page.screenshot(path=site["screenshot_deploy"])
        print(f"  ERROR: No editor found.")
        return False

    print("\n[Step 3] Setting plugin content (v5.7.0)...")
    set_ok = False

    if has_codemirror:
        result = page.evaluate("""(content) => {
            try {
                const cmEl = document.querySelector('.CodeMirror');
                if (!cmEl) return 'no_cm_element';
                const cm = cmEl.CodeMirror;
                if (!cm) return 'no_cm_instance';
                cm.setValue(content);
                const val = cm.getValue();
                if (
                    val.includes('Version:     5.7.0') &&
                    !val.includes('pb-why-purebrain-bar') &&
                    val.includes('pb-aether-footer')
                ) return 'success';
                return 'set_failed: len=' + val.length;
            } catch(e) { return 'error: ' + e.message; }
        }""", content)
        print(f"  CodeMirror result: {result}")
        set_ok = (result == "success")

    if not set_ok:
        print("  Using textarea fallback...")
        page.evaluate("""() => {
            const ta = document.querySelector('#newcontent');
            if (ta) {
                ta.style.display = 'block';
                ta.style.visibility = 'visible';
            }
        }""")
        page.evaluate("""(content) => {
            const ta = document.querySelector('#newcontent');
            if (!ta) return;
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(ta, content);
            ta.dispatchEvent(new Event('input', {bubbles: true}));
            ta.dispatchEvent(new Event('change', {bubbles: true}));
        }""", content)
        print("  Textarea content set.")

    time.sleep(1)

    print("\n[Step 4] Saving plugin...")
    page.evaluate("""() => {
        const btn = document.querySelector('#submit') ||
                    document.querySelector('input[type="submit"]');
        if (btn) btn.click();
    }""")

    try:
        page.wait_for_load_state("domcontentloaded", timeout=45000)
    except Exception:
        pass
    time.sleep(4)

    page.screenshot(path=site["screenshot_deploy"])
    page_text = page.inner_text("body")

    if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
        print("  SUCCESS: Plugin file saved!")
        return True
    elif "Parse error" in page_text or "syntax error" in page_text.lower():
        print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
        return False
    else:
        print(f"  Status unclear. Checking content in editor...")
        if has_codemirror:
            current = page.evaluate("""() => {
                const cm = document.querySelector('.CodeMirror');
                return cm ? cm.CodeMirror.getValue().substring(0, 3000) : 'N/A';
            }""")
            if "Version:     5.7.0" in current and "pb-why-purebrain-bar" not in current:
                print("  v5.7.0 content found in editor (banner absent) — save assumed successful.")
                return True
        return False


def deploy_plugin_to_site(site: dict, content: str) -> bool:
    from playwright.sync_api import sync_playwright

    print(f"\n{'='*65}")
    print(f"DEPLOYING PLUGIN TO: {site['name']}")
    print(f"{'='*65}")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = ctx.new_page()

        print(f"\n[Step 1] Logging in to {site['name']}...")
        page.goto(site["login_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        sso_toggle_class = page.locator(".wpaas-sso-login-toggle")
        sso_toggle_link  = page.locator("a:has-text('username and password'), a:has-text('Log in with username')")

        if sso_toggle_class.count() > 0 and sso_toggle_class.is_visible():
            print("  GoDaddy SSO overlay (class) — clicking...")
            sso_toggle_class.click()
            time.sleep(3)
        elif sso_toggle_link.count() > 0:
            print("  GoDaddy SSO overlay (link text) — clicking...")
            sso_toggle_link.first.click()
            time.sleep(3)
        else:
            print("  No SSO overlay detected.")
            time.sleep(1)

        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  CAPTCHA detected! Screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: Login form not visible.")
            browser.close()
            return False

        page.fill("#user_login", site["user"])
        page.fill("#user_pass", site["password"])
        page.click("#wp-submit")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        time.sleep(3)

        if "wp-login.php" in page.url:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: Login failed. URL: {page.url}")
            browser.close()
            return False

        print("  Login successful!")

        success = deploy_via_plugin_editor(page, site, content)

        if success:
            credentials = base64.b64encode(
                f"{site['user']}:{site['app_password']}".encode()
            ).decode()

            # Clear Elementor cache
            print("\n[Step 5] Clearing Elementor cache...")
            cache_req = urllib.request.Request(
                "https://purebrain.ai/wp-json/elementor/v1/cache",
                method="DELETE",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(cache_req, timeout=20) as resp:
                    print(f"  Elementor cache cleared: HTTP {resp.status}")
            except urllib.error.HTTPError as e:
                print(f"  Elementor cache response: HTTP {e.code}")
            except Exception as ex:
                print(f"  Elementor cache clear skipped: {ex}")

        browser.close()

    return success


def verify_live() -> bool:
    print("\n[Verification] Checking homepage for ABSENCE of pb-why-purebrain-bar...")

    url = f"https://purebrain.ai/?cb={int(time.time())}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma":        "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            print(f"  Fetched homepage: HTTP 200 ({len(html)} chars)")
    except Exception as ex:
        print(f"  fetch error: {ex}")
        return False

    checks = {
        "page loads (non-empty)":                   bool(html),
        "pb-why-purebrain-bar ABSENT (banner gone)": "pb-why-purebrain-bar" not in html,
        "pb-aether-footer still present":            "pb-aether-footer" in html,
        "pb-footer-mission (M&V pill) still present": "pb-footer-mission" in html,
        "v5.7.0 marker NOT required in HTML":       True,  # Version not always in page HTML
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False

    # Extra: confirm the banner string is truly gone
    if "pb-why-purebrain-bar" in html:
        print("\n  *** WARNING: pb-why-purebrain-bar STILL found in homepage HTML! ***")
        # Show the surrounding context
        idx = html.find("pb-why-purebrain-bar")
        snippet = html[max(0, idx-100):idx+200]
        print(f"  Context: ...{snippet}...")
        all_ok = False
    else:
        print("\n  CONFIRMED: 'pb-why-purebrain-bar' does NOT appear in homepage HTML.")

    return all_ok


def main():
    print("=" * 65)
    print("PureBrain Security Plugin v5.7.0 — Remove homepage banner")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Content length: {len(content)} chars\n")

    print("--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Plugin validation failed. Aborting.")
        sys.exit(1)
    print("All validation checks passed.\n")

    print("\n" + "=" * 65)
    print("DEPLOYING plugin v5.7.0 via Playwright (WP Plugin Editor)")
    print("=" * 65)
    success = deploy_plugin_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Plugin deployment succeeded.")

    print("\nWaiting 8 seconds for cache to settle...")
    time.sleep(8)

    print("\n" + "=" * 65)
    print("LIVE VERIFICATION")
    print("=" * 65)
    verified = verify_live()

    if verified:
        print("\nDEPLOYMENT COMPLETE AND VERIFIED.")
        print("Change deployed:")
        print("  - 'See Why PureBrain Is Different' homepage banner REMOVED")
        print("  - pb-why-purebrain-bar no longer injected at wp_footer priority 99")
        print("  - No more mobile overlap with Aether footer credit bar")
        print("  - Duplicate body padding-bottom:76px also removed")
        print("  - All other plugin features intact (footer, FAQ, transparency, etc.)")
    else:
        print("\nDeployment done — some verification checks flagged issues.")
        print("Note: CDN cache may need a moment. Hard-refresh or add ?cb=timestamp to confirm.")


if __name__ == "__main__":
    main()
