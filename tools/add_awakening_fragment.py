#!/usr/bin/env python3
"""
Add #awakening fragment to ALL "Start Your AI Partnership" CTA button links
across both WordPress sites.

Target transformation:
  BEFORE: https://purebrain.ai/?utm_source=blog&utm_medium=cta&...
  AFTER:  https://purebrain.ai/?utm_source=blog&utm_medium=cta&...#awakening

  BEFORE: https://purebrain.ai/  (bare, no UTM)
  AFTER:  https://purebrain.ai/#awakening

Rules:
  - ONLY modify links that are CTA links (associated with "Start Your AI Partnership")
  - Skip newsletter/subscribe links
  - Skip blog interlinking (/blog/)
  - Preserve ALL existing UTM params
  - #awakening goes at the VERY END (after all query params)
  - Do NOT double-add: skip links that already have #awakening

Sites:
  - purebrain.ai     (auth: Aether / PUREBRAIN_WP_APP_PASSWORD)
  - jareddsanborn.com (auth: jared / WORDPRESS_APP_PASSWORD)
"""

import os
import re
import sys
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

SITES = [
    {
        "name": "purebrain.ai",
        "base": "https://purebrain.ai/wp-json/wp/v2",
        "auth": ("Aether", os.getenv("PUREBRAIN_WP_APP_PASSWORD", "").strip("'")),
        # Posts known to have CTAs (plus we fetch all to catch any extras)
        "priority_ids": [480, 381, 316, 373, 172, 98],
    },
    {
        "name": "jareddsanborn.com",
        "base": "https://jareddsanborn.com/wp-json/wp/v2",
        "auth": ("jared", os.getenv("WORDPRESS_APP_PASSWORD", "").strip("'")),
        "priority_ids": [1069],
    },
]

DELAY = 2  # seconds between API calls

# CTA link detection: href must point to purebrain.ai (homepage/root) and NOT be:
#   - a /blog/ path
#   - a newsletter/subscribe path
#   - any subpage other than bare domain or domain with query params
#
# We want to catch:
#   https://purebrain.ai/
#   https://purebrain.ai/?utm_source=blog&...
#   https://purebrain.ai/?utm_source=blog&...  (any variant)
# And NOT catch:
#   https://purebrain.ai/blog/
#   https://purebrain.ai/blog-post-slug/
#   newsletter links

# Pattern: href to purebrain.ai root (with optional query params), no path after domain
CTA_HREF_PATTERN = re.compile(
    r'href=["\']'
    r'(https?://purebrain\.ai/?)([^"\'\s#]*)'  # group 1 = base+slash, group 2 = query string
    r'(?:#[^"\'\s]*)?'  # optional existing fragment (we'll replace it)
    r'["\']',
    re.IGNORECASE
)

# Patterns that identify a link as a CTA (text near the href in ~200 chars of context)
CTA_TEXT_SIGNALS = [
    "Start Your AI Partnership",
    "start your ai partnership",
    "blog-cta-block",
    "blog-cta-button",
]

# Links to never touch
SAFE_HREF_SIGNALS = [
    "/blog",
    "subscribe",
    "/newsletter",
    "linkedin.com",
    "twitter.com",
    "facebook.com",
]

# Any link that goes to a subpage of purebrain.ai (not the root) — skip it
SUBPAGE_PATTERN = re.compile(
    r'https?://purebrain\.ai/(?!(?:\?|#|$))',  # has a path segment after the /
    re.IGNORECASE
)


def is_cta_link(href: str, surrounding_context: str) -> bool:
    """
    Returns True if this href is a CTA "Start Your AI Partnership" link.

    Detection approach:
    1. Must point to purebrain.ai root (no subpage paths)
    2. Check surrounding 300 chars for CTA text signals
    3. Skip if any SAFE_HREF_SIGNALS present in the href
    """
    # Must be a purebrain.ai link
    if 'purebrain.ai' not in href.lower():
        return False

    # Skip if it goes to a subpage (has path segment after the slash)
    if SUBPAGE_PATTERN.search(href):
        return False

    # Skip known safe/non-CTA links
    for signal in SAFE_HREF_SIGNALS:
        if signal in href.lower():
            return False

    # Check for CTA text signals in the surrounding context
    context_lower = surrounding_context.lower()
    for signal in CTA_TEXT_SIGNALS:
        if signal.lower() in context_lower:
            return True

    return False


