#!/usr/bin/env python3
"""
PayPal Final - Direct database approach via Elementor data
"""

import json
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/tmp"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

PAYPAL_SECTION_HTML = '''<section id="paypal-purchase-section" style="padding: 60px 20px; background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(20,20,20,0.9) 100%);">
  <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
    <h2 style="font-family: 'Oswald', sans-serif; color: #f1420b; font-size: 42px; margin-bottom: 15px; text-transform: uppercase;">Ready to Start?</h2>
    <p style="color: #cccccc; font-size: 18px; margin-bottom: 40px;">Choose your Pure Brain package and begin your AI journey today.</p>
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 24px;">
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(241,66,11,0.3); border-radius: 16px; padding: 32px; width: 260px; text-align: center;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">STARTER</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$79</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick"><input type="hidden" name="business" value="support@puremarketing.ai"><input type="hidden" name="item_name" value="Pure Brain Starter"><input type="hidden" name="item_number" value="PB-STARTER"><input type="hidden" name="amount" value="79.00"><input type="hidden" name="currency_code" value="USD"><input type="hidden" name="no_shipping" value="1"><input type="hidden" name="return" value="https://purebrain.ai/thank-you/"><input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Get Started - $79</button>
        </form>
      </div>
      <div style="background: rgba(255,255,255,0.03); border: 2px solid #f1420b; border-radius: 16px; padding: 32px; width: 260px; text-align: center; position: relative;">
        <div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #f1420b; color: white; padding: 4px 16px; border-radius: 20px; font-size: 12px; font-weight: 600;">POPULAR</div>
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">PRO</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$149</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick"><input type="hidden" name="business" value="support@puremarketing.ai"><input type="hidden" name="item_name" value="Pure Brain Pro"><input type="hidden" name="item_number" value="PB-PRO"><input type="hidden" name="amount" value="149.00"><input type="hidden" name="currency_code" value="USD"><input type="hidden" name="no_shipping" value="1"><input type="hidden" name="return" value="https://purebrain.ai/thank-you/"><input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Go Pro - $149</button>
        </form>
      </div>
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(241,66,11,0.3); border-radius: 16px; padding: 32px; width: 260px; text-align: center;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">ENTERPRISE</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$499</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick"><input type="hidden" name="business" value="support@puremarketing.ai"><input type="hidden" name="item_name" value="Pure Brain Enterprise"><input type="hidden" name="item_number" value="PB-ENTERPRISE"><input type="hidden" name="amount" value="499.00"><input type="hidden" name="currency_code" value="USD"><input type="hidden" name="no_shipping" value="1"><input type="hidden" name="return" value="https://purebrain.ai/thank-you/"><input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Enterprise - $499</button>
        </form>
      </div>
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(241,66,11,0.3); border-radius: 16px; padding: 32px; width: 260px; text-align: center;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">ULTIMATE</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$999</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick"><input type="hidden" name="business" value="support@puremarketing.ai"><input type="hidden" name="item_name" value="Pure Brain Ultimate"><input type="hidden" name="item_number" value="PB-ULTIMATE"><input type="hidden" name="amount" value="999.00"><input type="hidden" name="currency_code" value="USD"><input type="hidden" name="no_shipping" value="1"><input type="hidden" name="return" value="https://purebrain.ai/thank-you/"><input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Ultimate - $999</button>
        </form>
      </div>
    </div>
  </div>
</section>'''

def screenshot(page, name):
    path = f"{SCREENSHOT_DIR}/paypal-final-{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"Screenshot: {path}")
    return path

