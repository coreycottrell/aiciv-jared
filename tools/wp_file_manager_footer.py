#!/usr/bin/env python3
"""
Use WP File Manager to add social icons to the footer
"""

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"

# The social icons HTML to add after the footer__brand div
SOCIAL_ICONS_HTML = '''
            <!-- Social Icons -->
            <div class="footer__social" style="display: flex; gap: 15px; justify-content: center; margin-top: 15px;">
                <a href="https://www.linkedin.com/company/purebrain-ai/" target="_blank" rel="noopener noreferrer" style="color: #2a93c1;">
                    <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
                </a>
                <a href="https://www.facebook.com/PureBrainAI/" target="_blank" rel="noopener noreferrer" style="color: #2a93c1;">
                    <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v3.385z"/></svg>
                </a>
                <a href="https://x.com/PureBrainAI" target="_blank" rel="noopener noreferrer" style="color: #2a93c1;">
                    <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                </a>
                <a href="https://www.instagram.com/purebrain.ai/" target="_blank" rel="noopener noreferrer" style="color: #2a93c1;">
                    <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
                </a>
            </div>
'''


def take_screenshot(page, name):
    path = f"/tmp/wp_file_{name}.png"
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
    print("Using WP File Manager to Add Footer Social Icons")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            print("\n[Step 1] Logging in...")
            login(page)
            take_screenshot(page, "01_login")

            # Go to WP File Manager
            print("\n[Step 2] Opening WP File Manager...")
            page.goto("https://purebrain.ai/wp-admin/admin.php?page=wp_file_manager",
                      wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            take_screenshot(page, "02_file_manager")

            # Look for the file manager interface
            print("\n[Step 3] Looking for theme files...")

            # The file manager should show a directory structure
            # We need to navigate to wp-content/themes/[theme-name]/footer.php

            # Check if we can see the file tree
            file_tree = page.locator('.elfinder-navbar, .elfinder-tree, .wp-file-manager')
            if file_tree.count() > 0:
                print("  File manager interface found")

            # Try to find wp-content folder
            wp_content = page.locator('text="wp-content"')
            if wp_content.count() > 0:
                print("  Found wp-content folder")
                wp_content.first.dblclick()
                page.wait_for_timeout(2000)
                take_screenshot(page, "03_wp_content")

                # Look for themes folder
                themes = page.locator('text="themes"')
                if themes.count() > 0:
                    themes.first.dblclick()
                    page.wait_for_timeout(2000)
                    take_screenshot(page, "04_themes")

            # Check what theme we're using
            print("\n[Step 4] Identifying active theme...")
            page.goto("https://purebrain.ai/wp-admin/themes.php",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            take_screenshot(page, "05_themes_page")

            # Get active theme name
            active_theme = page.locator('.theme.active .theme-name, .current-theme .theme-name')
            if active_theme.count() > 0:
                theme_name = active_theme.first.text_content()
                print(f"  Active theme: {theme_name}")

            # Instead of file manager, let's try the Theme File Editor
            print("\n[Step 5] Trying Theme File Editor...")
            page.goto("https://purebrain.ai/wp-admin/theme-editor.php",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            take_screenshot(page, "06_theme_editor")

            # Dismiss any warning dialog
            understand_button = page.locator('button:has-text("I understand")')
            if understand_button.count() > 0:
                understand_button.click()
                page.wait_for_timeout(1000)

            # Look for footer.php in the file list
            print("\n[Step 6] Looking for footer.php...")
            footer_file = page.locator('a:has-text("footer.php")')
            if footer_file.count() > 0:
                print("  Found footer.php!")
                footer_file.first.click()
                page.wait_for_timeout(2000)
                take_screenshot(page, "07_footer_php")

                # Get the current content
                editor_content = page.locator('#newcontent, textarea.wp-editor-area, .CodeMirror')
                if editor_content.count() > 0:
                    current_content = page.evaluate("""
                        () => {
                            const cm = document.querySelector('.CodeMirror');
                            if (cm && cm.CodeMirror) {
                                return cm.CodeMirror.getValue();
                            }
                            const textarea = document.querySelector('#newcontent');
                            if (textarea) return textarea.value;
                            return '';
                        }
                    """)
                    print(f"  Current footer.php length: {len(current_content)} chars")

                    # Save to file for analysis
                    with open('/tmp/footer_php_current.txt', 'w') as f:
                        f.write(current_content)
                    print("  Saved current content to /tmp/footer_php_current.txt")

            print("\n" + "=" * 60)
            print("SUMMARY:")
            print("\nThe footer is defined in a custom HTML/PHP file.")
            print("To add social icons, the footer HTML needs to be modified.")
            print("\nThe HTML to add (after the footer__brand closing tag):")
            print(SOCIAL_ICONS_HTML[:500] + "...")
            print("\nScreenshots saved to /tmp/wp_file_*.png")

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
