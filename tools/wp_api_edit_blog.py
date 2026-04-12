#!/usr/bin/env python3
"""
Edit the Blog page via WordPress REST API.
This bypasses browser automation and CAPTCHA protection.
"""

import sys
import requests
import json
from base64 import b64encode

# Configuration
WP_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"
BLOG_PAGE_ID = 95

HTML_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-blog-page-v2.html"


def main():
    print("=" * 70)
    print("WordPress REST API Blog Page Editor")
    print("=" * 70)

    # Read HTML content
    try:
        with open(HTML_FILE, 'r') as f:
            html_content = f.read()
        print(f"HTML content loaded: {len(html_content)} characters")
    except FileNotFoundError:
        print(f"ERROR: HTML file not found: {HTML_FILE}")
        return 1

    # Create Basic Auth header
    credentials = f"{WP_USER}:{WP_PASS}"
    token = b64encode(credentials.encode()).decode('ascii')
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
    }

    # Test API access
    print("\n[Step 1] Testing API access...")
    try:
        # Try to get the page first
        response = requests.get(
            f"{WP_URL}/wp-json/wp/v2/pages/{BLOG_PAGE_ID}",
            headers=headers,
            timeout=30
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            page_data = response.json()
            print(f"  Page title: {page_data.get('title', {}).get('rendered', 'N/A')}")
            print(f"  Page status: {page_data.get('status', 'N/A')}")
            print(f"  Page type: {page_data.get('type', 'N/A')}")

            # Check current content
            current_content = page_data.get('content', {}).get('rendered', '')
            print(f"  Current content length: {len(current_content)} characters")

        elif response.status_code == 401:
            print("  Authentication failed. Trying Application Passwords...")
            # WordPress might need Application Passwords instead of regular password
            print("\n  Note: WordPress REST API may require Application Passwords.")
            print("  Go to: Users > Your Profile > Application Passwords in WordPress admin")
            print("  Create a new application password and use that instead.")
            return 1

        elif response.status_code == 403:
            print("  Access forbidden. CORS or permission issue.")
            print(f"  Response: {response.text[:500]}")
            return 1

        else:
            print(f"  Unexpected status: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return 1

    except requests.exceptions.RequestException as e:
        print(f"  Request error: {e}")
        return 1

    # Try to update the page
    print("\n[Step 2] Attempting to update page content...")

    update_data = {
        'content': html_content,
    }

    try:
        response = requests.post(
            f"{WP_URL}/wp-json/wp/v2/pages/{BLOG_PAGE_ID}",
            headers=headers,
            json=update_data,
            timeout=60
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            updated_page = response.json()
            print("  SUCCESS! Page updated.")
            print(f"  New content length: {len(updated_page.get('content', {}).get('rendered', ''))}")
            print(f"  Modified: {updated_page.get('modified', 'N/A')}")
        else:
            print(f"  Update failed: {response.status_code}")
            print(f"  Response: {response.text[:1000]}")

    except requests.exceptions.RequestException as e:
        print(f"  Request error: {e}")
        return 1

    # Verify by fetching the page again
    print("\n[Step 3] Verifying update...")
    try:
        response = requests.get(
            f"{WP_URL}/wp-json/wp/v2/pages/{BLOG_PAGE_ID}",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            page_data = response.json()
            new_content = page_data.get('content', {}).get('rendered', '')
            print(f"  Verified content length: {len(new_content)} characters")
            if 'purebrain-blog' in new_content.lower() or 'neural-feed' in new_content.lower():
                print("  SUCCESS: New content detected!")
            else:
                print("  Warning: Expected content markers not found")
                print(f"  Content preview: {new_content[:500]}")
    except Exception as e:
        print(f"  Verification error: {e}")

    print("\n" + "=" * 70)
    print("API OPERATION COMPLETE!")
    print("\nView the page at: https://purebrain.ai/blog/")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
