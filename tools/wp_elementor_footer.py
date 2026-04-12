#!/usr/bin/env python3
"""
Access Elementor Theme Builder to edit the footer template
"""

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"


def take_screenshot(page, name):
    path = f"/tmp/wp_elementor_{name}.png"
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
    print("Accessing Elementor Theme Builder for Footer")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            print("\n[Step 1] Logging in...")
            login(page)
            take_screenshot(page, "01_login")

            # Go to Elementor dashboard
            print("\n[Step 2] Opening Elementor...")
            page.goto("https://purebrain.ai/wp-admin/admin.php?page=elementor",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            take_screenshot(page, "02_elementor")

            # Click on Theme Builder
            print("\n[Step 3] Clicking Theme Builder...")
            theme_builder = page.locator('a:has-text("Theme Builder"), [href*="theme_templates"]')
            if theme_builder.count() > 0:
                theme_builder.first.click()
                page.wait_for_timeout(3000)
                take_screenshot(page, "03_theme_builder")
            else:
                # Try direct URL
                print("  Trying direct URL...")
                page.goto("https://purebrain.ai/wp-admin/admin.php?page=elementor-app&ver=3.35.4#/site-editor/templates/footer",
                          wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)
                take_screenshot(page, "03_theme_builder_direct")

            # Look for footer template
            print("\n[Step 4] Looking for footer template...")

            # Check current page content
            page_text = page.text_content('body')
            if 'footer' in page_text.lower():
                print("  Found 'footer' in page content")

            # Look for footer template link/button
            footer_elem = page.locator('[class*="footer"], [data-type="footer"], :has-text("Footer"):visible').first
            if footer_elem.count() > 0:
                print("  Found footer element")
                take_screenshot(page, "04_footer_found")

            # Try Elementor Template Library
            print("\n[Step 5] Checking Elementor Template Library...")
            page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=elementor_library",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            take_screenshot(page, "05_template_library")

            # List all templates
            templates = page.locator('tr.type-elementor_library .row-title').all()
            print(f"  Found {len(templates)} templates")
            for t in templates:
                title = t.text_content()
                print(f"    - {title}")
                if 'footer' in title.lower():
                    edit_url = t.get_attribute('href')
                    print(f"      Edit URL: {edit_url}")

            # Try editing the homepage to find footer section
            print("\n[Step 6] Checking homepage for footer section ID...")
            page.goto("https://purebrain.ai/wp-admin/post.php?post=11&action=elementor",
                      wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            take_screenshot(page, "06_elementor_editor")

            print("\n" + "=" * 60)
            print("ANALYSIS COMPLETE")
            print("\nTo add social icons to the footer:")
            print("1. Open Elementor on the homepage (post ID 11)")
            print("2. Scroll to the footer section")
            print("3. Add a Social Icons widget")
            print("4. Configure with these URLs:")
            print("   - LinkedIn: https://www.linkedin.com/company/purebrain-ai/")
            print("   - Facebook: https://www.facebook.com/PureBrainAI/")
            print("   - Twitter/X: https://x.com/PureBrainAI")
            print("   - Instagram: https://www.instagram.com/purebrain.ai/")
            print("\nScreenshots saved to /tmp/wp_elementor_*.png")

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
