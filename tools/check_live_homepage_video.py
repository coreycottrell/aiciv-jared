#!/usr/bin/env python3
"""
Check live homepage HTML to see what video scripts are present,
and check plugin states via WP REST API.
"""

import requests
import json
import re
from base64 import b64encode

WP_BASE = "https://purebrain.ai/wp-json"
WP_USER = "Aether"
WP_APP_PASSWORD = "ZGuh 1W8k WpWM c9iy kqyd buPr"

auth_str = f"{WP_USER}:{WP_APP_PASSWORD}"
auth_header = b64encode(auth_str.encode()).decode()
AUTH_HEADERS = {
    "Authorization": f"Basic {auth_header}",
    "Content-Type": "application/json",
}

def check_plugins():
    """Check active plugins and their versions."""
    url = f"{WP_BASE}/wp/v2/plugins?per_page=100"
    resp = requests.get(url, headers=AUTH_HEADERS, timeout=30)
    print(f"Plugins API status: {resp.status_code}")
    if resp.status_code == 200:
        plugins = resp.json()
        video_related = []
        security_related = []
        for p in plugins:
            name = p.get("name", "")
            slug = p.get("plugin", "")
            version = p.get("version", "")
            status = p.get("status", "")
            if status == "active":
                if any(kw in name.lower() or kw in slug.lower() for kw in ["video", "security", "pb-"]):
                    print(f"  ACTIVE: {name} | {slug} | v{version}")
        return plugins
    elif resp.status_code == 401:
        print("  Auth failed")
        return []
    else:
        print(f"  Error: {resp.status_code} {resp.text[:200]}")
        return []

def check_live_html():
    """Fetch homepage HTML and look for video scripts."""
    print("\nFetching live homepage HTML...")
    # Simulate mobile user agent
    mobile_headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    }
    resp = requests.get("https://purebrain.ai/", headers=mobile_headers, timeout=30)
    print(f"Status: {resp.status_code}")

    html = resp.text

    # Look for pb-video-mobile-pause script
    if "pb-video-mobile-pause" in html:
        print("  FOUND: pb-video-mobile-pause script in HTML")
        # Extract the script content
        match = re.search(r'<script id="pb-video-mobile-pause">(.*?)</script>', html, re.DOTALL)
        if match:
            script = match.group(1)
            print(f"\n  === pb-video-mobile-pause CONTENT ===")
            print(script[:1000])
            print("  ...")

            # Key check: does it HIDE or SHOW video on mobile?
            if "wrapper.style.display = 'none'" in script or "vid.style.display = 'none'" in script:
                print("\n  *** SMOKING GUN: Script HIDES video on mobile (OLD behavior) ***")
            elif "wrapper.style.zIndex = '0'" in script:
                print("\n  *** GOOD: Script sets z-index to 0 on mobile (NEW behavior) ***")
    else:
        print("  NOT FOUND: pb-video-mobile-pause script")

    # Look for pb-video-handler-css
    if "pb-video-handler-css" in html:
        print("\n  FOUND: pb-video-handler-css in HTML (pb-video-handler plugin is active)")
        match = re.search(r'<style id="pb-video-handler-css">(.*?)</style>', html, re.DOTALL)
        if match:
            print(f"  CSS content:\n{match.group(1)[:500]}")
    else:
        print("\n  NOT FOUND: pb-video-handler-css (pb-video-handler plugin NOT active?)")

    # Look for video elements
    print("\n  Video elements in HTML:")
    vid_elements = re.findall(r'<video[^>]*id=["\']bgVideo["\'][^>]*>', html)
    for v in vid_elements:
        print(f"    {v}")

    # Look for source elements (video sources)
    if "bgVideo" in html:
        # Find the full video block
        vid_block = re.search(r'(<video[^>]*id=["\']bgVideo["\'][^>]*>.*?</video>)', html, re.DOTALL)
        if vid_block:
            print(f"\n  Full bgVideo element:\n{vid_block.group(1)[:800]}")

    # Look for living-background
    if "living-background" in html:
        print("\n  FOUND: living-background element")
        lb_match = re.search(r'(<[^>]*class=["\'][^"\']*living-background[^"\']*["\'][^>]*>.*?</[^>]+>)', html, re.DOTALL)
        if lb_match:
            print(f"  living-background element (first 300 chars): {lb_match.group(1)[:300]}")
    else:
        print("\n  NOT FOUND: living-background (no spiral/vortex element by this class)")

    # Check for vortex/spiral canvas or divs
    for kw in ["vortex", "spiral", "geometric", "canvas"]:
        count = html.lower().count(kw)
        if count > 0:
            print(f"  '{kw}' appears {count} times in HTML")

    # Save the full HTML for inspection
    output_path = "/home/jared/projects/AI-CIV/aether/exports/homepage_mobile_html.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n  Full HTML saved to: {output_path}")

    return html


