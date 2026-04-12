#!/usr/bin/env python3
"""
Update PureBrain API endpoint URLs in WordPress Elementor pages.

Replaces self-signed cert IP:port references with the new trusted domain.

FROM: https://89.167.19.20:8443/api/...
TO:   https://api.purebrain.ai/api/...

Affects pages:
  - ID 439: pay-test
  - ID 468: pay-test-sandbox

Author: devops-engineer
Date: 2026-02-20
"""

import json
import os
import sys
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# Configuration
# ============================================================

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_FILE = AETHER_ROOT / ".env"
load_dotenv(ENV_FILE)

WORDPRESS_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_APP_PASSWORD = os.environ.get("PUREBRAIN_WP_APP_PASSWORD", "")

# Old IP-based URL pattern to replace
OLD_BASE_URL = "https://89.167.19.20:8443"

# New trusted domain URL
NEW_BASE_URL = "https://api.purebrain.ai"

# Pages to update
TARGET_PAGES = [
    {"id": 439, "slug": "pay-test", "description": "Pay-test (live)"},
    {"id": 468, "slug": "pay-test-sandbox", "description": "Pay-test-sandbox"},
]

# Specific endpoint strings to update
ENDPOINT_REPLACEMENTS = [
    (f"{OLD_BASE_URL}/api/log-conversation", f"{NEW_BASE_URL}/api/log-conversation"),
    (f"{OLD_BASE_URL}/api/verify-payment",   f"{NEW_BASE_URL}/api/verify-payment"),
    (f"{OLD_BASE_URL}/api/log-pay-test",      f"{NEW_BASE_URL}/api/log-pay-test"),
    # Catch-all for any other endpoints on the old base
    (OLD_BASE_URL, NEW_BASE_URL),
]

# ============================================================
# Helpers
# ============================================================

def get_auth_header():
    """Return Basic Auth header for WordPress REST API."""
    import base64
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def fetch_page(page_id: int) -> dict:
    """Fetch a WordPress page by ID."""
    # context=edit is required for _elementor_data to appear in meta
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/pages/{page_id}?context=edit"
    headers = get_auth_header()
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def count_occurrences(data: dict, old_url: str) -> int:
    """Count how many times old_url appears in the page data."""
    page_str = json.dumps(data)
    return page_str.count(old_url)


def replace_in_elementor_data(elementor_data_str: str) -> tuple[str, int]:
    """
    Replace all old URLs in the _elementor_data string.

    Returns (new_string, replacement_count).
    """
    count = 0
    result = elementor_data_str

    for old_url, new_url in ENDPOINT_REPLACEMENTS:
        occurrences = result.count(old_url)
        if occurrences > 0:
            result = result.replace(old_url, new_url)
            count += occurrences
            print(f"  Replaced {occurrences}x: {old_url} -> {new_url}")

    return result, count


