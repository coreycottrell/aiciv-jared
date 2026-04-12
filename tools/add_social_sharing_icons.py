#!/usr/bin/env python3
"""
Add social sharing icons to all published blog posts on purebrain.ai.

Injects a Pure Tech Blue branded social sharing bar (LinkedIn, Twitter/X,
Facebook, Email) below the main post content, above any existing CTA/footer.

Idempotency: Skips posts that already contain 'pt-social-share' class.
"""

import requests
import time
import json
from datetime import datetime

# --- Config ---
BASE_URL = "https://purebrain.ai/wp-json/wp/v2"
AUTH = ("Aether", "FlFr2VOtlHiHaJWjzW96OHUJ")
IDEMPOTENCY_MARKER = "pt-social-share"
RATE_LIMIT_SECONDS = 3

# --- Social Sharing HTML Template ---
# Uses window.location.href and document.title so it works on any post URL.
# javascript:void(0) onclick pattern opens a proper popup share window.
# SVG icons are inline so no external dependencies needed.
SOCIAL_SHARE_HTML = """\

<!-- Social Sharing Icons - Pure Tech Blue -->
<style>
.pt-social-share { display: flex; align-items: center; gap: 12px; padding: 20px 0; margin: 20px 0; border-top: 2px solid rgba(42, 147, 193, 0.3); flex-wrap: wrap; }
.pt-social-share span { font-weight: 600; color: #fff; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
.pt-social-share a { display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; background: rgba(42, 147, 193, 0.15); color: #2a93c1; text-decoration: none; transition: all 0.3s; font-size: 18px; }
.pt-social-share a:hover { background: #2a93c1; color: #fff; transform: scale(1.1); }
.pt-social-share a svg { width: 20px; height: 20px; fill: currentColor; }
</style>
<div class="pt-social-share">
<span>Share:</span>
<a href="javascript:void(0)" onclick="window.open('https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(window.location.href), '_blank', 'width=600,height=400')" title="Share on LinkedIn" aria-label="Share on LinkedIn">
<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://twitter.com/intent/tweet?url=' + encodeURIComponent(window.location.href) + '&amp;text=' + encodeURIComponent(document.title), '_blank', 'width=600,height=400')" title="Share on X" aria-label="Share on X">
<svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(window.location.href), '_blank', 'width=600,height=400')" title="Share on Facebook" aria-label="Share on Facebook">
<svg viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.location.href='mailto:?subject=' + encodeURIComponent(document.title) + '&amp;body=' + encodeURIComponent(window.location.href)" title="Share via Email" aria-label="Share via Email">
<svg viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
</a>
</div>"""


def fetch_all_posts():
    """Fetch all published posts with raw content."""
    print("Fetching all published posts...")
    resp = requests.get(
        f"{BASE_URL}/posts",
        auth=AUTH,
        params={
            "status": "publish",
            "per_page": 100,
            "page": 1,
            "context": "edit",  # Returns raw HTML content
        },
        timeout=30,
    )
    resp.raise_for_status()
    posts = resp.json()
    print(f"  Found {len(posts)} published posts")
    return posts


def inject_social_share(content: str) -> tuple[str, str]:
    """
    Inject the social sharing bar into post content.

    Placement strategy:
    1. If post has a 'blog-cta-block' div, insert BEFORE it (sharing before CTA).
    2. Otherwise append at the end of content.

    Returns (updated_content, placement_description).
    """
    cta_marker = '<div class="blog-cta-block"'

    if cta_marker in content:
        # Insert social share block just before the CTA block
        idx = content.index(cta_marker)
        updated = content[:idx] + SOCIAL_SHARE_HTML + "\n" + content[idx:]
        return updated, "before CTA block"
    else:
        # Append at end
        updated = content.rstrip() + "\n" + SOCIAL_SHARE_HTML
        return updated, "appended at end"


def update_post(post_id: int, new_content: str) -> bool:
    """Update a post's content via REST API. Returns True on success."""
    resp = requests.post(
        f"{BASE_URL}/posts/{post_id}",
        auth=AUTH,
        json={"content": new_content},
        timeout=30,
    )
    return resp.status_code in (200, 201)


def verify_post(post_id: int) -> dict:
    """Re-fetch a post and verify social share block is present."""
    resp = requests.get(
        f"{BASE_URL}/posts/{post_id}",
        auth=AUTH,
        params={"context": "edit"},
        timeout=30,
    )
    resp.raise_for_status()
    post = resp.json()
    content = post["content"]["raw"]
    return {
        "has_social_share": IDEMPOTENCY_MARKER in content,
        "title": post["title"]["rendered"],
        "link": post["link"],
    }


def main():
    print("=" * 60)
    print("PureBrain.ai - Social Sharing Icons Injector")
    print(f"Run time: {datetime.now().isoformat()}")
    print("=" * 60)

    posts = fetch_all_posts()

    results = []
    skipped = []
    failed = []

    for i, post in enumerate(posts):
        post_id = post["id"]
        title = post["title"]["rendered"]
        content = post["content"]["raw"]
        link = post.get("link", "")

        print(f"\n[{i+1}/{len(posts)}] Post ID {post_id}: {title[:60]}")

        # Idempotency check
        if IDEMPOTENCY_MARKER in content:
            print(f"  SKIP - social share already present")
            skipped.append({"id": post_id, "title": title})
            continue

        # Inject social sharing block
        updated_content, placement = inject_social_share(content)
        print(f"  Injecting social share ({placement})...")

        # Push update
        success = update_post(post_id, updated_content)
        if not success:
            print(f"  FAILED to update post {post_id}")
            failed.append({"id": post_id, "title": title})
        else:
            print(f"  Updated successfully")
            results.append({"id": post_id, "title": title, "placement": placement, "link": link})

        # Rate limiting
        if i < len(posts) - 1:
            time.sleep(RATE_LIMIT_SECONDS)

    # --- Verification ---
    print("\n" + "=" * 60)
    print("VERIFICATION - Re-fetching updated posts")
    print("=" * 60)

    # Verify first updated post in detail
    if results:
        first = results[0]
        print(f"\nVerifying post ID {first['id']}: {first['title'][:60]}")
        time.sleep(2)
        verification = verify_post(first["id"])
        print(f"  has_social_share: {verification['has_social_share']}")
        print(f"  link: {verification['link']}")

        if not verification["has_social_share"]:
            print("  VERIFICATION FAILED - social share marker not found!")
        else:
            print("  VERIFICATION PASSED")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Updated:  {len(results)} posts")
    print(f"Skipped (already done): {len(skipped)} posts")
    print(f"Failed:   {len(failed)} posts")

    if results:
        print("\nUpdated posts:")
        for r in results:
            print(f"  - [{r['id']}] {r['title'][:55]} ({r['placement']})")
            print(f"       {r['link']}")

    if skipped:
        print("\nSkipped posts (already had social share):")
        for s in skipped:
            print(f"  - [{s['id']}] {s['title'][:55]}")

    if failed:
        print("\nFailed posts:")
        for f in failed:
            print(f"  - [{f['id']}] {f['title'][:55]}")

    # Save report
    report = {
        "run_time": datetime.now().isoformat(),
        "updated": results,
        "skipped": skipped,
        "failed": failed,
    }
    report_path = "/home/jared/projects/AI-CIV/aether/exports/social-sharing-icons-report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: {report_path}")

    return len(failed) == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
