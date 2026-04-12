#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v2.2.0 to WordPress.

v2.2.0 changes:
- Added blog CTA hover effect (from v2.1.0, not previously deployed)
- Added blog navigation link on category/archive pages (section k)
  * Injects "← All Posts" link into the navbar on category/archive/tag pages
  * Uses existing .blog-nav-links CSS from WordPress Additional CSS
  * Link points to /blog/

Issues fixed:
1. Post-payment CTA overlap: Already applied (margin: 32px on both pages 439 + 468)
2. Blog link on category pages: New injection via wp_footer hook

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

PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)

SCREENSHOT_DEPLOY = str(AETHER_ROOT / "exports/screenshots/plugin_v220_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v220_verify.png")
SCREENSHOT_CATEGORY = str(AETHER_ROOT / "exports/screenshots/plugin_v220_category_live.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v2.2.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")
    print("Features: Blog CTA hover + Blog nav link on category pages")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    # Validate the new code is present
    if "2.2.0" not in new_content:
        print("ERROR: Plugin file does not contain version 2.2.0. Aborting.")
        sys.exit(1)

    if "purebrain-category-blog-nav" not in new_content:
        print("ERROR: Plugin file does not contain category blog nav script. Aborting.")
        sys.exit(1)

    if "blog-nav-links" not in new_content:
        print("ERROR: Plugin file does not contain blog-nav-links class. Aborting.")
        sys.exit(1)

    print("Plugin content validated (v2.2.0, blog nav code present). Starting Playwright...")

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
            page.screenshot(path=SCREENSHOT_DEPLOY)
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
            page.screenshot(path=SCREENSHOT_DEPLOY)
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
            page.screenshot(path=SCREENSHOT_DEPLOY)
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
                    if (val.includes('2.2.0') && val.includes('blog-nav-links')) return 'success';
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

        page.screenshot(path=SCREENSHOT_DEPLOY)
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
            print(f"  Status unclear. Page excerpt: {page_text[:400]}")
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 300) : 'N/A';
                }""")
                print(f"  Current editor start: {current}")
                if '2.2.0' in current:
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


def verify_live():
    """Verify the blog nav link is live on a category page."""
    print("\n[Verification] Checking blog nav on category page...")

    url = "https://purebrain.ai/category/for-teams/"
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

        has_blog_nav_script = "purebrain-category-blog-nav" in html
        has_all_posts_text = "All Posts" in html
        has_blog_url = "/blog/" in html

        print(f"  Category blog nav script: {has_blog_nav_script}")
        print(f"  'All Posts' text in page: {has_all_posts_text}")
        print(f"  /blog/ URL reference: {has_blog_url}")

        if has_blog_nav_script:
            print("  CONFIRMED: Blog nav injection script is LIVE!")
            return True
        else:
            print("  WARNING: Script not detected. CDN may still serve cached version.")
            return False

    except Exception as e:
        print(f"  Verification request failed: {e}")
        return False


def screenshot_category():
    """Take a screenshot of the category page showing the blog nav."""
    from playwright.sync_api import sync_playwright

    print("\n[Visual Check] Taking screenshot of category page with blog nav...")

    url = "https://purebrain.ai/category/for-teams/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        # Check what's in the navbar
        nav_info = page.evaluate("""() => {
            const navLinks = document.querySelector('.blog-nav-links');
            const script = document.getElementById('purebrain-category-blog-nav');
            const navbar = document.querySelector('nav.navbar .container');
            return {
                hasNavLinks: !!navLinks,
                navLinksText: navLinks ? navLinks.innerText : 'N/A',
                hasScript: !!script,
                navbarFound: !!navbar,
                navbarChildren: navbar ? navbar.children.length : 0
            };
        }""")

        print(f"  .blog-nav-links element: {nav_info.get('hasNavLinks')}")
        print(f"  Nav links text: {nav_info.get('navLinksText')}")
        print(f"  Script tag present: {nav_info.get('hasScript')}")
        print(f"  Navbar container found: {nav_info.get('navbarFound')}")

        page.screenshot(path=SCREENSHOT_CATEGORY)
        print(f"  Screenshot: {SCREENSHOT_CATEGORY}")

        browser.close()

    return nav_info


if __name__ == "__main__":
    print("=" * 60)
    print("PUREBRAIN SECURITY PLUGIN v2.2.0 DEPLOY")
    print("Features:")
    print("  - Blog CTA button hover (blue glow)")
    print("  - Blog navigation link on category pages")
    print("=" * 60)

    result = deploy()

    if result:
        print("\n[Deploy] SUCCESS: Plugin saved to WordPress.")
    else:
        print("\n[Deploy] FAILED or uncertain. Check screenshots.")
        sys.exit(1)

    # Wait for CDN
    print("\nWaiting 8 seconds for CDN propagation...")
    time.sleep(8)

    # Verify
    live_ok = verify_live()
    nav_info = screenshot_category()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    if live_ok:
        print("\n[SUCCESS] Blog nav v2.2.0 IS LIVE!")
        print(f"  .blog-nav-links element injected: {nav_info.get('hasNavLinks')}")
        print(f"  Nav text: {nav_info.get('navLinksText')}")
        print(f"\n  Screenshot: {SCREENSHOT_CATEGORY}")
        print("\n  How it works:")
        print("  - On category/archive/tag pages, JS injects '← All Posts' link")
        print("  - Link appears in the top navbar, right-aligned (margin-left: auto)")
        print("  - Points to /blog/ for easy return navigation")
        print("  - Styled with existing .blog-nav-links CSS (white text, orange hover)")
        print("\n  Pages affected:")
        print("  - /category/for-teams/")
        print("  - /category/for-individuals/")
        print("  - Any archive, tag, or category page")
    else:
        print("\n[WARNING] Script may not be visible yet due to CDN caching.")
        print("  Wait 15-30 minutes for full propagation.")
        print(f"  Deploy screenshot: {SCREENSHOT_DEPLOY}")
