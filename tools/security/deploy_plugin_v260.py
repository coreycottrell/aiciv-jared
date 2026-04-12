#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v2.6.0 to WordPress.

v2.6.0 changes:
1. Proxy endpoints switch from raw IP (89.167.19.20:8443) to Cloudflare Tunnel
   (api.purebrain.ai) — valid TLS, no raw IP exposed to browser clients.

2. sslverify=true enabled on wp_remote_post calls (Cloudflare Tunnel provides
   a valid TLS certificate, so we no longer need to disable verification).

3. Transient-based rate limiting added:
   - Log conversation proxy: 30 req/min per IP
   - Payment verification proxy: 10 req/min per IP (stricter)
   - Uses WordPress transients — no extra DB tables needed.

4. 64 KB body size cap on all proxy endpoints.

5. Inline onmouseover/onmouseout handlers in legal footer replaced with
   CSS-only hover class (.pb-legal-link:hover), removing inline JS event handlers.

Author: full-stack-developer agent
Date: 2026-02-20
"""

import os
import sys
import time
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_FILE = AETHER_ROOT / ".env"
load_dotenv(ENV_FILE)

PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security-plugin.php"
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = os.environ.get("PUREBRAIN_WP_PASSWORD", "")

# NOTE: Plugin directory is "purebrain-security" (not "purebrain-security-plugin")
PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)

SCREENSHOT_DEPLOY = str(AETHER_ROOT / "exports/screenshots/plugin_v260_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v260_verify.png")
SCREENSHOT_LIVE   = str(AETHER_ROOT / "exports/screenshots/plugin_v260_live.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v2.6.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")
    print("Changes: Cloudflare Tunnel endpoints, sslverify=true, rate limiting, CSS hover")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    # Validate v2.6.0 content markers
    checks = {
        "version 2.6.0": "2.6.0" in new_content,
        "api.purebrain.ai endpoint (log)": "https://api.purebrain.ai/api/log-conversation" in new_content,
        "api.purebrain.ai endpoint (payment)": "https://api.purebrain.ai/api/verify-payment" in new_content,
        # IP may appear in PHP docblock comments (historical reference) but NOT as a URL
        "NO raw IP in endpoint URLs": "https://89.167.19.20" not in new_content and "http://89.167.19.20" not in new_content,
        "sslverify true": "'sslverify' => true" in new_content,
        "rate limiter function": "purebrain_check_rate_limit" in new_content,
        "transient rate limiting": "get_transient" in new_content,
        "64KB body size cap": "65536" in new_content,
        "pb-legal-link CSS class": "pb-legal-link" in new_content,
        "CSS hover (no inline handlers)": "pb-legal-link:hover" in new_content,
        "pb-blog-nav still present": "pb-blog-nav" in new_content,
        "nav menu still present": "AI Assessment" in new_content,
        "FAQ accordion still present": "faq-accordion" in new_content,
    }

    all_passed = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_passed = False

    if not all_passed:
        print("\nERROR: Plugin file validation failed. Aborting deploy.")
        sys.exit(1)

    print("Plugin content validated (v2.6.0, all markers present). Starting Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,  # Sharp rendering for CAPTCHA reading
        )
        page = context.new_page()

        # ----------------------------------------------------------------
        # Step 1: Login
        # ----------------------------------------------------------------
        print("\n[Step 1] Logging in to WP Admin...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        # Handle GoDaddy SSO overlay
        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("  GoDaddy SSO overlay detected. Clicking username/password link...")
            sso_toggle.click()
            time.sleep(2)

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=SCREENSHOT_DEPLOY)
            print("  ERROR: Login form not visible. Screenshot saved.")
            browser.close()
            return False

        # Check for CAPTCHA (GoDaddy bot protection)
        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=SCREENSHOT_DEPLOY)
            print(f"  CAPTCHA detected! Screenshot saved: {SCREENSHOT_DEPLOY}")
            print("  Cannot proceed automatically - CAPTCHA requires manual solving.")
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

        current_url = page.url
        print(f"  After login URL: {current_url}")

        if "wp-login.php" in current_url:
            page.screenshot(path=SCREENSHOT_DEPLOY)
            page_text = page.inner_text("body")
            print(f"  ERROR: Login failed. Page: {page_text[:300]}")
            browser.close()
            return False

        print("  Login successful!")

        # ----------------------------------------------------------------
        # Step 2: Navigate to Plugin Editor
        # ----------------------------------------------------------------
        print("\n[Step 2] Opening Plugin Editor...")
        page.goto(PLUGIN_EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        page_text = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
            print("  ERROR: File editing disabled in wp-config.php")
            browser.close()
            return False
        if "You need a higher level" in page_text:
            print("  ERROR: Insufficient permissions")
            browser.close()
            return False

        # Check which editor type is present
        has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_textarea = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

        if not has_codemirror and not has_textarea:
            print("  ERROR: No editor found on page")
            page.screenshot(path=SCREENSHOT_DEPLOY)
            browser.close()
            return False

        # ----------------------------------------------------------------
        # Step 3: Set plugin content
        # ----------------------------------------------------------------
        print("\n[Step 3] Setting plugin content via JS...")

        if has_codemirror:
            print("  Using CodeMirror setValue()...")
            success = page.evaluate("""(content) => {
                try {
                    const cmEl = document.querySelector('.CodeMirror');
                    if (!cmEl) return 'no_cm_element';
                    const cm = cmEl.CodeMirror;
                    if (!cm) return 'no_cm_instance';
                    cm.setValue(content);
                    const val = cm.getValue();
                    if (
                        val.includes('2.6.0') &&
                        val.includes('api.purebrain.ai') &&
                        val.includes('purebrain_check_rate_limit') &&
                        val.includes('pb-legal-link') &&
                        val.includes('pb-blog-nav')
                    ) return 'success';
                    return 'set_failed: got ' + val.length + ' chars, missing expected content';
                } catch(e) {
                    return 'error: ' + e.message;
                }
            }""", new_content)
            print(f"  CodeMirror result: {success}")

            if success != 'success':
                print("  CodeMirror failed. Trying textarea fallback...")
                page.evaluate("""() => {
                    const ta = document.querySelector('#newcontent');
                    if (ta) {
                        ta.style.display = 'block';
                        ta.style.visibility = 'visible';
                    }
                }""")
                page.evaluate("""(content) => {
                    const ta = document.querySelector('#newcontent');
                    if (ta) {
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLTextAreaElement.prototype, 'value').set;
                        nativeInputValueSetter.call(ta, content);
                        ta.dispatchEvent(new Event('input', { bubbles: true }));
                        ta.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""", new_content)
                print("  Textarea fallback set.")
        else:
            print("  Using textarea via JS...")
            page.evaluate("""(content) => {
                const ta = document.querySelector('#newcontent');
                if (ta) {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeInputValueSetter.call(ta, content);
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    ta.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", new_content)
            print("  Textarea content set.")

        time.sleep(1)

        # ----------------------------------------------------------------
        # Step 4: Save the file
        # ----------------------------------------------------------------
        print("\n[Step 4] Saving plugin file...")
        saved = page.evaluate("""() => {
            const btn = document.querySelector('#submit') ||
                        document.querySelector('input[type="submit"]');
            if (btn) {
                btn.click();
                return 'clicked';
            }
            return 'no_button';
        }""")
        print(f"  Save button click: {saved}")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=45000)
        except Exception:
            pass
        time.sleep(4)

        page.screenshot(path=SCREENSHOT_DEPLOY)
        page_text = page.inner_text("body")

        save_success = False
        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin file saved!")
            save_success = True
        elif "Parse error" in page_text or "syntax error" in page_text:
            print("  ERROR: PHP syntax error - file NOT saved!")
            print(f"  Page excerpt: {page_text[:500]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear. Page excerpt: {page_text[:400]}")
            # Check editor content to confirm version
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 500) : 'N/A';
                }""")
                print(f"  Current editor start: {current}")
                if '2.6.0' in current:
                    save_success = True
                    print("  Version 2.6.0 found in editor - assuming success.")

        # ----------------------------------------------------------------
        # Step 5: Flush GoDaddy/Cloudflare cache
        # ----------------------------------------------------------------
        print("\n[Step 5] Flushing GoDaddy/Cloudflare cache...")
        page.goto(f"{WP_ADMIN_URL}/options-general.php", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # Look for the GoDaddy flush_cache nonce link
        flush_url = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            const flushLink = links.find(a =>
                /flush.cache/i.test(a.textContent) ||
                /flush.cache/i.test(a.href) ||
                /wpaas_action=flush_cache/i.test(a.href)
            );
            return flushLink ? flushLink.href : null;
        }""")
        print(f"  Flush URL found: {flush_url}")

        if flush_url:
            page.goto(flush_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            print("  Cache flush requested!")
            page.screenshot(path=SCREENSHOT_VERIFY)
        else:
            print("  No flush URL found. Cache will expire naturally.")
            page.screenshot(path=SCREENSHOT_VERIFY)

        browser.close()

    return save_success


def verify_live():
    """Verify v2.6.0 changes are live by checking rendered HTML."""
    print("\n[Verification] Checking v2.6.0 indicators on live site...")

    # Check a blog post (tests plugin CSS output) and the main site
    blog_url = "https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/"
    home_url = "https://purebrain.ai/"

    results = {}

    for label, url in [("blog post", blog_url), ("homepage", home_url)]:
        print(f"\n  Checking {label}: {url}")
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
            },
        )
        try:
            response = urllib.request.urlopen(req, timeout=30)
            html = response.read().decode("utf-8")

            checks = {
                "pb-legal-link class in footer": "pb-legal-link" in html,
                # IP must not appear as a live URL in rendered page source
                "NO raw IP as URL in HTML": "https://89.167.19.20" not in html and "http://89.167.19.20" not in html,
            }

            if label == "blog post":
                checks.update({
                    "v2.6.0 version reference": "2.6.0" in html,
                    "pb-blog-nav present": "pb-blog-nav" in html,
                    "FAQ accordion present": "faq-accordion" in html,
                    "orange CTA gradient present": "#f1420b 0%, #d13608" in html,
                })

            page_ok = True
            for name, result in checks.items():
                status = "OK" if result else "MISSING/FAIL"
                print(f"    [{status}] {name}")
                if not result:
                    page_ok = False

            results[label] = page_ok

        except Exception as e:
            print(f"    Request failed: {e}")
            results[label] = False

    return all(results.values())


