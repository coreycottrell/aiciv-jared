#!/usr/bin/env python3
"""
CTO: Clone sandbox-3 (page 1013) to pay-test-2 (page 689) with LIVE PayPal
"""

import requests
import json
import sys
import re
from requests.auth import HTTPBasicAuth

# === CREDENTIALS ===
WP_USER = "Aether"
WP_APP_PASSWORD = "41w3 xWWZ 11em UXgj hjAF sx2T"
BASE_URL = "https://purebrain.ai/wp-json/wp/v2"

# === PayPal IDs ===
SANDBOX_CLIENT_ID = "AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_"
LIVE_CLIENT_ID = "AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI"

# === Page IDs ===
SANDBOX_3_ID = 1013  # Source: pay-test-sandbox-3
PAY_TEST_2_ID = 689   # Destination: pay-test-2

auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)

def get_page(page_id):
    print(f"\n[STEP] Fetching page {page_id}...")
    url = f"{BASE_URL}/pages/{page_id}?context=edit"
    resp = requests.get(url, auth=auth, timeout=30)
    if resp.status_code != 200:
        print(f"[ERROR] GET page {page_id} returned {resp.status_code}: {resp.text[:500]}")
        sys.exit(1)
    data = resp.json()
    print(f"[OK] Got page {page_id}: '{data.get('title', {}).get('raw', 'unknown')}'")
    return data

def extract_html_from_elementor_data(page_data):
    """Extract the HTML content from _elementor_data or post_content."""
    meta = page_data.get('meta', {})
    elementor_data = meta.get('_elementor_data', '')
    post_content_raw = page_data.get('content', {}).get('raw', '')

    print(f"[INFO] _elementor_data length: {len(elementor_data)}")
    print(f"[INFO] post_content raw length: {len(post_content_raw)}")

    return elementor_data, post_content_raw

def replace_paypal_ids(content, sandbox_id, live_id):
    """Replace sandbox PayPal client ID with live client ID."""
    count = content.count(sandbox_id)
    if count == 0:
        print(f"[WARN] Sandbox PayPal ID not found in content. Searching for partial matches...")
        # Check for 'AYTFob05' prefix
        if 'AYTFob05' in content:
            print(f"[INFO] Found 'AYTFob05' prefix in content - sandbox ID present but possibly truncated")
        else:
            print(f"[INFO] No sandbox PayPal ID references found at all")
    else:
        print(f"[OK] Found {count} occurrence(s) of sandbox PayPal client ID - replacing with live ID")

    updated = content.replace(sandbox_id, live_id)
    return updated

def replace_sandbox_paypal_urls(content):
    """Replace sandbox.paypal.com with www.paypal.com in PayPal SDK script URLs."""
    # Common sandbox URL patterns in PayPal SDK
    replacements = [
        ('sandbox.paypal.com', 'www.paypal.com'),
        ('api-m.sandbox.paypal.com', 'api-m.paypal.com'),
    ]
    for old, new in replacements:
        count = content.count(old)
        if count > 0:
            print(f"[OK] Replacing {count} occurrence(s) of '{old}' → '{new}'")
            content = content.replace(old, new)
        else:
            print(f"[INFO] No occurrences of '{old}' found")

    # Also check for &intent=sandbox or similar sandbox params in PayPal script URLs
    # e.g., https://www.paypal.com/sdk/js?client-id=XXX&intent=authorize&currency=USD
    # The URL-encoded client-id in script tags
    if '&debug=true' in content:
        print(f"[INFO] Found debug=true in PayPal SDK URL — leaving as-is for now")

    return content

def check_environment_mode(content):
    """Check if there's an explicit 'sandbox' environment setting in the JS."""
    if '"sandbox"' in content or "'sandbox'" in content:
        # Find context
        idx = content.find('"sandbox"')
        if idx == -1:
            idx = content.find("'sandbox'")
        context_start = max(0, idx - 200)
        context_end = min(len(content), idx + 200)
        snippet = content[context_start:context_end]
        print(f"\n[WARN] Found 'sandbox' string in content. Context:")
        print(f"  ...{snippet}...")
        print(f"[ACTION] Review if this needs to be changed to 'production' or 'live'")

    # Check PayPal SDK script tag for environment parameter
    paypal_sdk_matches = re.findall(r'https://www\.paypal\.com/sdk/js[^"\'>\s]*', content)
    paypal_sandbox_sdk = re.findall(r'https://sandbox\.paypal\.com/sdk/js[^"\'>\s]*', content)

    if paypal_sdk_matches:
        print(f"\n[INFO] PayPal LIVE SDK URLs found:")
        for m in paypal_sdk_matches[:5]:
            print(f"  {m}")
    if paypal_sandbox_sdk:
        print(f"\n[WARN] PayPal SANDBOX SDK URLs found (will be replaced):")
        for m in paypal_sandbox_sdk[:5]:
            print(f"  {m}")

