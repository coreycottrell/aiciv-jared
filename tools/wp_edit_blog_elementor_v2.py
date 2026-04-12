#!/usr/bin/env python3
"""
Edit the Blog page (ID 95) in WordPress Elementor.
The page uses Elementor Canvas template - we need to find and edit the HTML widget.
"""

import sys
import os
from playwright.sync_api import sync_playwright

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"
BLOG_PAGE_ID = 95

HTML_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-blog-page-v2.html"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/blog_edit"


def take_screenshot(page, name):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"Screenshot saved: {path}")
    return path


def login(page):
    """Log into WordPress admin"""
    page.goto(WP_URL, wait_until="networkidle", timeout=30000)
    if page.url.endswith("/wp-login.php") or "wp-login" in page.url:
        link = page.locator('text="Log in with username and password"')
        if link.count() > 0:
            link.click()
            page.wait_for_timeout(1000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")
    print(f"Logged in. URL: {page.url}")


def main():
    print("=" * 70)
    print("WordPress Blog Page Elementor Editor v2")
    print("=" * 70)

    # Read HTML content
    if not os.path.exists(HTML_FILE):
        print(f"ERROR: HTML file not found: {HTML_FILE}")
        return 1

    with open(HTML_FILE, 'r') as f:
        html_content = f.read()
    print(f"HTML content loaded: {len(html_content)} characters")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Step 1: Login
            print("\n[Step 1] Logging in...")
            login(page)
            take_screenshot(page, "v2_01_logged_in")

            # Step 2: Go directly to Elementor editor for page 95
            print("\n[Step 2] Opening page in Elementor directly...")
            # Use the direct Elementor URL format
            elementor_url = f"https://purebrain.ai/?p={BLOG_PAGE_ID}&elementor=1"
            # Alternative: use the admin URL
            elementor_admin_url = f"https://purebrain.ai/wp-admin/post.php?post={BLOG_PAGE_ID}&action=elementor"

            print(f"  Trying: {elementor_admin_url}")
            page.goto(elementor_admin_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(10000)  # Wait for Elementor to fully load
            take_screenshot(page, "v2_02_elementor_loading")

            print(f"  Current URL: {page.url}")

            # Check if Elementor loaded
            elementor_panel = page.locator('#elementor-panel')
            if elementor_panel.count() > 0:
                print("  Elementor panel detected!")
            else:
                print("  Elementor panel not detected yet. Checking for loading screen...")
                # Wait more for Elementor
                page.wait_for_timeout(5000)
                take_screenshot(page, "v2_02b_waiting")

            # Step 3: Navigate through Elementor
            print("\n[Step 3] Looking for HTML widget in Elementor...")

            # Wait for the preview iframe
            try:
                page.wait_for_selector('iframe#elementor-preview-iframe', timeout=20000)
                print("  Preview iframe found!")
            except:
                print("  Preview iframe not found. Trying alternate methods...")
                # Try to access via iframe name
                iframes = page.locator('iframe').all()
                print(f"  Found {len(iframes)} iframes on page")

            take_screenshot(page, "v2_03_elementor_loaded")

            # Try to access the preview iframe
            iframe = page.frame_locator('iframe#elementor-preview-iframe')

            # Look for widgets in the iframe
            print("\n[Step 4] Searching for widgets...")

            widget_types = [
                ('[data-widget_type="html.default"]', 'HTML Widget'),
                ('.elementor-widget-html', 'HTML Widget (class)'),
                ('[data-widget_type="text-editor.default"]', 'Text Editor'),
                ('[data-widget_type="heading.default"]', 'Heading'),
                ('.elementor-section', 'Section'),
                ('.elementor-widget', 'Any Widget'),
            ]

            for selector, name in widget_types:
                try:
                    elements = iframe.locator(selector).all()
                    print(f"  {name}: {len(elements)} found")
                    if elements and 'html' in selector.lower():
                        # Click the first HTML widget
                        elements[0].click()
                        page.wait_for_timeout(2000)
                        take_screenshot(page, "v2_04_widget_clicked")
                        break
                except Exception as e:
                    print(f"  {name}: Error - {e}")

            # Step 5: Check the panel for content editor
            print("\n[Step 5] Looking for content editor in panel...")

            # Check if CodeMirror editor is visible
            codemirror = page.locator('.CodeMirror')
            textarea = page.locator('.elementor-control-html textarea, textarea[data-setting="html"]')

            if codemirror.count() > 0:
                print("  CodeMirror editor found!")
                # Set content via CodeMirror
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
                print("  Content set via CodeMirror!")
                take_screenshot(page, "v2_05_content_set")
            elif textarea.count() > 0:
                print("  Textarea editor found!")
                textarea.first.fill(html_content)
                print("  Content set via textarea!")
                take_screenshot(page, "v2_05_content_set")
            else:
                print("  No HTML editor found in panel")
                # Maybe we need to add an HTML widget first
                print("\n  Trying to add HTML widget via panel...")

                # Look for widget search or panel
                search = page.locator('#elementor-panel-elements-search-input')
                if search.count() > 0:
                    search.fill("html")
                    page.wait_for_timeout(1000)
                    take_screenshot(page, "v2_05b_searching_html")

                    # Look for HTML widget in the search results
                    html_widget_option = page.locator('.elementor-element:has-text("HTML")').first
                    if html_widget_option.count() > 0:
                        print("  Found HTML widget option in panel!")
                        take_screenshot(page, "v2_05c_html_widget_found")
                    else:
                        print("  HTML widget not found in search results")
                else:
                    print("  Search input not found")
                take_screenshot(page, "v2_05_no_editor")

            # Step 6: Save the page
            print("\n[Step 6] Saving the page...")

            # Multiple save button selectors
            save_selectors = [
                '#elementor-panel-saver-button-publish',
                '#elementor-panel-saver-menu-save-options',
                'button:has-text("Update")',
                'button:has-text("Publish")',
                '.elementor-saver-button',
            ]

            saved = False
            for selector in save_selectors:
                btn = page.locator(selector).first
                if btn.count() > 0:
                    print(f"  Found save button: {selector}")
                    btn.click()
                    page.wait_for_timeout(5000)
                    take_screenshot(page, "v2_06_saved")
                    saved = True
                    break

            if not saved:
                print("  Save button not found")
                take_screenshot(page, "v2_06_no_save_btn")

            # Step 7: View the live page
            print("\n[Step 7] Viewing live blog page...")
            page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)
            take_screenshot(page, "v2_07_live_blog")

            # Scroll down to capture more
            page.evaluate("window.scrollBy(0, 800)")
            page.wait_for_timeout(1000)
            take_screenshot(page, "v2_07b_live_blog_scrolled")

            print("\n" + "=" * 70)
            print("COMPLETE!")
            print(f"Screenshots saved to: {SCREENSHOT_DIR}/")
            print("=" * 70)

        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "v2_error")
            return 1
        finally:
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
