#!/usr/bin/env python3
"""
Force Elementor to regenerate cache by saving the page in Elementor
"""

from playwright.sync_api import sync_playwright

WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

def login(page):
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

def regenerate_elementor_css(page):
    """Try to regenerate Elementor CSS/cache"""
    print("Attempting to regenerate Elementor cache...")

    # Go to Elementor tools page
    page.goto("https://purebrain.ai/wp-admin/admin.php?page=elementor-tools", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    page.screenshot(path="/tmp/elementor-tools.png")

    # Look for "Regenerate CSS" button
    regen_btn = page.locator("button:has-text('Regenerate CSS'), a:has-text('Regenerate CSS')")
    if regen_btn.count() > 0:
        print("Found Regenerate CSS button, clicking...")
        regen_btn.first.click()
        page.wait_for_timeout(5000)
        return True

    # Also try the sync library button
    sync_btn = page.locator("button:has-text('Sync Library')")
    if sync_btn.count() > 0:
        print("Found Sync Library button, clicking...")
        sync_btn.first.click()
        page.wait_for_timeout(3000)

    return False

def save_in_elementor(page):
    """Open Elementor editor and save to trigger cache rebuild"""
    print("Opening Elementor to trigger save...")

    page.goto("https://purebrain.ai/wp-admin/post.php?post=174&action=elementor", wait_until="domcontentloaded")
    page.wait_for_timeout(15000)  # Elementor takes time

    page.screenshot(path="/tmp/elementor-editor.png")

    # Check if Elementor loaded
    if "elementor" not in page.url:
        print("Elementor didn't load properly")
        return False

    # Wait for panel to load
    page.wait_for_timeout(5000)

    # Click the Update/Publish button
    update_btn = page.locator("#elementor-panel-saver-button-publish")
    if update_btn.count() > 0 and update_btn.is_visible():
        print("Clicking Update button...")
        update_btn.click()
        page.wait_for_timeout(10000)
        page.screenshot(path="/tmp/elementor-after-save.png")
        return True
    else:
        print("Update button not found")

        # Try to find any save mechanism
        save_btns = page.locator("button:has-text('Update'), button:has-text('Publish'), button:has-text('Save')")
        if save_btns.count() > 0:
            print(f"Found {save_btns.count()} save buttons")
            save_btns.first.click()
            page.wait_for_timeout(10000)
            return True

    return False

def verify(page):
    """Verify PayPal buttons appear"""
    print("\nVerifying front-end...")
    page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Scroll to find buttons
    for _ in range(25):
        page.evaluate("window.scrollBy(0, 300)")
        page.wait_for_timeout(100)

    page.screenshot(path="/tmp/purebrain20-final.png", full_page=True)

    paypal_forms = page.locator("form[action*='paypal']").count()
    html = page.content()

    print(f"PayPal forms in DOM: {paypal_forms}")
    print(f"PayPal in source: {'paypal.com' in html}")

    return paypal_forms > 0

def main():
    print("Elementor Cache Regeneration")
    print("=" * 40)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            print("1. Login...")
            if not login(page):
                print("   Failed")
                return
            print("   OK")

            print("2. Regenerate cache...")
            regenerate_elementor_css(page)

            print("3. Save in Elementor...")
            save_in_elementor(page)

            print("4. Verify...")
            success = verify(page)

            if success:
                print("\n*** SUCCESS! PayPal buttons are visible! ***")
            else:
                print("\n*** Still not showing - may need manual intervention ***")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    main()
