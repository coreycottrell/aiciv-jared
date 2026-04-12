#!/usr/bin/env python3
"""
CTO: Fetch both pages, analyze content, perform replacements, deploy.
This script does everything step by step with full output.
"""

import requests
import json
import sys
import re
from requests.auth import HTTPBasicAuth

WP_USER = "Aether"
WP_APP_PASSWORD = "41w3 xWWZ 11em UXgj hjAF sx2T"
BASE_URL = "https://purebrain.ai/wp-json/wp/v2"

SANDBOX_CLIENT_ID = "AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_"
LIVE_CLIENT_ID = "AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI"

SANDBOX_3_ID = 1013
PAY_TEST_2_ID = 689

auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)

# ---- STEP 1: Fetch sandbox-3 ----
print(f"[1] Fetching page {SANDBOX_3_ID} (sandbox-3)...")
r = requests.get(f"{BASE_URL}/pages/{SANDBOX_3_ID}?context=edit", auth=auth, timeout=60)
print(f"    Status: {r.status_code}")
if r.status_code != 200:
    print(f"    ERROR: {r.text[:300]}")
    sys.exit(1)

sandbox3 = r.json()
print(f"    Title: {sandbox3.get('title', {}).get('raw', 'N/A')}")
print(f"    Template: {sandbox3.get('template', 'N/A')}")

s3_meta = sandbox3.get('meta', {})
s3_elementor = s3_meta.get('_elementor_data', '')
s3_content_raw = sandbox3.get('content', {}).get('raw', '')

print(f"    _elementor_data length: {len(s3_elementor)}")
print(f"    content.raw length: {len(s3_content_raw)}")

# Save sandbox-3 full content for inspection
with open('/tmp/sandbox3_elementor.txt', 'w') as f:
    f.write(s3_elementor)
with open('/tmp/sandbox3_content.txt', 'w') as f:
    f.write(s3_content_raw)
print(f"    Saved to /tmp/sandbox3_elementor.txt and /tmp/sandbox3_content.txt")

# ---- STEP 2: Fetch pay-test-2 ----
print(f"\n[2] Fetching page {PAY_TEST_2_ID} (pay-test-2)...")
r = requests.get(f"{BASE_URL}/pages/{PAY_TEST_2_ID}?context=edit", auth=auth, timeout=60)
print(f"    Status: {r.status_code}")
if r.status_code != 200:
    print(f"    ERROR: {r.text[:300]}")
    sys.exit(1)

paytest2 = r.json()
print(f"    Title: {paytest2.get('title', {}).get('raw', 'N/A')}")
print(f"    Template: {paytest2.get('template', 'N/A')}")

pt2_meta = paytest2.get('meta', {})
pt2_elementor = pt2_meta.get('_elementor_data', '')
pt2_content_raw = paytest2.get('content', {}).get('raw', '')

print(f"    _elementor_data length: {len(pt2_elementor)}")
print(f"    content.raw length: {len(pt2_content_raw)}")

with open('/tmp/paytest2_elementor.txt', 'w') as f:
    f.write(pt2_elementor)
with open('/tmp/paytest2_content.txt', 'w') as f:
    f.write(pt2_content_raw)
print(f"    Saved to /tmp/paytest2_elementor.txt and /tmp/paytest2_content.txt")

# ---- STEP 3: Analyze PayPal in sandbox-3 ----
print(f"\n[3] PayPal analysis in sandbox-3...")

# Check all possible PayPal references
all_s3 = s3_elementor + s3_content_raw

sandbox_count = all_s3.count(SANDBOX_CLIENT_ID)
live_count = all_s3.count(LIVE_CLIENT_ID)
sandbox_url_count = all_s3.count('sandbox.paypal.com')
paypal_sdk_count = all_s3.count('paypal.com/sdk/js')
paypal_keyword_count = all_s3.lower().count('paypal')

print(f"    Sandbox client ID occurrences: {sandbox_count}")
print(f"    Live client ID occurrences: {live_count}")
print(f"    sandbox.paypal.com occurrences: {sandbox_url_count}")
print(f"    paypal.com/sdk/js occurrences: {paypal_sdk_count}")
print(f"    'paypal' keyword occurrences: {paypal_keyword_count}")

# Find PayPal SDK script tag
sdk_pattern = r'https?://[^"\'>\s]*paypal[^"\'>\s]*sdk/js[^"\'>\s]*'
sdk_matches = re.findall(sdk_pattern, all_s3, re.IGNORECASE)
if sdk_matches:
    print(f"    PayPal SDK URLs found:")
    for m in sdk_matches[:10]:
        print(f"      {m}")

