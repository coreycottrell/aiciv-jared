#!/usr/bin/env python3
"""
WordPress Automation: Add PayPal Buttons to Pure Brain 2.0 Page
and Redesign Thank You Page

Tasks:
1. Login to WordPress
2. Check existing PayPal Buttons page
3. Edit Pure Brain 2.0 page with Elementor to find pricing section
4. Add PayPal buttons to each pricing tier
5. Redesign Thank You page
"""

import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Create screenshots directory
SCREENSHOT_DIR = "/tmp"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Credentials
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# PayPal button HTML templates
PAYPAL_BUTTONS = {
    79: '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="text-align: center; margin-top: 15px;">
<input type="hidden" name="cmd" value="_xclick">
<input type="hidden" name="business" value="support@puremarketing.ai">
<input type="hidden" name="item_name" value="Pure Brain Starter">
<input type="hidden" name="amount" value="79.00">
<input type="hidden" name="currency_code" value="USD">
<input type="hidden" name="no_shipping" value="1">
<input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
<button type="submit" style="background: linear-gradient(135deg, #f1420b, #ff6b3d); color: white; border: none; padding: 14px 35px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer;">Get Started</button>
</form>''',
    149: '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="text-align: center; margin-top: 15px;">
<input type="hidden" name="cmd" value="_xclick">
<input type="hidden" name="business" value="support@puremarketing.ai">
<input type="hidden" name="item_name" value="Pure Brain Pro">
<input type="hidden" name="amount" value="149.00">
<input type="hidden" name="currency_code" value="USD">
<input type="hidden" name="no_shipping" value="1">
<input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
<button type="submit" style="background: linear-gradient(135deg, #f1420b, #ff6b3d); color: white; border: none; padding: 14px 35px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer;">Go Pro</button>
</form>''',
    499: '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="text-align: center; margin-top: 15px;">
<input type="hidden" name="cmd" value="_xclick">
<input type="hidden" name="business" value="support@puremarketing.ai">
<input type="hidden" name="item_name" value="Pure Brain Enterprise">
<input type="hidden" name="amount" value="499.00">
<input type="hidden" name="currency_code" value="USD">
<input type="hidden" name="no_shipping" value="1">
<input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
<button type="submit" style="background: linear-gradient(135deg, #f1420b, #ff6b3d); color: white; border: none; padding: 14px 35px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer;">Enterprise</button>
</form>''',
    999: '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="text-align: center; margin-top: 15px;">
<input type="hidden" name="cmd" value="_xclick">
<input type="hidden" name="business" value="support@puremarketing.ai">
<input type="hidden" name="item_name" value="Pure Brain Ultimate">
<input type="hidden" name="amount" value="999.00">
<input type="hidden" name="currency_code" value="USD">
<input type="hidden" name="no_shipping" value="1">
<input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
<button type="submit" style="background: linear-gradient(135deg, #f1420b, #ff6b3d); color: white; border: none; padding: 14px 35px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer;">Ultimate</button>
</form>'''
}

