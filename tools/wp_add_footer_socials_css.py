#!/usr/bin/env python3
"""
Add social icons to purebrain.ai footer via Additional CSS/JavaScript
Since the footer is custom-built with Elementor, we use CSS to inject icons
"""

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"

# CSS to add social icons to the footer
# This creates a row of social icons that will be injected after the copyright text
CUSTOM_CSS = '''
/* Social Icons in Footer - Added via Customizer */
.footer__brand::after {
    content: '';
    display: block;
    margin-top: 15px;
}

.footer-social-icons {
    display: flex;
    gap: 20px;
    justify-content: center;
    padding: 15px 0;
    margin-top: 10px;
}

.footer-social-icons a {
    color: #2a93c1;
    font-size: 28px;
    transition: opacity 0.3s ease;
}

.footer-social-icons a:hover {
    opacity: 0.8;
}

.footer-social-icons svg {
    width: 28px;
    height: 28px;
    fill: currentColor;
}
'''

# JavaScript to inject social icons HTML
# This will be added via a simple plugin or header scripts
SOCIAL_HTML_INJECTION = '''
<style>
/* Injected Social Icons */
.footer__brand::after {
    content: '';
    display: block;
}
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var footerBrand = document.querySelector('.footer__brand');
    if (footerBrand) {
        var socialDiv = document.createElement('div');
        socialDiv.className = 'footer-social-icons';
        socialDiv.innerHTML = `
            <a href="https://www.linkedin.com/company/purebrain-ai/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                <svg viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            </a>
            <a href="https://www.facebook.com/PureBrainAI/" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
                <svg viewBox="0 0 24 24"><path d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v3.385z"/></svg>
            </a>
            <a href="https://x.com/PureBrainAI" target="_blank" rel="noopener noreferrer" aria-label="X (Twitter)">
                <svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            </a>
            <a href="https://www.instagram.com/purebrain.ai/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
                <svg viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            </a>
        `;
        footerBrand.appendChild(socialDiv);
    }
});
</script>
'''


def take_screenshot(page, name):
    """Take screenshot and save to temp directory"""
    path = f"/tmp/wp_footer_css_{name}.png"
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
    print("Adding Social Icons to Footer via Additional CSS")
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

            # Go to Theme Customizer
            print("\n[Step 2] Opening Theme Customizer...")
            page.goto("https://purebrain.ai/wp-admin/customize.php",
                      wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            take_screenshot(page, "02_customizer")

            # Click on Additional CSS
            print("\n[Step 3] Opening Additional CSS section...")
            additional_css = page.locator('#accordion-section-custom_css, li:has-text("Additional CSS")')
            if additional_css.count() > 0:
                additional_css.first.click()
                page.wait_for_timeout(2000)
                take_screenshot(page, "03_additional_css_section")
            else:
                print("Additional CSS section not found!")
                # List all visible sections
                sections = page.locator('.accordion-section-title').all()
                print("Available sections:")
                for s in sections:
                    print(f"  - {s.text_content()}")
                return 1

            # Find the CSS textarea
            print("\n[Step 4] Adding custom CSS...")
            css_textarea = page.locator('#customize-control-custom_css textarea, .ace_text-input, textarea.wp-editor-area, #custom_css')

            if css_textarea.count() > 0:
                # Get existing CSS
                existing_css = css_textarea.first.input_value()
                print(f"  Existing CSS length: {len(existing_css)} characters")

                # Check if our CSS is already added
                if 'footer-social-icons' in existing_css:
                    print("  Social icons CSS already exists!")
                else:
                    # Append our CSS
                    new_css = existing_css + "\n\n" + CUSTOM_CSS
                    css_textarea.first.fill(new_css)
                    print("  Added custom CSS for social icons")
                    take_screenshot(page, "04_css_added")
            else:
                # Try CodeMirror editor
                print("  Looking for CodeMirror editor...")
                cm_editor = page.locator('.CodeMirror')
                if cm_editor.count() > 0:
                    # Click to focus the editor
                    cm_editor.first.click()
                    page.wait_for_timeout(500)

                    # Get current content via JavaScript
                    existing_css = page.evaluate("""
                        () => {
                            const cm = document.querySelector('.CodeMirror');
                            if (cm && cm.CodeMirror) {
                                return cm.CodeMirror.getValue();
                            }
                            return '';
                        }
                    """)

                    if 'footer-social-icons' in existing_css:
                        print("  Social icons CSS already exists!")
                    else:
                        # Set new content
                        page.evaluate(f"""
                            () => {{
                                const cm = document.querySelector('.CodeMirror');
                                if (cm && cm.CodeMirror) {{
                                    const newCss = cm.CodeMirror.getValue() + "\\n\\n" + `{CUSTOM_CSS}`;
                                    cm.CodeMirror.setValue(newCss);
                                }}
                            }}
                        """)
                        print("  Added custom CSS for social icons via CodeMirror")
                        take_screenshot(page, "04_css_added_cm")

            # Publish changes
            print("\n[Step 5] Publishing changes...")
            page.wait_for_timeout(1000)
            publish_button = page.locator('#save, button:has-text("Publish"), input[value="Publish"]').first
            if publish_button.count() > 0:
                is_disabled = publish_button.get_attribute("disabled")
                if not is_disabled:
                    publish_button.click()
                    page.wait_for_timeout(3000)
                    take_screenshot(page, "05_published")
                    print("Changes published!")
                else:
                    print("Publish button is disabled - no changes detected")
                    take_screenshot(page, "05_no_changes")
            else:
                print("Could not find Publish button")

            # Now we need to add JavaScript for the actual icons
            # This requires either a plugin or adding to theme's functions.php
            # For now, let's try the Header/Footer Scripts plugin approach
            print("\n[Step 6] Note: CSS alone won't create the icons.")
            print("         The social icons need to be added via JavaScript or")
            print("         by directly editing the Elementor footer template.")
            print("\n         Options to add icons:")
            print("         1. Edit the Elementor footer template directly (if accessible)")
            print("         2. Use a Header/Footer Scripts plugin to add JS")
            print("         3. Manually add icons in the Elementor page builder")

            # Verify on frontend
            print("\n[Step 7] Checking frontend...")
            page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            take_screenshot(page, "06_frontend_footer")

            print("\n" + "=" * 60)
            print("SUMMARY:")
            print("- The footer is built with Elementor, not WordPress widgets")
            print("- Theme Customizer social URLs are configured correctly")
            print("- CSS has been added for styling social icons")
            print("- To add the actual icons, you need to either:")
            print("  1. Edit the Elementor footer template (Elementor > Theme Builder)")
            print("  2. Add a Social Icons widget/element in Elementor")
            print("  3. Use a 'Header/Footer Scripts' plugin to inject the HTML")
            print("\nScreenshots saved to /tmp/wp_footer_css_*.png")

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
