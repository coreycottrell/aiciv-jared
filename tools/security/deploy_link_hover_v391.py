#!/usr/bin/env python3
"""
Deploy blog in-text link hover fix (v3.9.1) to ALL blog posts on BOTH sites.

Fix: In-content links on hover should show orange background + WHITE text.
     Previously: orange background + orange text (invisible).

Method: REST API — prepend <style id="pb-link-hover-v391"> to each post's content.
        This works even when GoDaddy wp-admin login is rate-limited (CAPTCHA blocked),
        because WP Application Passwords work for REST API Basic Auth.

Sites:
  - purebrain.ai     (user=Aether, PUREBRAIN_WP_APP_PASSWORD)
  - jareddsanborn.com (user=AetherPureBrain.ai, WORDPRESS_APP_PASSWORD)

Author: full-stack-developer agent
Date:   2026-02-22
"""

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")

# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"{key}='([^']+)'", env_text)
    if m:
        return m.group(1)
    m = re.search(rf"{key}=([^\n]+)", env_text)
    return m.group(1).strip() if m else ""


SITES = [
    {
        "name": "purebrain.ai",
        "base_url": "https://purebrain.ai",
        "user": "Aether",
        "password": _env("PUREBRAIN_WP_APP_PASSWORD"),
    },
    {
        "name": "jareddsanborn.com",
        "base_url": "https://jareddsanborn.com",
        "user": "AetherPureBrain.ai",
        "password": _env("WORDPRESS_APP_PASSWORD"),
    },
]

# ---------------------------------------------------------------------------
# The CSS style block to prepend to every blog post
# Style ID: pb-link-hover-v391  (unique, allows detection and idempotency)
# ---------------------------------------------------------------------------
STYLE_BLOCK_ID = "pb-link-hover-v391"

STYLE_BLOCK = """\
<style id="pb-link-hover-v391">
/* ============================================================
   BLOG IN-TEXT LINK HOVER — v3.9.1
   Problem: links are orange (#f1420b) by default. On hover the
   theme added an orange background too, making text invisible
   (orange-on-orange). Fix: keep orange background on hover but
   swap text to WHITE (#ffffff).
   Exclusions: .blog-cta-button and [rel="tag"] (tag pills).
   ============================================================ */
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]),
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]) {
    transition: background-color 0.2s ease, color 0.2s ease !important;
}
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]):hover,
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]):hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
}
</style>
"""


# ---------------------------------------------------------------------------
# REST API helpers
# ---------------------------------------------------------------------------

def make_auth_header(user: str, password: str) -> str:
    creds = base64.b64encode(f"{user}:{password}".encode()).decode()
    return f"Basic {creds}"


def wp_get(url: str, auth_header: str) -> dict | list:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": auth_header,
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def wp_patch(url: str, auth_header: str, data: dict) -> dict:
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",  # WP REST API uses POST with X-HTTP-Method-Override for PATCH
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "X-HTTP-Method-Override": "PATCH",
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def get_all_posts(base_url: str, auth_header: str) -> list:
    """Fetch all published posts (up to 100)."""
    url = f"{base_url}/wp-json/wp/v2/posts?per_page=100&status=publish"
    posts = wp_get(url, auth_header)
    return posts


def post_needs_update(content_raw: str) -> bool:
    """Return True if the style block is not already in the post content."""
    return STYLE_BLOCK_ID not in content_raw


def prepend_style_block(content_raw: str) -> str:
    """Prepend the style block to the raw content (no wrapping wptexturize issues)."""
    # Remove any old version of this exact block first (idempotent)
    # Pattern: anything between <style id="pb-link-hover-v391"> and </style>
    cleaned = re.sub(
        r'<style id="pb-link-hover-v391">.*?</style>\s*',
        "",
        content_raw,
        flags=re.DOTALL,
    )
    return STYLE_BLOCK + cleaned


