#!/usr/bin/env python3
"""
Check for code injection plugins and Elementor footer access
"""

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"


def take_screenshot(page, name):
    path = f"/tmp/wp_check_{name}.png"
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
    print("Checking for Code Plugins and Elementor Footer Access")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            print("\n[Step 1] Logging in...")
            login(page)

            # Check installed plugins
            print("\n[Step 2] Checking installed plugins...")
            page.goto("https://purebrain.ai/wp-admin/plugins.php", wait_until="networkidle", timeout=30000)
            take_screenshot(page, "01_plugins")

            # Look for header/footer script plugins
            plugins = page.locator('tr.active, tr.inactive').all()
            print(f"Found {len(plugins)} plugins")

            code_plugins = []
            for plugin in plugins[:30]:  # Check first 30
                text = plugin.text_content()
                if any(kw in text.lower() for kw in ['header', 'footer', 'script', 'code', 'snippet', 'insert', 'wpcode']):
                    plugin_name = plugin.locator('.plugin-title strong').text_content() if plugin.locator('.plugin-title strong').count() > 0 else "Unknown"
                    code_plugins.append(plugin_name)
                    print(f"  Found code plugin: {plugin_name}")

            # Check Elementor
            print("\n[Step 3] Checking Elementor access...")
            page.goto("https://purebrain.ai/wp-admin/admin.php?page=elementor",
                      wait_until="networkidle", timeout=30000)
            take_screenshot(page, "02_elementor")

            # Check for Elementor Theme Builder
            print("\n[Step 4] Checking Elementor Theme Builder...")
            page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=elementor_library&tabs_group=theme",
                      wait_until="networkidle", timeout=30000)
            take_screenshot(page, "03_theme_builder")

            # Look for footer template
            templates = page.locator('tr.type-elementor_library').all()
            print(f"Found {len(templates)} Elementor templates")
            for t in templates[:10]:
                title = t.locator('.row-title').text_content() if t.locator('.row-title').count() > 0 else ""
                if "footer" in title.lower():
                    print(f"  Found footer template: {title}")
                    # Get the edit link
                    edit_link = t.locator('a.row-title').get_attribute('href') if t.locator('a.row-title').count() > 0 else None
                    if edit_link:
                        print(f"    Edit URL: {edit_link}")

            # Check WP File Manager plugin
            print("\n[Step 5] Checking WP File Manager...")
            page.goto("https://purebrain.ai/wp-admin/admin.php?page=wp_file_manager",
                      wait_until="networkidle", timeout=30000)
            take_screenshot(page, "04_file_manager")

            # Check if we can add header/footer scripts via GoDaddy
            print("\n[Step 6] Checking GoDaddy Site Customization...")
            page.goto("https://purebrain.ai/wp-admin/admin.php?page=starter-starter",
                      wait_until="networkidle", timeout=30000)
            take_screenshot(page, "05_godaddy_starter")

            # Summary
            print("\n" + "=" * 60)
            print("SUMMARY:")
            print(f"  Code plugins found: {code_plugins if code_plugins else 'None'}")
            print("\n  Next steps:")
            print("  1. Install WPCode or Header/Footer Scripts plugin")
            print("  2. Or use Elementor to edit the footer template directly")
            print("  3. Or add Social Icons widget in Elementor")

        except PlaywrightTimeout as e:
            print(f"Timeout: {e}")
            take_screenshot(page, "error")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