def update_page(page_id, elementor_data, post_content_raw, template='elementor_canvas'):
    """Deploy updated content to WordPress page."""
    print(f"\n[STEP] Updating page {page_id}...")
    url = f"{BASE_URL}/pages/{page_id}"

    payload = {
        'template': template,
        'status': 'publish',
    }

    if elementor_data:
        payload['meta'] = {'_elementor_data': elementor_data}

    if post_content_raw:
        payload['content'] = post_content_raw

    resp = requests.post(url, auth=auth, json=payload, timeout=60)
    if resp.status_code not in (200, 201):
        print(f"[ERROR] POST page {page_id} returned {resp.status_code}: {resp.text[:500]}")
        return False

    data = resp.json()
    print(f"[OK] Page {page_id} updated successfully. Status: {data.get('status')}, Template: {data.get('template')}")
    return True

def clear_elementor_cache():
    """Clear Elementor cache."""
    print(f"\n[STEP] Clearing Elementor cache...")
    url = "https://purebrain.ai/wp-json/elementor/v1/cache"
    resp = requests.delete(url, auth=auth, timeout=30)
    print(f"[INFO] Cache clear response: {resp.status_code} — {resp.text[:200]}")
    return resp.status_code in (200, 204)

def verify_live_page(page_id):
    """Re-fetch the page to confirm our changes took."""
    print(f"\n[STEP] Verifying deployment (re-fetching page {page_id})...")
    url = f"{BASE_URL}/pages/{page_id}?context=edit"
    resp = requests.get(url, auth=auth, timeout=30)
    if resp.status_code != 200:
        print(f"[ERROR] Verification GET failed: {resp.status_code}")
        return False
    data = resp.json()
    meta = data.get('meta', {})
    elementor_data = meta.get('_elementor_data', '')
    post_content = data.get('content', {}).get('raw', '')

    combined = elementor_data + post_content

    if LIVE_CLIENT_ID in combined:
        print(f"[VERIFIED] LIVE PayPal client ID confirmed present in page {page_id}")
    else:
        print(f"[WARN] LIVE PayPal client ID NOT found in page {page_id} after update")

    if SANDBOX_CLIENT_ID in combined:
        print(f"[FAIL] Sandbox PayPal client ID still present — replacement may have failed")
    else:
        print(f"[VERIFIED] Sandbox PayPal client ID NOT present — clean replacement confirmed")

    if 'sandbox.paypal.com' in combined:
        print(f"[FAIL] sandbox.paypal.com still present in content")
    else:
        print(f"[VERIFIED] No sandbox.paypal.com URLs found")

    return True

def main():
    print("=" * 60)
    print("CTO: Cloning sandbox-3 → pay-test-2 with LIVE PayPal")
    print("=" * 60)

    # Step 1: Get sandbox-3 (source)
    sandbox3_page = get_page(SANDBOX_3_ID)
    elementor_data, post_content = extract_html_from_elementor_data(sandbox3_page)

    # Determine which content field to work with
    working_content = elementor_data if elementor_data else post_content
    content_type = '_elementor_data' if elementor_data else 'post_content'
    print(f"\n[INFO] Working with: {content_type} (length: {len(working_content)})")

    # Step 2: Inspect PayPal references before any changes
    print(f"\n[STEP] Analyzing PayPal references in sandbox-3...")
    check_environment_mode(working_content)

    # Step 3: Replace sandbox PayPal client ID → LIVE
    print(f"\n[STEP] Replacing PayPal client IDs...")
    updated_content = replace_paypal_ids(working_content, SANDBOX_CLIENT_ID, LIVE_CLIENT_ID)

    # Step 4: Replace sandbox PayPal URLs → live
    print(f"\n[STEP] Replacing sandbox PayPal URLs...")
    updated_content = replace_sandbox_paypal_urls(updated_content)

    # Step 5: Also check if current pay-test-2 already has sandbox ID
    print(f"\n[STEP] Checking current pay-test-2 for context...")
    pay_test_2_page = get_page(PAY_TEST_2_ID)
    pt2_elementor, pt2_content = extract_html_from_elementor_data(pay_test_2_page)
    combined_pt2 = pt2_elementor + pt2_content
    if SANDBOX_CLIENT_ID in combined_pt2:
        print(f"[INFO] Current pay-test-2 already has SANDBOX client ID (will be fully replaced)")
    elif LIVE_CLIENT_ID in combined_pt2:
        print(f"[INFO] Current pay-test-2 has LIVE client ID (will be replaced with sandbox-3 clone + live ID)")
    else:
        print(f"[INFO] Current pay-test-2 PayPal ID not detected in initial scan")

    # Step 6: Deploy to pay-test-2
    print(f"\n[STEP] Deploying updated content to pay-test-2 (ID: {PAY_TEST_2_ID})...")

    if content_type == '_elementor_data':
        success = update_page(PAY_TEST_2_ID, updated_content, None)
    else:
        success = update_page(PAY_TEST_2_ID, None, updated_content)

    if not success:
        print("[FATAL] Deployment failed. Aborting.")
        sys.exit(1)

    # Step 7: Clear Elementor cache
    clear_elementor_cache()

    # Step 8: Verify
    verify_live_page(PAY_TEST_2_ID)

    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE")
    print(f"  Source: sandbox-3 (page {SANDBOX_3_ID})")
    print(f"  Destination: pay-test-2 (page {PAY_TEST_2_ID})")
    print(f"  PayPal mode: LIVE ({LIVE_CLIENT_ID[:20]}...)")
    print(f"  URL: https://purebrain.ai/pay-test-2/")
    print("=" * 60)

if __name__ == '__main__':
    main()
