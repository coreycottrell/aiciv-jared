#!/usr/bin/env python3
import sys as _sys
_sys.stderr.write("RETIRED 2026-06-07 P0 disarm — pushes dead exports/cf-pages-deploy mirror (stale $149/$499/$999) to live. Canonical deploy = github:puretechnyc/purebrain-site.\n")
_sys.exit(1)
# === RETIRED 2026-06-07 (P0 revenue-integrity disarm, Decision-2 Jared-GO).
# The guard above fires before any import/deploy. This script ran
# `npx wrangler pages deploy .` from exports/cf-pages-deploy (the dead mirror
# holding stale $149/$499/$999 prices). Reversible: delete the three _sys lines. ===
"""
CF Pages Blog Fix v2.0 — Static file edition.

Since purebrain.ai is served by Cloudflare Pages (not WordPress directly),
all fixes go to the static HTML files in exports/cf-pages-deploy/.

Task 1: Fix blog listing page banner images.
  - /blog-neural-feed-memories/index.html
  - Replace JS-driven card grid with static HTML that has hardcoded banner img tags.

Task 2: Fix blog post formatting (12 posts).
  - Wrap the post content in <article class="pb-blog-post"> for CSS scoping.
  - These older posts were published before the wrapper pattern was established.

Deploy: wrangler pages deploy
Author: dept-systems-technology / full-stack-developer
Date: 2026-03-13
"""

import re
import sys
import subprocess
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
CF_DEPLOY_ROOT = AETHER_ROOT / "exports/cf-pages-deploy"
BLOG_LISTING_FILE = CF_DEPLOY_ROOT / "blog-neural-feed-memories/index.html"
BLOG_DIR = CF_DEPLOY_ROOT / "blog"

# ---------------------------------------------------------------------------
# Image URL Map - Banner images for all 25 blog posts
# ---------------------------------------------------------------------------

SLUG_TO_IMAGE = {
    "your-ai-has-no-idea-who-you-are": "https://purebrain.ai/blog/your-ai-has-no-idea-who-you-are/banner.png",
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": "https://purebrain.ai/wp-content/uploads/2026/02/ai-competence-divide-banner.png",
    "your-ai-resets-to-zero-every-morning": "https://purebrain.ai/wp-content/uploads/2026/03/your-ai-resets-to-zero-every-morning-banner.png",
    "age-of-ai-agents-next-18-months": "https://purebrain.ai/wp-content/uploads/2026/03/age-of-ai-agents-banner.png",
    "teach-your-ai-something-no-one-else-can": "https://purebrain.ai/wp-content/uploads/2026/03/teach-your-ai-banner-jared-approved.jpg",
    "52-billion-ai-agents-market-is-not-the-story": "https://purebrain.ai/wp-content/uploads/2026/03/52-billion-ai-agents-market-banner.jpg",
    "something-big-already-happened-you-just-werent-invited-yet": "https://purebrain.ai/wp-content/uploads/2026/03/something-big-already-happened-banner.png",
    "the-ai-that-forgets-you-every-single-time": "https://purebrain.ai/wp-content/uploads/2026/03/the-ai-that-forgets-you-banner.png",
    "why-95-percent-of-ai-pilots-fail": "https://purebrain.ai/wp-content/uploads/2026/02/why-your-ai-pilot-is-failing-banner.png",
    "the-age-of-ai-agents": "https://purebrain.ai/wp-content/uploads/2026/03/the-age-of-ai-agents-banner.png",
    "your-ai-doesnt-work-for-you": "https://purebrain.ai/wp-content/uploads/2026/03/your-ai-doesnt-work-for-you-blog-post.png",
    "the-context-tax": "https://purebrain.ai/wp-content/uploads/2026/03/the-context-tax-banner.jpg",
    "the-first-90-days-of-an-ai-partnership": "https://purebrain.ai/wp-content/uploads/2026/02/the-first-90-days-of-an-ai-partnership-banner.png",
    "your-ai-has-no-memory-mine-does": "https://purebrain.ai/wp-content/uploads/2026/02/your-ai-has-no-memory-mine-does-banner.jpg",
    "your-next-direct-report-wont-be-human": "https://purebrain.ai/wp-content/uploads/2026/02/your-next-direct-report-wont-be-human-banner.jpg",
    "why-ai-memory-changes-everything": "https://purebrain.ai/wp-content/uploads/2026/02/why-ai-memory-changes-everything-banner.png",
    "we-both-wrote-this-post": "https://purebrain.ai/wp-content/uploads/2026/02/origin-story-blog-banner.png",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": "https://purebrain.ai/wp-content/uploads/2026/02/why-your-ai-pilot-is-failing-banner.png",
    "the-ai-trust-gap": "https://purebrain.ai/wp-content/uploads/2026/02/trust-gap-blog-banner.png",
    "how-my-human-named-me-and-what-it-meant": "https://purebrain.ai/wp-content/uploads/2026/02/how-my-human-named-me.png",
    "the-difference-between-using-ai-and-having-an-ai-partner": "https://purebrain.ai/wp-content/uploads/2026/02/the-difference-using-ai-partner.png",
    "what-i-actually-do-all-day": "https://purebrain.ai/wp-content/uploads/2026/02/origin-story-blog-banner.png",
    "ceo-vs-employee-ai-transformation-gap": "https://purebrain.ai/wp-content/uploads/2026/02/ceo-vs-employee-ai-lens-banner.png",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": "https://purebrain.ai/wp-content/uploads/2026/02/why-your-ai-pilot-is-failing-banner.png",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2": "https://purebrain.ai/wp-content/uploads/2026/02/ai-competence-divide-banner.png",
}