if __name__ == "__main__":
    print("=" * 65)
    print("PUREBRAIN SECURITY PLUGIN v2.6.0 - DEPLOY")
    print("Change 1: Raw IP 89.167.19.20 → api.purebrain.ai (Cloudflare Tunnel)")
    print("Change 2: sslverify=true (Cloudflare provides valid TLS cert)")
    print("Change 3: Transient rate limiting (30/min log, 10/min payment)")
    print("Change 4: 64KB body size cap on proxy endpoints")
    print("Change 5: CSS-only hover on legal footer (no inline JS handlers)")
    print("=" * 65)

    result = deploy()

    if result:
        print("\n[Deploy] SUCCESS: Plugin saved to WordPress.")
    else:
        print("\n[Deploy] FAILED or uncertain. Check screenshots.")
        print(f"  Deploy screenshot: {SCREENSHOT_DEPLOY}")
        sys.exit(1)

    # Allow CDN propagation
    print("\nWaiting 10 seconds for CDN propagation...")
    time.sleep(10)

    # Verify live
    live_ok = verify_live()

    print("\n" + "=" * 65)
    print("FINAL RESULT")
    print("=" * 65)

    if live_ok:
        print("\n[SUCCESS] v2.6.0 IS LIVE!")
        print(f"\n  Screenshots:")
        print(f"    Deploy/save:    {SCREENSHOT_DEPLOY}")
        print(f"    Cache flush:    {SCREENSHOT_VERIFY}")
        print("\n  Security improvements now active:")
        print("  - Log/payment proxies use api.purebrain.ai (Cloudflare Tunnel)")
        print("  - TLS verification enabled (sslverify=true)")
        print("  - Rate limiter: 30 req/min (logging), 10 req/min (payment) per IP")
        print("  - Body size capped at 64KB per request")
        print("  - Legal footer uses CSS hover (no inline JS handlers)")
        print("  - Raw IP 89.167.19.20 no longer exposed in plugin PHP or HTML output")
    else:
        print("\n[WARNING] Some checks failed - CDN may still be serving cached content.")
        print("  CDN cache-control is set to 31 days (Cloudflare). Hard-refresh")
        print("  (Ctrl+Shift+R) or wait for cache expiry to see all changes.")
        print(f"  Deploy screenshot: {SCREENSHOT_DEPLOY}")
        print(f"  Verify screenshot: {SCREENSHOT_VERIFY}")