def check_page_elementor_data(page_id, label):
    """Check elementor data for video references."""
    url = f"{WP_BASE}/wp/v2/pages/{page_id}?context=edit"
    resp = requests.get(url, headers=AUTH_HEADERS, timeout=30)
    print(f"\nPage {page_id} ({label}) - Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"  Error: {resp.text[:200]}")
        return

    data = resp.json()
    meta = data.get("meta", {})
    elementor_data = meta.get("_elementor_data", "")

    print(f"  Template: {data.get('template', '')}")
    print(f"  Elementor data length: {len(elementor_data)}")

    if elementor_data:
        # Key checks
        checks = {
            "bgVideo": "bgVideo",
            "video-background": "video-background",
            "living-background": "living-background",
            "vortex": "vortex",
            "spiral": "spiral",
        }
        for key, pattern in checks.items():
            found = pattern.lower() in elementor_data.lower()
            print(f"  '{key}': {found}")

        # Extract video file URLs from editor HTML
        # Decode JSON-escaped HTML in editor fields
        editor_matches = re.finditer(r'"editor"\s*:\s*"((?:[^"\\]|\\.)*)"', elementor_data)
        video_editors = []
        for i, match in enumerate(editor_matches):
            raw = match.group(1)
            decoded = raw.replace('\\/', '/').replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            if any(kw in decoded.lower() for kw in ['video', 'bgvideo', 'video-background', 'living-background']):
                srcs = re.findall(r'src=["\']([^"\']+)["\']', decoded)
                video_editors.append({
                    "index": i,
                    "srcs": srcs,
                    "preview": decoded[:600],
                })

        if video_editors:
            print(f"\n  Video-related HTML editors ({len(video_editors)}):")
            for ed in video_editors:
                print(f"\n  Editor #{ed['index']}:")
                print(f"    src attributes: {ed['srcs']}")
                print(f"    Preview:\n{ed['preview'][:600]}")
        else:
            print("  No video-related HTML editors found (video may be in section background settings)")

        # Check Elementor section background video settings
        bg_video_links = re.findall(r'"background_video_link"\s*:\s*"([^"]*)"', elementor_data)
        if bg_video_links:
            print(f"  Elementor background_video_link settings: {bg_video_links}")

    return data


def main():
    print("="*80)
    print("STEP 1: CHECK ACTIVE PLUGINS")
    print("="*80)
    check_plugins()

    print("\n" + "="*80)
    print("STEP 2: CHECK LIVE HOMEPAGE HTML (MOBILE UA)")
    print("="*80)
    check_live_html()

    print("\n" + "="*80)
    print("STEP 3: CHECK ELEMENTOR DATA ON ALL 3 PAGES")
    print("="*80)
    for page_id, label in [(11, "HOMEPAGE-BROKEN"), (689, "PAY-TEST-2-WORKING"), (1232, "SANDBOX-3-WORKING")]:
        check_page_elementor_data(page_id, label)


if __name__ == "__main__":
    main()
