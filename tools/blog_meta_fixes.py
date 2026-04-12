#!/usr/bin/env python3
"""
blog_meta_fixes.py — Fix OG images, BlogPosting schema, and blog index.

Fixes:
  1. Add og:image meta tags to 7 posts missing them
  2. Add BlogPosting JSON-LD schema to 29 posts missing it
  3. Rebuild blog index to show all 32 posts

Usage:
    python3 tools/blog_meta_fixes.py
"""

import os
import re
import json
import html

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

BLOG_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog"

# Complete date mapping for all blog posts
SLUG_TO_DATE = {
    # From source markdown filenames
    "how-my-human-named-me-and-what-it-meant": "2026-02-14",
    "what-i-actually-do-all-day": "2026-02-15",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2": "2026-02-16",
    "why-ai-memory-changes-everything": "2026-02-17",
    "ceo-vs-employee-ai-transformation-gap": "2026-02-18",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": "2026-02-19",
    "the-difference-between-using-ai-and-having-an-ai-partner": "2026-02-20",
    "why-95-percent-of-ai-pilots-fail": "2026-02-21",
    "the-ai-trust-gap": "2026-02-22",
    "we-both-wrote-this-post": "2026-02-23",
    "your-next-direct-report-wont-be-human": "2026-02-24",
    "your-ai-has-no-memory-mine-does": "2026-02-25",
    "the-first-90-days-of-an-ai-partnership": "2026-02-26",
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": "2026-02-28",
    "your-ai-doesnt-work-for-you": "2026-03-01",
    "the-age-of-ai-agents": "2026-03-02",
    "the-context-tax": "2026-03-03",
    "something-big-already-happened-you-just-werent-invited-yet": "2026-03-04",
    "the-ai-that-forgets-you-every-single-time": "2026-03-04",
    "age-of-ai-agents-next-18-months": "2026-03-05",
    "52-billion-ai-agents-market-is-not-the-story": "2026-03-06",
    "teach-your-ai-something-no-one-else-can": "2026-03-07",
    # Inferred from existing schema and memory
    "why-your-ai-should-have-a-name": "2026-02-13",
    "what-i-named-my-ai": "2026-02-13",
    "why-enterprises-are-betting-on-agentic-ai": "2026-02-14",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": "2026-02-21",
    "the-ai-that-knows-you-before-you-even-speak": "2026-03-15",
    "prompting-is-dead": "2026-03-17",
    "your-ai-has-no-idea-who-you-are": "2026-03-18",
    "the-ai-that-gets-smarter-when-you-push-back": "2026-03-18",
    "your-ai-resets-to-zero-every-morning": "2026-03-19",
    "the-meeting-your-ai-should-already-know-about": "2026-03-20",
}

# Post order for index (newest first) - from guide folder authoritative order
# Guide numbers: 1=oldest, higher=newer
# Augmented with unmapped posts at approximate positions
POST_ORDER_NEWEST_FIRST = [
    "the-meeting-your-ai-should-already-know-about",
    "your-ai-resets-to-zero-every-morning",
    "your-ai-has-no-idea-who-you-are",
    "the-ai-that-gets-smarter-when-you-push-back",
    "prompting-is-dead",
    "the-ai-that-knows-you-before-you-even-speak",
    "teach-your-ai-something-no-one-else-can",
    "52-billion-ai-agents-market-is-not-the-story",
    "age-of-ai-agents-next-18-months",
    "something-big-already-happened-you-just-werent-invited-yet",
    "the-ai-that-forgets-you-every-single-time",
    "the-context-tax",
    "the-age-of-ai-agents",
    "your-ai-doesnt-work-for-you",
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger",
    "the-first-90-days-of-an-ai-partnership",
    "your-ai-has-no-memory-mine-does",
    "your-next-direct-report-wont-be-human",
    "we-both-wrote-this-post",
    "the-ai-trust-gap",
    "why-95-percent-of-ai-pilots-fail",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value",
    "the-difference-between-using-ai-and-having-an-ai-partner",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time",
    "ceo-vs-employee-ai-transformation-gap",
    "why-ai-memory-changes-everything",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2",
    "what-i-actually-do-all-day",
    "how-my-human-named-me-and-what-it-meant",
    "why-enterprises-are-betting-on-agentic-ai",
    "what-i-named-my-ai",
    "why-your-ai-should-have-a-name",
]

