#!/usr/bin/env python3
"""
Add Analytics Tags to Google Tag Manager
GTM Container: GTM-WTDXL4VJ
Account: purebrain@puremarketing.ai

Tags to add:
1. GA4 - PureBrain (Tag ID: G-86325WBT3P)
2. Search Console Verification (meta tag)
3. Microsoft Clarity (script)

Usage:
    xvfb-run python3 gtm_add_analytics_tags.py
"""

import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots/gtm"
GTM_URL = "https://tagmanager.google.com/"
GTM_CONTAINER = "GTM-WTDXL4VJ"
USER_DATA_DIR = "/home/jared/projects/AI-CIV/aether/.browser-data/gtm-profile"

# Login credentials
GOOGLE_EMAIL = "purebrain@puremarketing.ai"
# Note: Google typically requires 2FA or app passwords, this may not work
# Using the app password from .env
GOOGLE_APP_PASSWORD = "mldvztmeligxhyaw"

# Tag configurations
GA4_TAG_ID = "G-86325WBT3P"

SEARCH_CONSOLE_HTML = '''<meta name="google-site-verification" content="S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0" />'''

CLARITY_HTML = '''<script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "viy9bnc56x");
</script>'''


def screenshot(page, name):
    """Take a screenshot with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"Screenshot saved: {path}")
    return path


def google_login(page):
    """Attempt to login to Google"""
    print("Attempting Google login...")

    # Wait for email input
    try:
        email_input = page.wait_for_selector('input[type="email"]', timeout=10000)
        if email_input:
            email_input.fill(GOOGLE_EMAIL)
            time.sleep(1)
            page.click('button:has-text("Next")')
            time.sleep(3)
            screenshot(page, "login_01_email")
    except Exception as e:
        print(f"Email step failed: {e}")
        return False

    # Wait for password input
    try:
        password_input = page.wait_for_selector('input[type="password"]', timeout=10000)
        if password_input:
            password_input.fill(GOOGLE_APP_PASSWORD)
            time.sleep(1)
            page.click('button:has-text("Next")')
            time.sleep(5)
            screenshot(page, "login_02_password")
    except Exception as e:
        print(f"Password step failed: {e}")
        return False

    # Check for 2FA or other challenges
    time.sleep(3)
    screenshot(page, "login_03_after")

    if 'accounts.google.com' in page.url:
        print("May need 2FA or additional verification")
        return False

    return True


def is_logged_in(page):
    """Check if we're logged into GTM"""
    page_content = page.content().lower()
    return (
        'accounts.google.com' not in page.url and
        'sign in' not in page_content[:500] and
        ('tag manager' in page_content or 'workspace' in page_content or 'container' in page_content)
    )


def navigate_to_tags(page):
    """Navigate to the Tags section"""
    print("Navigating to Tags section...")

    # Look for Tags link in sidebar
    selectors = [
        'a[href*="/tags"]',
        'text="Tags"',
        '[data-gtmid="tags"]',
    ]

    for selector in selectors:
        try:
            element = page.wait_for_selector(selector, timeout=5000)
            if element:
                element.click()
                time.sleep(2)
                return True
        except:
            continue

    return False


def click_new_tag(page):
    """Click the New Tag button"""
    print("Clicking New Tag button...")

    try:
        # Wait for page to stabilize
        time.sleep(2)

        # Try different approaches
        new_btn = page.query_selector('button:has-text("New")')
        if new_btn:
            new_btn.click()
            time.sleep(2)
            return True
    except:
        pass

    return False


