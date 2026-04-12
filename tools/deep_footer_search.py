#!/usr/bin/env python3
"""
Deep search in Footer Options for Show Social Icons toggle.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/deep-footer")
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
    print("Deep Search Footer Options")
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
        
        # Click Footer Options directly
        print("\n[OPENING FOOTER OPTIONS]")
        await page.click("#accordion-section-artistics_footer_settings, [id*='footer_options']")
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "footer_options")
        
        # Get ALL controls in the footer section
        print("\n[FOOTER OPTIONS CONTROLS - DETAILED]")
        footer_controls = await page.evaluate("""
            () => {
                const results = [];
                // Try multiple selectors to find footer section
                const section = document.querySelector('#sub-accordion-section-artistics_footer_settings') ||
                               document.querySelector('#sub-accordion-section-footer_options') ||
                               document.querySelector('.customize-pane-child.open');
                
                if (!section) return {error: 'No section found', html: document.body.innerHTML.substring(0, 1000)};
                
                // Get all customize controls
                const controls = section.querySelectorAll('.customize-control');
                for (const ctrl of controls) {
                    const title = ctrl.querySelector('.customize-control-title');
                    const desc = ctrl.querySelector('.customize-control-description');
                    const inputs = ctrl.querySelectorAll('input, select, textarea');
                    
                    const inputDetails = [];
                    for (const inp of inputs) {
                        inputDetails.push({
                            tag: inp.tagName,
                            type: inp.type,
                            id: inp.id,
                            name: inp.name,
                            value: inp.type === 'checkbox' ? inp.checked : inp.value?.substring(0, 50)
                        });
                    }
                    
                    results.push({
                        id: ctrl.id,
                        title: title?.innerText || '',
                        description: desc?.innerText || '',
                        inputs: inputDetails,
                        html: ctrl.innerHTML.substring(0, 200)
                    });
                }
                
                return {controls: results, sectionId: section.id};
            }
        """)
        
        if 'error' in footer_controls:
            print(f"  Error: {footer_controls['error']}")
        else:
            print(f"  Section ID: {footer_controls.get('sectionId', 'unknown')}")
            print(f"  Found {len(footer_controls.get('controls', []))} controls:")
            
            for ctrl in footer_controls.get('controls', []):
                title = ctrl.get('title', '').strip()
                desc = ctrl.get('description', '').strip()
                inputs = ctrl.get('inputs', [])
                
                print(f"\n  === {ctrl['id']} ===")
                if title: print(f"      Title: {title}")
                if desc: print(f"      Desc: {desc[:100]}")
                if inputs:
                    for inp in inputs:
                        print(f"      Input: {inp}")
                
                # Check if this could be the social icons toggle
                combined = f"{title} {desc} {ctrl['id']}".lower()
                if any(kw in combined for kw in ['social', 'icon', 'show', 'display', 'enable']):
                    print(f"      >>> POSSIBLE SOCIAL TOGGLE!")
        
        # Also check if there are subsections in footer
        print("\n[CHECKING FOR SUBSECTIONS IN FOOTER]")
        subsections = await page.evaluate("""
            () => {
                const results = [];
                const section = document.querySelector('#sub-accordion-section-artistics_footer_settings') ||
                               document.querySelector('.customize-pane-child.open');
                if (!section) return [];
                
                const subs = section.querySelectorAll('.accordion-section, [id*="accordion"]');
                for (const sub of subs) {
                    results.push({
                        id: sub.id,
                        title: sub.querySelector('.accordion-section-title')?.innerText || ''
                    });
                }
                return results;
            }
        """)
        
        for sub in subsections:
            print(f"  Subsection: {sub['title']} (id: {sub['id']})")
        
        # Dump the raw HTML of footer options section for analysis
        print("\n[RAW HTML SNIPPET OF FOOTER SECTION]")
        html = await page.evaluate("""
            () => {
                const section = document.querySelector('#sub-accordion-section-artistics_footer_settings') ||
                               document.querySelector('.customize-pane-child.open');
                return section ? section.innerHTML : 'section not found';
            }
        """)
        
        # Look for specific keywords in HTML
        keywords = ['show', 'display', 'enable', 'visible', 'toggle', 'social', 'icon', 'footer']
        for kw in keywords:
            count = html.lower().count(kw.lower())
            if count > 0:
                print(f"  '{kw}' appears {count} times")
                # Find context
                idx = html.lower().find(kw.lower())
                if idx >= 0:
                    snippet = html[max(0, idx-30):idx+80]
                    print(f"    First occurrence: ...{snippet}...")
        
        await save_screenshot(page, "footer_analysis")
        
        # Now let's check the live site footer
        print("\n[CHECKING LIVE SITE FOOTER]")
        await page.goto("https://purebrain.ai")
        await page.wait_for_timeout(5000)
        
        # Scroll to footer
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        await save_screenshot(page, "live_footer")
        
        # Get footer HTML
        footer_html = await page.evaluate("""
            () => {
                const footer = document.querySelector('footer') || document.querySelector('[class*="footer"]');
                return footer ? footer.innerHTML : 'no footer found';
            }
        """)
        
        print(f"  Footer HTML length: {len(footer_html)}")
        
        # Check for social links in footer
        social_indicators = ['social', 'linkedin', 'facebook', 'twitter', 'instagram', 'fa-', 'icon']
        for ind in social_indicators:
            if ind.lower() in footer_html.lower():
                print(f"  Found '{ind}' in footer!")
                idx = footer_html.lower().find(ind.lower())
                snippet = footer_html[max(0,idx-20):idx+80]
                print(f"    Context: {snippet[:100]}...")
        
        await save_screenshot(page, "final")
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
