#!/usr/bin/env python3
"""
fix_blog_index.py — Rebuild blog/index.html to show all 32 posts.

The index uses WordPress wp-block-latest-posts format.
This script rebuilds the <ul> contents with all posts in correct order.
"""

import os
import re
import html as html_module
from datetime import datetime

BLOG_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog"
INDEX_PATH = os.path.join(BLOG_DIR, "index.html")

# Complete date mapping
SLUG_TO_DATE = {
    "why-your-ai-should-have-a-name": "2026-02-13",
    "what-i-named-my-ai": "2026-02-13",
    "how-my-human-named-me-and-what-it-meant": "2026-02-14",
    "why-enterprises-are-betting-on-agentic-ai": "2026-02-14",
    "what-i-actually-do-all-day": "2026-02-15",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2": "2026-02-16",
    "why-ai-memory-changes-everything": "2026-02-17",
    "ceo-vs-employee-ai-transformation-gap": "2026-02-18",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": "2026-02-19",
    "the-difference-between-using-ai-and-having-an-ai-partner": "2026-02-20",
    "why-95-percent-of-ai-pilots-fail": "2026-02-21",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": "2026-02-21",
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
    "the-ai-that-knows-you-before-you-even-speak": "2026-03-15",
    "prompting-is-dead": "2026-03-17",
    "your-ai-has-no-idea-who-you-are": "2026-03-18",
    "the-ai-that-gets-smarter-when-you-push-back": "2026-03-18",
    "your-ai-resets-to-zero-every-morning": "2026-03-19",
    "the-meeting-your-ai-should-already-know-about": "2026-03-20",
}

# Post order: newest first
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


def extract_meta(slug: str) -> dict:
    """Extract title and description from a post's index.html."""
    html_path = os.path.join(BLOG_DIR, slug, "index.html")
    if not os.path.exists(html_path):
        return None

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Title
    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    title = title_match.group(1) if title_match else slug.replace("-", " ").title()
    title = re.sub(r"\s*\|\s*PureBrain.*$", "", title).strip()
    title = html_module.unescape(title)

    # Description (og:description or meta description)
    desc_match = re.search(
        r'<meta(?:\s+[^>]*)?\sproperty="og:description"\s+content="([^"]+)"',
        content, re.IGNORECASE
    )
    if not desc_match:
        desc_match = re.search(
            r'<meta name="description" content="([^"]+)"', content, re.IGNORECASE
        )
    description = desc_match.group(1) if desc_match else ""
    description = html_module.unescape(description)

    return {"title": title, "description": description}


def make_post_item(slug: str) -> str:
    """Build a <li> block in wp-block-latest-posts format."""
    date_str = SLUG_TO_DATE.get(slug, "2026-02-13")
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        display_date = dt.strftime("%B %-d, %Y")
        datetime_iso = f"{date_str}T10:00:00+00:00"
    except Exception:
        display_date = date_str
        datetime_iso = f"{date_str}T10:00:00+00:00"

    meta = extract_meta(slug)
    if not meta:
        return ""

    title = meta["title"]
    description = meta["description"]
    # Truncate description to ~160 chars, encode HTML entities
    if len(description) > 160:
        description = description[:157] + "..."
    desc_encoded = html_module.escape(description).replace("'", "&#8217;")
    title_encoded = html_module.escape(title)
    alt_encoded = html_module.escape(title)

    return (
        f'<li>'
        f'<div class="wp-block-latest-posts__featured-image">'
        f'<img loading="lazy" decoding="async" width="800" height="450" '
        f'src="/blog/{slug}/banner.png" '
        f'class="attachment-large size-large wp-post-image" '
        f'alt="{alt_encoded}" /></div>'
        f'<a class="wp-block-latest-posts__post-title" href="/blog/{slug}/">{title_encoded}</a>'
        f'<time datetime="{datetime_iso}" class="wp-block-latest-posts__post-date">{display_date}</time>'
        f'<div class="wp-block-latest-posts__post-excerpt">{desc_encoded}</div>'
        f'</li>'
    )


def rebuild():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Build ordered list of slugs (no duplicates)
    seen = set()
    ordered_slugs = []
    for slug in POST_ORDER_NEWEST_FIRST:
        if slug not in seen and os.path.isdir(os.path.join(BLOG_DIR, slug)):
            ordered_slugs.append(slug)
            seen.add(slug)

    # Add any additional slugs not in the ordered list
    all_dirs = sorted([
        d for d in os.listdir(BLOG_DIR)
        if os.path.isdir(os.path.join(BLOG_DIR, d))
    ])
    for slug in all_dirs:
        if slug not in seen:
            ordered_slugs.append(slug)
            seen.add(slug)

    print(f"[fix_blog_index] Building {len(ordered_slugs)} post items")

    # Build new <li> items
    items = []
    for slug in ordered_slugs:
        item = make_post_item(slug)
        if item:
            items.append(item)
        else:
            print(f"  SKIP (no html): {slug}")

    new_ul_content = "\n".join(items)

    # Replace the content of the <ul class="...wp-block-latest-posts..."> block
    ul_pattern = re.compile(
        r'(<ul[^>]*class="[^"]*wp-block-latest-posts[^"]*"[^>]*>)(.*?)(</ul>)',
        re.DOTALL | re.IGNORECASE
    )
    match = ul_pattern.search(content)
    if match:
        new_content = (
            content[: match.start(2)]
            + new_ul_content
            + content[match.end(2):]
        )
        print(f"[fix_blog_index] Replaced ul block successfully")
    else:
        print("[fix_blog_index] ERROR: Could not find wp-block-latest-posts ul!")
        return 0

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    # Verify
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        verify = f.read()
    count = len(re.findall(r'<a class="wp-block-latest-posts__post-title"', verify))
    print(f"[fix_blog_index] Verification: {count} post links in index")
    return count


if __name__ == "__main__":
    count = rebuild()
    print(f"\nBlog index now shows {count} posts.")