# Thank You page HTML
THANK_YOU_HTML = '''<div style="min-height: 100vh; background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%); padding: 80px 20px; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">

  <div style="max-width: 900px; margin: 0 auto;">

    <!-- Logo/Brand -->
    <div style="margin-bottom: 40px;">
      <span style="font-size: 32px; font-weight: 800; letter-spacing: 2px;">
        <span style="color: #2a93c1;">PURE BR</span><span style="color: #f1420b;">AI</span><span style="color: #2a93c1;">N</span>
      </span>
    </div>

    <!-- Main Heading -->
    <h1 style="font-size: 56px; font-weight: 800; margin-bottom: 20px; background: linear-gradient(135deg, #ffffff 0%, #f1420b 50%, #ff6b3d 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
      Welcome to the Family!
    </h1>

    <p style="font-size: 24px; color: #cccccc; margin-bottom: 50px; line-height: 1.6;">
      Your Pure Brain journey begins now. We're thrilled to have you.
    </p>

    <!-- Confirmation Box -->
    <div style="background: rgba(241, 66, 11, 0.1); border: 2px solid rgba(241, 66, 11, 0.3); border-radius: 16px; padding: 40px; margin-bottom: 50px;">
      <div style="font-size: 48px; margin-bottom: 20px;">&#10024;</div>
      <h2 style="color: #ffffff; font-size: 28px; margin-bottom: 15px;">Payment Confirmed</h2>
      <p style="color: #aaaaaa; font-size: 18px;">
        Check your email for your receipt and onboarding details.
      </p>
    </div>

    <!-- Timeline -->
    <h3 style="color: #f1420b; font-size: 14px; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 30px;">
      What Happens Next
    </h3>

    <div style="display: flex; flex-direction: column; gap: 20px; max-width: 600px; margin: 0 auto 50px auto; text-align: left;">

      <div style="display: flex; align-items: center; gap: 20px; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px;">
        <div style="background: #f1420b; color: white; padding: 12px 16px; border-radius: 8px; font-weight: bold; white-space: nowrap;">24 hrs</div>
        <div style="color: #ffffff;">Personal welcome email from our team</div>
      </div>

      <div style="display: flex; align-items: center; gap: 20px; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px;">
        <div style="background: #f1420b; color: white; padding: 12px 16px; border-radius: 8px; font-weight: bold; white-space: nowrap;">48 hrs</div>
        <div style="color: #ffffff;">Your AI partner setup begins</div>
      </div>

      <div style="display: flex; align-items: center; gap: 20px; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px;">
        <div style="background: #f1420b; color: white; padding: 12px 16px; border-radius: 8px; font-weight: bold; white-space: nowrap;">1 week</div>
        <div style="color: #ffffff;">Your Pure Brain is fully configured and ready</div>
      </div>

    </div>

    <!-- CTA Button -->
    <a href="https://purebrain.ai" style="
      display: inline-block;
      background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%);
      color: white;
      padding: 18px 50px;
      font-size: 18px;
      font-weight: bold;
      border-radius: 50px;
      text-decoration: none;
      box-shadow: 0 8px 30px rgba(241, 66, 11, 0.4);
      transition: transform 0.2s;
    ">Return to Homepage</a>

    <!-- Footer Note -->
    <p style="color: #666666; font-size: 14px; margin-top: 60px;">
      Questions? Email us at <a href="mailto:support@puremarketing.ai" style="color: #f1420b;">support@puremarketing.ai</a>
    </p>

  </div>
</div>'''