# ---------------------------------------------------------------------------
# Helper: extract title + description from HTML
# ---------------------------------------------------------------------------

def extract_meta(content: str, slug: str) -> tuple[str, str]:
    """Extract title and description from HTML content."""
    # Title
    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    title = title_match.group(1) if title_match else slug.replace("-", " ").title()
    # Remove '| PureBrain' suffix and decode HTML entities
    title = re.sub(r"\s*\|\s*PureBrain.*$", "", title).strip()
    title = html.unescape(title)

    # Description
    desc_match = re.search(
        r'<meta name="description" content="([^"]+)"', content, re.IGNORECASE
    )
    description = desc_match.group(1) if desc_match else ""
    description = html.unescape(description)

    return title, description


# ---------------------------------------------------------------------------
# Fix 2: Add missing og:image tags
# ---------------------------------------------------------------------------

def fix_og_image(slug: str, content: str) -> str:
    """Add og:image meta tags if missing."""
    if "og:image" in content:
        return content  # Already has it

    og_block = (
        f'<meta property="og:image" content="https://purebrain.ai/blog/{slug}/banner.png" />\n'
        f'    <meta property="og:image:width" content="1200" />\n'
        f'    <meta property="og:image:height" content="630" />\n'
        f'    <meta property="og:image:type" content="image/png" />'
    )

    # Insert before </head> or before first <meta property="og:
    og_url_match = re.search(r'(<meta property="og:url"[^>]*/?>)', content)
    if og_url_match:
        # Insert right after og:url
        insert_after = og_url_match.group(1)
        return content.replace(insert_after, insert_after + "\n    " + og_block, 1)

    # Fallback: insert before </head>
    return content.replace("</head>", "    " + og_block + "\n</head>", 1)


# ---------------------------------------------------------------------------
# Fix 3: Add missing BlogPosting schema
# ---------------------------------------------------------------------------

def fix_blogposting_schema(slug: str, content: str) -> str:
    """Add BlogPosting JSON-LD schema if missing."""
    if "BlogPosting" in content:
        return content  # Already has it

    title, description = extract_meta(content, slug)
    date = SLUG_TO_DATE.get(slug, "2026-02-13")
    date_iso = f"{date}T12:00:00+00:00"

    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": description,
        "datePublished": date_iso,
        "dateModified": date_iso,
        "author": {
            "@type": "Person",
            "name": "Jared Sanborn"
        },
        "publisher": {
            "@type": "Organization",
            "name": "PureBrain",
            "url": "https://purebrain.ai/"
        },
        "url": f"https://purebrain.ai/blog/{slug}/",
        "image": f"https://purebrain.ai/blog/{slug}/banner.png",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://purebrain.ai/blog/{slug}/"
        }
    }

    schema_tag = (
        '<script type="application/ld+json">\n'
        + json.dumps(schema, indent=2, ensure_ascii=False)
        + "\n</script>"
    )

    # Insert before </head>
    return content.replace("</head>", schema_tag + "\n</head>", 1)


# ---------------------------------------------------------------------------
# Fix 4: Rebuild blog index
# ---------------------------------------------------------------------------

def get_post_metadata(slug: str) -> dict:
    """Extract title, description, and date from a post's index.html."""
    html_path = os.path.join(BLOG_DIR, slug, "index.html")
    if not os.path.exists(html_path):
        return None

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    title, description = extract_meta(content, slug)
    date = SLUG_TO_DATE.get(slug, "2026-02-13")

    # Format date for display: "March 6, 2026"
    from datetime import datetime
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        display_date = dt.strftime("%B %-d, %Y")
    except Exception:
        display_date = date

    return {
        "slug": slug,
        "title": title,
        "description": description,
        "date": date,
        "display_date": display_date,
    }


