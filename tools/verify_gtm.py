#!/usr/bin/env python3
"""Verify GTM is installed on purebrain.ai"""

from playwright.sync_api import sync_playwright
import time

GTM_ID = "GTM-WTDXL4VJ"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    # Force no cache
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        bypass_csp=True
    )
    page = context.new_page()

    # Clear cache
    page.goto("https://purebrain.ai/", wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)

    html = page.content()
    head = page.evaluate('() => document.head.innerHTML')

    print(f"Page length: {len(html)}")
    print(f"Head length: {len(head)}")

    # Check for GTM
    if GTM_ID in html:
        print(f"\nSUCCESS: {GTM_ID} found in page HTML")
    else:
        print(f"\n{GTM_ID} NOT found in page HTML")

    if GTM_ID in head:
        print(f"SUCCESS: {GTM_ID} found in <head>")
    else:
        print(f"{GTM_ID} NOT found in <head>")

    # Check for googletagmanager.com
    if 'googletagmanager.com' in html:
        print("SUCCESS: googletagmanager.com script found!")

        # Extract the exact script
        import re
        gtm_scripts = re.findall(r"https://www\.googletagmanager\.com[^'\"]+", html)
        for script in gtm_scripts[:3]:
            print(f"  Found: {script}")

        # Check for container IDs
        gtm_ids = re.findall(r'GTM-[A-Z0-9]+', html)
        print(f"  Container IDs: {set(gtm_ids)}")
    else:
        print("googletagmanager.com NOT found in HTML")
        print("\nChecking for any GTM-related content...")
        if 'gtm' in html.lower():
            print("  Found 'gtm' in HTML (case insensitive)")

    browser.close()
