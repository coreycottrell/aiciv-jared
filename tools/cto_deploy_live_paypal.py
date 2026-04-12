#!/usr/bin/env python3
"""
CTO: Clone sandbox-3 to pay-test-2 with LIVE PayPal client ID.
Run: python3 /home/jared/projects/AI-CIV/aether/tools/cto_deploy_live_paypal.py

Source: purebrain-site/public/pay-test-sandbox-3/index.html
Dest:   WordPress page 689 (pay-test-2) + local pay-test-2/index.html
Change: AYTFob05... → AWgWNlBQ... (sandbox → live PayPal client ID)
"""

import requests
import sys
from requests.auth import HTTPBasicAuth

# === Auth ===
WP_USER        = "Aether"
WP_APP_PASSWORD = "41w3 xWWZ 11em UXgj hjAF sx2T"
BASE_URL       = "https://purebrain.ai/wp-json/wp/v2"

# === PayPal IDs ===
SANDBOX_CLIENT_ID = "AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_"
LIVE_CLIENT_ID    = "AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI"

# === Files ===
SOURCE_FILE = "/home/jared/projects/AI-CIV/aether/purebrain-site/public/pay-test-sandbox-3/index.html"
DEST_FILE   = "/home/jared/projects/AI-CIV/aether/purebrain-site/public/pay-test-2/index.html"
PAGE_ID     = 689

auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)

def main():
    print("=" * 64)
    print("CTO: Deploying pay-test-2 with LIVE PayPal")
    print("=" * 64)

    # Step 1: Read source
    print(f"\n[1] Reading source file...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"    File size: {len(content):,} chars")

    # Step 2: Verify sandbox ID present
    sandbox_count = content.count(SANDBOX_CLIENT_ID)
    print(f"\n[2] Pre-replacement check:")
    print(f"    Sandbox client ID occurrences: {sandbox_count}")
    print(f"    Live client ID occurrences (before): {content.count(LIVE_CLIENT_ID)}")
    print(f"    sandbox.paypal.com occurrences: {content.count('sandbox.paypal.com')}")

    if sandbox_count == 0:
        print("    [FATAL] Sandbox client ID not found in source file. Aborting.")
        sys.exit(1)

    # Step 3: Make replacements
    print(f"\n[3] Making replacements...")
    updated = content.replace(SANDBOX_CLIENT_ID, LIVE_CLIENT_ID)
    updated = updated.replace('sandbox.paypal.com', 'www.paypal.com')
    updated = updated.replace('api-m.sandbox.paypal.com', 'api-m.paypal.com')

    # Verify
    sandbox_after = updated.count(SANDBOX_CLIENT_ID)
    live_after    = updated.count(LIVE_CLIENT_ID)
    print(f"    Sandbox client ID remaining: {sandbox_after} (expected 0)")
    print(f"    Live client ID present: {live_after} (expected 1)")

    if sandbox_after > 0:
        print("    [FATAL] Sandbox ID still present after replacement!")
        sys.exit(1)
    if live_after == 0:
        print("    [FATAL] Live ID not injected properly!")
        sys.exit(1)
    print("    [OK] Replacement verified")

    # Step 4: Save local copy
    print(f"\n[4] Saving updated local file: {DEST_FILE}")
    with open(DEST_FILE, 'w', encoding='utf-8') as f:
        f.write(updated)
    print(f"    [OK] Saved {len(updated):,} chars")

    # Step 5: Deploy to WordPress
    print(f"\n[5] Deploying to WordPress page {PAGE_ID}...")
    payload = {
        'content':  updated,
        'template': 'elementor_canvas',
        'status':   'publish',
    }
    r = requests.post(
        f"{BASE_URL}/pages/{PAGE_ID}",
        auth=auth,
        json=payload,
        timeout=180
    )
    print(f"    HTTP {r.status_code}")
    if r.status_code not in (200, 201):
        print(f"    [ERROR] {r.text[:600]}")
        sys.exit(1)
    resp = r.json()
    print(f"    Page ID:  {resp.get('id')}")
    print(f"    Status:   {resp.get('status')}")
    print(f"    Template: {resp.get('template')}")
    print(f"    Link:     {resp.get('link')}")
    print("    [OK] Deployed successfully")

    # Step 6: Clear Elementor cache
    print(f"\n[6] Clearing Elementor cache...")
    r = requests.delete(
        "https://purebrain.ai/wp-json/elementor/v1/cache",
        auth=auth,
        timeout=30
    )
    print(f"    HTTP {r.status_code} — {r.text[:200]}")

    # Step 7: Verify
    print(f"\n[7] Verification — re-fetching page {PAGE_ID}...")
    r = requests.get(
        f"{BASE_URL}/pages/{PAGE_ID}?context=edit",
        auth=auth,
        timeout=60
    )
    if r.status_code == 200:
        v = r.json()
        v_content   = v.get('content', {}).get('raw', '')
        v_meta      = v.get('meta') or {}
        v_elementor = v_meta.get('_elementor_data') or ''
        combined    = v_content + v_elementor

        live_ok       = LIVE_CLIENT_ID in combined
        sandbox_gone  = SANDBOX_CLIENT_ID not in combined
        template_ok   = v.get('template') == 'elementor_canvas'

        print(f"    LIVE client ID present:      {'YES [PASS]' if live_ok else 'NO  [FAIL]'}")
        print(f"    Sandbox client ID gone:      {'YES [PASS]' if sandbox_gone else 'NO  [FAIL]'}")
        print(f"    Template = elementor_canvas: {'YES [PASS]' if template_ok else 'NO  [FAIL]'}")
        print(f"    Page URL: {v.get('link')}")

        if live_ok and sandbox_gone and template_ok:
            print(f"\n    ALL CHECKS PASSED")
        else:
            print(f"\n    SOME CHECKS FAILED — review manually")
    else:
        print(f"    Verification GET returned HTTP {r.status_code}")

    print(f"\n{'='*64}")
    print("DEPLOYMENT COMPLETE")
    print(f"  https://purebrain.ai/pay-test-2/")
    print(f"{'='*64}")

if __name__ == '__main__':
    main()
