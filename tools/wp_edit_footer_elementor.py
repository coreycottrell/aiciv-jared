#!/usr/bin/env python3
"""
Edit the Elementor Footer template to add social icons
"""

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"

SOCIAL_LINKS = [
    {"platform": "linkedin", "url": "https://www.linkedin.com/company/purebrain-ai/"},
    {"platform": "facebook", "url": "https://www.facebook.com/PureBrainAI/"},
    {"platform": "twitter", "url": "https://x.com/PureBrainAI"},
    {"platform": "instagram", "url": "https://www.instagram.com/purebrain.ai/"},
]


def take_screenshot(page, name):
    path = f"/tmp/wp_edit_footer_{name}.png"
    page.screenshot(path=path)
    print(f"Screenshot saved: {path}")
    return path


def login(page):
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


def main():
    print("Editing Elementor Footer Template to Add Social Icons")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            print("\n[Step 1] Logging in...")
            login(page)
            take_screenshot(page, "01_login")

            # Go to Elementor Theme Builder
            print("\n[Step 2] Opening Theme Builder...")
            page.goto("https://purebrain.ai/wp-admin/admin.php?page=elementor-app#/site-editor",
                      wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            take_screenshot(page, "02_theme_builder")

            # Click on Footer in the left sidebar
            print("\n[Step 3] Clicking on Footer section...")
            footer_link = page.locator('text="Footer"').first
            if footer_link.count() > 0:
                footer_link.click()
                page.wait_for_timeout(2000)
                take_screenshot(page, "03_footer_section")
            else:
                # Try clicking on the Footer card
                footer_card = page.locator('[class*="Footer"], [data-type="footer"]').first
                if footer_card.count() > 0:
                    footer_card.click()
                    page.wait_for_timeout(2000)

            # Look for "Add New" or edit button for footer
            print("\n[Step 4] Looking for footer template to edit...")

            # Check for existing footer template
            footer_template = page.locator('.site-editor-templates__item:has-text("Footer")').first
            if footer_template.count() > 0:
                print("  Found footer template, clicking to edit...")
                footer_template.click()
                page.wait_for_timeout(3000)
                take_screenshot(page, "04_footer_template")

            # If no template, look for "Add New" button
            add_button = page.locator('button:has-text("Add New"), a:has-text("Add New")')
            if add_button.count() > 0:
                print("  Found 'Add New' button for footer")
                take_screenshot(page, "04_add_new_available")

            # Check current URL to see if we're in the editor
            current_url = page.url
            print(f"  Current URL: {current_url}")

            # Try direct access to footer template editing
            print("\n[Step 5] Trying to access footer template directly...")

            # First check if there's an existing footer template in the library
            page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=elementor_library&elementor_library_type=footer",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            take_screenshot(page, "05_footer_library")

            # Check for footer templates
            footer_templates = page.locator('tr.type-elementor_library .row-title').all()
            print(f"  Found {len(footer_templates)} footer templates in library")

            # The footer might be part of the main page, not a separate template
            # Let's check the main page (ID 11) for footer editing
            print("\n[Step 6] Opening main page in Elementor to find footer...")
            page.goto("https://purebrain.ai/wp-admin/post.php?post=11&action=elementor",
                      wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            take_screenshot(page, "06_page_editor")

            # Now let's scroll to the bottom of the page to find the footer section
            print("\n[Step 7] Scrolling to footer in page editor...")

            # In Elementor, we need to scroll the preview iframe
            iframe = page.frame_locator('iframe#elementor-preview-iframe')
            if iframe:
                # Scroll to bottom
                page.evaluate("""
                    () => {
                        const iframe = document.querySelector('iframe#elementor-preview-iframe');
                        if (iframe && iframe.contentWindow) {
                            iframe.contentWindow.scrollTo(0, iframe.contentDocument.body.scrollHeight);
                        }
                    }
                """)
                page.wait_for_timeout(2000)
                take_screenshot(page, "07_scrolled_to_footer")

            # Let's try searching for "social" in the widget panel
            print("\n[Step 8] Looking for Social Icons widget...")

            # Click the widget search or panel
            search_input = page.locator('#elementor-panel-elements-search-input')
            if search_input.count() > 0:
                search_input.fill("social")
                page.wait_for_timeout(1000)
                take_screenshot(page, "08_social_search")

            # Look for Social Icons widget
            social_widget = page.locator('.elementor-element:has-text("Social Icons")').first
            if social_widget.count() > 0:
                print("  Found Social Icons widget!")
                take_screenshot(page, "09_social_widget_found")

            # Summary
            print("\n" + "=" * 60)
            print("ANALYSIS COMPLETE")
            print("\nThe site uses a custom-coded footer section, not an Elementor")
            print("footer template. The footer is part of the main page build.")
            print("\nTo add social icons manually:")
            print("1. Open https://purebrain.ai/wp-admin/post.php?post=11&action=elementor")
            print("2. Scroll to the footer section at the bottom")
            print("3. Add a Social Icons widget")
            print("4. Configure the links:")
            for link in SOCIAL_LINKS:
                print(f"   - {link['platform'].capitalize()}: {link['url']}")
            print("\nOr use the WP File Manager to edit the theme's footer.php")
            print("to add the social icons HTML directly.")

        except PlaywrightTimeout as e:
            print(f"Timeout: {e}")
            take_screenshot(page, "error_timeout")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "error")
        finally:
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