# Card data for blog listing page (slug, date, title)
CARD_DATA = [
    ("your-ai-has-no-idea-who-you-are", "March 12, 2026", "Your AI Has No Idea Who You Are"),
    ("ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger", "March 11, 2026", "AI Doesn\u2019t Make Your Team Smarter. It Makes the Gap Bigger."),
    ("your-ai-resets-to-zero-every-morning", "March 9, 2026", "Your AI Resets to Zero Every Morning (And It\u2019s Costing You More Than You Think)"),
    ("age-of-ai-agents-next-18-months", "March 8, 2026", "The Age of AI Agents: Why the Next 18 Months Will Decide the Next 18 Years"),
    ("teach-your-ai-something-no-one-else-can", "March 7, 2026", "Teach Your AI Something No One Else Can"),
    ("52-billion-ai-agents-market-is-not-the-story", "March 6, 2026", "$52 Billion AI Agents Market Is Not the Story"),
    ("something-big-already-happened-you-just-werent-invited-yet", "March 4, 2026", "Something Big Already Happened. You Just Weren\u2019t Invited Yet."),
    ("the-ai-that-forgets-you-every-single-time", "March 3, 2026", "The AI That Forgets You Every Single Time"),
    ("why-95-percent-of-ai-pilots-fail", "March 2, 2026", "Pilot Purgatory: Why 95% of AI Projects Die Before Delivering Value"),
    ("the-age-of-ai-agents", "March 1, 2026", "The Age of AI Agents"),
    ("your-ai-doesnt-work-for-you", "March 1, 2026", "Your AI Doesn\u2019t Work for You"),
    ("the-context-tax", "February 28, 2026", "The Context Tax"),
    ("the-first-90-days-of-an-ai-partnership", "February 26, 2026", "The First 90 Days of an AI Partnership"),
    ("your-ai-has-no-memory-mine-does", "February 25, 2026", "Your AI Has No Memory. Mine Does."),
    ("your-next-direct-report-wont-be-human", "February 24, 2026", "Your Next Direct Report Won\u2019t Be Human"),
    ("why-ai-memory-changes-everything", "February 23, 2026", "Why AI Memory Changes Everything"),
    ("we-both-wrote-this-post", "February 22, 2026", "We Both Wrote This Post"),
    ("why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time", "February 21, 2026", "Why Your AI Pilot Is Succeeding and Failing at the Same Time"),
    ("the-ai-trust-gap", "February 21, 2026", "The AI Trust Gap"),
    ("how-my-human-named-me-and-what-it-meant", "February 20, 2026", "How My Human Named Me (And What It Meant)"),
    ("the-difference-between-using-ai-and-having-an-ai-partner", "February 20, 2026", "The Difference Between Using AI and Having an AI Partner"),
    ("what-i-actually-do-all-day", "February 20, 2026", "What I Actually Do All Day"),
    ("ceo-vs-employee-ai-transformation-gap", "February 20, 2026", "Your CEO Sees AI Differently Than Your Team Does. That Gap Is Costing You Both."),
    ("pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value", "February 21, 2026", "Pilot Purgatory: Why 95% of AI Projects Die Before Delivering Value"),
    ("most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2", "February 19, 2026", "Most AI Agents Break the Moment You Ask Where the Data Goes"),
]

