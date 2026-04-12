#!/usr/bin/env python3
"""
fix_blog_cf_pages.py
====================
Fixes two critical blog issues on the CF Pages static export:

ISSUE 1: Broken banner images - adds _redirects rules for WordPress thumbnail size variants
         (e.g. banner-1024x576.png -> banner.png)

ISSUE 2: Missing blog experience - injects nav bar + banner hero image into all 24 blog posts
         (social sharing + CTA is already present in most posts; adds it where missing)
"""

import os
import re

BLOG_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog"
REDIRECTS_FILE = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/_redirects"
UPLOADS_BASE = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/wp-content/uploads"

# ============================================================
# ISSUE 1: Image redirect mappings
# For each image in wp-content/uploads, generate redirects for
# all known WP thumbnail size variants -> original file
# ============================================================

WP_THUMB_PATTERNS = [
    r"-1024x576",
    r"-768x432",
    r"-300x169",
    r"-150x150",
    r"-300x300",
    r"-1536x864",
    r"-2048x1152",
    r"-scaled",
]

def get_upload_files():
    """Collect all original upload files from 2026/02 and 2026/03."""
    files = {}
    for year_month in ["2026/02", "2026/03"]:
        d = os.path.join(UPLOADS_BASE, year_month)
        if not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            fpath = f"/wp-content/uploads/{year_month}/{fname}"
            files[fpath] = True
    return files

def generate_image_redirects(upload_files):
    """For each upload file, generate redirects for all WP thumbnail variants -> original."""
    lines = []
    for fpath in sorted(upload_files.keys()):
        # Split filename and extension
        dot = fpath.rfind(".")
        if dot == -1:
            continue
        base = fpath[:dot]
        ext = fpath[dot:]  # includes the dot

        # For each size pattern, add a redirect
        for pattern in WP_THUMB_PATTERNS:
            thumb_path = base + pattern + ext
            lines.append(f"{thumb_path} {fpath} 301")

    return lines

# ============================================================
# ISSUE 2: Blog post experience injection
# Nav bar + banner hero for each post
# ============================================================

# Map: post slug -> banner image path (relative to CF Pages root)
POST_BANNERS = {
    "your-ai-resets-to-zero-every-morning": "/wp-content/uploads/2026/03/your-ai-resets-to-zero-every-morning-banner.png",
    "your-ai-doesnt-work-for-you": "/wp-content/uploads/2026/03/your-ai-doesnt-work-for-you-blog-post.png",
    "the-ai-that-forgets-you-every-single-time": "/wp-content/uploads/2026/03/the-ai-that-forgets-you-banner.png",
    "the-context-tax": "/wp-content/uploads/2026/03/the-context-tax-banner.jpg",
    "teach-your-ai-something-no-one-else-can": "/wp-content/uploads/2026/03/teach-your-ai-banner-jared-approved.jpg",
    "52-billion-ai-agents-market-is-not-the-story": "/wp-content/uploads/2026/03/52-billion-ai-agents-market-banner.jpg",
    "age-of-ai-agents-next-18-months": "/wp-content/uploads/2026/03/age-of-ai-agents-banner.png",
    "something-big-already-happened-you-just-werent-invited-yet": "/wp-content/uploads/2026/03/something-big-already-happened-banner.png",
    "the-age-of-ai-agents": "/wp-content/uploads/2026/03/the-age-of-ai-agents-banner.png",
    "the-ai-trust-gap": "/wp-content/uploads/2026/02/trust-gap-blog-banner.png",
    "the-first-90-days-of-an-ai-partnership": "/wp-content/uploads/2026/02/the-first-90-days-of-an-ai-partnership-banner.png",
    "ceo-vs-employee-ai-transformation-gap": "/wp-content/uploads/2026/02/ceo-vs-employee-ai-lens-banner.png",
    "the-difference-between-using-ai-and-having-an-ai-partner": "/wp-content/uploads/2026/02/the-difference-using-ai-partner.png",
    "why-ai-memory-changes-everything": "/wp-content/uploads/2026/02/why-ai-memory-changes-everything-banner.png",
    "your-ai-has-no-memory-mine-does": "/wp-content/uploads/2026/02/your-ai-has-no-memory-mine-does-banner.jpg",
    "your-next-direct-report-wont-be-human": "/wp-content/uploads/2026/02/your-next-direct-report-wont-be-human-banner.jpg",
    "how-my-human-named-me-and-what-it-meant": "/wp-content/uploads/2026/02/how-my-human-named-me.png",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2": "/wp-content/uploads/2026/02/ai-competence-divide-banner.png",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": "/wp-content/uploads/2026/02/why-your-ai-pilot-is-failing-banner.png",
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": "/wp-content/uploads/2026/02/ai-competence-divide-banner.png",
    "why-95-percent-of-ai-pilots-fail": "/wp-content/uploads/2026/02/why-your-ai-pilot-is-failing-banner.png",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": "/wp-content/uploads/2026/02/why-your-ai-pilot-is-failing-banner.png",
    "we-both-wrote-this-post": "/wp-content/uploads/2026/02/origin-story-blog-banner.png",
    "what-i-actually-do-all-day": "/wp-content/uploads/2026/02/origin-story-blog-banner.png",
}