# Find client-id= references
client_id_pattern = r'client-id=([A-Za-z0-9_\-]+)'
client_ids = re.findall(client_id_pattern, all_s3)
if client_ids:
    print(f"    client-id= references: {client_ids}")

# Find PAYPAL_CLIENT_ID variable assignments
var_pattern = r'PAYPAL_CLIENT_ID\s*=\s*[\'"]([A-Za-z0-9_\-]+)[\'"]'
var_matches = re.findall(var_pattern, all_s3)
if var_matches:
    print(f"    PAYPAL_CLIENT_ID variable assignments: {var_matches}")

# ---- STEP 4: Perform replacements ----
print(f"\n[4] Performing replacements on sandbox-3 content...")

# Work with the content that has actual HTML
if len(s3_elementor) > len(s3_content_raw):
    working = s3_elementor
    content_type = 'elementor'
    print(f"    Using _elementor_data as source")
else:
    working = s3_content_raw
    content_type = 'content'
    print(f"    Using post content as source")

# Replace sandbox client ID with live
before = working.count(SANDBOX_CLIENT_ID)
working = working.replace(SANDBOX_CLIENT_ID, LIVE_CLIENT_ID)
after_sandbox = working.count(SANDBOX_CLIENT_ID)
print(f"    Sandbox client ID: {before} → {after_sandbox} remaining")

# Replace sandbox.paypal.com URLs
before_url = working.count('sandbox.paypal.com')
working = working.replace('sandbox.paypal.com', 'www.paypal.com')
working = working.replace('api-m.sandbox.paypal.com', 'api-m.paypal.com')
after_url = working.count('sandbox.paypal.com')
print(f"    sandbox.paypal.com: {before_url} → {after_url} remaining")

# Confirm live ID is now present
live_present = working.count(LIVE_CLIENT_ID)
print(f"    Live client ID present: {live_present} occurrence(s)")

# ---- STEP 5: Deploy to pay-test-2 ----
print(f"\n[5] Deploying to pay-test-2 (page {PAY_TEST_2_ID})...")

if content_type == 'elementor':
    payload = {
        'template': 'elementor_canvas',
        'status': 'publish',
        'meta': {'_elementor_data': working}
    }
else:
    payload = {
        'template': 'elementor_canvas',
        'status': 'publish',
        'content': working
    }

r = requests.post(
    f"{BASE_URL}/pages/{PAY_TEST_2_ID}",
    auth=auth,
    json=payload,
    timeout=120
)
print(f"    Status: {r.status_code}")
if r.status_code not in (200, 201):
    print(f"    ERROR: {r.text[:500]}")
    sys.exit(1)

resp_data = r.json()
print(f"    Updated page ID: {resp_data.get('id')}")
print(f"    Status: {resp_data.get('status')}")
print(f"    Template: {resp_data.get('template')}")
print(f"    Link: {resp_data.get('link')}")

# ---- STEP 6: Clear Elementor cache ----
print(f"\n[6] Clearing Elementor cache...")
r = requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache", auth=auth, timeout=30)
print(f"    Status: {r.status_code} — {r.text[:200]}")

# ---- STEP 7: Verify ----
print(f"\n[7] Verification — re-fetching page {PAY_TEST_2_ID}...")
r = requests.get(f"{BASE_URL}/pages/{PAY_TEST_2_ID}?context=edit", auth=auth, timeout=60)
if r.status_code == 200:
    verify_data = r.json()
    v_meta = verify_data.get('meta', {})
    v_elementor = v_meta.get('_elementor_data', '')
    v_content = verify_data.get('content', {}).get('raw', '')
    combined = v_elementor + v_content

    live_ok = LIVE_CLIENT_ID in combined
    sandbox_gone = SANDBOX_CLIENT_ID not in combined
    sandbox_url_gone = 'sandbox.paypal.com' not in combined

    print(f"    LIVE client ID present: {'YES ✓' if live_ok else 'NO ✗'}")
    print(f"    Sandbox client ID gone: {'YES ✓' if sandbox_gone else 'NO ✗'}")
    print(f"    sandbox.paypal.com gone: {'YES ✓' if sandbox_url_gone else 'NO ✗'}")
    print(f"    Template: {verify_data.get('template')}")

    if live_ok and sandbox_gone:
        print(f"\n[SUCCESS] pay-test-2 is LIVE with production PayPal!")
        print(f"    URL: https://purebrain.ai/pay-test-2/")
    else:
        print(f"\n[PARTIAL] Deployment done but verify manually at https://purebrain.ai/pay-test-2/")

print("\nDone.")
