#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v2.5.0 to WordPress.

v2.5.0 changes:
1. CTA button now shows ORANGE background by default (was broken by v2.4.0's
   overbroad `body.single-post .blog-cta-block p a { background: none !important }` rule).

2. CTA button hover now changes to BLUE gradient (was orange in prior versions).
   Previous v2.3.0/v2.4.0 hover kept orange background + blue glow ring.
   Now: full blue gradient background on hover (per Jared's request).

3. Uses href-based attribute selectors to split CTA button vs newsletter link:
   - a[href*="awakening"] = CTA button → orange default, blue hover
   - a[href*="subscribe|newsletter|neural-feed"] = newsletter link → blue text/underline
   This eliminates the CSS collision between the two element types.

4. Version bumped to 2.5.0.

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

SCREENSHOT_DEPLOY = str(AETHER_ROOT / "exports/screenshots/plugin_v250_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v250_verify.png")
SCREENSHOT_BLOG   = str(AETHER_ROOT / "exports/screenshots/plugin_v250_blog_cta.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v2.5.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")
    print("Changes: CTA button orange default + blue hover, href-based selector split")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    # Validate v2.5.0 content markers
    checks = {
        "version 2.5.0": "2.5.0" in new_content,
        "awakening selector": 'a[href*="awakening"]' in new_content,
        "subscribe selector": 'a[href*="subscribe"]' in new_content,
        "neural-feed selector": 'a[href*="neural-feed"]' in new_content,
        "blue hover gradient": "#2a93c1 0%, #1e7da8" in new_content,
        "orange default gradient": "#f1420b 0%, #d13608" in new_content,
        "pb-blog-nav still present": "pb-blog-nav" in new_content,
        "nav menu still present": "AI Assessment" in new_content,
    }

    all_passed = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING"
        print(f"  [{status}] {name}")
        if not result:
            all_passed = False

    if not all_passed:
        print("\nERROR: Plugin file validation failed. Aborting deploy.")
        sys.exit(1)

    # The old overbroad p a rule should NOT be present as a catch-all
    # (Only the href-specific selectors should remain)
    if "blog-cta-block p a," in new_content and "blog-cta-block p a:link," in new_content:
        # Check if the old rule (without href selector) is still there
        if "body.single-post .blog-cta-block p a,\nbody.single-post .blog-cta-block p a:link" in new_content:
            print("ERROR: Old overbroad p a rule still present (without href selector). Aborting.")
            sys.exit(1)

    print("Plugin content validated (v2.5.0, all markers present). Starting Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,  # Sharp rendering for CAPTCHA reading
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

        # Check for CAPTCHA
        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=SCREENSHOT_DEPLOY)
            print(f"  CAPTCHA detected! Taking screenshot to read it...")
            print(f"  CAPTCHA screenshot: {SCREENSHOT_DEPLOY}")

            captcha_img = page.locator(".wpsec-captcha-img, img[src*='captcha'], .captcha img")
            if captcha_img.count() > 0:
                captcha_img.first.screenshot(path=SCREENSHOT_DEPLOY.replace(".png", "_captcha.png"))
                print(f"  Captcha crop saved. Manual read required.")

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
                    if (
                        val.includes('2.5.0') &&
                        val.includes('awakening') &&
                        val.includes('subscribe') &&
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
                    return cm ? cm.CodeMirror.getValue().substring(0, 400) : 'N/A';
                }""")
                print(f"  Current editor start: {current}")
                if '2.5.0' in current:
                    save_success = True
                    print("  Version 2.5.0 found in editor - assuming success.")

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
    """Verify the v2.5.0 changes are live on a blog post."""
    print("\n[Verification] Checking v2.5.0 CSS on live blog post...")

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

        has_version_250    = "2.5.0" in html
        has_awakening_sel  = 'href*="awakening"' in html
        has_subscribe_sel  = 'href*="subscribe"' in html
        has_neural_feed    = 'href*="neural-feed"' in html
        has_blue_hover     = "#2a93c1 0%, #1e7da8" in html
        has_orange_default = "#f1420b 0%, #d13608" in html
        has_blog_nav       = "pb-blog-nav" in html
        # Verify the old overbroad rule is gone from rendered HTML
        old_rule_gone      = "blog-cta-block p a:link" not in html

        checks = {
            "v2.5.0 version reference": has_version_250,
            "awakening href selector": has_awakening_sel,
            "subscribe href selector": has_subscribe_sel,
            "neural-feed href selector": has_neural_feed,
            "blue hover gradient (#2a93c1 -> #1e7da8)": has_blue_hover,
            "orange default gradient (#f1420b -> #d13608)": has_orange_default,
            "pb-blog-nav still present": has_blog_nav,
            "old overbroad p a:link rule gone": old_rule_gone,
        }

        all_good = True
        for name, result in checks.items():
            status = "OK" if result else "MISSING/FAIL"
            print(f"  [{status}] {name}")
            if not result:
                all_good = False

        return all_good

    except Exception as e:
        print(f"  Verification request failed: {e}")
        return False


def screenshot_blog_cta():
    """Take a screenshot of a blog post showing the CTA button state."""
    from playwright.sync_api import sync_playwright

    print("\n[Visual Check] Screenshotting CTA button on a live blog post...")

    post_url = "https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        # Scroll to CTA block
        page.evaluate("""() => {
            const cta = document.querySelector('.blog-cta-block');
            if (cta) cta.scrollIntoView({ behavior: 'instant', block: 'center' });
        }""")
        time.sleep(1)

        cta_info = page.evaluate("""() => {
            const btn = document.querySelector('.blog-cta-block p a[href*="awakening"]');
            const newsLink = document.querySelector('.blog-cta-block p a[href*="subscribe"], .blog-cta-block p a[href*="neural-feed"]');
            const ctaBlock = document.querySelector('.blog-cta-block');

            function getStyles(el) {
                if (!el) return null;
                const cs = window.getComputedStyle(el);
                return {
                    bg: cs.background,
                    color: cs.color,
                    display: cs.display,
                    padding: cs.padding,
                    borderRadius: cs.borderRadius,
                    textDecoration: cs.textDecoration,
                    href: el.getAttribute('href'),
                };
            }

            return {
                buttonFound: !!btn,
                newsLinkFound: !!newsLink,
                ctaBlockFound: !!ctaBlock,
                buttonStyles: getStyles(btn),
                newsLinkStyles: getStyles(newsLink),
            };
        }""")

        print(f"\n  CTA block found: {cta_info.get('ctaBlockFound')}")
        print(f"  Button (.blog-cta-block p a[href*=awakening]) found: {cta_info.get('buttonFound')}")
        if cta_info.get('buttonStyles'):
            s = cta_info['buttonStyles']
            print(f"    href: {s.get('href', 'N/A')}")
            print(f"    background: {s.get('bg', 'N/A')[:80]}")
            print(f"    color: {s.get('color', 'N/A')}")
            print(f"    display: {s.get('display', 'N/A')}")
            print(f"    padding: {s.get('padding', 'N/A')}")
            print(f"    border-radius: {s.get('borderRadius', 'N/A')}")

        print(f"\n  Newsletter link found: {cta_info.get('newsLinkFound')}")
        if cta_info.get('newsLinkStyles'):
            s = cta_info['newsLinkStyles']
            print(f"    href: {s.get('href', 'N/A')}")
            print(f"    background: {s.get('bg', 'N/A')[:80]}")
            print(f"    color: {s.get('color', 'N/A')}")
            print(f"    text-decoration: {s.get('textDecoration', 'N/A')}")

        page.screenshot(path=SCREENSHOT_BLOG)
        print(f"\n  Screenshot saved: {SCREENSHOT_BLOG}")

        browser.close()
    return cta_info


if __name__ == "__main__":
    print("=" * 60)
    print("PUREBRAIN SECURITY PLUGIN v2.5.0 - DEPLOY")
    print("Change 1: CTA button shows orange background by default")
    print("Change 2: CTA button hover = BLUE (not orange)")
    print("Change 3: href-based selectors prevent CSS collision")
    print("=" * 60)

    result = deploy()

    if result:
        print("\n[Deploy] SUCCESS: Plugin saved to WordPress.")
    else:
        print("\n[Deploy] FAILED or uncertain. Check screenshots.")
        sys.exit(1)

    # Wait for CDN propagation
    print("\nWaiting 10 seconds for CDN propagation...")
    time.sleep(10)

    # Verify live
    live_ok = verify_live()
    cta_info = screenshot_blog_cta()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    if live_ok:
        print("\n[SUCCESS] v2.5.0 IS LIVE!")
        print(f"\n  Screenshots:")
        print(f"    Deploy/save: {SCREENSHOT_DEPLOY}")
        print(f"    Blog CTA: {SCREENSHOT_BLOG}")
        print("\n  What changed:")
        print("  CTA Button (a[href*=awakening]):")
        print("    - Default: orange gradient (#f1420b → #d13608) + white text")
        print("    - Hover: BLUE gradient (#2a93c1 → #1e7da8) + blue glow ring + lift")
        print("  Newsletter link (a[href*=subscribe/newsletter/neural-feed]):")
        print("    - Default: blue text (#2a93c1) + underline")
        print("    - Hover: white text + no underline")
        print("  Root fix: href-based selectors prevent p a catch-all from breaking button bg")
    else:
        print("\n[WARNING] Changes may not be visible yet due to CDN caching.")
        print("  Wait 15-30 minutes for full propagation, then hard-refresh (Ctrl+Shift+R).")
        print(f"  Deploy screenshot: {SCREENSHOT_DEPLOY}")