# The 12 bad posts missing <article class="pb-blog-post"> wrapper
BAD_POSTS = [
    "why-95-percent-of-ai-pilots-fail",
    "your-next-direct-report-wont-be-human",
    "why-ai-memory-changes-everything",
    "we-both-wrote-this-post",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time",
    "the-ai-trust-gap",
    "how-my-human-named-me-and-what-it-meant",
    "the-difference-between-using-ai-and-having-an-ai-partner",
    "what-i-actually-do-all-day",
    "ceo-vs-employee-ai-transformation-gap",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2",
]


# ---------------------------------------------------------------------------
# Task 1: Build static card HTML and update blog listing page
# ---------------------------------------------------------------------------

def build_static_card(slug, date, title):
    """Build a blog card with hardcoded banner image."""
    img_url = SLUG_TO_IMAGE.get(slug, "")
    safe_title = title.replace('"', '&quot;')

    if img_url:
        image_html = (
            f'<div class="nfm-card-image-wrap">'
            f'<img src="{img_url}" alt="{safe_title}" loading="lazy" decoding="async">'
            f'</div>'
        )
    else:
        image_html = (
            '<div class="nfm-card-image-wrap">'
            '<div class="nfm-card-image-placeholder">'
            '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" '
            'stroke="rgba(42,147,193,0.4)" stroke-width="1.5">'
            '<rect x="3" y="3" width="18" height="18" rx="2"/>'
            '<path d="M3 9l4-4 4 4 4-4 4 4"/>'
            '<circle cx="8.5" cy="13.5" r="1.5"/>'
            '</svg>'
            '</div>'
            '</div>'
        )

    return (
        f'\n            <a href="/blog/{slug}/" class="nfm-card" aria-label="Read: {safe_title}">\n'
        f'                {image_html}\n'
        f'                <div class="nfm-card-body">\n'
        f'                    <div class="nfm-card-date">{date}</div>\n'
        f'                    <div class="nfm-card-title">{title}</div>\n'
        f'                    <span class="nfm-card-cta">Read More</span>\n'
        f'                </div>\n'
        f'            </a>'
    )


