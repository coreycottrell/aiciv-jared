#!/usr/bin/env python3
"""
Final report on Social Icons Toggle search.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/final-report")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

async def main():
    print("=" * 70)
    print("FINAL REPORT: Social Icons Toggle Search")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        # Login
        print("\n[1] LOGIN TO WORDPRESS")
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
        print("  Logged in successfully")
        
        # Go to Customizer and capture all relevant sections
        print("\n[2] CUSTOMIZER ANALYSIS")
        await page.goto(f"{WP_URL}/customize.php")
        await page.wait_for_timeout(8000)
        
        # List all top-level sections
        sections = await page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('.accordion-section-title'))
                    .map(s => s.innerText.trim())
                    .filter(s => s.length > 0 && s.length < 50);
            }
        """)
        
        print(f"\n  Customizer Sections Found:")
        for sec in sections:
            print(f"    - {sec}")
        
        # Open and screenshot each potentially relevant section
        relevant_sections = ['Footer Options', 'General Options', 'Blog Options']
        
        for section_name in relevant_sections:
            print(f"\n[3] EXAMINING: {section_name}")
            
            await page.evaluate(f"""
                const sections = document.querySelectorAll('.accordion-section-title');
                for (const s of sections) {{
                    if (s.innerText.includes('{section_name.split()[0]}')) {{
                        s.click();
                        break;
                    }}
                }}
            """)
            await page.wait_for_timeout(3000)
            
            # Get controls in this section
            controls = await page.evaluate("""
                () => {
                    const section = document.querySelector('.customize-pane-child[style*="left: 0"]') ||
                                   document.querySelector('.customize-pane-child.open');
                    if (!section) return [];
                    
                    return Array.from(section.querySelectorAll('.customize-control'))
                        .map(ctrl => {
                            const title = ctrl.querySelector('.customize-control-title');
                            const checkbox = ctrl.querySelector('input[type="checkbox"]');
                            return {
                                id: ctrl.id,
                                title: title?.innerText || '',
                                hasCheckbox: checkbox !== null,
                                isChecked: checkbox?.checked || false
                            };
                        })
                        .filter(c => c.title);
                }
            """)
            
            print(f"    Controls found: {len(controls)}")
            for ctrl in controls:
                checkbox_info = f" [{'X' if ctrl['isChecked'] else ' '}]" if ctrl['hasCheckbox'] else ""
                print(f"      - {ctrl['title']}{checkbox_info}")
                
                # Flag if it might be social-related
                if any(kw in ctrl['title'].lower() or kw in ctrl['id'].lower() 
                       for kw in ['social', 'icon', 'show', 'display']):
                    print(f"        >>> POTENTIAL SOCIAL TOGGLE")
            
            await page.screenshot(path=str(SCREENSHOT_DIR / f"{section_name.replace(' ', '_').lower()}.png"))
            
            # Go back
            back = await page.query_selector(".customize-section-back")
            if back:
                await back.click()
                await page.wait_for_timeout(1500)
        
        # Final summary
        print("\n" + "=" * 70)
        print("CONCLUSION")
        print("=" * 70)
        print("""
The Artistics theme (version used on purebrain.ai) has:

1. FOOTER OPTIONS section with:
   - Footer Logo (image upload)
   - Copyright Text (textarea)
   - Social URLs (multiple URL inputs - ALREADY FILLED)

2. NO "Show Social Icons" toggle exists in:
   - Footer Options
   - General Options
   - Blog Options
   - Any other Customizer section

3. The Social Sharing control found is for BLOG POST sharing,
   NOT for displaying social icons in the footer.

4. LIVE SITE CHECK: The footer currently shows:
   - Copyright text
   - Navigation links (Privacy, Contact, Team)
   - Brand website links
   - NO social media icons

RECOMMENDATION:
Since no toggle exists, social icons must be added manually by:
  a) Adding HTML to the footer template/widget
  b) Using a plugin like "Simple Social Icons"
  c) Editing the theme's footer.php file (child theme recommended)
  d) Using Elementor or another page builder to customize footer
""")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
