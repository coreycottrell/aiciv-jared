#!/usr/bin/env python3
"""
Check active WP plugins and fetch page content for video comparison.
"""

import requests
import json
import re
import os
from base64 import b64encode

WP_BASE = "https://purebrain.ai/wp-json"
WP_USER = "Aether"
WP_APP_PASSWORD = "ZGuh 1W8k WpWM c9iy kqyd buPr"

auth_str = f"{WP_USER}:{WP_APP_PASSWORD}"
auth_header = b64encode(auth_str.encode()).decode()
HEADERS = {
    "Authorization": f"Basic {auth_header}",
    "Content-Type": "application/json",
}

def fetch_plugins():
    """Fetch active plugins via WP REST API."""
    url = f"{WP_BASE}/wp/v2/plugins"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    print(f"Plugins status: {resp.status_code}")
    if resp.status_code == 200:
        plugins = resp.json()
        print(f"\nActive plugins ({len(plugins)}):")
        for p in plugins:
            if p.get("status") == "active":
                print(f"  ACTIVE: {p.get('name')} | {p.get('plugin')} | v{p.get('version')}")
        return plugins
    else:
        print(f"Error: {resp.text[:300]}")
        return []

def fetch_page_content_raw(page_id):
    """Fetch page content and elementor data."""
    url = f"{WP_BASE}/wp/v2/pages/{page_id}?context=edit"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    print(f"\nPage {page_id} status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        meta = data.get("meta", {})
        elementor_data = meta.get("_elementor_data", "")
        content = data.get("content", {}).get("raw", "")

        # Search for video-related content in elementor_data
        print(f"  Title: {data.get('title', {}).get('rendered', '')}")
        print(f"  Template: {data.get('template', '')}")
        print(f"  Elementor data length: {len(elementor_data)}")
        print(f"  Content length: {len(content)}")

        # Find all editor fields in elementor data that have video/background content
        if elementor_data:
            # Look for video related elements
            for pattern, label in [
                (r'bgVideo', 'bgVideo'),
                (r'video-background', 'video-background class'),
                (r'living-background', 'living-background'),
                (r'vortex', 'vortex'),
                (r'spiral', 'spiral'),
                (r'geometric', 'geometric'),
                (r'\.mp4', 'MP4 file reference'),
                (r'\.m3u8', 'HLS file reference'),
                (r'background_video_link', 'background_video_link'),
            ]:
                count = len(re.findall(pattern, elementor_data, re.IGNORECASE))
                if count > 0:
                    print(f"  FOUND '{label}': {count} occurrences in elementor_data")

            # Extract actual video src values
            mp4_urls = re.findall(r'"(?:url|src)"\s*:\s*"([^"]*\.mp4[^"]*)"', elementor_data)
            if mp4_urls:
                print(f"  MP4 URLs in elementor_data: {list(set(mp4_urls))}")

            # Extract all editor/html content that mentions video
            # Editors are JSON-escaped HTML in "editor" keys
            editor_pattern = re.finditer(r'"editor"\s*:\s*"((?:[^"\\]|\\.)*)"', elementor_data)
            for i, match in enumerate(editor_pattern):
                decoded = match.group(1).replace('\\/', '/').replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                if any(kw in decoded.lower() for kw in ['video', 'bgvideo', 'video-background', 'living-background', 'vortex', 'spiral']):
                    print(f"\n  === VIDEO-RELATED EDITOR #{i} ===")
                    # Find video sources
                    mp4s = re.findall(r'src=["\']([^"\']*)["\']', decoded)
                    print(f"  src attributes: {mp4s}")
                    # Show first 800 chars
                    print(f"  Content preview:\n{decoded[:800]}")
                    print(f"  ...")

            # Also look for background video via Elementor's built-in video widget
            bg_video = re.findall(r'"background_video_link"\s*:\s*"([^"]*)"', elementor_data)
            if bg_video:
                print(f"  Elementor background_video_link: {bg_video}")

        return data
    else:
        print(f"  Error: {resp.text[:200]}")
        return None


def main():
    print("="*80)
    print("CHECKING ACTIVE WP PLUGINS")
    print("="*80)
    plugins = fetch_plugins()

    print("\n" + "="*80)
    print("FETCHING PAGE CONTENT FOR VIDEO COMPARISON")
    print("="*80)

    pages = {
        11: "HOMEPAGE (BROKEN)",
        689: "PAY-TEST-2 (WORKING)",
        1232: "SANDBOX-3 (WORKING)",
    }

    page_data = {}
    for page_id, label in pages.items():
        print(f"\n{'='*40}")
        print(f"PAGE {page_id}: {label}")
        print('='*40)
        data = fetch_page_content_raw(page_id)
        page_data[page_id] = data

    # Quick diff between pages
    print("\n" + "="*80)
    print("QUICK DIFF SUMMARY")
    print("="*80)

    for page_id, label in pages.items():
        data = page_data.get(page_id)
        if data:
            meta = data.get("meta", {})
            ed = meta.get("_elementor_data", "")
            print(f"\nPage {page_id} ({label}):")
            print(f"  has bgVideo: {'bgVideo' in ed}")
            print(f"  has video-background: {'video-background' in ed}")
            print(f"  has living-background: {'living-background' in ed}")
            print(f"  has vortex/spiral/geometric: {any(x in ed.lower() for x in ['vortex','spiral','geometric'])}")


if __name__ == "__main__":
    main()