def screenshot(page, name):
    """Take a screenshot with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/paypal-final-{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"Screenshot saved: {path}")
    return path


def wp_login(page):
    """Login to WordPress admin"""
    print(f"Navigating to {WP_URL}...")
    page.goto(WP_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

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

        try:
            page.wait_for_url("**/wp-admin/**", timeout=15000)
        except PlaywrightTimeout as e:
            print(f"URL wait timeout: {e}")

        page.wait_for_timeout(3000)

    # Check current state
    print(f"Current URL: {page.url}")

    # Check for login error
    error_msg = page.locator("#login_error")
    if error_msg.count() > 0 and error_msg.is_visible():
        print(f"Login error detected!")
        error_text = error_msg.text_content()
        print(f"Error: {error_text}")
        return False

    return True


def view_paypal_embed_page(page):
    """Check the existing PayPal Buttons (Embed) page"""
    print("\n--- Checking existing PayPal Buttons (Embed) page ---")

    # Visit the page live
    page.goto("https://purebrain.ai/paypal-buttons-embed/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    screenshot(page, "20-paypal-embed-live")

    # Check page source for buttons
    content = page.content()
    if "paypal.com" in content.lower():
        print("Found PayPal references in existing embed page")

    return content


def open_elementor_for_page(page, page_name):
    """Open a page in Elementor editor by finding it in the pages list"""
    print(f"\n--- Opening {page_name} in Elementor ---")

    # Go to pages list
    page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Find the page row
    pages_table = page.locator("#the-list")
    if pages_table.count() == 0:
        print("Could not find pages table")
        return False

    rows = pages_table.locator("tr").all()
    target_row = None

    for row in rows:
        title_elem = row.locator(".row-title")
        if title_elem.count() > 0:
            title = title_elem.text_content().strip()
            if page_name.lower() in title.lower():
                print(f"Found page: {title}")
                target_row = row
                break

    if target_row is None:
        print(f"Could not find page: {page_name}")
        return False

    # Hover to reveal action links
    target_row.hover()
    page.wait_for_timeout(500)

    # Look for Edit with Elementor
    elementor_link = target_row.locator("a:has-text('Edit with Elementor')")
    if elementor_link.count() > 0:
        href = elementor_link.get_attribute("href")
        print(f"Opening Elementor: {href}")
        page.goto(href, wait_until="domcontentloaded")
        page.wait_for_timeout(10000)  # Elementor takes time
        return True

    # Try via regular edit
    edit_link = target_row.locator(".row-title")
    if edit_link.count() > 0:
        edit_link.click()
        page.wait_for_timeout(5000)

        # Look for Elementor button
        elementor_btn = page.locator("a:has-text('Edit with Elementor')")
        if elementor_btn.count() > 0:
            elementor_btn.first.click()
            page.wait_for_timeout(10000)
            return True

    return False


def explore_purebrain_page_in_elementor(page):
    """Explore the PureBrain 2.0 page in Elementor to find pricing widgets"""
    print("\n--- Exploring PureBrain 2.0 page structure ---")

    # Wait for Elementor
    try:
        page.wait_for_selector("#elementor-preview-iframe", timeout=15000)
    except:
        print("Could not find Elementor iframe")
        screenshot(page, "21-no-elementor")
        return

    screenshot(page, "22-elementor-loaded")

    # Switch to preview iframe
    iframe = page.frame_locator("#elementor-preview-iframe")

    # Scroll through the page to capture all sections
    # Try scrolling in the iframe
    try:
        # First, click somewhere in the iframe to focus it
        iframe.locator("body").click()
        page.wait_for_timeout(500)
    except:
        pass

    # Look for text patterns in the preview
    prices_found = []
    for price in ["$79", "$149", "$499", "$999", "79", "149", "499", "999"]:
        try:
            elements = iframe.locator(f"text={price}")
            count = elements.count()
            if count > 0:
                print(f"Found {count} elements with price: {price}")
                prices_found.append(price)
        except Exception as e:
            pass

    # Take multiple screenshots scrolling through preview
    screenshot(page, "23-elementor-preview-1")

    # Try to scroll in the panel/preview area
    try:
        # Click on the preview panel navigator
        nav = page.locator("#elementor-panel-footer-responsive")
        if nav.count() > 0:
            nav.click()
    except:
        pass

    # Look for widgets in the panel
    panel = page.locator("#elementor-panel")
    if panel.count() > 0:
        print("Found Elementor panel")
        # Try to see the structure
        structure_btn = page.locator("[data-view='navigator']")
        if structure_btn.count() > 0:
            structure_btn.click()
            page.wait_for_timeout(1000)
            screenshot(page, "24-elementor-navigator")

    return prices_found


def update_thank_you_page(page):
    """Update the Thank You page with new design"""
    print("\n--- Updating Thank You Page ---")

    # First, let's see the current Thank You page
    page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    screenshot(page, "30-thank-you-before")

    # Go to pages list to edit
    page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Find Thank You page
    pages_table = page.locator("#the-list")
    rows = pages_table.locator("tr").all()

    for row in rows:
        title_elem = row.locator(".row-title")
        if title_elem.count() > 0:
            title = title_elem.text_content().strip()
            if "thank you" in title.lower():
                print(f"Found Thank You page: {title}")

                # Click to edit
                title_elem.click()
                page.wait_for_timeout(5000)
                screenshot(page, "31-thank-you-editor")

                # Check if we're in Gutenberg or Classic editor
                is_gutenberg = page.locator(".edit-post-visual-editor, .block-editor").count() > 0

                if is_gutenberg:
                    print("Gutenberg editor detected")
                    # We'll need to add a Custom HTML block
                    add_custom_html_block_gutenberg(page)
                else:
                    print("Classic editor or other")
                    # Try Elementor
                    elementor_btn = page.locator("a:has-text('Edit with Elementor')")
                    if elementor_btn.count() > 0:
                        elementor_btn.first.click()
                        page.wait_for_timeout(10000)
                        add_html_via_elementor(page)

                return True

    return False


def add_custom_html_block_gutenberg(page):
    """Add custom HTML block in Gutenberg"""
    print("Adding custom HTML block in Gutenberg...")

    # Click to add a block
    add_block_btn = page.locator("button[aria-label='Add block'], .block-editor-inserter__toggle")
    if add_block_btn.count() > 0:
        add_block_btn.first.click()
        page.wait_for_timeout(1000)

        # Search for Custom HTML
        search = page.locator("input[placeholder*='Search'], .block-editor-inserter__search-input")
        if search.count() > 0:
            search.fill("Custom HTML")
            page.wait_for_timeout(500)

            # Click on Custom HTML block
            html_block = page.locator("button:has-text('Custom HTML')")
            if html_block.count() > 0:
                html_block.first.click()
                page.wait_for_timeout(1000)

                # Now paste our HTML
                # Find the textarea for HTML
                textarea = page.locator("textarea.block-editor-plain-text")
                if textarea.count() > 0:
                    textarea.fill(THANK_YOU_HTML)
                    screenshot(page, "32-html-added")

                    # Save/Update
                    update_btn = page.locator("button:has-text('Update'), button:has-text('Publish')")
                    if update_btn.count() > 0:
                        update_btn.first.click()
                        page.wait_for_timeout(3000)
                        screenshot(page, "33-saved")
                        return True

    return False


def add_html_via_elementor(page):
    """Add HTML widget in Elementor"""
    print("Adding HTML via Elementor...")

    # Wait for Elementor
    try:
        page.wait_for_selector("#elementor-preview-iframe", timeout=15000)
    except:
        print("Elementor not loaded")
        return False

    screenshot(page, "32-elementor-thank-you")

    # Look for the widgets panel
    # Search for HTML widget
    search = page.locator("#elementor-panel-elements-search-input")
    if search.count() > 0:
        search.fill("HTML")
        page.wait_for_timeout(1000)

        # Drag HTML widget to canvas
        html_widget = page.locator(".elementor-element-wrapper:has-text('HTML')")
        if html_widget.count() > 0:
            print("Found HTML widget")
            # This would require drag and drop which is complex
            # Instead, let's try clicking the widget

    return False


def main():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        print("=" * 60)
        print("WORDPRESS AUTOMATION: PayPal Buttons & Thank You Page")
        print("=" * 60)

        # Step 1: Login
        if not wp_login(page):
            print("Login failed!")
            screenshot(page, "99-login-failed")
            browser.close()
            return

        print("Login successful!")
        screenshot(page, "00-logged-in")

        # Step 2: Check existing PayPal page
        paypal_content = view_paypal_embed_page(page)

        # Step 3: Open PureBrain 2.0 in Elementor and explore
        if open_elementor_for_page(page, "PureBrain 2.0"):
            prices = explore_purebrain_page_in_elementor(page)
            print(f"Prices found in page: {prices}")

        # Step 4: Check and update Thank You page
        update_thank_you_page(page)

        # Final: View updated Thank You page
        page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        screenshot(page, "40-thank-you-final")

        browser.close()

        print("\n" + "=" * 60)
        print("Automation complete. Screenshots saved to /tmp/paypal-final-*.png")
        print("=" * 60)


if __name__ == "__main__":
    main()
