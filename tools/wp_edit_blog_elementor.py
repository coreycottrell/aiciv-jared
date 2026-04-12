#!/usr/bin/env python3
"""
Edit the Blog page (ID 95) in WordPress Elementor.
Navigate through WordPress UI to properly open Elementor.
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
    print("WordPress Blog Page Elementor Editor")
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
            take_screenshot(page, "01_logged_in")

            # Step 2: Go directly to Pages > Edit Blog page
            print("\n[Step 2] Going to edit Blog page...")
            page.goto(f"https://purebrain.ai/wp-admin/post.php?post={BLOG_PAGE_ID}&action=edit",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            take_screenshot(page, "02_edit_page")

            print(f"  Current URL: {page.url}")

            # Check if there's an "Edit with Elementor" button
            print("\n[Step 3] Looking for 'Edit with Elementor' button...")

            elementor_btn = page.locator('a:has-text("Edit with Elementor"), #elementor-switch-mode-button')
            if elementor_btn.count() > 0:
                print("  Found 'Edit with Elementor' button!")
                elementor_btn.first.click()
                page.wait_for_timeout(8000)  # Wait for Elementor to load
                take_screenshot(page, "03_elementor_opened")
            else:
                print("  'Edit with Elementor' button not found")
                print("  This page might not be Elementor-enabled or might be a special Posts page")

                # Let's check the page content and see what's there
                page_content = page.locator('#content, #wp-content-editor-container, .edit-post-visual-editor').first
                if page_content.count() > 0:
                    print("  Found page content area")

            # Check if we're now in Elementor
            if '#elementor' in page.url or 'elementor' in page.url:
                print("\n[Step 4] In Elementor editor!")

                # Wait for Elementor panel
                try:
                    page.wait_for_selector('#elementor-panel', timeout=15000)
                    print("  Elementor panel loaded")
                except:
                    print("  Elementor panel not found")

                take_screenshot(page, "04_elementor_panel")

                # Look for HTML widget
                iframe = page.frame_locator('iframe#elementor-preview-iframe')

                html_widget_selectors = [
                    '[data-widget_type="html.default"]',
                    '.elementor-widget-html',
                    '[data-widget_type*="html"]',
                ]

                widget_found = False
                for selector in html_widget_selectors:
                    try:
                        widget = iframe.locator(selector).first
                        if widget.count() > 0:
                            print(f"  Found HTML widget: {selector}")
                            widget.click()
                            page.wait_for_timeout(2000)
                            widget_found = True
                            take_screenshot(page, "05_html_widget_clicked")
                            break
                    except Exception as e:
                        print(f"  Selector {selector}: {e}")

                if widget_found:
                    # Find and edit the HTML content
                    print("\n[Step 5] Editing HTML content...")

                    # Try CodeMirror first
                    try:
                        result = page.evaluate(f"""
                            (content) => {{
                                const cm = document.querySelector('.CodeMirror');
                                if (cm && cm.CodeMirror) {{
                                    cm.CodeMirror.setValue(content);
                                    // Trigger change event
                                    cm.CodeMirror.focus();
                                    return 'codemirror';
                                }}
                                // Try textarea
                                const textarea = document.querySelector('.elementor-control-html textarea, textarea[data-setting="html"]');
                                if (textarea) {{
                                    textarea.value = content;
                                    textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    return 'textarea';
                                }}
                                return 'not_found';
                            }}
                        """, html_content)
                        print(f"  HTML set via: {result}")
                        page.wait_for_timeout(2000)
                        take_screenshot(page, "06_html_set")
                    except Exception as e:
                        print(f"  Error setting HTML: {e}")

                    # Save/Update
                    print("\n[Step 6] Saving page...")
                    update_btn = page.locator('#elementor-panel-saver-button-publish, button:has-text("Update")').first
                    if update_btn.count() > 0:
                        update_btn.click()
                        page.wait_for_timeout(5000)
                        take_screenshot(page, "07_saved")
                        print("  Page saved!")
                    else:
                        print("  Update button not found")
                        take_screenshot(page, "07_no_update_btn")
                else:
                    print("\n  No HTML widget found. Need to add one or use different approach.")
                    take_screenshot(page, "05_no_html_widget")

            else:
                # Not in Elementor - maybe need to check if this is a Posts Page
                print("\n[Step 4] Not in Elementor. Checking page type...")
                print(f"  Current URL: {page.url}")
                take_screenshot(page, "04_not_elementor")

                # Check if this is set as the Posts Page (WordPress static blog page)
                print("\n  This might be the Posts Page, not an Elementor page.")
                print("  The Blog page showing posts is typically handled by the theme, not Elementor.")
                print("\n  Options:")
                print("  1. Convert Blog page to Elementor and add HTML widget")
                print("  2. Use Custom CSS/HTML in theme settings")
                print("  3. Create a new page with the HTML content")

            # Final verification
            print("\n[Step 7] Viewing live blog page...")
            page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            take_screenshot(page, "08_live_blog")

            print("\n" + "=" * 70)
            print("COMPLETE!")
            print(f"Screenshots saved to: {SCREENSHOT_DIR}/")
            print("=" * 70)

        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "error")
            return 1
        finally:
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