def login(page):
    print("Logging in...")
    page.goto("https://purebrain.ai/wp-admin/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    pw_link = page.get_by_text("Log in with username and password")
    if pw_link.count() > 0:
        pw_link.click()
        page.wait_for_timeout(2000)

    if page.locator("#user_login").is_visible():
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        try:
            page.wait_for_url("**/wp-admin/**", timeout=15000)
        except:
            pass
        page.wait_for_timeout(3000)

    return "wp-admin" in page.url

def get_elementor_data(page):
    """Get the current Elementor data for page 174"""
    print("\nFetching Elementor data...")

    result = page.evaluate('''
        async () => {
            const nonce = window.wpApiSettings?.nonce;
            if (!nonce) return { error: 'No nonce' };

            // Get post meta including Elementor data
            const resp = await fetch('/wp-json/wp/v2/pages/174?context=edit', {
                headers: { 'X-WP-Nonce': nonce }
            });

            if (!resp.ok) return { error: 'Failed to fetch page' };

            const data = await resp.json();

            return {
                id: data.id,
                title: data.title.raw || data.title.rendered,
                meta: data.meta,
                has_elementor: !!data.meta?._elementor_data,
                elementor_data_length: data.meta?._elementor_data?.length || 0
            };
        }
    ''')

    print(f"Page info: {result}")
    return result

def update_via_post_editor(page):
    """Update the page by finding the main HTML widget in the Gutenberg/code view"""
    print("\nOpening page in code editor mode...")

    # Go to the edit page
    page.goto("https://purebrain.ai/wp-admin/post.php?post=174&action=edit", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    screenshot(page, "01-editor")

    # Check if we can access the code editor
    # Look for the options menu or code editing mode

    # In Gutenberg, there's an "Edit as HTML" option in the More Options menu
    more_options = page.locator("button[aria-label='Options'], button.components-dropdown-menu__toggle")
    if more_options.count() > 0:
        print("Found options menu")
        more_options.first.click()
        page.wait_for_timeout(500)

        # Look for "Code editor" option
        code_editor_btn = page.locator("button:has-text('Code editor')")
        if code_editor_btn.count() > 0:
            print("Switching to code editor...")
            code_editor_btn.click()
            page.wait_for_timeout(2000)

            screenshot(page, "02-code-editor")

    # Now we should have access to the raw content
    # Try to find the textarea with the HTML content
    code_textarea = page.locator("textarea.editor-post-text-editor, textarea[name='content']")

    if code_textarea.count() > 0 and code_textarea.is_visible():
        print("Found code editor textarea")

        # Get current content
        current = code_textarea.input_value()
        print(f"Content length: {len(current)}")

        # Check if PayPal already exists
        if 'paypal.com' in current:
            print("PayPal buttons already in content!")
            return True

        # The content is likely raw HTML for an Elementor HTML widget
        # We need to add our PayPal section

        # Find a good insertion point - look for the end of the main content
        # Usually before closing tags like </body>, </main>, or similar

        insert_points = ['</body>', '</main>', '</article>', '</section>']
        inserted = False

        for point in insert_points:
            if point in current:
                # Insert our PayPal section before this closing tag
                new_content = current.replace(point, PAYPAL_SECTION_HTML + '\n' + point, 1)
                print(f"Inserting before {point}")
                inserted = True
                break

        if not inserted:
            # Just append to end
            new_content = current + '\n' + PAYPAL_SECTION_HTML
            print("Appending to end")

        # Clear and fill is slow for large content, so let's try a different approach
        # Use JavaScript to set the value directly
        escaped = new_content.replace('\\', '\\\\').replace('`', '\\`')

        result = page.evaluate(f'''
            () => {{
                const textarea = document.querySelector('textarea.editor-post-text-editor, textarea[name="content"]');
                if (textarea) {{
                    textarea.value = `{escaped}`;
                    // Trigger change event
                    textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    return {{ success: true }};
                }}
                return {{ error: 'Textarea not found' }};
            }}
        ''')

        print(f"Content update result: {result}")

        if result.get('success'):
            # Now save/update the page
            print("Saving changes...")
            page.wait_for_timeout(2000)

            update_btn = page.locator("button:has-text('Update'), button:has-text('Save'), button.editor-post-publish-button")
            if update_btn.count() > 0:
                update_btn.first.click()
                page.wait_for_timeout(5000)
                screenshot(page, "03-saved")
                return True

    else:
        print("Code editor textarea not accessible")
        screenshot(page, "02-no-code-editor")

    return False

def verify(page):
    """Verify PayPal buttons appear on the page"""
    print("\n=== Verification ===")

    page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Scroll through the page
    for i in range(15):
        page.evaluate("window.scrollBy(0, 500)")
        page.wait_for_timeout(200)

    screenshot(page, "04-verify")

    # Check for PayPal
    paypal_forms = page.locator("form[action*='paypal']").count()
    print(f"PayPal forms found: {paypal_forms}")

    # Check source
    html = page.content()
    has_paypal = 'paypal.com/cgi-bin/webscr' in html
    print(f"PayPal in page source: {has_paypal}")

    return paypal_forms > 0 or has_paypal

def main():
    print("=" * 60)
    print("PayPal Final Integration")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            if not login(page):
                print("Login failed")
                return

            # Check current state
            get_elementor_data(page)

            # Try to update via editor
            update_via_post_editor(page)

            # Verify
            if verify(page):
                print("\nSUCCESS: PayPal buttons are now on the page!")
            else:
                print("\nPayPal buttons not found - may need manual Elementor editing")

                # Save the HTML for manual use
                with open("/tmp/paypal_section.html", "w") as f:
                    f.write(PAYPAL_SECTION_HTML)
                print("PayPal HTML saved to /tmp/paypal_section.html for manual insertion")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            screenshot(page, "error")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
