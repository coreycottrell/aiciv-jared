#!/usr/bin/env python3
"""
Check General Options and all sections for Show Social Icons toggle.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/general-options")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

screenshot_counter = [0]

def screenshot_path(name: str) -> str:
    screenshot_counter[0] += 1
    return str(SCREENSHOT_DIR / f"{screenshot_counter[0]:02d}_{name}.png")

async def save_screenshot(page, name: str):
    path = screenshot_path(name)
    await page.screenshot(path=path)
    print(f"[SCREENSHOT] {path}")
    return path

async def main():
    print("=" * 60)
    print("Check General Options for Social Toggle")
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
        
        # Click General Options
        print("\n[OPENING GENERAL OPTIONS]")
        await page.evaluate("""
            const sections = document.querySelectorAll('.accordion-section-title');
            for (const s of sections) {
                if (s.innerText.includes('General')) {
                    s.click();
                    break;
                }
            }
        """)
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "general_options_opened")
        
        # Get all controls in General Options
        print("\n[GENERAL OPTIONS CONTROLS]")
        controls = await page.evaluate("""
            () => {
                const results = [];
                const panel = document.querySelector('[id*="general"]') || document.querySelector('.customize-pane-child.open');
                if (!panel) return results;
                
                const ctrls = panel.querySelectorAll('.customize-control');
                for (const ctrl of ctrls) {
                    const title = ctrl.querySelector('.customize-control-title');
                    const checkbox = ctrl.querySelector('input[type="checkbox"]');
                    const input = ctrl.querySelector('input, select, textarea');
                    
                    results.push({
                        id: ctrl.id,
                        title: title ? title.innerText : '',
                        isCheckbox: checkbox !== null,
                        isChecked: checkbox ? checkbox.checked : null,
                        inputId: input ? input.id : '',
                        inputName: input ? input.name : ''
                    });
                }
                return results;
            }
        """)
        
        for ctrl in controls:
            print(f"  {ctrl}")
            if 'social' in str(ctrl).lower() or 'icon' in str(ctrl).lower() or 'show' in str(ctrl['title']).lower():
                print(f"    >>> POTENTIAL TOGGLE!")
        
        # Scroll through General Options
        print("\n[SCROLLING GENERAL OPTIONS]")
        panel = await page.query_selector(".customize-pane-child.open, [id*='general']")
        if panel:
            scroll_info = await panel.evaluate("el => ({scrollHeight: el.scrollHeight, clientHeight: el.clientHeight})")
            print(f"  Panel scroll: {scroll_info}")
            
            for pos in [0, 200, 400, 600, 800, 1000]:
                await panel.evaluate(f"el => el.scrollTop = {pos}")
                await page.wait_for_timeout(300)
            await save_screenshot(page, "general_options_scrolled")
        
        # Go back and check all sections for social_sharing
        print("\n[SEARCHING ALL SECTIONS FOR SOCIAL TOGGLE]")
        
        # Get all section IDs
        sections = await page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('[id*="accordion-section"]'))
                    .map(s => ({id: s.id, title: s.querySelector('.accordion-section-title')?.innerText || ''}));
            }
        """)
        
        print(f"  Found {len(sections)} sections")
        for sec in sections:
            if sec['title'] and any(kw in sec['title'].lower() for kw in ['general', 'footer', 'social', 'option']):
                print(f"    - {sec['title']} (id: {sec['id']})")
        
        # Now specifically look for the social_sharing control
        print("\n[LOOKING FOR SOCIAL_SHARING CONTROL]")
        social_sharing = await page.query_selector("#customize-control-social_sharing, [id*='social_sharing']")
        if social_sharing:
            html = await social_sharing.inner_html()
            print(f"  Found social_sharing control!")
            print(f"  HTML: {html[:500]}")
            
            # Check what's in it
            checkbox = await social_sharing.query_selector("input[type='checkbox']")
            if checkbox:
                checked = await checkbox.is_checked()
                print(f"  Has checkbox, checked: {checked}")
            
            await save_screenshot(page, "social_sharing_control")
        else:
            print("  social_sharing control not found in DOM")
        
        # Final check: dump ALL checkboxes with their labels
        print("\n[ALL PAGE CHECKBOXES]")
        all_checkboxes = await page.evaluate("""
            () => {
                const results = [];
                const cbs = document.querySelectorAll('input[type="checkbox"]');
                for (const cb of cbs) {
                    const parent = cb.closest('.customize-control');
                    const title = parent?.querySelector('.customize-control-title');
                    const label = cb.closest('label') || document.querySelector(`label[for="${cb.id}"]`);
                    
                    results.push({
                        id: cb.id,
                        name: cb.name,
                        checked: cb.checked,
                        controlTitle: title?.innerText || '',
                        label: label?.innerText || ''
                    });
                }
                return results.filter(x => x.controlTitle || x.label);
            }
        """)
        
        for cb in all_checkboxes:
            label = cb['controlTitle'] or cb['label']
            if any(kw in label.lower() for kw in ['social', 'icon', 'show', 'display', 'enable']):
                print(f"  >>> {cb['id']}: '{label}' - checked: {cb['checked']}")
            elif label:
                print(f"  {cb['id']}: '{label}' - checked: {cb['checked']}")
        
        await save_screenshot(page, "final")
        
        print("\n" + "=" * 60)
        print("DONE")
        print("=" * 60)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
