#!/usr/bin/env python3
"""
Final verification of GSC meta tag
Date: 2026-02-17
"""

import time
from playwright.sync_api import sync_playwright

GSC_VERIFICATION_CODE = "S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0"

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.set_default_timeout(30000)

        try:
            # Test with cache bust
            cache_bust = str(int(time.time()))
            print(f"Loading purebrain.ai with cache bust: {cache_bust}")
            page.goto(f"https://purebrain.ai/?nocache={cache_bust}", wait_until='domcontentloaded')
            time.sleep(5)

            page_source = page.content()

            # Find the meta tag
            import re
            meta_match = re.search(r'<meta[^>]*google-site-verification[^>]*>', page_source, re.IGNORECASE)

            if meta_match:
                print("\n" + "="*70)
                print("SUCCESS: Meta tag found!")
                print("="*70)
                print(f"\nMeta tag:\n{meta_match.group()}")

                if GSC_VERIFICATION_CODE in meta_match.group():
                    print(f"\nVerification code is CORRECT!")
                    return "VERIFIED"
                else:
                    print("\nWARNING: Verification code doesn't match!")
                    return "WRONG_CODE"
            else:
                print("Meta tag NOT FOUND")

                # Check if Yoast is outputting
                if '<!-- / Yoast SEO plugin. -->' in page_source:
                    print("Yoast SEO IS generating output")
                else:
                    print("Yoast SEO output not detected")

                return "NOT_FOUND"

        except Exception as e:
            print(f"ERROR: {e}")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    result = verify()
    print(f"\nFinal Result: {result}")
