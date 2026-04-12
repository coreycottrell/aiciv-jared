#!/usr/bin/env python3
"""
Deploy 'How This Levels You Up' links to 4 pricing pages.

Adds a teal link below each CTA button:
  "How This Levels You Up →"
  Links to /[tier]-how-this-levels-you-up/

Target pages:
1. partnered/           (page with "Get Partnered Now" CTA)
2. unified/             (page with "Activate Unified" CTA)
3. pay-test-2           (multi-tier page, Partnered + Unified CTAs)
4. pay-test-sandbox-3   (multi-tier page, ID=1232)

Run:
  python3 /home/jared/projects/AI-CIV/aether/tools/deploy_levels_up_links.py

Author: cto agent (2026-03-06)
"""

import json
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import base64

# ============================================================
# CONFIG
# ============================================================

WP_URL   = "https://purebrain.ai"
WP_USER  = "Aether"
WP_PASS  = "ZGuh 1W8k WpWM c9iy kqyd buPr"
AUTH     = "Basic " + base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()

LOG = []

# ============================================================
# LINK HTML TEMPLATE
# ============================================================

def levels_up_link(tier_slug):
    """
    Returns the HTML snippet for the 'How This Levels You Up' link.
    tier_slug: 'partnered' or 'unified'
    """
    href = f"https://purebrain.ai/{tier_slug}-how-this-levels-you-up/"
    return (
        '\n<div class="pb-levels-up-link" style="text-align:center;margin-top:14px;margin-bottom:4px;">'
        f'<a href="{href}" '
        'style="color:#00bcd4;font-size:0.875rem;font-weight:500;text-decoration:none;'
        'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;'
        'letter-spacing:0.025em;'
        'border-bottom:1px solid rgba(0,188,212,0.35);padding-bottom:2px;'
        'transition:color 0.15s,border-color 0.15s;">'
        'How This Levels You Up &#8594;'
        '</a>'
        '</div>'
    )

# ============================================================
# WP API HELPERS
# ============================================================

