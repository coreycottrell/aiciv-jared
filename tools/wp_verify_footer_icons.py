#!/usr/bin/env python3
"""
Verify current state of social icons in purebrain.ai footer
"""

import sys
from playwright.sync_api import sync_playwright


def main():
    print("Verifying Footer Social Icons State")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("\nNavigating to purebrain.ai...")
        page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        # Scroll to the absolute bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)

        # Take a screenshot
        page.screenshot(path="/tmp/footer_verify.png")
        print("Screenshot saved: /tmp/footer_verify.png")

        # Get all links that could be social media
        print("\nSearching for ANY social media links on the page:")
        all_links = page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a'));
                return links.filter(l =>
                    l.href.includes('linkedin') ||
                    l.href.includes('facebook') ||
                    l.href.includes('twitter') ||
                    l.href.includes('x.com') ||
                    l.href.includes('instagram') ||
                    l.href.includes('youtube')
                ).map(l => ({
                    href: l.href,
                    text: l.textContent.trim().substring(0, 50),
                    class: l.className,
                    parent: l.parentElement ? l.parentElement.className : '',
                    inFooter: l.closest('footer') !== null || l.closest('.footer') !== null
                }));
            }
        """)

        if all_links:
            print(f"\nFound {len(all_links)} social media links:")
            for link in all_links:
                print(f"  - {link['href']}")
                print(f"    In footer: {link['inFooter']}")
                print(f"    Class: {link['class']}")
                print(f"    Parent class: {link['parent']}")
        else:
            print("\nNo social media links found on the page!")

        # Check for social icon elements (SVG, img, i with fa-* classes)
        print("\nSearching for social icon elements:")
        icon_elements = page.evaluate("""
            () => {
                // Check for Font Awesome icons
                const faIcons = Array.from(document.querySelectorAll('[class*="fa-linkedin"], [class*="fa-facebook"], [class*="fa-twitter"], [class*="fa-instagram"]'));

                // Check for SVG icons inside links
                const svgIcons = Array.from(document.querySelectorAll('a svg'));

                // Check for img icons
                const imgIcons = Array.from(document.querySelectorAll('a img[src*="social"], a img[alt*="linkedin"], a img[alt*="facebook"]'));

                return {
                    faIconsCount: faIcons.length,
                    svgIconsCount: svgIcons.length,
                    imgIconsCount: imgIcons.length,
                    faIcons: faIcons.map(i => i.className).slice(0, 5),
                    svgParents: svgIcons.map(s => s.closest('a')?.href || 'no parent link').slice(0, 10)
                };
            }
        """)
        print(f"  Font Awesome icons: {icon_elements['faIconsCount']}")
        print(f"  SVG icons in links: {icon_elements['svgIconsCount']}")
        print(f"  Image icons: {icon_elements['imgIconsCount']}")
        if icon_elements['svgParents']:
            print(f"  SVG icon links: {icon_elements['svgParents']}")

        # Get complete footer HTML for analysis
        print("\nFooter HTML structure:")
        footer_structure = page.evaluate("""
            () => {
                const footer = document.querySelector('footer, .footer');
                if (footer) {
                    // Get all child divs
                    const children = Array.from(footer.children);
                    return {
                        found: true,
                        className: footer.className,
                        childrenCount: children.length,
                        html: footer.outerHTML
                    };
                }
                return { found: false };
            }
        """)

        if footer_structure['found']:
            print(f"  Footer class: {footer_structure['className']}")
            print(f"  Children count: {footer_structure['childrenCount']}")
            # Save full HTML to file
            with open('/tmp/footer_html.txt', 'w') as f:
                f.write(footer_structure['html'])
            print(f"  Full HTML saved to: /tmp/footer_html.txt")

        browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
