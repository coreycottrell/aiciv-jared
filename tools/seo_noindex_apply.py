#!/usr/bin/env python3
"""
SEO noindex + meta tags application script for purebrain.ai
Applies noindex to internal/test/deprecated pages and sets SEO meta for special pages.
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "https://purebrain.ai/wp-json/wp/v2"
PLUGIN_URL = "https://purebrain.ai/wp-json/purebrain/v1/update-post-meta"
AUTH = ("Aether", "FlFr2VOtlHiHaJWjzW96OHUJ")

results = []

def log(msg):
    print(msg)
    results.append(msg)

def set_noindex(page_id, slug, noindex_value):
    """Set or remove noindex on a page. noindex_value: '1' to noindex, '0' to index."""
    action = "noindex" if noindex_value == "1" else "REMOVE noindex (allow index)"
    try:
        resp = requests.post(
            f"{BASE_URL}/pages/{page_id}",
            auth=AUTH,
            json={"meta": {"_yoast_wpseo_meta-robots-noindex": noindex_value}},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            meta = data.get("meta", {})
            actual = meta.get("_yoast_wpseo_meta-robots-noindex", "?")
            status = "OK" if str(actual) == str(noindex_value) else f"MISMATCH (got {repr(actual)})"
            log(f"  [{status}] ID {page_id} /{slug}/ -> {action}")
            return status == "OK"
        else:
            log(f"  [FAIL] ID {page_id} /{slug}/ -> HTTP {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        log(f"  [ERROR] ID {page_id} /{slug}/ -> {e}")
        return False

def set_meta_via_plugin(page_id, meta_key, meta_value, label):
    """Set a Yoast meta field via the custom plugin endpoint."""
    try:
        resp = requests.post(
            PLUGIN_URL,
            auth=AUTH,
            json={"post_id": page_id, "meta_key": meta_key, "meta_value": meta_value},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                log(f"    [OK] {label}: {repr(meta_value[:80])}")
                return True
            else:
                log(f"    [FAIL] {label}: {data}")
                return False
        else:
            log(f"    [FAIL HTTP {resp.status_code}] {label}: {resp.text[:200]}")
            return False
    except Exception as e:
        log(f"    [ERROR] {label}: {e}")
        return False

def set_standard_meta(page_id, meta_key, meta_value, label):
    """Set a standard WP meta field via REST API."""
    try:
        resp = requests.post(
            f"{BASE_URL}/pages/{page_id}",
            auth=AUTH,
            json={"meta": {meta_key: meta_value}},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if resp.status_code in (200, 201):
            log(f"    [OK] {label}: {repr(meta_value[:80])}")
            return True
        else:
            log(f"    [FAIL HTTP {resp.status_code}] {label}: {resp.text[:200]}")
            return False
    except Exception as e:
        log(f"    [ERROR] {label}: {e}")
        return False

def set_excerpt(page_id, excerpt_value, label):
    """Set the page excerpt."""
    try:
        resp = requests.post(
            f"{BASE_URL}/pages/{page_id}",
            auth=AUTH,
            json={"excerpt": excerpt_value},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if resp.status_code in (200, 201):
            log(f"    [OK] {label}: {repr(excerpt_value[:80])}")
            return True
        else:
            log(f"    [FAIL HTTP {resp.status_code}] {label}: {resp.text[:200]}")
            return False
    except Exception as e:
        log(f"    [ERROR] {label}: {e}")
        return False

def verify_noindex(page_id, slug, expected):
    """Verify the noindex state of a page."""
    try:
        resp = requests.get(f"{BASE_URL}/pages/{page_id}", auth=AUTH, timeout=15)
        data = resp.json()
        meta = data.get("meta", {})
        actual = meta.get("_yoast_wpseo_meta-robots-noindex", "")
        match = str(actual) == str(expected)
        status = "CONFIRMED" if match else f"MISMATCH: expected {repr(expected)}, got {repr(actual)}"
        return match, status
    except Exception as e:
        return False, f"ERROR: {e}"


log("=" * 70)
log("SEO NOINDEX APPLICATION SCRIPT - purebrain.ai")
log(f"Run time: {datetime.now().isoformat()}")
log("=" * 70)

# ==========================================================================
# SECTION 1: Pages that already have noindex (verify, no changes needed)
# ==========================================================================
log("")
log("## SECTION 1: Verifying Already-Noindexed Pages")
log("")

already_done = [
    (95, "blog-old"),
    (174, "purebrain-2-0"),
    (338, "purebrain-3"),
    (383, "purebrain-4"),
    (439, "pay-test"),
    (468, "pay-test-sandbox"),
    (688, "pay-test-sandbox-2"),
    (689, "pay-test-2"),
    (811, "ai-partnership-calculator"),
    (843, "team-dashboard"),
    (854, "duckdive-report"),
    (859, "client-report-duckdive"),
    (309, "thank-you"),
    (855, "website-execution"),
]

for page_id, slug in already_done:
    match, status = verify_noindex(page_id, slug, "1")
    log(f"  [{status}] ID {page_id} /{slug}/")

# ==========================================================================
# SECTION 2: Apply noindex to pages that need it
# ==========================================================================
log("")
log("## SECTION 2: Applying noindex to Pages That Need It")
log("")

needs_noindex = [
    (963, "demo-no-bs"),
    (532, "living-avatar"),
]

for page_id, slug in needs_noindex:
    set_noindex(page_id, slug, "1")

# ==========================================================================
# SECTION 3: Remove noindex from legal pages (should be indexed)
# ==========================================================================
log("")
log("## SECTION 3: Removing noindex from Legal Pages (Allow Indexing)")
log("")

log("  Processing ID 3 /privacy-policy/ - removing noindex...")
set_noindex(3, "privacy-policy", "0")

log("  Processing ID 541 /terms-of-service/ - removing noindex...")
set_noindex(541, "terms-of-service", "0")

# ==========================================================================
# SECTION 4: AI Readiness Assessment (ID 403) - SEO meta
# ==========================================================================
log("")
log("## SECTION 4: AI Readiness Assessment (ID 403) - SEO Meta")
log("")

log("  Setting OG title...")
set_meta_via_plugin(403, "_yoast_wpseo_opengraph-title", "AI Readiness Self-Assessment | PureBrain.ai", "OG title")

log("  Setting OG description...")
set_meta_via_plugin(403, "_yoast_wpseo_opengraph-description", "Assess your readiness for AI partnership. Free self-assessment to determine which PureBrain tier fits your business.", "OG description")

log("  Setting meta description...")
set_meta_via_plugin(403, "_yoast_wpseo_metadesc", "Free AI readiness self-assessment to determine your business's readiness for AI partnership with PureBrain.", "Meta description")

log("  Setting excerpt...")
set_excerpt(403, "Free AI readiness self-assessment to determine your business's readiness for AI partnership with PureBrain.", "Excerpt")

log("  Setting OG image (media 694)...")
# Yoast OG image is stored as _yoast_wpseo_opengraph-image and _yoast_wpseo_opengraph-image-id
set_meta_via_plugin(403, "_yoast_wpseo_opengraph-image", "https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg", "OG image URL")
set_meta_via_plugin(403, "_yoast_wpseo_opengraph-image-id", "694", "OG image ID")

# ==========================================================================
# SECTION 5: Privacy Policy (ID 3) - SEO meta
# ==========================================================================
log("")
log("## SECTION 5: Privacy Policy (ID 3) - SEO Meta")
log("")

log("  Setting SEO title...")
set_meta_via_plugin(3, "_yoast_wpseo_title", "Privacy Policy | PureBrain.ai — Pure Technology", "SEO title")

log("  Setting OG title...")
set_meta_via_plugin(3, "_yoast_wpseo_opengraph-title", "Privacy Policy — PureBrain.ai", "OG title")

log("  Setting excerpt...")
set_excerpt(3, "PureBrain.ai privacy policy by Pure Technology. How we collect, use, and protect your data.", "Excerpt")

# ==========================================================================
# SECTION 6: Terms of Service (ID 541) - SEO meta
# ==========================================================================
log("")
log("## SECTION 6: Terms of Service (ID 541) - SEO Meta")
log("")

log("  Setting SEO title...")
set_meta_via_plugin(541, "_yoast_wpseo_title", "Terms of Service | PureBrain.ai — Pure Technology", "SEO title")

log("  Setting OG title...")
set_meta_via_plugin(541, "_yoast_wpseo_opengraph-title", "Terms of Service — PureBrain.ai", "OG title")

log("  Setting excerpt...")
set_excerpt(541, "PureBrain.ai terms of service by Pure Technology. Terms governing use of PureBrain AI partnership services.", "Excerpt")

# ==========================================================================
# SECTION 7: Final Verification
# ==========================================================================
log("")
log("## SECTION 7: Final Verification")
log("")

log("  Verifying noindex pages...")
verify_pages = [
    (963, "demo-no-bs", "1"),
    (532, "living-avatar", "1"),
    (3, "privacy-policy", "0"),
    (541, "terms-of-service", "0"),
]
for page_id, slug, expected in verify_pages:
    match, status = verify_noindex(page_id, slug, expected)
    expected_label = "noindex=1 (blocked)" if expected == "1" else "noindex=0 (indexed)"
    icon = "OK" if match else "FAIL"
    log(f"  [{icon}] ID {page_id} /{slug}/ -> {expected_label} | {status}")

log("  Verifying AI Readiness meta...")
try:
    resp = requests.get(f"{BASE_URL}/pages/403", auth=AUTH, timeout=15)
    data = resp.json()
    meta = data.get("meta", {})
    yoast = data.get("yoast_head_json", {})
    log(f"    og_title (meta): {repr(meta.get('_yoast_wpseo_opengraph-title',''))}")
    log(f"    og_title (yoast_head): {repr(yoast.get('og_title',''))}")
    log(f"    og_image (yoast_head): {repr(yoast.get('og_image',''))}")
    log(f"    og_desc (yoast_head): {repr(yoast.get('og_description',''))}")
except Exception as e:
    log(f"    ERROR verifying 403: {e}")

log("  Verifying Privacy Policy meta...")
try:
    resp = requests.get(f"{BASE_URL}/pages/3", auth=AUTH, timeout=15)
    data = resp.json()
    meta = data.get("meta", {})
    yoast = data.get("yoast_head_json", {})
    log(f"    seo_title (yoast): {repr(yoast.get('title',''))}")
    log(f"    og_title (yoast): {repr(yoast.get('og_title',''))}")
    log(f"    noindex: {repr(meta.get('_yoast_wpseo_meta-robots-noindex',''))}")
except Exception as e:
    log(f"    ERROR verifying 3: {e}")

log("  Verifying Terms of Service meta...")
try:
    resp = requests.get(f"{BASE_URL}/pages/541", auth=AUTH, timeout=15)
    data = resp.json()
    meta = data.get("meta", {})
    yoast = data.get("yoast_head_json", {})
    log(f"    seo_title (yoast): {repr(yoast.get('title',''))}")
    log(f"    og_title (yoast): {repr(yoast.get('og_title',''))}")
    log(f"    noindex: {repr(meta.get('_yoast_wpseo_meta-robots-noindex',''))}")
except Exception as e:
    log(f"    ERROR verifying 541: {e}")

log("")
log("=" * 70)
log("SCRIPT COMPLETE")
log("=" * 70)

# Output full results string
print("\n\n--- RESULTS FOR REPORT ---")
print("\n".join(results))