def fix_blog_listing_page():
    """Replace broken JS-driven card grid with static HTML."""
    print("\n[Task 1] Fixing blog listing page banners...")

    html = BLOG_LISTING_FILE.read_text(encoding="utf-8")
    original_len = len(html)
    print(f"  Original HTML length: {original_len}")

    count = len(CARD_DATA)
    badge_text = f"{count} Transmissions in The Archive"

    # Build new static card list
    cards_html = "".join(build_static_card(slug, date, title) for slug, date, title in CARD_DATA)

    new_grid = (
        f'<span id="nfm-count-badge" class="nfm-count-badge" style="display:inline-block;">'
        f'{badge_text}</span>\n\n'
        f'<div id="nfm-grid" class="nfm-grid" style="display:grid;">'
        f'{cards_html}\n'
        f'        </div>'
    )

    # Strategy: find and replace the section containing the dynamic grid.
    # The section starts with a <span id="nfm-count-badge"> tag (or the nfm-loading div)
    # and ends with the closing </div> of nfm-grid.

    # First: find the nfm-loading div (appears before/around the grid)
    nfm_loading_idx = html.find('<div id="nfm-loading"')
    nfm_grid_idx = html.find('<div id="nfm-grid"')
    nfm_badge_idx = html.find('<span id="nfm-count-badge"')

    print(f"  nfm-loading at: {nfm_loading_idx}")
    print(f"  nfm-grid at: {nfm_grid_idx}")
    print(f"  nfm-badge at: {nfm_badge_idx}")

    if nfm_grid_idx < 0:
        print("  ERROR: Could not find nfm-grid div in listing page")
        return False

    # Determine replacement start: use nfm-badge if before nfm-grid, otherwise nfm-grid
    replace_start = nfm_badge_idx if (0 <= nfm_badge_idx < nfm_grid_idx) else nfm_grid_idx

    # Find the end of the nfm-grid div (count nested divs)
    pos = nfm_grid_idx
    depth = 0
    end_pos = -1
    while pos < len(html):
        if html[pos:pos+4] == '<div':
            depth += 1
        elif html[pos:pos+6] == '</div>':
            depth -= 1
            if depth == 0:
                end_pos = pos + 6  # include the </div>
                break
        pos += 1

    if end_pos < 0:
        print("  ERROR: Could not find end of nfm-grid div")
        return False

    print(f"  Replace range: {replace_start} to {end_pos}")

    new_html = html[:replace_start] + new_grid + html[end_pos:]

    # Verify the new content has images
    img_count = new_html.count('<img src=')
    placeholder_count = new_html.count('nfm-card-image-placeholder')
    print(f"  Images in new HTML: {img_count}")
    print(f"  Placeholders in new HTML: {placeholder_count}")

    if img_count < 20:  # Should have ~25 images
        print(f"  WARNING: Only {img_count} images found. Expected ~25.")

    # Write the updated file
    BLOG_LISTING_FILE.write_text(new_html, encoding="utf-8")
    print(f"  Written: {BLOG_LISTING_FILE}")
    print(f"  New length: {len(new_html)}")
    return True


# ---------------------------------------------------------------------------
# Task 2: Add pb-blog-post wrapper to bad blog posts
# ---------------------------------------------------------------------------

# CSS for pb-blog-post (minimal - just ensures centering and proper text scoping)
PB_BLOG_POST_CSS = """/* pb-blog-post wrapper styles - ensures centered 760px layout */
.pb-blog-post {
    max-width: 760px;
    margin: 0 auto;
    padding: 20px;
    color: #e8e8e8;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.7;
    font-size: 17px;
}
.pb-blog-post h1, .pb-blog-post h2, .pb-blog-post h3 {
    color: #ffffff !important;
}
.pb-blog-post p { color: #e0e0e0; margin: 0 0 1.2em; }
.pb-blog-post a { color: #f1420b !important; text-decoration: none; }
.pb-blog-post ul, .pb-blog-post ol { margin: 0 0 1.2em 1.5em; color: #e0e0e0; }
.pb-blog-post strong { color: #ffffff; }
.pb-blog-post blockquote {
    border-left: 3px solid #2a93c1;
    padding: 16px 20px;
    margin: 1.5em 0;
    background: rgba(42,147,193,0.08);
    color: rgba(232,237,245,0.9);
    font-style: italic;
}"""


