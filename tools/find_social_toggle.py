#!/usr/bin/env python3
"""
Find and enable the "Show Social Icons" toggle in WordPress theme settings.
Searches: Footer Options, General Options, Theme Settings
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/social-toggle-search")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

screenshot_counter = [0]

def screenshot_path(name: str) -> str:
    screenshot_counter[0] += 1
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"{screenshot_counter[0]:02d}_{timestamp}_{name}.png")

async def save_screenshot(page, name: str, full_page: bool = False):
    path = screenshot_path(name)
    await page.screenshot(path=path, full_page=full_page)
    print(f"[SCREENSHOT] Saved: {path}")
    return path

async def login_to_wordpress(page):
    """Login to WordPress admin."""
    print("\n=== LOGIN ===")
    await page.goto(WP_URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(3000)
    
    if "wp-login.php" not in page.url:
        content = await page.content()
        if "wpbody" in content or "adminmenu" in content:
            print("[INFO] Already logged in")
            await save_screenshot(page, "already_logged_in")
            return True
    
    # Check for GoDaddy login toggle
    try:
        username_link = await page.query_selector("a:has-text('Log in with username and password')")
        if username_link:
            await username_link.click()
            await page.wait_for_timeout(2000)
    except:
        pass
    
    await page.fill("#user_login", WP_USERNAME, timeout=10000)
    await page.fill("#user_pass", WP_PASSWORD, timeout=10000)
    await page.click("#wp-submit")
    await page.wait_for_timeout(5000)
    await save_screenshot(page, "dashboard")
    print("[SUCCESS] Logged in")
    return True

async def search_customizer_section(page, section_name):
    """Open a customizer section and look for social toggle."""
    print(f"\n=== Searching: {section_name} ===")
    
    try:
        # Click the section
        section = await page.query_selector(f"text='{section_name}'")
        if not section:
            section = await page.query_selector(f"li:has-text('{section_name}')")
        if not section:
            section = await page.query_selector(f"h3:has-text('{section_name}')")
        
        if section:
            await section.click()
            await page.wait_for_timeout(3000)
            await save_screenshot(page, f"section_{section_name.replace(' ', '_').lower()}")
            
            # Look for toggles/checkboxes with social-related labels
            content = await page.content()
            
            # Search for toggle keywords
            toggle_keywords = [
                "show social", "display social", "enable social",
                "social icon", "social media", "footer social",
                "show icon", "display icon"
            ]
            
            for keyword in toggle_keywords:
                if keyword.lower() in content.lower():
                    print(f"  [FOUND] '{keyword}' mentioned in this section!")
            
            # Find all checkboxes and toggles in this section
            checkboxes = await page.query_selector_all("input[type='checkbox']")
            print(f"  Found {len(checkboxes)} checkboxes")
            
            for i, cb in enumerate(checkboxes):
                try:
                    cb_id = await cb.get_attribute("id")
                    is_checked = await cb.is_checked()
                    # Get nearby label
                    label = await page.query_selector(f"label[for='{cb_id}']")
                    label_text = await label.inner_text() if label else "no label"
                    print(f"    Checkbox #{i}: id={cb_id}, checked={is_checked}, label='{label_text}'")
                    
                    # Check if this is a social-related toggle
                    if any(kw in str(cb_id or '').lower() or kw in label_text.lower() 
                           for kw in ['social', 'icon', 'show', 'display', 'enable']):
                        print(f"    >>> POTENTIAL SOCIAL TOGGLE: {label_text} <<<")
                        return cb, label_text
                except Exception as e:
                    pass
            
            # Also look for toggle switches (non-checkbox styled)
            toggles = await page.query_selector_all(".toggle, .switch, .customize-control-checkbox")
            print(f"  Found {len(toggles)} toggle-style controls")
            
            return None, None
        else:
            print(f"  Section '{section_name}' not found")
            return None, None
            
    except Exception as e:
        print(f"  Error searching section: {e}")
        return None, None

async def main():
    print("=" * 60)
    print("WordPress Social Icons Toggle Finder")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        try:
            # Login
            await login_to_wordpress(page)
            
            # Go to Customizer
            print("\n=== OPENING CUSTOMIZER ===")
            await page.goto(f"{WP_URL}/customize.php", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(8000)
            await save_screenshot(page, "customizer_main")
            
            # List all visible sections
            sections = await page.query_selector_all(".accordion-section-title")
            print(f"\nFound {len(sections)} customizer sections:")
            section_names = []
            for sec in sections:
                try:
                    name = await sec.inner_text()
                    section_names.append(name.strip())
                    print(f"  - {name.strip()}")
                except:
                    pass
            
            # Search priority sections for social toggle
            priority_sections = [
                "Footer Options",
                "Footer Settings", 
                "General Options",
                "General Settings",
                "Theme Options",
                "Social",
                "Social Media",
                "Social Icons"
            ]
            
            found_toggle = None
            
            for section in priority_sections:
                if any(section.lower() in s.lower() for s in section_names):
                    toggle, label = await search_customizer_section(page, section)
                    if toggle:
                        found_toggle = (toggle, label)
                        break
                    # Go back to main customizer
                    back_btn = await page.query_selector(".customize-section-back, .accordion-section-back")
                    if back_btn:
                        await back_btn.click()
                        await page.wait_for_timeout(2000)
            
            # If not found in priority, check Footer Options more thoroughly
            print("\n=== DEEP SEARCH: Footer Options ===")
            await page.click("text='Footer Options'", timeout=5000)
            await page.wait_for_timeout(3000)
            
            # Scroll through the entire panel
            panel = await page.query_selector(".customize-pane-child.open, #sub-accordion-section-artistics_footer_settings")
            if panel:
                # Scroll down to see all options
                for scroll_amount in [100, 200, 300, 400, 500]:
                    await panel.evaluate(f"el => el.scrollTop = {scroll_amount}")
                    await page.wait_for_timeout(500)
                    await save_screenshot(page, f"footer_scroll_{scroll_amount}")
            
            # Get ALL content in the footer options
            content = await page.inner_html(".customize-pane-child.open, #sub-accordion-section-artistics_footer_settings") if await page.query_selector(".customize-pane-child.open") else ""
            print(f"\nFooter Options HTML length: {len(content)} characters")
            
            # Search for any toggle-related text
            toggle_patterns = [
                "show", "display", "enable", "visible", "hide",
                "social", "icon", "media", "links", "footer"
            ]
            
            for pattern in toggle_patterns:
                if pattern.lower() in content.lower():
                    # Find the context around this pattern
                    idx = content.lower().find(pattern.lower())
                    context_snippet = content[max(0, idx-50):idx+100]
                    print(f"  Found '{pattern}': ...{context_snippet[:80]}...")
            
            # Take final screenshot
            await save_screenshot(page, "footer_options_complete", full_page=False)
            
            # Now check Theme Options page (not in Customizer)
            print("\n=== CHECKING THEME OPTIONS PAGE ===")
            
            # Check if there's a separate theme options page
            await page.goto(WP_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # Look for theme-specific admin menus
            admin_menu = await page.inner_html("#adminmenu")
            theme_pages = [
                "Artistics",
                "Theme Options", 
                "Theme Settings",
                "Starter Templates"
            ]
            
            for theme_page in theme_pages:
                if theme_page.lower() in admin_menu.lower():
                    print(f"  Found '{theme_page}' in admin menu!")
                    # Try to click it
                    try:
                        await page.click(f"text='{theme_page}'")
                        await page.wait_for_timeout(3000)
                        await save_screenshot(page, f"theme_page_{theme_page.replace(' ', '_').lower()}")
                    except:
                        pass
            
            # Final summary
            print("\n" + "=" * 60)
            print("SEARCH COMPLETE")
            print("=" * 60)
            print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
            
            # List all screenshots
            for f in sorted(SCREENSHOT_DIR.glob("*.png")):
                print(f"  - {f.name}")
                
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await save_screenshot(page, "error")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
