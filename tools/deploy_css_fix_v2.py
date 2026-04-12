#!/usr/bin/env python3
"""
Deploy CSS Fix v2 - 2026-02-18
Uses correct credentials and proper login flow.
Tries:
1. WordPress REST API for custom CSS (if supported)
2. Playwright with correct password
"""

import sys
import time
import os
import json
import base64
import requests
from playwright.sync_api import sync_playwright

# WordPress credentials from .env
WP_URL = "https://purebrain.ai"
USERNAME = "Aether"
PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"

# CSS file
CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css"

# Screenshot dir
SCREENSHOT_DIR = "/tmp/purebrain-css-fix-2026-02-18"


def try_rest_api(new_css):
    """Try updating custom CSS via WordPress REST API"""
    print("\n=== METHOD 1: WordPress REST API ===")

    # Try with Application Password first
    credentials = f"{USERNAME}:{APP_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }

    # Test connection
    try:
        resp = requests.get(f"{WP_URL}/wp-json/wp/v2/users/me", headers=headers, timeout=15)
        print(f"  Auth test: {resp.status_code}")
        if resp.status_code == 200:
            user = resp.json()
            print(f"  Authenticated as: {user.get('name', 'unknown')}")
        else:
            print(f"  Auth failed: {resp.text[:200]}")
            # Try with regular password
            credentials2 = f"{USERNAME}:{PASSWORD}"
            encoded2 = base64.b64encode(credentials2.encode()).decode()
            headers["Authorization"] = f"Basic {encoded2}"
            resp2 = requests.get(f"{WP_URL}/wp-json/wp/v2/users/me", headers=headers, timeout=15)
            print(f"  Alt auth test: {resp2.status_code}")
            if resp2.status_code != 200:
                print("  Both auth methods failed for REST API")
                return False
    except Exception as e:
        print(f"  REST API connection error: {e}")
        return False

    # Try to get current custom CSS
    # WordPress custom CSS is stored as a `custom_css` post type
    try:
        resp = requests.get(
            f"{WP_URL}/wp-json/wp/v2/custom_css",
            headers=headers,
            timeout=15
        )
        print(f"  Custom CSS endpoint: {resp.status_code}")
        if resp.status_code == 200:
            css_posts = resp.json()
            if css_posts:
                css_post = css_posts[0]
                css_id = css_post["id"]
                print(f"  Found custom CSS post ID: {css_id}")
                print(f"  Current CSS length: {len(css_post.get('content', {}).get('raw', ''))}")

                # Update the CSS
                update_resp = requests.put(
                    f"{WP_URL}/wp-json/wp/v2/custom_css/{css_id}",
                    headers=headers,
                    json={"content": new_css},
                    timeout=30
                )
                print(f"  Update response: {update_resp.status_code}")
                if update_resp.status_code == 200:
                    print("  CSS updated successfully via REST API!")
                    return True
                else:
                    print(f"  Update failed: {update_resp.text[:300]}")
            else:
                print("  No custom CSS posts found")
        else:
            print(f"  Custom CSS endpoint response: {resp.text[:200]}")
    except Exception as e:
        print(f"  Custom CSS API error: {e}")

    # Try alternate approach: look for the theme's custom CSS setting
    try:
        # WordPress stores custom CSS per theme - try getting it
        resp = requests.get(
            f"{WP_URL}/wp-json/wp/v2/settings",
            headers=headers,
            timeout=15
        )
        print(f"  Settings endpoint: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Settings keys: {list(resp.json().keys())[:10]}")
    except Exception as e:
        print(f"  Settings endpoint error: {e}")

    return False


