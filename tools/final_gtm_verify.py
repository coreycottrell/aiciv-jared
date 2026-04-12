#!/usr/bin/env python3
"""Final GTM verification with detailed output"""

import time
import re
from playwright.sync_api import sync_playwright

GTM_ID = "GTM-WTDXL4VJ"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        # Disable caching
        extra_http_headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache'
        }
    )
    page = context.new_page()

    # Navigate with cache bust
    url = f"https://purebrain.ai/?verify={int(time.time())}"
    print(f"Loading: {url}")

    page.goto(url, wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)

    html = page.content()
    head = page.evaluate('() => document.head.innerHTML')

    print(f"\nPage size: {len(html)} chars")
    print(f"Head size: {len(head)} chars")

    # Search for GTM
    print(f"\nSearching for {GTM_ID}...")

    if GTM_ID in html:
        print(f"  FOUND in full HTML!")

        # Find the context
        idx = html.find(GTM_ID)
        context_start = max(0, idx - 100)
        context_end = min(len(html), idx + 100)
        print(f"  Context: ...{html[context_start:context_end]}...")

    if GTM_ID in head:
        print(f"  FOUND in <head>!")

    # Search for googletagmanager
    if 'googletagmanager.com' in html:
        print("\nFound googletagmanager.com references:")
        matches = re.findall(r'[^"\']*googletagmanager\.com[^"\']*', html)
        for m in set(matches):
            print(f"  {m}")

    # Find all GTM container IDs
    gtm_ids = re.findall(r'GTM-[A-Z0-9]+', html)
    if gtm_ids:
        print(f"\nGTM Container IDs found: {set(gtm_ids)}")
    else:
        print("\nNo GTM Container IDs found in page")

    # Check for GTM snippet in scripts
    print("\nChecking scripts...")
    scripts = page.evaluate('''() => {
        const scripts = document.querySelectorAll('script');
        const results = [];
        for (let s of scripts) {
            const src = s.src || '';
            const text = s.innerText || '';
            if (src.includes('gtm') || src.includes('tagmanager') ||
                text.includes('GTM-') || text.includes('googletagmanager')) {
                results.push({
                    src: src.substring(0, 200),
                    text: text.substring(0, 200)
                });
            }
        }
        return results;
    }''')

    if scripts:
        print(f"Found {len(scripts)} GTM-related scripts:")
        for s in scripts:
            if s['src']:
                print(f"  SRC: {s['src']}")
            if s['text']:
                print(f"  INLINE: {s['text'][:150]}...")
    else:
        print("No GTM-related scripts found")

    # Also check for noscript GTM
    noscripts = page.query_selector_all('noscript')
    for ns in noscripts:
        inner = ns.inner_html()
        if 'gtm' in inner.lower() or 'googletagmanager' in inner.lower():
            print(f"\nFound GTM in <noscript>: {inner[:150]}...")

    browser.close()

    print("\n" + "="*60)
    if GTM_ID in html or GTM_ID in head:
        print(f"RESULT: GTM {GTM_ID} is INSTALLED and ACTIVE!")
    else:
        print(f"RESULT: GTM {GTM_ID} not found")
    print("="*60)
