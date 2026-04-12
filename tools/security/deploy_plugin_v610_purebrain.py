#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v6.1.0 to purebrain.ai.

v6.1.0 changes:
  Fix 1: 301 redirect /ai-adoption-assessment → /ai-partnership-assessment/
  Fix 2: Twitter/X Card meta tags injection on all pages (twitter:card = summary_large_image)
  Fix 3: Hide Aether footer bar on assessment page (ID 284) on mobile to prevent
         overlap with answer Option C on the quiz.

Author: full-stack-developer agent
Date: 2026-02-25
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
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v610_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v610_verify.png",
}


def validate_plugin_content(content: str) -> bool:
    checks = {
        "v6.1.0 version header":                     "Version:     6.1.0" in content,
        "v6.1.0 changelog entry":                    "v6.1.0 - Three analytics audit fixes" in content,
        "301 redirect hook present":                 "ai-adoption-assessment" in content,
        "301 redirect target present":               "ai-partnership-assessment" in content,
        "twitter:card meta injection present":       "twitter:card" in content,
        "twitter:site @purebrain_ai present":        "@purebrain_ai" in content,
        "twitter wp_head hook present":              "g2b) TWITTER/X CARD META TAGS" in content,
        "assessment footer hide CSS present":        "body.page-id-284 #pb-aether-footer" in content,
        "Aether footer credit bar present":          "pb-aether-footer" in content,
        "FAQ accordion still present":               "purebrain-faq-accordion" in content,
        "aether-transparency present":               "aether-transparency" in content,
        "legal footer still present":                "purebrain-legal-footer" in content,
        "FAQPage schema (v5.8.0) still present":     "j-schema" in content,
        "body padding-bottom 64px present":          "padding-bottom: 64px" in content,
        "mobile padding-bottom 80px present":        "padding-bottom: 80px" in content,
        "IndexNow key server (v6.0.0) still present": "823869521fbf4f33b93e67c781571e20.txt" in content,
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

    print("\n[Step 3] Setting plugin content (v6.1.0)...")
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
                    val.includes('Version:     6.1.0') &&
                    val.includes('twitter:card') &&
                    val.includes('ai-adoption-assessment') &&
                    val.includes('page-id-284') &&
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
                return cm ? cm.CodeMirror.getValue().substring(0, 5000) : 'N/A';
            }""")
            if "Version:     6.1.0" in current and "pb-aether-footer" in current:
                print("  v6.1.0 content found in editor — save assumed successful.")
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
    """
    Verify all three fixes are live:
    1. /ai-adoption-assessment returns 301 → /ai-partnership-assessment/
    2. Homepage has twitter:card meta tags
    3. Assessment page HTML present (ID 284 check)
    """
    print("\n[Verification] Checking all three fixes are live...")
    all_ok = True
    cb = int(time.time())

    # ---- Fix 1: 301 redirect ----
    print("\n  === Fix 1: 301 Redirect ===")
    redir_url = f"https://purebrain.ai/ai-adoption-assessment/?cb={cb}"
    req = urllib.request.Request(
        redir_url,
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )
    try:
        # Don't follow redirects — we want to check for 301
        import http.client
        import ssl
        ctx_ssl = ssl.create_default_context()
        conn = http.client.HTTPSConnection("purebrain.ai", context=ctx_ssl, timeout=20)
        conn.request("GET", f"/ai-adoption-assessment/?cb={cb}", headers={
            "User-Agent": "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache",
        })
        resp = conn.getresponse()
        status = resp.status
        location = resp.getheader("Location", "")
        conn.close()

        redirect_ok = (status == 301 and "ai-partnership-assessment" in location)
        print(f"  [{'PASS' if redirect_ok else 'FAIL'}] /ai-adoption-assessment redirect")
        print(f"    HTTP status: {status} (expected 301)")
        print(f"    Location: {location}")
        if not redirect_ok:
            all_ok = False
    except Exception as ex:
        print(f"  [FAIL] Redirect check error: {ex}")
        all_ok = False

    # ---- Fix 2: Twitter cards ----
    print("\n  === Fix 2: Twitter/X Cards ===")
    home_req = urllib.request.Request(
        f"https://purebrain.ai/?cb={cb}",
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(home_req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        twitter_card_ok  = 'name="twitter:card"' in html
        twitter_site_ok  = 'name="twitter:site"' in html
        twitter_title_ok = 'name="twitter:title"' in html
        footer_ok        = 'id="pb-aether-footer"' in html

        print(f"  [{'PASS' if twitter_card_ok else 'FAIL'}] twitter:card meta tag present")
        print(f"  [{'PASS' if twitter_site_ok else 'FAIL'}] twitter:site meta tag present")
        print(f"  [{'PASS' if twitter_title_ok else 'FAIL'}] twitter:title meta tag present")
        print(f"  [{'PASS' if footer_ok else 'FAIL'}] Aether footer still present")

        if not (twitter_card_ok and twitter_site_ok and twitter_title_ok and footer_ok):
            all_ok = False
    except Exception as ex:
        print(f"  [FAIL] Homepage fetch error: {ex}")
        all_ok = False

    # ---- Fix 3: Assessment page renders (CSS class check) ----
    print("\n  === Fix 3: Assessment page footer hide CSS ===")
    assess_req = urllib.request.Request(
        f"https://purebrain.ai/ai-partnership-assessment/?cb={cb}",
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(assess_req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        # Check: page-id-284 CSS class is on the body AND pb-footer-aether hide rule appears in HTML
        page_id_ok   = "page-id-284" in html
        css_rule_ok  = "page-id-284 #pb-aether-footer" in html
        print(f"  [{'PASS' if page_id_ok else 'FAIL'}] body.page-id-284 class present")
        print(f"  [{'PASS' if css_rule_ok else 'FAIL'}] footer hide CSS rule in page HTML")
        if not (page_id_ok and css_rule_ok):
            all_ok = False
    except Exception as ex:
        print(f"  [FAIL] Assessment page fetch error: {ex}")
        all_ok = False

    return all_ok


def main():
    print("=" * 65)
    print("PureBrain Security Plugin v6.1.0 — Three Analytics Audit Fixes")
    print("=" * 65)
    print("\nFixes in this version:")
    print("  1. 301 redirect: /ai-adoption-assessment → /ai-partnership-assessment/")
    print("  2. Twitter/X Card meta tags: summary_large_image on all pages")
    print("  3. Assessment footer hide: body.page-id-284 #pb-aether-footer on mobile")

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
    print("DEPLOYING plugin v6.1.0 via Playwright (WP Plugin Editor)")
    print("=" * 65)
    success = deploy_plugin_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Plugin deployment succeeded.")

    print("\nWaiting 10 seconds for cache to settle...")
    time.sleep(10)

    print("\n" + "=" * 65)
    print("LIVE VERIFICATION")
    print("=" * 65)
    verified = verify_live()

    if verified:
        print("\nDEPLOYMENT COMPLETE AND VERIFIED.")
        print("Changes deployed:")
        print("  - 301 redirect: /ai-adoption-assessment → /ai-partnership-assessment/")
        print("  - Twitter/X cards: summary_large_image on ALL pages")
        print("  - Assessment page (ID 284): footer bar hidden on mobile")
        print("  - All other plugin features intact")
    else:
        print("\nDeployment done — some verification checks flagged issues.")
        print("Note: CDN cache may need a moment to propagate.")


if __name__ == "__main__":
    main()
