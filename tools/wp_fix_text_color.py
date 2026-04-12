#!/usr/bin/env python3
"""
WordPress CSS Fix for "What Happens Next" Section
Adds CSS to make text white instead of orange
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Purebrain@puremarketing.ai"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

SCREENSHOT_DIR = "/tmp"
SCREENSHOT_PREFIX = "purebrain-text-fix"

# CSS to add
CSS_TO_ADD = """
/* Fix What Happens Next section - text should be white, not orange */
.what-happens-next__timeline-item,
.what-happens-next__time,
.what-happens-next__description,
.timeline-item,
.timeline-item p,
.timeline-item span,
[class*="what-happens"] p,
[class*="what-happens"] span,
[class*="timeline"] p,
[class*="timeline"] span {
    color: #ffffff !important;
}

/* Keep the time markers orange for visual hierarchy */
.what-happens-next__time,
[class*="timeline"] .time,
.timeline-time {
    color: #f1420b !important;
}
"""

def take_screenshot(page, name):
    """Take a screenshot and save it"""
    filename = f"{SCREENSHOT_PREFIX}-{name}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    page.screenshot(path=filepath, full_page=False)
    print(f"Screenshot saved: {filepath}")
    return filepath

def main():
    with sync_playwright() as p:
        # Launch browser (headless)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Step 1: Navigate to WordPress admin
            print("Navigating to WordPress admin...")
            page.goto(WP_ADMIN_URL, wait_until='domcontentloaded')
            time.sleep(2)

            # Take screenshot of login page
            take_screenshot(page, "01-login-page")

            # Step 2: Login
            print("Logging in...")

            # Check if there's a GoDaddy login option - need to click "Log in with username and password"
            username_password_link = page.locator('text=Log in with username and password')
            if username_password_link.count() > 0 and username_password_link.is_visible():
                print("Found GoDaddy login page - clicking username/password option")
                username_password_link.click()
                time.sleep(1)
                take_screenshot(page, "01b-login-expanded")

            # Now fill the login form
            # Wait for the login form to be visible
            page.wait_for_selector('#user_login', state='visible', timeout=10000)

            # Fill username
            page.fill('#user_login', WP_USERNAME)

            # Fill password
            page.fill('#user_pass', WP_PASSWORD)

            take_screenshot(page, "01c-credentials-filled")

            # Click login button
            page.click('#wp-submit')

            # Wait for dashboard to load
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            take_screenshot(page, "02-dashboard")

            # Step 3: Navigate to Customize > Additional CSS
            print("Navigating to Appearance > Customize...")

            # Go directly to the customizer URL
            customizer_url = "https://purebrain.ai/wp-admin/customize.php"
            page.goto(customizer_url, wait_until='domcontentloaded')
            time.sleep(5)  # Give customizer more time to load

            take_screenshot(page, "03-customizer")

            # Step 4: Find and click on Additional CSS
            print("Looking for Additional CSS option...")

            # Wait for the customizer panel to be present (not necessarily visible)
            time.sleep(2)

            # List what sections are available
            sections = page.query_selector_all('.accordion-section-title')
            print("Available sections:")
            for s in sections:
                try:
                    text = s.inner_text()
                    if text.strip():
                        print(f"  - '{text}'")
                except:
                    pass

            # Scroll the customizer panel to reveal "Additional CSS" if hidden
            panel = page.locator('#customize-theme-controls')
            if panel.count() > 0:
                # Scroll inside the panel
                page.evaluate("""
                    () => {
                        const panel = document.querySelector('#customize-theme-controls');
                        if (panel) {
                            panel.scrollTop = panel.scrollHeight;
                        }
                    }
                """)
                time.sleep(1)
                take_screenshot(page, "03a-scrolled-panel")

            # Look for Additional CSS section - try multiple methods
            additional_css_selectors = [
                '#accordion-section-custom_css',
                'li#accordion-section-custom_css',
                '[id*="custom_css"]',
                'text=Additional CSS',
                '.accordion-section-title:text("Additional CSS")',
                'h3:text("Additional CSS")',
            ]

            clicked = False
            for selector in additional_css_selectors:
                try:
                    element = page.locator(selector).first
                    if element.count() > 0:
                        # Check if it's visible, scroll to it if needed
                        element.scroll_into_view_if_needed()
                        time.sleep(0.5)
                        if element.is_visible():
                            element.click()
                            clicked = True
                            print(f"Clicked Additional CSS using: {selector}")
                            break
                except Exception as e:
                    print(f"  Selector {selector} failed: {e}")
                    continue

            if not clicked:
                # Try clicking by text directly
                try:
                    page.click('text=Additional CSS', timeout=5000)
                    clicked = True
                    print("Clicked Additional CSS using text selector")
                except:
                    pass

            if not clicked:
                take_screenshot(page, "03b-cannot-find-additional-css")
                print("Could not find Additional CSS - it may need to be accessed differently")
                # Try using the URL directly for Additional CSS
                print("Trying direct URL to Additional CSS...")
                page.goto("https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css", wait_until='domcontentloaded')
                time.sleep(3)

            time.sleep(2)
            take_screenshot(page, "04-additional-css-panel")

            # Step 5: Add the CSS
            print("Adding CSS...")

            css_added = False

            # Try CodeMirror first (WordPress typically uses this)
            codemirror = page.locator('.CodeMirror')
            if codemirror.count() > 0:
                print("Found CodeMirror editor")
                # CodeMirror requires clicking to focus, then typing
                codemirror.first.click()
                time.sleep(0.5)

                # Get existing CSS first
                existing_css = page.evaluate("""
                    () => {
                        const cm = document.querySelector('.CodeMirror');
                        if (cm && cm.CodeMirror) {
                            return cm.CodeMirror.getValue();
                        }
                        return '';
                    }
                """)
                print(f"Existing CSS length: {len(existing_css)} chars")

                # Append new CSS
                new_css = existing_css.rstrip() + "\n\n" + CSS_TO_ADD

                page.evaluate(f"""
                    () => {{
                        const cm = document.querySelector('.CodeMirror');
                        if (cm && cm.CodeMirror) {{
                            cm.CodeMirror.setValue({repr(new_css)});
                            return true;
                        }}
                        return false;
                    }}
                """)
                css_added = True
                print("CSS added via CodeMirror")
            else:
                # Try regular textarea
                css_editor_selectors = [
                    '#customize-control-custom_css textarea',
                    '.code-editor-textarea',
                    'textarea.wp-editor-area',
                    '#custom_css',
                ]
                for selector in css_editor_selectors:
                    try:
                        textarea = page.locator(selector)
                        if textarea.count() > 0:
                            existing_css = textarea.input_value()
                            new_css = existing_css.rstrip() + "\n\n" + CSS_TO_ADD
                            textarea.fill(new_css)
                            css_added = True
                            print(f"CSS added via: {selector}")
                            break
                    except Exception as e:
                        continue

            if not css_added:
                print("WARNING: Could not add CSS - editor not found")
                take_screenshot(page, "error-no-editor")

            time.sleep(1)
            take_screenshot(page, "05-css-added")

            # Step 6: Publish/Save
            print("Publishing changes...")

            # Look for Publish button
            publish_selectors = [
                '#save',
                '#publish',
                'button:has-text("Publish")',
                '.customize-save-button-wrapper button',
                'input[type="submit"][value="Publish"]',
                'input#save',
            ]

            published = False
            for selector in publish_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.count() > 0 and btn.is_visible():
                        btn.click()
                        published = True
                        print(f"Clicked publish using: {selector}")
                        break
                except:
                    continue

            if not published:
                print("WARNING: Could not find publish button")
                take_screenshot(page, "error-no-publish")

            time.sleep(3)
            take_screenshot(page, "06-published")

            # Step 7: Verify by visiting the page
            print("Verifying by visiting purebrain.ai...")

            # Open new page to verify
            verify_page = context.new_page()
            verify_page.goto("https://purebrain.ai", wait_until='domcontentloaded')
            time.sleep(3)

            # Scroll to find "What Happens Next" section
            found_section = verify_page.evaluate("""
                () => {
                    // Try to find the section by various methods
                    const allElements = document.querySelectorAll('*');
                    for (const el of allElements) {
                        const text = el.textContent || '';
                        if (text.toLowerCase().includes('what happens next') ||
                            (el.className && el.className.toLowerCase().includes('what-happens')) ||
                            (el.className && el.className.toLowerCase().includes('timeline'))) {
                            el.scrollIntoView({behavior: 'instant', block: 'center'});
                            return true;
                        }
                    }
                    // Scroll down a bit to see more content
                    window.scrollTo(0, window.innerHeight * 3);
                    return false;
                }
            """)
            print(f"Found 'What Happens Next' section: {found_section}")
            time.sleep(1)

            take_screenshot(verify_page, "07-verification-what-happens-next")

            print("\n=== TASK COMPLETE ===")
            print(f"Screenshots saved to {SCREENSHOT_DIR}/{SCREENSHOT_PREFIX}-*.png")

            verify_page.close()

        except Exception as e:
            print(f"ERROR: {e}")
            take_screenshot(page, "error")
            raise
        finally:
            browser.close()

if __name__ == "__main__":
    main()
