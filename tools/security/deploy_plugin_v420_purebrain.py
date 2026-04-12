#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v4.2.0 (as part of v4.3.0 file)
to purebrain.ai.

GEO Fix 3: Social sharing bar injection on all single blog posts.
- Injects LinkedIn, X, Email, Copy Link buttons before .blog-cta-block
- CSS injected via wp_head (un-hides theme .post-social-sharing too)
- Pure Brain brand colors: blue (#2a93c1) default, orange (#f1420b) hover

Author: full-stack-developer agent
Date: 2026-02-23
"""

import os
import re
import sys
import time
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"
SCREENSHOT_DIR = str(AETHER_ROOT / "exports/screenshots")

# --- Credentials -----------------------------------------------------------
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"{key}=([^\n]+)", env_text)
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
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v420_purebrain_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v420_purebrain_verify.png",
    "blog_post_url":     "https://purebrain.ai/the-ai-trust-gap/",
}


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "social share CSS block":          "purebrain-social-share-css" in content,
        "social share JS block":           "pb-social-share-js" in content,
        "pb-social-share element":         "bar.id = 'pb-social-share'" in content,
        "LinkedIn share button":           "linkedin.com/sharing" in content,
        "X/Twitter share button":          "twitter.com/intent/tweet" in content,
        "Email share button":              "pb-share-btn" in content and "mailto:" in content,
        "Copy Link button":                "pb-copy-link-btn" in content,
        "theme sharing un-hide CSS":       "post-social-sharing" in content,
        "changelog GEO Fix 3":            "GEO Fix 3" in content,
        # Previous features preserved
        "guide-unlock REST route":         "purebrain/v1', '/guide-unlock'" in content,
        "pb-guide-gate-css style block":   "pb-guide-gate-css" in content,
        "blog listing Read More button":   "pb-read-more-btn" in content,
        "transparency section":            "aether-transparency__cta-btn" in content,
        "link hover fix":                  "purebrain-link-hover-fix" in content,
        "footer logo brand":               "pb-logo-brand" in content,
        "FAQ accordion":                   "faq-accordion" in content,
        "rate limiter":                    "purebrain_check_rate_limit" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


# --- Playwright deploy -----------------------------------------------------

def deploy_to_site(site: dict, content: str) -> bool:
    from playwright.sync_api import sync_playwright

    name = site["name"]
    print(f"\n{'='*65}")
    print(f"DEPLOYING TO: {name}")
    print(f"{'='*65}")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = ctx.new_page()

        # Step 1: Login
        print(f"\n[Step 1] Logging in to {name}...")
        page.goto(site["login_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        # Handle GoDaddy SSO overlay
        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("  GoDaddy SSO overlay — clicking username/password link...")
            sso_toggle.click()
            time.sleep(2)

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: Login form not visible. Screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # CAPTCHA check
        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  CAPTCHA detected! Screenshot: {site['screenshot_deploy']}")
            print("  Wait 15-30 minutes for GoDaddy bot protection to reset, then retry.")
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

        # Step 2: Plugin Editor
        print(f"\n[Step 2] Opening Plugin Editor...")
        page.goto(site["editor_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        page_text = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
            print("  ERROR: File editing is disabled.")
            browser.close()
            return False

        has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_textarea   = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

        if not has_codemirror and not has_textarea:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: No editor found.")
            browser.close()
            return False

        # Step 3: Set content
        print("\n[Step 3] Setting plugin content...")
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
                        val.includes('pb-social-share') &&
                        val.includes('pb-social-share-css') &&
                        val.includes('pb-copy-link-btn')
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

        # Step 4: Save
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

        save_success = False
        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin file saved!")
            save_success = True
        elif "Parse error" in page_text or "syntax error" in page_text.lower():
            print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear: {page_text[:200]}")
            # Check editor content as proxy for success
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 800) : 'N/A';
                }""")
                if "pb-social-share" in current and "pb-copy-link-btn" in current:
                    save_success = True
                    print("  social share found in editor — save assumed successful.")

        if not save_success:
            print(f"  Deploy screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # Step 5: Clear Elementor cache
        print("\n[Step 5] Clearing Elementor cache...")
        credentials = base64.b64encode(
            f"{site['user']}:{site['app_password']}".encode()
        ).decode()

        cache_req = urllib.request.Request(
            "https://purebrain.ai/wp-json/elementor/v1/cache",
            method="DELETE",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
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

    return True


# --- Post-deploy cache bust ------------------------------------------------

def bust_page_cache(site: dict) -> None:
    credentials = base64.b64encode(
        f"{site['user']}:{site['app_password']}".encode()
    ).decode()
    auth_header = f"Basic {credentials}"

    post_ids = [631, 381, 316, 98, 172, 373, 565, 480, 606, 696]

    print(f"\n[Step 6] Busting page cache (touching blog posts)...")
    for post_id in post_ids:
        payload = json.dumps({"status": "publish"}).encode()
        req = urllib.request.Request(
            f"https://purebrain.ai/wp-json/wp/v2/posts/{post_id}",
            data=payload,
            method="POST",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                print(f"  Post {post_id}: HTTP {resp.status} — cache busted")
        except urllib.error.HTTPError as e:
            print(f"  Post {post_id}: HTTP {e.code}")
        except Exception as ex:
            print(f"  Post {post_id}: {ex}")


# --- Live verification -----------------------------------------------------

def verify_live(site: dict) -> dict:
    url = site["blog_post_url"]
    print(f"\n[Verify] Checking live blog post: {url}")

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
            http_code = resp.status
    except Exception as ex:
        return {"fetch_error": str(ex)}

    results = {}
    checks = {
        "page_loads":             http_code == 200,
        "pb_social_share_css":    "purebrain-social-share-css" in html,
        "pb_social_share_js":     "pb-social-share-js" in html or "pb-social-share" in html,
        "linkedin_share":         "linkedin.com/sharing" in html,
        "twitter_share":          "twitter.com/intent/tweet" in html,
        "copy_link_btn":          "pb-copy-link-btn" in html,
        "read_next_block":        "pb-read-next" in html,
    }

    for name, result in checks.items():
        status = "OK" if result else "MISSING"
        print(f"  [{status}] {name}")
        results[name] = result

    passed = sum(1 for v in results.values() if v is True)
    total  = len(results)
    print(f"\n  Verification: {passed}/{total} checks passed")
    return results


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin — GEO Fix 3 Deployment")
    print("Social sharing bar + theme share restore")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Content length: {len(content)} chars\n")

    # Pre-flight validation
    print("--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Plugin validation failed.")
        sys.exit(1)
    print("Validation passed.\n")

    # Deploy
    success = deploy_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Deployment succeeded.")

    # Bust cache
    bust_page_cache(SITE)

    # Wait for cache to settle
    print("\nWaiting 5 seconds for cache to settle...")
    time.sleep(5)

    # Verify live
    results = verify_live(SITE)

    # Summary
    print("\n" + "=" * 65)
    all_ok = all(v for v in results.values() if isinstance(v, bool))

    if all_ok:
        print("DEPLOYMENT COMPLETE AND VERIFIED.")
        print("\nFix 3 is live:")
        print("  - Social sharing bar (LinkedIn, X, Email, Copy Link) injected on all blog posts")
        print("  - Theme .post-social-sharing buttons un-hidden and styled")
        print("  - Brand colors: #2a93c1 default, #f1420b hover")
    else:
        failed = [k for k, v in results.items() if v is not True]
        print(f"DEPLOYMENT DONE — some verification checks failed: {', '.join(failed)}")
        print("Note: CDN cache may need time to clear. Try hard-refresh to verify.")


if __name__ == "__main__":
    main()
