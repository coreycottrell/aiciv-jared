#!/usr/bin/env python3
"""
sync_blog_memories.py - Sync blog posts to the Neural Feed Memories archive page.

RUN THIS EVERY TIME A BLOG IS PUBLISHED.

This script:
1. Scans all blog post directories in /home/jared/purebrain-site/blog/*/
2. Extracts title, date, banner image path, description from each post's index.html
3. Generates nfm-card entries for the memories page
4. Sorts ALL posts newest first
5. Writes the updated memories page at blog-neural-feed-memories/index.html

Usage:
    python3 /home/jared/projects/AI-CIV/aether/tools/sync_blog_memories.py

Also updates blog/index.html to show only the 10 most recent posts (latest transmissions).
The full archive lives at /blog-neural-feed-memories/.
"""

import os
import re
import glob
import html
from datetime import datetime, timezone

SITE_ROOT = "/home/jared/purebrain-site"
BLOG_DIR = os.path.join(SITE_ROOT, "blog")
MEMORIES_FILE = os.path.join(SITE_ROOT, "blog-neural-feed-memories", "index.html")
BLOG_INDEX_FILE = os.path.join(SITE_ROOT, "blog", "index.html")

SKIP_DIRS = {"_archived"}


def find_banner(post_dir):
    """Find banner image file in post directory."""
    slug = os.path.basename(post_dir)
    for ext in ["jpg", "jpeg", "png", "webp"]:
        banner = os.path.join(post_dir, f"banner.{ext}")
        if os.path.exists(banner):
            return f"/blog/{slug}/banner.{ext}"
    return None


def extract_post_metadata(post_dir):
    """Extract title, date, description, banner from a blog post's index.html."""
    index_file = os.path.join(post_dir, "index.html")
    if not os.path.exists(index_file):
        return None

    slug = os.path.basename(post_dir)
    if slug in SKIP_DIRS:
        return None

    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip redirect pages
    if 'http-equiv="refresh"' in content or "<title>Redirecting" in content:
        return None

    # Extract title from <title> tag
    title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
    title = title_match.group(1).strip() if title_match else slug.replace("-", " ").title()
    # Decode HTML entities in title
    title = html.unescape(title)
    # Clean up title - remove " - PureBrain" suffix
    title = re.sub(r"\s*[-–—]\s*PureBrain.*$", "", title)

    # Extract date from article:published_time or datetime attribute
    date_obj = None
    date_match = re.search(r'article:published_time"\s+content="([^"]+)"', content)
    if date_match:
        try:
            date_obj = datetime.fromisoformat(date_match.group(1).replace("+00:00", "+00:00").rstrip("Z"))
        except ValueError:
            pass

    if not date_obj:
        date_match = re.search(r'datetime="([^"]+)"', content)
        if date_match:
            try:
                date_obj = datetime.fromisoformat(date_match.group(1).replace("+00:00", "+00:00").rstrip("Z"))
            except ValueError:
                pass

    if not date_obj:
        # Try to find a date string like "April 23, 2026"
        date_match = re.search(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', content)
        if date_match:
            try:
                date_obj = datetime.strptime(date_match.group(0), "%B %d, %Y")
            except ValueError:
                pass

    if not date_obj:
        # Fallback: use file modification time
        mtime = os.path.getmtime(index_file)
        date_obj = datetime.fromtimestamp(mtime, tz=timezone.utc)

    # Normalize to offset-aware (UTC)
    if date_obj.tzinfo is None:
        date_obj = date_obj.replace(tzinfo=timezone.utc)

    # Extract description from meta description
    desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content)
    description = desc_match.group(1).strip() if desc_match else ""

    # Find banner image
    banner = find_banner(post_dir)

    return {
        "slug": slug,
        "title": title,
        "date": date_obj,
        "date_display": date_obj.strftime("%B %d, %Y").replace(" 0", " "),
        "description": description,
        "banner": banner,
        "url": f"/blog/{slug}/",
    }


def generate_nfm_card(post):
    """Generate an nfm-card HTML block for a post."""
    title_escaped = html.escape(post["title"], quote=True)
    banner_html = ""
    if post["banner"]:
        banner_html = f'''<img src="{post['banner']}" alt="PureBrain Blog" class="nfm-card-banner-img" loading="lazy" style="width:100%;height:100%;object-fit:cover;display:block;">'''
    else:
        banner_html = '''<div class="nfm-card-image-placeholder" style="width:100%;height:100%;background:linear-gradient(135deg,rgba(42,147,193,0.2),rgba(241,66,11,0.2));display:flex;align-items:center;justify-content:center;color:#2a93c1;font-size:2rem;">&#x1F9E0;</div>'''

    return f'''            <a href="{post['url']}" class="nfm-card" aria-label="Read: {title_escaped}">
                <div class="nfm-card-image-wrap">
                    {banner_html}
                </div>
                <div class="nfm-card-body">
                    <div class="nfm-card-date">{post['date_display']}</div>
                    <div class="nfm-card-title">{title_escaped}</div>
                    <span class="nfm-card-cta">Read More</span>
                </div>
            </a>'''


