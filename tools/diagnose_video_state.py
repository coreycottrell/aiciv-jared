#!/usr/bin/env python3
"""
Quick diagnostic - what is the current state of video on all 3 pages?
Outputs enough info to understand the exact problem before fixing.
"""

import json
import base64
import requests
import re

WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
AUTH = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}"}
BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"

PAGES = [
    (11, "Homepage"),
    (689, "Pay Test 2"),
    (688, "Pay Test Sandbox 2"),
]

for page_id, page_name in PAGES:
    print(f"\n{'='*60}")
    print(f"PAGE {page_id}: {page_name}")
    print('='*60)

    try:
        resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ERROR fetching: {e}")
        continue

    meta = data.get("meta", {})
    ed = meta.get("_elementor_data", "")

    if not ed:
        print("  ERROR: No elementor data")
        continue

    # Parse elementor data to find main widget
    try:
        el_data = json.loads(ed)
    except Exception as e:
        print(f"  ERROR parsing JSON: {e}")
        continue

    # Find main widget
    main_html = None
    for ci, container in enumerate(el_data):
        for wi, widget in enumerate(container.get("elements", [])):
            hc = widget.get("settings", {}).get("html", "")
            if len(hc) > 50000 and "Watch Demo" in hc:
                main_html = hc
                print(f"  Main widget: [container {ci}][element {wi}] len={len(hc)}")
                break
        if main_html:
            break

    if not main_html:
        print("  ERROR: Main HTML widget not found")
        continue

    # Key checks
    print(f"\n  KEY CHECKS:")
    print(f"  - Watch Demo button present: {'YES' if 'Watch Demo' in main_html else 'NO'}")
    print(f"  - openVideoModal function: {'YES' if 'function openVideoModal' in main_html else 'NO'}")
    print(f"  - closeVideoModal function: {'YES' if 'function closeVideoModal' in main_html else 'NO'}")
    print(f"  - #videoModal element: {'YES' if 'id=\"videoModal\"' in main_html else 'NO'}")
    print(f"  - #demoVideo element: {'YES' if 'id=\"demoVideo\"' in main_html else 'NO'}")
    print(f"  - pb-demo-section: {'YES' if 'pb-demo-section' in main_html else 'NO'}")
    print(f"  - #pb-demo-section id: {'YES' if 'id=\"pb-demo-section\"' in main_html else 'NO'}")
    print(f"  - pbDemoPlay function: {'YES' if 'pbDemoPlay' in main_html else 'NO'}")
    print(f"  - hls.js loaded: {'YES' if 'hls.js' in main_html or 'hls.min.js' in main_html else 'NO'}")
    print(f"  - HLS.isSupported: {'YES' if 'Hls.isSupported' in main_html else 'NO'}")
    print(f"  - Portal Demo video: {'YES' if 'eaf39ae1_Portal_demo' in main_html else 'NO'}")
    print(f"  - PureBrain Demo video: {'YES' if '75114256_Pure-Brain-Demo-Video' in main_html else 'NO'}")
    print(f"  - startModalHls: {'YES' if 'startModalHls' in main_html else 'NO'}")

    # Find HLS URLs
    hls_urls = list(set(re.findall(r'https://[^\s"\'\\]+\.m3u8', main_html)))
    print(f"\n  HLS URLs in page:")
    for url in hls_urls:
        print(f"    {url}")
    if not hls_urls:
        print(f"    NONE FOUND")

    # Find awakening hrefs
    awk_hrefs = list(set(re.findall(r'href=["\'][^"\']*awakening[^"\']*["\']', main_html)))
    print(f"\n  Awakening hrefs:")
    for href in awk_hrefs:
        print(f"    {href}")
    if not awk_hrefs:
        print(f"    NONE FOUND")

    # Show openVideoModal function body
    ovm_pos = main_html.find("function openVideoModal()")
    if ovm_pos != -1:
        brace = main_html.find("{", ovm_pos)
        end = main_html.find("}", brace) + 1
        # Get full function (may have nested braces)
        depth = 0
        pos = brace
        while pos < len(main_html):
            if main_html[pos] == '{':
                depth += 1
            elif main_html[pos] == '}':
                depth -= 1
                if depth == 0:
                    end = pos + 1
                    break
            pos += 1
        print(f"\n  openVideoModal function body:")
        print(f"    {main_html[ovm_pos:end][:600]}")

    # Show Watch Demo button context
    wd_pos = main_html.find("Watch Demo")
    if wd_pos != -1:
        print(f"\n  Watch Demo context (200 chars around):")
        print(f"    {main_html[max(0,wd_pos-100):wd_pos+200]}")

    # Show pb-demo-section context if present
    pds_pos = main_html.find("pb-demo-section")
    if pds_pos != -1:
        print(f"\n  pb-demo-section context (300 chars from start):")
        section_html_start = main_html.rfind("<section", 0, pds_pos + 50)
        print(f"    {main_html[section_html_start:section_html_start+400]}")
