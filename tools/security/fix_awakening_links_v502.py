#!/usr/bin/env python3
"""
Fix #awakening links across all blog posts on purebrain.ai and jareddsanborn.com.

Changes:
1. All href="#awakening" or href="...#awakening" → href="https://purebrain.ai/ai-partnership-assessment/..."
   - UTM params preserved (moved to assessment URL)
   - Direct #awakening links → https://purebrain.ai/ai-partnership-assessment/
2. Add -webkit-text-fill-color: #ffffff to styled button <a> tags

This fixes the link destination AND ensures WebKit browsers show white text.
"""

import os
import re
import json
import time
import requests
from urllib.parse import urlparse, parse_qs, urlencode

# ─── CREDENTIALS ─────────────────────────────────────────────────────────────
PB_USER = "Aether"
PB_PASS = os.environ.get("PUREBRAIN_WP_APP_PASSWORD", "")
if not PB_PASS:
    # Read from .env directly
    env_path = os.path.join(os.path.dirname(__file__), "../../.env")
    with open(env_path) as f:
        for line in f:
            if line.startswith("PUREBRAIN_WP_APP_PASSWORD="):
                PB_PASS = line.split("=", 1)[1].strip().strip("'")
                break

JDS_USER = "AetherPureBrain.ai"
JDS_PASS = os.environ.get("WORDPRESS_APP_PASSWORD", "")
if not JDS_PASS:
    env_path = os.path.join(os.path.dirname(__file__), "../../.env")
    with open(env_path) as f:
        for line in f:
            if line.startswith("WORDPRESS_APP_PASSWORD="):
                JDS_PASS = line.split("=", 1)[1].strip().strip("'")
                break

ASSESSMENT_URL = "https://purebrain.ai/ai-partnership-assessment/"

# ─── POST LISTS ──────────────────────────────────────────────────────────────
PB_POSTS = [879, 696, 631, 606, 565, 480, 381, 316, 373, 172]
JDS_POSTS = [1195, 1180, 1122, 1092, 1074, 1069, 1060]


def build_assessment_href(original_href):
    """
    Convert any #awakening href to the assessment URL.

    Examples:
      https://purebrain.ai/#awakening → https://purebrain.ai/ai-partnership-assessment/
      https://purebrain.ai/?utm_source=blog&utm_medium=cta#awakening
        → https://purebrain.ai/ai-partnership-assessment/?utm_source=blog&utm_medium=cta
    """
    # Strip the #awakening fragment
    base = original_href.split("#awakening")[0]
    # Decode HTML entities in URL
    base = base.replace("&#038;", "&")

    # If it's just the root URL (with or without trailing ?)
    parsed = urlparse(base)
    query = parsed.query.rstrip("&")

    if query:
        return f"{ASSESSMENT_URL}?{query}"
    else:
        return ASSESSMENT_URL


def fix_link_href(match_str):
    """
    Take a full <a ...> tag string and:
    1. Update href to assessment URL
    2. Add -webkit-text-fill-color: #ffffff if it's a styled button
    Returns the fixed tag.
    """
    # Extract existing href
    href_match = re.search(r'href=["\']([^"\']+)["\']', match_str)
    if not href_match:
        return match_str

    old_href = href_match.group(1)
    new_href = build_assessment_href(old_href)

    # Replace the href
    result = re.sub(r'href=["\'][^"\']+["\']', f'href="{new_href}"', match_str)

    # Check if this is a styled button (has display:inline-block or background:linear-gradient)
    is_styled_button = "inline-block" in match_str or "linear-gradient" in match_str

    if is_styled_button:
        # Check if -webkit-text-fill-color already there
        if "-webkit-text-fill-color" not in result:
            # Add it after the existing color: #ffffff !important
            # Insert before closing > of the <a tag
            if "text-decoration: none !important;" in result:
                result = result.replace(
                    "text-decoration: none !important;",
                    "text-decoration: none !important; -webkit-text-fill-color: #ffffff;"
                )
            elif "color: #ffffff !important;" in result:
                result = result.replace(
                    "color: #ffffff !important;",
                    "color: #ffffff !important; -webkit-text-fill-color: #ffffff;"
                )
            else:
                # Add it to the style attribute if present
                if 'style="' in result:
                    result = result.replace('style="', 'style="-webkit-text-fill-color: #ffffff; ', 1)

    return result


