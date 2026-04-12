#!/usr/bin/env python3
"""
PayPal Integration v2 for purebrain.ai
- Creates Thank You page with proper content and publishes it
- Adds PayPal buttons to Pure Brain 2.0 page (which uses raw HTML in Gutenberg)
"""

import os
import sys
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# Create screenshots directory
SCREENSHOT_DIR = "/tmp"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Credentials provided
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

THANK_YOU_CONTENT = '''<div style="text-align: center; padding: 60px 20px; max-width: 800px; margin: 0 auto;">
  <h1 style="color: #f1420b; font-size: 48px; margin-bottom: 20px;">Thank You!</h1>
  <p style="font-size: 24px; color: #ffffff; margin-bottom: 30px;">Your Pure Brain journey begins now.</p>
  <p style="font-size: 18px; color: #cccccc; margin-bottom: 40px;">
    We've received your payment and our team will reach out within 24 hours to begin your onboarding.
    <br><br>
    Check your email for a confirmation and next steps.
  </p>
  <div style="background: rgba(241, 66, 11, 0.1); border: 1px solid #f1420b; border-radius: 12px; padding: 30px; margin: 40px 0;">
    <h3 style="color: #f1420b; margin-bottom: 15px;">What Happens Next?</h3>
    <ul style="text-align: left; color: #ffffff; line-height: 2;">
      <li>Within 24 hours: Personal welcome email from our team</li>
      <li>Within 48 hours: Your AI partner setup begins</li>
      <li>Within 1 week: Your Pure Brain is fully configured and ready</li>
    </ul>
  </div>
  <a href="https://purebrain.ai" style="
    display: inline-block;
    background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%);
    color: white;
    padding: 16px 40px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 8px;
    text-decoration: none;
    margin-top: 20px;
  ">Return to Homepage</a>
</div>'''

PAYPAL_BUTTONS = {
    "starter": '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display: inline-block; margin-top: 20px;">
  <input type="hidden" name="cmd" value="_xclick">
  <input type="hidden" name="business" value="support@puremarketing.ai">
  <input type="hidden" name="item_name" value="Pure Brain Starter">
  <input type="hidden" name="item_number" value="PB-STARTER">
  <input type="hidden" name="amount" value="79.00">
  <input type="hidden" name="currency_code" value="USD">
  <input type="hidden" name="no_shipping" value="1">
  <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
  <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
  <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">Get Started - $79</button>
</form>''',
    "pro": '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display: inline-block; margin-top: 20px;">
  <input type="hidden" name="cmd" value="_xclick">
  <input type="hidden" name="business" value="support@puremarketing.ai">
  <input type="hidden" name="item_name" value="Pure Brain Pro">
  <input type="hidden" name="item_number" value="PB-PRO">
  <input type="hidden" name="amount" value="149.00">
  <input type="hidden" name="currency_code" value="USD">
  <input type="hidden" name="no_shipping" value="1">
  <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
  <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
  <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">Go Pro - $149</button>
</form>''',
    "enterprise": '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display: inline-block; margin-top: 20px;">
  <input type="hidden" name="cmd" value="_xclick">
  <input type="hidden" name="business" value="support@puremarketing.ai">
  <input type="hidden" name="item_name" value="Pure Brain Enterprise">
  <input type="hidden" name="item_number" value="PB-ENTERPRISE">
  <input type="hidden" name="amount" value="499.00">
  <input type="hidden" name="currency_code" value="USD">
  <input type="hidden" name="no_shipping" value="1">
  <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
  <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
  <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">Enterprise - $499</button>
</form>''',
    "ultimate": '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display: inline-block; margin-top: 20px;">
  <input type="hidden" name="cmd" value="_xclick">
  <input type="hidden" name="business" value="support@puremarketing.ai">
  <input type="hidden" name="item_name" value="Pure Brain Ultimate">
  <input type="hidden" name="item_number" value="PB-ULTIMATE">
  <input type="hidden" name="amount" value="999.00">
  <input type="hidden" name="currency_code" value="USD">
  <input type="hidden" name="no_shipping" value="1">
  <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
  <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
  <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">Ultimate - $999</button>
</form>'''
}

def screenshot(page, name):
    """Take a screenshot with timestamp"""
    path = f"{SCREENSHOT_DIR}/paypal-integration-{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"Screenshot saved: {path}")
    return path