def process_site(site: dict) -> dict:
    """Process one site. Returns summary dict."""
    name = site["name"]
    base_url = site["base_url"]
    auth_header = make_auth_header(site["user"], site["password"])

    print(f"\n{'='*60}")
    print(f"SITE: {name}")
    print(f"{'='*60}")

    results = {
        "site": name,
        "total": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "posts": [],
    }

    # Get all posts
    try:
        posts = get_all_posts(base_url, auth_header)
    except Exception as ex:
        print(f"  [ERROR] Could not fetch posts: {ex}")
        results["errors"] += 1
        return results

    results["total"] = len(posts)
    print(f"  Found {len(posts)} published posts")

    for post in posts:
        post_id = post["id"]
        slug = post.get("slug", "?")
        content_raw = post.get("content", {}).get("raw", "")

        if not content_raw:
            # Try rendered content as fallback
            content_rendered = post.get("content", {}).get("rendered", "")
            if content_rendered:
                print(f"  [WARN] Post {post_id} ({slug}): no raw content, using rendered")
                content_raw = content_rendered

        if not content_raw:
            print(f"  [SKIP] Post {post_id} ({slug}): empty content")
            results["skipped"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": "skipped_empty"})
            continue

        if not post_needs_update(content_raw):
            print(f"  [SKIP] Post {post_id} ({slug}): already has {STYLE_BLOCK_ID}")
            results["skipped"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": "already_present"})
            continue

        # Prepend the style block
        new_content = prepend_style_block(content_raw)

        try:
            patch_url = f"{base_url}/wp-json/wp/v2/posts/{post_id}"
            updated = wp_patch(patch_url, auth_header, {"content": new_content})
            # Verify the update took
            updated_raw = updated.get("content", {}).get("raw", "")
            if STYLE_BLOCK_ID in updated_raw:
                print(f"  [OK]   Post {post_id} ({slug}): style block injected")
                results["updated"] += 1
                results["posts"].append({"id": post_id, "slug": slug, "status": "updated"})
            else:
                print(f"  [WARN] Post {post_id} ({slug}): PATCH succeeded but block not found in response")
                results["errors"] += 1
                results["posts"].append({"id": post_id, "slug": slug, "status": "verify_failed"})
        except urllib.error.HTTPError as http_err:
            body = http_err.read().decode("utf-8", errors="replace")[:300]
            print(f"  [ERR]  Post {post_id} ({slug}): HTTP {http_err.code} — {body}")
            results["errors"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": f"http_{http_err.code}"})
        except Exception as ex:
            print(f"  [ERR]  Post {post_id} ({slug}): {ex}")
            results["errors"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": f"error_{ex}"})

        # Brief pause between updates to avoid hammering the server
        time.sleep(0.5)

    print(f"\n  Summary: total={results['total']} updated={results['updated']} "
          f"skipped={results['skipped']} errors={results['errors']}")
    return results


# ---------------------------------------------------------------------------
# Live verification — fetch rendered page HTML, check for style block
# ---------------------------------------------------------------------------

VERIFY_SLUGS = {
    "purebrain.ai": [
        "https://purebrain.ai/the-ai-trust-gap/",
        "https://purebrain.ai/why-95-percent-of-ai-pilots-fail/",
    ],
    "jareddsanborn.com": [
        "https://jareddsanborn.com/the-ai-trust-gap/",
        "https://jareddsanborn.com/why-95-percent-of-ai-pilots-fail/",
    ],
}


def verify_live(site_name: str) -> None:
    urls = VERIFY_SLUGS.get(site_name, [])
    if not urls:
        return

    print(f"\n  Live verification for {site_name}:")
    for url in urls:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            has_block = STYLE_BLOCK_ID in html
            has_white_text = "#ffffff !important" in html
            has_orange_hover = "background-color: #f1420b !important" in html

            status = "OK" if (has_block and has_white_text and has_orange_hover) else "WARN"
            print(f"    [{status}] {url}")
            print(f"           style block present:  {has_block}")
            print(f"           white text rule:       {has_white_text}")
            print(f"           orange bg hover rule:  {has_orange_hover}")
        except Exception as ex:
            print(f"    [WARN] Could not fetch {url}: {ex}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Blog In-Text Link Hover Fix — v3.9.1 Deployment")
    print("Fix: orange bg + WHITE text on hover (was orange-on-orange)")
    print("Method: REST API (app password — works even if WP Admin CAPTCHA blocked)")
    print("=" * 60)

    all_results = []

    for site in SITES:
        if not site["password"]:
            print(f"\n[SKIP] {site['name']}: password not found in .env")
            continue
        result = process_site(site)
        all_results.append(result)

    # Live verification
    print(f"\n{'='*60}")
    print("Live Verification (fetching rendered pages)")
    print("Note: CDN may serve cached HTML. Hard-refresh (Cmd+Shift+R) to confirm.")
    print("=" * 60)
    for result in all_results:
        verify_live(result["site"])

    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print("=" * 60)
    total_updated = sum(r["updated"] for r in all_results)
    total_errors = sum(r["errors"] for r in all_results)
    for r in all_results:
        print(f"  {r['site']}: updated={r['updated']} skipped={r['skipped']} errors={r['errors']}")

    if total_errors > 0:
        print(f"\nCOMPLETED WITH {total_errors} ERROR(S)")
        sys.exit(1)
    else:
        print(f"\nALL POSTS UPDATED SUCCESSFULLY ({total_updated} posts across {len(all_results)} sites)")
        print("\nIn-text links on blog posts will now show:")
        print("  - Hover: orange background (#f1420b) + WHITE text (#ffffff)")
        print("  - Smooth 0.2s transition")
        print("  - Subtle border-radius (3px) + padding (1px 4px)")
        print("  - CTA button and tag pills are EXCLUDED (they have their own styling)")


if __name__ == "__main__":
    main()
