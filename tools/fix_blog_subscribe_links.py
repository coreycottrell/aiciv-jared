#!/usr/bin/env python3
"""
Fix blog subscribe links on purebrain.ai.

Problem 1: Inline styles on subscribe links override plugin hover CSS.
           Fixed via plugin JS (v2.8.0) AND by cleaning the stored content here.

Problem 2: Post 565 has wrong href (missing #neural-feed-subscribe).
           Fixed via REST API.

Author: full-stack-developer agent
Date: 2026-02-21
Version: 1.0.0
"""

import re
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")

WP_BASE     = "https://purebrain.ai"
WP_USER     = "Aether"
WP_APP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"

WP_AUTH = HTTPBasicAuth(WP_USER, WP_APP_PASS)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def wp_get_post(post_id: int) -> dict:
    """Get post with raw content (requires context=edit)."""
    url = f"{WP_BASE}/wp-json/wp/v2/posts/{post_id}"
    resp = requests.get(url, auth=WP_AUTH, params={"context": "edit", "_fields": "id,slug,content"}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def wp_update_post(post_id: int, payload: dict) -> dict:
    """Update a post via POST to /posts/{id} (WP REST API standard)."""
    url = f"{WP_BASE}/wp-json/wp/v2/posts/{post_id}"
    resp = requests.post(url, auth=WP_AUTH, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Inline style stripping
# ---------------------------------------------------------------------------
# Matches subscribe/newsletter/neural-feed anchor tags with style="" attribute.
# Captures everything before the style attr and after, so we can reassemble without it.
INLINE_STYLE_PATTERN = re.compile(
    r'(<a\s[^>]*href="[^"]*(?:subscribe|newsletter|neural-feed)[^"]*"[^>]*?)\s+style="[^"]*"([^>]*>)',
    re.IGNORECASE | re.DOTALL,
)


def strip_inline_styles_from_content(content: str) -> str:
    """Remove style= attribute from subscribe/newsletter/neural-feed link tags."""
    return INLINE_STYLE_PATTERN.sub(r'\1\2', content)


def count_styled_links(content: str) -> int:
    return len(INLINE_STYLE_PATTERN.findall(content))


# ---------------------------------------------------------------------------
# Fix 1: Post 565 wrong href + strip inline styles
# ---------------------------------------------------------------------------
def fix_post_565():
    print("\n[Fix 1] Post 565 - fix wrong href AND strip inline styles")
    print("  Getting content...")

    post    = wp_get_post(565)
    slug    = post["slug"]
    content = post["content"]["raw"]
    print(f"  Slug: {slug}")
    print(f"  Content length: {len(content)} chars")

    # The wrong href (purebrain.ai/blog/? without #neural-feed-subscribe)
    old_href = (
        "https://purebrain.ai/blog/?utm_source=blog"
        "&utm_medium=cta&utm_campaign=newsletter"
        "&utm_content=the-difference-between-using-ai-and-having-an-ai-partner"
    )
    new_href = (
        "https://purebrain.ai/blog/#neural-feed-subscribe"
        "?utm_source=blog&utm_medium=cta&utm_campaign=newsletter"
        "&utm_content=the-difference-between-using-ai-and-having-an-ai-partner"
    )

    href_changed = False
    if old_href in content:
        print(f"  Replacing href:")
        print(f"    OLD: {old_href}")
        print(f"    NEW: {new_href}")
        content = content.replace(old_href, new_href, 1)
        href_changed = True
    elif new_href in content:
        print(f"  Href already correct - no href change needed.")
        href_changed = True  # Already correct, count as OK
    else:
        print("  WARNING: Neither old nor new href found in content!")

    # Strip inline styles
    styled_count = count_styled_links(content)
    if styled_count > 0:
        print(f"  Stripping {styled_count} inline style(s) from subscribe links...")
        content = strip_inline_styles_from_content(content)
        remaining = count_styled_links(content)
        print(f"  Remaining after strip: {remaining}")
    else:
        print("  No inline styles to strip.")

    # Save if anything changed
    print("  Saving via REST API...")
    result = wp_update_post(565, {"content": content})
    print(f"  Saved. Slug: {result.get('slug', '?')}")

    # Verify via fresh GET
    print("  Verifying...")
    verify = wp_get_post(565)
    v_content = verify["content"]["raw"]
    href_ok  = new_href in v_content and old_href not in v_content
    style_ok = count_styled_links(v_content) == 0
    print(f"  Href correct: {href_ok}")
    print(f"  No inline styles: {style_ok}")

    return href_ok and style_ok


# ---------------------------------------------------------------------------
# Fix 2: Strip inline styles from all other posts
# ---------------------------------------------------------------------------
def fix_all_posts_inline_styles():
    """Strip inline styles from subscribe links in all blog posts (except 565, done above)."""
    # All known post IDs with subscribe links (excluding 565 already handled)
    post_ids = [480, 381, 316, 373, 172, 98]
    print(f"\n[Fix 2] Strip inline styles from {len(post_ids)} remaining posts")

    results = {}
    for post_id in post_ids:
        print(f"\n  Post {post_id}...")
        try:
            post    = wp_get_post(post_id)
            slug    = post["slug"]
            content = post["content"]["raw"]

            styled = count_styled_links(content)
            if styled == 0:
                print(f"    [{slug}] Already clean - no inline styles.")
                results[post_id] = "already_clean"
                continue

            print(f"    [{slug}] Found {styled} inline style(s). Stripping...")
            new_content = strip_inline_styles_from_content(content)
            remaining = count_styled_links(new_content)
            if remaining > 0:
                print(f"    ERROR: {remaining} inline style(s) still present after strip!")
                results[post_id] = "error"
                continue

            r = wp_update_post(post_id, {"content": new_content})
            print(f"    Saved (slug: {r.get('slug', '?')})")

            # Verify
            v = wp_get_post(post_id)
            v_count = count_styled_links(v["content"]["raw"])
            if v_count == 0:
                print(f"    Verified clean.")
                results[post_id] = "fixed"
            else:
                print(f"    WARNING: {v_count} style(s) still in stored content after save!")
                results[post_id] = "warning"

        except Exception as e:
            print(f"    ERROR: {e}")
            results[post_id] = f"error: {e}"

    return results


# ---------------------------------------------------------------------------
# Verification: check live HTML
# ---------------------------------------------------------------------------
def verify_live():
    print("\n[Verification] Checking live rendered HTML...")
    posts_to_check = [
        ("the-difference-between-using-ai-and-having-an-ai-partner", "#neural-feed-subscribe"),
        ("why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time", "neural-feed-subscribe"),
        ("ceo-vs-employee-ai-transformation-gap", "neural-feed-subscribe"),
    ]

    all_ok = True
    for slug, check in posts_to_check:
        url = f"{WP_BASE}/{slug}/"
        try:
            resp = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                },
                timeout=30,
                allow_redirects=True,
            )
            html = resp.text
            found = check in html
            status = "OK" if found else "MISSING"
            print(f"  [{status}] {slug}: {check!r}")
            if not found:
                all_ok = False
        except Exception as e:
            print(f"  [ERROR] {slug}: {e}")
            all_ok = False

    # Also check plugin v2.8.0 JS is present
    url = f"{WP_BASE}/ceo-vs-employee-ai-transformation-gap/"
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}, timeout=30)
        html = resp.text
        has_strip_js = "purebrain-strip-newsletter-inline-styles" in html
        has_v280     = "2.8.0" in html
        print(f"  [{'OK' if has_strip_js else 'MISSING'}] Plugin strip-inline-styles JS block")
        print(f"  [{'OK' if has_v280 else 'MISSING'}] Plugin v2.8.0 version reference")
        if not has_strip_js or not has_v280:
            all_ok = False
    except Exception as e:
        print(f"  [ERROR] Plugin check: {e}")
        all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("PUREBRAIN BLOG SUBSCRIBE LINK FIXER v1.0")
    print("Fix 1: Post 565 href missing #neural-feed-subscribe")
    print("Fix 2: Strip inline styles from all subscribe links")
    print("=" * 65)

    # Fix 1: post 565 (href + inline styles)
    post565_ok = fix_post_565()

    # Fix 2: all other posts (inline styles only)
    other_results = fix_all_posts_inline_styles()

    # Summary
    print("\n" + "=" * 65)
    print("CONTENT FIX SUMMARY")
    print("=" * 65)
    print(f"  Post 565 (href + styles): {'OK' if post565_ok else 'FAILED'}")
    for pid, status in other_results.items():
        icon = "OK" if status in ("fixed", "already_clean") else "FAIL"
        print(f"  Post {pid} (styles): [{icon}] {status}")

    all_content_ok = post565_ok and all(
        v in ("fixed", "already_clean") for v in other_results.values()
    )

    if all_content_ok:
        print("\n[SUCCESS] All content fixes applied successfully.")
        print("\nNote: Live HTML verification requires plugin v2.8.0 to be deployed first.")
        print("      Run the deploy script next, then verify.")
    else:
        print("\n[FAILED] Some fixes did not apply. Review above.")
        sys.exit(1)