def login(page):
    """Login to WordPress admin"""
    print(f"Navigating to {WP_URL}...")
    page.goto(WP_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Check if we're on GoDaddy SSO login page
    password_login_link = page.get_by_text("Log in with username and password")
    if password_login_link.count() > 0:
        print("Found GoDaddy SSO page, clicking username/password option...")
        password_login_link.click()
        page.wait_for_timeout(2000)

    # Check if we're on login page
    if page.locator("#user_login").is_visible():
        print("On login page, entering credentials...")
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)

        # Click login
        print("Clicking Log In button...")
        page.click("#wp-submit")

        # Wait for navigation
        try:
            page.wait_for_url("**/wp-admin/**", timeout=15000)
        except Exception as e:
            print(f"URL wait timeout: {e}")

        page.wait_for_timeout(3000)

    print(f"Current URL after login: {page.url}")
    return "wp-admin" in page.url

def create_thank_you_page_via_api(page):
    """Create Thank You page using WordPress REST API via JavaScript"""
    print("\n=== TASK 1: Creating Thank You Page via REST API ===")

    # First, get the nonce from the admin page
    page.goto("https://purebrain.ai/wp-admin/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Escape the content for JSON
    content_escaped = THANK_YOU_CONTENT.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

    # Use JavaScript to create the page via REST API
    result = page.evaluate(f'''
        async () => {{
            try {{
                // Get nonce from wpApiSettings
                const nonce = window.wpApiSettings?.nonce || '';
                if (!nonce) {{
                    return {{ success: false, error: 'No nonce found' }};
                }}

                const response = await fetch('/wp-json/wp/v2/pages', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': nonce
                    }},
                    body: JSON.stringify({{
                        title: 'Thank You',
                        content: `{content_escaped}`,
                        status: 'publish',
                        slug: 'thank-you'
                    }})
                }});

                if (response.ok) {{
                    const data = await response.json();
                    return {{ success: true, id: data.id, link: data.link }};
                }} else {{
                    const error = await response.text();
                    return {{ success: false, error: error, status: response.status }};
                }}
            }} catch (e) {{
                return {{ success: false, error: e.toString() }};
            }}
        }}
    ''')

    print(f"REST API result: {result}")

    if result and result.get('success'):
        print(f"Thank You page created! ID: {result.get('id')}, URL: {result.get('link')}")
        return True
    else:
        print(f"REST API failed: {result}")
        return False

def create_thank_you_page_classic(page):
    """Create Thank You page using classic editor interface"""
    print("\n=== TASK 1: Creating Thank You Page (Classic Method) ===")

    # Navigate to Add New Page with classic editor
    page.goto("https://purebrain.ai/wp-admin/post-new.php?post_type=page&classic-editor", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "v2-01-add-new-page")

    # Check if we have classic editor
    title_input = page.locator("#title")
    if title_input.count() > 0 and title_input.is_visible():
        print("Using classic editor...")

        # Fill title
        title_input.fill("Thank You")
        page.wait_for_timeout(500)

        # Click Edit slug button if visible
        edit_slug = page.locator("#edit-slug-buttons button, #edit-slug-buttons a")
        if edit_slug.count() > 0:
            edit_slug.click()
            page.wait_for_timeout(500)

            slug_input = page.locator("#new-post-slug")
            if slug_input.count() > 0:
                slug_input.fill("thank-you")

                # Save slug
                save_slug = page.locator("#edit-slug-buttons .save")
                if save_slug.count() > 0:
                    save_slug.click()
                    page.wait_for_timeout(500)

        # Switch to Text/HTML mode
        text_tab = page.locator("#content-html")
        if text_tab.count() > 0 and text_tab.is_visible():
            text_tab.click()
            page.wait_for_timeout(500)

        # Fill content
        content_area = page.locator("#content")
        if content_area.count() > 0:
            content_area.fill(THANK_YOU_CONTENT)

        screenshot(page, "v2-02-content-filled")

        # Click Publish
        publish_btn = page.locator("#publish")
        if publish_btn.count() > 0:
            publish_btn.click()
            page.wait_for_timeout(5000)

        screenshot(page, "v2-03-published")
        return True

    return False

def create_thank_you_page_gutenberg(page):
    """Create Thank You page in Gutenberg with HTML block"""
    print("\n=== TASK 1: Creating Thank You Page (Gutenberg) ===")

    # Navigate to Add New Page
    page.goto("https://purebrain.ai/wp-admin/post-new.php?post_type=page", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "v2-01-add-new-page")

    # Close welcome modal if present
    close_modal = page.locator("button.components-modal__header-button, button[aria-label='Close']")
    if close_modal.count() > 0:
        try:
            close_modal.first.click()
            page.wait_for_timeout(500)
        except:
            pass

    # Add title - click on title area first
    title_area = page.locator(".editor-post-title__input, [aria-label='Add title']")
    if title_area.count() > 0:
        print("Adding title...")
        title_area.first.click()
        page.wait_for_timeout(300)
        page.keyboard.type("Thank You")
        page.wait_for_timeout(500)

    # Now add content block - click in content area and use keyboard shortcut
    # Press Enter to move to content, then add Custom HTML block
    page.keyboard.press("Enter")
    page.wait_for_timeout(300)

    # Type /html to add HTML block via slash command
    page.keyboard.type("/html")
    page.wait_for_timeout(1000)

    # Press Enter to select Custom HTML
    page.keyboard.press("Enter")
    page.wait_for_timeout(1000)

    # Now we should be in the HTML textarea - paste content
    page.keyboard.type(THANK_YOU_CONTENT)
    page.wait_for_timeout(500)

    screenshot(page, "v2-02-content-added")

    # Change slug - open Page settings sidebar
    page_settings = page.locator("button.edit-post-sidebar__panel-tab[aria-label='Page']")
    if page_settings.count() == 0:
        # Try to open settings sidebar first
        settings_btn = page.locator("button[aria-label='Settings']")
        if settings_btn.count() > 0:
            settings_btn.click()
            page.wait_for_timeout(500)

    # Look for URL/Slug section
    url_section = page.locator("button:has-text('URL'), .editor-post-url")
    if url_section.count() > 0:
        url_section.first.click()
        page.wait_for_timeout(500)

        slug_input = page.locator("input[placeholder='thank-you'], input.components-input-control__input")
        if slug_input.count() > 0:
            slug_input.last.fill("thank-you")

    # Publish
    print("Publishing...")

    # Click Publish button
    publish_btn = page.locator("button.editor-post-publish-button, button.editor-post-publish-panel__toggle")
    if publish_btn.count() > 0:
        publish_btn.first.click()
        page.wait_for_timeout(2000)

        # Confirm publish in panel
        confirm_btn = page.locator("button.editor-post-publish-button")
        if confirm_btn.count() > 0:
            confirm_btn.click()
            page.wait_for_timeout(3000)

    screenshot(page, "v2-03-published")

    return True

def edit_purebrain_page(page):
    """Edit Pure Brain 2.0 page to add PayPal buttons"""
    print("\n=== TASK 2: Adding PayPal Buttons to Pure Brain 2.0 ===")

    # Navigate directly to the page editor (we know it's post 174)
    page.goto("https://purebrain.ai/wp-admin/post.php?post=174&action=edit", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    screenshot(page, "v2-04-purebrain-edit")

    # The page uses raw HTML in a code block. We need to find and edit that.
    # First, let's check if we're in code editing mode

    # Get the content textarea/code editor
    code_editor = page.locator("textarea.wp-block-code__textarea, .block-editor-plain-text, textarea.editor-post-text-editor")

    if code_editor.count() > 0:
        print("Found code editor, getting current content...")
        current_content = code_editor.first.input_value()
        print(f"Content length: {len(current_content)} characters")

        # Save original content for backup
        with open("/tmp/purebrain20_original.html", "w") as f:
            f.write(current_content)
        print("Original content backed up to /tmp/purebrain20_original.html")

        # Find the pricing section and add PayPal buttons
        # Look for the pricing tier divs and add buttons after them

        # The page has pricing cards - we need to find where to insert buttons
        # Look for patterns like "$79" "$149" "$499" "$999"

        modified_content = current_content

        # Add buttons after each pricing tier
        # Pattern: Find the price and add button after the containing div closes

        # For $79 Starter
        if "$79" in modified_content and "paypal" not in modified_content.lower():
            # Find a good insertion point after $79 section
            idx = modified_content.find("$79")
            if idx > 0:
                # Find the next </div> that closes the pricing card
                close_div_count = 0
                search_start = idx
                for i in range(5):  # Look through next few closing divs
                    next_close = modified_content.find("</div>", search_start)
                    if next_close > 0:
                        search_start = next_close + 6

                # Insert after this pricing section
                # Actually, let's be smarter - add all buttons at once in a section at the end
                pass

        # Instead of complex insertion, let's add a PayPal section before </body>
        paypal_section = '''
<!-- PayPal Purchase Buttons Section -->
<section id="paypal-buttons" style="padding: 60px 20px; background: rgba(0,0,0,0.3);">
  <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
    <h2 style="color: #f1420b; font-size: 36px; margin-bottom: 40px;">Ready to Get Started?</h2>
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 30px;">

      <!-- Starter $79 -->
      <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 30px; min-width: 250px;">
        <h3 style="color: #ffffff; margin-bottom: 10px;">Starter</h3>
        <p style="color: #f1420b; font-size: 32px; font-weight: bold;">$79</p>
        ''' + PAYPAL_BUTTONS["starter"] + '''
      </div>

      <!-- Pro $149 -->
      <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 30px; min-width: 250px;">
        <h3 style="color: #ffffff; margin-bottom: 10px;">Pro</h3>
        <p style="color: #f1420b; font-size: 32px; font-weight: bold;">$149</p>
        ''' + PAYPAL_BUTTONS["pro"] + '''
      </div>

      <!-- Enterprise $499 -->
      <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 30px; min-width: 250px;">
        <h3 style="color: #ffffff; margin-bottom: 10px;">Enterprise</h3>
        <p style="color: #f1420b; font-size: 32px; font-weight: bold;">$499</p>
        ''' + PAYPAL_BUTTONS["enterprise"] + '''
      </div>

      <!-- Ultimate $999 -->
      <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 30px; min-width: 250px;">
        <h3 style="color: #ffffff; margin-bottom: 10px;">Ultimate</h3>
        <p style="color: #f1420b; font-size: 32px; font-weight: bold;">$999</p>
        ''' + PAYPAL_BUTTONS["ultimate"] + '''
      </div>

    </div>
  </div>
</section>
'''

        # Insert before </body>
        if "</body>" in modified_content:
            modified_content = modified_content.replace("</body>", paypal_section + "\n</body>")
            print("Added PayPal section before </body>")
        else:
            # Just append
            modified_content = modified_content + "\n" + paypal_section
            print("Appended PayPal section at end")

        # Update the content
        code_editor.first.fill("")  # Clear first
        code_editor.first.fill(modified_content)

        screenshot(page, "v2-05-buttons-added")

        # Save the page
        save_btn = page.locator("button.editor-post-save-draft, button:has-text('Save'), button:has-text('Update')")
        if save_btn.count() > 0:
            save_btn.first.click()
            page.wait_for_timeout(3000)

        screenshot(page, "v2-06-saved")

        # Save modified content for reference
        with open("/tmp/purebrain20_modified.html", "w") as f:
            f.write(modified_content)
        print("Modified content saved to /tmp/purebrain20_modified.html")

        return True
    else:
        print("Could not find code editor. Page might use different structure.")

        # Let's check if there's a Custom HTML block we can edit
        html_block = page.locator(".wp-block-html textarea")
        if html_block.count() > 0:
            print(f"Found {html_block.count()} HTML blocks")

        # Check for edit with Elementor
        elementor_btn = page.locator("a:has-text('Edit with Elementor')")
        if elementor_btn.count() > 0:
            print("Page uses Elementor - would need to edit via Elementor interface")

        return False

def verify_pages(page):
    """Verify both pages are working"""
    print("\n=== TASK 3: Verification ===")

    # Check Thank You page
    print("Checking Thank You page...")
    page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "v2-10-verify-thankyou")

    title = page.title()
    print(f"Thank You page title: {title}")

    # Check if page has content
    body_text = page.locator("body").text_content()
    has_content = "Thank You" in body_text or "Pure Brain" in body_text
    print(f"Thank You page has expected content: {has_content}")

    # Check Pure Brain 2.0 page
    print("\nChecking Pure Brain 2.0 page...")
    page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "v2-11-verify-purebrain20")

    # Scroll down to find PayPal buttons
    for i in range(5):
        page.evaluate(f"window.scrollBy(0, 500)")
        page.wait_for_timeout(500)

    screenshot(page, "v2-12-purebrain20-scrolled")

    # Check for PayPal buttons
    paypal_forms = page.locator("form[action*='paypal']").count()
    print(f"PayPal forms found: {paypal_forms}")

    return paypal_forms > 0

def main():
    print("=" * 60)
    print("PayPal Integration v2 for purebrain.ai")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Step 1: Login
            if not login(page):
                print("Login may have failed, continuing anyway...")
                screenshot(page, "v2-00-login-state")

            # Step 2: Create Thank You page
            # Try API method first, fall back to Gutenberg
            if not create_thank_you_page_via_api(page):
                print("API method failed, trying Gutenberg...")
                create_thank_you_page_gutenberg(page)

            # Step 3: Edit Pure Brain 2.0 page
            edit_purebrain_page(page)

            # Step 4: Verify
            verify_pages(page)

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            screenshot(page, "v2-error")
        finally:
            browser.close()

    print("\n" + "=" * 60)
    print("PayPal Integration v2 Complete")
    print("Screenshots saved to /tmp/paypal-integration-*.png")
    print("=" * 60)

if __name__ == "__main__":
    main()