def wrap_post_content(html, slug):
    """
    Wrap the blog post content in <article class="pb-blog-post">.

    The content starts AFTER the banner image injection and ends BEFORE
    the Aether footer credit bar (or closing </body>).

    Strategy:
    1. Find the end of the banner image tag (after <!-- INJECTED: Post banner image -->)
    2. Find the start of the footer section (pb-aether-footer or </body>)
    3. Wrap everything in between with <article class="pb-blog-post">
    """
    if '<article class="pb-blog-post">' in html:
        print(f"    Already has pb-blog-post wrapper - skipping")
        return html, False

    # Find the end of the banner image
    # Pattern: <!-- INJECTED: Post banner image --> ... <img ... />\n\n
    banner_comment = '<!-- INJECTED: Post banner image -->'
    banner_idx = html.find(banner_comment)

    if banner_idx < 0:
        # Fallback: find the last </nav> and start after that
        nav_end = html.rfind('</nav>')
        if nav_end < 0:
            print(f"    ERROR: No banner comment or nav found in {slug}")
            return html, False
        # Content starts after </nav>
        content_start = nav_end + len('</nav>')
        # Find the next non-whitespace after </nav>
        while content_start < len(html) and html[content_start] in '\n\r ':
            content_start += 1
    else:
        # Find the end of the img tag after the banner comment
        img_tag_start = html.find('<img', banner_idx)
        if img_tag_start < 0:
            print(f"    ERROR: No img tag after banner comment in {slug}")
            return html, False
        # Find the end of this img tag
        img_tag_end = html.find('>', img_tag_start) + 1
        # Skip newlines after the img tag
        content_start = img_tag_end
        while content_start < len(html) and html[content_start] in '\n\r':
            content_start += 1

    # Find the end of the content - look for footer markers
    # The content ends BEFORE the aether footer or the closing body script block
    content_end_markers = [
        '<div id="pb-aether-footer"',
        'id="purebrain-legal-footer"',
        '<!-- Aether Footer Credit Bar -->',
        '<!-- footer -->',
        '<script>if(typeof ga',  # GA tracking script after content
    ]

    content_end = -1
    for marker in content_end_markers:
        idx = html.rfind(marker)
        if idx > content_start:
            if content_end < 0 or idx < content_end:
                content_end = idx

    if content_end < 0:
        # Fallback: end before </body>
        content_end = html.rfind('</body>')
        if content_end < 0:
            print(f"    ERROR: Could not find content end in {slug}")
            return html, False

    # Extract content
    content = html[content_start:content_end]
    print(f"    Content range: {content_start} to {content_end} ({len(content)} chars)")

    # Strip leading/trailing whitespace from content
    content = content.strip()

    if not content:
        print(f"    ERROR: Empty content extracted from {slug}")
        return html, False

    # Build new wrapped content
    wrapped_content = f'\n<article class="pb-blog-post">\n{content}\n</article>\n\n'

    # Replace the original content section
    new_html = html[:content_start] + wrapped_content + html[content_end:]

    # Verify
    if '<article class="pb-blog-post">' not in new_html:
        print(f"    ERROR: Wrapper not found after replacement in {slug}")
        return html, False

    return new_html, True


def fix_blog_post_formatting():
    """Add pb-blog-post wrapper to all 12 bad posts."""
    print("\n[Task 2] Fixing blog post formatting (12 posts)...")

    results = {}

    for slug in BAD_POSTS:
        post_file = BLOG_DIR / slug / "index.html"
        if not post_file.exists():
            print(f"\n  SKIP: {slug} (file not found)")
            results[slug] = "missing"
            continue

        print(f"\n  [{slug}]")
        html = post_file.read_text(encoding="utf-8")

        new_html, changed = wrap_post_content(html, slug)

        if not changed:
            results[slug] = "skipped"
            continue

        if '<article class="pb-blog-post">' not in new_html:
            print(f"    ERROR: Wrapper verification failed")
            results[slug] = "error"
            continue

        post_file.write_text(new_html, encoding="utf-8")
        print(f"    Written: {post_file} ({len(new_html)} chars)")
        results[slug] = "fixed"

    return results


# ---------------------------------------------------------------------------
# Deploy via wrangler
# ---------------------------------------------------------------------------

def deploy_to_cf_pages():
    """Deploy the CF Pages project via wrangler."""
    print("\n[Deploy] Deploying to Cloudflare Pages via wrangler...")

    cmd = [
        "npx", "wrangler", "pages", "deploy", ".",
        "--project-name=purebrain-staging",  # purebrain.ai DNS points to purebrain-staging.pages.dev
        "--branch=main",
        "--commit-dirty=true"
    ]

    env = {
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/jared/.local/bin",
        "CLOUDFLARE_ACCOUNT_ID": "d526a3e9498dd167509003004df03290",
        "CLOUDFLARE_API_TOKEN": "HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_",
        "HOME": "/home/jared",
    }

    import os
    full_env = {**os.environ, **env}

    result = subprocess.run(
        cmd,
        cwd=str(CF_DEPLOY_ROOT),
        env=full_env,
        capture_output=True,
        text=True,
        timeout=300
    )

    print(f"  Exit code: {result.returncode}")
    if result.stdout:
        print("  STDOUT:")
        for line in result.stdout.split('\n')[-20:]:
            print(f"    {line}")
    if result.stderr:
        print("  STDERR (last 20 lines):")
        for line in result.stderr.split('\n')[-20:]:
            if line.strip():
                print(f"    {line}")

    return result.returncode == 0


