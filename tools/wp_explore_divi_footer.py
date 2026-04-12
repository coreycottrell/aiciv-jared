#!/usr/bin/env python3
"""
WordPress/Divi Footer Explorer
Explores the Divi theme settings to find where to add footer social icons
"""

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"


def take_screenshot(page, name):
    """Take screenshot and save to temp directory"""
    path = f"/tmp/wp_divi_explore_{name}.png"
    page.screenshot(path=path)
    print(f"Screenshot saved: {path}")
    return path


def login(page):
    """Handle WordPress login"""
    page.goto(WP_URL, wait_until="networkidle", timeout=30000)

    if page.url.endswith("/wp-login.php") or "wp-login" in page.url:
        username_password_link = page.locator('text="Log in with username and password"')
        if username_password_link.count() > 0:
            print("Clicking 'Log in with username and password'")
            username_password_link.click()
            page.wait_for_timeout(1000)

        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")
        print("Logged in successfully")


def main():
    print("Exploring Divi Footer Options")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Login
            print("\n[Step 1] Logging in...")
            login(page)
            take_screenshot(page, "01_dashboard")

            # Check Divi Theme Options
            print("\n[Step 2] Checking Divi Theme Options...")
            page.goto("https://purebrain.ai/wp-admin/admin.php?page=et_divi_options",
                      wait_until="networkidle", timeout=30000)
            take_screenshot(page, "02_divi_options")

            # Look for footer-related tabs in Divi options
            page.wait_for_timeout(1000)

            # Check for General Settings tab (often has footer settings)
            general_tab = page.locator('a:has-text("General")')
            if general_tab.count() > 0:
                print("Found General tab")
                general_tab.click()
                page.wait_for_timeout(500)
                take_screenshot(page, "03_general_tab")

            # Check for Footer tab
            footer_tab = page.locator('a:has-text("Footer")')
            if footer_tab.count() > 0:
                print("Found Footer tab")
                footer_tab.click()
                page.wait_for_timeout(500)
                take_screenshot(page, "04_footer_tab")

            # Check for Social tab (social icons might be there)
            social_tab = page.locator('a:has-text("Social")')
            if social_tab.count() > 0:
                print("Found Social tab")
                social_tab.click()
                page.wait_for_timeout(500)
                take_screenshot(page, "05_social_tab")

            # Check Divi Theme Builder
            print("\n[Step 3] Checking Divi Theme Builder...")
            page.goto("https://purebrain.ai/wp-admin/admin.php?page=et_theme_builder",
                      wait_until="networkidle", timeout=30000)
            take_screenshot(page, "06_theme_builder")

            # Look for Global Footer template
            footer_template = page.locator(':has-text("Footer"):visible').first
            if footer_template.count() > 0:
                print("Found footer in Theme Builder")

            # Check Theme Customizer
            print("\n[Step 4] Checking Theme Customizer...")
            page.goto("https://purebrain.ai/wp-admin/customize.php",
                      wait_until="networkidle", timeout=60000)
            take_screenshot(page, "07_customizer")

            # Look for footer-related sections in customizer
            page.wait_for_timeout(2000)

            # Click on Footer & General Settings if available
            footer_section = page.locator('li:has-text("Footer")').first
            if footer_section.count() > 0:
                print("Found Footer section in Customizer")
                footer_section.click()
                page.wait_for_timeout(1000)
                take_screenshot(page, "08_customizer_footer")

            # Check Appearance menu for footer
            print("\n[Step 5] Checking Appearance > Theme File Editor for footer.php...")
            page.goto("https://purebrain.ai/wp-admin/theme-editor.php",
                      wait_until="networkidle", timeout=30000)
            take_screenshot(page, "09_theme_editor")

            # Look for footer.php in the file list
            footer_file = page.locator('a:has-text("footer.php")').first
            if footer_file.count() > 0:
                print("Found footer.php - clicking to view")
                footer_file.click()
                page.wait_for_timeout(1000)
                take_screenshot(page, "10_footer_php")

            # Final check: Look at the actual footer on the site
            print("\n[Step 6] Examining actual footer on frontend...")
            page.goto("https://purebrain.ai", wait_until="networkidle", timeout=30000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
            take_screenshot(page, "11_frontend_footer")

            # Get footer HTML structure
            footer_html = page.evaluate("""
                () => {
                    const footer = document.querySelector('footer, #footer, .footer, #et-footer, .et-footer');
                    if (footer) {
                        return {
                            tag: footer.tagName,
                            id: footer.id,
                            class: footer.className,
                            children: Array.from(footer.children).map(c => c.className || c.tagName).slice(0, 10)
                        };
                    }
                    return 'No footer element found';
                }
            """)
            print(f"Footer structure: {footer_html}")

            print("\n" + "=" * 60)
            print("Exploration complete!")
            print("Screenshots saved to /tmp/wp_divi_explore_*.png")
            print("\nSUMMARY OF FINDINGS:")
            print("- Check screenshots to determine best approach for adding social icons")

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
