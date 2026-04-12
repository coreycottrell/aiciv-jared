#!/usr/bin/env python3
"""
WordPress CSS Fix Script - Add icon styling CSS to purebrain.ai
Uses Playwright for browser automation

Purpose: Add CSS to fix icon boxes: solid orange background + white icons
"""

import sys
import time
from playwright.sync_api import sync_playwright

# WordPress credentials
WP_URL = "https://purebrain.ai/wp-admin"
USERNAME = "Purebrain@puremarketing.ai"
PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# CSS to add
ICON_FIX_CSS = """
/* Fix icon boxes: solid orange background + white icons */
.feature-card__icon--orange {
    background: rgb(241, 66, 11) !important;
    color: #ffffff !important;
}

.feature-card__icon--orange svg,
.feature-card__icon--orange svg path {
    color: #ffffff !important;
    fill: #ffffff !important;
}

.value-card__icon--orange {
    background: rgb(241, 66, 11) !important;
    color: #ffffff !important;
}

.value-card__icon--orange svg,
.value-card__icon--orange svg path {
    color: #ffffff !important;
    fill: #ffffff !important;
}
"""

def main():
    with sync_playwright() as p:
        # Launch browser (headless for server environment)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Use shorter timeouts and domcontentloaded instead of networkidle
        print("Step 1: Taking BEFORE screenshot of purebrain.ai...")
        try:
            page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)  # Let page render
            page.screenshot(path="/tmp/purebrain-icons-before.png", full_page=False)
            print("  Saved: /tmp/purebrain-icons-before.png")
        except Exception as e:
            print(f"  Warning on homepage: {e}")
            page.screenshot(path="/tmp/purebrain-icons-before.png", full_page=False)

        print("\nStep 2: Navigating to WordPress login...")
        page.goto(WP_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Take screenshot of login page
        page.screenshot(path="/tmp/purebrain-wp-login.png")
        print("  Saved: /tmp/purebrain-wp-login.png")

        # Check if we need to click "Log in with username and password"
        try:
            login_with_user_pass = page.locator("text=Log in with username and password")
            if login_with_user_pass.is_visible(timeout=3000):
                print("  Found GoDaddy login - clicking 'Log in with username and password'...")
                login_with_user_pass.click()
                time.sleep(2)
                page.screenshot(path="/tmp/purebrain-wp-login2.png")
        except:
            print("  Standard WordPress login form")

        print("\nStep 3: Logging in...")
        # Fill login form
        username_field = page.locator("input[name='log'], input#user_login, input[id='user_login']")
        password_field = page.locator("input[name='pwd'], input#user_pass, input[id='user_pass']")

        if username_field.count() > 0:
            username_field.first.fill(USERNAME)
            password_field.first.fill(PASSWORD)

            # Click submit
            submit_btn = page.locator("input[type='submit'], button[type='submit']").first
            submit_btn.click()
            time.sleep(5)

            page.screenshot(path="/tmp/purebrain-wp-dashboard.png")
            print("  Logged in. Saved: /tmp/purebrain-wp-dashboard.png")
        else:
            print("  ERROR: Could not find login fields")
            page.screenshot(path="/tmp/purebrain-wp-error.png")
            browser.close()
            return 1

        print("\nStep 4: Navigating to Customizer Additional CSS...")
        # Try direct URL to customizer
        customizer_url = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
        page.goto(customizer_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(8)  # Customizer needs more time to load

        page.screenshot(path="/tmp/purebrain-customizer.png")
        print("  Saved: /tmp/purebrain-customizer.png")

        print("\nStep 5: Finding and updating CSS...")
        # Look for the CSS textarea in customizer
        # The customizer uses CodeMirror, so we need to find the right element

        # First, check if Additional CSS section is visible
        css_section = page.locator("text=Additional CSS")
        if css_section.count() > 0:
            print("  Found Additional CSS section")

        # Try clicking on Additional CSS in sidebar first
        try:
            additional_css_link = page.locator("[id*='custom_css'], [data-section='custom_css'], li[id*='customize-control-custom_css']")
            if additional_css_link.count() > 0:
                additional_css_link.first.click()
                time.sleep(3)
        except:
            pass

        # For CodeMirror, we need to use JS to add the CSS
        # First get current CSS content
        current_css = page.evaluate("""
            () => {
                // Try CodeMirror
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    return cm.CodeMirror.getValue();
                }
                // Try textarea
                const textarea = document.querySelector('textarea[id*="custom_css"], textarea.customize-control-code-editor');
                if (textarea) {
                    return textarea.value;
                }
                // Try wp.customize
                if (typeof wp !== 'undefined' && wp.customize) {
                    const setting = wp.customize('custom_css[flavor]') || wp.customize('custom_css');
                    if (setting) {
                        return setting.get() || '';
                    }
                }
                return null;
            }
        """)

        if current_css is not None:
            print(f"  Current CSS length: {len(current_css)} chars")

            # Check if our CSS is already there
            if ".feature-card__icon--orange" in current_css:
                print("  CSS already contains icon fix - skipping addition")
                new_css = current_css
            else:
                # Append our CSS
                new_css = current_css + "\n\n" + ICON_FIX_CSS
                print(f"  Adding icon fix CSS. New length: {len(new_css)} chars")

            # Set the new CSS
            result = page.evaluate("""
                (newCss) => {
                    // Try CodeMirror
                    const cm = document.querySelector('.CodeMirror');
                    if (cm && cm.CodeMirror) {
                        cm.CodeMirror.setValue(newCss);
                        cm.CodeMirror.refresh();
                        return 'codemirror';
                    }
                    // Try textarea
                    const textarea = document.querySelector('textarea[id*="custom_css"], textarea.customize-control-code-editor');
                    if (textarea) {
                        textarea.value = newCss;
                        textarea.dispatchEvent(new Event('change', { bubbles: true }));
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        return 'textarea';
                    }
                    return 'failed';
                }
            """, new_css)
            print(f"  CSS update method: {result}")

            time.sleep(2)
            page.screenshot(path="/tmp/purebrain-css-added.png")
            print("  Saved: /tmp/purebrain-css-added.png")

            print("\nStep 6: Publishing changes...")
            # Find and click Publish button
            publish_btn = page.locator("input#save, button#save, #customize-save-button-wrapper button, button:has-text('Publish'), input[value='Publish']")
            if publish_btn.count() > 0:
                publish_btn.first.click()
                time.sleep(5)
                page.screenshot(path="/tmp/purebrain-published.png")
                print("  Published. Saved: /tmp/purebrain-published.png")
            else:
                print("  WARNING: Could not find Publish button")
                # Try keyboard shortcut
                page.keyboard.press("Control+s")
                time.sleep(3)
                page.screenshot(path="/tmp/purebrain-after-save.png")
        else:
            print("  WARNING: Could not access CSS editor")
            # Try alternative approach - find textarea directly
            textarea = page.locator("textarea")
            print(f"  Found {textarea.count()} textareas on page")
            page.screenshot(path="/tmp/purebrain-customizer-debug.png")

        print("\nStep 7: Taking AFTER screenshot...")
        page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        # Force cache refresh with Ctrl+Shift+R behavior
        page.evaluate("() => { location.reload(true); }")
        time.sleep(5)
        page.screenshot(path="/tmp/purebrain-icons-after.png", full_page=False)
        print("  Saved: /tmp/purebrain-icons-after.png")

        browser.close()
        print("\nDone! Check screenshots in /tmp/")
        return 0

if __name__ == "__main__":
    sys.exit(main())
