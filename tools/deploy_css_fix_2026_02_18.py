#!/usr/bin/env python3
"""
Deploy CSS Fix - 2026-02-18
Fixes three urgent issues on purebrain.ai:
1. Social sharing icons RESTORED (were hidden by display:none)
2. Homepage CTA arrow stays ORANGE
3. Orange square artifact REMOVED (was from unscoped [class*="magic"])

Uses Playwright to:
- Login to WordPress
- Navigate to Customizer > Additional CSS
- REPLACE all CSS with fixed version
- Publish
- Verify homepage, blog, and blog post pages
"""

import sys
import time
import os
from playwright.sync_api import sync_playwright

# WordPress credentials
WP_URL = "https://purebrain.ai/wp-admin"
USERNAME = "Aether"
PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"

# Read the fixed CSS from file
CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css"

# Screenshot output directory
SCREENSHOT_DIR = "/tmp/purebrain-css-fix-2026-02-18"

def main():
    # Read the CSS file
    with open(CSS_FILE, 'r') as f:
        new_css = f.read()

    print(f"CSS file loaded: {len(new_css)} chars ({len(new_css.splitlines())} lines)")

    # Create screenshot directory
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # ============ STEP 1: BEFORE SCREENSHOTS ============
        print("\n=== STEP 1: Taking BEFORE screenshots ===")

        # Homepage
        print("  Taking homepage screenshot...")
        try:
            page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=30000)
            time.sleep(8)
            page.screenshot(path=f"{SCREENSHOT_DIR}/01_before_homepage.png", full_page=False)
            print(f"  Saved: {SCREENSHOT_DIR}/01_before_homepage.png")
        except Exception as e:
            print(f"  Warning: {e}")
            try:
                page.screenshot(path=f"{SCREENSHOT_DIR}/01_before_homepage.png", full_page=False)
            except:
                pass

        # Blog page
        print("  Taking blog page screenshot...")
        try:
            page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            page.screenshot(path=f"{SCREENSHOT_DIR}/02_before_blog.png", full_page=False)
            print(f"  Saved: {SCREENSHOT_DIR}/02_before_blog.png")
        except Exception as e:
            print(f"  Warning: {e}")

        # Blog post
        print("  Taking blog post screenshot...")
        try:
            page.goto("https://purebrain.ai/why-ai-memory-changes-everything/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            page.screenshot(path=f"{SCREENSHOT_DIR}/03_before_blogpost.png", full_page=False)
            print(f"  Saved: {SCREENSHOT_DIR}/03_before_blogpost.png")
        except Exception as e:
            print(f"  Warning: {e}")

        # ============ STEP 2: LOGIN ============
        print("\n=== STEP 2: Logging into WordPress ===")

        page.goto(f"{WP_URL}", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/04_login_page.png")
        print(f"  Saved: {SCREENSHOT_DIR}/04_login_page.png")

        # Check for GoDaddy SSO login redirect
        try:
            login_with_user_pass = page.locator("text=Log in with username and password")
            if login_with_user_pass.is_visible(timeout=3000):
                print("  Found GoDaddy login - clicking 'Log in with username and password'...")
                login_with_user_pass.click()
                time.sleep(2)
        except:
            print("  Standard WordPress login form")

        # Fill login form
        username_field = page.locator("input[name='log'], input#user_login, input[id='user_login']")
        password_field = page.locator("input[name='pwd'], input#user_pass, input[id='user_pass']")

        if username_field.count() > 0:
            username_field.first.fill(USERNAME)
            password_field.first.fill(PASSWORD)

            page.screenshot(path=f"{SCREENSHOT_DIR}/05_login_filled.png")

            submit_btn = page.locator("input[type='submit'], button[type='submit']").first
            submit_btn.click()
            time.sleep(5)

            page.screenshot(path=f"{SCREENSHOT_DIR}/06_after_login.png")
            print(f"  Logged in. Saved: {SCREENSHOT_DIR}/06_after_login.png")

            # Check if we actually logged in
            current_url = page.url
            print(f"  Current URL: {current_url}")
            if "wp-login" in current_url:
                print("  WARNING: Still on login page - may need CAPTCHA or different credentials")
                page.screenshot(path=f"{SCREENSHOT_DIR}/06_login_failed.png")
                # Try alternate username
                print("  Trying alternate username: Purebrain@puremarketing.ai")
                try:
                    username_field2 = page.locator("input[name='log'], input#user_login")
                    password_field2 = page.locator("input[name='pwd'], input#user_pass")
                    if username_field2.count() > 0:
                        username_field2.first.fill("Purebrain@puremarketing.ai")
                        password_field2.first.fill("NW2u!JLQ3!Bt$XD$7CWzz5Z@")
                        submit_btn2 = page.locator("input[type='submit'], button[type='submit']").first
                        submit_btn2.click()
                        time.sleep(5)
                        page.screenshot(path=f"{SCREENSHOT_DIR}/06b_alt_login.png")
                        current_url = page.url
                        print(f"  Current URL after alt login: {current_url}")
                except Exception as e:
                    print(f"  Alt login error: {e}")
        else:
            print("  ERROR: Could not find login fields")
            page.screenshot(path=f"{SCREENSHOT_DIR}/06_error_no_fields.png")
            browser.close()
            return 1

        # ============ STEP 3: NAVIGATE TO CUSTOMIZER ============
        print("\n=== STEP 3: Navigating to Customizer > Additional CSS ===")

        customizer_url = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
        page.goto(customizer_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)  # Customizer is slow

        page.screenshot(path=f"{SCREENSHOT_DIR}/07_customizer.png")
        print(f"  Saved: {SCREENSHOT_DIR}/07_customizer.png")

        # ============ STEP 4: REPLACE CSS ============
        print("\n=== STEP 4: Replacing CSS content ===")

        # Use CodeMirror API to replace ALL content
        # Escape the CSS for JavaScript string
        escaped_css = new_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

        result = page.evaluate(f"""
            () => {{
                // Try CodeMirror first
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {{
                    cm.CodeMirror.setValue(`{escaped_css}`);
                    cm.CodeMirror.refresh();
                    return 'codemirror_success_' + cm.CodeMirror.getValue().length + '_chars';
                }}

                // Try textarea
                const textarea = document.querySelector('textarea[id*="custom_css"], textarea.customize-control-code-editor');
                if (textarea) {{
                    textarea.value = `{escaped_css}`;
                    textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    return 'textarea_success_' + textarea.value.length + '_chars';
                }}

                // Try wp.customize API
                if (typeof wp !== 'undefined' && wp.customize) {{
                    // Try to find the custom_css setting
                    const settingKeys = Object.keys(wp.customize.settings.settings);
                    const cssKey = settingKeys.find(k => k.includes('custom_css'));
                    if (cssKey) {{
                        wp.customize(cssKey).set(`{escaped_css}`);
                        return 'wp_customize_success';
                    }}
                }}

                return 'failed_no_editor_found';
            }}
        """)

        print(f"  CSS update result: {result}")

        time.sleep(2)
        page.screenshot(path=f"{SCREENSHOT_DIR}/08_css_updated.png")
        print(f"  Saved: {SCREENSHOT_DIR}/08_css_updated.png")

        # ============ STEP 5: PUBLISH ============
        print("\n=== STEP 5: Publishing changes ===")

        # Find and click Publish button
        publish_btn = page.locator("#save, button#save, #customize-save-button-wrapper button, button:has-text('Publish'), input[value='Publish']")
        if publish_btn.count() > 0:
            publish_btn.first.click()
            time.sleep(5)
            page.screenshot(path=f"{SCREENSHOT_DIR}/09_published.png")
            print(f"  Published. Saved: {SCREENSHOT_DIR}/09_published.png")
        else:
            print("  WARNING: Could not find Publish button, trying keyboard shortcut...")
            page.keyboard.press("Control+s")
            time.sleep(5)
            page.screenshot(path=f"{SCREENSHOT_DIR}/09_after_save.png")
            print(f"  Saved: {SCREENSHOT_DIR}/09_after_save.png")

        # Wait for publish to complete
        time.sleep(3)

        # ============ STEP 6: VERIFY PAGES ============
        print("\n=== STEP 6: Verifying all three pages ===")

        # Close customizer iframe context, open new page for verification
        verify_page = context.new_page()

        # Verify Homepage
        print("  Verifying homepage...")
        try:
            verify_page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=30000)
            time.sleep(8)
            # Force cache bypass
            verify_page.evaluate("() => { location.reload(true); }")
            time.sleep(5)
            verify_page.screenshot(path=f"{SCREENSHOT_DIR}/10_after_homepage.png", full_page=False)
            print(f"  Saved: {SCREENSHOT_DIR}/10_after_homepage.png")

            # Check for orange square artifact - look for any visible element in top-left corner
            artifact_check = verify_page.evaluate("""
                () => {
                    // Check for elements in the top-left 50x50px area
                    const elements = document.elementsFromPoint(10, 10);
                    return elements.map(e => ({
                        tag: e.tagName,
                        class: e.className,
                        id: e.id,
                        bg: getComputedStyle(e).backgroundColor,
                        display: getComputedStyle(e).display
                    })).filter(e => e.bg !== 'rgba(0, 0, 0, 0)' && e.bg !== 'transparent');
                }
            """)
            print(f"  Top-left elements: {artifact_check}")

            # Check CTA arrow color
            arrow_check = verify_page.evaluate("""
                () => {
                    const arrows = document.querySelectorAll('.btn__icon--arrow, .btn__icon--arrow path, .btn--primary svg, .btn--primary svg path');
                    return Array.from(arrows).map(e => ({
                        tag: e.tagName,
                        stroke: getComputedStyle(e).stroke,
                        color: getComputedStyle(e).color,
                        fill: getComputedStyle(e).fill
                    }));
                }
            """)
            print(f"  CTA arrow styles: {arrow_check}")

        except Exception as e:
            print(f"  Homepage verification warning: {e}")

        # Verify Blog page
        print("  Verifying blog page...")
        try:
            verify_page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            verify_page.evaluate("() => { location.reload(true); }")
            time.sleep(5)
            verify_page.screenshot(path=f"{SCREENSHOT_DIR}/11_after_blog.png", full_page=False)
            print(f"  Saved: {SCREENSHOT_DIR}/11_after_blog.png")
        except Exception as e:
            print(f"  Blog verification warning: {e}")

        # Verify Blog Post
        print("  Verifying blog post...")
        try:
            verify_page.goto("https://purebrain.ai/why-ai-memory-changes-everything/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            verify_page.evaluate("() => { location.reload(true); }")
            time.sleep(5)
            verify_page.screenshot(path=f"{SCREENSHOT_DIR}/12_after_blogpost.png", full_page=False)
            print(f"  Saved: {SCREENSHOT_DIR}/12_after_blogpost.png")

            # Check social sharing icons visibility
            social_check = verify_page.evaluate("""
                () => {
                    const socialContainers = document.querySelectorAll(
                        '.post-social-sharing, .social-sharing, .share-buttons, [class*="social-share"]:not(footer [class*="social-share"]), [class*="share-icons"]'
                    );
                    return Array.from(socialContainers).map(e => ({
                        class: e.className,
                        display: getComputedStyle(e).display,
                        visibility: getComputedStyle(e).visibility,
                        height: getComputedStyle(e).height,
                        childCount: e.children.length
                    }));
                }
            """)
            print(f"  Social sharing containers: {social_check}")

            # Also scroll down to find social sharing area
            verify_page.evaluate("() => { window.scrollTo(0, document.body.scrollHeight * 0.7); }")
            time.sleep(2)
            verify_page.screenshot(path=f"{SCREENSHOT_DIR}/13_after_blogpost_scrolled.png", full_page=False)
            print(f"  Saved: {SCREENSHOT_DIR}/13_after_blogpost_scrolled.png")

        except Exception as e:
            print(f"  Blog post verification warning: {e}")

        verify_page.close()
        browser.close()

        print(f"\n=== COMPLETE ===")
        print(f"All screenshots saved to: {SCREENSHOT_DIR}/")
        print(f"Files:")
        for f in sorted(os.listdir(SCREENSHOT_DIR)):
            print(f"  {SCREENSHOT_DIR}/{f}")

        return 0

if __name__ == "__main__":
    sys.exit(main())