def wp_request(method, path, data=None, timeout=120):
    url = f"{WP_URL}/wp-json/{path}"
    headers = {
        "Authorization": AUTH,
        "Content-Type": "application/json",
        "User-Agent": "Aether-CTO/1.0",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Length"] = str(len(body))

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  HTTP {e.code}: {body[:300]}")
        return e.code, body
    except Exception as ex:
        print(f"  Error: {ex}")
        return 0, str(ex)


def get_page_by_slug(slug):
    """Find a page by slug."""
    status, data = wp_request("GET", f"wp/v2/pages?slug={urllib.parse.quote(slug)}&context=edit&_fields=id,slug,title,link,content,meta&per_page=5")
    if status == 200 and isinstance(data, list) and data:
        return data[0]
    return None


def get_page_by_id(page_id):
    """Get page content by ID."""
    status, data = wp_request("GET", f"wp/v2/pages/{page_id}?context=edit")
    if status == 200 and isinstance(data, dict):
        return data
    return None


def update_page(page_id, content_raw, elementor_data=None):
    """Update page content + optionally elementor_data."""
    payload = {"content": content_raw}
    if elementor_data is not None:
        payload["meta"] = {"_elementor_data": elementor_data}
    status, resp = wp_request("POST", f"wp/v2/pages/{page_id}", data=payload, timeout=180)
    return status, resp


def clear_elementor_cache():
    """DELETE /wp-json/elementor/v1/cache"""
    status, resp = wp_request("DELETE", "elementor/v1/cache", timeout=30)
    print(f"  Cache clear: HTTP {status}")
    return status


# ============================================================
# LINK INJECTION
# ============================================================

def already_has_link(text):
    """Check if the levels-up link is already present."""
    if not text:
        return False
    checks = [
        "how this levels you up",
        "levels-you-up",
        "pb-levels-up-link",
    ]
    lower = text.lower()
    return any(c in lower for c in checks)


def find_cta_patterns(combined_text):
    """Detect which CTA button texts exist in the content."""
    patterns = [
        "Get Partnered Now",
        "Activate Your Partnered AI",
        "Get Unified Now",
        "Activate Unified",
        "Activate Your AI Now",
        "Claim This Spot",
        "Reserve Keen Now",
        "Reserve Your AI Now",
    ]
    found = []
    for p in patterns:
        if p.lower() in combined_text.lower():
            found.append(p)
    return found


def inject_after_cta_button(html, cta_text, link_html):
    """
    Inject link_html immediately after the closing tag of a CTA button/link
    that contains cta_text. Works on <button> and <a> elements.
    Returns (modified_html, count).
    """
    count = 0
    result = html

    # Pattern 1: <button ...>cta_text...</button>
    # Pattern 2: <a ...>cta_text...</a>
    # Use flexible matching that allows for HTML entities and surrounding whitespace

    escaped = re.escape(cta_text)

    patterns = [
        # Button element containing the text
        rf'(<button[^>]*>(?:(?!</button>).)*?{escaped}(?:(?!</button>).)*?</button>)',
        # Anchor element containing the text
        rf'(<a[^>]*>(?:(?!</a>).)*?{escaped}(?:(?!</a>).)*?</a>)',
        # Div/span with role=button
        rf'(<(?:div|span)[^>]*>(?:(?!</(?:div|span)>).)*?{escaped}(?:(?!</(?:div|span)>).)*?</(?:div|span)>)',
    ]

    for pat in patterns:
        try:
            matches = list(re.finditer(pat, result, re.IGNORECASE | re.DOTALL))
            if matches:
                # Insert after each match (reverse order to preserve positions)
                for m in reversed(matches):
                    result = result[:m.end()] + link_html + result[m.end():]
                    count += len(matches)
                print(f"    Pattern found '{cta_text}' x{len(matches)} using tag pattern")
                return result, count
        except re.error as e:
            print(f"    Regex error for '{cta_text}': {e}")
            continue

    return result, 0


def inject_after_openmodal_button(html, modal_fn, link_html):
    """
    For pay-test pages where buttons call JS modal functions (openWaitlistModal, openPayPalModal).
    Find onclick="openXxxModal" buttons and inject after them.
    """
    count = 0
    result = html

    pat = rf'(<(?:button|a)[^>]*onclick=["\'][^"\']*{re.escape(modal_fn)}[^"\']*["\'][^>]*>.*?</(?:button|a)>)'
    try:
        matches = list(re.finditer(pat, result, re.IGNORECASE | re.DOTALL))
        if matches:
            for m in reversed(matches):
                result = result[:m.end()] + link_html + result[m.end():]
                count += len(matches)
            print(f"    Injected after onclick={modal_fn} x{len(matches)}")
    except re.error as e:
        print(f"    Regex error for modal fn '{modal_fn}': {e}")

    return result, count


def inject_by_button_id(html, button_id, link_html):
    """Inject after a button with a specific ID."""
    pat = rf'(<(?:button|a)[^>]*id=["\'](?:{re.escape(button_id)})["\'][^>]*>.*?</(?:button|a)>)'
    count = 0
    result = html
    try:
        matches = list(re.finditer(pat, result, re.IGNORECASE | re.DOTALL))
        if matches:
            for m in reversed(matches):
                result = result[:m.end()] + link_html + result[m.end():]
                count += len(matches)
            print(f"    Injected after button id='{button_id}' x{len(matches)}")
    except re.error as e:
        print(f"    Regex error for button id '{button_id}': {e}")
    return result, count


# ============================================================
# PAGE-SPECIFIC STRATEGIES
# ============================================================

def process_partnered_page(page):
    """
    /partnered/ — single tier page, CTA is 'Get Partnered Now'
    Add link → /partnered-how-this-levels-you-up/
    """
    tier = "partnered"
    link = levels_up_link(tier)

    content = page.get("content", {}).get("raw", "") or ""
    meta = page.get("meta", {}) or {}
    elementor_data = meta.get("_elementor_data", "") or ""

    if not isinstance(elementor_data, str):
        elementor_data = json.dumps(elementor_data)

    combined = content + elementor_data

    if already_has_link(combined):
        print("  ✅ Link already present — skipping")
        return None, None, "already_present"

    print(f"  Content: {len(content):,} chars | Elementor: {len(elementor_data):,} chars")
    ctabs = find_cta_patterns(combined)
    print(f"  CTA buttons found: {ctabs}")

    # Try injecting into content.raw
    new_content = content
    total_injected = 0

    cta_texts = ["Get Partnered Now", "Activate Your Partnered AI", "Activate Your AI Now"]
    for cta_text in cta_texts:
        if cta_text.lower() in new_content.lower():
            new_content, cnt = inject_after_cta_button(new_content, cta_text, link)
            total_injected += cnt
            if cnt > 0:
                break

    if total_injected == 0 and elementor_data:
        print("  Trying elementor_data injection...")
        new_elementor = elementor_data
        for cta_text in cta_texts:
            if cta_text.lower() in new_elementor.lower():
                new_elementor, cnt = inject_after_cta_button(new_elementor, cta_text, link)
                total_injected += cnt
                if cnt > 0:
                    break
        if total_injected > 0:
            return new_content, new_elementor, f"injected_elementor_{total_injected}"

    if total_injected > 0:
        return new_content, None, f"injected_content_{total_injected}"

    print(f"  ⚠️  No injection point found. Appending link before </body> or end of content.")
    # Fallback: append before </body>
    if "</body>" in new_content:
        new_content = new_content.replace("</body>", link + "\n</body>", 1)
    else:
        new_content = new_content + link

    return new_content, None, "appended_fallback"


def process_unified_page(page):
    """
    /unified/ — single tier page
    Add link → /unified-how-this-levels-you-up/
    """
    tier = "unified"
    link = levels_up_link(tier)

    content = page.get("content", {}).get("raw", "") or ""
    meta = page.get("meta", {}) or {}
    elementor_data = meta.get("_elementor_data", "") or ""

    if not isinstance(elementor_data, str):
        elementor_data = json.dumps(elementor_data)

    combined = content + elementor_data

    if already_has_link(combined):
        print("  ✅ Link already present — skipping")
        return None, None, "already_present"

    print(f"  Content: {len(content):,} chars | Elementor: {len(elementor_data):,} chars")
    ctabs = find_cta_patterns(combined)
    print(f"  CTA buttons found: {ctabs}")

    new_content = content
    total_injected = 0

    cta_texts = ["Get Unified Now", "Activate Unified", "Activate Your AI Now", "pb-activate-btn"]
    for cta_text in cta_texts:
        if cta_text.lower() in new_content.lower():
            new_content, cnt = inject_after_cta_button(new_content, cta_text, link)
            total_injected += cnt
            if cnt > 0:
                break

    if total_injected == 0 and elementor_data:
        new_elementor = elementor_data
        for cta_text in cta_texts:
            if cta_text.lower() in new_elementor.lower():
                new_elementor, cnt = inject_after_cta_button(new_elementor, cta_text, link)
                total_injected += cnt
                if cnt > 0:
                    break
        if total_injected > 0:
            return new_content, new_elementor, f"injected_elementor_{total_injected}"

    if total_injected > 0:
        return new_content, None, f"injected_content_{total_injected}"

    # Fallback
    if "</body>" in new_content:
        new_content = new_content.replace("</body>", link + "\n</body>", 1)
    else:
        new_content = new_content + link
    return new_content, None, "appended_fallback"


def process_multitiered_page(page, slug):
    """
    Multi-tier pages (pay-test-2, pay-test-sandbox-3):
    Add BOTH partnered and unified links under their respective CTA buttons.
    These pages have pricing-grid with Awakened, Partnered, Unified, Enterprise cards.
    """
    content = page.get("content", {}).get("raw", "") or ""
    meta = page.get("meta", {}) or {}
    elementor_data = meta.get("_elementor_data", "") or ""

    if not isinstance(elementor_data, str):
        elementor_data = json.dumps(elementor_data)

    combined = content + elementor_data

    if already_has_link(combined):
        print("  ✅ Link already present — skipping")
        return None, None, "already_present"

    print(f"  Content: {len(content):,} chars | Elementor: {len(elementor_data):,} chars")
    ctabs = find_cta_patterns(combined)
    print(f"  CTA buttons found: {ctabs}")

    new_content = content
    total_injected = 0

    # For multi-tier pages, inject BOTH partnered and unified links
    # Strategy: find button by ID (proCta, partnerCta, unifiedCta from memory)
    # or by text pattern near the tier name

    # Partnered CTA
    partnered_link = levels_up_link("partnered")
    unified_link = levels_up_link("unified")

    # Try button IDs first (known from sandbox-3 QA memory)
    new_content, cnt = inject_by_button_id(new_content, "partnerCta", partnered_link)
    total_injected += cnt

    new_content, cnt = inject_by_button_id(new_content, "unifiedCta", unified_link)
    total_injected += cnt

    # Try onclick modal functions
    if total_injected == 0:
        # openPayPalModal = Partnered/Unified CTA on older pages
        new_content, cnt = inject_after_openmodal_button(new_content, "openPayPalModal", partnered_link)
        total_injected += cnt

    # Try CTA text patterns
    if total_injected == 0:
        cta_pairs = [
            ("Activate Your AI Now", "partnered"),  # Used on sandbox-3 per memory
            ("Claim This Spot", "partnered"),
            ("Reserve Keen Now", "partnered"),
        ]
        for cta_text, tier in cta_pairs:
            if cta_text.lower() in new_content.lower():
                link = levels_up_link(tier)
                new_content, cnt = inject_after_cta_button(new_content, cta_text, link)
                total_injected += cnt

    # Also try elementor_data if content injection failed
    if total_injected == 0 and elementor_data and len(elementor_data) > 1000:
        print("  Trying elementor_data injection...")
        new_elementor = elementor_data
        cnt_total = 0

        new_elementor, cnt = inject_by_button_id(new_elementor, "partnerCta", partnered_link)
        cnt_total += cnt
        new_elementor, cnt = inject_by_button_id(new_elementor, "unifiedCta", unified_link)
        cnt_total += cnt

        if cnt_total > 0:
            return new_content, new_elementor, f"injected_elementor_{cnt_total}"

    if total_injected > 0:
        return new_content, None, f"injected_content_{total_injected}"

    # Fallback for multi-tier: add before pricing grid closing tag
    # These pages have a single HTML widget, content IS the page
    print("  ⚠️  No button patterns matched — using pricing grid fallback")

    # Look for pricing grid closing area and insert there
    grid_patterns = [
        r'</div>\s*<!-- end pricing-grid -->',
        r'</div>\s*<!-- /?pricing -->',
        r'(class="pricing-grid[^"]*"[^>]*>)((?:(?!</div>).)*?)(</div>)',
    ]
    # Simple approach: find each CTA area by context
    # Insert both links before </div> of each pricing card that mentions price
    # Pattern: "$499" or "$999" followed eventually by a button followed by </div>

    for price, tier in [("$499", "partnered"), ("$999", "unified")]:
        link = levels_up_link(tier)
        # Find the pricing card that has this price
        # Look for button in vicinity of this price
        price_idx = new_content.find(price)
        if price_idx >= 0:
            # Search forward for next </button> or </a> after the price
            btn_close = new_content.find("</button>", price_idx)
            a_close = new_content.find("</a>", price_idx)
            if btn_close > 0 and (a_close < 0 or btn_close < a_close):
                insert_pos = btn_close + len("</button>")
            elif a_close > 0:
                insert_pos = a_close + len("</a>")
            else:
                continue

            new_content = new_content[:insert_pos] + link + new_content[insert_pos:]
            total_injected += 1
            print(f"    Inserted {tier} link after button near {price}")

    if total_injected > 0:
        return new_content, None, f"injected_near_price_{total_injected}"

    # Last resort fallback
    print("  ⚠️  All strategies failed — prepending links before </body>")
    both_links = partnered_link + unified_link
    if "</body>" in new_content:
        new_content = new_content.replace("</body>", both_links + "\n</body>", 1)
    else:
        new_content = new_content + both_links
    return new_content, None, "appended_fallback"


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("LEVELS-UP LINK DEPLOYMENT")
    print("Target: 4 pricing pages | 2026-03-06")
    print("=" * 70)

    results = {}

    # ---- 1. partnered/ ----
    print("\n[1/4] PARTNERED PRICING PAGE")
    page = get_page_by_slug("partnered")
    if not page:
        print("  ERROR: /partnered/ not found — trying /partnered-how-this-levels-you-up/")
        page = get_page_by_slug("partnered-how-this-levels-you-up")

    if page:
        page_id = page["id"]
        slug = page["slug"]
        print(f"  Found: ID={page_id} slug='{slug}' url={page.get('link','?')}")
        new_content, new_elementor, action = process_partnered_page(page)

        if action != "already_present" and new_content is not None:
            status, resp = update_page(page_id, new_content, new_elementor)
            print(f"  Save: HTTP {status} ({action})")
            results["partnered"] = {"id": page_id, "action": action, "save_status": status}
        else:
            results["partnered"] = {"id": page_id, "action": action}
    else:
        print("  ERROR: Page not found")
        results["partnered"] = {"action": "not_found"}

    # ---- 2. unified/ ----
    print("\n[2/4] UNIFIED PRICING PAGE")
    page = get_page_by_slug("unified")
    if not page:
        print("  ERROR: /unified/ not found — trying /unified-how-this-levels-you-up/")
        page = get_page_by_slug("unified-how-this-levels-you-up")

    if page:
        page_id = page["id"]
        slug = page["slug"]
        print(f"  Found: ID={page_id} slug='{slug}' url={page.get('link','?')}")
        new_content, new_elementor, action = process_unified_page(page)

        if action != "already_present" and new_content is not None:
            status, resp = update_page(page_id, new_content, new_elementor)
            print(f"  Save: HTTP {status} ({action})")
            results["unified"] = {"id": page_id, "action": action, "save_status": status}
        else:
            results["unified"] = {"id": page_id, "action": action}
    else:
        print("  ERROR: Page not found")
        results["unified"] = {"action": "not_found"}

    # ---- 3. pay-test-2 ----
    print("\n[3/4] PAY-TEST-2")
    page = get_page_by_slug("pay-test-2")
    if not page:
        # Try by known ID 689 from exports folder
        print("  Slug not found — trying ID 689...")
        page = get_page_by_id(689)

    if page:
        page_id = page["id"]
        slug = page.get("slug", "pay-test-2")
        print(f"  Found: ID={page_id} slug='{slug}'")
        new_content, new_elementor, action = process_multitiered_page(page, "pay-test-2")

        if action != "already_present" and new_content is not None:
            status, resp = update_page(page_id, new_content, new_elementor)
            print(f"  Save: HTTP {status} ({action})")
            results["pay-test-2"] = {"id": page_id, "action": action, "save_status": status}
        else:
            results["pay-test-2"] = {"id": page_id, "action": action}
    else:
        print("  ERROR: Page not found")
        results["pay-test-2"] = {"action": "not_found"}

    # ---- 4. pay-test-sandbox-3 ----
    print("\n[4/4] PAY-TEST-SANDBOX-3")
    page = get_page_by_slug("pay-test-sandbox-3")
    if not page:
        print("  Slug not found — trying known ID 1232...")
        page = get_page_by_id(1232)

    if page:
        page_id = page["id"]
        slug = page.get("slug", "pay-test-sandbox-3")
        print(f"  Found: ID={page_id} slug='{slug}'")
        new_content, new_elementor, action = process_multitiered_page(page, "pay-test-sandbox-3")

        if action != "already_present" and new_content is not None:
            status, resp = update_page(page_id, new_content, new_elementor)
            print(f"  Save: HTTP {status} ({action})")
            results["pay-test-sandbox-3"] = {"id": page_id, "action": action, "save_status": status}
        else:
            results["pay-test-sandbox-3"] = {"id": page_id, "action": action}
    else:
        print("  ERROR: Page not found")
        results["pay-test-sandbox-3"] = {"action": "not_found"}

    # ---- Clear cache ----
    print("\n" + "=" * 70)
    print("CLEARING ELEMENTOR CACHE")
    clear_elementor_cache()

    # ---- Summary ----
    print("\n" + "=" * 70)
    print("DEPLOYMENT SUMMARY")
    print("=" * 70)

    for page_label, result in results.items():
        action = result.get("action", "unknown")
        page_id = result.get("id", "?")
        save_status = result.get("save_status", "N/A")

        if action == "already_present":
            status_str = "✅ ALREADY HAD LINK"
        elif action == "not_found":
            status_str = "❓ PAGE NOT FOUND"
        elif action.startswith("injected"):
            ok = "✅" if save_status == 200 else "⚠️"
            status_str = f"{ok} LINK ADDED ({action}, HTTP {save_status})"
        elif action == "appended_fallback":
            ok = "✅" if save_status == 200 else "⚠️"
            status_str = f"{ok} FALLBACK APPEND ({action}, HTTP {save_status})"
        else:
            status_str = f"⚠️ {action}"

        print(f"  {status_str}")
        print(f"    /{page_label}/ | ID={page_id}")

    print("\nDone.")
    return results


if __name__ == "__main__":
    main()
