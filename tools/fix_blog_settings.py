#!/usr/bin/env python3
"""
Fix WordPress Blog Settings - Set Blog page as Posts page
"""

import time
from playwright.sync_api import sync_playwright

WP_USER = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

def fix_settings():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Login
        print("Logging in...")
        page.goto("https://purebrain.ai/wp-admin", timeout=60000)
        time.sleep(3)

        # Click username/password option
        try:
            link = page.locator('text=Log in with username and password')
            if link.count() > 0:
                link.click()
                time.sleep(2)
        except:
            pass

        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASSWORD)
        page.click('#wp-submit')
        time.sleep(5)

        # Go to Reading Settings
        print("Going to Reading Settings...")
        page.goto("https://purebrain.ai/wp-admin/options-reading.php", timeout=60000)
        time.sleep(3)

        page.screenshot(path="/tmp/wp_fix_01_before.png")
        print("Screenshot before: /tmp/wp_fix_01_before.png")

        # Find the "Posts page" dropdown and select "Blog"
        print("Setting Posts page to 'Blog'...")
        posts_page_select = page.locator('select[name="page_for_posts"]')
        if posts_page_select.count() > 0:
            # Get available options
            options = posts_page_select.locator('option')
            count = options.count()
            print(f"Found {count} options in Posts page dropdown")

            # Look for "Blog" option
            for i in range(count):
                option_text = options.nth(i).text_content()
                option_value = options.nth(i).get_attribute('value')
                print(f"  Option {i}: '{option_text}' (value: {option_value})")
                if "Blog" in option_text:
                    print(f"  -> Selecting this option!")
                    posts_page_select.select_option(value=option_value)
                    break

        time.sleep(2)
        page.screenshot(path="/tmp/wp_fix_02_selected.png")
        print("Screenshot after selection: /tmp/wp_fix_02_selected.png")

        # Click Save Changes
        print("Saving changes...")
        save_btn = page.locator('input[type="submit"][value="Save Changes"]')
        if save_btn.count() > 0:
            save_btn.click()
            time.sleep(3)

        page.screenshot(path="/tmp/wp_fix_03_saved.png")
        print("Screenshot after save: /tmp/wp_fix_03_saved.png")

        # Verify blog page
        print("Verifying blog page...")
        page.goto("https://purebrain.ai/blog/", timeout=60000)
        time.sleep(5)

        page.screenshot(path="/tmp/wp_fix_04_blog.png")
        print("Screenshot of blog: /tmp/wp_fix_04_blog.png")

        # Scroll down to see posts
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(2)
        page.screenshot(path="/tmp/wp_fix_05_blog_scrolled.png")
        print("Screenshot scrolled: /tmp/wp_fix_05_blog_scrolled.png")

        print("\nDone!")
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    fix_settings()
