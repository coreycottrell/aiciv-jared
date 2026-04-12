#!/usr/bin/env python3
"""
Detailed check of purebrain.ai footer for social icons
"""

import sys
from playwright.sync_api import sync_playwright


def main():
    print("Detailed Footer Analysis for purebrain.ai")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("\nNavigating to purebrain.ai...")
        page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)  # Wait longer for dynamic content

        # Take full page screenshot
        page.screenshot(path="/tmp/purebrain_fullpage.png", full_page=True)
        print("Full page screenshot saved: /tmp/purebrain_fullpage.png")

        # Get page height
        page_height = page.evaluate("() => document.body.scrollHeight")
        print(f"Page height: {page_height}px")

        # Scroll to absolute bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

        # Take viewport screenshot at bottom
        page.screenshot(path="/tmp/purebrain_bottom.png")
        print("Bottom viewport screenshot saved: /tmp/purebrain_bottom.png")

        # Get all footer-related elements
        print("\nLooking for footer elements:")
        footer_selectors = [
            'footer',
            '#footer',
            '.footer',
            '#et-footer',
            '#main-footer',
            '.site-footer',
            '[class*="footer"]',
            '#et-main-area + *',  # Element after main content
        ]

        for selector in footer_selectors:
            elements = page.locator(selector)
            count = elements.count()
            if count > 0:
                print(f"  Found {count} elements for '{selector}'")
                for i in range(min(count, 3)):
                    el = elements.nth(i)
                    tag = el.evaluate("el => el.tagName")
                    cls = el.evaluate("el => el.className")
                    text = el.text_content()[:100] if el.text_content() else ""
                    print(f"    [{i}] <{tag}> class='{cls}' text='{text}'...")

        # Check if there's a Divi-specific footer
        print("\nLooking for Divi footer components:")
        divi_footers = page.locator('#et-footer-info, #footer-info, .et-social-icons, #et-social')
        if divi_footers.count() > 0:
            for i in range(divi_footers.count()):
                el = divi_footers.nth(i)
                print(f"  Found Divi footer element: {el.evaluate('el => el.className')}")

        # Get page structure to understand layout
        print("\nPage structure (main sections):")
        page_structure = page.evaluate("""
            () => {
                const sections = document.querySelectorAll('body > *');
                return Array.from(sections).map(s => ({
                    tag: s.tagName,
                    id: s.id || '',
                    class: s.className || '',
                    height: s.offsetHeight
                })).filter(s => s.height > 50);
            }
        """)
        for section in page_structure:
            print(f"  <{section['tag']}> id='{section['id']}' class='{section['class'][:50]}' h={section['height']}px")

        # Get the actual footer HTML
        print("\nActual footer content:")
        footer_html = page.evaluate("""
            () => {
                const footer = document.querySelector('footer, .footer, #footer');
                if (footer) {
                    return {
                        html: footer.innerHTML.substring(0, 2000),
                        links: Array.from(footer.querySelectorAll('a')).map(a => ({
                            href: a.href,
                            text: a.textContent.trim().substring(0, 50)
                        }))
                    };
                }
                return 'No footer found';
            }
        """)
        if isinstance(footer_html, dict):
            print(f"  HTML preview: {footer_html['html'][:500]}...")
            print(f"\n  Footer links ({len(footer_html['links'])}):")
            for link in footer_html['links']:
                print(f"    - {link['href'][:60]} | '{link['text']}'")
        else:
            print(f"  {footer_html}")

        browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
