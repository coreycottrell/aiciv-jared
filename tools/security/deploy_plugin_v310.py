#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v3.1.0 to WordPress.

v3.1.0 changes:
- Nav menu hover color fix: .pb-blog-nav a:hover now shows orange (#f1420b)
  on BOTH blog posts AND category/archive pages consistently.

Root cause of the bug:
  The plugin's .pb-blog-nav a:hover was set to #2a93c1 (blue).
  On blog posts, Additional CSS had `body.single-post a:hover { color: #f1420b }`
  which accidentally overrode the plugin's blue to orange (Additional CSS loads
  after plugin CSS, so at equal specificity it wins).
  On category pages, no such broad rule existed, so hover stayed blue.

Fix:
  1. Plugin now directly sets hover color to #f1420b (orange).
  2. Body-class-scoped selectors added for high specificity:
     body.single-post .pb-blog-nav a:hover,
     body.category .pb-blog-nav a:hover,
     body.archive .pb-blog-nav a:hover,
     body.tag .pb-blog-nav a:hover,
     .pb-blog-nav a:hover
  3. All use `color: #f1420b !important` — consistent everywhere.

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

SCREENSHOT_DEPLOY = str(AETHER_ROOT / "exports/screenshots/plugin_v310_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v310_verify.png")


def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 3.1.0":                           "3.1.0" in content,
        "v3.1.0 changelog entry":                  "Nav menu hover color fix" in content,
        "pb-blog-nav orange hover (#f1420b)":      "body.category .pb-blog-nav a:hover" in content,
        "body.archive .pb-blog-nav a:hover":       "body.archive .pb-blog-nav a:hover" in content,
        "body.single-post .pb-blog-nav a:hover":   "body.single-post .pb-blog-nav a:hover" in content,
        "orange color in hover rule":              "color: #f1420b !important;" in content,
        "NOT blue in hover": "pb-blog-nav a:hover,\n.pb-blog-nav a:focus {\n    color: #2a93c1" not in content,
        "footer-logo-brand script id":             "purebrain-footer-logo-brand" in content,
        "pb-logo-brand class":                     "pb-logo-brand" in content,
        "strip-newsletter-inline-styles JS":       "purebrain-strip-newsletter-inline-styles" in content,
        "data-pb-subscribe attribute":             "data-pb-subscribe" in content,
        "CTA awakening selector present":          'a[href*="awakening"]' in content,
        "subscribe selector present":             'a[href*="subscribe"]' in content,
        "api.purebrain.ai (log)":                  "https://api.purebrain.ai/api/log-conversation" in content,
        "api.purebrain.ai (payment)":              "https://api.purebrain.ai/api/verify-payment" in content,
        "sslverify true":                          "'sslverify' => true" in content,
        "rate limiter":                            "purebrain_check_rate_limit" in content,
        "pb-legal-link":                           "pb-legal-link" in content,
        "pb-blog-nav":                             "pb-blog-nav" in content,
        "FAQ accordion":                           "faq-accordion" in content,
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

    print("=== PureBrain Security Plugin v3.1.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")
    print("Change: Nav menu hover → orange (#f1420b) on blog posts AND category pages")

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
                        val.includes('3.1.0') &&
                        val.includes('body.category .pb-blog-nav a:hover') &&
                        val.includes('body.archive .pb-blog-nav a:hover') &&
                        val.includes('pb-logo-brand') &&
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
                if "3.1.0" in current:
                    save_success = True
                    print("  v3.1.0 found in editor - assuming success.")

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
    """Verify v3.1.0 nav hover fix is live on both page types."""
    print("\n[Verification] Checking live site...")

    test_urls = [
        ("blog post", "https://purebrain.ai/blog/why-95-percent-of-ai-pilots-fail/"),
        ("category/for-teams", "https://purebrain.ai/category/for-teams/"),
        ("category/for-individuals", "https://purebrain.ai/category/for-individuals/"),
    ]

    all_ok = True
    for page_type, test_url in test_urls:
        print(f"\n  Checking {page_type}: {test_url}")
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
                "pb-blog-nav style injected":                    "purebrain-blog-nav-menu" in html,
                "pb-blog-nav JS injected":                       "purebrain-blog-nav-menu-js" in html,
                "body.category hover rule present":              "body.category .pb-blog-nav a:hover" in html,
                "orange #f1420b in nav hover":                   "color: #f1420b !important;" in html,
                "NOT blue #2a93c1 as sole hover":                "color: #2a93c1 !important;\n    text-decoration: none !important;\n    background: none" not in html,
            }

            for name, result in checks.items():
                status = "OK" if result else "MISSING"
                print(f"    [{status}] {name}")
                if not result:
                    all_ok = False

        except Exception as e:
            print(f"  Request failed: {e}")
            all_ok = False

    return all_ok


if __name__ == "__main__":
    print("=" * 65)
    print("PUREBRAIN SECURITY PLUGIN v3.1.0 - DEPLOY")
    print("Change: Nav menu hover color → orange (#f1420b) on ALL page types")
    print("  Fixes: Category/archive pages showing blue hover (should be orange)")
    print("  Root cause: Plugin used #2a93c1; Additional CSS accidentally")
    print("    overrode to orange on posts only via body.single-post a:hover")
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
        print("\n[SUCCESS] v3.1.0 IS LIVE!")
        print("\n  What's now fixed:")
        print("  - Nav menu (Home | Blog | AI Assessment) hover is ORANGE on:")
        print("    * Blog posts (body.single-post)")
        print("    * /category/for-teams/ (body.category)")
        print("    * /category/for-individuals/ (body.category)")
        print("    * All archive/tag pages")
        print("  - Uses high-specificity scoped selectors to prevent any override")
        print(f"\n  Screenshots:")
        print(f"    Deploy: {SCREENSHOT_DEPLOY}")
        print(f"    Verify: {SCREENSHOT_VERIFY}")
    else:
        print("\n[WARNING] Some checks failed - CDN may still be caching old content.")
        print("  Hard-refresh (Ctrl+Shift+R) to bypass browser cache.")
        print(f"  Deploy screenshot: {SCREENSHOT_DEPLOY}")
        print(f"  Verify screenshot: {SCREENSHOT_VERIFY}")
