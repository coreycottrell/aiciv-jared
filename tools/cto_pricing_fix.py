#!/usr/bin/env python3
"""
CTO: pay-test-5 (1527) and sandbox-5 (1528) pricing section fix.
Extracts the checkout pricing section from sandbox-3 (1013) and
replaces the homepage pricing section in pay-test-5 and sandbox-5.

Live PayPal:    AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI
Sandbox PayPal: AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_
"""

import os
import sys
import json
import re
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"
WP_USER = "purebrain@puremarketing.ai"
WP_PASS = os.environ.get("PUREBRAIN_WP_APP_PASSWORD", "").strip()

LIVE_CLIENT_ID   = "AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI"
SANDBOX_CLIENT_ID = "AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_"

auth = HTTPBasicAuth(WP_USER, WP_PASS)

def fetch_page(page_id):
    resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", auth=auth, timeout=30)
    if resp.status_code != 200:
        print(f"ERROR fetching page {page_id}: {resp.status_code}")
        print(resp.text[:500])
        return None
    return resp.json()

def save_raw(page_id, raw_content, label):
    path = f"/home/jared/projects/AI-CIV/aether/exports/cto-pricing-fix/page-{page_id}-{label}-raw.html"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(raw_content)
    print(f"  Saved {path} ({len(raw_content)} chars)")
    return path

def update_page(page_id, new_content):
    payload = {"content": new_content}
    resp = requests.post(
        f"{BASE_URL}/{page_id}",
        auth=auth,
        json=payload,
        timeout=60
    )
    if resp.status_code in (200, 201):
        print(f"  Page {page_id} updated successfully.")
        return True
    else:
        print(f"  ERROR updating page {page_id}: {resp.status_code}")
        print(resp.text[:500])
        return False

def clear_elementor_cache():
    resp = requests.delete(
        "https://purebrain.ai/wp-json/elementor/v1/cache",
        auth=auth,
        timeout=30
    )
    print(f"  Cache clear: {resp.status_code}")

def extract_pricing_section_from_sandbox3(html):
    """
    Extract the pricing section from sandbox-3's HTML.
    Looking for <section id="pricing" or the div containing the pricing cards.
    The section is gated behind CSS display:none, revealed via JS .active class.
    """
    # Try to find section with id="pricing"
    # Pattern: <section id="pricing" ...>...</section>
    # Also include everything from the "Bring [NAME] Fully Online" heading

    # First look for the pricing section block
    # sandbox-3 uses: <section id="pricing" class="pricing-section">
    match = re.search(r'(<section[^>]*id=["\']pricing["\'][^>]*>.*?</section>)', html, re.DOTALL)
    if match:
        print("  Found #pricing section via section tag match")
        return match.group(1)

    # Try div approach
    match = re.search(r'(<div[^>]*id=["\']pricing["\'][^>]*>.*?</div>\s*</div>)', html, re.DOTALL)
    if match:
        print("  Found #pricing via div tag match")
        return match.group(1)

    print("  WARNING: Could not find #pricing section via regex. Saving full HTML for manual inspection.")
    return None

def find_pricing_in_html(html, label="page"):
    """Look for pricing-related markers to help locate the section."""
    markers = [
        "Reserve Keen Now",
        "Activate Keen Now",
        "pricing-section",
        'id="pricing"',
        'id=\'pricing\'',
        "Bring [NAME] Fully Online",
        "Bring Fully Online",
        "Claude Max Account",
        "Requirement:",
        "PayPal",
        "paypal",
    ]
    print(f"\n  === {label} content markers ===")
    for marker in markers:
        idx = html.find(marker)
        if idx >= 0:
            print(f"    FOUND '{marker}' at position {idx}")
            # Show 100 chars of context
            ctx = html[max(0,idx-50):idx+100].replace('\n', ' ')
            print(f"      Context: ...{ctx}...")
        else:
            print(f"    NOT FOUND: '{marker}'")


def main():
    if not WP_PASS:
        print("ERROR: PUREBRAIN_WP_APP_PASSWORD not set in environment")
        sys.exit(1)

    print("=== CTO Pricing Fix: Fetching pages ===")

    # Fetch all three pages
    print("\n1. Fetching sandbox-3 (page 1013) - SOURCE of correct pricing...")
    sandbox3 = fetch_page(1013)
    if not sandbox3:
        sys.exit(1)

    print("\n2. Fetching pay-test-5 (page 1527) - NEEDS pricing replaced...")
    paytest5 = fetch_page(1527)
    if not paytest5:
        sys.exit(1)

    print("\n3. Fetching sandbox-5 (page 1528) - NEEDS pricing replaced...")
    sandbox5 = fetch_page(1528)
    if not sandbox5:
        sys.exit(1)

    # Get raw content
    sb3_raw = sandbox3.get("content", {}).get("raw", "")
    pt5_raw = paytest5.get("content", {}).get("raw", "")
    s5_raw = sandbox5.get("content", {}).get("raw", "")

    print(f"\n  sandbox-3 content length: {len(sb3_raw)}")
    print(f"  pay-test-5 content length: {len(pt5_raw)}")
    print(f"  sandbox-5 content length: {len(s5_raw)}")

    # Save originals
    print("\n=== Saving original content ===")
    save_raw(1013, sb3_raw, "sandbox3-original")
    save_raw(1527, pt5_raw, "paytest5-original")
    save_raw(1528, s5_raw, "sandbox5-original")

    # Analyze what we have
    find_pricing_in_html(sb3_raw, "sandbox-3")
    find_pricing_in_html(pt5_raw, "pay-test-5")
    find_pricing_in_html(s5_raw, "sandbox-5")

    print("\n=== Analysis complete. Check exports/cto-pricing-fix/ for raw HTML files. ===")
    print("Next step: Inspect the raw HTML to determine exact extraction approach.")


if __name__ == "__main__":
    main()
