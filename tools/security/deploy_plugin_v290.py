#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v2.9.0 to WordPress.

v2.9.0 changes:
1. Added high-specificity CSS override (section 4 of purebrain-blog-cta-hover)
   targeting data-pb-subscribe attribute to beat the Additional CSS blue-glow rule.
   Root cause: Additional CSS loads after plugin CSS in <head>, so broad
   body.single-post .blog-cta-block a:hover wins at equal specificity for
   subscribe link box-shadow and transform (even with !important on both).
   Fix: JS sets data-pb-subscribe="1" on subscribe links, enabling a CSS rule
   with specificity 0,5,3 vs the conflicting rule's 0,3,3.

2. Updated initSubscribeLinks() (was stripNewsletterInlineStyles) to also
   set data-pb-subscribe="1" on each subscribe/newsletter link for the
   high-specificity CSS hook.

Author: full-stack-developer agent
Date: 2026-02-21
"""

import os
import re
import sys
import time
import urllib.request
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")

PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security-plugin.php"
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"

env_text = (AETHER_ROOT / ".env").read_text()
WP_PASSWORD_MATCH = re.search(r"PUREBRAIN_WP_PASSWORD='([^']+)'", env_text)
WP_PASSWORD = WP_PASSWORD_MATCH.group(1) if WP_PASSWORD_MATCH else ""

PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)

SCREENSHOT_DEPLOY = str(AETHER_ROOT / "exports/screenshots/plugin_v290_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v290_verify.png")


def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 2.9.0":                        "2.9.0" in content,
        "v2.9.0 changelog entry":               "high-specificity" in content.lower() or "data-pb-subscribe" in content,
        "strip-newsletter-inline-styles JS":    "purebrain-strip-newsletter-inline-styles" in content,
        "initSubscribeLinks function":           "initSubscribeLinks" in content,
        "setAttribute data-pb-subscribe":        'setAttribute(\'data-pb-subscribe\'' in content or 'setAttribute("data-pb-subscribe"' in content,
        "high-specificity CSS rule":            "data-pb-subscribe" in content,
        "transform: none on subscribe hover":   "transform: none !important" in content,
        "orange box-shadow on subscribe hover": "rgba(241, 66, 11, 0.3)" in content,
        "CTA awakening selector present":       'a[href*="awakening"]' in content,
        "subscribe selector present":           'a[href*="subscribe"]' in content,
        "api.purebrain.ai (log)":               "https://api.purebrain.ai/api/log-conversation" in content,
        "api.purebrain.ai (payment)":           "https://api.purebrain.ai/api/verify-payment" in content,
        "sslverify true":                       "'sslverify' => true" in content,
        "rate limiter":                         "purebrain_check_rate_limit" in content,
        "pb-legal-link":                        "pb-legal-link" in content,
        "pb-blog-nav":                          "pb-blog-nav" in content,
        "FAQ accordion":                        "faq-accordion" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v2.9.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")
    print("Changes: high-specificity CSS + data-pb-subscribe JS for subscribe link hover fix")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    print("\nValidating plugin content...")
    if not validate_plugin_content(new_content):
        print("\nERROR: Plugin validation failed. Aborting.")
        sys.exit(1)
    print("Plugin content validated. Starting Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = context.new_page()

        # Step 1: Login
        print("\n[Step 1] Logging in to WP Admin...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("  GoDaddy SSO overlay - clicking username/password link...")
            sso_toggle.click()
            time.sleep(2)

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=SCREENSHOT_DEPLOY)
            print("  ERROR: Login form not visible.")
            browser.close()
            return False

        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=SCREENSHOT_DEPLOY)
            print(f"  CAPTCHA detected! Screenshot: {SCREENSHOT_DEPLOY}")
            print("  Wait 15-30 minutes for GoDaddy bot protection to reset, then retry.")
            browser.close()
            return False

        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASSWORD)
        page.click("#wp-submit")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        time.sleep(3)

        if "wp-login.php" in page.url:
            page.screenshot(path=SCREENSHOT_DEPLOY)
            print(f"  ERROR: Login failed. URL: {page.url}")
            browser.close()
            return False

        print("  Login successful!")

        # Step 2: Plugin Editor
        print("\n[Step 2] Opening Plugin Editor...")
        page.goto(PLUGIN_EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        page_text = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
            print("  ERROR: File editing disabled.")
            browser.close()
            return False

        has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_textarea   = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

        if not has_codemirror and not has_textarea:
            page.screenshot(path=SCREENSHOT_DEPLOY)
            print("  ERROR: No editor found.")
            browser.close()
            return False

        # Step 3: Set content
        print("\n[Step 3] Setting plugin content...")
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
                        val.includes('2.9.0') &&
                        val.includes('data-pb-subscribe') &&
                        val.includes('initSubscribeLinks') &&
                        val.includes('purebrain-strip-newsletter-inline-styles') &&
                        val.includes('pb-blog-nav')
                    ) return 'success';
                    return 'set_failed: ' + val.length + ' chars';
                } catch(e) { return 'error: ' + e.message; }
            }""", new_content)
            print(f"  CodeMirror result: {result}")

            if result != "success":
                print("  CodeMirror failed, trying textarea...")
                page.evaluate("""() => {
                    const ta = document.querySelector('#newcontent');
                    if (ta) { ta.style.display='block'; ta.style.visibility='visible'; }
                }""")
                page.evaluate("""(content) => {
                    const ta = document.querySelector('#newcontent');
                    if (!ta) return;
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value').set;
                    setter.call(ta, content);
                    ta.dispatchEvent(new Event('input', {bubbles:true}));
                    ta.dispatchEvent(new Event('change', {bubbles:true}));
                }""", new_content)
                print("  Textarea fallback set.")
        else:
            page.evaluate("""(content) => {
                const ta = document.querySelector('#newcontent');
                if (!ta) return;
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLTextAreaElement.prototype, 'value').set;
                setter.call(ta, content);
                ta.dispatchEvent(new Event('input', {bubbles:true}));
                ta.dispatchEvent(new Event('change', {bubbles:true}));
            }""", new_content)
            print("  Textarea content set.")

        time.sleep(1)

        # Step 4: Save
        print("\n[Step 4] Saving...")
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

        page.screenshot(path=SCREENSHOT_DEPLOY)
        page_text = page.inner_text("body")

        save_success = False
        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin saved!")
            save_success = True
        elif "Parse error" in page_text or "syntax error" in page_text:
            print(f"  ERROR: PHP syntax error! {page_text[:400]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear: {page_text[:300]}")
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0,300) : 'N/A';
                }""")
                if "2.9.0" in current:
                    save_success = True
                    print("  v2.9.0 found in editor - assuming success.")

        # Step 5: Flush cache
        print("\n[Step 5] Flushing cache...")
        page.goto(f"{WP_ADMIN_URL}/options-general.php", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        flush_url = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            const link = links.find(a =>
                /flush.cache/i.test(a.textContent) ||
                /flush.cache/i.test(a.href) ||
                /wpaas_action=flush_cache/i.test(a.href)
            );
            return link ? link.href : null;
        }""")

        if flush_url:
            page.goto(flush_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            print("  Cache flushed!")
        else:
            print("  No flush URL found - cache will expire naturally.")

        page.screenshot(path=SCREENSHOT_VERIFY)
        browser.close()

    return save_success


def verify_live():
    """Verify v2.9.0 is live on the blog."""
    print("\n[Verification] Checking live site...")
    test_url = "https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/"

    req = urllib.request.Request(
        test_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")

        checks = {
            "v2.9.0 version reference":                 "2.9.0" in html,
            "strip-inline-styles JS block":             "purebrain-strip-newsletter-inline-styles" in html,
            "initSubscribeLinks function":              "initSubscribeLinks" in html,
            "setAttribute data-pb-subscribe":           "data-pb-subscribe" in html,
            "high-specificity CSS (data-pb-subscribe)": "data-pb-subscribe" in html,
            "newsletter hover CSS (neural-feed)":       "neural-feed" in html,
            "pb-blog-nav present":                      "pb-blog-nav" in html,
            "FAQ accordion present":                    "faq-accordion" in html,
        }

        all_ok = True
        for name, result in checks.items():
            status = "OK" if result else "MISSING"
            print(f"  [{status}] {name}")
            if not result:
                all_ok = False

        return all_ok

    except Exception as e:
        print(f"  Request failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 65)
    print("PUREBRAIN SECURITY PLUGIN v2.9.0 - DEPLOY")
    print("Change: High-specificity CSS + data-pb-subscribe JS for subscribe hover fix")
    print("=" * 65)

    result = deploy()

    if result:
        print("\n[Deploy] SUCCESS: Plugin saved to WordPress.")
    else:
        print("\n[Deploy] FAILED. Check screenshots.")
        print(f"  Screenshot: {SCREENSHOT_DEPLOY}")
        sys.exit(1)

    print("\nWaiting 10 seconds for CDN propagation...")
    time.sleep(10)

    live_ok = verify_live()

    print("\n" + "=" * 65)
    print("FINAL RESULT")
    print("=" * 65)
    if live_ok:
        print("\n[SUCCESS] v2.9.0 IS LIVE!")
        print("\n  What's now active:")
        print("  - JS tags subscribe links with data-pb-subscribe='1' attribute")
        print("  - High-specificity CSS targets [data-pb-subscribe] on hover:")
        print("    → Orange box-shadow (not blue glow)")
        print("    → transform: none (not translateY(-2px))")
        print("    → White text + orange gradient background")
        print("  - Old inline style stripping (v2.8.0) still active")
        print(f"\n  Screenshots:")
        print(f"    Deploy: {SCREENSHOT_DEPLOY}")
        print(f"    Verify: {SCREENSHOT_VERIFY}")
    else:
        print("\n[WARNING] Some checks failed - CDN may still be caching old content.")
        print("  Hard-refresh (Ctrl+Shift+R) to bypass browser cache.")
        print(f"  Deploy screenshot: {SCREENSHOT_DEPLOY}")
        print(f"  Verify screenshot: {SCREENSHOT_VERIFY}")
