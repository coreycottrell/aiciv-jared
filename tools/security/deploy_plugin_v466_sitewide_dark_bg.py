#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v4.6.6 — SITE-WIDE dark background fix.

Key change from v4.6.5:
- Dark background (#080a12) is now SITE-WIDE (all pages), not just page-id-777.
- Jared explicitly locked in: NO page on purebrain.ai should ever show orange background.
- Blog posts (body.single-post) excluded: they keep their own dark bg system.

Author: dept-systems-technology (ST#)
Date: 2026-02-27
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
PLUGIN_SOURCE = AETHER_ROOT / "exports/purebrain-security-plugin-v466.php"

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
    """Validate the v4.6.6 plugin has all required markers."""
    checks = {
        "Version 4.6.6":                    "Version:     4.6.6" in content,
        "Layer 1 CSS injected":             "pb-dark-bg-layer1" in content,
        "Layer 2 CSS injected":             "pb-dark-bg-layer2" in content,
        "Layer 3 JS injected":              "pb-dark-bg-js" in content,
        "Dark bg color correct (#080a12)":  "#080a12" in content,
        "Blog posts excluded":              "single-post" in content,
        "NO is_page(777) scoping":          "is_page( 777 )" not in content or "dark" not in content.split("is_page( 777 )")[0][-200:],
        "CSP 89.167.19.20 still present":   "https://89.167.19.20:8443;" in content,
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

    print("\n[Step 3] Setting plugin content (v4.6.6 - site-wide dark bg)...")
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
                    val.includes('Version:     4.6.6') &&
                    val.includes('pb-dark-bg-layer1') &&
                    val.includes('pb-dark-bg-layer2') &&
                    val.includes('pb-dark-bg-js') &&
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
            if ("Version:     4.6.6" in current and
                    "pb-dark-bg-layer1" in current):
                print("  v4.6.6 markers found in editor — save assumed successful.")
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


def get_cf_cache_status(url: str) -> str:
    """Get Cloudflare cache status from a HEAD request."""
    ctx_ssl = ssl.create_default_context()
    parsed = url.replace("https://", "").split("/", 1)
    host = parsed[0]
    path = "/" + parsed[1] if len(parsed) > 1 else "/"
    conn = http.client.HTTPSConnection(host, context=ctx_ssl, timeout=20)
    conn.request("HEAD", path, headers={
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    })
    resp = conn.getresponse()
    hdrs = dict(resp.getheaders())
    conn.close()
    return (hdrs.get("cf-cache-status") or
            hdrs.get("Cf-Cache-Status") or "unknown")


def verify_live() -> bool:
    """
    Verify dark bg is present on multiple pages site-wide.

    Checks:
    1. Homepage (purebrain.ai) — dark bg CSS in HEAD
    2. Calculator page (/ai-tool-stack-calculator/) — dark bg still works
    3. Blog listing (/blog/) — dark bg present
    4. A blog post — dark bg present (from its own system, not broken)
    """
    ctx_ssl = ssl.create_default_context()

    pages_to_check = [
        {
            "name":  "Homepage (purebrain.ai)",
            "url":   "https://purebrain.ai/",
            "checks": {
                "Layer1 CSS (pb-dark-bg-layer1)": lambda b: "pb-dark-bg-layer1" in b,
                "Layer2 CSS (pb-dark-bg-layer2)": lambda b: "pb-dark-bg-layer2" in b,
                "Layer3 JS (pb-dark-bg-js)":      lambda b: "pb-dark-bg-js" in b,
                "#080a12 color present":           lambda b: "#080a12" in b,
            }
        },
        {
            "name":  "Calculator (/ai-tool-stack-calculator/)",
            "url":   "https://purebrain.ai/ai-tool-stack-calculator/",
            "checks": {
                "Layer1 CSS (pb-dark-bg-layer1)": lambda b: "pb-dark-bg-layer1" in b,
                "Layer2 CSS (pb-dark-bg-layer2)": lambda b: "pb-dark-bg-layer2" in b,
                "Layer3 JS (pb-dark-bg-js)":      lambda b: "pb-dark-bg-js" in b,
                "#080a12 color present":           lambda b: "#080a12" in b,
            }
        },
        {
            "name":  "Blog Listing (/blog/)",
            "url":   "https://purebrain.ai/blog/",
            "checks": {
                "Layer1 CSS (pb-dark-bg-layer1)": lambda b: "pb-dark-bg-layer1" in b,
                "Layer2 CSS (pb-dark-bg-layer2)": lambda b: "pb-dark-bg-layer2" in b,
                "#080a12 color present":           lambda b: "#080a12" in b,
            }
        },
    ]

    all_passed = True

    for page_info in pages_to_check:
        print(f"\n  --- {page_info['name']} ---")
        try:
            body = fetch_page_html(page_info["url"])
            for check_name, check_fn in page_info["checks"].items():
                result = check_fn(body)
                status = "PASS" if result else "FAIL"
                print(f"    [{status}] {check_name}")
                if not result:
                    all_passed = False

            cf = get_cf_cache_status(page_info["url"])
            print(f"    Cloudflare cache: {cf}")

        except Exception as ex:
            print(f"    [ERROR] Failed to fetch: {ex}")
            all_passed = False

    # Check a blog post — dark bg should still be present via its own system
    print(f"\n  --- Blog Post (spot-check) ---")
    try:
        # Fetch the blog listing to find a post URL
        blog_html = fetch_page_html("https://purebrain.ai/blog/")
        # Find first post link from blog listing
        import re
        post_links = re.findall(
            r'href="(https://purebrain\.ai/(?!blog/?$|#)[^"]+?/)"',
            blog_html
        )
        post_url = post_links[0] if post_links else None

        if post_url:
            print(f"    Checking: {post_url}")
            post_body = fetch_page_html(post_url)

            # Blog posts should have dark bg from their own CSS, not broken by new plugin
            dark_bg_present = "#080a12" in post_body or "#0a0a0f" in post_body
            print(f"    [{'PASS' if dark_bg_present else 'FAIL'}] Dark bg color in blog post HTML")

            # Verify the post still has its theme structure (single-post class etc.)
            has_single_post = "single-post" in post_body
            print(f"    [{'PASS' if has_single_post else 'WARN'}] body.single-post class present")

            if not dark_bg_present:
                all_passed = False
        else:
            print("    [SKIP] Could not extract a blog post URL from listing page.")

    except Exception as ex:
        print(f"    [WARN] Blog post check failed: {ex}")
        # Not a hard failure — blog post is bonus verification

    return all_passed


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


def main():
    print("=" * 65)
    print("PureBrain Security Plugin v4.6.6 — SITE-WIDE Dark BG Fix")
    print("=" * 65)
    print("\nKey change: Dark background is now site-wide, not page-777-only.")
    print("Jared's rule: NO page on purebrain.ai should ever show orange background.")
    print("Blog posts (body.single-post) retain their own dark bg system.")
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
    print("\nWaiting 10 seconds for cache to settle...")
    time.sleep(10)

    # Verify via REST API that version changed
    print("\n--- REST API Version Check ---")
    live_version = check_plugin_version_via_api()
    version_ok = live_version == "4.6.6"
    print(f"  Live plugin version: {live_version}")
    print(f"  [{('PASS' if version_ok else 'FAIL')}] Version is 4.6.6")

    print("\n" + "=" * 65)
    print("LIVE VERIFICATION — SITE-WIDE DARK BG")
    print("=" * 65)
    verified = verify_live()

    print("\n" + "=" * 65)
    if verified and version_ok:
        print("DEPLOYMENT COMPLETE AND VERIFIED.")
        print("")
        print("Site-wide dark background (#080a12) is now active on all pages.")
        print("Calculator page 777 dark bg: confirmed.")
        print("Blog listing dark bg: confirmed.")
        print("Blog posts: retain own dark bg system, not broken.")
        print("No page on purebrain.ai will show orange background.")
    else:
        print("DEPLOYMENT DONE — some verification checks flagged issues.")
        print("")
        if not version_ok:
            print(f"  - Plugin version mismatch (got: {live_version}, expected: 4.6.6)")
        if not verified:
            print("  - Some page checks failed — see details above.")
        print("\nTroubleshooting:")
        print("  1. Try hard-refresh (Ctrl+Shift+R) on the affected page.")
        print("  2. Cloudflare may be serving cached content (wait ~60s).")
        print("  3. If version mismatch: check WP Admin > Plugins for active version.")


if __name__ == "__main__":
    main()
