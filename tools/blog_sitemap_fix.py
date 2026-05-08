#!/usr/bin/env python3
"""
GAP-C: Sitemap fixes
- Set <changefreq>weekly</changefreq> for blog post URLs (was monthly)
- Set <lastmod>2026-04-14</lastmod> for blog post URLs
- Idempotent.
"""
import re
from pathlib import Path

SITEMAP = Path("/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/sitemap.xml")
TODAY = "2026-04-14"

src = SITEMAP.read_text(encoding="utf-8")

# Find each <url>...</url> block, check if its <loc> contains /blog/<slug>/ (not root /blog/)
blog_post_re = re.compile(r'<url>\s*<loc>https://purebrain\.ai/blog/[^<]+/</loc>.*?</url>', re.DOTALL)

changed_posts = 0

def fix_block(m):
    global changed_posts
    block = m.group(0)
    loc_match = re.search(r'<loc>([^<]+)</loc>', block)
    loc = loc_match.group(1) if loc_match else ""
    # Exclude the blog index (/blog/) — only match /blog/<slug>/
    if loc.rstrip("/") in ("https://purebrain.ai/blog",):
        return block
    new = re.sub(r'<changefreq>monthly</changefreq>', '<changefreq>weekly</changefreq>', block)
    new = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{TODAY}</lastmod>', new)
    if new != block:
        changed_posts += 1
    return new

new_src = blog_post_re.sub(fix_block, src)

if new_src != src:
    SITEMAP.write_text(new_src, encoding="utf-8")
    print(f"Sitemap updated: {changed_posts} blog post URLs set to weekly + lastmod {TODAY}")
else:
    print(f"Sitemap already up to date (no changes needed).")
