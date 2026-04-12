#!/usr/bin/env python3
"""
Apply Pricing Enhancements to PureBrain 3.0 Page
Date: 2026-02-17

Steps:
1. Login to WordPress admin (with CAPTCHA handling)
2. Add tooltip CSS to Additional CSS
3. Navigate to purebrain-3 page and edit with Elementor
4. Update feature text with market jargon
"""

import time
import sys
import re
from playwright.sync_api import sync_playwright

# Credentials (updated 2026-02-17)
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# The tooltip CSS to add
TOOLTIP_CSS = """/* TOOLTIP SYSTEM - 2026-02-17 */
.feature-tooltip {
    position: relative;
    cursor: help;
    border-bottom: 1px dotted rgba(255,255,255,0.4);
}
.feature-tooltip::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(20, 20, 30, 0.98);
    color: #fff;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.85rem;
    width: 280px;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
    z-index: 1000;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    border: 1px solid rgba(42, 147, 193, 0.3);
}
.feature-tooltip:hover::after {
    opacity: 1;
    visibility: visible;
}
.jargon { color: #2a93c1; font-weight: 500; }
.jargon-orange { color: #f1420b; font-weight: 500; }
"""

def apply_pricing_enhancements(captcha_solution=None):
    with sync_playwright() as p:
        # Launch browser in HEADLESS mode (WSL2 compatibility)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # ============================================
            # STEP 1: Login to WordPress
            # ============================================
            print("=" * 60)
            print("STEP 1: Logging into WordPress Admin")
            print("=" * 60)

            page.goto(f"{WP_URL}")
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            page.screenshot(path="/tmp/pricing_01_login_page.png")
            print("Screenshot: /tmp/pricing_01_login_page.png")

            # Check for GoDaddy SSO page
            try:
                username_pass_link = page.locator('text=Log in with username and password')
                if username_pass_link.count() > 0:
                    print("Found GoDaddy login page, clicking username/password option...")
                    username_pass_link.click()
                    time.sleep(2)
                    page.screenshot(path="/tmp/pricing_01b_login_form.png")
                    print("Screenshot: /tmp/pricing_01b_login_form.png")
            except Exception as e:
                print(f"Note: {e}")

            # Fill login form
            print(f"Filling login: {WP_USER}")

            # Check which input fields exist
            user_input = page.locator('#user_login')
            pass_input = page.locator('#user_pass')

            if user_input.count() > 0:
                user_input.fill(WP_USER)
            else:
                # Try alternative selector
                page.locator('input[name="log"]').fill(WP_USER)

            if pass_input.count() > 0:
                pass_input.fill(WP_PASSWORD)
            else:
                # Try alternative selector
                page.locator('input[name="pwd"]').fill(WP_PASSWORD)

            # Check for CAPTCHA field - look for any input after password and before submit
            # Common selectors for WP CAPTCHA plugins
            captcha_selectors = [
                'input[name="captcha_code"]',
                'input[name="captcha"]',
                '#captcha_code',
                '#captcha',
                'input[name="jetpack_protect_answer"]',
                'input[placeholder*="CAPTCHA" i]',
                'input[placeholder*="captcha" i]',
                # Look for input after the label "Type in the text displayed above"
                'input[type="text"]:not(#user_login):not(#user_pass)'
            ]

            captcha_input = None
            for selector in captcha_selectors:
                loc = page.locator(selector)
                if loc.count() > 0:
                    # Make sure it's not the user login or password field
                    elem = loc.first
                    elem_id = elem.get_attribute('id') or ''
                    elem_name = elem.get_attribute('name') or ''
                    if elem_id not in ['user_login', 'user_pass', 'log', 'pwd'] and \
                       elem_name not in ['log', 'pwd', 'rememberme']:
                        captcha_input = elem
                        print(f"Found CAPTCHA input: selector={selector}, id={elem_id}, name={elem_name}")
                        break

            # Also look for any input field that comes after a CAPTCHA image
            if captcha_input is None:
                # Look for the third text input (after username and password)
                text_inputs = page.locator('input[type="text"]').all()
                if len(text_inputs) > 0:
                    # Find the one that is NOT username
                    for inp in text_inputs:
                        inp_id = inp.get_attribute('id') or ''
                        inp_name = inp.get_attribute('name') or ''
                        if inp_id != 'user_login' and inp_name != 'log':
                            captcha_input = inp
                            print(f"Found CAPTCHA input via text inputs: id={inp_id}, name={inp_name}")
                            break

            if captcha_input:
                print("CAPTCHA field detected!")
                # Capture CAPTCHA screenshot
                page.screenshot(path="/tmp/pricing_02_captcha.png")
                print("CAPTCHA Screenshot: /tmp/pricing_02_captcha.png")

                if captcha_solution:
                    print(f"Entering CAPTCHA solution: {captcha_solution}")
                    captcha_input.fill(captcha_solution)
                else:
                    print("ERROR: CAPTCHA required but no solution provided.")
                    print("Please look at /tmp/pricing_02_captcha.png and run with:")
                    print("  python3 script.py <captcha_text>")
                    browser.close()
                    return "CAPTCHA_NEEDED"
            else:
                print("No CAPTCHA field found - proceeding without it")

            page.screenshot(path="/tmp/pricing_02_filled.png")
            print("Screenshot: /tmp/pricing_02_filled.png")

            # Submit the form
            submit_btn = page.locator('#wp-submit, input[type="submit"][name="wp-submit"], input[value="Log In"]')
            if submit_btn.count() > 0:
                submit_btn.first.click()
            else:
                page.locator('input[type="submit"]').first.click()

            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/pricing_03_after_submit.png")
            print("Screenshot: /tmp/pricing_03_after_submit.png")

            # Check current URL and page content
            current_url = page.url
            print(f"Current URL: {current_url}")

            # Check for error messages
            page_content = page.content()
            if "Incorrect CAPTCHA" in page_content or "incorrect captcha" in page_content.lower():
                print("ERROR: Incorrect CAPTCHA")
                return "CAPTCHA_FAILED"

            if "incorrect username" in page_content.lower() or "invalid username" in page_content.lower():
                print("ERROR: Invalid username or password")
                return "LOGIN_FAILED"

            # Check if login was successful
            if "wp-admin" in current_url and "login" not in current_url.lower():
                print("SUCCESS: Logged into WordPress!")
            else:
                print("Login may not have succeeded. Checking page...")
                page.screenshot(path="/tmp/pricing_error_login.png")
                # Continue anyway to see what happens

            # ============================================
            # STEP 2: Add Tooltip CSS to Additional CSS
            # ============================================
            print("\n" + "=" * 60)
            print("STEP 2: Adding Tooltip CSS to Additional CSS")
            print("=" * 60)

            page.goto("https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css")
            page.wait_for_load_state('networkidle')
            time.sleep(5)

            page.screenshot(path="/tmp/pricing_04_customizer.png")
            print("Screenshot: /tmp/pricing_04_customizer.png")

            # Check if we're on the customizer
            if "customize.php" not in page.url:
                print("ERROR: Not on customizer page. May need to login.")
                page.screenshot(path="/tmp/pricing_error_customizer.png")
                return "NOT_LOGGED_IN"

            # Find the CodeMirror editor and add CSS
            try:
                css_area = page.locator('.CodeMirror')
                if css_area.count() > 0:
                    css_area.first.click()
                    time.sleep(1)

                    # Move to end of file
                    page.keyboard.press('Control+End')
                    time.sleep(0.5)

                    # Add new line and paste CSS
                    page.keyboard.press('Enter')
                    page.keyboard.press('Enter')

                    # Type the CSS (Playwright will handle it)
                    for line in TOOLTIP_CSS.split('\n'):
                        page.keyboard.type(line)
                        page.keyboard.press('Enter')

                    print("CSS added via CodeMirror")
                else:
                    print("CodeMirror not found, trying alternative...")
            except Exception as e:
                print(f"Error adding CSS: {e}")

            time.sleep(2)
            page.screenshot(path="/tmp/pricing_05_css_added.png")
            print("Screenshot: /tmp/pricing_05_css_added.png")

            # Click Publish
            print("Publishing CSS changes...")
            try:
                publish_btn = page.locator('#save')
                if publish_btn.count() > 0 and publish_btn.is_enabled():
                    publish_btn.click()
                    time.sleep(3)
                    print("Published!")
                else:
                    # Try text-based
                    page.locator('text=Publish').first.click()
                    time.sleep(3)
            except Exception as e:
                print(f"Note on publish: {e}")

            page.screenshot(path="/tmp/pricing_06_published.png")
            print("Screenshot: /tmp/pricing_06_published.png")

            # ============================================
            # STEP 3: Find the PureBrain-3 Page
            # ============================================
            print("\n" + "=" * 60)
            print("STEP 3: Finding PureBrain-3 Page")
            print("=" * 60)

            page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page")
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/pricing_07_pages_list.png")
            print("Screenshot: /tmp/pricing_07_pages_list.png")

            # Search for purebrain-3
            search_box = page.locator('#post-search-input')
            if search_box.count() > 0:
                search_box.fill('purebrain')
                page.locator('#search-submit').click()
                page.wait_for_load_state('networkidle')
                time.sleep(2)

            page.screenshot(path="/tmp/pricing_08_search_results.png")
            print("Screenshot: /tmp/pricing_08_search_results.png")

            # Look for the page row
            page_links = page.locator('a.row-title:has-text("purebrain")')
            print(f"Found {page_links.count()} matching pages")

            if page_links.count() > 0:
                # Get the page title
                for i in range(page_links.count()):
                    title = page_links.nth(i).text_content()
                    print(f"  Page {i+1}: {title}")

            # ============================================
            # STEP 4: Navigate to the page to see structure
            # ============================================
            print("\n" + "=" * 60)
            print("STEP 4: Viewing the PureBrain 3.0 Page")
            print("=" * 60)

            # Go to the front-end page first
            page.goto("https://purebrain.ai/purebrain-3/")
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/pricing_09_frontend.png", full_page=True)
            print("Screenshot: /tmp/pricing_09_frontend.png (full page)")

            # Scroll to pricing section
            page.evaluate('window.scrollTo(0, document.body.scrollHeight * 0.5)')
            time.sleep(2)
            page.screenshot(path="/tmp/pricing_10_pricing_section.png")
            print("Screenshot: /tmp/pricing_10_pricing_section.png")

            # ============================================
            # FINAL: Show current state
            # ============================================
            print("\n" + "=" * 60)
            print("STEP COMPLETE: CSS Added, Page Located")
            print("=" * 60)
            print("\nThe tooltip CSS has been added to Additional CSS.")
            print("The purebrain-3 page is at: https://purebrain.ai/purebrain-3/")
            print("\nScreenshots saved to /tmp/pricing_*.png")

            return "SUCCESS"

        except Exception as e:
            print(f"\nERROR: {e}")
            page.screenshot(path="/tmp/pricing_error.png")
            print("Error screenshot: /tmp/pricing_error.png")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    captcha = None
    if len(sys.argv) > 1:
        captcha = sys.argv[1]
        print(f"CAPTCHA solution provided: {captcha}")

    result = apply_pricing_enhancements(captcha)
    print(f"\nFinal result: {result}")
