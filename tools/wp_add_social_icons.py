#!/usr/bin/env python3
"""
WordPress Social Icons Widget Automation
Adds social media icons to footer via WordPress Widgets
"""

import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"

SOCIAL_HTML = '''<div style="display: flex; gap: 20px; justify-content: center; padding: 15px 0;">
    <a href="https://www.linkedin.com/company/purebrain-ai/" target="_blank" style="color: #2a93c1; font-size: 28px;">
        <svg width="28" height="28" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
    </a>
    <a href="https://www.facebook.com/PureBrainAI/" target="_blank" style="color: #2a93c1; font-size: 28px;">
        <svg width="28" height="28" fill="currentColor" viewBox="0 0 24 24"><path d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v3.385z"/></svg>
    </a>
    <a href="https://x.com/PureBrainAI" target="_blank" style="color: #2a93c1; font-size: 28px;">
        <svg width="28" height="28" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
    </a>
    <a href="https://www.instagram.com/purebrain.ai/" target="_blank" style="color: #2a93c1; font-size: 28px;">
        <svg width="28" height="28" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
    </a>
</div>'''


def take_screenshot(page, name):
    """Take screenshot and save to temp directory"""
    path = f"/tmp/wp_social_icons_{name}.png"
    page.screenshot(path=path)
    print(f"Screenshot saved: {path}")
    return path


