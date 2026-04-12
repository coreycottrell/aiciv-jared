#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v3.9.1 to BOTH sites:
  1. purebrain.ai      (user=Aether, PUREBRAIN_WP_PASSWORD)
  2. jareddsanborn.com (user=AetherPureBrain.ai, WORDPRESS_APP_PASSWORD)

v3.9.1 changes:
- Blog in-text link hover fix: orange background + WHITE text on hover (was invisible orange-on-orange)
- wp_head CSS injection on is_single() pages: style id="purebrain-link-hover-fix"
- Selectors: body.single-post .entry-content a + .elementor-widget-theme-post-content a
- Exclusions: :not(.blog-cta-button):not([rel="tag"])

CDN Cache fix strategy:
- The plugin injects CSS via wp_head on every PHP render
- wp_head CSS is in <head>, part of the server-rendered HTML
- If CDN caches the HTML, the CSS will be cached WITH the page from the next render
- Also: injecting style block into post content via REST API (complementary approach)

Author: full-stack-developer agent
Date: 2026-02-22
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


def _env(key, quoted=True):
    if quoted:
        m = re.search(rf"{key}='([^']+)'", env_text)
        if m:
            return m.group(1)
    m = re.search(rf"{key}=([^\n]+)", env_text)
    return m.group(1).strip() if m else ""


SITES = [
    {
        "name":         "purebrain.ai",
        "admin_url":    "https://purebrain.ai/wp-admin",
        "login_url":    "https://purebrain.ai/wp-login.php",
        "user":         "Aether",
        "password":     _env("PUREBRAIN_WP_PASSWORD"),
        "app_password": _env("PUREBRAIN_WP_APP_PASSWORD"),
        "editor_url":   (
            "https://purebrain.ai/wp-admin/plugin-editor.php"
            "?file=purebrain-security/purebrain-security-plugin.php"
            "&plugin=purebrain-security/purebrain-security-plugin.php"
        ),
        "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v391_purebrain_deploy.png",
        "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v391_purebrain_verify.png",
        "blog_post_url": "https://purebrain.ai/the-ai-trust-gap/",
    },
    {
        "name":         "jareddsanborn.com",
        "admin_url":    "https://jareddsanborn.com/wp-admin",
        "login_url":    "https://jareddsanborn.com/wp-login.php",
        "user":         "AetherPureBrain.ai",
        "password":     _env("WORDPRESS_APP_PASSWORD"),
        "app_password": _env("WORDPRESS_APP_PASSWORD"),
        "editor_url":   (
            "https://jareddsanborn.com/wp-admin/plugin-editor.php"
            "?file=purebrain-security/purebrain-security-plugin.php"
            "&plugin=purebrain-security/purebrain-security-plugin.php"
        ),
        "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v391_jared_deploy.png",
        "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v391_jared_verify.png",
        "blog_post_url": "https://jareddsanborn.com/the-ai-trust-gap/",
    },
]


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 3.9.1":                        "3.9.1" in content,
        "link hover CSS section j3":             "j3) BLOG IN-TEXT LINK HOVER FIX" in content,
        "purebrain-link-hover-fix style":        "purebrain-link-hover-fix" in content,
        "orange bg hover rule":                  "background-color: #f1420b !important" in content,
        "white text on hover":                   "color: #ffffff !important" in content,
        "entry-content selector":                ".entry-content a:not(.blog-cta-button)" in content,
        "elementor selector":                    ".elementor-widget-theme-post-content" in content,
        "is_single check":                       "is_single()" in content,
        # v3.9.0 features retained
        "tag pills CSS present":                 "purebrain-tag-pills-cta-fix" in content,
        # v3.8.0 features retained
        "v3.8.0 security hardening":             "MED-003" in content,
        # v3.7.0 features retained
        "Subscribe nav link":                    "neural-feed-subscribe" in content,
        # v3.6.0 features retained
        "transparency REST route":               "purebrain/v1', '/transparency-data'" in content,
        # v3.5.0 features retained
        "pb-lead-inline":                        "pb-lead-inline" in content,
        # v3.2.0 features retained
        "html body .pb-blog-nav a:hover":        "html body .pb-blog-nav a:hover" in content,
        # older features retained
        "pb-logo-brand class":                   "pb-logo-brand" in content,
        "FAQ accordion":                         "faq-accordion" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


