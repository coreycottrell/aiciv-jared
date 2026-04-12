#!/usr/bin/env python3
"""
Check the actual live footer for social icons.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/live-footer-check")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

async def main():
    print("=" * 60)
    print("Check Live Footer for Social Icons")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        # Go to the live site
        print("\n[LOADING PUREBRAIN.AI]")
        await page.goto("https://purebrain.ai")
        await page.wait_for_timeout(5000)
        
        # Take full page screenshot
        await page.screenshot(path=str(SCREENSHOT_DIR / "01_fullpage.png"), full_page=True)
        print(f"[SCREENSHOT] 01_fullpage.png")
        
        # Scroll to the very bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(SCREENSHOT_DIR / "02_bottom.png"))
        print(f"[SCREENSHOT] 02_bottom.png")
        
        # Get footer content
        footer_content = await page.evaluate("""
            () => {
                const footer = document.querySelector('footer');
                if (!footer) {
                    // Try to find anything at the bottom
                    const allDivs = document.querySelectorAll('div');
                    for (let i = allDivs.length - 1; i >= 0; i--) {
                        const div = allDivs[i];
                        if (div.getBoundingClientRect().bottom >= window.innerHeight - 200) {
                            if (div.innerText.includes('2024') || div.innerText.includes('2025') || 
                                div.innerText.includes('copyright') || div.innerText.includes('Pure')) {
                                return {
                                    type: 'div-footer',
                                    html: div.innerHTML.substring(0, 2000),
                                    text: div.innerText
                                };
                            }
                        }
                    }
                    return {type: 'not-found', html: 'no footer element'};
                }
                return {
                    type: 'footer-element',
                    html: footer.innerHTML,
                    text: footer.innerText,
                    classList: footer.className
                };
            }
        """)
        
        print(f"\n[FOOTER ANALYSIS]")
        print(f"  Type: {footer_content.get('type', 'unknown')}")
        print(f"  Class: {footer_content.get('classList', 'none')}")
        print(f"  Text: {footer_content.get('text', 'none')[:200]}")
        
        # Check for social icons in footer HTML
        html = footer_content.get('html', '')
        
        social_patterns = [
            ('linkedin', 'LinkedIn'),
            ('facebook', 'Facebook'),
            ('twitter', 'Twitter'),
            ('instagram', 'Instagram'),
            ('youtube', 'YouTube'),
            ('fa-linkedin', 'Font Awesome LinkedIn'),
            ('fa-facebook', 'Font Awesome Facebook'),
            ('fa-twitter', 'Font Awesome Twitter'),
            ('fa-instagram', 'Font Awesome Instagram'),
            ('social-icon', 'Social Icon class'),
            ('social_links', 'Social Links class'),
            ('icon-social', 'Icon Social class')
        ]
        
        print(f"\n[SOCIAL ICON CHECK IN FOOTER]")
        found_social = False
        for pattern, name in social_patterns:
            if pattern.lower() in html.lower():
                print(f"  [FOUND] {name}: Yes")
                found_social = True
                # Show context
                idx = html.lower().find(pattern.lower())
                snippet = html[max(0, idx-30):idx+80]
                print(f"    Context: ...{snippet}...")
            else:
                print(f"  [ ] {name}: No")
        
        if not found_social:
            print("\n  !!! NO SOCIAL ICONS FOUND IN FOOTER !!!")
            print("  The theme may need manual HTML/CSS to display social icons.")
        
        # Also check for any social-related elements anywhere on page
        print(f"\n[PAGE-WIDE SOCIAL CHECK]")
        page_social = await page.evaluate("""
            () => {
                const results = [];
                const elements = document.querySelectorAll('[class*="social"], [id*="social"], [href*="linkedin"], [href*="facebook"], [href*="twitter"], [href*="instagram"]');
                for (const el of elements) {
                    results.push({
                        tag: el.tagName,
                        class: el.className,
                        id: el.id,
                        href: el.href || '',
                        text: el.innerText?.substring(0, 50) || ''
                    });
                }
                return results;
            }
        """)
        
        print(f"  Found {len(page_social)} social-related elements:")
        for el in page_social[:10]:  # Show first 10
            print(f"    {el}")
        
        await browser.close()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        if found_social:
            print("Social icons ARE present in the footer.")
        else:
            print("Social icons are NOT present in the footer.")
            print("\nThe Artistics theme has Social URLs fields but NO toggle to show/hide them.")
            print("The theme likely requires manual footer template modification to display social icons.")

if __name__ == "__main__":
    asyncio.run(main())