def main():
    print("Starting WordPress Social Icons Widget Automation")
    print("=" * 60)

    with sync_playwright() as p:
        # Launch browser (headless for WSL, can be changed to headless=False for debugging)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Step 1: Navigate to WP Admin
            print("\n[Step 1] Navigating to WordPress admin...")
            page.goto(WP_URL, wait_until="networkidle", timeout=30000)
            take_screenshot(page, "01_login_page")

            # Step 2: Login - Handle GoDaddy-hosted WordPress login
            print("\n[Step 2] Logging in...")

            # Check if we're on login page
            if page.url.endswith("/wp-login.php") or "wp-login" in page.url:
                # GoDaddy WordPress shows "Log in with GoDaddy" button first
                # We need to click "Log in with username and password" link
                username_password_link = page.locator('text="Log in with username and password"')
                if username_password_link.count() > 0:
                    print("Detected GoDaddy login - clicking 'Log in with username and password'")
                    username_password_link.click()
                    page.wait_for_timeout(1000)
                    take_screenshot(page, "02_username_form_revealed")

                # Now fill in the credentials
                page.fill("#user_login", WP_USER)
                page.fill("#user_pass", WP_PASS)
                take_screenshot(page, "03_credentials_filled")
                page.click("#wp-submit")
                page.wait_for_load_state("networkidle")
                take_screenshot(page, "04_after_login")
            else:
                print("Already logged in or redirected to dashboard")
                take_screenshot(page, "02_dashboard")

            # Step 3: Navigate to Widgets
            print("\n[Step 3] Navigating to Widgets...")

            # Try different paths to widgets
            widgets_url = "https://purebrain.ai/wp-admin/widgets.php"
            page.goto(widgets_url, wait_until="networkidle", timeout=30000)
            take_screenshot(page, "05_widgets_page")

            # Step 4: Check available widget areas
            print("\n[Step 4] Looking for footer widget areas...")

            # Get all widget areas - try both classic and block editor
            widget_areas = page.locator(".widgets-holder-wrap")
            count = widget_areas.count()
            print(f"Found {count} classic widget areas")

            # Find footer areas
            footer_found = False
            footer_area_id = None

            for i in range(count):
                area = widget_areas.nth(i)
                area_text = area.inner_text()
                area_id = area.get_attribute("id")
                print(f"  Widget area {i+1}: {area_id}")

                if "footer" in area_text.lower() or "footer" in (area_id or "").lower():
                    footer_found = True
                    footer_area_id = area_id
                    print(f"  -> Found footer area: {area_id}")

            take_screenshot(page, "06_widget_areas")

            # Step 5: Add Custom HTML widget to footer
            print("\n[Step 5] Adding Custom HTML widget...")

            # WordPress Gutenberg widgets editor (new style)
            # Check if it's the new block-based widgets editor
            if page.locator(".edit-widgets-header").count() > 0:
                print("Detected block-based widgets editor")

                # Look for Footer widget area and click on it
                footer_section = page.locator('.edit-widgets-block-area:has-text("Footer")')
                if footer_section.count() > 0:
                    print("Found Footer widget area in block editor")
                    footer_section.click()
                    page.wait_for_timeout(500)

                # Click the + button to add block
                add_block_button = page.locator(".block-editor-button-block-appender, .edit-widgets-header-toolbar__inserter-toggle").first
                if add_block_button.count() > 0:
                    add_block_button.click()
                    page.wait_for_timeout(500)

                # Search for Custom HTML
                search_input = page.locator('input[placeholder="Search"], input[type="search"]').first
                if search_input.count() > 0:
                    search_input.fill("Custom HTML")
                    page.wait_for_timeout(500)
                    take_screenshot(page, "07_search_html_block")

                # Click Custom HTML block
                custom_html_option = page.locator('.block-editor-block-types-list__item:has-text("Custom HTML"), button:has-text("Custom HTML")').first
                if custom_html_option.count() > 0:
                    custom_html_option.click()
                    page.wait_for_timeout(500)

                # Fill in the HTML
                textarea = page.locator('textarea.block-editor-plain-text, textarea[aria-label*="HTML"]').last
                if textarea.count() > 0:
                    textarea.fill(SOCIAL_HTML)
                    take_screenshot(page, "08_html_entered")

                # Save/Update
                update_button = page.locator('button:has-text("Update")').first
                if update_button.count() > 0:
                    update_button.click()
                    page.wait_for_timeout(2000)
                    take_screenshot(page, "09_saved")
                    print("Saved changes via block editor")

            else:
                # Classic widgets editor
                print("Detected classic widgets editor")

                # Look for "Available Widgets" section and find Custom HTML
                available_widgets = page.locator("#available-widgets")

                # Find Custom HTML widget
                custom_html_widget = page.locator('#available-widgets .widget:has-text("Custom HTML")').first

                if custom_html_widget.count() > 0:
                    print("Found Custom HTML widget")
                    custom_html_widget.click()
                    page.wait_for_timeout(500)
                    take_screenshot(page, "07_custom_html_selected")

                    # Select footer area from dropdown (look for select that appeared)
                    widget_select = page.locator("#available-widgets select, .widget-inside select").first
                    if widget_select.count() > 0:
                        # Get all options and find footer
                        options = widget_select.locator("option").all_text_contents()
                        footer_option = None
                        for opt in options:
                            if "footer" in opt.lower():
                                footer_option = opt
                                break
                        if footer_option:
                            widget_select.select_option(label=footer_option)
                            print(f"Selected footer area: {footer_option}")

                    # Click Add Widget button
                    add_widget_btn = page.locator('#available-widgets input[value="Add Widget"], .widget-control-save').first
                    if add_widget_btn.count() > 0:
                        add_widget_btn.click()
                        page.wait_for_timeout(1000)
                        take_screenshot(page, "08_widget_added")

                    # Now find the newly added widget in the footer area and fill in content
                    # The widget should now be in the sidebar area
                    # Look for expanded Custom HTML widget with textarea
                    content_textarea = page.locator('.widget:has-text("Custom HTML") textarea.content, .widget-inside textarea').last
                    if content_textarea.count() > 0:
                        content_textarea.fill(SOCIAL_HTML)
                        take_screenshot(page, "09_content_filled")

                        # Save
                        save_btn = page.locator('.widget:has-text("Custom HTML") input[value="Save"], .widget-control-save').last
                        if save_btn.count() > 0:
                            save_btn.click()
                            page.wait_for_timeout(2000)
                            take_screenshot(page, "10_saved")
                            print("Saved Custom HTML widget")
                else:
                    print("Custom HTML widget not found in available widgets")
                    take_screenshot(page, "07_no_custom_html")

            # Step 6: Verify on frontend
            print("\n[Step 6] Verifying on frontend...")
            page.goto("https://purebrain.ai", wait_until="networkidle", timeout=30000)

            # Scroll to footer
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            take_screenshot(page, "11_frontend_footer")

            # Check for social icons
            linkedin = page.locator('a[href*="linkedin.com/company/purebrain"]')
            if linkedin.count() > 0:
                print("SUCCESS: LinkedIn icon found in footer!")
            else:
                print("LinkedIn icon not found yet - may need manual verification")

            print("\n" + "=" * 60)
            print("Automation complete!")
            print("Screenshots saved to /tmp/wp_social_icons_*.png")
            print("Please verify the footer at https://purebrain.ai")

        except PlaywrightTimeout as e:
            print(f"Timeout error: {e}")
            take_screenshot(page, "error_timeout")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "error_general")
            return 1
        finally:
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
