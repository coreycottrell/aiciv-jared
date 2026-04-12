#!/usr/bin/env python3
"""
Check purebrain.ai footer for social icons
"""

import sys
from playwright.sync_api import sync_playwright


def main():
    print("Checking purebrain.ai footer for social icons")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Navigate to the site with longer timeout
        print("\nNavigating to purebrain.ai...")
        page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)  # Wait for dynamic content

        # Scroll to footer
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

        # Take screenshot of footer
        page.screenshot(path="/tmp/purebrain_footer_check.png")
        print("Screenshot saved: /tmp/purebrain_footer_check.png")

        # Check for footer element
        footer = page.locator('footer, #footer, .footer, #et-footer')
        if footer.count() > 0:
            print(f"\nFound footer element")
            footer_html = footer.first.inner_html()
            print(f"Footer HTML length: {len(footer_html)} characters")

        # Check for social links
        print("\nSearching for social media links in footer:")

        social_platforms = {
            "linkedin": ["linkedin.com", "linkedin"],
            "facebook": ["facebook.com", "fb.com"],
            "twitter": ["twitter.com", "x.com"],
            "instagram": ["instagram.com"],
            "youtube": ["youtube.com"],
        }

        for platform, patterns in social_platforms.items():
            for pattern in patterns:
                links = page.locator(f'footer a[href*="{pattern}"], #footer a[href*="{pattern}"], .footer a[href*="{pattern}"]')
                if links.count() > 0:
                    href = links.first.get_attribute("href")
                    print(f"  [FOUND] {platform}: {href}")
                    break
            else:
                # Check whole page for the pattern
                page_links = page.locator(f'a[href*="{patterns[0]}"]')
                if page_links.count() > 0:
                    href = page_links.first.get_attribute("href")
                    print(f"  [FOUND - not in footer] {platform}: {href}")
                else:
                    print(f"  [NOT FOUND] {platform}")

        # Get footer structure for debugging
        print("\nFooter element structure:")
        footer_info = page.evaluate("""
            () => {
                const footer = document.querySelector('footer, #footer, .footer, #et-footer');
                if (!footer) return 'No footer found';

                // Get all links in footer
                const links = Array.from(footer.querySelectorAll('a'));
                return {
                    tag: footer.tagName,
                    id: footer.id,
                    class: footer.className,
                    linkCount: links.length,
                    socialLinks: links.filter(l =>
                        l.href.includes('linkedin') ||
                        l.href.includes('facebook') ||
                        l.href.includes('twitter') ||
                        l.href.includes('x.com') ||
                        l.href.includes('instagram') ||
                        l.href.includes('youtube')
                    ).map(l => l.href)
                };
            }
        """)
        print(f"  {footer_info}")

        browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
