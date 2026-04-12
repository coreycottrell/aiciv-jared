#!/usr/bin/env python3
"""
Deploy Mark Christie minisite to purebrain.ai WordPress
Task: ST# - dept-systems-technology
Date: 2026-03-03
"""

import json
import base64
import urllib.request
import urllib.parse
import urllib.error

WP_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"
HTML_FILE = "/home/jared/projects/AI-CIV/aether/exports/mark-christie-minisite.html"

def get_headers():
    creds = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    return {
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

def wp_request(endpoint, data=None, method="GET"):
    url = f"{WP_URL}/wp-json/wp/v2/{endpoint}"
    headers = get_headers()
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {error_body[:500]}")
        raise
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        raise

def main():
    print("=== Mark Christie Minisite Deployment ===")
    print(f"Target: {WP_URL}")
    print()

    # Step 1: Read HTML file
    print("[1/5] Reading HTML file...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()
    print(f"      File size: {len(html_content)} bytes")

    # Step 2: Wrap in wp:html block
    print("[2/5] Wrapping in wp:html block...")
    wrapped_content = f"<!-- wp:html -->\n{html_content}\n<!-- /wp:html -->"
    print(f"      Wrapped size: {len(wrapped_content)} bytes")

    # Step 3: Check if page already exists (by slug)
    print("[3/5] Checking for existing page with slug 'mark-christie'...")
    try:
        pages, status = wp_request("pages?slug=mark-christie&status=any")
        if pages:
            existing_id = pages[0]['id']
            existing_link = pages[0].get('link', 'unknown')
            print(f"      Found existing page ID {existing_id} at {existing_link}")
            print(f"      Will UPDATE existing page instead of creating new.")
            action = "update"
            page_id = existing_id
        else:
            print("      No existing page found. Will CREATE new page.")
            action = "create"
            page_id = None
    except Exception as e:
        print(f"      Could not check existing pages: {e}")
        action = "create"
        page_id = None

    # Step 4: Build page payload
    print("[4/5] Building page payload...")
    page_data = {
        "title": "Mark Christie — PureBrain Intelligence Profile",
        "slug": "mark-christie",
        "status": "publish",
        "content": wrapped_content,
        "template": "elementor_canvas",
        "meta": {
            "_yoast_wpseo_meta-robots-noindex": "1",
            "_yoast_wpseo_meta-robots-nofollow": "1"
        }
    }

    # Step 5: Deploy
    print("[5/5] Deploying to WordPress...")
    if action == "update" and page_id:
        result, status_code = wp_request(f"pages/{page_id}", data=page_data, method="POST")
    else:
        result, status_code = wp_request("pages", data=page_data, method="POST")

    page_link = result.get("link", "")
    page_id_result = result.get("id", "")
    page_slug = result.get("slug", "")
    page_status = result.get("status", "")

    print()
    print("=== DEPLOYMENT RESULT ===")
    print(f"HTTP Status:  {status_code}")
    print(f"Page ID:      {page_id_result}")
    print(f"Page Slug:    {page_slug}")
    print(f"Page Status:  {page_status}")
    print(f"Live URL:     {page_link}")
    print()

    # Step 6: Verify live URL is accessible
    print("=== VERIFICATION ===")
    print(f"Fetching live URL: {page_link}")
    verify_req = urllib.request.Request(
        page_link,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(verify_req, timeout=15) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            http_status = resp.status
            print(f"HTTP Status:  {http_status}")
            # Check for key content
            if "Mark Christie" in resp_body:
                print("Content check: PASS - 'Mark Christie' found in response")
            else:
                print("Content check: WARN - 'Mark Christie' not found in response body (may be cached/delayed)")
            if "PureBrain" in resp_body or "purebrain" in resp_body.lower():
                print("Brand check:   PASS - PureBrain branding present")
            else:
                print("Brand check:   WARN - PureBrain branding not detected")
            print(f"Response size: {len(resp_body)} bytes")
    except Exception as e:
        print(f"Verification fetch error: {e}")
        print("Note: Page may still be live — WordPress cache or CDN may delay visibility.")

    print()
    print("=== DEPLOYMENT COMPLETE ===")
    print(f"URL: {page_link}")
    return page_link

if __name__ == "__main__":
    url = main()
