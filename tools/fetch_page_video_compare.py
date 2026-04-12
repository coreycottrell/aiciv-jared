#!/usr/bin/env python3
"""
Fetch and compare video/background sections from pages 11, 689, 1232
to diagnose mobile video background bug on page 11 (homepage).
"""

import requests
import json
import re
import os
from base64 import b64encode

WP_BASE = "https://purebrain.ai/wp-json/wp/v2"
# Credentials from .env: User "Aether", App Password "ZGuh 1W8k WpWM c9iy kqyd buPr"
# (Also have PUREBRAIN_WP_APP_PASSWORD from .env)
WP_USER = "Aether"
WP_APP_PASSWORD = "ZGuh 1W8k WpWM c9iy kqyd buPr"

auth_str = f"{WP_USER}:{WP_APP_PASSWORD}"
auth_header = b64encode(auth_str.encode()).decode()
HEADERS = {
    "Authorization": f"Basic {auth_header}",
    "Content-Type": "application/json",
}

PAGE_IDS = {
    "homepage_11_BROKEN": 11,
    "pay_test_2_689_WORKING": 689,
    "sandbox_3_1232_WORKING": 1232,
}

def extract_video_info(data):
    """Extract video-related elements from page data."""
    info = {}

    # Template
    info["template"] = data.get("template", "NOT SET")
    info["title"] = data.get("title", {}).get("rendered", "")
    info["slug"] = data.get("slug", "")

    # Check post_content for video markup
    content = data.get("content", {}).get("rendered", "")
    info["content_has_bgVideo"] = "bgVideo" in content
    info["content_has_video_background"] = "video-background" in content
    info["content_has_living_background"] = "living-background" in content
    info["content_has_vortex"] = "vortex" in content.lower()
    info["content_has_spiral"] = "spiral" in content.lower()
    info["content_has_geometric"] = "geometric" in content.lower()

    # Extract video src from content
    video_srcs = re.findall(r'src=["\']([^"\']*\.mp4[^"\']*)["\']', content)
    info["content_video_srcs"] = video_srcs

    # Also check for HLS manifest
    hls_srcs = re.findall(r'src=["\']([^"\']*\.m3u8[^"\']*)["\']', content)
    info["content_hls_srcs"] = hls_srcs

    # Check meta / elementor_data
    meta = data.get("meta", {})
    elementor_data_raw = meta.get("_elementor_data", "")

    if elementor_data_raw:
        info["has_elementor_data"] = True
        info["elementor_data_length"] = len(elementor_data_raw)

        # Search for video-related strings in elementor data
        info["elementor_has_bgVideo"] = "bgVideo" in elementor_data_raw
        info["elementor_has_video_background"] = "video-background" in elementor_data_raw
        info["elementor_has_living_background"] = "living-background" in elementor_data_raw
        info["elementor_has_vortex"] = "vortex" in elementor_data_raw.lower()
        info["elementor_has_spiral"] = "spiral" in elementor_data_raw.lower()
        info["elementor_has_geometric"] = "geometric" in elementor_data_raw.lower()

        # Extract video URLs from elementor data
        elementor_video_srcs = re.findall(r'"url"\s*:\s*"([^"]*\.mp4[^"]*)"', elementor_data_raw)
        info["elementor_video_mp4_urls"] = list(set(elementor_video_srcs))

        hls_elementor = re.findall(r'"url"\s*:\s*"([^"]*\.m3u8[^"]*)"', elementor_data_raw)
        info["elementor_video_hls_urls"] = list(set(hls_elementor))

        # Look for any video-type elements
        video_type_matches = re.findall(r'"video_type"\s*:\s*"([^"]*)"', elementor_data_raw)
        info["elementor_video_types"] = list(set(video_type_matches))

        # Look for background_video_link
        bg_video_links = re.findall(r'"background_video_link"\s*:\s*"([^"]*)"', elementor_data_raw)
        info["elementor_bg_video_links"] = list(set(bg_video_links))

        # Look for custom HTML widgets (which is where video markup likely lives)
        html_widgets = re.findall(r'"widgetType"\s*:\s*"html"', elementor_data_raw)
        info["elementor_html_widget_count"] = len(html_widgets)

        # Extract content from html widgets
        # Find all html widget innerHTML
        # Pattern: look for "elType":"widget","isInner":...,"widgetType":"html" then find "editor" value
        editor_matches = re.findall(r'"editor"\s*:\s*"((?:[^"\\]|\\.)*)\"', elementor_data_raw)
        info["elementor_html_editors_count"] = len(editor_matches)

        # Check each editor for video content
        video_editors = []
        for i, editor in enumerate(editor_matches):
            decoded = editor.replace('\\/', '/').replace('\\n', '\n').replace('\\"', '"')
            if any(k in decoded for k in ["video", "bgVideo", "video-background", "living-background", "vortex", "spiral"]):
                # Extract video sources from this editor
                editor_mp4 = re.findall(r'src=["\']([^"\']*\.mp4[^"\']*)["\']', decoded)
                editor_hls = re.findall(r'src=["\']([^"\']*\.m3u8[^"\']*)["\']', decoded)
                video_editors.append({
                    "index": i,
                    "has_bgVideo": "bgVideo" in decoded,
                    "has_video_background": "video-background" in decoded,
                    "has_living_background": "living-background" in decoded,
                    "has_vortex": "vortex" in decoded.lower(),
                    "has_spiral": "spiral" in decoded.lower(),
                    "mp4_srcs": editor_mp4,
                    "hls_srcs": editor_hls,
                    "snippet": decoded[:500],
                })
        info["elementor_video_editors"] = video_editors

    else:
        info["has_elementor_data"] = False

    return info

def main():
    results = {}

    for label, page_id in PAGE_IDS.items():
        print(f"\nFetching page {page_id} ({label})...")
        url = f"{WP_BASE}/pages/{page_id}?context=edit"

        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            print(f"  Status: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                results[label] = extract_video_info(data)
            else:
                results[label] = {"error": f"HTTP {resp.status_code}", "body": resp.text[:200]}
        except Exception as e:
            results[label] = {"error": str(e)}

    # Print comparison
    print("\n" + "="*80)
    print("VIDEO BACKGROUND COMPARISON")
    print("="*80)

    for label, info in results.items():
        print(f"\n--- {label} ---")
        if "error" in info:
            print(f"ERROR: {info['error']}")
            continue
        for key, val in info.items():
            if key not in ("elementor_video_editors",):
                print(f"  {key}: {val}")

        if "elementor_video_editors" in info:
            editors = info["elementor_video_editors"]
            print(f"  Video editors ({len(editors)}):")
            for ed in editors:
                print(f"    Editor #{ed['index']}:")
                for k, v in ed.items():
                    if k != "snippet":
                        print(f"      {k}: {v}")
                print(f"      snippet: {ed.get('snippet', '')[:200]}")

    # Save full results
    output_path = "/home/jared/projects/AI-CIV/aether/exports/video_compare_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull results saved to: {output_path}")

    return results

if __name__ == "__main__":
    main()
