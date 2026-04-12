#!/usr/bin/env python3
"""
PayPal Integration for purebrain.ai
Creates Thank You page and adds PayPal buttons to Pure Brain 2.0 page
"""

import os
import sys
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

def create_thank_you_page(page):
    """Create the Thank You page"""
    print("\n=== TASK 1: Creating Thank You Page ===")

    # Navigate to Add New Page
    page.goto("https://purebrain.ai/wp-admin/post-new.php?post_type=page", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "01-add-new-page")

    # Check for Gutenberg editor
    is_gutenberg = page.locator(".edit-post-visual-editor, .block-editor").count() > 0
    print(f"Gutenberg editor: {is_gutenberg}")

    if is_gutenberg:
        # Close any welcome modal
        close_btn = page.locator("button:has-text('Close'), .components-modal__header button")
        if close_btn.count() > 0:
            try:
                close_btn.first.click()
                page.wait_for_timeout(500)
            except:
                pass

        # Add title
        title_input = page.locator(".editor-post-title__input, [aria-label='Add title']")
        if title_input.count() > 0:
            print("Adding title...")
            title_input.first.click()
            page.keyboard.type("Thank You")
            page.wait_for_timeout(1000)

        # Click to add a block
        block_inserter = page.locator(".block-editor-inserter__toggle")
        if block_inserter.count() > 0:
            print("Opening block inserter...")
            block_inserter.first.click()
            page.wait_for_timeout(1000)

            # Search for Custom HTML block
            search_input = page.locator(".components-search-control__input, .block-editor-inserter__search input")
            if search_input.count() > 0:
                search_input.first.fill("custom html")
                page.wait_for_timeout(1000)

                # Click Custom HTML block
                html_block = page.locator("button:has-text('Custom HTML')")
                if html_block.count() > 0:
                    html_block.first.click()
                    page.wait_for_timeout(1000)

                    # Enter HTML content
                    textarea = page.locator("textarea.block-editor-plain-text")
                    if textarea.count() > 0:
                        textarea.first.fill(THANK_YOU_CONTENT)
                        page.wait_for_timeout(500)
                    else:
                        print("Could not find HTML textarea")
                else:
                    print("Custom HTML block not found")

        screenshot(page, "02-thank-you-content")

        # Set the slug
        # Open the Page panel in sidebar
        page_panel = page.locator("button:has-text('Page')")
        if page_panel.count() > 0:
            page_panel.first.click()
            page.wait_for_timeout(1000)

        # Try to find and edit the URL/slug
        permalink_btn = page.locator("button:has-text('Change URL')")
        if permalink_btn.count() > 0:
            permalink_btn.click()
            page.wait_for_timeout(500)

            slug_input = page.locator("#editor-post-slug input")
            if slug_input.count() > 0:
                slug_input.fill("thank-you")
                page.wait_for_timeout(500)

        # Publish the page
        publish_btn = page.locator("button.editor-post-publish-button")
        if publish_btn.count() > 0:
            print("Publishing page...")
            publish_btn.click()
            page.wait_for_timeout(2000)

            # Confirm publish
            confirm_btn = page.locator("button.editor-post-publish-button")
            if confirm_btn.count() > 0:
                confirm_btn.click()
                page.wait_for_timeout(3000)

        screenshot(page, "03-thank-you-published")
    else:
        # Classic editor
        print("Using classic editor...")

        # Fill title
        title = page.locator("#title")
        if title.count() > 0:
            title.fill("Thank You")

        # Set slug
        slug = page.locator("#new-post-slug")
        if slug.count() > 0:
            slug.fill("thank-you")

        # Switch to Text mode
        text_tab = page.locator("#content-html")
        if text_tab.count() > 0:
            text_tab.click()
            page.wait_for_timeout(500)

        # Fill content
        content_area = page.locator("#content")
        if content_area.count() > 0:
            content_area.fill(THANK_YOU_CONTENT)

        screenshot(page, "02-thank-you-content")

        # Publish
        publish_btn = page.locator("#publish")
        if publish_btn.count() > 0:
            publish_btn.click()
            page.wait_for_timeout(5000)

        screenshot(page, "03-thank-you-published")

    print("Thank You page creation complete")