def add_ga4_tag(page):
    """Add GA4 Configuration Tag"""
    print("\n" + "="*50)
    print("Adding GA4 Tag")
    print("="*50)

    if not click_new_tag(page):
        print("Failed to click New button")
        screenshot(page, "ga4_error_new_button")
        return False

    screenshot(page, "ga4_01_new_clicked")

    # Click on tag configuration area
    time.sleep(2)
    try:
        config_area = page.query_selector('text="Choose a tag type"')
        if config_area:
            config_area.click()
            time.sleep(2)
        else:
            # Click on the tag config panel
            page.click('.tag-config-panel, [data-automation-id="tag-config-panel"]', timeout=5000)
            time.sleep(2)
    except Exception as e:
        print(f"Clicking config area: {e}")

    screenshot(page, "ga4_02_config_clicked")

    # Search for Google Tag
    try:
        search = page.query_selector('input[type="search"], input[placeholder*="earch"]')
        if search:
            search.fill("Google Tag")
            time.sleep(2)
    except:
        pass

    screenshot(page, "ga4_03_search")

    # Click Google Tag option
    try:
        # Look for the specific option
        google_tag = page.query_selector('text="Google Tag"')
        if google_tag:
            google_tag.click()
            time.sleep(2)
    except:
        pass

    screenshot(page, "ga4_04_type_selected")

    # Enter Tag ID
    try:
        # Look for tag ID input
        inputs = page.query_selector_all('input[type="text"]')
        for inp in inputs:
            placeholder = inp.get_attribute('placeholder') or ''
            aria_label = inp.get_attribute('aria-label') or ''
            if 'tag id' in placeholder.lower() or 'tag id' in aria_label.lower() or 'g-' in placeholder.lower():
                inp.fill(GA4_TAG_ID)
                print(f"Entered Tag ID: {GA4_TAG_ID}")
                break
    except Exception as e:
        print(f"Could not enter Tag ID: {e}")

    time.sleep(1)
    screenshot(page, "ga4_05_tag_id")

    # Add trigger
    try:
        trigger_area = page.query_selector('text="Choose a trigger"')
        if trigger_area:
            trigger_area.click()
            time.sleep(2)
    except:
        pass

    screenshot(page, "ga4_06_trigger_panel")

    # Select All Pages
    try:
        all_pages = page.query_selector('text="All Pages"')
        if all_pages:
            all_pages.click()
            time.sleep(2)
            print("Selected All Pages trigger")
    except:
        pass

    screenshot(page, "ga4_07_trigger_selected")

    # Name the tag
    try:
        # Find the title input
        title = page.query_selector('input[value="Untitled Tag"]')
        if title:
            title.triple_click()
            title.fill("GA4 - PureBrain")
    except:
        pass

    # Save
    try:
        save_btn = page.query_selector('button:has-text("Save")')
        if save_btn:
            save_btn.click()
            time.sleep(3)
            print("GA4 tag saved!")
    except Exception as e:
        print(f"Could not save: {e}")
        return False

    screenshot(page, "ga4_08_saved")
    return True


def add_custom_html_tag(page, name, html_content):
    """Add a Custom HTML tag"""
    safe_name = name.lower().replace(' ', '_')

    print("\n" + "="*50)
    print(f"Adding {name} Tag")
    print("="*50)

    if not click_new_tag(page):
        print("Failed to click New button")
        return False

    screenshot(page, f"{safe_name}_01_new")

    # Click on tag configuration
    time.sleep(2)
    try:
        config_area = page.query_selector('text="Choose a tag type"')
        if config_area:
            config_area.click()
            time.sleep(2)
    except:
        pass

    screenshot(page, f"{safe_name}_02_config")

    # Search for Custom HTML
    try:
        search = page.query_selector('input[type="search"], input[placeholder*="earch"]')
        if search:
            search.fill("Custom HTML")
            time.sleep(2)
    except:
        pass

    # Click Custom HTML option
    try:
        custom_html = page.query_selector('text="Custom HTML"')
        if custom_html:
            custom_html.click()
            time.sleep(2)
    except:
        pass

    screenshot(page, f"{safe_name}_03_type")

    # Enter HTML
    try:
        # Look for HTML textarea
        textarea = page.query_selector('textarea')
        if textarea:
            textarea.fill(html_content)
            print("Entered HTML content")
    except Exception as e:
        print(f"Could not enter HTML: {e}")
        return False

    time.sleep(1)
    screenshot(page, f"{safe_name}_04_html")

    # Add trigger
    try:
        trigger_area = page.query_selector('text="Choose a trigger"')
        if trigger_area:
            trigger_area.click()
            time.sleep(2)
    except:
        pass

    # Select All Pages
    try:
        all_pages = page.query_selector('text="All Pages"')
        if all_pages:
            all_pages.click()
            time.sleep(2)
            print("Selected All Pages trigger")
    except:
        pass

    screenshot(page, f"{safe_name}_05_trigger")

    # Name the tag
    try:
        title = page.query_selector('input[value="Untitled Tag"]')
        if title:
            title.triple_click()
            title.fill(name)
    except:
        pass

    # Save
    try:
        save_btn = page.query_selector('button:has-text("Save")')
        if save_btn:
            save_btn.click()
            time.sleep(3)
            print(f"{name} tag saved!")
    except:
        return False

    screenshot(page, f"{safe_name}_06_saved")
    return True