def build_clean_href(href: str) -> str:
    """
    Clean version: strip fragment, ensure trailing / on bare domain, append #awakening.

    Examples:
      https://purebrain.ai/  -> https://purebrain.ai/#awakening
      https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content=slug
        -> https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content=slug#awakening
    """
    # Strip any existing fragment
    if '#' in href:
        href = href[:href.index('#')]

    # Ensure bare domain has trailing slash
    # https://purebrain.ai -> https://purebrain.ai/
    base_no_path = re.match(r'^(https?://purebrain\.ai)$', href, re.IGNORECASE)
    if base_no_path:
        href = href + '/'

    # Append fragment
    return href + '#awakening'


def fix_content_add_awakening(content: str) -> tuple:
    """
    Scan content for CTA links to purebrain.ai and add #awakening fragment.
    Returns (updated_content, list_of_changes).
    """
    changes = []

    # We need to find href="..." values with their surrounding context
    # Strategy: iterate through all href matches, check context window, replace if CTA

    result_parts = []
    last_end = 0

    # Find every href="..." in the content
    for m in re.finditer(r'href=["\']([^"\']+)["\']', content):
        href_full = m.group(0)   # e.g. href="https://purebrain.ai/?utm_source=..."
        href_val = m.group(1)    # e.g. https://purebrain.ai/?utm_source=...

        # Get surrounding context (300 chars before and after)
        ctx_start = max(0, m.start() - 300)
        ctx_end = min(len(content), m.end() + 300)
        context = content[ctx_start:ctx_end]

        # Check if this is a CTA link
        if not is_cta_link(href_val, context):
            continue

        # Already has #awakening — skip
        if '#awakening' in href_val:
            continue

        # Build new href
        new_href_val = build_clean_href(href_val)
        quote_char = href_full[5]  # the quote character after href=
        new_href_full = f'href={quote_char}{new_href_val}{quote_char}'

        # Record the change
        changes.append({
            "old": href_val,
            "new": new_href_val,
        })

        # Accumulate replacement
        result_parts.append(content[last_end:m.start()])
        result_parts.append(new_href_full)
        last_end = m.end()

    # Append remaining content
    result_parts.append(content[last_end:])
    updated = ''.join(result_parts)

    return updated, changes


def fetch_all_posts(base: str, auth: tuple) -> list:
    """Fetch all published posts across all pages."""
    posts = []
    page = 1
    while True:
        resp = requests.get(
            f"{base}/posts",
            params={
                "status": "publish",
                "per_page": 100,
                "page": page,
                "context": "edit",
            },
            auth=auth,
            timeout=30,
        )
        if resp.status_code == 400:
            # No more pages
            break
        if resp.status_code not in (200, 201):
            print(f"  ERROR fetching page {page}: {resp.status_code} - {resp.text[:200]}")
            break
        batch = resp.json()
        if not batch:
            break
        posts.extend(batch)
        print(f"  Fetched page {page}: {len(batch)} posts (total so far: {len(posts)})")
        if len(batch) < 100:
            break
        page += 1
        time.sleep(DELAY)
    return posts


