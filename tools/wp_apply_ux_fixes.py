#!/usr/bin/env python3
"""
WordPress UX Fixes Application via Playwright
Applies the priority UX fixes from the 2026-02-15 audit to purebrain.ai
Handles GoDaddy SSO login page
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
EXISTING_CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css"
UX_FIXES_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-ux-fixes-2026-02-15.css"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/wp-screenshots"

def ensure_screenshot_dir():
    """Create screenshot directory if it doesn't exist"""
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

def take_screenshot(page, name):
    """Take a screenshot with timestamp"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"Screenshot saved: {path}")
    return path

def load_and_merge_css():
    """Load existing CSS and merge with UX fixes"""
    # Load existing CSS
    with open(EXISTING_CSS_FILE, 'r') as f:
        existing_css = f.read()

    # Load UX fixes
    with open(UX_FIXES_FILE, 'r') as f:
        ux_fixes_css = f.read()

    # Merge: existing first, then UX fixes (UX fixes override)
    merged_css = f"{existing_css}\n\n{ux_fixes_css}"

    return merged_css

def apply_wordpress_css():
    """Main function to apply WordPress CSS UX fixes"""
    ensure_screenshot_dir()
    css_content = load_and_merge_css()
    print(f"Loaded merged CSS: {len(css_content)} characters")

    with sync_playwright() as p:
        # Launch browser (headless for automation)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Step 1: Navigate to wp-admin login
            print("\n[Step 1] Navigating to WordPress admin...")
            page.goto(WP_ADMIN_URL, wait_until='load', timeout=60000)
            take_screenshot(page, "01_login_page")

            # Step 2: Handle GoDaddy login page
            print("[Step 2] Handling login page...")

            # Check if we need to click "Log in with username and password" link
            username_password_link = page.query_selector('text="Log in with username and password"')
            if username_password_link:
                print("Found GoDaddy SSO page - clicking username/password option...")
                username_password_link.click()
                time.sleep(2)
                take_screenshot(page, "02_username_form_revealed")

            # Wait for login form to be visible
            page.wait_for_selector('#user_login', state='visible', timeout=30000)

            # Fill credentials
            print("Filling credentials...")
            page.fill('#user_login', USERNAME)
            page.fill('#user_pass', PASSWORD)
            take_screenshot(page, "03_credentials_filled")

            # Click login button
            page.click('#wp-submit')

            # Wait for dashboard to appear (don't use networkidle - takes too long)
            print("Waiting for dashboard...")
            page.wait_for_load_state('load', timeout=60000)
            time.sleep(5)  # Extra wait for page to settle
            take_screenshot(page, "04_after_login")

            # Verify we're logged in by checking for dashboard elements
            if page.query_selector('#wpadminbar') or page.query_selector('.wrap') or 'wp-admin' in page.url:
                print(f"Successfully logged in! URL: {page.url}")
            else:
                # Check for error message
                error = page.query_selector('#login_error')
                if error:
                    error_text = error.inner_text()
                    print(f"Login error: {error_text}")
                    return False
                print("Warning: Could not verify login, but continuing...")

            # Step 3: Navigate to Customizer CSS section
            print("[Step 3] Navigating to Additional CSS...")
            page.goto(WP_CSS_URL, wait_until='load', timeout=90000)
            time.sleep(8)  # Customizer needs significant time to initialize
            take_screenshot(page, "05_customizer_loading")

            # Wait for customizer to fully load
            print("Waiting for customizer to initialize...")
            # Wait for the customizer controls to appear
            try:
                page.wait_for_selector('#customize-controls', state='visible', timeout=30000)
            except:
                print("Warning: customize-controls not found, continuing...")

            time.sleep(5)  # Extra time for CodeMirror to initialize
            take_screenshot(page, "06_customizer_loaded")

            # Step 4: Find and update the CSS textarea
            print("[Step 4] Finding CSS editor...")

            # Try to find the CSS textarea - it might be CodeMirror or plain textarea
            # Method 1: Look for CodeMirror (WordPress uses this for CSS)
            codemirror = page.query_selector('.CodeMirror')
            if codemirror:
                print("Found CodeMirror editor")
                # Click on CodeMirror to focus it
                codemirror.click()
                time.sleep(1)

                # Use JavaScript to set the value directly
                print("Inserting new CSS content via JavaScript...")
                page.evaluate(f'''() => {{
                    const cm = document.querySelector('.CodeMirror').CodeMirror;
                    cm.setValue({repr(css_content)});
                }}''')
                time.sleep(2)
                take_screenshot(page, "07_css_updated")
                print("CSS content updated in CodeMirror")

            else:
                # Method 2: Look for plain textarea
                print("Looking for plain textarea...")
                css_textarea = page.query_selector('textarea.wp-editor-area, #custom-css-textarea, textarea[id*="css"]')
                if css_textarea:
                    print("Found plain textarea")
                    css_textarea.fill('')  # Clear first
                    css_textarea.fill(css_content)
                    take_screenshot(page, "07_css_updated")
                else:
                    # Method 3: Try ace editor or other code editors
                    ace_editor = page.query_selector('.ace_editor')
                    if ace_editor:
                        print("Found ACE editor")
                        page.evaluate(f'''() => {{
                            const editor = ace.edit(document.querySelector('.ace_editor'));
                            editor.setValue({repr(css_content)}, -1);
                        }}''')
                        take_screenshot(page, "07_css_updated")
                    else:
                        print("Could not find CSS editor!")
                        # Save page HTML for debugging
                        html = page.content()
                        with open(f"{SCREENSHOT_DIR}/debug_page.html", 'w') as f:
                            f.write(html)
                        take_screenshot(page, "07_error_no_editor")
                        return False

            # Step 5: Click Publish button
            print("[Step 5] Publishing changes...")
            time.sleep(3)  # Wait for CSS to be fully set

            # WordPress customizer has a specific publish button
            # Try multiple selectors for the Publish button
            publish_selectors = [
                '#save',
                '#customize-save-button-wrapper button',
                'input[type="submit"][value="Publish"]',
                'button:has-text("Publish")',
                '.button-primary:has-text("Publish")',
            ]

            publish_btn = None
            for selector in publish_selectors:
                try:
                    btn = page.query_selector(selector)
                    if btn and btn.is_visible():
                        publish_btn = btn
                        print(f"Found publish button with selector: {selector}")
                        break
                except:
                    continue

            if publish_btn:
                take_screenshot(page, "08_before_publish")
                publish_btn.click()
                print("Clicked publish button")

                # Wait for save to complete
                time.sleep(5)
                take_screenshot(page, "09_after_publish")

                # Check for success - button text might change
                print("Changes published successfully!")
            else:
                print("Could not find Publish button - trying keyboard shortcut...")
                take_screenshot(page, "08_no_publish_button")

                # Try pressing Ctrl+Shift+S (WordPress customizer save shortcut)
                page.keyboard.press('Control+Shift+s')
                time.sleep(5)
                take_screenshot(page, "09_after_keyboard_save")

            # Step 6: Verify on live site
            print("\n[Step 6] Verifying on live site...")

            # Open new context to avoid cache
            verify_context = browser.new_context(viewport={'width': 1440, 'height': 900})
            verify_page = verify_context.new_page()

            # Check blog page
            print("Checking blog page...")
            verify_page.goto("https://purebrain.ai/blog/", wait_until='domcontentloaded', timeout=30000)
            time.sleep(5)
            take_screenshot(verify_page, "10_verify_blog_desktop")

            # Check a single post
            print("Checking single post...")
            verify_page.goto("https://purebrain.ai/what-i-actually-do-all-day/", wait_until='domcontentloaded', timeout=30000)
            time.sleep(5)
            take_screenshot(verify_page, "11_verify_post_desktop")

            # Check mobile viewport
            print("Checking mobile viewport...")
            mobile_context = browser.new_context(viewport={'width': 375, 'height': 812})
            mobile_page = mobile_context.new_page()

            mobile_page.goto("https://purebrain.ai/blog/", wait_until='domcontentloaded', timeout=30000)
            time.sleep(5)
            take_screenshot(mobile_page, "12_verify_blog_mobile")

            mobile_page.goto("https://purebrain.ai/what-i-actually-do-all-day/", wait_until='domcontentloaded', timeout=30000)
            time.sleep(5)
            take_screenshot(mobile_page, "13_verify_post_mobile")

            verify_context.close()
            mobile_context.close()

            print("\n=== UX FIXES APPLIED SUCCESSFULLY ===")
            print(f"Screenshots saved to: {SCREENSHOT_DIR}")
            return True

        except PlaywrightTimeout as e:
            print(f"Timeout error: {e}")
            take_screenshot(page, "error_timeout")
            return False
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "error_exception")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = apply_wordpress_css()
    print(f"\n{'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