def generate_blog_li(post):
    """Generate a <li> blog card for blog/index.html."""
    title_escaped = html.escape(post["title"], quote=True)
    desc_escaped = html.escape(post["description"], quote=True)
    iso_date = post["date"].strftime("%Y-%m-%dT%H:%M:%S+00:00")
    banner_ext = post["banner"].split(".")[-1] if post["banner"] else "png"

    img_html = ""
    if post["banner"]:
        img_html = f'<div class="wp-block-latest-posts__featured-image"><img loading="lazy" decoding="async" width="800" height="450" src="{post["banner"]}" class="attachment-large size-large wp-post-image" alt="{title_escaped}" /></div>'

    return f'<li>{img_html}<a class="wp-block-latest-posts__post-title" href="{post["url"]}">{post["title"]}</a><time datetime="{iso_date}" class="wp-block-latest-posts__post-date">{post["date_display"]}</time><div class="wp-block-latest-posts__post-excerpt">{post["description"]}</div></li>'


def scan_all_posts():
    """Scan all blog post directories and return sorted list of posts."""
    posts = []
    for post_dir in glob.glob(os.path.join(BLOG_DIR, "*/")):
        post_dir = post_dir.rstrip("/")
        slug = os.path.basename(post_dir)
        if slug in SKIP_DIRS:
            continue
        meta = extract_post_metadata(post_dir)
        if meta:
            posts.append(meta)

    # Sort by date descending (newest first)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def update_memories_page(posts):
    """Update the Neural Feed Memories page with all posts."""
    with open(MEMORIES_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Generate all card HTML
    cards_html = "\n\n".join(generate_nfm_card(p) for p in posts)

    # Find the grid section and replace it
    # Pattern: from <div class="nfm-grid"> to its closing </div>
    grid_pattern = re.compile(
        r'(<div class="nfm-grid">)\s*.*?\s*(</div>\s*</div>)',
        re.DOTALL
    )
    grid_match = grid_pattern.search(content)
    if grid_match:
        new_grid = f'<div class="nfm-grid">\n\n{cards_html}\n\n        </div>\n    </div>'
        # Replace from nfm-grid opening to the container closing
        start = content.find('<div class="nfm-grid">')
        # Find the closing </div></div> for grid + container
        # We need to find the right closing tags
        end_marker = "<!-- FOOTER -->"
        end = content.find(end_marker)
        if end == -1:
            end_marker = '<div class="nfm-footer">'
            end = content.find(end_marker)

        if start != -1 and end != -1:
            content = content[:start] + new_grid + "\n    " + content[end:]

    # Update the count badge
    count = len(posts)
    content = re.sub(
        r'<div class="nfm-count-badge">.*?</div>',
        f'<div class="nfm-count-badge">{count} Transmissions in The Archive</div>',
        content
    )

    # Update version comment
    today = datetime.now().strftime("%Y-%m-%d")
    content = re.sub(
        r'<!-- v[\d.]+ - \d{4}-\d{2}-\d{2} - .*?-->',
        f'<!-- v4.0.0 - {today} - Auto-synced by sync_blog_memories.py, {count} posts -->',
        content
    )

    with open(MEMORIES_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[MEMORIES] Updated {MEMORIES_FILE} with {count} posts")


def update_blog_index(posts):
    """Update blog/index.html to show only the 10 most recent posts."""
    with open(BLOG_INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    top_10 = posts[:10]

    # Generate the <li> entries for top 10
    li_entries = "\n".join(generate_blog_li(p) for p in top_10)

    # Find and replace the posts list
    # Pattern: from the comment "<!-- All NN blog posts" through </ul>
    list_pattern = re.compile(
        r'<!-- All \d+ blog posts.*?-->\s*<ul class="wp-block-latest-posts__list has-dates wp-block-latest-posts">\s*.*?\s*</ul>',
        re.DOTALL
    )
    today = datetime.now().strftime("%Y-%m-%d")
    replacement = f'''<!-- Latest 10 blog posts (full archive at /blog-neural-feed-memories/) -- updated {today} -->
    <ul class="wp-block-latest-posts__list has-dates wp-block-latest-posts">
{li_entries}
</ul>'''

    content = list_pattern.sub(replacement, content)

    # Also update the JSON-LD schema to only include top 10
    schema_items = []
    for i, p in enumerate(top_10, 1):
        schema_items.append(f'{{"@type": "ListItem", "position": {i}, "url": "https://purebrain.ai{p["url"]}"}}')

    schema_list = ",\n      ".join(schema_items)
    schema_pattern = re.compile(
        r'"itemListElement":\s*\[.*?\]',
        re.DOTALL
    )
    content = schema_pattern.sub(f'"itemListElement": [\n      {schema_list}\n    ]', content)

    with open(BLOG_INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[BLOG INDEX] Updated {BLOG_INDEX_FILE} with {len(top_10)} latest posts (of {len(posts)} total)")


def main():
    print("=" * 60)
    print("Blog Sync: Scanning all blog posts...")
    print("=" * 60)

    posts = scan_all_posts()
    print(f"Found {len(posts)} blog posts")

    if not posts:
        print("ERROR: No posts found! Aborting.")
        return

    # Show top 10 for verification
    print("\nTop 10 most recent:")
    for i, p in enumerate(posts[:10], 1):
        print(f"  {i}. [{p['date_display']}] {p['title']}")

    print(f"\nOldest: [{posts[-1]['date_display']}] {posts[-1]['title']}")

    # Update both pages
    update_blog_index(posts)
    update_memories_page(posts)

    print("\nDone! Both pages updated.")
    print(f"  Blog index: {BLOG_INDEX_FILE} (latest 10)")
    print(f"  Memories:   {MEMORIES_FILE} (all {len(posts)})")


if __name__ == "__main__":
    main()