def publish_container(page, version_name):
    """Submit and publish the container"""
    print("\n" + "="*50)
    print("Publishing Container")
    print("="*50)

    # Click Submit
    try:
        submit_btn = page.query_selector('button:has-text("Submit")')
        if submit_btn:
            submit_btn.click()
            time.sleep(3)
    except:
        print("Could not click Submit")
        return False

    screenshot(page, "publish_01_dialog")

    # Enter version name
    try:
        # Look for version name input
        inputs = page.query_selector_all('input[type="text"]')
        for inp in inputs:
            placeholder = inp.get_attribute('placeholder') or ''
            aria_label = inp.get_attribute('aria-label') or ''
            if 'version' in placeholder.lower() or 'version' in aria_label.lower():
                inp.fill(version_name)
                break
    except:
        pass

    screenshot(page, "publish_02_version")

    # Click Publish
    try:
        publish_btn = page.query_selector('button:has-text("Publish")')
        if publish_btn:
            publish_btn.click()
            time.sleep(5)
            print(f"Published with version: {version_name}")
    except:
        print("Could not click Publish")
        return False

    screenshot(page, "publish_03_done")
    return True


def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=True,
            viewport={'width': 1920, 'height': 1080},
            slow_mo=500  # Slow down for debugging
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        print("Step 1: Navigating to Google Tag Manager...")
        page.goto(GTM_URL, wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)
        screenshot(page, "00_landing")

        # Check if we need to login
        if not is_logged_in(page):
            print("Not logged in. Attempting login...")
            if not google_login(page):
                print("\n*** LOGIN FAILED ***")
                print("Google may require 2FA or interactive login.")
                print("Screenshots saved to show current state.")
                browser.close()
                return

        # Reload and verify
        time.sleep(2)
        page.goto(GTM_URL, wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)
        screenshot(page, "01_after_login")

        if not is_logged_in(page):
            print("Still not logged in after login attempt.")
            browser.close()
            return

        print("Logged in successfully!")

        # Look for the container
        print(f"\nStep 2: Finding container {GTM_CONTAINER}...")
        container = page.query_selector(f'text="{GTM_CONTAINER}"')
        if container:
            container.click()
            time.sleep(3)
        else:
            print("Container not found on page. Looking at available options...")

        screenshot(page, "02_container")

        # Navigate to Tags
        print("\nStep 3: Navigating to Tags...")
        if not navigate_to_tags(page):
            print("Could not find Tags section")

        time.sleep(2)
        screenshot(page, "03_tags")

        # Add tags
        results = {
            'GA4': False,
            'Search Console': False,
            'Clarity': False,
            'Published': False
        }

        try:
            results['GA4'] = add_ga4_tag(page)
        except Exception as e:
            print(f"Error adding GA4: {e}")
            screenshot(page, "error_ga4")

        try:
            results['Search Console'] = add_custom_html_tag(page, "Search Console Verification", SEARCH_CONSOLE_HTML)
        except Exception as e:
            print(f"Error adding Search Console: {e}")
            screenshot(page, "error_search_console")

        try:
            results['Clarity'] = add_custom_html_tag(page, "Microsoft Clarity", CLARITY_HTML)
        except Exception as e:
            print(f"Error adding Clarity: {e}")
            screenshot(page, "error_clarity")

        # Publish if any tags were added
        if any([results['GA4'], results['Search Console'], results['Clarity']]):
            try:
                results['Published'] = publish_container(page, "Added GA4, Search Console, Clarity")
            except Exception as e:
                print(f"Error publishing: {e}")
                screenshot(page, "error_publish")

        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        for tag, success in results.items():
            status = "SUCCESS" if success else "FAILED"
            print(f"  {tag}: {status}")
        print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
        print("="*60)

        browser.close()


if __name__ == "__main__":
    main()