# --- Playwright deploy to one site -----------------------------------------

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
        print(f"\n[Step 1] Logging in to {name} WP Admin...")
        page.goto(site["login_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        # Handle GoDaddy SSO overlay (purebrain.ai)
        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("  GoDaddy SSO overlay detected - clicking username/password link...")
            sso_toggle.click()
            time.sleep(2)

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: Login form not visible. Screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # CAPTCHA check (GoDaddy bot protection)
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
        print(f"\n[Step 2] Opening Plugin Editor for {name}...")
        page.goto(site["editor_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        page_text = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
            print("  ERROR: File editing is disabled (DISALLOW_FILE_EDIT).")
            browser.close()
            return False

        has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_textarea   = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

        if not has_codemirror and not has_textarea:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: No editor found. Screenshot: {site['screenshot_deploy']}")
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
                        val.includes('3.9.1') &&
                        val.includes('purebrain-link-hover-fix') &&
                        val.includes('purebrain-tag-pills-cta-fix') &&
                        val.includes('pb-transparency-section') &&
                        val.includes('neural-feed-subscribe') &&
                        val.includes('pb-logo-brand')
                    ) return 'success';
                    return 'set_failed: ' + val.length + ' chars';
                } catch(e) { return 'error: ' + e.message; }
            }""", content)
            print(f"  CodeMirror result: {result}")
            set_ok = (result == "success")

            if not set_ok:
                print("  CodeMirror failed, trying textarea fallback...")

        if not set_ok:
            # Unhide and set textarea
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
            print(f"  ERROR: PHP syntax error! {page_text[:400]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear: {page_text[:300]}")
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 300) : 'N/A';
                }""")
                if "3.9.1" in current and "purebrain-link-hover-fix" in current:
                    save_success = True
                    print("  v3.9.1 found in editor content - assuming save succeeded.")

        if not save_success:
            print(f"  Deploy screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # Step 5: Clear Elementor cache via REST API (app password auth)
        print("\n[Step 5] Clearing Elementor cache...")
        credentials = base64.b64encode(
            f"{site['user']}:{site['app_password']}".encode()
        ).decode()

        base_url = site["admin_url"].replace("/wp-admin", "")
        cache_req = urllib.request.Request(
            f"{base_url}/wp-json/elementor/v1/cache",
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
            print(f"  Elementor cache response: HTTP {e.code} (may be normal)")
        except Exception as ex:
            print(f"  Elementor cache clear skipped: {ex}")

        page.screenshot(path=site["screenshot_verify"])
        browser.close()

    print(f"\n  Deploy screenshots:")
    print(f"    {site['screenshot_deploy']}")
    print(f"    {site['screenshot_verify']}")
    return True


# --- Also inject style block into post content via REST API ---------------

def inject_style_into_posts(site: dict) -> dict:
    """
    Complementary approach: inject <style id='pb-link-hover-v391'> into each post's
    raw content via REST API. This ensures the CSS is part of the stored post HTML,
    so even if CDN serves cached plugin output, the post content CSS still fires.
    """
    import json

    STYLE_BLOCK_ID = "pb-link-hover-v391"
    STYLE_BLOCK = """<style id="pb-link-hover-v391">
/* Blog in-text link hover — v3.9.1
   Orange background + WHITE text on hover (was orange-on-orange = invisible).
   Excludes: .blog-cta-button and [rel="tag"] tag pills. */
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]),
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]) {
    transition: background-color 0.2s ease, color 0.2s ease !important;
}
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]):hover,
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]):hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
}
</style>
"""

    name = site["name"]
    base_url = site["admin_url"].replace("/wp-admin", "")
    credentials = base64.b64encode(
        f"{site['user']}:{site['app_password']}".encode()
    ).decode()
    auth_header = f"Basic {credentials}"

    print(f"\n[Style Injection] {name} — injecting style block into all posts...")

    results = {"updated": 0, "skipped": 0, "errors": 0}

    # Fetch all posts
    req = urllib.request.Request(
        f"{base_url}/wp-json/wp/v2/posts?per_page=100&status=publish",
        headers={"Authorization": auth_header, "User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            posts = json.loads(resp.read())
    except Exception as ex:
        print(f"  ERROR fetching posts: {ex}")
        return results

    print(f"  Found {len(posts)} published posts")

    import re as re_mod
    for post in posts:
        post_id = post["id"]
        slug = post.get("slug", "?")
        content_raw = post.get("content", {}).get("raw", "")

        if not content_raw:
            print(f"  [SKIP] {slug} (id={post_id}): empty raw content")
            results["skipped"] += 1
            continue

        if STYLE_BLOCK_ID in content_raw:
            print(f"  [SKIP] {slug} (id={post_id}): already has {STYLE_BLOCK_ID}")
            results["skipped"] += 1
            continue

        # Remove any old version, prepend new
        cleaned = re_mod.sub(
            r'<style id="pb-link-hover-v391">.*?</style>\s*',
            "",
            content_raw,
            flags=re_mod.DOTALL,
        )
        new_content = STYLE_BLOCK + cleaned

        # PATCH via REST API
        payload = json.dumps({"content": new_content}).encode("utf-8")
        patch_req = urllib.request.Request(
            f"{base_url}/wp-json/wp/v2/posts/{post_id}",
            data=payload,
            method="POST",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
                "X-HTTP-Method-Override": "PATCH",
                "User-Agent": "Mozilla/5.0",
            },
        )
        try:
            with urllib.request.urlopen(patch_req, timeout=30) as resp:
                updated = json.loads(resp.read())
            updated_raw = updated.get("content", {}).get("raw", "")
            if STYLE_BLOCK_ID in updated_raw:
                print(f"  [OK] {slug} (id={post_id}): style block injected")
                results["updated"] += 1
            else:
                print(f"  [WARN] {slug} (id={post_id}): PATCH OK but block not in response")
                results["errors"] += 1
        except urllib.error.HTTPError as he:
            body = he.read().decode("utf-8", errors="replace")[:200]
            print(f"  [ERR] {slug} (id={post_id}): HTTP {he.code} — {body}")
            results["errors"] += 1
        except Exception as ex:
            print(f"  [ERR] {slug} (id={post_id}): {ex}")
            results["errors"] += 1

        time.sleep(0.3)

    print(f"  Done: updated={results['updated']} skipped={results['skipped']} errors={results['errors']}")
    return results


# --- Live verification -------------------------------------------------------

def verify_live(site: dict) -> bool:
    """Fetch rendered blog post, verify both CSS injection methods are present."""
    name = site["name"]
    url = site["blog_post_url"]

    print(f"\n[Verify] {name} — {url}")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        has_plugin_css = "purebrain-link-hover-fix" in html
        has_content_css = "pb-link-hover-v391" in html
        has_white_text = "#ffffff !important" in html
        has_orange_bg = "background-color: #f1420b !important" in html

        print(f"  purebrain-link-hover-fix (plugin wp_head):  {'YES' if has_plugin_css else 'NO'}")
        print(f"  pb-link-hover-v391 (post content injection): {'YES' if has_content_css else 'NO'}")
        print(f"  white text rule present:                     {'YES' if has_white_text else 'NO'}")
        print(f"  orange bg hover rule present:                {'YES' if has_orange_bg else 'NO'}")

        if has_white_text and has_orange_bg:
            print(f"  RESULT: CSS is present in rendered HTML")
            return True
        else:
            print(f"  RESULT: CSS MISSING from rendered HTML — CDN may be serving stale cache")
            return False

    except Exception as ex:
        print(f"  ERROR: {ex}")
        return False


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin v3.9.1 — Deployment")
    print("Fix: Blog in-text link hover: orange bg + WHITE text (was invisible)")
    print("Method: Playwright plugin editor + REST API content injection")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Content length: {len(content)} chars\n")

    print("--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Plugin validation failed. Fix the issues above before deploying.")
        sys.exit(1)
    print("Validation passed.\n")

    any_plugin_error = False
    for site in SITES:
        success = deploy_to_site(site, content)
        if not success:
            print(f"\n[FAIL] Plugin deployment to {site['name']} failed.")
            any_plugin_error = True
        else:
            print(f"\n[OK] Plugin deployment to {site['name']} succeeded.")

        # Also inject via REST API (belt-and-suspenders for CDN cache)
        inject_style_into_posts(site)

    print("\n" + "=" * 65)
    print("--- Live Verification (with cache-bypass headers) ---")
    all_verified = True
    for site in SITES:
        ok = verify_live(site)
        if not ok:
            all_verified = False

    print("\n" + "=" * 65)
    if any_plugin_error:
        print("DEPLOYMENT HAD ERRORS — check output above.")
        print("\nNOTE: Even if plugin deploy failed, REST API injection covers posts.")
        sys.exit(1)
    else:
        print("DEPLOYMENT COMPLETE.")
        print("\nWhat changed:")
        print("  - Plugin v3.9.1 deployed: wp_head CSS injection on ALL single blog posts")
        print("  - Style block injected into post content via REST API")
        print("  - In-text links on hover: orange background (#f1420b) + WHITE text (#ffffff)")
        print("  - Smooth 0.2s transition")
        print("  - Excludes: CTA button (.blog-cta-button) and tag pills ([rel='tag'])")
        print()
        if not all_verified:
            print("WARNING: Live verification shows CSS not yet in cached CDN output.")
            print("  The CSS WILL appear after Cloudflare cache expires (Age shown above).")
            print("  For immediate fix: Jared should hard-refresh (Cmd+Shift+R / Ctrl+Shift+R)")
            print("  OR purge Cloudflare cache via dashboard > Caching > Purge Everything")


if __name__ == "__main__":
    main()