def update_page(page_id: int, description: str, dry_run: bool = True) -> bool:
    """
    Update the Elementor data in a WordPress page.

    Returns True if update was successful (or dry_run).
    """
    print(f"\n{'='*60}")
    print(f"Processing: {description} (ID: {page_id})")
    print(f"{'='*60}")

    # Fetch current page data
    print("Fetching page data...")
    try:
        page_data = fetch_page(page_id)
    except requests.HTTPError as e:
        print(f"ERROR: Failed to fetch page {page_id}: {e}")
        return False

    # Get _elementor_data from meta
    meta = page_data.get("meta", {})
    elementor_data_raw = meta.get("_elementor_data", "")

    if not elementor_data_raw:
        print("WARNING: No _elementor_data found on this page")
        # Check content.raw as fallback
        content_raw = page_data.get("content", {}).get("raw", "")
        if OLD_BASE_URL in content_raw:
            print(f"  Found {content_raw.count(OLD_BASE_URL)}x in content.raw (not Elementor page)")
        print("  Skipping.")
        return False

    print(f"Elementor data size: {len(elementor_data_raw):,} chars")

    # Count current occurrences
    old_count = elementor_data_raw.count(OLD_BASE_URL)
    print(f"Occurrences of old URL: {old_count}")

    if old_count == 0:
        print("No old URLs found. Page may already be updated.")
        return True

    # Validate current Elementor data is valid JSON
    try:
        elementor_parsed = json.loads(elementor_data_raw)
        print(f"Elementor data: valid JSON ({len(elementor_parsed)} top-level elements)")
    except json.JSONDecodeError as e:
        print(f"ERROR: Current _elementor_data is invalid JSON: {e}")
        print("Cannot safely update. Manual intervention required.")
        return False

    # Perform replacements
    print("Performing URL replacements...")
    new_elementor_data, replacements_made = replace_in_elementor_data(elementor_data_raw)

    if replacements_made == 0:
        print("No replacements made.")
        return True

    # Validate new data is still valid JSON
    try:
        json.loads(new_elementor_data)
        print(f"Validation: new _elementor_data is valid JSON. {replacements_made} replacement(s) made.")
    except json.JSONDecodeError as e:
        print(f"ERROR: Replacement produced invalid JSON: {e}")
        print("Aborting update to prevent page breakage.")
        return False

    if dry_run:
        print(f"\nDRY RUN: Would update page {page_id} with {replacements_made} replacement(s).")
        print("Run with --execute to apply changes.")
        return True

    # Apply update via WordPress REST API
    print(f"\nApplying update to page {page_id}...")
    update_url = f"{WORDPRESS_URL}/wp-json/wp/v2/pages/{page_id}"
    headers = get_auth_header()
    headers["Content-Type"] = "application/json"

    payload = {
        "meta": {
            "_elementor_data": new_elementor_data
        }
    }

    try:
        response = requests.post(
            update_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        print(f"SUCCESS: Page {page_id} updated.")
    except requests.HTTPError as e:
        print(f"ERROR: REST API update failed: {e}")
        print(f"Response: {e.response.text[:500] if e.response else 'no response'}")
        return False

    # Clear Elementor cache for this page
    print("Clearing Elementor cache...")
    try:
        cache_url = f"{WORDPRESS_URL}/wp-json/elementor/v1/cache"
        cache_response = requests.delete(cache_url, headers=get_auth_header(), timeout=30)
        if cache_response.status_code in (200, 204):
            print("Elementor cache cleared.")
        else:
            print(f"Cache clear returned: {cache_response.status_code} (may be OK)")
    except Exception as e:
        print(f"Cache clear warning (non-critical): {e}")

    return True


def verify_endpoint(new_base: str = NEW_BASE_URL) -> bool:
    """Verify the new API endpoint is accessible and returns trusted cert."""
    health_url = f"{new_base}/api/health"
    print(f"\nVerifying new endpoint: {health_url}")
    try:
        response = requests.get(health_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Endpoint healthy - {data}")
            return True
        else:
            print(f"WARNING: Endpoint returned {response.status_code}")
            return False
    except requests.SSLError as e:
        print(f"SSL ERROR: {e}")
        print("The new endpoint still has SSL issues. Check Cloudflare tunnel or Let's Encrypt setup.")
        return False
    except requests.ConnectionError as e:
        print(f"CONNECTION ERROR: {e}")
        print("Cannot reach new endpoint. Check DNS propagation and tunnel status.")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


# ============================================================
# Main
# ============================================================

def main():
    dry_run = "--execute" not in sys.argv

    print("PureBrain API Endpoint URL Updater")
    print("=" * 60)
    print(f"Old URL: {OLD_BASE_URL}")
    print(f"New URL: {NEW_BASE_URL}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()

    if not WP_APP_PASSWORD:
        print("ERROR: PUREBRAIN_WP_APP_PASSWORD not set in .env")
        sys.exit(1)

    # Check new endpoint is working before updating pages
    endpoint_ok = verify_endpoint()
    if not endpoint_ok:
        if dry_run:
            print("\nWARNING: New endpoint not reachable, but continuing in dry-run mode.")
            print("In execute mode, we would abort to prevent broken pages.")
        else:
            print("\nABORTING: Cannot update pages when new endpoint is not reachable.")
            print("Fix the Cloudflare tunnel or Let's Encrypt cert first.")
            sys.exit(1)

    # Update each target page
    results = {}
    for page_info in TARGET_PAGES:
        success = update_page(
            page_id=page_info["id"],
            description=page_info["description"],
            dry_run=dry_run,
        )
        results[page_info["id"]] = success

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for page_info in TARGET_PAGES:
        page_id = page_info["id"]
        status = "OK" if results.get(page_id) else "FAILED"
        print(f"  Page {page_id} ({page_info['description']}): {status}")

    if dry_run:
        print("\nThis was a DRY RUN. No changes were made.")
        print("To apply changes, run:")
        print("  python3 tools/security/update-endpoint-urls.py --execute")
    else:
        all_ok = all(results.values())
        if all_ok:
            print("\nAll pages updated successfully!")
            print(f"\nVerify in Chrome incognito:")
            print(f"  1. Open https://purebrain.ai/pay-test-sandbox/")
            print(f"  2. Open DevTools -> Console")
            print(f"  3. Confirm no ERR_CERT_AUTHORITY_INVALID errors")
            print(f"  4. Address bar should show green padlock, no 'Not Secure' warning")
        else:
            print("\nSome pages failed to update. Check errors above.")
            sys.exit(1)


if __name__ == "__main__":
    main()
