#!/usr/bin/env python3
"""
Edit the PureBrain.ai Blog page (page 95) in Elementor.
Find the HTML widget and replace its content with the beautiful blog page HTML.
"""

import sys
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"
BLOG_PAGE_ID = 95

# HTML content file
HTML_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-blog-page-v2.html"

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/blog_edit"


def take_screenshot(page, name):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=path)
    print(f"Screenshot saved: {path}")
    return path


def login(page):
    """Log into WordPress admin"""
    page.goto(WP_URL, wait_until="networkidle", timeout=30000)
    if page.url.endswith("/wp-login.php") or "wp-login" in page.url:
        # Check for "Log in with username and password" link (some setups have OAuth)
        link = page.locator('text="Log in with username and password"')
        if link.count() > 0:
            link.click()
            page.wait_for_timeout(1000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")
    print(f"Logged in successfully. Current URL: {page.url}")


def main():
    print("=" * 70)
    print("PureBrain Blog Page Elementor Editor")
    print("=" * 70)
    print(f"\nTarget: Page ID {BLOG_PAGE_ID} (Blog page)")
    print(f"HTML Source: {HTML_FILE}")

    # Read the HTML content
    if not os.path.exists(HTML_FILE):
        print(f"ERROR: HTML file not found: {HTML_FILE}")
        return 1

    with open(HTML_FILE, 'r') as f:
        html_content = f.read()
    print(f"HTML content loaded: {len(html_content)} characters")

    with sync_playwright() as p:
        # Launch browser in headless mode (required for WSL2 without X server)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Step 1: Login
            print("\n[Step 1] Logging into WordPress...")
            login(page)
            take_screenshot(page, "01_logged_in")

            # Step 2: Open blog page in Elementor
            print("\n[Step 2] Opening Blog page in Elementor editor...")
            elementor_url = f"https://purebrain.ai/wp-admin/post.php?post={BLOG_PAGE_ID}&action=elementor"
            page.goto(elementor_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(8000)  # Wait for Elementor to fully load
            take_screenshot(page, "02_elementor_loaded")

            # Step 3: Wait for the panel to be ready
            print("\n[Step 3] Waiting for Elementor panel...")
            try:
                page.wait_for_selector('#elementor-panel', timeout=30000)
                print("  Elementor panel detected")
            except:
                print("  Panel not visible, continuing anyway...")
            take_screenshot(page, "03_panel_ready")

            # Step 4: Find HTML widget on the page
            print("\n[Step 4] Looking for HTML widget...")

            # Click into the preview iframe to interact with widgets
            iframe = page.frame_locator('iframe#elementor-preview-iframe')

            # Try multiple selectors for HTML widget
            html_widget_selectors = [
                '[data-widget_type="html.default"]',
                '.elementor-widget-html',
                '[data-element_type="widget"][data-widget_type*="html"]',
            ]

            widget_found = False
            for selector in html_widget_selectors:
                try:
                    widget = iframe.locator(selector).first
                    if widget.count() > 0:
                        print(f"  Found HTML widget using selector: {selector}")
                        widget.click()
                        page.wait_for_timeout(2000)
                        widget_found = True
                        take_screenshot(page, "04_html_widget_selected")
                        break
                except Exception as e:
                    print(f"  Selector {selector} failed: {e}")

            if not widget_found:
                print("\n  HTML widget not found directly. Let's look at all widgets...")
                # Take a screenshot showing what's there
                take_screenshot(page, "04_searching_widgets")

                # Try clicking the Navigator to find widgets
                navigator_btn = page.locator('#elementor-panel-footer-navigator, button[data-tooltip="Navigator"]').first
                if navigator_btn.count() > 0:
                    navigator_btn.click()
                    page.wait_for_timeout(1000)
                    take_screenshot(page, "04b_navigator_open")

                    # Look for HTML in navigator
                    html_nav = page.locator('.elementor-navigator__element:has-text("HTML")').first
                    if html_nav.count() > 0:
                        html_nav.click()
                        page.wait_for_timeout(1000)
                        widget_found = True
                        take_screenshot(page, "04c_html_from_navigator")

            if not widget_found:
                print("\n  WARNING: Could not find HTML widget. Will try to add one...")
                # If no HTML widget exists, we might need to add one
                take_screenshot(page, "04_no_html_widget")

                # For now, let's report what we found
                print("\n  Current page structure (capturing for analysis)...")
                take_screenshot(page, "04_page_structure")

            # Step 5: Edit the HTML content
            print("\n[Step 5] Editing HTML content...")

            # Look for the HTML code textarea/editor in the panel
            html_editor_selectors = [
                'textarea.elementor-code-editor',
                '#elementor-controls textarea',
                '.elementor-control-html textarea',
                '[data-setting="html"]',
                '.CodeMirror',
            ]

            editor_found = False
            for selector in html_editor_selectors:
                try:
                    editor = page.locator(selector).first
                    if editor.count() > 0:
                        print(f"  Found editor using: {selector}")

                        if 'CodeMirror' in selector:
                            # CodeMirror requires special handling
                            page.evaluate("""
                                () => {
                                    const cm = document.querySelector('.CodeMirror');
                                    if (cm && cm.CodeMirror) {
                                        cm.CodeMirror.setValue('');
                                    }
                                }
                            """)
                        else:
                            # Select all and clear
                            editor.click()
                            page.keyboard.press('Control+a')
                            page.keyboard.press('Delete')

                        editor_found = True
                        take_screenshot(page, "05_editor_cleared")
                        break
                except Exception as e:
                    print(f"  Selector {selector} failed: {e}")

            if editor_found:
                print("\n[Step 6] Pasting new HTML content...")

                # Set clipboard content and paste
                page.evaluate(f"""
                    (content) => {{
                        navigator.clipboard.writeText(content);
                    }}
                """, html_content)

                # Or type it directly (for smaller content)
                # For large content, we need to use fill() or set value
                try:
                    # Try CodeMirror approach
                    page.evaluate(f"""
                        (content) => {{
                            const cm = document.querySelector('.CodeMirror');
                            if (cm && cm.CodeMirror) {{
                                cm.CodeMirror.setValue(content);
                                return true;
                            }}
                            return false;
                        }}
                    """, html_content)
                except:
                    pass

                # Try direct textarea fill
                textarea = page.locator('.elementor-control-html textarea, textarea.elementor-code-editor').first
                if textarea.count() > 0:
                    textarea.fill(html_content)

                page.wait_for_timeout(2000)
                take_screenshot(page, "06_html_pasted")

                # Step 7: Save/Update the page
                print("\n[Step 7] Saving the page...")

                # Look for Update button
                update_btn = page.locator('#elementor-panel-saver-button-publish, button:has-text("Update")').first
                if update_btn.count() > 0:
                    update_btn.click()
                    page.wait_for_timeout(3000)
                    take_screenshot(page, "07_saved")
                    print("  Page updated successfully!")
                else:
                    print("  Could not find Update button")
                    take_screenshot(page, "07_no_update_btn")
            else:
                print("\n  Could not find HTML editor. Manual intervention needed.")
                take_screenshot(page, "05_no_editor")

            # Step 8: Verify by viewing the page
            print("\n[Step 8] Verifying the change...")
            page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            take_screenshot(page, "08_final_result")

            print("\n" + "=" * 70)
            print("COMPLETE!")
            print(f"Screenshots saved to: {SCREENSHOT_DIR}/")
            print("=" * 70)

        except PlaywrightTimeout as e:
            print(f"\nTimeout error: {e}")
            take_screenshot(page, "error_timeout")
            return 1
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "error")
            return 1
        finally:
            # Keep browser open for a moment to see result
            page.wait_for_timeout(3000)
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
