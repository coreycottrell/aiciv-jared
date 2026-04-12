#!/usr/bin/env python3
"""
CTO URGENT FIX: pay-test-5 (1527) and sandbox-5 (1528) pricing section fix.

Strategy:
1. Fetch sandbox-3 (1013) — source of CORRECT checkout pricing section
2. Fetch pay-test-5 (1527) and sandbox-5 (1528) — targets to fix
3. Find the pricing section in sandbox-3 (section#pricing with "Activate Keen Now" buttons)
4. Find the pricing section in pay-test-5/sandbox-5 (has "Reserve Keen Now" buttons)
5. Replace the wrong pricing section with the correct one
6. For pay-test-5: ensure LIVE PayPal client ID
7. For sandbox-5: ensure SANDBOX PayPal client ID
8. Deploy both pages and clear Elementor cache

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
WP_PASS = "41w3 xWWZ 11em UXgj hjAF sx2T"

LIVE_CLIENT_ID    = "AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI"
SANDBOX_CLIENT_ID = "AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_"

EXPORT_DIR = "/home/jared/projects/AI-CIV/aether/exports/cto-pricing-fix"

auth = HTTPBasicAuth(WP_USER, WP_PASS)

def fetch_page(page_id):
    resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", auth=auth, timeout=30)
    if resp.status_code != 200:
        print(f"  ERROR fetching page {page_id}: HTTP {resp.status_code}")
        print(f"  Response: {resp.text[:300]}")
        return None
    return resp.json()

def save_file(filename, content):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    path = f"{EXPORT_DIR}/{filename}"
    with open(path, "w") as f:
        f.write(content)
    print(f"  Saved: {path} ({len(content)} chars)")
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
        print(f"  Page {page_id} updated OK (HTTP {resp.status_code})")
        return True
    else:
        print(f"  ERROR updating page {page_id}: HTTP {resp.status_code}")
        print(f"  {resp.text[:400]}")
        return False

def clear_elementor_cache():
    resp = requests.delete(
        "https://purebrain.ai/wp-json/elementor/v1/cache",
        auth=auth,
        timeout=30
    )
    print(f"  Elementor cache clear: HTTP {resp.status_code}")

def show_markers(html, label):
    """Print positions of key strings in the HTML to help locate sections."""
    markers = [
        "Reserve Keen Now",
        "Activate Keen Now",
        'id="pricing"',
        "pricing-section",
        "Claude Max Account",
        "Requirement:",
        "paypal.com/sdk",
        LIVE_CLIENT_ID[:20],
        SANDBOX_CLIENT_ID[:20],
        "Bring Fully Online",
        "Bring [NAME] Fully Online",
        "<!-- wp:html -->",
    ]
    print(f"\n  Markers in {label} ({len(html)} chars total):")
    for marker in markers:
        idx = html.find(marker)
        if idx >= 0:
            ctx = html[max(0, idx-40):idx+80].replace('\n', ' ')
            print(f"    [pos {idx:6d}] FOUND '{marker}': ...{ctx}...")
        else:
            print(f"    [      -] NOT FOUND: '{marker}'")


def extract_pricing_section(html, source_label="source"):
    """
    Extract the complete pricing section from sandbox-3 HTML.

    The section in sandbox-3 is:
    <section id="pricing" class="pricing-section ...">
        ...Activate Keen Now buttons...
        ...Claude Max Account section...
    </section>

    We need to grab this whole section.
    """
    # Try: <section id="pricing" ...>...</section>
    # Use a balanced approach - find opening tag, then walk to matching </section>

    # Find all matches for the opening tag pattern
    pattern = r'<section[^>]*id=["\']pricing["\'][^>]*>'
    match = re.search(pattern, html)
    if not match:
        # Also try with class first
        pattern = r'<section[^>]*class=["\'][^"\']*pricing[^"\']*["\'][^>]*id=["\']pricing["\'][^>]*>'
        match = re.search(pattern, html)

    if not match:
        print(f"  Could not find <section id='pricing'> in {source_label}")
        return None

    start = match.start()
    print(f"  Found pricing section opening tag at position {start}")

    # Now find the matching closing </section>
    # Count nested <section> tags
    depth = 0
    pos = start
    while pos < len(html):
        # Find next <section or </section
        next_open = html.find('<section', pos)
        next_close = html.find('</section', pos)

        if next_close == -1:
            print(f"  ERROR: Could not find closing </section> for pricing section")
            return None

        if next_open != -1 and next_open < next_close:
            # Another <section opens before the next close
            depth += 1
            pos = next_open + 1
        else:
            # A close comes first
            depth -= 1
            if depth == 0:
                # This is our closing tag
                end = next_close + len('</section>')
                section = html[start:end]
                print(f"  Extracted pricing section: {len(section)} chars (pos {start} to {end})")
                return section
            pos = next_close + 1

    print(f"  ERROR: Reached end of HTML without finding matched </section>")
    return None


def find_homepage_pricing_section(html, target_label="target"):
    """
    Find the homepage-style pricing section in pay-test-5/sandbox-5.
    The homepage pricing has "Reserve Keen Now" buttons.

    Two possible structures:
    1. A <section id="pricing"> (same ID, different content)
    2. The pricing HTML blob within the wp:html block

    We need to identify the exact boundaries to replace.
    """

    # Check if there's a section#pricing with Reserve Keen Now
    reserve_idx = html.find("Reserve Keen Now")
    if reserve_idx < 0:
        print(f"  'Reserve Keen Now' not found in {target_label}")
        return None, None

    print(f"  'Reserve Keen Now' found at position {reserve_idx}")

    # Now find the section that contains this button
    # Look backwards from the Reserve Keen Now position for a <section with id="pricing"
    before = html[:reserve_idx]

    # Find last <section before Reserve Keen Now
    section_match = None
    for m in re.finditer(r'<section[^>]*id=["\']pricing["\'][^>]*>', before):
        section_match = m

    if section_match:
        start = section_match.start()
        print(f"  Found enclosing <section id='pricing'> at position {start}")

        # Find its closing tag
        depth = 0
        pos = start
        while pos < len(html):
            next_open = html.find('<section', pos)
            next_close = html.find('</section', pos)

            if next_close == -1:
                print(f"  ERROR: Could not find closing </section>")
                return None, None

            if next_open != -1 and next_open < next_close:
                depth += 1
                pos = next_open + 1
            else:
                depth -= 1
                if depth == 0:
                    end = next_close + len('</section>')
                    old_section = html[start:end]
                    print(f"  Found old pricing section: {len(old_section)} chars (pos {start} to {end})")
                    return start, end
                pos = next_close + 1

    # No section#pricing found. The homepage pricing might be in a different structure.
    # Try looking for the pricing section wrapper by "Bring Fully Online" heading
    bring_idx = html.find("Bring Fully Online")
    if bring_idx < 0:
        bring_idx = html.find("Bring [NAME] Fully Online")
    if bring_idx < 0:
        bring_idx = html.find("Fully Online")

    if bring_idx >= 0:
        print(f"  Found 'Fully Online' at position {bring_idx} — looking for enclosing section")
        before = html[:bring_idx]
        # Find last <section before this position
        for m in re.finditer(r'<section[^>]*>', before):
            section_match = m
        if section_match:
            start = section_match.start()
            # find matching close
            depth = 0
            pos = start
            while pos < len(html):
                next_open = html.find('<section', pos)
                next_close = html.find('</section', pos)
                if next_close == -1:
                    break
                if next_open != -1 and next_open < next_close:
                    depth += 1
                    pos = next_open + 1
                else:
                    depth -= 1
                    if depth == 0:
                        end = next_close + len('</section>')
                        print(f"  Found pricing section by 'Fully Online': pos {start} to {end}")
                        return start, end
                    pos = next_close + 1

    print(f"  Could not determine exact pricing section boundaries in {target_label}")
    return None, None


def replace_paypal_client_id(html, target_client_id):
    """Replace any PayPal client-id in the HTML with the target one."""
    # Both known client IDs
    both_ids = [LIVE_CLIENT_ID, SANDBOX_CLIENT_ID]
    result = html
    for cid in both_ids:
        if cid in result:
            if cid != target_client_id:
                result = result.replace(cid, target_client_id)
                print(f"  Replaced PayPal client ID: ...{cid[:20]}... -> ...{target_client_id[:20]}...")
            else:
                print(f"  PayPal client ID already correct: ...{target_client_id[:20]}...")
    return result


def main():
    print("=" * 60)
    print("CTO URGENT: pricing section fix for pay-test-5 & sandbox-5")
    print("=" * 60)

    # ---- Step 1: Fetch pages ----
    print("\n[1/6] Fetching pages via WordPress API...")

    sandbox3_data = fetch_page(1013)
    if not sandbox3_data:
        print("FATAL: Cannot fetch sandbox-3 (source page). Aborting.")
        sys.exit(1)

    paytest5_data = fetch_page(1527)
    if not paytest5_data:
        print("FATAL: Cannot fetch pay-test-5. Aborting.")
        sys.exit(1)

    sandbox5_data = fetch_page(1528)
    if not sandbox5_data:
        print("FATAL: Cannot fetch sandbox-5. Aborting.")
        sys.exit(1)

    # ---- Step 2: Extract raw content ----
    print("\n[2/6] Extracting raw content...")

    sb3_raw = sandbox3_data.get("content", {}).get("raw", "")
    pt5_raw = paytest5_data.get("content", {}).get("raw", "")
    s5_raw  = sandbox5_data.get("content", {}).get("raw", "")

    print(f"  sandbox-3 (1013): {len(sb3_raw):,} chars")
    print(f"  pay-test-5 (1527): {len(pt5_raw):,} chars")
    print(f"  sandbox-5  (1528): {len(s5_raw):,} chars")

    # Save originals for safety
    save_file("sandbox3-1013-original.html", sb3_raw)
    save_file("paytest5-1527-original.html", pt5_raw)
    save_file("sandbox5-1528-original.html", s5_raw)

    # ---- Step 3: Show markers ----
    print("\n[3/6] Analyzing content structure...")
    show_markers(sb3_raw, "sandbox-3")
    show_markers(pt5_raw, "pay-test-5")
    show_markers(s5_raw, "sandbox-5")

    # ---- Step 4: Extract pricing section from sandbox-3 ----
    print("\n[4/6] Extracting correct pricing section from sandbox-3...")
    sb3_pricing = extract_pricing_section(sb3_raw, "sandbox-3")

    if not sb3_pricing:
        print("\nFATAL: Could not extract pricing section from sandbox-3.")
        print("Check exports/cto-pricing-fix/sandbox3-1013-original.html manually.")
        sys.exit(1)

    save_file("sandbox3-pricing-section-extracted.html", sb3_pricing)
    print(f"  Pricing section extracted: {len(sb3_pricing):,} chars")

    # Verify it has the right buttons
    if "Activate Keen Now" in sb3_pricing:
        print("  CONFIRMED: Contains 'Activate Keen Now' buttons")
    else:
        print("  WARNING: 'Activate Keen Now' NOT found in extracted section!")

    if "Claude Max Account" in sb3_pricing or "Requirement:" in sb3_pricing:
        print("  CONFIRMED: Contains 'Requirement: Claude Max Account' section")
    else:
        print("  WARNING: 'Claude Max Account' NOT found in extracted section!")

    # ---- Step 5: Apply fix to pay-test-5 (LIVE PayPal) ----
    print("\n[5/6] Applying fix to pay-test-5 (page 1527)...")

    pt5_start, pt5_end = find_homepage_pricing_section(pt5_raw, "pay-test-5")

    if pt5_start is None:
        print("  WARNING: Could not auto-locate pricing section boundaries in pay-test-5")
        print("  Attempting fallback: look for the position around 'Reserve Keen Now'")
        # Fallback: just show what's around Reserve Keen Now
        reserve_idx = pt5_raw.find("Reserve Keen Now")
        if reserve_idx >= 0:
            ctx = pt5_raw[max(0, reserve_idx-500):reserve_idx+500]
            save_file("paytest5-reserve-context.html", ctx)
            print(f"  Saved context around 'Reserve Keen Now' for inspection")
        print("  Manual inspection required. Check exports/cto-pricing-fix/")
        pt5_success = False
    else:
        # Replace the old pricing section with sandbox-3's pricing section
        old_pricing = pt5_raw[pt5_start:pt5_end]
        save_file("paytest5-old-pricing-extracted.html", old_pricing)

        # Build new pay-test-5 content: swap in sandbox-3 pricing, keep LIVE PayPal
        pt5_new_pricing = replace_paypal_client_id(sb3_pricing, LIVE_CLIENT_ID)
        pt5_new_raw = pt5_raw[:pt5_start] + pt5_new_pricing + pt5_raw[pt5_end:]

        # Also ensure LIVE PayPal client ID throughout the whole page (PayPal script tag)
        pt5_new_raw = replace_paypal_client_id(pt5_new_raw, LIVE_CLIENT_ID)

        save_file("paytest5-1527-new.html", pt5_new_raw)
        print(f"  New pay-test-5 content: {len(pt5_new_raw):,} chars")

        # Verify
        if "Activate Keen Now" in pt5_new_raw:
            print("  VERIFIED: New content has 'Activate Keen Now'")
        else:
            print("  WARNING: 'Activate Keen Now' not in new content!")

        if "Reserve Keen Now" in pt5_new_raw:
            print("  WARNING: 'Reserve Keen Now' still present in new content!")
        else:
            print("  VERIFIED: 'Reserve Keen Now' removed")

        if LIVE_CLIENT_ID in pt5_new_raw:
            print("  VERIFIED: LIVE PayPal client ID present")
        if SANDBOX_CLIENT_ID in pt5_new_raw:
            print("  WARNING: SANDBOX PayPal client ID still present in pay-test-5!")

        print("  Deploying pay-test-5...")
        pt5_success = update_page(1527, pt5_new_raw)

    # ---- Step 6: Apply fix to sandbox-5 (SANDBOX PayPal) ----
    print("\n[6/6] Applying fix to sandbox-5 (page 1528)...")

    s5_start, s5_end = find_homepage_pricing_section(s5_raw, "sandbox-5")

    if s5_start is None:
        print("  WARNING: Could not auto-locate pricing section boundaries in sandbox-5")
        reserve_idx = s5_raw.find("Reserve Keen Now")
        if reserve_idx >= 0:
            ctx = s5_raw[max(0, reserve_idx-500):reserve_idx+500]
            save_file("sandbox5-reserve-context.html", ctx)
        s5_success = False
    else:
        old_pricing = s5_raw[s5_start:s5_end]
        save_file("sandbox5-old-pricing-extracted.html", old_pricing)

        # Build new sandbox-5 content: swap in sandbox-3 pricing, keep SANDBOX PayPal
        s5_new_pricing = replace_paypal_client_id(sb3_pricing, SANDBOX_CLIENT_ID)
        s5_new_raw = s5_raw[:s5_start] + s5_new_pricing + s5_raw[s5_end:]

        # Also ensure SANDBOX PayPal client ID throughout
        s5_new_raw = replace_paypal_client_id(s5_new_raw, SANDBOX_CLIENT_ID)

        save_file("sandbox5-1528-new.html", s5_new_raw)
        print(f"  New sandbox-5 content: {len(s5_new_raw):,} chars")

        if "Activate Keen Now" in s5_new_raw:
            print("  VERIFIED: New content has 'Activate Keen Now'")
        else:
            print("  WARNING: 'Activate Keen Now' not in new content!")

        if "Reserve Keen Now" in s5_new_raw:
            print("  WARNING: 'Reserve Keen Now' still present in new content!")
        else:
            print("  VERIFIED: 'Reserve Keen Now' removed")

        if SANDBOX_CLIENT_ID in s5_new_raw:
            print("  VERIFIED: SANDBOX PayPal client ID present")
        if LIVE_CLIENT_ID in s5_new_raw:
            print("  WARNING: LIVE PayPal client ID still present in sandbox-5!")

        print("  Deploying sandbox-5...")
        s5_success = update_page(1528, s5_new_raw)

    # ---- Clear cache ----
    print("\n[+] Clearing Elementor cache...")
    clear_elementor_cache()

    # ---- Summary ----
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  pay-test-5  (1527): {'SUCCESS' if pt5_success else 'NEEDS MANUAL INTERVENTION'}")
    print(f"  sandbox-5   (1528): {'SUCCESS' if s5_success else 'NEEDS MANUAL INTERVENTION'}")
    print(f"  Files saved in: {EXPORT_DIR}")
    print("\nQA CHECKLIST:")
    print("  1. pay-test-5: https://purebrain.ai/pay-test-5/")
    print("     - Buttons say 'Activate Keen Now' (NOT 'Reserve Keen Now')")
    print("     - 'Requirement: Claude Max Account' section visible")
    print("     - PayPal modal opens on button click")
    print("     - LIVE PayPal client ID in use")
    print("  2. sandbox-5: https://purebrain.ai/sandbox-5/ (or /pay-test-sandbox-5/)")
    print("     - Same as above but SANDBOX PayPal client ID")
    print("  3. Hero, video, testimonials unchanged on both pages")


if __name__ == "__main__":
    main()
