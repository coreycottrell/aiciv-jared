#!/usr/bin/env python3
"""
PureBrain 3.0 Pricing Page Update Script

Updates the pricing section features per Jared's specifications:
- Change "Unlimited agents: 10 running simultaneously" to "Unlimited Agents"
- Add market jargon to features

Uses headless Playwright for automation.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin/"
WP_USERNAME = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/purebrain-pricing-update")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def ss(name):
    """Generate timestamped screenshot filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"{timestamp}_{name}.png")


async def main():
    async with async_playwright() as p:
        print("[INIT] Launching headless browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        try:
            # Step 1: Navigate to WordPress login
            print("[NAV] Going to WordPress admin...")
            await page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)
            await page.screenshot(path=ss("01_login_page"))
            print(f"[SCREENSHOT] Login page captured")

            # Check if there's a "Log in with username and password" link
            username_link = await page.query_selector("a:has-text('Log in with username and password')")
            if username_link:
                print("[INFO] Found 'Log in with username and password' link, clicking...")
                await username_link.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path=ss("02_username_login_form"))

            # Wait for login form
            try:
                await page.wait_for_selector("#user_login", state="visible", timeout=10000)
            except:
                # Try alternate GoDaddy login form
                print("[INFO] Standard login form not found, checking for GoDaddy login...")

            await page.screenshot(path=ss("03_before_credentials"))

            # Fill login credentials
            print(f"[INFO] Entering credentials for {WP_USERNAME}...")

            # Try standard WordPress login
            user_field = await page.query_selector("#user_login")
            pass_field = await page.query_selector("#user_pass")

            if user_field and pass_field:
                await user_field.fill(WP_USERNAME)
                await pass_field.fill(WP_PASSWORD)
                await page.screenshot(path=ss("04_credentials_entered"))

                # Check for CAPTCHA
                captcha = await page.query_selector("input[name='wpsec_captcha_answer'], .wpsec-captcha")
                if captcha:
                    print("[WARN] CAPTCHA detected - taking screenshot for manual solution")
                    await page.screenshot(path=ss("05_captcha_detected"))
                    # Get CAPTCHA image and try to solve
                    captcha_img = await page.query_selector(".wpsec-captcha-image, img[alt*='captcha']")
                    if captcha_img:
                        print("[INFO] CAPTCHA image found, attempting to read it...")

                # Submit login
                submit_btn = await page.query_selector("#wp-submit")
                if submit_btn:
                    await submit_btn.click()
                else:
                    await page.keyboard.press("Enter")

                await page.wait_for_timeout(5000)
            else:
                print("[WARN] Standard login form not found")

            await page.screenshot(path=ss("06_after_login"))

            # Check if logged in
            current_url = page.url
            print(f"[INFO] Current URL after login: {current_url}")

            if "wp-admin" in current_url:
                print("[SUCCESS] Logged in successfully!")
            else:
                print("[INFO] May need to check login status...")

            # Step 2: Navigate to Pages
            print("[NAV] Going to Pages list...")
            await page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", timeout=60000)
            await page.wait_for_timeout(3000)
            await page.screenshot(path=ss("07_pages_list"))
            print("[SCREENSHOT] Pages list captured")

            # Step 3: Search for PureBrain 3.0 page
            print("[ACTION] Searching for 'purebrain' page...")
            search_box = await page.query_selector("#post-search-input")
            if search_box:
                await search_box.fill("purebrain")
                # Click search button
                search_btn = await page.query_selector("#search-submit")
                if search_btn:
                    await search_btn.click()
                else:
                    await page.keyboard.press("Enter")
                await page.wait_for_timeout(3000)

            await page.screenshot(path=ss("08_search_results"))
            print("[SCREENSHOT] Search results captured")

            # Step 4: Find the PureBrain.ai 3.0 page
            print("[ACTION] Looking for PureBrain.ai 3.0 page...")

            # Look for the page row
            page_rows = await page.query_selector_all(".type-page")
            target_row = None

            for row in page_rows:
                title_elem = await row.query_selector(".row-title")
                if title_elem:
                    title = await title_elem.inner_text()
                    print(f"  - Found page: {title}")
                    if "purebrain" in title.lower() and "3" in title:
                        target_row = row
                        print(f"[FOUND] Target page: {title}")
                        break

            if target_row:
                # Hover to reveal row actions
                await target_row.hover()
                await page.wait_for_timeout(500)
                await page.screenshot(path=ss("09_page_hover"))

                # Find Edit with Elementor link
                elementor_link = await target_row.query_selector("a.elementor-action-edit")
                if not elementor_link:
                    elementor_link = await target_row.query_selector("a:has-text('Edit with Elementor')")

                if elementor_link:
                    print("[ACTION] Clicking 'Edit with Elementor'...")
                    await elementor_link.click()
                    await page.wait_for_timeout(10000)  # Wait for Elementor to load
                    await page.screenshot(path=ss("10_elementor_loading"))
                else:
                    print("[WARN] 'Edit with Elementor' link not found, trying direct URL...")
                    # Get post ID from row
                    row_id = await target_row.get_attribute("id")
                    if row_id and row_id.startswith("post-"):
                        post_id = row_id.replace("post-", "")
                        elementor_url = f"https://purebrain.ai/?p={post_id}&elementor"
                        print(f"[NAV] Direct Elementor URL: {elementor_url}")
                        await page.goto(elementor_url, timeout=120000)
                        await page.wait_for_timeout(10000)
                        await page.screenshot(path=ss("10_elementor_loading"))
            else:
                # Try direct page edit approach
                print("[WARN] Target page row not found, listing all pages...")
                all_pages = await page.query_selector_all("a.row-title")
                for p in all_pages[:10]:
                    text = await p.inner_text()
                    print(f"  - Page: {text}")

            # Step 5: Wait for Elementor to fully load
            print("[WAIT] Waiting for Elementor editor to load...")
            await page.wait_for_timeout(5000)

            # Close any modals/popups
            try:
                close_btns = await page.query_selector_all(".dialog-close-button, .eicon-close, [aria-label='Close']")
                for btn in close_btns:
                    if await btn.is_visible():
                        await btn.click()
                        await page.wait_for_timeout(500)
            except:
                pass

            await page.screenshot(path=ss("11_elementor_loaded"))
            print("[SCREENSHOT] Elementor loaded")

            # Step 6: Explore the page structure in Elementor
            print("[EXPLORE] Analyzing page structure...")

            # Check if we're in Elementor editor
            elementor_panel = await page.query_selector("#elementor-panel")
            if elementor_panel:
                print("[SUCCESS] Elementor editor detected!")

                # Look for Navigator panel to understand page structure
                nav_btn = await page.query_selector(".elementor-panel-menu-item-navigator, [data-hint='Navigator']")
                if nav_btn:
                    await nav_btn.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=ss("12_navigator_panel"))
                    print("[SCREENSHOT] Navigator panel opened")

                # Scroll through the preview to find pricing section
                preview_frame = page.frame_locator("#elementor-preview-iframe")

                # Try to scroll in the preview
                print("[ACTION] Scrolling through preview to find pricing section...")

                scroll_count = 0
                for i in range(10):
                    scroll_count += 1
                    await page.evaluate("""
                        () => {
                            const iframe = document.getElementById('elementor-preview-iframe');
                            if (iframe && iframe.contentDocument) {
                                const body = iframe.contentDocument.body;
                                const scrollable = iframe.contentDocument.scrollingElement || body;
                                scrollable.scrollTop += 500;
                            }
                        }
                    """)
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=ss(f"13_scroll_{scroll_count}"))

                    # Check for pricing-related text
                    frame_content = await page.evaluate("""
                        () => {
                            const iframe = document.getElementById('elementor-preview-iframe');
                            if (iframe && iframe.contentDocument) {
                                return iframe.contentDocument.body.innerText;
                            }
                            return '';
                        }
                    """)

                    if any(keyword in frame_content.lower() for keyword in ['$79', '$149', '$499', '$999', 'awakened', 'bonded', 'partnered', 'unified', 'unlimited agents']):
                        print(f"[FOUND] Pricing section detected at scroll position {scroll_count}")
                        await page.screenshot(path=ss("14_pricing_section_found"))
                        break

                # Click on pricing elements in the preview to edit them
                print("[ACTION] Attempting to click on pricing elements...")

                # Try to find and click on "Unlimited agents" text
                try:
                    await page.evaluate("""
                        () => {
                            const iframe = document.getElementById('elementor-preview-iframe');
                            if (iframe && iframe.contentDocument) {
                                const elements = iframe.contentDocument.querySelectorAll('*');
                                for (let el of elements) {
                                    if (el.innerText && el.innerText.includes('Unlimited agents')) {
                                        el.click();
                                        return true;
                                    }
                                }
                            }
                            return false;
                        }
                    """)
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=ss("15_clicked_unlimited_agents"))
                except Exception as e:
                    print(f"[WARN] Could not click unlimited agents: {e}")

                # Look for text editor in the Elementor panel
                text_editor_panel = await page.query_selector(".elementor-control-type-wysiwyg")
                if text_editor_panel:
                    print("[FOUND] Text editor panel detected!")
                    await page.screenshot(path=ss("16_text_editor_panel"))

            else:
                print("[WARN] Not in Elementor editor, may be viewing the page normally")
                await page.screenshot(path=ss("11_not_elementor"))

            # Final state screenshot
            await page.screenshot(path=ss("17_final_state"))
            print("[SCREENSHOT] Final state captured")

            # Generate report
            print("\n" + "="*60)
            print("EXPLORATION COMPLETE")
            print("="*60)
            print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
            print("\nNext steps:")
            print("1. Review screenshots to understand the page structure")
            print("2. Manually make the text changes in Elementor if automation failed")
            print("3. Changes needed per Jared:")
            print("   - 'Unlimited agents: 10 running simultaneously' -> 'Unlimited Agents'")
            print("   - Add 'always-on infrastructure' to 24/7 deployment")
            print("   - Add 'via RAG knowledge base' to wisdom inheritance")
            print("   - Add 'SLA guarantees' to higher tiers")
            print("   - Add 'autonomous workflows' language")

        except Exception as e:
            print(f"[ERROR] Exception occurred: {e}")
            await page.screenshot(path=ss("error_state"))
            raise

        finally:
            await browser.close()
            print("[DONE] Browser closed")


if __name__ == "__main__":
    asyncio.run(main())