def try_playwright(new_css):
    """Try updating custom CSS via Playwright browser automation"""
    print("\n=== METHOD 2: Playwright Browser Automation ===")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Login with correct password
        print("  Navigating to WordPress login...")
        page.goto(f"{WP_URL}/wp-admin", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Click "Log in with username and password" (GoDaddy)
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=3000):
                print("  Clicking 'Log in with username and password'...")
                login_link.click()
                time.sleep(2)
        except:
            pass

        # Fill login form with correct password
        username_field = page.locator("input[name='log'], input#user_login")
        password_field = page.locator("input[name='pwd'], input#user_pass")

        if username_field.count() > 0:
            username_field.first.fill(USERNAME)
            password_field.first.fill(PASSWORD)

            # Check for CAPTCHA
            captcha = page.locator("img.captcha-image, .captcha, [class*='captcha'], #captcha")
            if captcha.count() > 0:
                print("  WARNING: CAPTCHA detected! Cannot proceed with Playwright.")
                page.screenshot(path=f"{SCREENSHOT_DIR}/captcha_detected.png")
                browser.close()
                return False

            # Submit
            submit_btn = page.locator("input[type='submit'], button[type='submit']").first
            submit_btn.click()
            time.sleep(5)

            page.screenshot(path=f"{SCREENSHOT_DIR}/20_login_result.png")
            current_url = page.url
            print(f"  After login URL: {current_url}")

            if "wp-login" in current_url:
                # Check for error message
                error = page.locator("#login_error, .login-error, [class*='error']")
                if error.count() > 0:
                    error_text = error.first.inner_text()
                    print(f"  Login error: {error_text}")
                browser.close()
                return False

            print("  Login successful!")

            # Navigate to Customizer Additional CSS
            print("  Navigating to Customizer > Additional CSS...")
            customizer_url = f"{WP_URL}/wp-admin/customize.php?autofocus[section]=custom_css"
            page.goto(customizer_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(10)

            page.screenshot(path=f"{SCREENSHOT_DIR}/21_customizer.png")

            # Escape CSS for JavaScript
            escaped_css = new_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

            # Try CodeMirror
            result = page.evaluate(f"""
                () => {{
                    // Try CodeMirror
                    const cm = document.querySelector('.CodeMirror');
                    if (cm && cm.CodeMirror) {{
                        cm.CodeMirror.setValue(`{escaped_css}`);
                        cm.CodeMirror.refresh();
                        return 'codemirror_' + cm.CodeMirror.getValue().length;
                    }}

                    // Try textarea
                    const ta = document.querySelector('textarea[id*="custom_css"]');
                    if (ta) {{
                        ta.value = `{escaped_css}`;
                        ta.dispatchEvent(new Event('change', {{bubbles: true}}));
                        return 'textarea_' + ta.value.length;
                    }}

                    // Try wp.customize
                    if (typeof wp !== 'undefined' && wp.customize) {{
                        try {{
                            const keys = Object.keys(wp.customize.settings.settings);
                            const cssKey = keys.find(k => k.includes('custom_css'));
                            if (cssKey) {{
                                wp.customize(cssKey).set(`{escaped_css}`);
                                return 'wp_customize_' + cssKey;
                            }}
                        }} catch(e) {{
                            return 'wp_customize_error_' + e.message;
                        }}
                    }}

                    return 'failed';
                }}
            """)
            print(f"  CSS update result: {result}")

            if 'failed' in str(result):
                page.screenshot(path=f"{SCREENSHOT_DIR}/22_css_failed.png")
                browser.close()
                return False

            time.sleep(2)
            page.screenshot(path=f"{SCREENSHOT_DIR}/22_css_updated.png")

            # Click Publish
            print("  Publishing...")
            publish_btn = page.locator("#save, button#save, button:has-text('Publish'), input[value='Publish']")
            if publish_btn.count() > 0:
                publish_btn.first.click()
                time.sleep(5)
                page.screenshot(path=f"{SCREENSHOT_DIR}/23_published.png")
                print("  Published!")
            else:
                page.keyboard.press("Control+s")
                time.sleep(5)
                page.screenshot(path=f"{SCREENSHOT_DIR}/23_saved.png")

            browser.close()
            return True

        else:
            print("  Could not find login fields")
            page.screenshot(path=f"{SCREENSHOT_DIR}/20_no_fields.png")
            browser.close()
            return False


def verify_pages():
    """Verify all three pages visually"""
    print("\n=== VERIFICATION ===")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})

        # Homepage
        print("  Checking homepage...")
        page = context.new_page()
        try:
            page.goto(f"{WP_URL}", wait_until="domcontentloaded", timeout=30000)
            time.sleep(8)
            page.evaluate("() => location.reload(true)")
            time.sleep(5)
            page.screenshot(path=f"{SCREENSHOT_DIR}/30_verify_homepage.png", full_page=False)

            # Check for orange square
            body_bg = page.evaluate("""
                () => {
                    const body = document.body;
                    return {
                        bodyBg: getComputedStyle(body).backgroundColor,
                        bodyClasses: body.className,
                        topLeftElements: document.elementsFromPoint(5, 5).map(e => ({
                            tag: e.tagName, class: e.className.substring(0, 100),
                            bg: getComputedStyle(e).backgroundColor,
                            w: e.offsetWidth, h: e.offsetHeight
                        })).filter(e => e.bg !== 'rgba(0, 0, 0, 0)' && e.bg !== 'transparent')
                    };
                }
            """)
            print(f"  Body background: {body_bg['bodyBg']}")
            print(f"  Top-left elements: {json.dumps(body_bg['topLeftElements'], indent=2)}")
        except Exception as e:
            print(f"  Homepage error: {e}")

        # Blog
        print("  Checking blog page...")
        try:
            page.goto(f"{WP_URL}/blog/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            page.screenshot(path=f"{SCREENSHOT_DIR}/31_verify_blog.png", full_page=False)
        except Exception as e:
            print(f"  Blog error: {e}")

        # Blog post
        print("  Checking blog post...")
        try:
            page.goto(f"{WP_URL}/why-ai-memory-changes-everything/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            page.screenshot(path=f"{SCREENSHOT_DIR}/32_verify_blogpost.png", full_page=False)

            # Check social sharing
            social = page.evaluate("""
                () => {
                    const containers = document.querySelectorAll('.post-social-sharing, [class*="social-share"]:not(footer *)');
                    return Array.from(containers).map(e => ({
                        class: e.className,
                        display: getComputedStyle(e).display,
                        visibility: getComputedStyle(e).visibility,
                        height: getComputedStyle(e).height,
                        children: e.children.length,
                        html: e.innerHTML.substring(0, 200)
                    }));
                }
            """)
            print(f"  Social sharing: {json.dumps(social, indent=2)}")

            # Scroll to social area
            page.evaluate("() => window.scrollTo(0, document.body.scrollHeight * 0.7)")
            time.sleep(2)
            page.screenshot(path=f"{SCREENSHOT_DIR}/33_verify_blogpost_scroll.png", full_page=False)
        except Exception as e:
            print(f"  Blog post error: {e}")

        browser.close()


def main():
    # Read CSS
    with open(CSS_FILE, 'r') as f:
        new_css = f.read()
    print(f"CSS loaded: {len(new_css)} chars")

    # Try REST API first
    if try_rest_api(new_css):
        print("\n  CSS deployed via REST API!")
        verify_pages()
        return 0

    # Fall back to Playwright
    if try_playwright(new_css):
        print("\n  CSS deployed via Playwright!")
        verify_pages()
        return 0

    print("\n  FAILED: Could not deploy CSS via either method.")
    print("  Manual deployment needed:")
    print(f"  1. Open: {WP_URL}/wp-admin/customize.php?autofocus[section]=custom_css")
    print(f"  2. Replace ALL content with: {CSS_FILE}")
    print("  3. Click 'Publish'")

    # Still verify current state
    verify_pages()
    return 1


if __name__ == "__main__":
    sys.exit(main())
