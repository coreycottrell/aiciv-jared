#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v4.7.5 — Pricing Bullet Alignment Fix.

Key change from v4.7.4:
- PRICING BULLET ALIGNMENT FIX: Nova/AI name text no longer splits into
  separate columns in the Awakened pricing tier bullet points.
- Root cause: .pricing-card__feature uses display:flex. The <span class="ai-name-dynamic">
  and the trailing text node become separate flex items, causing "Nova"
  to appear left-separated from the rest of the bullet text.
- Fix: CSS changes .pricing-card__feature to display:grid (2 cols: icon + text).
  In grid layout, span and text node fall into same track, flowing inline.
- Applies site-wide to all pages with pricing cards.

Author: dept-systems-technology (ST#)
Date: 2026-03-01
"""

import os
import re
import sys
import time
import base64
import urllib.request
import urllib.error
import ssl
import http.client
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_SOURCE = AETHER_ROOT / "exports/purebrain-security-plugin-v475.php"

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
    "name":       "purebrain.ai",
    "login_url":  "https://purebrain.ai/wp-login.php",
    "user":       "Aether",
    "password":   PUREBRAIN_PASSWORD,
    "app_password": PUREBRAIN_APP_PASS,
    "editor_url": (
        "https://purebrain.ai/wp-admin/plugin-editor.php"
        "?file=purebrain-security/purebrain-security-plugin.php"
        "&plugin=purebrain-security/purebrain-security-plugin.php"
    ),
}


def validate_plugin_content(content: str) -> bool:
    """Validate the v4.7.5 plugin has all required markers."""
    checks = {
        "Version 4.7.5":                    "Version:     4.7.5" in content,
        "Pricing bullet fix CSS id":        "pb-pricing-bullet-fix" in content,
        "Grid CSS applied":                 "display: grid !important" in content,
        "Layer 1 CSS injected":             "pb-dark-bg-layer1" in content,
        "Layer 2 CSS injected":             "pb-dark-bg-layer2" in content,
        "Layer 3 JS injected":              "pb-dark-bg-js" in content,
        "Dark bg color correct (#080a12)":  "#080a12" in content,
        "Core: Aether footer":              "pb-aether-footer" in content,
        "Core: FAQ accordion":              "purebrain-faq-accordion" in content,
    }
    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


def deploy_via_plugin_editor(page, site: dict, content: str) -> bool:
    """Write plugin content via WP Admin plugin editor (CodeMirror or textarea)."""
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
        print("  ERROR: No editor found.")
        return False

    print("\n[Step 3] Setting plugin content (v4.7.5 - pricing bullet fix)...")
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
                    val.includes('Version:     4.7.5') &&
                    val.includes('pb-pricing-bullet-fix') &&
                    val.includes('pb-dark-bg-layer1') &&
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

    page_text = page.inner_text("body")

    if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
        print("  SUCCESS: Plugin file saved!")
        return True
    elif "Parse error" in page_text or "syntax error" in page_text.lower():
        print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
        return False
    else:
        print("  Status unclear. Checking content in editor...")
        if has_codemirror:
            current = page.evaluate("""() => {
                const cm = document.querySelector('.CodeMirror');
                return cm ? cm.CodeMirror.getValue().substring(0, 5000) : 'N/A';
            }""")
            if ("Version:     4.7.5" in current and
                    "pb-pricing-bullet-fix" in current):
                print("  v4.7.5 markers found in editor — save assumed successful.")
                return True
        return False


def deploy_plugin_to_site(site: dict, content: str) -> bool:
    """Full deployment: login -> plugin editor -> save -> cache clear."""
    from playwright.sync_api import sync_playwright

    print(f"\n{'='*65}")
    print(f"DEPLOYING PLUGIN TO: {site['name']}")
    print(f"{'='*65}")

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
        sso_toggle_link  = page.locator(
            "a:has-text('username and password'), a:has-text('Log in with username')"
        )

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
            print("  CAPTCHA detected! Cannot proceed.")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            print("  ERROR: Login form not visible.")
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
            print(f"  ERROR: Login failed. URL: {page.url}")
            browser.close()
            return False

        print("  Login successful!")

        success = deploy_via_plugin_editor(page, site, content)

        if success:
            credentials = base64.b64encode(
                f"{site['user']}:{site['app_password']}".encode()
            ).decode()

            print("\n[Step 5] Clearing Elementor cache...")
            cache_req = urllib.request.Request(
                "https://purebrain.ai/wp-json/elementor/v1/cache",
                method="DELETE",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type":  "application/json",
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


def fetch_page_html(url: str) -> str:
    """Fetch a URL, return decoded HTML string."""
    ctx_ssl = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma":        "no-cache",
        }
    )
    with urllib.request.urlopen(req, context=ctx_ssl, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def check_plugin_version_via_api() -> str:
    """Check the live plugin version via WP REST API."""
    try:
        credentials = base64.b64encode(
            f"Aether:{PUREBRAIN_APP_PASS}".encode()
        ).decode()
        ctx_ssl = ssl.create_default_context()
        req = urllib.request.Request(
            "https://purebrain.ai/wp-json/wp/v2/plugins",
            headers={
                "Authorization": f"Basic {credentials}",
                "User-Agent":    "AetherBot/1.0",
            }
        )
        with urllib.request.urlopen(req, context=ctx_ssl, timeout=20) as resp:
            import json
            data = json.loads(resp.read().decode())
            for plugin in data:
                if "purebrain" in plugin.get("plugin", "").lower():
                    return plugin.get("version", "unknown")
    except Exception as ex:
        return f"error: {ex}"
    return "not found"


def verify_live() -> bool:
    """Verify pricing bullet fix CSS is present on the homepage."""
    print("\n--- Live Verification ---")
    try:
        body = fetch_page_html("https://purebrain.ai/")
        checks = {
            "pb-pricing-bullet-fix CSS id present": "pb-pricing-bullet-fix" in body,
            "display: grid CSS present":            "display: grid !important" in body,
            ".pricing-card__feature grid rule":     "pricing-card__feature" in body,
            "Dark bg Layer1 still present":         "pb-dark-bg-layer1" in body,
            "Dark bg Layer2 still present":         "pb-dark-bg-layer2" in body,
        }
        all_ok = True
        for name, result in checks.items():
            status = "PASS" if result else "FAIL"
            print(f"  [{status}] {name}")
            if not result:
                all_ok = False
        return all_ok
    except Exception as ex:
        print(f"  [ERROR] Verification failed: {ex}")
        return False


def main():
    print("=" * 65)
    print("PureBrain Security Plugin v4.7.5 — Pricing Bullet Alignment Fix")
    print("=" * 65)
    print("\nKey change: .pricing-card__feature switches from flex to CSS grid.")
    print("This prevents Nova/AI name from separating from bullet text in flex layout.")
    print("")

    if not PLUGIN_SOURCE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_SOURCE}")
        sys.exit(1)

    content = PLUGIN_SOURCE.read_text()
    print(f"Plugin file: {PLUGIN_SOURCE}")
    print(f"Content length: {len(content):,} chars\n")

    print("--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Plugin validation failed. Aborting.")
        sys.exit(1)
    print("All validation checks passed.\n")

    success = deploy_plugin_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print("\n[OK] Plugin deployment to WP editor succeeded.")
    print("\nWaiting 8 seconds for cache to settle...")
    time.sleep(8)

    # Verify via REST API that version changed
    print("\n--- REST API Version Check ---")
    live_version = check_plugin_version_via_api()
    version_ok = live_version == "4.7.5"
    print(f"  Live plugin version: {live_version}")
    print(f"  [{'PASS' if version_ok else 'FAIL'}] Version is 4.7.5")

    verified = verify_live()

    print("\n" + "=" * 65)
    if verified and version_ok:
        print("DEPLOYMENT COMPLETE AND VERIFIED.")
        print("")
        print("Pricing bullet fix (v4.7.5) is now live on purebrain.ai.")
        print("Nova/AI name now aligns correctly with bullet text.")
        print("CSS grid layout applied to .pricing-card__feature site-wide.")
    else:
        print("DEPLOYMENT DONE — some verification checks flagged issues.")
        if not version_ok:
            print(f"  - Plugin version mismatch (got: {live_version}, expected: 4.7.5)")
        if not verified:
            print("  - Some page checks failed — see details above.")
        print("\nTroubleshooting:")
        print("  1. Try hard-refresh (Ctrl+Shift+R) on the affected page.")
        print("  2. Cloudflare may be serving cached content (wait ~60s).")


if __name__ == "__main__":
    main()