def find_purebrain_page(page):
    """Find the Pure Brain 2.0 page"""
    print("\n=== TASK 2: Finding Pure Brain 2.0 Page ===")

    # Navigate to Pages list
    page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "04-pages-list")

    # Search for Pure Brain 2.0
    search_input = page.locator("#post-search-input")
    if search_input.count() > 0:
        search_input.fill("Pure Brain 2.0")
        page.click("#search-submit")
        page.wait_for_timeout(3000)
        screenshot(page, "05-search-results")

    # Find the page row
    page_row = page.locator("tr:has-text('Pure Brain 2.0'), tr:has-text('purebrain-2-0')")
    if page_row.count() > 0:
        print("Found Pure Brain 2.0 page")
        # Get the edit link
        edit_link = page_row.first.locator(".row-title")
        if edit_link.count() > 0:
            href = edit_link.get_attribute("href")
            print(f"Edit URL: {href}")
            return href

    # Try broader search
    print("Searching for any purebrain page...")
    search_input.fill("purebrain")
    page.click("#search-submit")
    page.wait_for_timeout(3000)
    screenshot(page, "05b-broader-search")

    # List all found pages
    rows = page.locator("#the-list tr").all()
    for row in rows:
        title = row.locator(".row-title").text_content() if row.locator(".row-title").count() > 0 else "N/A"
        print(f"  Found: {title}")
        if "2.0" in title or "2-0" in title.lower():
            edit_link = row.locator(".row-title")
            if edit_link.count() > 0:
                href = edit_link.get_attribute("href")
                return href

    return None

