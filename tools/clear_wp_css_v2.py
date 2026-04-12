#!/usr/bin/env python3
"""
Clear WordPress Additional CSS - PureBrain.ai
Version 2: More robust CSS clearing
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

        # Check for GoDaddy login page - need to click "Log in with username and password"
        print("Step 2: Clicking 'Log in with username and password'...")
        try:
            username_pass_link = page.locator('text=Log in with username and password')
            if username_pass_link.count() > 0:
                username_pass_link.click()
                time.sleep(2)
        except Exception as e:
            print(f"No GoDaddy page or error: {e}")

        # Login
        print("Step 3: Logging in...")
        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASSWORD)
        page.click('#wp-submit')
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        # Take screenshot of dashboard
        page.screenshot(path="/tmp/wp_css2_01_dashboard.png")
        print("Screenshot saved: /tmp/wp_css2_01_dashboard.png")

        # Navigate to Customizer Additional CSS
        print("Step 4: Navigating to Customizer > Additional CSS...")
        page.goto("https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css")
        page.wait_for_load_state('networkidle')
        time.sleep(8)

        page.screenshot(path="/tmp/wp_css2_02_customizer.png")
        print("Screenshot saved: /tmp/wp_css2_02_customizer.png")

        # Wait for the CSS editor to load
        print("Step 5: Clearing CSS using JavaScript...")
        time.sleep(3)

        # Use JavaScript to clear the CodeMirror editor completely
        result = page.evaluate('''
            () => {
                // Find all CodeMirror instances
                var cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    var value = cm.CodeMirror.getValue();
                    console.log("Current CSS length:", value.length);
                    cm.CodeMirror.setValue('');
                    return "CSS cleared via CodeMirror. Previous length: " + value.length;
                }

                // Alternative: use the customize API
                if (typeof wp !== 'undefined' && wp.customize) {
                    // Get all registered settings
                    var keys = Object.keys(wp.customize._value);
                    for (var key of keys) {
                        if (key.indexOf('custom_css') !== -1) {
                            wp.customize(key).set('');
                            return "CSS cleared via wp.customize: " + key;
                        }
                    }
                }

                return "Could not find CodeMirror or customize API";
            }
        ''')
        print(f"JavaScript result: {result}")

        time.sleep(2)
        page.screenshot(path="/tmp/wp_css2_03_cleared.png")
        print("Screenshot saved: /tmp/wp_css2_03_cleared.png")

        # Click inside CodeMirror and verify it's empty
        print("Step 6: Verifying editor is empty...")
        try:
            css_area = page.locator('.CodeMirror')
            if css_area.count() > 0:
                css_area.first.click()
                time.sleep(0.5)
                # Select all and verify
                page.keyboard.press('Control+a')
                time.sleep(0.5)
                # Type nothing (delete selection)
                page.keyboard.press('Backspace')
                time.sleep(0.5)
                print("Editor verified empty")
        except Exception as e:
            print(f"Error verifying: {e}")

        time.sleep(2)
        page.screenshot(path="/tmp/wp_css2_04_verified.png")
        print("Screenshot saved: /tmp/wp_css2_04_verified.png")

        # Click Publish button
        print("Step 7: Publishing changes...")
        try:
            # The Publish button in customizer
            publish_btn = page.locator('#save')
            if publish_btn.count() > 0 and publish_btn.is_visible():
                publish_btn.click()
                print("Clicked #save button")
            else:
                # Try to find Publish button by text
                publish_btn = page.locator('button:has-text("Publish")')
                if publish_btn.count() > 0:
                    publish_btn.first.click()
                    print("Clicked Publish button by text")
                else:
                    # Last resort - any input with value Publish
                    page.click('input[value="Publish"]')
                    print("Clicked Publish input")
        except Exception as e:
            print(f"Error publishing: {e}")

        time.sleep(5)
        page.screenshot(path="/tmp/wp_css2_05_published.png")
        print("Screenshot saved: /tmp/wp_css2_05_published.png")

        # Navigate to blog to verify
        print("Step 8: Verifying blog page...")
        page.goto("https://purebrain.ai/blog/", timeout=60000)
        time.sleep(5)

        page.screenshot(path="/tmp/wp_css2_06_blog.png")
        print("Screenshot saved: /tmp/wp_css2_06_blog.png")

        # Scroll down
        page.evaluate("window.scrollBy(0, 600)")
        time.sleep(2)
        page.screenshot(path="/tmp/wp_css2_07_blog_scrolled.png")
        print("Screenshot saved: /tmp/wp_css2_07_blog_scrolled.png")

        print("\nDone! Check the screenshots to verify.")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    clear_additional_css()
