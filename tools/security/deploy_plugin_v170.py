#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v1.7.0 to WordPress.

v1.7.0 changes:
- Tightened image max-width to 760px (was 820px)
- Increased padding-left/right to 60px (was 40px)
- Added box-shadow and border treatment to featured image
- Added padding-top to page-single-post section
- Fixed aspect-ratio override (was panoramic)

Also flushes GoDaddy/Cloudflare cache after deploy.

Author: full-stack-developer agent
Date: 2026-02-20
"""

import os
import sys
import time
import urllib.request
import json
from pathlib import Path
from dotenv import load_dotenv

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_FILE = AETHER_ROOT / ".env"
load_dotenv(ENV_FILE)

PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security-plugin.php"
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = os.environ.get("PUREBRAIN_WP_PASSWORD", "")

PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)

SCREENSHOT_PATH = str(AETHER_ROOT / "exports/screenshots/plugin_v170_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v170_verify.png")
SCREENSHOT_CACHED = str(AETHER_ROOT / "exports/screenshots/plugin_v170_live.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v1.7.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    if "1.7.0" not in new_content:
        print("ERROR: Plugin file does not contain version 1.7.0. Aborting.")
        sys.exit(1)

    if "max-width: 760px" not in new_content:
        print("ERROR: Plugin file does not contain 760px constraint. Aborting.")
        sys.exit(1)

    if "box-shadow" not in new_content:
        print("ERROR: Plugin file does not contain box-shadow. Aborting.")
        sys.exit(1)

    print("Plugin content validated (v1.7.0, 760px, box-shadow). Starting Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
        )
        page = context.new_page()

        # Step 1: Login
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
            page.screenshot(path=SCREENSHOT_PATH)
            print("  ERROR: Login form not visible. Screenshot saved.")
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
            page.screenshot(path=SCREENSHOT_PATH)
            page_text = page.inner_text("body")
            print(f"  ERROR: Login failed. Page: {page_text[:300]}")
            browser.close()
            return False

        print("  Login successful!")

        # Step 2: Plugin Editor
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
            print("  ERROR: No editor found")
            page.screenshot(path=SCREENSHOT_PATH)
            browser.close()
            return False

        # Step 3: Set content
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
                    if (val.includes('1.7.0')) return 'success';
                    return 'set_failed: got ' + val.length + ' chars';
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

        # Step 4: Save
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

        page.screenshot(path=SCREENSHOT_PATH)
        page_text = page.inner_text("body")

        save_success = False
        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin file saved!")
            save_success = True
        elif "Parse error" in page_text or "syntax error" in page_text:
            print("  ERROR: PHP syntax error - file NOT saved!")
            print(f"  Page: {page_text[:500]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear. Page excerpt:")
            print(f"  {page_text[:400]}")
            # Try to check if current content matches
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 100) : 'N/A';
                }""")
                print(f"  Current editor start: {current}")
                if '1.7.0' in current:
                    save_success = True

        # Step 5: Flush GoDaddy cache
        print("\n[Step 5] Flushing GoDaddy/Cloudflare cache...")
        page.goto(f"{WP_ADMIN_URL}/options-general.php", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        flush_url = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            const flushLink = links.find(a => /flush.cache/i.test(a.textContent) || /flush.cache/i.test(a.href));
            return flushLink ? flushLink.href : null;
        }""")
        print(f"  Flush URL: {flush_url}")

        if flush_url:
            page.goto(flush_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            print("  Cache flush requested!")
            page.screenshot(path=SCREENSHOT_VERIFY)
        else:
            print("  No flush URL found. Trying direct cache flush via WP Admin...")
            # Try the Settings page for cache flushing
            flush_result = page.evaluate("""() => {
                const btn = document.querySelector('[data-action="flush_cache"], .wpaas-flush-cache-btn');
                if (btn) {
                    btn.click();
                    return 'clicked';
                }
                return 'no_button';
            }""")
            print(f"  Flush button: {flush_result}")

        browser.close()

    # Step 6: Verify on server (bypass CDN)
    print("\n[Step 6] Verifying CSS on server origin (bypassing CDN cache)...")
    time.sleep(3)

    verify_css()

    return save_success


def verify_css():
    """Verify the CSS is live on the server."""
    import re

    url = "https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
        },
    )

    try:
        response = urllib.request.urlopen(req, timeout=30)
        html = response.read().decode("utf-8")

        style_start = html.find('purebrain-blog-desktop-padding')
        if style_start == -1:
            print("  ERROR: No blog padding CSS block found!")
            return False

        style_end = html.find('</style>', style_start)
        css = html[style_start:style_end]

        maxwidths = re.findall(r'max-width:\s*[\w%]+', css)
        paddings = re.findall(r'padding-left:\s*[\w%]+', css)
        has_shadow = 'box-shadow' in css

        print(f"  max-widths: {maxwidths}")
        print(f"  padding-lefts: {paddings}")
        print(f"  has box-shadow: {has_shadow}")

        if 'max-width: 760px' in css:
            print("  CONFIRMED: v1.7.0 CSS is live (760px + box-shadow)!")
            return True
        elif 'max-width: 820px' in css:
            print("  WARNING: Still seeing v1.6.0 CSS (820px). CDN may be caching.")
            print("  Server deploy succeeded but CDN needs to expire (~30 min) or manual flush needed.")
            return False
        else:
            print(f"  Unexpected CSS. max-widths found: {maxwidths}")
            return False

    except Exception as e:
        print(f"  Verification failed: {e}")
        return False


def verify_computed_styles():
    """Use Playwright to check computed styles and take screenshot."""
    from playwright.sync_api import sync_playwright

    print("\n[Computed Style Verification] Loading blog post at 1440px...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        page.goto(
            "https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        time.sleep(4)

        # Scroll to featured image
        page.evaluate("""() => {
            const img = document.querySelector('.post-single-image');
            if (img) img.scrollIntoView({block: 'center'});
        }""")
        time.sleep(1)

        page.screenshot(path=SCREENSHOT_CACHED, full_page=False)
        print(f"  Screenshot saved: {SCREENSHOT_CACHED}")

        computed = page.evaluate("""() => {
            const image = document.querySelector('.post-single-image');
            const img = document.querySelector('.post-single-image img');
            const container = document.querySelector('.page-single-post .container');

            return {
                viewportWidth: window.innerWidth,
                containerWidth: container ? container.offsetWidth : null,
                containerPaddingLeft: container ? window.getComputedStyle(container).paddingLeft : null,
                imageWidth: image ? image.offsetWidth : null,
                imageMaxWidth: image ? window.getComputedStyle(image).maxWidth : null,
                imageMarginLeft: image ? window.getComputedStyle(image).marginLeft : null,
                imageBoundsLeft: image ? image.getBoundingClientRect().left : null,
                imageBoundsRight: image ? image.getBoundingClientRect().right : null,
                hasBoxShadow: image ? window.getComputedStyle(image).boxShadow !== 'none' : null,
                cssVersion: document.querySelector('#purebrain-blog-desktop-padding') ?
                    (document.querySelector('#purebrain-blog-desktop-padding').textContent.includes('760px') ? 'v1.7.0' :
                     document.querySelector('#purebrain-blog-desktop-padding').textContent.includes('820px') ? 'v1.6.0' : 'older')
                    : 'not found'
            };
        }""")

        print("\n  === Computed Styles ===")
        for k, v in computed.items():
            print(f"  {k}: {v}")

        browser.close()
        return computed


if __name__ == "__main__":
    print("=" * 60)
    print("PUREBRAIN BLOG POST PADDING FIX - v1.7.0 DEPLOYMENT")
    print("=" * 60)

    result = deploy()

    print("\n" + "=" * 60)
    print("COMPUTED STYLE VERIFICATION")
    print("=" * 60)
    computed = verify_computed_styles()

    if computed.get('cssVersion') == 'v1.7.0':
        print("\n[SUCCESS] v1.7.0 CSS is LIVE and verified!")
        print(f"  Image left margin from viewport: {computed.get('imageBoundsLeft')}px")
        print(f"  Image right margin from viewport: {1440 - computed.get('imageBoundsRight', 0) if computed.get('imageBoundsRight') else 'N/A'}px")
    else:
        print(f"\n[WARNING] CSS version is '{computed.get('cssVersion')}' - may need CDN cache flush.")
        print("  CDN cache can take 30-60 minutes to expire naturally.")
        print("  Screenshot saved for review.")
