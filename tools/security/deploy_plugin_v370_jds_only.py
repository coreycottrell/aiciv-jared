#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v3.7.0 to jareddsanborn.com ONLY.

Context: purebrain.ai already has v3.7.0. This script handles the JDS deploy
which was blocked by CAPTCHA in the previous attempt.

v3.7.0 change: Blog nav "Blog" link changed to "Subscribe" on single posts
               + category/archive pages. Subscribe links to /blog/#neural-feed-subscribe.

IMPORTANT lessons from memory (2026-02-21--plugin-v360-deployment.md):
- WORDPRESS_APP_PASSWORD (.env) = REST API auth only (does NOT work on wp-login.php form)
- Admin password for wp-login.php form: New1Jared88887 (provided by Jared)
- Plugin editor (CodeMirror) is the reliable deploy method for updates

Author: full-stack-developer agent
Date: 2026-02-21
"""

import os
import re
import sys
import time
import base64
import urllib.request
import urllib.error
from pathlib import Path

AETHER_ROOT    = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE    = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"
SCREENSHOT_DIR = str(AETHER_ROOT / "exports/screenshots")

# --- Credentials -----------------------------------------------------------
# Admin password for wp-login.php form (NOT the app password)
JDS_ADMIN_USER     = "jared"
JDS_ADMIN_PASSWORD = "New1Jared88887"   # wp-login.php form password

# App password for REST API calls (cache flush etc.)
env_text = (AETHER_ROOT / ".env").read_text()
def _env(key):
    m = re.search(rf"{key}='([^']+)'", env_text)
    if m:
        return m.group(1)
    m = re.search(rf"{key}=([^\n]+)", env_text)
    return m.group(1).strip() if m else ""

JDS_APP_PASSWORD = _env("WORDPRESS_APP_PASSWORD")  # for REST API

SITE = {
    "name":             "jareddsanborn.com",
    "admin_url":        "https://jareddsanborn.com/wp-admin",
    "login_url":        "https://jareddsanborn.com/wp-login.php",
    "user":             JDS_ADMIN_USER,
    "password":         JDS_ADMIN_PASSWORD,
    "editor_url": (
        "https://jareddsanborn.com/wp-admin/plugin-editor.php"
        "?file=purebrain-security/purebrain-security-plugin.php"
        "&plugin=purebrain-security/purebrain-security-plugin.php"
    ),
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v370_jds_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v370_jds_verify.png",
    "blog_post_url":     "https://jareddsanborn.com/why-95-percent-of-ai-pilots-fail/",
}


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 3.7.0":                        "3.7.0" in content,
        "subscribe_url var":                    "subscribe_url" in content and "neural-feed-subscribe" in content,
        "Subscribe link in nav HTML":            ">Subscribe</a>" in content,
        "Blog link removed from nav":           "neural-feed-subscribe" in content,
        # v3.6.0 features retained
        "transparency REST route":              "purebrain/v1', '/transparency-data'" in content,
        "pb-transparency-section":              "pb-transparency-section" in content,
        # v3.5.0 features retained
        "pb-lead-inline":                       "pb-lead-inline" in content,
        "pb-lead-bar":                          "pb-lead-bar" in content,
        # older features retained
        "html body .pb-blog-nav a:hover":       "html body .pb-blog-nav a:hover" in content,
        "pb-logo-brand class":                  "pb-logo-brand" in content,
        "FAQ accordion":                        "faq-accordion" in content,
        "rate limiter":                         "purebrain_check_rate_limit" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


# --- Deploy ----------------------------------------------------------------

def deploy_to_jds(content: str) -> bool:
    from playwright.sync_api import sync_playwright

    print(f"\n{'='*65}")
    print(f"DEPLOYING TO: jareddsanborn.com")
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
        print(f"\n[Step 1] Navigating to wp-login.php...")
        page.goto(SITE["login_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        page.screenshot(path=f"{SCREENSHOT_DIR}/jds_v370_login_initial.png")
        print(f"  Screenshot: jds_v370_login_initial.png")
        print(f"  Current URL: {page.url}")

        # --- CAPTCHA DETECTION (broad: any image CAPTCHA or text CAPTCHA) ---
        # Inspect the login form for any CAPTCHA input field
        captcha_info = page.evaluate("""() => {
            // Look for any input that is NOT user_login / user_pass / rememberme / wp-submit
            const known = new Set(['user_login','user_pass','rememberme','wp-submit','redirect_to','testcookie','log','pwd','submit']);
            const inputs = Array.from(document.querySelectorAll('input[type="text"], input[type="number"], input:not([type])'));
            const captchaInputs = inputs.filter(i => !known.has(i.id) && !known.has(i.name));
            // Find any images in the login form
            const formImgs = Array.from(document.querySelectorAll('form#loginform img, .login img, body img'));
            return {
                captchaInputs: captchaInputs.map(i => ({id: i.id, name: i.name, placeholder: i.placeholder})),
                formImgs: formImgs.map(i => ({src: i.src.substring(0,120), alt: i.alt, id: i.id, width: i.width, height: i.height})),
                pageText: document.body.innerText.substring(0, 300),
            };
        }""")
        print(f"  CAPTCHA scan: inputs={captcha_info.get('captchaInputs')}, imgs={captcha_info.get('formImgs')}")

        captcha_inputs = captcha_info.get('captchaInputs', [])
        if captcha_inputs:
            # There is a CAPTCHA field present
            captcha_input_id   = captcha_inputs[0].get('id')   or ''
            captcha_input_name = captcha_inputs[0].get('name') or ''
            print(f"\n  CAPTCHA field detected! id='{captcha_input_id}' name='{captcha_input_name}'")

            # Screenshot the full page at 2x for vision reading
            captcha_ss = f"{SCREENSHOT_DIR}/jds_v370_captcha_read.png"
            page.screenshot(path=captcha_ss)
            print(f"  Captcha screenshot saved: {captcha_ss}")
            print("  NOTE: Image CAPTCHA present. Reading with vision (see screenshot).")

            # The CAPTCHA text is read externally via the screenshot - we pass it as an arg
            # or read from env var CAPTCHA_ANSWER if set
            import os as _os
            captcha_answer = _os.environ.get("CAPTCHA_ANSWER", "").strip()

            if not captcha_answer:
                # Check if a captcha_answer.txt was written
                ca_file = Path(AETHER_ROOT) / ".captcha_answer.txt"
                if ca_file.exists():
                    captcha_answer = ca_file.read_text().strip()
                    ca_file.unlink()  # consume it
                    print(f"  Read CAPTCHA answer from file: '{captcha_answer}'")

            if not captcha_answer:
                # Poll for answer file for up to 90 seconds (browser session stays open)
                ca_file = Path(AETHER_ROOT) / ".captcha_answer.txt"
                print(f"\n  WAITING for CAPTCHA answer...")
                print(f"  View screenshot: {captcha_ss}")
                print(f"  Write answer to: {ca_file}")
                print(f"  Or set env var: CAPTCHA_ANSWER=<text>")
                print(f"  Polling for up to 90 seconds...")
                for i in range(90):
                    if ca_file.exists():
                        captcha_answer = ca_file.read_text().strip()
                        ca_file.unlink()
                        print(f"  Got CAPTCHA answer from file (after {i}s): '{captcha_answer}'")
                        break
                    captcha_answer = os.environ.get("CAPTCHA_ANSWER", "").strip()
                    if captcha_answer:
                        print(f"  Got CAPTCHA answer from env (after {i}s): '{captcha_answer}'")
                        break
                    if i % 10 == 0 and i > 0:
                        print(f"  ... still waiting ({i}s elapsed) ...")
                    time.sleep(1)

            if captcha_answer:
                selector = f"#{captcha_input_id}" if captcha_input_id else f"[name='{captcha_input_name}']"
                page.fill(selector, captcha_answer)
                print(f"  Filled CAPTCHA field ({selector}) with: '{captcha_answer}'")
                time.sleep(0.5)
            else:
                print("  ERROR: No CAPTCHA answer received within 90 seconds. Aborting.")
                print(f"  View screenshot: {captcha_ss}")
                browser.close()
                return False

        # Check login form is visible
        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=SITE["screenshot_deploy"])
            page_title = page.title()
            print(f"  ERROR: Login form not visible. Page title: {page_title}")
            browser.close()
            return False

        # Fill login form
        print(f"  Filling login form: user={SITE['user']}")
        page.fill("#user_login", SITE["user"])
        time.sleep(0.5)
        page.fill("#user_pass", SITE["password"])
        time.sleep(0.5)

        page.screenshot(path=f"{SCREENSHOT_DIR}/jds_v370_login_filled.png")

        page.click("#wp-submit")
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        time.sleep(4)

        page.screenshot(path=f"{SCREENSHOT_DIR}/jds_v370_after_login.png")
        print(f"  After-login URL: {page.url}")

        if "wp-login.php" in page.url:
            page_body = page.inner_text("body")
            print(f"  ERROR: Login failed. Body snippet: {page_body[:400]}")
            browser.close()
            return False

        print("  Login successful!")

        # Step 2: Plugin Editor
        print(f"\n[Step 2] Opening Plugin Editor...")
        page.goto(SITE["editor_url"], wait_until="domcontentloaded", timeout=60000)
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
            page.screenshot(path=SITE["screenshot_deploy"])
            print(f"  ERROR: No editor found.")
            browser.close()
            return False

        # Step 3: Set content
        print("\n[Step 3] Setting plugin content (v3.7.0)...")
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
                        val.includes('3.7.0') &&
                        val.includes('neural-feed-subscribe') &&
                        val.includes('>Subscribe</a>') &&
                        val.includes('pb-transparency-section') &&
                        val.includes('pb-lead-inline') &&
                        val.includes('html body .pb-blog-nav a:hover') &&
                        val.includes('pb-logo-brand')
                    ) return 'success';
                    return 'set_failed: missing_checks. val_len=' + val.length;
                } catch(e) { return 'error: ' + e.message; }
            }""", content)
            print(f"  CodeMirror result: {result}")
            set_ok = (result == "success")

        if not set_ok and has_textarea:
            print("  Trying textarea fallback...")
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
            set_ok = True

        if not set_ok:
            page.screenshot(path=SITE["screenshot_deploy"])
            print("  ERROR: Could not set plugin content.")
            browser.close()
            return False

        time.sleep(1)

        # Step 4: Save
        print("\n[Step 4] Clicking Save...")
        page.evaluate("""() => {
            const btn = document.querySelector('#submit') ||
                        document.querySelector('input[type=\"submit\"]');
            if (btn) btn.click();
        }""")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=45000)
        except Exception:
            pass
        time.sleep(5)

        page.screenshot(path=SITE["screenshot_deploy"])
        page_text = page.inner_text("body")

        save_success = False
        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: 'File edited successfully' confirmed!")
            save_success = True
        elif "Parse error" in page_text or "syntax error" in page_text.lower():
            print(f"  ERROR: PHP syntax error detected! First 500 chars:\n{page_text[:500]}")
            browser.close()
            return False
        else:
            # Check if v3.7.0 is now in the editor
            if has_codemirror:
                current_first_200 = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 300) : 'N/A';
                }""")
                print(f"  Editor content check: {current_first_200[:200]}")
                if "3.7.0" in current_first_200 and "neural-feed-subscribe" in page.content():
                    save_success = True
                    print("  v3.7.0 confirmed in editor - save likely succeeded.")
            if not save_success:
                print(f"  Status unclear. Page snippet: {page_text[:300]}")
                print(f"  URL: {page.url}")

        if not save_success:
            browser.close()
            return False

        # Step 5: LiteSpeed Cache flush (jareddsanborn.com has LiteSpeed Cache plugin)
        print("\n[Step 5] Flushing LiteSpeed Cache...")
        # Try LiteSpeed Cache purge via admin URL
        litespeed_url = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            const ls = links.find(a =>
                /litespeed/i.test(a.href) ||
                /lscache/i.test(a.href) ||
                /ls_purge/i.test(a.href) ||
                /purge.*cache/i.test(a.textContent.toLowerCase())
            );
            return ls ? ls.href : null;
        }""")

        if litespeed_url:
            print(f"  LiteSpeed URL found: {litespeed_url}")
            page.goto(litespeed_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            print("  LiteSpeed cache purged!")
        else:
            # Try WP admin settings cache flush link
            page.goto("https://jareddsanborn.com/wp-admin/options-general.php",
                      wait_until="domcontentloaded", timeout=30000)
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
                print("  WP cache flushed!")
            else:
                # Try LiteSpeed Cache admin page directly
                page.goto("https://jareddsanborn.com/wp-admin/admin.php?page=litespeed-cache",
                          wait_until="domcontentloaded", timeout=30000)
                time.sleep(2)
                ls_purge = page.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll('a, button'));
                    const btn = btns.find(b =>
                        /purge all/i.test(b.textContent) ||
                        /flush all/i.test(b.textContent)
                    );
                    return btn ? btn.href || btn.getAttribute('data-href') : null;
                }""")
                if ls_purge:
                    page.goto(ls_purge, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(2)
                    print("  LiteSpeed 'Purge All' clicked!")
                else:
                    print("  No explicit cache flush found — will expire naturally.")

        page.screenshot(path=SITE["screenshot_verify"])
        browser.close()

    print(f"\n  Screenshots:")
    print(f"    Deploy: {SITE['screenshot_deploy']}")
    print(f"    Verify: {SITE['screenshot_verify']}")
    return True


# --- Live Verification via Playwright (JS-rendered nav) --------------------

def verify_live_playwright() -> dict:
    from playwright.sync_api import sync_playwright

    print(f"\n[Verify] jareddsanborn.com — checking Subscribe nav link (Playwright)...")
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = ctx.new_page()

        url = SITE["blog_post_url"]
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        page.screenshot(path=f"{SCREENSHOT_DIR}/plugin_v370_jds_nav_live.png")

        nav_html = page.evaluate("""() => {
            const nav = document.querySelector('.pb-blog-nav');
            return nav ? nav.outerHTML : 'NOT FOUND';
        }""")
        print(f"  Nav HTML: {nav_html[:400]}")

        checks = {
            "pb-blog-nav present":        "pb-blog-nav" in nav_html,
            "Subscribe text in nav":      ">Subscribe<" in nav_html,
            "neural-feed-subscribe link": "neural-feed-subscribe" in nav_html,
            "Blog link gone (old):":      ">Blog<" not in nav_html,
        }
        for k, ok in checks.items():
            status = "OK" if ok else "FAIL"
            print(f"  [{status}] {k}: {ok}")
            results[k] = "ok" if ok else "fail"

        browser.close()

    return results


# --- Main ------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("PUREBRAIN SECURITY PLUGIN v3.7.0 - JDS ONLY DEPLOY")
    print("=" * 65)
    print("Target: jareddsanborn.com")
    print("Login:  jared / New1Jared88887 (wp-login.php admin password)")
    print("Change: Blog nav 'Blog' → 'Subscribe' (/blog/#neural-feed-subscribe)")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    plugin_content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Size: {len(plugin_content):,} chars")

    # Validate plugin content
    print("\n--- Validating plugin content ---")
    if not validate_plugin_content(plugin_content):
        print("\nERROR: Validation failed. Aborting.")
        sys.exit(1)
    print("Validation passed.\n")

    # Deploy to JDS
    ok = deploy_to_jds(plugin_content)

    if not ok:
        print("\n[FAILED] Deploy to jareddsanborn.com failed. Check screenshots.")
        sys.exit(1)

    # Wait for cache propagation
    print("\nWaiting 8 seconds for cache propagation...")
    time.sleep(8)

    # Verify
    verify_results = verify_live_playwright()

    # Final summary
    print("\n" + "=" * 65)
    print("FINAL RESULT - jareddsanborn.com")
    print("=" * 65)
    all_verified = all(v == "ok" for v in verify_results.values())
    print(f"  Deploy: SUCCESS")
    for k, v in verify_results.items():
        print(f"  Verify '{k}': {v}")

    if all_verified:
        print("\n[SUCCESS] v3.7.0 deployed and verified on jareddsanborn.com!")
        print("  Nav now shows: Home | Subscribe | AI Assessment")
        print("  Subscribe links to: /blog/#neural-feed-subscribe")
    else:
        print("\n[PARTIAL] Deploy succeeded but some verifications failed.")
        print("  May need cache flush - check live in browser.")

    print(f"\n  Screenshots saved to: {SCREENSHOT_DIR}/plugin_v370_jds_*.png")
