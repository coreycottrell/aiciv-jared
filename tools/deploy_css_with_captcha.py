#!/usr/bin/env python3
"""
Deploy CSS with CAPTCHA solving - 2026-02-18
Step-by-step approach:
1. Navigate to login
2. Fill credentials
3. Save CAPTCHA image for human/AI reading
4. Accept CAPTCHA text as argument
5. Complete login and deploy CSS
"""

import sys
import time
import os
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai"
USERNAME = "Aether"
PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css"
SCREENSHOT_DIR = "/tmp/purebrain-css-fix-2026-02-18"


def main():
    captcha_text = sys.argv[1] if len(sys.argv) > 1 else None

    with open(CSS_FILE, 'r') as f:
        new_css = f.read()
    print(f"CSS loaded: {len(new_css)} chars")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Navigate to login
        print("Navigating to login...")
        page.goto(f"{WP_URL}/wp-admin", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Click "Log in with username and password"
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=3000):
                login_link.click()
                time.sleep(2)
        except:
            pass

        # Fill credentials
        username_field = page.locator("input[name='log'], input#user_login")
        password_field = page.locator("input[name='pwd'], input#user_pass")

        if username_field.count() > 0:
            username_field.first.fill(USERNAME)
            password_field.first.fill(PASSWORD)
        else:
            print("ERROR: No login fields found")
            browser.close()
            return 1

        # Check for CAPTCHA
        captcha_input = page.locator("input[name*='captcha'], input[id*='captcha'], input[name*='wpsec']")
        captcha_img = page.locator("img.captcha-image, img[class*='captcha'], img[src*='captcha']")

        if captcha_input.count() == 0:
            # Try broader search
            # The CAPTCHA field is the one after "Type in the text displayed above"
            captcha_input = page.locator("input:below(:text('Type in the text displayed above'))").first
            if captcha_input.count() == 0:
                # Try by position - it should be the field between password and remember me
                all_inputs = page.locator("input[type='text']")
                for i in range(all_inputs.count()):
                    inp = all_inputs.nth(i)
                    name = inp.get_attribute("name") or ""
                    id_attr = inp.get_attribute("id") or ""
                    if name != "log" and id_attr != "user_login":
                        captcha_input = inp
                        print(f"Found probable CAPTCHA field: name={name}, id={id_attr}")
                        break

        if not captcha_text:
            # Save screenshot for CAPTCHA reading
            page.screenshot(path=f"{SCREENSHOT_DIR}/captcha_to_solve.png")
            print(f"CAPTCHA screenshot saved to: {SCREENSHOT_DIR}/captcha_to_solve.png")
            print("Please read the CAPTCHA and run:")
            print(f"  python3 {sys.argv[0]} <captcha_text>")
            browser.close()
            return 2

        # Fill CAPTCHA
        print(f"Filling CAPTCHA: {captcha_text}")
        try:
            if hasattr(captcha_input, 'fill'):
                captcha_input.fill(captcha_text)
            else:
                # Find the input
                ci = page.locator("input[type='text']:not(#user_login)")
                for i in range(ci.count()):
                    inp = ci.nth(i)
                    name = inp.get_attribute("name") or ""
                    id_attr = inp.get_attribute("id") or ""
                    if name != "log" and id_attr != "user_login":
                        inp.fill(captcha_text)
                        print(f"  Filled input: name={name}, id={id_attr}")
                        break
        except Exception as e:
            print(f"Error filling CAPTCHA: {e}")
            # Try alternate approach
            page.locator("input[type='text']").last.fill(captcha_text)

        time.sleep(1)
        page.screenshot(path=f"{SCREENSHOT_DIR}/captcha_filled.png")

        # Submit
        print("Submitting login...")
        submit = page.locator("input[type='submit'], button[type='submit']").first
        submit.click()
        time.sleep(5)

        page.screenshot(path=f"{SCREENSHOT_DIR}/login_result.png")
        current_url = page.url
        print(f"After login URL: {current_url}")

        if "wp-login" in current_url:
            print("Login FAILED - check CAPTCHA text or credentials")
            browser.close()
            return 1

        print("LOGIN SUCCESSFUL!")

        # Navigate to Customizer
        print("Navigating to Customizer > Additional CSS...")
        page.goto(
            f"{WP_URL}/wp-admin/customize.php?autofocus[section]=custom_css",
            wait_until="domcontentloaded",
            timeout=60000
        )
        time.sleep(10)
        page.screenshot(path=f"{SCREENSHOT_DIR}/customizer.png")

        # Replace CSS via CodeMirror
        print("Replacing CSS content...")
        escaped_css = new_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

        result = page.evaluate(f"""
            () => {{
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {{
                    cm.CodeMirror.setValue(`{escaped_css}`);
                    cm.CodeMirror.refresh();
                    return 'codemirror_' + cm.CodeMirror.getValue().length;
                }}
                const ta = document.querySelector('textarea[id*="custom_css"]');
                if (ta) {{
                    ta.value = `{escaped_css}`;
                    ta.dispatchEvent(new Event('change', {{bubbles: true}}));
                    return 'textarea_' + ta.value.length;
                }}
                if (typeof wp !== 'undefined' && wp.customize) {{
                    try {{
                        const keys = Object.keys(wp.customize.settings.settings);
                        const cssKey = keys.find(k => k.includes('custom_css'));
                        if (cssKey) {{
                            wp.customize(cssKey).set(`{escaped_css}`);
                            return 'wp_customize_' + cssKey;
                        }}
                    }} catch(e) {{
                        return 'error_' + e.message;
                    }}
                }}
                return 'failed';
            }}
        """)
        print(f"CSS update: {result}")

        if 'failed' in str(result):
            page.screenshot(path=f"{SCREENSHOT_DIR}/css_failed.png")
            print("Failed to find CSS editor!")
            browser.close()
            return 1

        time.sleep(2)
        page.screenshot(path=f"{SCREENSHOT_DIR}/css_updated.png")

        # Publish
        print("Publishing...")
        publish_btn = page.locator("#save, button#save, button:has-text('Publish')")
        if publish_btn.count() > 0:
            publish_btn.first.click()
            time.sleep(5)
            page.screenshot(path=f"{SCREENSHOT_DIR}/published.png")
            print("Published!")
        else:
            page.keyboard.press("Control+s")
            time.sleep(5)

        # Verify
        print("\n=== VERIFICATION ===")
        vp = context.new_page()

        # Homepage
        vp.goto(f"{WP_URL}", wait_until="domcontentloaded", timeout=30000)
        time.sleep(8)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/verify_homepage.png", full_page=False)
        print(f"Homepage: {SCREENSHOT_DIR}/verify_homepage.png")

        # Check body bg
        body_bg = vp.evaluate("() => getComputedStyle(document.body).backgroundColor")
        print(f"Body background: {body_bg}")

        # Blog
        vp.goto(f"{WP_URL}/blog/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/verify_blog.png", full_page=False)
        print(f"Blog: {SCREENSHOT_DIR}/verify_blog.png")

        # Blog post
        vp.goto(f"{WP_URL}/why-ai-memory-changes-everything/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/verify_blogpost.png", full_page=False)
        social = vp.evaluate("""
            () => {
                const c = document.querySelectorAll('.post-social-sharing');
                return Array.from(c).map(e => ({
                    display: getComputedStyle(e).display,
                    visibility: getComputedStyle(e).visibility,
                    height: getComputedStyle(e).height
                }));
            }
        """)
        print(f"Social sharing: {social}")

        vp.evaluate("() => window.scrollTo(0, document.body.scrollHeight * 0.7)")
        time.sleep(2)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/verify_blogpost_scroll.png", full_page=False)
        print(f"Blog post scrolled: {SCREENSHOT_DIR}/verify_blogpost_scroll.png")

        browser.close()
        print("\nDONE!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