def fix_post_content(content):
    """
    Find and fix all <a href="...#awakening..."> tags in the post content.
    Returns (fixed_content, list_of_changes)
    """
    changes = []

    def replace_link(m):
        original = m.group(0)
        fixed = fix_link_href(original)
        if fixed != original:
            # Extract just the <a ...> opening tag for the report
            old_href_m = re.search(r'href=["\']([^"\']+)["\']', original)
            new_href_m = re.search(r'href=["\']([^"\']+)["\']', fixed)
            old_href = old_href_m.group(1) if old_href_m else "?"
            new_href = new_href_m.group(1) if new_href_m else "?"

            webkit_added = "-webkit-text-fill-color" in fixed and "-webkit-text-fill-color" not in original

            changes.append({
                "old_href": old_href,
                "new_href": new_href,
                "webkit_added": webkit_added,
            })
        return fixed

    # Match full <a ...>...</a> tags that contain #awakening in the href
    fixed = re.sub(
        r'<a\b[^>]*#awakening[^>]*>.*?</a>',
        replace_link,
        content,
        flags=re.DOTALL
    )

    return fixed, changes


def update_post(site_url, user, password, post_id, dry_run=False):
    """Fetch, fix, and update a single WordPress post."""
    fetch_url = f"{site_url}/wp-json/wp/v2/posts/{post_id}?context=edit"

    r = requests.get(fetch_url, auth=(user, password))
    if r.status_code != 200:
        print(f"  ERROR fetching post {post_id}: {r.status_code}")
        return False

    data = r.json()
    original_content = data["content"]["raw"]

    fixed_content, changes = fix_post_content(original_content)

    if not changes:
        print(f"  Post {post_id}: no changes needed")
        return True

    print(f"  Post {post_id} '{data['title']['raw'][:50]}': {len(changes)} change(s)")
    for c in changes:
        print(f"    href: {c['old_href'][:70]} → {c['new_href'][:70]}")
        if c['webkit_added']:
            print(f"    +webkit-text-fill-color: #ffffff")

    if dry_run:
        print(f"  [DRY RUN] Would update post {post_id}")
        return True

    # Update the post
    update_url = f"{site_url}/wp-json/wp/v2/posts/{post_id}"
    update_r = requests.post(
        update_url,
        auth=(user, password),
        json={"content": fixed_content}
    )

    if update_r.status_code in (200, 201):
        print(f"  Post {post_id}: UPDATED OK (HTTP {update_r.status_code})")
        return True
    else:
        print(f"  Post {post_id}: UPDATE FAILED (HTTP {update_r.status_code})")
        print(f"  Response: {update_r.text[:300]}")
        return False


def verify_post(site_url, user, password, post_id):
    """Verify that a post has been correctly updated."""
    fetch_url = f"{site_url}/wp-json/wp/v2/posts/{post_id}?context=edit"
    r = requests.get(fetch_url, auth=(user, password))
    if r.status_code != 200:
        return False, "fetch failed"

    content = r.json()["content"]["raw"]

    remaining_awakening = re.findall(r'href=["\'][^"\']*#awakening[^"\']*["\']', content)
    has_assessment = ASSESSMENT_URL in content

    # Check styled buttons have webkit
    styled_btns = re.findall(r'<a[^>]*(?:inline-block|linear-gradient)[^>]*>', content)
    missing_webkit = [b for b in styled_btns if "webkit-text-fill-color" not in b]

    if remaining_awakening:
        return False, f"{len(remaining_awakening)} awakening links remain: {remaining_awakening}"
    if not has_assessment:
        return False, "assessment URL not found in content"
    if missing_webkit:
        return False, f"{len(missing_webkit)} styled buttons missing -webkit-text-fill-color"

    return True, "OK"


def main():
    print("=" * 60)
    print("fix_awakening_links_v502.py")
    print(f"Target: {ASSESSMENT_URL}")
    print("=" * 60)
    print()

    results = {"pb": {}, "jds": {}}

    # ─── PUREBRAIN.AI ─────────────────────────────────────────────────
    print("=== PUREBRAIN.AI ===")
    for post_id in PB_POSTS:
        success = update_post("https://purebrain.ai", PB_USER, PB_PASS, post_id)
        results["pb"][post_id] = success
        time.sleep(0.5)

    print()
    print("=== JAREDDSANBORN.COM ===")
    for post_id in JDS_POSTS:
        success = update_post("https://jareddsanborn.com", JDS_USER, JDS_PASS, post_id)
        results["jds"][post_id] = success
        time.sleep(0.5)

    print()
    print("=" * 60)
    print("VERIFICATION PASS")
    print("=" * 60)

    all_ok = True

    print("\n--- PUREBRAIN.AI ---")
    for post_id in PB_POSTS:
        ok, msg = verify_post("https://purebrain.ai", PB_USER, PB_PASS, post_id)
        status = "PASS" if ok else "FAIL"
        print(f"  Post {post_id}: [{status}] {msg}")
        if not ok:
            all_ok = False

    print("\n--- JAREDDSANBORN.COM ---")
    for post_id in JDS_POSTS:
        ok, msg = verify_post("https://jareddsanborn.com", JDS_USER, JDS_PASS, post_id)
        status = "PASS" if ok else "FAIL"
        print(f"  Post {post_id}: [{status}] {msg}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED — see above")

    return all_ok


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
