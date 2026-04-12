#!/usr/bin/env python3
"""
Scroll through Footer Options completely to find Show Social Icons toggle.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/footer-scroll")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

screenshot_counter = [0]

def screenshot_path(name: str) -> str:
    screenshot_counter[0] += 1
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"{screenshot_counter[0]:02d}_{name}.png")

async def save_screenshot(page, name: str):
    path = screenshot_path(name)
    await page.screenshot(path=path)
    print(f"[SCREENSHOT] {path}")
    return path

async def main():
    print("=" * 60)
    print("Footer Options Complete Scroll")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        # Login
        print("\n[LOGIN]")
        await page.goto(WP_URL)
        await page.wait_for_timeout(3000)
        
        if "wp-login.php" in page.url:
            try:
                link = await page.query_selector("a:has-text('Log in with username')")
                if link: await link.click(); await page.wait_for_timeout(2000)
            except: pass
            
            await page.fill("#user_login", WP_USERNAME)
            await page.fill("#user_pass", WP_PASSWORD)
            await page.click("#wp-submit")
            await page.wait_for_timeout(5000)
        
        # Go to Customizer
        print("[CUSTOMIZER]")
        await page.goto(f"{WP_URL}/customize.php")
        await page.wait_for_timeout(8000)
        await save_screenshot(page, "customizer_loaded")
        
        # Click Footer Options
        print("[OPENING FOOTER OPTIONS]")
        try:
            # Use a more specific selector
            footer_section = await page.wait_for_selector("#accordion-section-artistics_footer_settings, li[id*='footer']", timeout=10000)
            if footer_section:
                await footer_section.click()
                await page.wait_for_timeout(3000)
                await save_screenshot(page, "footer_options_opened")
        except Exception as e:
            print(f"  Error clicking footer options: {e}")
            # Try alternate approach
            await page.evaluate("""
                const sections = document.querySelectorAll('.accordion-section-title');
                for (const s of sections) {
                    if (s.innerText.includes('Footer')) {
                        s.click();
                        break;
                    }
                }
            """)
            await page.wait_for_timeout(3000)
            await save_screenshot(page, "footer_options_alternate")
        
        # Find the active panel and scroll through it
        print("[SCROLLING FOOTER OPTIONS PANEL]")
        
        # Get the open panel
        panel = await page.query_selector(".customize-pane-child[style*='left: 0'], .open, #sub-accordion-section-artistics_footer_settings")
        
        if panel:
            # Get panel scroll height
            scroll_info = await panel.evaluate("el => ({scrollHeight: el.scrollHeight, clientHeight: el.clientHeight})")
            print(f"  Panel scroll height: {scroll_info['scrollHeight']}, client height: {scroll_info['clientHeight']}")
            
            # Scroll through the panel
            scroll_positions = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600]
            for pos in scroll_positions:
                await panel.evaluate(f"el => el.scrollTop = {pos}")
                await page.wait_for_timeout(500)
                await save_screenshot(page, f"scroll_{pos}")
                
                # Get visible controls
                controls_html = await panel.inner_html()
                
                # Look for toggle-related keywords in visible content
                keywords = ['show', 'display', 'enable', 'toggle', 'checkbox', 'switch']
                for kw in keywords:
                    if kw.lower() in controls_html.lower():
                        # Find the context
                        idx = controls_html.lower().find(kw.lower())
                        snippet = controls_html[max(0,idx-30):idx+100]
                        if 'social' in snippet.lower() or 'icon' in snippet.lower():
                            print(f"  POTENTIAL TOGGLE at scroll {pos}: ...{snippet[:80]}...")
        else:
            print("  Could not find open panel, trying full page content")
            await page.evaluate("document.querySelector('.wp-full-overlay-sidebar-content').scrollTop = 500")
            await page.wait_for_timeout(1000)
            await save_screenshot(page, "sidebar_scrolled")
        
        # Now let's dump all the customize controls in Footer Options
        print("\n[ANALYZING FOOTER OPTIONS CONTROLS]")
        
        all_controls = await page.evaluate("""
            () => {
                const results = [];
                const controls = document.querySelectorAll('.customize-control');
                for (const ctrl of controls) {
                    const label = ctrl.querySelector('label, .customize-control-title');
                    const input = ctrl.querySelector('input, select, textarea');
                    const checkbox = ctrl.querySelector('input[type="checkbox"]');
                    
                    if (label || input || checkbox) {
                        results.push({
                            id: ctrl.id || 'no-id',
                            label: label ? label.innerText : '',
                            inputType: input ? input.type : '',
                            inputId: input ? input.id : '',
                            isCheckbox: checkbox !== null,
                            isChecked: checkbox ? checkbox.checked : null,
                            visible: ctrl.offsetParent !== null
                        });
                    }
                }
                return results;
            }
        """)
        
        print(f"  Found {len(all_controls)} controls total")
        
        # Filter for potentially relevant controls
        for ctrl in all_controls:
            label_lower = ctrl['label'].lower() if ctrl['label'] else ''
            ctrl_id = ctrl['id'].lower() if ctrl['id'] else ''
            
            if any(kw in label_lower or kw in ctrl_id for kw in ['social', 'icon', 'show', 'display', 'footer']):
                print(f"  RELEVANT: {ctrl}")
        
        # Also specifically look for checkboxes
        print("\n[ALL CHECKBOXES IN PAGE]")
        checkboxes = await page.evaluate("""
            () => {
                const results = [];
                const cbs = document.querySelectorAll('input[type="checkbox"]');
                for (const cb of cbs) {
                    const parent = cb.closest('.customize-control');
                    const label = parent ? parent.querySelector('.customize-control-title') : null;
                    results.push({
                        id: cb.id,
                        checked: cb.checked,
                        name: cb.name,
                        label: label ? label.innerText : '',
                        parentId: parent ? parent.id : ''
                    });
                }
                return results;
            }
        """)
        
        for cb in checkboxes:
            label_lower = cb['label'].lower() if cb['label'] else ''
            cb_id = (cb['id'] or '').lower()
            cb_name = (cb['name'] or '').lower()
            
            if any(kw in label_lower or kw in cb_id or kw in cb_name for kw in ['social', 'icon', 'show', 'display']):
                print(f"  >>> SOCIAL-RELATED CHECKBOX: {cb}")
        
        # Check for any toggle-style elements
        print("\n[LOOKING FOR TOGGLE SWITCH ELEMENTS]")
        toggle_elements = await page.query_selector_all(".toggle, .switch, .wp-switch-editor, [class*='toggle'], [class*='switch']")
        print(f"  Found {len(toggle_elements)} toggle-style elements")
        
        await save_screenshot(page, "final_state")
        
        # Summary
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"\nScreenshots in: {SCREENSHOT_DIR}")
        for f in sorted(SCREENSHOT_DIR.glob("*.png")):
            print(f"  - {f.name}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
