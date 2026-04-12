#!/usr/bin/env python3
"""
Clear WordPress Additional CSS - PureBrain.ai
Emergency fix to restore blog page
"""

import time
import sys
from playwright.sync_api import sync_playwright

# Credentials
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

def clear_additional_css():
    with sync_playwright() as p:
        # Launch browser in visible mode
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("Step 1: Navigating to WordPress login...")
        page.goto(f"{WP_URL}")
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # Take screenshot
        page.screenshot(path="/tmp/wp_css_01_login.png")
        print("Screenshot saved: /tmp/wp_css_01_login.png")

        # Check for GoDaddy login page - need to click "Log in with username and password"
        print("Step 2: Clicking 'Log in with username and password'...")
        try:
            username_pass_link = page.locator('text=Log in with username and password')
            if username_pass_link.count() > 0:
                username_pass_link.click()
                time.sleep(2)
                page.screenshot(path="/tmp/wp_css_01b_login_form.png")
                print("Screenshot saved: /tmp/wp_css_01b_login_form.png")
        except Exception as e:
            print(f"No GoDaddy page or error: {e}")

        # Login
        print("Step 3: Logging in...")
        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASSWORD)
        page.screenshot(path="/tmp/wp_css_02_filled.png")
        print("Screenshot saved: /tmp/wp_css_02_filled.png")

        page.click('#wp-submit')
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        # Take screenshot of dashboard
        page.screenshot(path="/tmp/wp_css_03_dashboard.png")
        print("Screenshot saved: /tmp/wp_css_03_dashboard.png")

        # Navigate to Customizer Additional CSS
        print("Step 4: Navigating to Customizer > Additional CSS...")
        # Direct URL to Additional CSS in customizer
        page.goto("https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css")
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        page.screenshot(path="/tmp/wp_css_04_customizer.png")
        print("Screenshot saved: /tmp/wp_css_04_customizer.png")

        # Wait for the CSS editor to load
        print("Step 5: Clearing CSS...")
        time.sleep(3)

        # The CodeMirror editor - we need to access it differently
        # Try to find and clear the textarea or CodeMirror instance
        try:
            # First approach: Try clicking the CSS area and selecting all
            css_area = page.locator('.CodeMirror')
            if css_area.count() > 0:
                css_area.first.click()
                time.sleep(1)
                # Select all and delete
                page.keyboard.press('Control+a')
                time.sleep(0.5)
                page.keyboard.press('Backspace')
                time.sleep(1)
                print("CSS cleared via CodeMirror")
            else:
                # Try textarea directly
                textarea = page.locator('textarea#custom_css')
                if textarea.count() > 0:
                    textarea.fill('')
                    print("CSS cleared via textarea")
        except Exception as e:
            print(f"Error clearing CSS: {e}")
            # Alternative: use JavaScript
            page.evaluate('''
                // Try to clear CodeMirror
                if (window.wp && wp.customize) {
                    var cssControl = wp.customize('custom_css[flavor-flavor-flavor]');
                    if (cssControl) cssControl.set('');
                }
                // Or find CodeMirror instance
                var cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    cm.CodeMirror.setValue('');
                }
            ''')
            print("Attempted JS clear")

        time.sleep(2)
        page.screenshot(path="/tmp/wp_css_05_cleared.png")
        print("Screenshot saved: /tmp/wp_css_05_cleared.png")

        # Click Publish button
        print("Step 6: Publishing changes...")
        try:
            publish_btn = page.locator('#save')
            if publish_btn.count() > 0:
                publish_btn.click()
            else:
                # Try alternative selector
                page.click('input[type="submit"][value="Publish"]')
        except:
            # Look for any publish button
            page.locator('text=Publish').first.click()

        time.sleep(3)
        page.screenshot(path="/tmp/wp_css_06_published.png")
        print("Screenshot saved: /tmp/wp_css_06_published.png")

        # Navigate to blog to verify
        print("Step 7: Verifying blog page...")
        page.goto("https://purebrain.ai/blog/")
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        page.screenshot(path="/tmp/wp_css_07_blog_verify.png")
        print("Screenshot saved: /tmp/wp_css_07_blog_verify.png")

        print("\nDone! Check the screenshots to verify.")
        print("Keeping browser open for 10 seconds for manual verification...")
        time.sleep(10)

        browser.close()

if __name__ == "__main__":
    clear_additional_css()
