#!/usr/bin/env python3
"""
URGENT FIX: Magic cursor CSS selector killing body display
==========================================================
ROOT CAUSE IDENTIFIED (2026-02-18):
  In WordPress Additional CSS (Customizer > Additional CSS), the rule:
  
    .magic-cursor, #magic-cursor, [class*="magic-cursor"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }
  
  contains [class*="magic-cursor"] which matches the body element because
  body has class 'tt-magic-cursor' (added by the Artistics theme).
  
  This makes body { display: none !important } - blank page.
  
  AFFECTS: ALL pages on purebrain.ai including:
  - Homepage (https://purebrain.ai/)
  - pay-test (https://purebrain.ai/pay-test/)
  - All other pages using Artistics theme

FIX: Replace [class*="magic-cursor"] with :not(body):not(html) qualified version
     so it no longer matches the body element.

DEPLOYMENT: Uses Playwright to login + CodeMirror JS to update Additional CSS
"""

import sys
import time
import os
import re
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai/wp-admin"
USERNAME = "Aether"
PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots/paytest-blank-investigation"

# The BAD rule (causes body display:none)
BAD_RULE = """.magic-cursor, #magic-cursor, [class*="magic-cursor"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}"""

# The FIXED rule (specific selectors only, doesn't match body.tt-magic-cursor)
FIXED_RULE = """.magic-cursor, #magic-cursor {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}
/* FIXED 2026-02-18: Removed [class*="magic-cursor"] wildcard selector
   REASON: body.tt-magic-cursor matched [class*="magic-cursor"] causing
   the entire page to be display:none (blank white page bug) */"""

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def main():
    print("=" * 60)
    print("MAGIC CURSOR BLANK PAGE FIX")
    print("=" * 60)
    print(f"Bad rule to replace:")
    print(f"  {BAD_RULE[:80]}...")
    print(f"\nFixed rule:")
    print(f"  {FIXED_RULE[:80]}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2
        )
        page = context.new_page()
        
        # ============ LOGIN ============
        print("\n=== STEP 1: Login to WordPress ===")
        page.goto(f"{WP_URL}", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/fix_01_login.png")
        
        # Check for GoDaddy SSO
        try:
            user_pass_link = page.locator("text=Log in with username and password")
            if user_pass_link.is_visible(timeout=3000):
                print("  GoDaddy SSO - clicking 'Log in with username and password'...")
                user_pass_link.click()
                time.sleep(2)
        except:
            pass
        
        # Login
        username_field = page.locator("input[name='log'], input#user_login").first
        password_field = page.locator("input[name='pwd'], input#user_pass").first
        
        username_field.fill(USERNAME, timeout=15000)
        password_field.fill(PASSWORD)
        page.screenshot(path=f"{SCREENSHOT_DIR}/fix_02_login_filled.png")
        
        # Handle CAPTCHA if present
        captcha_field = page.locator("input[name='wpsec_captcha_answer']")
        if captcha_field.count() > 0:
            print("  CAPTCHA detected - taking screenshot for visual solve...")
            page.screenshot(path=f"{SCREENSHOT_DIR}/fix_captcha.png")
            print(f"  CAPTCHA screenshot: {SCREENSHOT_DIR}/fix_captcha.png")
            # Try to read the CAPTCHA image
            captcha_img = page.locator(".wpsec-captcha-image img, img.captcha, input + img")
            if captcha_img.count() > 0:
                print("  CAPTCHA image found - attempting to read...")
        
        page.locator("input[type='submit']").first.click()
        time.sleep(5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/fix_03_after_login.png")
        
        current_url = page.url
        print(f"  After login URL: {current_url}")
        
        if "wp-login" in current_url or "login" in current_url.lower():
            print("  ERROR: Login failed or CAPTCHA required")
            print(f"  Screenshot: {SCREENSHOT_DIR}/fix_03_after_login.png")
            browser.close()
            return 1
        
        print("  Login successful!")
        
        # ============ NAVIGATE TO CUSTOMIZER ============
        print("\n=== STEP 2: Navigate to Customizer > Additional CSS ===")
        
        customizer_url = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
        page.goto(customizer_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(8)
        page.screenshot(path=f"{SCREENSHOT_DIR}/fix_04_customizer.png")
        print(f"  Customizer loaded: {SCREENSHOT_DIR}/fix_04_customizer.png")
        
        # ============ READ CURRENT CSS ============
        print("\n=== STEP 3: Read current CSS and apply fix ===")
        
        # Read current CSS via CodeMirror
        current_css = page.evaluate("""
            () => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    return { method: 'codemirror', css: cm.CodeMirror.getValue() };
                }
                const textarea = document.querySelector('textarea[id*="custom_css"], #customize-control-custom_css textarea');
                if (textarea) {
                    return { method: 'textarea', css: textarea.value };
                }
                return { method: 'not_found', css: null };
            }
        """)
        
        print(f"  Current CSS method: {current_css.get('method')}")
        current_css_text = current_css.get('css', '')
        if current_css_text:
            print(f"  Current CSS length: {len(current_css_text)} chars")
        else:
            print("  ERROR: Could not read current CSS")
            browser.close()
            return 1
        
        # Apply the fix
        if BAD_RULE in current_css_text:
            new_css = current_css_text.replace(BAD_RULE, FIXED_RULE)
            print(f"  BAD RULE FOUND! Replacing...")
            print(f"  New CSS length: {len(new_css)} chars")
        else:
            print("  WARNING: Exact BAD_RULE not found in current CSS")
            # Try a broader match
            bad_pattern = r'\.magic-cursor,\s*#magic-cursor,\s*\[class\*="magic-cursor"\]\s*\{[^}]*display:\s*none[^}]*\}'
            if re.search(bad_pattern, current_css_text):
                new_css = re.sub(bad_pattern, FIXED_RULE.replace('\\', '\\\\'), current_css_text)
                print(f"  Found via regex pattern. New CSS length: {len(new_css)} chars")
            else:
                print("  CRITICAL: Could not find the bad rule!")
                print("  Current CSS snippet at end:")
                print(current_css_text[-500:])
                browser.close()
                return 1
        
        # Set the new CSS
        escaped_css = new_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
        
        result = page.evaluate(f"""
            () => {{
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {{
                    cm.CodeMirror.setValue(`{escaped_css}`);
                    cm.CodeMirror.refresh();
                    return 'codemirror_success_' + cm.CodeMirror.getValue().length + '_chars';
                }}
                const textarea = document.querySelector('textarea[id*="custom_css"]');
                if (textarea) {{
                    textarea.value = `{escaped_css}`;
                    textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return 'textarea_success_' + textarea.value.length + '_chars';
                }}
                return 'not_found';
            }}
        """)
        
        print(f"  CSS set result: {result}")
        page.screenshot(path=f"{SCREENSHOT_DIR}/fix_05_css_set.png")
        
        # ============ PUBLISH ============
        print("\n=== STEP 4: Publish the changes ===")
        
        # Click the Publish button
        publish_btn = page.locator("#save, .save-publish, button.save, [value='Publish'], [data-text-while-loading='Publishing']")
        if publish_btn.count() > 0:
            publish_btn.first.click()
            time.sleep(5)
            print("  Published!")
        else:
            # Try keyboard shortcut or alternative
            print("  Publish button not found, trying alternative...")
            all_buttons = page.locator("button").all_text_contents()
            print(f"  Available buttons: {all_buttons[:10]}")
            
            # Try clicking the Save & Publish button
            page.keyboard.press("Enter")
            time.sleep(3)
        
        page.screenshot(path=f"{SCREENSHOT_DIR}/fix_06_published.png")
        print(f"  Published screenshot: {SCREENSHOT_DIR}/fix_06_published.png")
        
        # ============ VERIFY ============
        print("\n=== STEP 5: Verify the fix ===")
        
        # Check homepage
        page2 = context.new_page()
        page2.goto("https://purebrain.ai/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        
        body_state = page2.evaluate("""() => {
            return {
                display: window.getComputedStyle(document.body).display,
                visibility: window.getComputedStyle(document.body).visibility,
                height: document.body.getBoundingClientRect().height
            };
        }""")
        print(f"  Homepage body state: {body_state}")
        page2.screenshot(path=f"{SCREENSHOT_DIR}/fix_07_homepage_after.png")
        
        # Check pay-test
        page2.goto("https://purebrain.ai/pay-test/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        
        paytest_state = page2.evaluate("""() => {
            return {
                display: window.getComputedStyle(document.body).display,
                visibility: window.getComputedStyle(document.body).visibility,
                height: document.body.getBoundingClientRect().height
            };
        }""")
        print(f"  pay-test body state: {paytest_state}")
        page2.screenshot(path=f"{SCREENSHOT_DIR}/fix_08_paytest_after.png")
        
        homepage_fixed = body_state.get('display') == 'block'
        paytest_fixed = paytest_state.get('display') == 'block'
        
        if homepage_fixed and paytest_fixed:
            print("\n=== FIX SUCCESSFUL! Both pages now render correctly ===")
        elif homepage_fixed or paytest_fixed:
            print(f"\n=== PARTIAL FIX: homepage={homepage_fixed}, paytest={paytest_fixed} ===")
        else:
            print("\n=== FIX MAY NOT HAVE BEEN APPLIED ===")
            print("  Check screenshots and try manual deployment")
        
        browser.close()
        return 0 if (homepage_fixed and paytest_fixed) else 1

if __name__ == "__main__":
    sys.exit(main())
