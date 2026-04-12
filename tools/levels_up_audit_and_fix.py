#!/usr/bin/env python3
"""
Audit all 4 pricing pages for 'How This Levels You Up' links.
Add the links where missing.

Pages:
1. partnered/ (partnered pricing page)
2. unified/ (unified pricing page)
3. pay-test-2
4. pay-test-sandbox-3 (ID 1232)
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import base64
import re
import sys

WP_URL = "https://purebrain.ai/wp-json/wp/v2"
WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"

credentials = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()

def wp_get(endpoint, timeout=30):
    url = f"{WP_URL}{endpoint}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {credentials}"
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {e.read().decode()[:200]}")
        raise

def wp_post(endpoint, data_dict, method="POST"):
    url = f"{WP_URL}{endpoint}"
    data = json.dumps(data_dict).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f"  HTTP Error {e.code}: {body}")
        raise

def clear_elementor_cache():
    """Clear Elementor cache after updates."""
    url = f"{WP_URL.replace('/wp/v2', '')}/elementor/v1/cache"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {credentials}"
    }, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"  Cache clear: {resp.status} {resp.reason}")
    except urllib.error.HTTPError as e:
        # 204 No Content or 200 are both fine
        if e.code in [204, 200]:
            print(f"  Cache cleared (HTTP {e.code})")
        else:
            print(f"  Cache clear HTTP {e.code}: {e.read().decode()[:100]}")
    except Exception as e:
        print(f"  Cache clear error: {e}")

def find_page_by_slug(slug):
    results = wp_get(f"/pages?slug={urllib.parse.quote(slug)}&_fields=id,slug,title,link,status")
    if results:
        return results[0]
    return None

def get_page_full(page_id):
    return wp_get(f"/pages/{page_id}?context=edit")

def check_for_link(content_str):
    """Check if the 'How This Levels You Up' link exists."""
    phrases = [
        "How This Levels You Up",
        "levels-you-up",
        "how-this-levels",
    ]
    for phrase in phrases:
        if phrase.lower() in (content_str or '').lower():
            return True
    return False

# ============================================================
# LINK INJECTION HELPERS
# ============================================================

def make_levels_up_link(tier_slug, tier_name):
    """
    Generate the HTML for 'How This Levels You Up →' link.
    tier_slug: 'partnered' or 'unified'
    """
    href = f"https://purebrain.ai/{tier_slug}-how-this-levels-you-up/"
    return (
        f'<div class="levels-up-link-wrap" style="text-align:center;margin-top:12px;">'
        f'<a href="{href}" '
        f'style="color:#00bcd4;font-size:0.9rem;text-decoration:none;'
        f'font-family:\'Inter\',sans-serif;letter-spacing:0.02em;'
        f'border-bottom:1px solid rgba(0,188,212,0.3);padding-bottom:2px;">'
        f'How This Levels You Up &#8594;</a>'
        f'</div>'
    )

def inject_link_after_button(html_content, button_patterns, link_html):
    """
    Find CTA button(s) and inject the levels-up link after each one.
    Returns (modified_html, count_injected).
    """
    count = 0
    result = html_content

    for pattern in button_patterns:
        # Find all occurrences of the button
        matches = list(re.finditer(pattern, result, re.IGNORECASE | re.DOTALL))
        if matches:
            # Process in reverse to preserve positions
            for match in reversed(matches):
                insert_pos = match.end()
                result = result[:insert_pos] + link_html + result[insert_pos:]
                count += 1
            print(f"    Injected after pattern: '{pattern[:60]}...' ({len(matches)}x)")
            break

    return result, count

def json_escape(s):
    """Escape a string for embedding in JSON."""
    return json.dumps(s)[1:-1]  # Strip surrounding quotes

# ============================================================
# PAGE AUDIT
# ============================================================

print("=" * 70)
print("LEVELS-UP LINK AUDIT — ALL 4 PRICING PAGES")
print("=" * 70)

TARGET_PAGES = [
    {"label": "Partnered Pricing Page", "slug": "partnered", "tier": "partnered", "tier_name": "Partnered"},
    {"label": "Unified Pricing Page", "slug": "unified", "tier": "unified", "tier_name": "Unified"},
    {"label": "Pay Test 2", "slug": "pay-test-2", "tier": None, "tier_name": None},
    {"label": "Pay Test Sandbox 3", "slug": "pay-test-sandbox-3", "tier": None, "tier_name": None},
]

# Also try known IDs
KNOWN_IDS = {
    "pay-test-sandbox-3": 1232,
}

audit_results = []

for target in TARGET_PAGES:
    slug = target["slug"]
    label = target["label"]
    print(f"\n{'='*60}")
    print(f"CHECKING: {label} (/{slug}/)")
    print(f"{'='*60}")

    # Find page
    page = find_page_by_slug(slug)

    if not page and slug in KNOWN_IDS:
        print(f"  Slug lookup failed, trying known ID {KNOWN_IDS[slug]}...")
        try:
            page_data = get_page_full(KNOWN_IDS[slug])
            page = {"id": KNOWN_IDS[slug], "slug": slug, "link": f"https://purebrain.ai/{slug}/"}
        except Exception as e:
            print(f"  Known ID also failed: {e}")
            audit_results.append({**target, "found": False, "error": str(e)})
            continue

    if not page:
        print(f"  ERROR: Page not found for slug '{slug}'")
        audit_results.append({**target, "found": False, "error": "Page not found"})
        continue

    page_id = page['id']
    page_url = page.get('link', f"https://purebrain.ai/{slug}/")
    print(f"  Found: ID={page_id} URL={page_url}")

    # Get full content
    try:
        full = get_page_full(page_id)
    except Exception as e:
        print(f"  ERROR getting full content: {e}")
        audit_results.append({**target, "found": True, "page_id": page_id, "error": str(e)})
        continue

    content_raw = full.get('content', {}).get('raw', '')
    meta = full.get('meta', {}) or {}
    elementor_data = meta.get('_elementor_data', '') or ''

    if not isinstance(elementor_data, str):
        elementor_data = json.dumps(elementor_data)

    print(f"  Content raw: {len(content_raw):,} chars")
    print(f"  Elementor data: {len(elementor_data):,} chars")

    # Check for existing link
    has_link_in_content = check_for_link(content_raw)
    has_link_in_elementor = check_for_link(elementor_data)
    has_link = has_link_in_content or has_link_in_elementor

    if has_link:
        print(f"  STATUS: ✅ LINK ALREADY PRESENT")
        print(f"    In content: {has_link_in_content}")
        print(f"    In elementor: {has_link_in_elementor}")
        audit_results.append({**target, "found": True, "page_id": page_id, "has_link": True, "updated": False})
        continue

    print(f"  STATUS: ❌ LINK MISSING — will add")

    # Detect what CTA buttons exist
    cta_checks = {
        'Reserve Keen Now': content_raw + elementor_data,
        'Activate Your AI Now': content_raw + elementor_data,
        'Claim This Spot': content_raw + elementor_data,
        'Get Started': content_raw + elementor_data,
        'Reserve Your AI Now': content_raw + elementor_data,
        'Get Partnered Now': content_raw + elementor_data,
        'Get Unified Now': content_raw + elementor_data,
    }

    found_ctas = []
    for cta_text, combined in cta_checks.items():
        if cta_text.lower() in combined.lower():
            found_ctas.append(cta_text)

    print(f"  CTA buttons found: {found_ctas}")

    # Determine tier-specific link targets
    # For pay-test pages, both tiers may appear
    tier_links = []
    if target["tier"]:
        # Single-tier pages
        tier_links = [(target["tier"], target["tier_name"])]
    else:
        # Multi-tier pay-test pages - check which tiers appear
        combined_all = content_raw + elementor_data
        if "partnered" in combined_all.lower():
            tier_links.append(("partnered", "Partnered"))
        if "unified" in combined_all.lower():
            tier_links.append(("unified", "Unified"))
        if not tier_links:
            tier_links = [("partnered", "Partnered"), ("unified", "Unified")]

    print(f"  Tiers to add links for: {[t[1] for t in tier_links]}")

    # Strategy: update content.raw (the wp:html block)
    # The pages use elementor_canvas with a single html widget
    # The HTML is in content.raw wrapped in <!-- wp:html -->

    if len(content_raw) < 1000:
        print(f"  WARNING: content_raw very short ({len(content_raw)} chars) — may be empty")
        print(f"  Will try to work with elementor_data instead")

    # For these pages, the actual HTML is in content.raw (the wp:html block)
    # We need to find the CTA button and inject the link after it

    updated_content = content_raw
    updates_made = 0

    # Different button patterns to search for
    for tier_slug, tier_name in tier_links:
        link_html = make_levels_up_link(tier_slug, tier_name)
        print(f"\n  Injecting link for {tier_name} tier...")

        # Try various button patterns
        # Pattern 1: button with "Reserve Keen Now"
        patterns_to_try = [
            # Match closing </button> or </a> for CTA
            r'<button[^>]*(?:reserve|keen|activate|claim|get started|partnered|unified)[^>]*>.*?</button>',
            r'<a[^>]*(?:reserve|keen|activate|claim|partnered|unified)[^>]*>.*?</a>',
            # Match by class patterns common in these pages
            r'<div[^>]*class="[^"]*cta-btn[^"]*"[^>]*>.*?</div>',
            r'<div[^>]*class="[^"]*pricing-cta[^"]*"[^>]*>.*?</div>',
            # Match the button itself
            r'<button[^>]*id="[^"]*Cta[^"]*"[^>]*>.*?</button>',
            r'<button[^>]*id="(?:proCta|partnerCta|unifiedCta)"[^>]*>.*?</button>',
        ]

        injected = False
        for pattern in patterns_to_try:
            try:
                matches = list(re.finditer(pattern, updated_content, re.IGNORECASE | re.DOTALL))
                if matches:
                    print(f"    Pattern matched: '{pattern[:50]}' ({len(matches)} times)")
                    # Insert after each match (in reverse)
                    for match in reversed(matches):
                        updated_content = updated_content[:match.end()] + link_html + updated_content[match.end():]
                        updates_made += 1
                    injected = True
                    break
            except Exception as e:
                print(f"    Pattern error: {e}")

        if not injected:
            print(f"    WARNING: Could not find button pattern to inject after")
            # Fallback: add before closing </div> of pricing card for this tier
            tier_pattern = rf'(?i)(</div>\s*</div>\s*(?=.*{tier_slug}))'
            print(f"    Trying fallback approach...")

    if updates_made > 0:
        print(f"\n  Attempting to save {updates_made} injected links...")

        # Save updated content
        try:
            result = wp_post(f"/pages/{page_id}", {
                "content": updated_content
            })
            print(f"  ✅ Saved content update")

            # Clear Elementor cache
            print(f"  Clearing Elementor cache...")
            clear_elementor_cache()

            audit_results.append({**target, "found": True, "page_id": page_id, "has_link": False, "updated": True, "updates_made": updates_made})
        except Exception as e:
            print(f"  ❌ Save failed: {e}")
            audit_results.append({**target, "found": True, "page_id": page_id, "has_link": False, "updated": False, "error": str(e)})
    else:
        print(f"\n  WARNING: No injection points found — manual intervention needed")
        print(f"  Saving raw content snippet for review...")

        # Save first 3000 chars of content for review
        preview = content_raw[:3000] if content_raw else elementor_data[:3000]
        preview_file = f"/home/jared/projects/AI-CIV/aether/exports/content-preview-{slug}.txt"
        with open(preview_file, 'w') as f:
            f.write(f"Page: {label}\nSlug: {slug}\nID: {page_id}\n\n")
            f.write(f"=== CONTENT RAW (first 3000 chars) ===\n{preview}")
        print(f"  Preview saved: {preview_file}")

        audit_results.append({**target, "found": True, "page_id": page_id, "has_link": False, "updated": False, "error": "No button patterns matched"})

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("AUDIT COMPLETE — SUMMARY")
print("=" * 70)

for result in audit_results:
    label = result["label"]
    if result.get("error") and not result.get("found"):
        status = "❓ NOT FOUND"
    elif result.get("has_link"):
        status = "✅ ALREADY HAD LINK"
    elif result.get("updated"):
        status = f"✅ LINK ADDED ({result.get('updates_made', '?')} injections)"
    elif result.get("error"):
        status = f"❌ FAILED: {result.get('error', 'unknown')[:60]}"
    else:
        status = "⚠️ NEEDS MANUAL ATTENTION"
    print(f"  {status}")
    print(f"    {label} | ID={result.get('page_id','?')} | /{result.get('slug','?')}/")

print("\nScript complete.")
