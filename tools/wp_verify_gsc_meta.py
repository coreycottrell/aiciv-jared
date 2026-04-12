#!/usr/bin/env python3
"""
Verify Google Search Console Meta Tag
Date: 2026-02-17
"""

import time
from playwright.sync_api import sync_playwright

def verify_meta_tag():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.set_default_timeout(30000)

        try:
            print("Loading purebrain.ai...")
            page.goto("https://purebrain.ai", wait_until='domcontentloaded')
            time.sleep(5)

            # Get full page content
            page_source = page.content()

            # Search for google-site-verification
            if "google-site-verification" in page_source:
                print("\n" + "="*60)
                print("FOUND: google-site-verification in page source!")
                print("="*60)

                # Find the context around it
                import re
                matches = re.findall(r'(.{0,100}google-site-verification.{0,100})', page_source, re.IGNORECASE)
                for i, match in enumerate(matches):
                    print(f"\nMatch {i+1}:")
                    print(match)

                # Extract the actual meta tag if it exists
                meta_match = re.search(r'<meta[^>]*google-site-verification[^>]*>', page_source, re.IGNORECASE)
                if meta_match:
                    print(f"\nFull meta tag: {meta_match.group()}")
            else:
                print("NOT FOUND: google-site-verification not in page source")

            # Also check just the head section
            head_content = page.locator('head').inner_html()
            if "google-site-verification" in head_content:
                print("\nMeta tag IS in <head> section")
            else:
                print("\nMeta tag NOT in <head> section")

            # Check for Yoast's webmaster tools output
            if "yoast" in page_source.lower() and "verification" in page_source.lower():
                print("\nYoast verification section found")

            # Save the head content for review
            with open("/tmp/purebrain_head.html", "w") as f:
                f.write(head_content)
            print("\nHead content saved to /tmp/purebrain_head.html")

            return "DONE"

        except Exception as e:
            print(f"ERROR: {e}")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    result = verify_meta_tag()
    print(f"\nResult: {result}")