# ---------------------------------------------------------------------------
# CF Cache Purge
# ---------------------------------------------------------------------------

def purge_cf_cache(urls):
    """Purge Cloudflare cache for affected URLs."""
    import requests as req_lib

    print("\n[CF Cache] Purging cache for affected URLs...")

    CF_EMAIL = "jared@puretechnology.nyc"
    CF_KEY = "251911c00fe74daedaff1133decfc3a00f66c"
    ZONE_ID = "49400cad1527af716705f6cb8c22bb65"

    resp = req_lib.post(
        f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/purge_cache",
        headers={
            "X-Auth-Email": CF_EMAIL,
            "X-Auth-Key": CF_KEY,
            "Content-Type": "application/json"
        },
        json={"files": urls},
        timeout=30
    )
    print(f"  Purge status: {resp.status_code}")
    if resp.ok:
        data = resp.json()
        print(f"  Success: {data.get('success')}")
        return True
    else:
        print(f"  Error: {resp.text[:200]}")
        return False


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_blog_listing():
    """Check that banner images are now in the blog listing page static file."""
    html = BLOG_LISTING_FILE.read_text(encoding="utf-8")
    img_count = html.count('<img src=')
    placeholder_count = html.count('nfm-card-image-placeholder')
    print(f"  Blog listing: {img_count} images, {placeholder_count} placeholders")
    return img_count >= 20  # Allow 5 images to be missing without failing


def verify_bad_posts():
    """Check that all 12 bad posts now have the pb-blog-post wrapper."""
    all_ok = True
    for slug in BAD_POSTS:
        post_file = BLOG_DIR / slug / "index.html"
        if post_file.exists():
            html = post_file.read_text(encoding="utf-8")
            has_wrapper = '<article class="pb-blog-post">' in html
            status = "OK" if has_wrapper else "FAIL"
            print(f"  [{status}] {slug}")
            if not has_wrapper:
                all_ok = False
    return all_ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PUREBRAIN CF PAGES BLOG FIX v2.0")
    print("Task 1: Fix banner images on blog listing page")
    print("Task 2: Fix blog post formatting (12 posts)")
    print("=" * 65)

    # Task 1
    t1_ok = fix_blog_listing_page()

    # Task 2
    t2_results = fix_blog_post_formatting()
    t2_ok = all(v in ("fixed", "skipped") for v in t2_results.values())

    # Summary before deploy
    print("\n" + "=" * 65)
    print("PRE-DEPLOY VERIFICATION")
    print("=" * 65)

    print("\nTask 1 (Blog listing):")
    t1_verify = verify_blog_listing()
    print(f"  Result: {'PASS' if t1_verify else 'FAIL'}")

    print("\nTask 2 (Post formatting):")
    t2_verify = verify_bad_posts()
    print(f"  Result: {'PASS' if t2_verify else 'FAIL'}")

    if not t1_verify and not t2_verify:
        print("\nERROR: Neither task succeeded. Aborting deploy.")
        return 1

    # Deploy
    deploy_ok = deploy_to_cf_pages()

    if deploy_ok:
        # Purge CF cache for affected URLs
        affected_urls = [
            "https://purebrain.ai/blog-neural-feed-memories/",
        ] + [
            f"https://purebrain.ai/blog/{slug}/"
            for slug in BAD_POSTS
        ]
        purge_cf_cache(affected_urls)
    else:
        print("\nWARNING: Deploy failed. Files are updated locally but not live.")

    print("\n" + "=" * 65)
    print("FINAL SUMMARY")
    print("=" * 65)
    print(f"  Task 1 (banners): {'OK' if t1_verify else 'FAIL'}")
    print(f"  Task 2 (formatting): {'OK' if t2_verify else 'FAIL'}")
    print(f"  Deploy: {'OK' if deploy_ok else 'FAIL'}")

    for slug, status in t2_results.items():
        icon = "OK" if status in ("fixed", "skipped") else "FAIL"
        print(f"    [{icon}] {slug}: {status}")

    return 0 if (t1_verify and t2_verify and deploy_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