def update_post(base: str, auth: tuple, post_id: int, updated_content: str) -> bool:
    """Update a post's content via WP REST API."""
    resp = requests.post(
        f"{base}/posts/{post_id}",
        auth=auth,
        json={"content": updated_content},
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        print(f"    ERROR updating post {post_id}: {resp.status_code} - {resp.text[:200]}")
    return resp.status_code in (200, 201)


def verify_post_has_awakening(base: str, auth: tuple, post_id: int, expected_count: int) -> tuple:
    """Re-fetch post and confirm #awakening fragment is present the expected number of times."""
    time.sleep(1)
    resp = requests.get(
        f"{base}/posts/{post_id}?context=edit",
        auth=auth,
        timeout=30,
    )
    if resp.status_code != 200:
        return False, f"HTTP {resp.status_code}"
    content = resp.json().get("content", {}).get("raw", "")
    actual_count = content.count('#awakening')
    if actual_count >= expected_count:
        return True, f"Found {actual_count} #awakening occurrence(s)"
    return False, f"Expected >={expected_count} #awakening, found {actual_count}"


def process_site(site: dict) -> dict:
    name = site["name"]
    base = site["base"]
    auth = site["auth"]

    print(f"\n{'='*60}")
    print(f"PROCESSING: {name}")
    print(f"{'='*60}")

    results = {
        "site": name,
        "posts_checked": 0,
        "posts_changed": 0,
        "posts_verified": 0,
        "changes": [],
        "errors": [],
    }

    posts = fetch_all_posts(base, auth)
    results["posts_checked"] = len(posts)
    print(f"  Total posts fetched: {len(posts)}")

    for post in posts:
        pid = post["id"]
        title = post.get("title", {}).get("rendered", f"Post {pid}")
        slug = post.get("slug", str(pid))
        raw_content = post.get("content", {}).get("raw", "")

        # Quick pre-check: does post contain any purebrain.ai link at all?
        if 'purebrain.ai' not in raw_content.lower():
            continue

        # Try to fix content
        updated_content, changes = fix_content_add_awakening(raw_content)

        if not changes:
            # No CTA links found, or all already have #awakening
            awakening_count = raw_content.count('#awakening')
            if awakening_count > 0:
                print(f"  [POST {pid}] '{title}' — already has #awakening ({awakening_count}x), skipping")
            else:
                # Has purebrain.ai link but it's not a CTA (e.g., in-content mention)
                pass
            continue

        print(f"\n  [POST {pid}] '{title}' (slug: {slug})")
        print(f"    Found {len(changes)} CTA link(s) to update:")
        for c in changes:
            print(f"      OLD: {c['old']}")
            print(f"      NEW: {c['new']}")

        # Update via REST API
        success = update_post(base, auth, pid, updated_content)
        if not success:
            err = f"Post {pid}: Update API call failed"
            results["errors"].append(err)
            time.sleep(DELAY)
            continue

        # Verify
        verified, verify_msg = verify_post_has_awakening(base, auth, pid, len(changes))
        status = "VERIFIED" if verified else "VERIFICATION FAILED"
        print(f"    Update result: {status} ({verify_msg})")

        results["posts_changed"] += 1
        if verified:
            results["posts_verified"] += 1
        else:
            results["errors"].append(f"Post {pid}: {verify_msg}")

        results["changes"].append({
            "post_id": pid,
            "post_title": title,
            "post_slug": slug,
            "changes_count": len(changes),
            "changes": changes,
            "verified": verified,
            "verify_msg": verify_msg,
        })

        time.sleep(DELAY)

    return results


def main():
    print("=" * 60)
    print("ADD #awakening FRAGMENT TO CTA LINKS")
    print("Targets: purebrain.ai + jareddsanborn.com")
    print("=" * 60)

    all_results = []

    for site in SITES:
        result = process_site(site)
        all_results.append(result)

    # ─── SUMMARY REPORT ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")

    total_changed = 0
    total_verified = 0
    total_errors = 0

    for r in all_results:
        print(f"\nSite: {r['site']}")
        print(f"  Posts checked:  {r['posts_checked']}")
        print(f"  Posts changed:  {r['posts_changed']}")
        print(f"  Posts verified: {r['posts_verified']}")
        print(f"  Errors:         {len(r['errors'])}")

        if r["changes"]:
            print("  Changed posts:")
            for c in r["changes"]:
                v = "VERIFIED" if c["verified"] else "NOT VERIFIED"
                print(f"    - [Post {c['post_id']}] {c['post_title']} — {c['changes_count']} link(s) — {v}")
                for ch in c["changes"]:
                    print(f"        OLD: {ch['old']}")
                    print(f"        NEW: {ch['new']}")

        if r["errors"]:
            print("  Errors:")
            for e in r["errors"]:
                print(f"    - {e}")

        total_changed += r["posts_changed"]
        total_verified += r["posts_verified"]
        total_errors += len(r["errors"])

    print(f"\nOVERALL:")
    print(f"  Total posts changed:  {total_changed}")
    print(f"  Total posts verified: {total_verified}")
    print(f"  Total errors:         {total_errors}")

    if total_errors == 0 and total_changed > 0:
        print("\nSUCCESS: All CTA links now include #awakening fragment.")
    elif total_changed == 0:
        print("\nNO CHANGES NEEDED: No CTA links missing #awakening found.")
    else:
        print(f"\nPARTIAL: {total_changed} changed, {total_errors} error(s). Review above.")

    # Save JSON report
    report_path = "/home/jared/projects/AI-CIV/aether/exports/cta-awakening-fix-report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDetailed report saved: {report_path}")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