NAV_CSS = """
/* ============================================================
   BLOG POST NAV BAR
   ============================================================ */
.pb-post-nav {
    position: sticky;
    top: 0;
    z-index: 1000;
    display: flex !important;
    justify-content: center;
    align-items: center;
    gap: 20px;
    background: rgba(10, 10, 15, 0.95);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 12px 24px;
    border-bottom: 1px solid rgba(42, 147, 193, 0.3);
    flex-wrap: wrap;
}

.pb-post-nav a {
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    font-family: 'Oswald', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 8px 14px;
    border-radius: 6px;
    transition: all 0.3s ease;
    min-height: 44px;
    display: flex;
    align-items: center;
    border-bottom: none !important;
}

.pb-post-nav a:hover {
    color: #2a93c1;
    background: rgba(42, 147, 193, 0.1);
    padding: 8px 14px;
    border-radius: 6px;
    border-bottom: none !important;
}

.pb-post-nav a.nav-cta {
    color: #ffffff !important;
    background: linear-gradient(135deg, #f1420b 0%, #ed6626 100%);
    border-bottom: none !important;
}

.pb-post-nav a.nav-cta:hover {
    background: linear-gradient(135deg, #ed6626 0%, #f1420b 100%);
    box-shadow: 0 4px 20px rgba(241, 66, 11, 0.4);
    transform: translateY(-1px);
    padding: 8px 14px;
    border-radius: 6px;
    border-bottom: none !important;
}

@media (max-width: 600px) {
    .pb-post-nav {
        gap: 8px;
        padding: 10px 12px;
    }
    .pb-post-nav a {
        font-size: 0.78rem;
        padding: 6px 10px;
        min-height: 40px;
    }
}

/* ============================================================
   BANNER HERO IMAGE
   ============================================================ */
.pb-post-banner {
    width: 100%;
    max-width: 900px;
    margin: 32px auto 0;
    display: block;
    border-radius: 12px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
    position: relative;
    z-index: 1;
}

@media (max-width: 940px) {
    .pb-post-banner {
        border-radius: 8px;
        margin: 20px auto 0;
    }
}
"""

NAV_HTML_TEMPLATE = """<!-- INJECTED: Blog post nav bar -->
<nav class="pb-post-nav" aria-label="Site navigation">
    <a href="https://purebrain.ai/">Home</a>
    <a href="https://purebrain.ai/blog/">The Neural Feed</a>
    <a href="https://purebrain.ai/blog/#neural-feed-subscribe">Subscribe</a>
    <a href="https://purebrain.ai/ai-partnership-assessment/">AI Assessment</a>
    <a href="https://purebrain.ai/#awakening" class="nav-cta">Start Your AI Partnership</a>
</nav>"""

BANNER_HTML_TEMPLATE = """<!-- INJECTED: Post banner image -->
<img class="pb-post-banner" src="{banner_src}" alt="{alt_text}" loading="eager" />"""

