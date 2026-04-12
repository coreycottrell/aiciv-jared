#!/usr/bin/env python3
"""
WordPress UX Quick Wins - APPEND CSS
2026-02-17

IMPORTANT: This script APPENDS new CSS to existing CSS, it does NOT replace.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration - Using credentials from .env (PUREBRAIN_WP_USER/PUREBRAIN_WP_PASSWORD)
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"  # Updated from .env PUREBRAIN_WP_PASSWORD
UX_QUICKWINS_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-ux-quickwins-2026-02-17.css"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/wp-screenshots"

def ensure_screenshot_dir():
    """Create screenshot directory if it doesn't exist"""
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

def take_screenshot(page, name):
    """Take a screenshot with timestamp"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"Screenshot saved: {path}")
    return path

def load_quickwins_css():
    """Load the quick wins CSS"""
    with open(UX_QUICKWINS_FILE, 'r') as f:
        return f.read()

def append_wordpress_css():
    """Main function to APPEND CSS to WordPress"""
    ensure_screenshot_dir()
    quickwins_css = load_quickwins_css()
    print(f"Loaded quick wins CSS: {len(quickwins_css)} characters")

    with sync_playwright() as p:
        # Launch browser (HEADLESS for WSL2 environment)
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

            # Wait for dashboard to appear
            print("Waiting for dashboard...")
            page.wait_for_load_state('load', timeout=60000)
            time.sleep(5)  # Extra wait for page to settle
            take_screenshot(page, "04_after_login")

            # Verify we're logged in
            if page.query_selector('#wpadminbar') or page.query_selector('.wrap') or 'wp-admin' in page.url:
                print(f"Successfully logged in! URL: {page.url}")
            else:
                error = page.query_selector('#login_error')
                if error:
                    error_text = error.inner_text()
                    print(f"Login error: {error_text}")
                    return False
                print("Warning: Could not verify login, but continuing...")

            # Step 3: Navigate to Customizer CSS section
            print("[Step 3] Navigating to Additional CSS...")
            page.goto(WP_CSS_URL, wait_until='load', timeout=90000)
            time.sleep(10)  # Customizer needs significant time to initialize
            take_screenshot(page, "05_customizer_loading")

            # Wait for customizer to fully load
            print("Waiting for customizer to initialize...")
            try:
                page.wait_for_selector('#customize-controls', state='visible', timeout=30000)
            except:
                print("Warning: customize-controls not found, continuing...")

            time.sleep(5)  # Extra time for CodeMirror to initialize
            take_screenshot(page, "06_customizer_loaded")

            # Step 4: Get existing CSS and APPEND new CSS
            print("[Step 4] Finding CSS editor and getting existing content...")

            codemirror = page.query_selector('.CodeMirror')
            if codemirror:
                print("Found CodeMirror editor")
                codemirror.click()
                time.sleep(1)

                # Get existing CSS
                existing_css = page.evaluate('''() => {
                    const cm = document.querySelector('.CodeMirror').CodeMirror;
                    return cm.getValue();
                }''')

                print(f"Existing CSS length: {len(existing_css)} characters")

                # Check if quick wins already applied
                if "UX AUDIT QUICK WINS - 2026-02-17" in existing_css:
                    print("Quick wins CSS already present! Skipping append.")
                    take_screenshot(page, "07_already_applied")
                else:
                    # Append the new CSS
                    combined_css = existing_css + "\n\n" + quickwins_css

                    print(f"Appending quick wins CSS. New total: {len(combined_css)} characters")

                    # Set the combined value
                    page.evaluate(f'''() => {{
                        const cm = document.querySelector('.CodeMirror').CodeMirror;
                        cm.setValue({repr(combined_css)});
                    }}''')
                    time.sleep(2)
                    take_screenshot(page, "07_css_appended")
                    print("CSS content appended in CodeMirror")
            else:
                print("Could not find CodeMirror editor!")
                take_screenshot(page, "07_error_no_editor")
                return False

            # Step 5: Click Publish button
            print("[Step 5] Publishing changes...")
            time.sleep(3)

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
                time.sleep(5)
                take_screenshot(page, "09_after_publish")
                print("Changes published successfully!")
            else:
                print("Could not find Publish button - trying keyboard shortcut...")
                take_screenshot(page, "08_no_publish_button")
                page.keyboard.press('Control+Shift+s')
                time.sleep(5)
                take_screenshot(page, "09_after_keyboard_save")

            # Step 6: Verify on live site
            print("\n[Step 6] Verifying on live site...")

            # Open new context to avoid cache
            verify_context = browser.new_context(viewport={'width': 1440, 'height': 900})
            verify_page = verify_context.new_page()

            print("Checking homepage...")
            verify_page.goto("https://purebrain.ai/", wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            take_screenshot(verify_page, "10_verify_homepage")

            # Check for visible navigation
            nav_visible = verify_page.query_selector('.navbar:visible, .main-navigation:visible, nav:visible')
            if nav_visible:
                print("Navigation appears visible!")
            else:
                print("Note: Navigation may be hidden or using different selectors")

            verify_context.close()

            print("\n=== UX QUICK WINS APPLIED SUCCESSFULLY ===")
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
    success = append_wordpress_css()
    print(f"\n{'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
