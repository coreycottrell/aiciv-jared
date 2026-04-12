#!/usr/bin/env python3
"""
Diagnose current video state on all 3 pages.
Checks:
1. Is pb-demo-section present?
2. Is Watch Demo button present?
3. What HLS URL is used?
4. What are the awakening links pointing to?
5. What video is in the embedded section?
"""

import os
import json
import base64
import requests
import re

WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"

AUTH = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"

PAGES = [
    (11, "Homepage (purebrain.ai/)"),
    (689, "Pay Test 2 (/pay-test-2/)"),
    (688, "Pay Test Sandbox 2 (/pay-test-sandbox-2/)"),
]

for page_id, page_name in PAGES:
    print(f"\n{'='*70}")
    print(f"PAGE: {page_name} (ID: {page_id})")
    print('='*70)

    resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS)
    if resp.status_code != 200:
        print(f"  ERROR: HTTP {resp.status_code}")
        continue

    data = resp.json()
    meta = data.get("meta", {})
    ed = meta.get("_elementor_data", "")

    if not ed:
        print("  ERROR: No _elementor_data found")
        continue

    print(f"  Elementor data length: {len(ed)} chars")

    # Check for pb-demo-section
    has_demo_section = "pb-demo-section" in ed
    print(f"  pb-demo-section present: {has_demo_section}")

    # Check for Watch Demo
    has_watch_demo = "Watch Demo" in ed
    print(f"  Watch Demo button present: {has_watch_demo}")

    # Check for openVideoModal
    has_open_modal = "openVideoModal" in ed
    print(f"  openVideoModal function present: {has_open_modal}")

    # Find what HLS URLs are in the page
    hls_urls = re.findall(r'https://[^\s"\']+\.m3u8', ed)
    if hls_urls:
        print(f"  HLS URLs found:")
        for url in set(hls_urls):
            print(f"    - {url}")
    else:
        print(f"  HLS URLs: NONE FOUND")

    # Find awakening links
    awakening_links = re.findall(r'href=["\'][^"\']*awakening[^"\']*["\']', ed)
    if awakening_links:
        print(f"  Awakening links:")
        for link in set(awakening_links):
            print(f"    - {link}")
    else:
        print(f"  Awakening links: NONE FOUND")

    # Find Watch Demo button href if any
    watch_demo_context = re.findall(r'.{0,200}Watch Demo.{0,200}', ed)
    if watch_demo_context:
        print(f"\n  Watch Demo context (first match):")
        print(f"    {watch_demo_context[0][:300]}")

    # Find pb-demo-section context
    if has_demo_section:
        idx = ed.find("pb-demo-section")
        print(f"\n  pb-demo-section context:")
        print(f"    {ed[max(0,idx-50):idx+200]}")

    # Check for Pure Brain Demo video URL
    purebrain_demo = "75114256_Pure-Brain-Demo-Video" in ed
    portal_demo = "eaf39ae1_Portal_demo" in ed
    print(f"\n  Pure Brain Demo Video (75114256): {purebrain_demo}")
    print(f"  Portal Demo Video (eaf39ae1): {portal_demo}")

    # Check for autoplay on embedded video
    if has_demo_section:
        autoplay_in_embed = "autoplay" in ed[ed.find("pb-demo-section"):ed.find("pb-demo-section")+5000] if has_demo_section else False
        print(f"  Autoplay attr in demo section: {autoplay_in_embed}")

    print()

print("\nDIAGNOSIS COMPLETE")