SOCIAL_SHARE_HTML = """<!-- INJECTED: Social sharing -->
<style>
.pt-social-share { display: flex; align-items: center; gap: 12px; padding: 20px 0; margin: 28px 0 0; border-top: 2px solid rgba(42, 147, 193, 0.3); flex-wrap: wrap; }
.pt-social-share span { font-weight: 600; color: #fff; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
.pt-social-share a { display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; background: rgba(42, 147, 193, 0.15); color: #2a93c1; text-decoration: none; transition: all 0.3s; font-size: 18px; border: none !important; border-bottom: none !important; padding: 0 !important; }
.pt-social-share a:hover { background: #2a93c1; color: #fff; transform: scale(1.1); border-bottom: none !important; }
.pt-social-share a svg { width: 20px; height: 20px; fill: currentColor; }
</style>
<div class="pt-social-share">
<span>Share:</span>
<a href="javascript:void(0)" onclick="window.open('https://www.linkedin.com/sharing/share-offsite/?url='+encodeURIComponent(window.location.href),'_blank','width=600,height=400')" title="Share on LinkedIn" aria-label="Share on LinkedIn">
<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://twitter.com/intent/tweet?url='+encodeURIComponent(window.location.href)+'&text='+encodeURIComponent(document.title),'_blank','width=600,height=400')" title="Share on X" aria-label="Share on X">
<svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(window.location.href),'_blank','width=600,height=400')" title="Share on Facebook" aria-label="Share on Facebook">
<svg viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.location.href='mailto:?subject='+encodeURIComponent(document.title)+'&body='+encodeURIComponent(window.location.href)" title="Share via Email" aria-label="Share via Email">
<svg viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
</a>
</div>
<div class="blog-cta-block" style="margin-top:40px;padding:32px;background:rgba(42,147,193,0.08);border:1px solid rgba(42,147,193,0.15);border-radius:16px;text-align:center;">
<p style="font-size:1.2rem;color:#ffffff;margin-bottom:12px;font-weight:600;">Ready to awaken your AI partner?</p>
<p><a href="https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content={slug}#awakening" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#f1420b 0%,#d13608 100%);color:#ffffff !important;font-weight:700;font-size:1.1rem;border-radius:8px;text-decoration:none;letter-spacing:0.5px;">Start Your AI Partnership</a></p>
<p style="font-size:0.95rem;color:rgba(255,255,255,0.6);margin-top:16px;">And if this perspective was valuable, <a href="https://purebrain.ai/blog/?utm_source=blog&utm_medium=cta&utm_campaign=newsletter&utm_content={slug}" style="color:#2a93c1 !important;text-decoration:underline;">subscribe to our newsletter</a> where we share insights on building AI relationships every week.</p>
</div>"""


def slugify_to_title(slug):
    """Convert a slug to a readable title for alt text."""
    return slug.replace("-", " ").title()


def inject_nav_css_into_post(html, slug):
    """Inject nav CSS into <style> block or add it."""
    if ".pb-post-nav {" in html:
        return html, False  # Already has nav CSS
    # Find the first </style> and inject before it
    # Or find the first <style> block and append our CSS at end of it
    if "</style>" in html:
        insert_point = html.index("</style>")
        html = html[:insert_point] + NAV_CSS + "\n" + html[insert_point:]
        return html, True
    return html, False


def inject_nav_html(html, slug):
    """Inject nav bar HTML after <body> tag."""
    # Check for the actual HTML nav element, not just the CSS class name
    if '<nav class="pb-post-nav"' in html:
        return html, False  # Already has nav HTML
    # Insert after <body> tag
    if "<body>" in html:
        insert_after = "<body>"
        pos = html.index(insert_after) + len(insert_after)
        html = html[:pos] + "\n" + NAV_HTML_TEMPLATE + "\n" + html[pos:]
        return html, True
    return html, False


def inject_banner(html, slug, banner_src):
    """Inject banner image after the nav bar, before the article content."""
    # Check for the actual img element, not the CSS class definition
    if '<img class="pb-post-banner"' in html:
        return html, False  # Already has banner

    alt_text = f"PureBrain Blog: {slugify_to_title(slug)}"
    banner_html = BANNER_HTML_TEMPLATE.format(banner_src=banner_src, alt_text=alt_text)

    # Format 1: Insert before <article class="pb-blog-post">
    article_marker = '<article class="pb-blog-post">'
    if article_marker in html:
        pos = html.index(article_marker)
        html = html[:pos] + banner_html + "\n" + html[pos:]
        return html, True

    # Format 2: Older posts - insert after the nav HTML, before the first real content block
    # Find the nav closing tag and insert after it
    nav_end = '</nav>'
    if nav_end in html:
        pos = html.index(nav_end) + len(nav_end)
        html = html[:pos] + "\n" + banner_html + "\n" + html[pos:]
        return html, True

    return html, False


