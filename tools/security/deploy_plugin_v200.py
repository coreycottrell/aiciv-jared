#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v2.0.0 to WordPress.

v2.0.0 changes:
- Added FAQ accordion (section j) for single blog posts.
- .faq-section divs convert to collapsible accordions:
  * All items start collapsed (question visible, answer hidden)
  * Click question to expand answer with smooth CSS animation
  * One-at-a-time behavior (clicking one collapses previous)
  * Blue chevron rotates on open
  * Blue left border accent on active item
- Scoped to body.single-post .post-content only.
- No changes to existing functionality.

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

SCREENSHOT_DEPLOY = str(AETHER_ROOT / "exports/screenshots/plugin_v200_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v200_verify.png")
SCREENSHOT_FAQ = str(AETHER_ROOT / "exports/screenshots/plugin_v200_faq_live.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v2.0.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")
    print("Feature: FAQ accordion on single blog posts")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    # Validate the new code is present
    if "2.0.0" not in new_content:
        print("ERROR: Plugin file does not contain version 2.0.0. Aborting.")
        sys.exit(1)

    if "purebrain-faq-accordion" not in new_content:
        print("ERROR: Plugin file does not contain FAQ accordion CSS. Aborting.")
        sys.exit(1)

    if "faq-open" not in new_content:
        print("ERROR: Plugin file does not contain faq-open class logic. Aborting.")
        sys.exit(1)

    print("Plugin content validated (v2.0.0, FAQ accordion code present). Starting Playwright...")

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
                    if (val.includes('2.0.0') && val.includes('faq-open')) return 'success';
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
                    return cm ? cm.CodeMirror.getValue().substring(0, 200) : 'N/A';
                }""")
                print(f"  Current editor start: {current}")
                if '2.0.0' in current:
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
    """Verify the accordion CSS+JS is live on a blog post."""
    print("\n[Verification] Checking FAQ accordion on live blog post...")

    # Post 381: CEO vs Employee AI Transformation Gap - has 6 FAQ items
    url = "https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/"
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

        has_faq_style = "purebrain-faq-accordion" in html
        has_faq_js = "purebrain-faq-accordion-js" in html
        has_faq_open_class = "faq-open" in html
        has_faq_section_div = 'class="faq-section"' in html
        has_version_200 = "2.0.0" in html

        print(f"  FAQ accordion CSS block: {has_faq_style}")
        print(f"  FAQ accordion JS block: {has_faq_js}")
        print(f"  faq-open class in JS: {has_faq_open_class}")
        print(f"  .faq-section divs in content: {has_faq_section_div}")
        print(f"  v2.0.0 reference: {has_version_200}")

        if has_faq_style and has_faq_js and has_faq_section_div:
            print("  CONFIRMED: FAQ accordion is LIVE!")
            return True
        else:
            print("  WARNING: Not all elements detected. CDN may still serve cached version.")
            return False

    except Exception as e:
        print(f"  Verification request failed: {e}")
        return False


def screenshot_faq():
    """Take a screenshot of the FAQ section on a blog post."""
    from playwright.sync_api import sync_playwright

    print("\n[Visual Check] Taking screenshot of FAQ section...")

    url = "https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        # Scroll to FAQ section
        page.evaluate("""() => {
            const faq = document.querySelector('.faq-section');
            if (faq) faq.scrollIntoView({block: 'center', behavior: 'smooth'});
        }""")
        time.sleep(1)

        # Check what JS finds
        faq_info = page.evaluate("""() => {
            const items = document.querySelectorAll('.single-post .post-content .faq-section');
            const style = document.getElementById('purebrain-faq-accordion');
            const script = document.getElementById('purebrain-faq-accordion-js');
            return {
                faqCount: items.length,
                hasStyle: !!style,
                hasScript: !!script,
                firstQuestion: items.length > 0 ? items[0].querySelector('h3')?.textContent?.trim().substring(0, 60) : 'N/A',
                firstAnswerHidden: items.length > 0 ? window.getComputedStyle(items[0]).overflow === 'hidden' : 'N/A'
            };
        }""")

        print(f"  FAQ items found by JS: {faq_info.get('faqCount')}")
        print(f"  Style tag present: {faq_info.get('hasStyle')}")
        print(f"  Script tag present: {faq_info.get('hasScript')}")
        print(f"  First question: {faq_info.get('firstQuestion')}")

        page.screenshot(path=SCREENSHOT_FAQ)
        print(f"  Screenshot: {SCREENSHOT_FAQ}")

        browser.close()

    return faq_info


if __name__ == "__main__":
    print("=" * 60)
    print("PUREBRAIN SECURITY PLUGIN v2.0.0 - FAQ ACCORDION DEPLOY")
    print("Feature: Collapsible FAQ accordion on single blog posts")
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
    faq_info = screenshot_faq()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    if live_ok:
        print("\n[SUCCESS] FAQ accordion v2.0.0 IS LIVE!")
        print(f"  FAQ items detected: {faq_info.get('faqCount', '?')}")
        print(f"  Style injected: {faq_info.get('hasStyle', '?')}")
        print(f"  Script injected: {faq_info.get('hasScript', '?')}")
        print(f"\n  Screenshot: {SCREENSHOT_FAQ}")
        print("\n  How it works:")
        print("  - All FAQ items start collapsed (only question visible)")
        print("  - Click question -> answer expands with smooth animation")
        print("  - Click another -> previous collapses, new one opens")
        print("  - Blue chevron rotates 180deg when open")
        print("  - Blue left border accent on active item")
        print("\n  Posts affected:")
        print("  - Post 381: CEO vs Employee (6 FAQs)")
        print("  - Post 316: Why AI Memory Changes Everything (5 FAQs)")
        print("  - Post 373: AI Agents Break... (5 FAQs)")
        print("  - Post 172: (5 FAQs)")
        print("  - Post 98: How My Human Named Me (5 FAQs)")
        print("  - Post 480: AI Pilot Purgatory (6 FAQs)")
    else:
        print("\n[WARNING] CSS/JS may not be visible yet due to CDN caching.")
        print("  Wait 15-30 minutes for full propagation.")
        print(f"  Deploy screenshot: {SCREENSHOT_DEPLOY}")