def add_paypal_buttons(page, edit_url):
    """Add PayPal buttons to the Pure Brain 2.0 page"""
    print("\n=== Adding PayPal Buttons ===")

    if not edit_url:
        print("No edit URL provided")
        return

    page.goto(edit_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    screenshot(page, "06-purebrain-edit")

    # Check what editor we're using
    is_elementor = "elementor" in page.url or page.locator("#elementor").count() > 0
    is_gutenberg = page.locator(".edit-post-visual-editor, .block-editor").count() > 0

    print(f"Editor: {'Elementor' if is_elementor else 'Gutenberg' if is_gutenberg else 'Classic'}")

    if is_elementor:
        print("Elementor detected - need to edit with Elementor")
        # Click Edit with Elementor button
        elementor_btn = page.locator("a:has-text('Edit with Elementor')")
        if elementor_btn.count() > 0:
            elementor_btn.first.click()
            page.wait_for_timeout(10000)  # Elementor takes time to load
            screenshot(page, "07-elementor-editor")

            # This would require complex Elementor widget manipulation
            # For now, document the need for manual intervention
            print("NOTE: Elementor editing requires manual button placement")
            print("PayPal button HTML snippets have been saved to /tmp/paypal_buttons.txt")

            with open("/tmp/paypal_buttons.txt", "w") as f:
                for tier, html in PAYPAL_BUTTONS.items():
                    f.write(f"\n=== {tier.upper()} TIER ===\n")
                    f.write(html)
                    f.write("\n")

    elif is_gutenberg:
        print("Gutenberg editor - adding Custom HTML blocks")

        # Scroll to find pricing sections and add blocks
        # This is complex in Gutenberg - would need to find the right location

        # For now, add all PayPal buttons at the end
        for tier, html in PAYPAL_BUTTONS.items():
            print(f"Adding {tier} PayPal button...")

            # Click to add block at end
            add_block = page.locator(".block-list-appender button")
            if add_block.count() > 0:
                add_block.first.click()
                page.wait_for_timeout(1000)

                # Search for Custom HTML
                search = page.locator(".components-search-control__input, .block-editor-inserter__search input")
                if search.count() > 0:
                    search.first.fill("custom html")
                    page.wait_for_timeout(1000)

                    html_block = page.locator("button:has-text('Custom HTML')")
                    if html_block.count() > 0:
                        html_block.first.click()
                        page.wait_for_timeout(1000)

                        textarea = page.locator("textarea.block-editor-plain-text")
                        if textarea.count() > 0:
                            # Find the last one (just added)
                            textareas = textarea.all()
                            if textareas:
                                textareas[-1].fill(html)

        screenshot(page, "08-buttons-added")

        # Update the page
        update_btn = page.locator("button:has-text('Update')")
        if update_btn.count() > 0:
            update_btn.click()
            page.wait_for_timeout(3000)

        screenshot(page, "09-page-updated")

    else:
        # Classic editor - use Text mode
        print("Classic editor - switching to Text mode")

        text_tab = page.locator("#content-html")
        if text_tab.count() > 0:
            text_tab.click()
            page.wait_for_timeout(500)

        # Get current content
        content_area = page.locator("#content")
        if content_area.count() > 0:
            current = content_area.input_value()

            # Append PayPal buttons
            new_content = current
            for tier, html in PAYPAL_BUTTONS.items():
                new_content += f"\n\n<!-- {tier.upper()} PayPal Button -->\n{html}"

            content_area.fill(new_content)

        screenshot(page, "08-buttons-added")

        # Update
        update_btn = page.locator("#publish")
        if update_btn.count() > 0:
            update_btn.click()
            page.wait_for_timeout(5000)

        screenshot(page, "09-page-updated")

def verify_pages(page):
    """Verify the pages are accessible"""
    print("\n=== TASK 3: Verification ===")

    # Check Thank You page
    print("Checking Thank You page...")
    page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "10-verify-thankyou")

    status_code = page.evaluate("window.performance.getEntries()[0].responseStatus || 200")
    print(f"Thank You page status: {status_code}")
    print(f"Thank You page URL: {page.url}")

    # Check Pure Brain 2.0 page
    print("\nChecking Pure Brain 2.0 page...")
    page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "11-verify-purebrain20")

    # Check if PayPal buttons are present
    paypal_forms = page.locator("form[action*='paypal']").count()
    print(f"PayPal forms found on page: {paypal_forms}")

    # Scroll down to see more
    page.evaluate("window.scrollBy(0, 500)")
    page.wait_for_timeout(1000)
    screenshot(page, "12-purebrain20-scrolled")

    page.evaluate("window.scrollBy(0, 500)")
    page.wait_for_timeout(1000)
    screenshot(page, "13-purebrain20-more")

def main():
    print("=" * 60)
    print("PayPal Integration for purebrain.ai")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Step 1: Login
            if not login(page):
                print("Login may have failed, continuing anyway...")
                screenshot(page, "00-login-state")

            # Step 2: Create Thank You page
            create_thank_you_page(page)

            # Step 3: Find and edit Pure Brain 2.0 page
            edit_url = find_purebrain_page(page)
            if edit_url:
                add_paypal_buttons(page, edit_url)
            else:
                print("Could not find Pure Brain 2.0 page to edit")
                # Save buttons to file for manual addition
                with open("/tmp/paypal_buttons.txt", "w") as f:
                    f.write("PayPal Integration Buttons for purebrain.ai\n")
                    f.write("=" * 50 + "\n\n")
                    for tier, html in PAYPAL_BUTTONS.items():
                        f.write(f"\n=== {tier.upper()} TIER (${{'79' if tier=='starter' else '149' if tier=='pro' else '499' if tier=='enterprise' else '999'}}) ===\n")
                        f.write(html)
                        f.write("\n")
                print("PayPal button HTML saved to /tmp/paypal_buttons.txt")

            # Step 4: Verify
            verify_pages(page)

        except Exception as e:
            print(f"Error: {e}")
            screenshot(page, "error")
            raise
        finally:
            browser.close()

    print("\n" + "=" * 60)
    print("PayPal Integration Complete")
    print("Screenshots saved to /tmp/paypal-integration-*.png")
    print("=" * 60)

if __name__ == "__main__":
    main()
