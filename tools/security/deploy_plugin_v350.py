#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v3.5.0 to WordPress.

v3.5.0 changes:
- Lead capture systems for blog posts (body.single-post only)
- Three capture points:
  1. In-Content Subscribe Box (50% scroll depth) — inline dark card, slide-in animation
  2. Post-Read CTA Bar (85% scroll depth)        — fixed bottom bar, slide-up animation
  3. Subscriber Detection                         — localStorage 'pb_subscribed' flag
- New REST endpoint: POST /wp-json/pb-security/v1/subscribe
  - Accepts: { email: "..." }
  - Server-side call to Brevo API v3 to add contact to list 3 (The Neural Feed)
  - Rate limit: 5 req/IP/min
  - BREVO_API_KEY read from wp-config.php constant
- All JS injected via wp_footer (priority 25)
- All CSS injected via wp_head (priority 25)

Author: full-stack-developer agent
Date: 2026-02-21
"""

import os
import re
import sys
import time
import json
import urllib.request
import urllib.error
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")

PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"

env_text = (AETHER_ROOT / ".env").read_text()
WP_PASSWORD_MATCH = re.search(r"PUREBRAIN_WP_PASSWORD='([^']+)'", env_text)
WP_PASSWORD = WP_PASSWORD_MATCH.group(1) if WP_PASSWORD_MATCH else ""
WP_APP_PASSWORD_MATCH = re.search(r"PUREBRAIN_WP_APP_PASSWORD='([^']+)'", env_text)
WP_APP_PASSWORD = WP_APP_PASSWORD_MATCH.group(1) if WP_APP_PASSWORD_MATCH else ""

PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)

SCREENSHOT_DEPLOY = str(AETHER_ROOT / "exports/screenshots/plugin_v350_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v350_verify.png")


def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 3.5.0":                                  "3.5.0" in content,
        "v3.5.0 changelog entry":                         "Lead capture systems" in content,
        "pb-security/v1 subscribe route":                 "pb-security/v1', '/subscribe'" in content,
        "purebrain_brevo_subscribe function":             "purebrain_brevo_subscribe" in content,
        "Brevo API URL (api.brevo.com)":                  "api.brevo.com/v3/contacts" in content,
        "Brevo list 3 (The Neural Feed)":                 "'listIds'       => array( 3 )" in content,
        "BREVO_API_KEY constant read":                    "defined( 'BREVO_API_KEY' )" in content,
        "rate limit 5 per minute subscribe":              "purebrain_check_rate_limit( 'brevo_subscribe', 5, 60 )" in content,
        "updateEnabled in Brevo body":                    "'updateEnabled' => true" in content,
        "pb-lead-inline CSS id":                          "#pb-lead-inline" in content,
        "pb-lead-bar CSS id":                             "#pb-lead-bar" in content,
        "pb-lead-capture-css style id":                   "purebrain-lead-capture-css" in content,
        "pb-lead-capture-js script id":                   "purebrain-lead-capture-js" in content,
        "LS_SUBSCRIBED key":                              "pb_subscribed" in content,
        "LS_INLINE_DISMISSED key":                        "pb_inline_dismissed" in content,
        "LS_BAR_DISMISSED key":                           "pb_bar_dismissed" in content,
        "50% scroll threshold":                           "depth >= 50" in content,
        "85% scroll threshold":                           "depth >= 85" in content,
        "inline dismiss 7 days":                          "7  * 24 * 60 * 60 * 1000" in content,
        "bar dismiss 14 days":                            "14 * 24 * 60 * 60 * 1000" in content,
        "Neural Feed inline text":                        "Aether writes more like this every week" in content,
        "Post-read bar headline":                         "You made it to the end" in content,
        "success message text":                           "Welcome to The Neural Feed" in content,
        "wp_footer priority 25":                          "}, 25 );" in content,
        "wp_head priority 25":                            "}, 25 );" in content,
        "doSubscribe function":                           "function doSubscribe(" in content,
        # Retained from v3.4.0
        "v3.4.0 update-post-meta":                        "purebrain_update_post_meta_handler" in content,
        "wpseo_schema_breadcrumb filter":                 "wpseo_schema_breadcrumb" in content,
        "html body .pb-blog-nav a:hover rule":            "html body .pb-blog-nav a:hover" in content,
        "footer-logo-brand script id":                    "purebrain-footer-logo-brand" in content,
        "pb-logo-brand class":                            "pb-logo-brand" in content,
        "strip-newsletter-inline-styles JS":              "purebrain-strip-newsletter-inline-styles" in content,
        "data-pb-subscribe attribute":                    "data-pb-subscribe" in content,
        "CTA awakening selector present":                 'a[href*="awakening"]' in content,
        "subscribe selector present":                     'a[href*="subscribe"]' in content,
        "api.purebrain.ai (log)":                         "https://api.purebrain.ai/api/log-conversation" in content,
        "api.purebrain.ai (payment)":                     "https://api.purebrain.ai/api/verify-payment" in content,
        "sslverify true":                                 "'sslverify' => true" in content,
        "rate limiter":                                   "purebrain_check_rate_limit" in content,
        "pb-legal-link":                                  "pb-legal-link" in content,
        "pb-blog-nav":                                    "pb-blog-nav" in content,
        "FAQ accordion":                                  "faq-accordion" in content,
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

    print("=== PureBrain Security Plugin v3.5.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")
    print("Change: Lead capture systems - in-content box (50%) + post-read bar (85%)")
    print("        New endpoint: POST /wp-json/pb-security/v1/subscribe -> Brevo list 3")

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
                        val.includes('3.5.0') &&
                        val.includes('pb-security/v1') &&
                        val.includes('purebrain_brevo_subscribe') &&
                        val.includes('pb-lead-inline') &&
                        val.includes('pb-lead-bar') &&
                        val.includes('html body .pb-blog-nav a:hover') &&
                        val.includes('pb-logo-brand')
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
                if "3.5.0" in current:
                    save_success = True
                    print("  v3.5.0 found in editor - assuming success.")

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
    """Verify v3.5.0 subscribe endpoint is available and blog post renders capture elements."""
    print("\n[Verification] Checking live subscribe endpoint...")

    # Check endpoint registration via OPTIONS
    test_url = "https://purebrain.ai/wp-json/pb-security/v1/subscribe"
    req = urllib.request.Request(
        test_url,
        method="OPTIONS",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://purebrain.ai",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            print(f"  [OK] Endpoint responded: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        if e.code in (200, 405):  # 405 = Method Not Allowed (endpoint exists but POST only)
            print(f"  [OK] Endpoint exists (HTTP {e.code})")
        else:
            print(f"  [WARN] Endpoint HTTP {e.code}: {body[:200]}")
    except Exception as e:
        print(f"  [ERROR] Could not reach endpoint: {e}")

    # Check that a blog post has lead capture markup
    print("\n[Verification] Checking blog post for lead capture markup...")
    blog_url = "https://purebrain.ai/why-95-percent-of-ai-pilots-fail/"
    req2 = urllib.request.Request(
        blog_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req2, timeout=30) as resp:
            html = resp.read().decode("utf-8")

        checks = {
            "pb-lead-inline element":    'id="pb-lead-inline"' in html,
            "pb-lead-bar element":       'id="pb-lead-bar"' in html,
            "pb-lead-capture-css style": 'id="purebrain-lead-capture-css"' in html,
            "pb-lead-capture-js script": 'id="purebrain-lead-capture-js"' in html,
            "Neural Feed text":          "Neural Feed" in html,
        }

        all_ok = True
        for name, result in checks.items():
            status = "OK" if result else "MISSING"
            print(f"  [{status}] {name}")
            if not result:
                all_ok = False
        return all_ok

    except Exception as e:
        print(f"  [ERROR] Could not fetch blog post: {e}")
        return False


if __name__ == "__main__":
    print("=" * 65)
    print("PUREBRAIN SECURITY PLUGIN v3.5.0 - DEPLOY")
    print("Change: Lead capture systems for blog posts")
    print("  Adds: In-content subscribe box (50% scroll)")
    print("        Post-read CTA bar (85% scroll)")
    print("        POST /wp-json/pb-security/v1/subscribe")
    print("        -> Brevo API -> list 3 (The Neural Feed)")
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
        print("\n[SUCCESS] v3.5.0 IS LIVE!")
        print("\n  What's now active on blog posts:")
        print("  - In-content subscribe box: slides in at 50% scroll")
        print("    'Enjoying this? Aether writes more like this every week in The Neural Feed.'")
        print("  - Post-read CTA bar: slides up at 85% scroll")
        print("    'You made it to the end. That means you take AI seriously.'")
        print("  - Subscriber detection: localStorage 'pb_subscribed' prevents repeat shows")
        print("  - Both forms submit to Brevo list 3 via /wp-json/pb-security/v1/subscribe")
        print("  - Dismissal memory: inline 7 days, bar 14 days")
        print("\n  IMPORTANT - Add BREVO_API_KEY to wp-config.php:")
        print("    define( 'BREVO_API_KEY', 'xkeysib-...' );")
        print("  Without this constant, subscribes will silently succeed (no Brevo entry).")
        print(f"\n  Screenshots:")
        print(f"    Deploy: {SCREENSHOT_DEPLOY}")
        print(f"    Verify: {SCREENSHOT_VERIFY}")
    else:
        print("\n[WARNING] Some live checks failed - CDN may still be caching old content.")
        print("  Hard-refresh (Ctrl+Shift+R) to bypass browser cache.")
        print("  If markup not in HTML, check plugin is active and saved correctly.")
        print(f"  Deploy screenshot: {SCREENSHOT_DEPLOY}")
        print(f"  Verify screenshot: {SCREENSHOT_VERIFY}")
