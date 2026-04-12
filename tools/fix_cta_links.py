#!/usr/bin/env python3
"""
Fix CTA button links across both WordPress sites.
Replaces any test page links (purebrain-4, purebrain-3, pay-test) with
the correct homepage URL with UTM parameters.

Sites:
  - purebrain.ai (auth: Aether / PUREBRAIN_WP_APP_PASSWORD)
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
    },
    {
        "name": "jareddsanborn.com",
        "base": "https://jareddsanborn.com/wp-json/wp/v2",
        "auth": ("jared", os.getenv("WORDPRESS_APP_PASSWORD", "").strip("'")),
    },
]

# Patterns that indicate a test-page link inside a CTA context.
# We look for href values pointing to these pages.
BAD_HREF_PATTERNS = [
    r'https?://(?:purebrain\.ai)?/purebrain-4/?',
    r'https?://(?:purebrain\.ai)?/purebrain-3/?',
    r'https?://(?:purebrain\.ai)?/pay-test/?',
    r'https?://(?:purebrain\.ai)?/purebrain-20/?',
    # relative versions
    r'(?<!["\w])/purebrain-4/?(?=["\s>?])',
    r'(?<!["\w])/purebrain-3/?(?=["\s>?])',
    r'(?<!["\w])/pay-test/?(?=["\s>?])',
    r'(?<!["\w])/purebrain-20/?(?=["\s>?])',
]

# Safe links — do NOT touch these even if they look like CTAs
SAFE_HREF_PATTERNS = [
    r'/blog',
    r'subscribe',
    r'/newsletter',
]

DELAY = 2  # seconds between API calls


def get_slug_from_content(content: str, post_id: int) -> str:
    """Extract slug hint from content or fall back to post ID."""
    # Look for blog-cta-block UTM content parameter
    m = re.search(r'utm_content=([^&"\']+)', content)
    if m:
        return m.group(1)
    return str(post_id)


def build_replacement_url(slug: str) -> str:
    return (
        f"https://purebrain.ai/"
        f"?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership"
        f"&utm_content={slug}"
    )


def find_bad_hrefs(content: str) -> list:
    """Return list of (full_href_attr_value, matched_bad_url) for CTA links."""
    found = []
    # Find all href="..." in the content
    for m in re.finditer(r'href=["\']([^"\']+)["\']', content):
        url = m.group(1)
        for pat in BAD_HREF_PATTERNS:
            if re.search(pat, url):
                found.append((m.group(0), url))
                break
    return found


def fix_content(content: str, slug: str) -> tuple[str, list]:
    """
    Replace bad CTA hrefs with the correct homepage URL.
    Returns (updated_content, list_of_changes).
    Do NOT touch /blog/ links or newsletter links.
    """
    changes = []
    replacement_url = build_replacement_url(slug)

    def replace_href(m):
        full = m.group(0)  # e.g. href="https://purebrain.ai/purebrain-4/"
        url = m.group(1)

        # Skip safe links
        for safe in SAFE_HREF_PATTERNS:
            if re.search(safe, url):
                return full

        # Check if this is a bad link
        is_bad = False
        for pat in BAD_HREF_PATTERNS:
            if re.search(pat, url):
                is_bad = True
                break

        if is_bad:
            new_full = f'href="{replacement_url}"'
            changes.append({
                "old": url,
                "new": replacement_url,
                "context": full,
            })
            return new_full

        return full

    updated = re.sub(r'href=["\']([^"\']+)["\']', replace_href, content)
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
        if resp.status_code != 200:
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
    return resp.status_code in (200, 201)


def verify_post(base: str, auth: tuple, post_id: int, bad_patterns: list) -> bool:
    """Re-fetch post and confirm no bad links remain."""
    time.sleep(1)
    resp = requests.get(
        f"{base}/posts/{post_id}?context=edit",
        auth=auth,
        timeout=30,
    )
    if resp.status_code != 200:
        return False
    content = resp.json().get("content", {}).get("raw", "")
    for pat in bad_patterns:
        if re.search(pat, content):
            return False
    return True


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
        raw_content = post.get("content", {}).get("raw", "")

        # Quick check — skip posts with no bad links at all
        has_bad = False
        for pat in BAD_HREF_PATTERNS:
            if re.search(pat, raw_content):
                has_bad = True
                break

        if not has_bad:
            continue

        print(f"\n  [POST {pid}] '{title}'")
        bad_hrefs = find_bad_hrefs(raw_content)
        print(f"    Found {len(bad_hrefs)} bad href(s):")
        for full, url in bad_hrefs:
            print(f"      - {url}")

        # Get or derive slug
        slug = get_slug_from_content(raw_content, pid)
        # Try to get the actual post slug from the API response
        post_slug = post.get("slug", "")
        if post_slug:
            slug = post_slug

        updated_content, changes = fix_content(raw_content, slug)

        if not changes:
            print(f"    No changes made (all bad links were safe/exempt).")
            continue

        print(f"    Replacing {len(changes)} link(s):")
        for c in changes:
            print(f"      OLD: {c['old']}")
            print(f"      NEW: {c['new']}")

        # Update via REST API
        success = update_post(base, auth, pid, updated_content)
        if not success:
            err = f"Post {pid}: Update API call failed"
            print(f"    ERROR: {err}")
            results["errors"].append(err)
            time.sleep(DELAY)
            continue

        # Verify
        verified = verify_post(base, auth, pid, BAD_HREF_PATTERNS)
        status = "VERIFIED" if verified else "VERIFICATION FAILED"
        print(f"    Update result: {status}")

        results["posts_changed"] += 1
        if verified:
            results["posts_verified"] += 1
        else:
            results["errors"].append(f"Post {pid}: Verification failed after update")

        results["changes"].append({
            "post_id": pid,
            "post_title": title,
            "post_slug": slug,
            "changes": changes,
            "verified": verified,
        })

        time.sleep(DELAY)

    return results


def main():
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
                print(f"    - [{c['post_id']}] {c['post_title']} ({c['post_slug']}) — {v}")
                for ch in c["changes"]:
                    print(f"        {ch['old']} -> {ch['new']}")

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
        print("\nSUCCESS: All bad CTA links replaced and verified.")
    elif total_changed == 0:
        print("\nNO CHANGES NEEDED: No bad CTA links found across any posts.")
    else:
        print(f"\nPARTIAL: {total_changed} changed, {total_errors} error(s). Review above.")

    # Save JSON report
    report_path = "/home/jared/projects/AI-CIV/aether/exports/cta-link-fix-report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDetailed report saved: {report_path}")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