def inject_social_and_cta(html, slug):
    """Inject social share + CTA before </article> if not already present."""
    # Check for the actual HTML div element, not just the CSS class
    if '<div class="pt-social-share"' in html or "class='pt-social-share'" in html:
        return html, False  # Already has social share HTML

    share_html = SOCIAL_SHARE_HTML.replace("{slug}", slug)

    # Insert before </article>
    if "</article>" in html:
        pos = html.rindex("</article>")
        html = html[:pos] + "\n" + share_html + "\n" + html[pos:]
        return html, True

    return html, False


def process_blog_post(post_dir):
    """Process a single blog post directory."""
    index_path = os.path.join(post_dir, "index.html")
    if not os.path.exists(index_path):
        return None

    slug = os.path.basename(post_dir)

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    changes = []

    # Inject nav CSS
    html, changed = inject_nav_css_into_post(html, slug)
    if changed:
        changes.append("nav-css")

    # Inject nav HTML
    html, changed = inject_nav_html(html, slug)
    if changed:
        changes.append("nav-html")

    # Inject banner if we have one for this post
    banner_src = POST_BANNERS.get(slug)
    if banner_src:
        html, changed = inject_banner(html, slug, banner_src)
        if changed:
            changes.append(f"banner({banner_src.split('/')[-1]})")

    # Inject social + CTA if missing
    html, changed = inject_social_and_cta(html, slug)
    if changed:
        changes.append("social+cta")

    if changes:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)

    return slug, changes


def update_redirects(new_redirect_lines):
    """Append image redirect rules to the _redirects file."""
    with open(REDIRECTS_FILE, "r", encoding="utf-8") as f:
        existing = f.read()

    marker = "# WordPress thumbnail size redirects - auto-generated"
    if marker in existing:
        # Remove old auto-generated block and replace
        start = existing.index(marker)
        # Find end of block (next section comment or EOF)
        after = existing[start:]
        # Remove everything from marker to end of the generated block
        lines_after = after.split("\n")
        # Find where generated block ends (empty line after generated lines)
        end_idx = 0
        for i, line in enumerate(lines_after[1:], 1):
            if line.startswith("#") and "WordPress thumbnail" not in line:
                end_idx = i
                break
            if not line.strip() and i > 5:
                end_idx = i + 1
                break
        if end_idx:
            existing = existing[:start] + "\n".join(lines_after[end_idx:])
        else:
            existing = existing[:start]

    new_block = marker + "\n" + "\n".join(new_redirect_lines) + "\n\n"
    with open(REDIRECTS_FILE, "w", encoding="utf-8") as f:
        f.write(existing.rstrip() + "\n\n" + new_block)


def main():
    print("=" * 60)
    print("PureBrain Blog CF Pages Fix")
    print("=" * 60)

    # ISSUE 1: Generate image redirects
    print("\n[ISSUE 1] Generating image redirect rules...")
    upload_files = get_upload_files()
    print(f"  Found {len(upload_files)} upload files")

    redirect_lines = generate_image_redirects(upload_files)
    print(f"  Generated {len(redirect_lines)} redirect rules")

    update_redirects(redirect_lines)
    print(f"  Written to: {REDIRECTS_FILE}")

    # ISSUE 2: Process all blog posts
    print("\n[ISSUE 2] Processing blog posts...")
    blog_dirs = sorted([
        os.path.join(BLOG_DIR, d)
        for d in os.listdir(BLOG_DIR)
        if os.path.isdir(os.path.join(BLOG_DIR, d))
    ])

    total_posts = 0
    total_changes = 0
    for post_dir in blog_dirs:
        result = process_blog_post(post_dir)
        if result is None:
            continue
        slug, changes = result
        total_posts += 1
        if changes:
            total_changes += 1
            print(f"  UPDATED {slug}: {', '.join(changes)}")
        else:
            print(f"  OK      {slug}: no changes needed")

    print(f"\n[SUMMARY]")
    print(f"  Blog posts processed: {total_posts}")
    print(f"  Blog posts updated:   {total_changes}")
    print(f"  Image redirects:      {len(redirect_lines)}")
    print(f"\nDone.")


if __name__ == "__main__":
    main()
