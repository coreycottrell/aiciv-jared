#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v1.9.0 to WordPress.

v1.9.0 changes:
- Fixed bottom-clipping bug on blog post featured images on desktop/tablet.
- Root cause: Artistics theme forces aspect-ratio: 1/0.50 on BOTH
  .post-single-image figure AND img - constraining container height to
  50% of width, then object-fit: cover crops from center, cutting off
  bottom text in banners (e.g. "THE DIFFERENCE" / CTA text).
- Fix: Override aspect-ratio to auto on BOTH figure AND img so image
  displays at its natural dimensions. object-fit changed to fill so
  nothing is cropped. overflow on wrapper changed from hidden to visible
  to ensure full image is visible.
- Mobile (<768px) is completely untouched.

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

SCREENSHOT_PATH = str(AETHER_ROOT / "exports/screenshots/plugin_v190_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v190_verify.png")
SCREENSHOT_DESKTOP = str(AETHER_ROOT / "exports/screenshots/plugin_v190_desktop.png")
SCREENSHOT_TABLET = str(AETHER_ROOT / "exports/screenshots/plugin_v190_tablet.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v1.9.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")
    print("Fix: Featured image bottom clipping on desktop/tablet")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    # Validate the fix is in the file
    if "1.9.0" not in new_content:
        print("ERROR: Plugin file does not contain version 1.9.0. Aborting.")
        sys.exit(1)

    if "aspect-ratio: auto !important" not in new_content:
        print("ERROR: Plugin file does not contain aspect-ratio: auto fix. Aborting.")
        sys.exit(1)

    if "object-fit: fill !important" not in new_content:
        print("ERROR: Plugin file does not contain object-fit: fill fix. Aborting.")
        sys.exit(1)

    print("Plugin content validated (v1.9.0, aspect-ratio fix, object-fit: fill). Starting Playwright...")

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
                    if (val.includes('1.9.0')) return 'success';
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
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 100) : 'N/A';
                }""")
                print(f"  Current editor start: {current}")
                if '1.9.0' in current:
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
            print("  No flush URL found. Cache will expire naturally.")

        browser.close()

    return save_success


def verify_css():
    """Verify the CSS fix is live on the server."""
    print("\n[Verification] Checking CSS on server...")

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

        has_aspect_ratio_auto = 'aspect-ratio: auto !important' in css
        has_object_fit_fill = 'object-fit: fill !important' in css
        has_figure_fix = 'post-single-image figure' in css
        is_v190 = '1.9.0' in css or ('aspect-ratio: auto' in css and 'object-fit: fill' in css)

        print(f"  aspect-ratio: auto override: {has_aspect_ratio_auto}")
        print(f"  object-fit: fill override: {has_object_fit_fill}")
        print(f"  figure rule present: {has_figure_fix}")
        print(f"  v1.9.0 fix confirmed: {is_v190}")

        if has_aspect_ratio_auto and has_object_fit_fill:
            print("  CONFIRMED: v1.9.0 bottom-clipping fix is LIVE!")
            return True
        else:
            print("  WARNING: Fix not detected yet. CDN may still be serving cached version.")
            return False

    except Exception as e:
        print(f"  Verification failed: {e}")
        return False


def verify_computed_styles():
    """Use Playwright to check computed styles at desktop and tablet breakpoints."""
    from playwright.sync_api import sync_playwright

    print("\n[Visual Verification] Taking screenshots at desktop + tablet...")
    blog_url = "https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/"

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for viewport_name, width, height in [("desktop_1440", 1440, 900), ("tablet_1024", 1024, 900)]:
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()

            page.goto(blog_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)

            # Scroll to featured image
            page.evaluate("""() => {
                const img = document.querySelector('.post-single-image');
                if (img) img.scrollIntoView({block: 'center'});
            }""")
            time.sleep(1)

            screenshot_path = SCREENSHOT_DESKTOP if "1440" in viewport_name else SCREENSHOT_TABLET
            page.screenshot(path=screenshot_path, full_page=False)
            print(f"  Screenshot ({viewport_name}): {screenshot_path}")

            computed = page.evaluate("""() => {
                const wrapper = document.querySelector('.post-single-image');
                const figure = document.querySelector('.post-single-image figure');
                const img = document.querySelector('.post-single-image img');

                const getStyle = (el, prop) => el ? window.getComputedStyle(el)[prop] : 'N/A';
                const getRect = (el) => el ? el.getBoundingClientRect() : null;

                const wrapperRect = getRect(wrapper);
                const imgRect = getRect(img);

                return {
                    viewport: window.innerWidth,
                    // Wrapper
                    wrapperMaxWidth: getStyle(wrapper, 'maxWidth'),
                    wrapperOverflow: getStyle(wrapper, 'overflow'),
                    wrapperHeight: wrapper ? wrapper.offsetHeight : 'N/A',
                    // Figure
                    figureAspectRatio: getStyle(figure, 'aspectRatio'),
                    figureHeight: figure ? figure.offsetHeight : 'N/A',
                    figureOverflow: getStyle(figure, 'overflow'),
                    // Image
                    imgAspectRatio: getStyle(img, 'aspectRatio'),
                    imgObjectFit: getStyle(img, 'objectFit'),
                    imgNaturalWidth: img ? img.naturalWidth : 'N/A',
                    imgNaturalHeight: img ? img.naturalHeight : 'N/A',
                    imgRenderedHeight: img ? img.offsetHeight : 'N/A',
                    // Is full banner visible?
                    imgBottomFromViewport: imgRect ? (window.innerHeight - imgRect.bottom) : 'N/A',
                    cssVersion: document.querySelector('#purebrain-blog-desktop-padding') ?
                        (document.querySelector('#purebrain-blog-desktop-padding').textContent.includes('object-fit: fill') ? 'v1.9.0' : 'older')
                        : 'not found'
                };
            }""")

            results[viewport_name] = computed
            print(f"\n  === {viewport_name} Computed Styles ===")
            for k, v in computed.items():
                print(f"  {k}: {v}")

            context.close()

        browser.close()

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("PUREBRAIN BLOG POST BANNER CLIPPING FIX - v1.9.0 DEPLOYMENT")
    print("Fix: aspect-ratio: auto + object-fit: fill on desktop/tablet")
    print("Mobile: UNTOUCHED")
    print("=" * 60)

    result = deploy()

    if result:
        print("\n[Deploy] SUCCESS: Plugin saved to WordPress.")
    else:
        print("\n[Deploy] FAILED or uncertain. Check screenshots.")

    # Wait a moment for CDN
    print("\nWaiting 5 seconds for CDN propagation...")
    time.sleep(5)

    css_ok = verify_css()
    computed = verify_computed_styles()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    desktop = computed.get("desktop_1440", {})
    tablet = computed.get("tablet_1024", {})

    desktop_fixed = desktop.get("imgObjectFit") == "fill" and desktop.get("imgAspectRatio") in ("auto", "none", "")
    tablet_fixed = tablet.get("imgObjectFit") == "fill" and tablet.get("imgAspectRatio") in ("auto", "none", "")

    print(f"\nDesktop (1440px):")
    print(f"  - object-fit: {desktop.get('imgObjectFit')} (want: fill)")
    print(f"  - aspect-ratio: {desktop.get('imgAspectRatio')} (want: auto/none)")
    print(f"  - figure height: {desktop.get('figureHeight')}px")
    print(f"  - img rendered height: {desktop.get('imgRenderedHeight')}px")
    print(f"  - CSS version: {desktop.get('cssVersion')}")

    print(f"\nTablet (1024px):")
    print(f"  - object-fit: {tablet.get('imgObjectFit')} (want: fill)")
    print(f"  - aspect-ratio: {tablet.get('imgAspectRatio')} (want: auto/none)")
    print(f"  - figure height: {tablet.get('figureHeight')}px")
    print(f"  - img rendered height: {tablet.get('imgRenderedHeight')}px")
    print(f"  - CSS version: {tablet.get('cssVersion')}")

    if desktop.get("cssVersion") == "v1.9.0" and tablet.get("cssVersion") == "v1.9.0":
        print("\n[SUCCESS] v1.9.0 CSS IS LIVE - Bottom clipping fix deployed!")
        print(f"  Desktop screenshot: {SCREENSHOT_DESKTOP}")
        print(f"  Tablet screenshot: {SCREENSHOT_TABLET}")
    else:
        print("\n[WARNING] CSS version mismatch - CDN may still be caching old version.")
        print("  GoDaddy CDN cache flush was attempted. Wait 30-60 min for expiry.")
        print(f"  Desktop screenshot: {SCREENSHOT_DESKTOP}")
        print(f"  Tablet screenshot: {SCREENSHOT_TABLET}")