def rebuild_blog_index():
    """Rebuild the blog index to include all posts in correct order."""
    index_path = os.path.join(BLOG_DIR, "index.html")

    # Read existing index
    with open(index_path, "r", encoding="utf-8") as f:
        existing = f.read()

    # Collect metadata for all posts in order
    posts = []
    seen_slugs = set()
    for slug in POST_ORDER_NEWEST_FIRST:
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        meta = get_post_metadata(slug)
        if meta:
            posts.append(meta)

    # Also pick up any slugs not in our explicit order
    all_slugs = sorted([
        d for d in os.listdir(BLOG_DIR)
        if os.path.isdir(os.path.join(BLOG_DIR, d))
    ])
    for slug in all_slugs:
        if slug not in seen_slugs:
            meta = get_post_metadata(slug)
            if meta:
                posts.append(meta)
                seen_slugs.add(slug)

    print(f"[blog_index] Building index with {len(posts)} posts")

    # Generate the posts HTML
    posts_html_parts = []
    for i, post in enumerate(posts):
        badge = ""
        if i == 0:
            badge = '<span class="pb-new-badge">NEW</span>'

        posts_html_parts.append(f"""        <a href="/blog/{post['slug']}/" class="pb-post-card">
          <div class="pb-post-card-image">
            <img src="/blog/{post['slug']}/banner.png" alt="{html.escape(post['title'])}" loading="lazy" />
          </div>
          <div class="pb-post-card-body">
            {badge}
            <div class="pb-post-date">{post['display_date']}</div>
            <h2 class="pb-post-title">{html.escape(post['title'])}</h2>
            <p class="pb-post-excerpt">{html.escape(post['description'][:140])}...</p>
            <span class="pb-read-more">Read Post &rarr;</span>
          </div>
        </a>""")

    posts_html = "\n".join(posts_html_parts)

    # Find the posts grid container in existing HTML and replace it
    # Look for the pb-posts-grid or similar container
    grid_pattern = re.compile(
        r'(<(?:div|section)[^>]*class="[^"]*(?:pb-posts-grid|posts-grid|blog-grid)[^"]*"[^>]*>)(.*?)(</(?:div|section)>)',
        re.DOTALL | re.IGNORECASE,
    )
    match = grid_pattern.search(existing)

    if match:
        new_content = (
            existing[: match.start(2)]
            + "\n"
            + posts_html
            + "\n      "
            + existing[match.end(2) :]
        )
        print(f"[blog_index] Replaced posts grid container")
    else:
        # Try finding individual post cards and replacing the whole block
        # Look for first pb-post-card link to last one
        first_card = re.search(r'<a[^>]*class="[^"]*pb-post-card[^"]*"', existing)
        if first_card:
            # Find the last closing </a> after all cards
            # Find all post card blocks
            cards = list(re.finditer(r'<a[^>]*class="[^"]*pb-post-card[^"]*".*?</a>', existing, re.DOTALL))
            if cards:
                start = cards[0].start()
                end = cards[-1].end()
                new_content = existing[:start] + posts_html + existing[end:]
                print(f"[blog_index] Replaced {len(cards)} post card blocks")
            else:
                print("[blog_index] WARNING: Could not find post card blocks to replace")
                new_content = existing
        else:
            print("[blog_index] WARNING: Could not find posts grid - manual inspection needed")
            new_content = existing

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return len(posts)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main():
    blog_dir = BLOG_DIR
    slugs = sorted([
        d for d in os.listdir(blog_dir)
        if os.path.isdir(os.path.join(blog_dir, d))
    ])

    og_fixed = 0
    schema_fixed = 0
    skipped = 0

    print(f"\n=== Processing {len(slugs)} blog posts ===\n")

    for slug in slugs:
        html_path = os.path.join(blog_dir, slug, "index.html")
        if not os.path.exists(html_path):
            skipped += 1
            continue

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # Fix 2: OG image
        content = fix_og_image(slug, content)
        if content != original:
            og_fixed += 1
            print(f"[og:image] Fixed: {slug}")

        # Fix 3: BlogPosting schema
        prev = content
        content = fix_blogposting_schema(slug, content)
        if content != prev:
            schema_fixed += 1
            print(f"[BlogPosting] Fixed: {slug}")

        # Write back only if changed
        if content != original:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)

    print(f"\n=== Fix 2 (OG image): {og_fixed} posts fixed ===")
    print(f"=== Fix 3 (BlogPosting schema): {schema_fixed} posts fixed ===")

    # Fix 4: Rebuild blog index
    print(f"\n=== Fix 4: Rebuilding blog index ===")
    total_posts = rebuild_blog_index()
    print(f"=== Blog index rebuilt with {total_posts} posts ===")

    return og_fixed, schema_fixed, total_posts


if __name__ == "__main__":
    og_fixed, schema_fixed, total_posts = main()
    print(f"\n--- SUMMARY ---")
    print(f"OG image tags added: {og_fixed}")
    print(f"BlogPosting schemas added: {schema_fixed}")
    print(f"Blog index total posts: {total_posts}")
