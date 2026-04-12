#!/usr/bin/env python3
"""
Publish "Why Your AI Pilot Is Succeeding and Failing at the Same Time"
to jareddsanborn.com via WordPress REST API.
"""

import os
import sys
import json
import base64
import requests
import re
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
WP_URL      = "https://jareddsanborn.com/wp-json/wp/v2"
WP_USER     = "jared"
WP_PASS     = "plhi NeE4 Cb1c 4d9i BbjZ Knq3"   # WORDPRESS_APP_PASSWORD from .env
SLUG        = "ai-pilot-purgatory"

BANNER_PATH = (
    "/home/jared/projects/AI-CIV/aether/docs/from-telegram/"
    "Why your ai pilot is failing - Newsletter size.png"
)

POST_TITLE = "Why Your AI Pilot Is Succeeding and Failing at the Same Time"

SEO_DESC = (
    "95% of enterprise AI pilots fail to scale. Learn why usage metrics lie, "
    "where pilots die, and the human-centric path from Pilot Purgatory to production."
)

# ── Auth header ──────────────────────────────────────────────────────────────
credentials = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json",
}


# ── Markdown → HTML conversion ───────────────────────────────────────────────
def md_to_html(md: str) -> str:
    """Simple but complete markdown-to-HTML converter for this post."""

    lines = md.split("\n")
    html_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Horizontal rule
        if re.match(r"^---+$", line.strip()):
            html_lines.append("<hr>")
            i += 1
            continue

        # H1
        if line.startswith("# "):
            text = line[2:].strip()
            html_lines.append(f"<h1>{inline_md(text)}</h1>")
            i += 1
            continue

        # H2
        if line.startswith("## "):
            text = line[3:].strip()
            html_lines.append(f"<h2>{inline_md(text)}</h2>")
            i += 1
            continue

        # H3
        if line.startswith("### "):
            text = line[4:].strip()
            html_lines.append(f"<h3>{inline_md(text)}</h3>")
            i += 1
            continue

        # Italic (em) paragraph starting with *...*
        if line.startswith("*") and line.endswith("*") and not line.startswith("**"):
            text = line[1:-1].strip()
            html_lines.append(f"<p><em>{inline_md(text)}</em></p>")
            i += 1
            continue

        # Empty line → paragraph break
        if line.strip() == "":
            html_lines.append("")
            i += 1
            continue

        # Normal paragraph (or bold paragraph)
        if line.strip():
            para = line.strip()
            html_lines.append(f"<p>{inline_md(para)}</p>")
            i += 1
            continue

        i += 1

    return "\n".join(html_lines)


def inline_md(text: str) -> str:
    """Convert inline markdown (bold, italic, links) to HTML."""
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic (single *)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Links [text](url)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def extract_blog_content(md_text: str) -> str:
    """Extract content between ## Draft and ## Meta markers."""
    # Find content after "## Draft" heading
    draft_match = re.search(r"## Draft\n", md_text)
    meta_match  = re.search(r"\n## Meta\n", md_text)

    if not draft_match:
        print("ERROR: Could not find '## Draft' marker in blog post.")
        sys.exit(1)

    start = draft_match.end()
    end   = meta_match.start() if meta_match else len(md_text)
    return md_text[start:end].strip()


def build_footer_html(slug: str) -> str:
    """Return the social share + CTA footer with {slug} replaced."""
    footer = """<!-- Social Sharing Icons - Pure Tech Blue -->
<style>
.pt-social-share { display: flex; align-items: center; gap: 12px; padding: 20px 0; margin: 20px 0; border-top: 2px solid rgba(42, 147, 193, 0.3); flex-wrap: wrap; }
.pt-social-share span { font-weight: 600; color: #fff; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
.pt-social-share a { display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; background: rgba(42, 147, 193, 0.15); color: #2a93c1; text-decoration: none; transition: all 0.3s; font-size: 18px; border: none !important; }
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
</div>
<div class="blog-cta-block" style="margin-top: 40px; padding: 32px; background: rgba(42, 147, 193, 0.08); border: 1px solid rgba(42, 147, 193, 0.15); border-radius: 16px; text-align: center;">
<p style="font-size: 1.2rem; color: #ffffff; margin-bottom: 12px; font-weight: 600;">Ready to awaken your AI partner?</p>
<p>  <a href="https://purebrain.ai/purebrain-4/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content={slug}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #f1420b 0%, #d13608 100%); color: #ffffff !important; font-weight: 700; font-size: 1.1rem; border-radius: 8px; text-decoration: none; letter-spacing: 0.5px;">Start Your AI Partnership</a></p>
<p style="font-size: 0.95rem; color: rgba(255, 255, 255, 0.6); margin-top: 16px;">And if this perspective was valuable, <a href="https://purebrain.ai/blog/?utm_source=blog&utm_medium=cta&utm_campaign=newsletter&utm_content={slug}" style="color: #2a93c1 !important; text-decoration: underline;">subscribe to our newsletter</a> where I share insights on building AI relationships every week.</p>
</div>"""
    return footer.replace("{slug}", slug)


# ── Step 1: Upload banner image ──────────────────────────────────────────────
def upload_image(image_path: str) -> int:
    """Upload image to WP media library. Returns media ID."""
    print(f"\n[1/3] Uploading banner image: {image_path}")

    if not os.path.exists(image_path):
        print(f"ERROR: Banner file not found: {image_path}")
        sys.exit(1)

    filename = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        image_data = f.read()

    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "image/png",
    }

    resp = requests.post(
        f"{WP_URL}/media",
        headers=headers,
        data=image_data,
        timeout=60,
    )

    if resp.status_code not in (200, 201):
        print(f"ERROR uploading image: {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)

    media_data = resp.json()
    media_id   = media_data["id"]
    media_url  = media_data.get("source_url", "unknown")
    print(f"  Image uploaded. Media ID: {media_id}")
    print(f"  URL: {media_url}")
    return media_id


# ── Step 2: Create the post ──────────────────────────────────────────────────
def create_post(content_html: str, media_id: int) -> dict:
    """Create the WordPress post. Returns response dict."""
    print("\n[2/3] Creating blog post...")

    post_payload = {
        "title":          POST_TITLE,
        "content":        content_html,
        "status":         "publish",
        "slug":           SLUG,
        "featured_media": media_id,
        "excerpt":        SEO_DESC,
        "meta": {
            "_yoast_wpseo_metadesc": SEO_DESC,
        },
        "comment_status": "open",
        "ping_status":    "open",
    }

    resp = requests.post(
        f"{WP_URL}/posts",
        headers=HEADERS,
        json=post_payload,
        timeout=60,
    )

    if resp.status_code not in (200, 201):
        print(f"ERROR creating post: {resp.status_code}")
        print(resp.text[:1000])
        sys.exit(1)

    post_data = resp.json()
    print(f"  Post created. ID: {post_data['id']}")
    print(f"  URL: {post_data.get('link', 'unknown')}")
    return post_data


# ── Step 3: Verify the post is live ─────────────────────────────────────────
def verify_post(post_id: int, post_url: str):
    """Verify the post is publicly accessible."""
    print(f"\n[3/3] Verifying post is live...")

    resp = requests.get(
        f"{WP_URL}/posts/{post_id}",
        timeout=30,
    )

    if resp.status_code == 200:
        data   = resp.json()
        status = data.get("status", "unknown")
        title  = data.get("title", {}).get("rendered", "unknown")
        link   = data.get("link", post_url)
        print(f"  Status : {status}")
        print(f"  Title  : {title}")
        print(f"  Live URL: {link}")
        return link
    else:
        print(f"  WARNING: Could not verify (HTTP {resp.status_code})")
        return post_url


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("WordPress Blog Publisher - jareddsanborn.com")
    print("=" * 60)

    # Read blog post markdown
    blog_md_path = (
        "/home/jared/projects/AI-CIV/aether/docs/from-telegram/"
        "why-your-ai-pilot-is-failing-blog-post.md"
    )
    with open(blog_md_path, "r") as f:
        full_md = f.read()

    # Extract the draft content (between ## Draft and ## Meta)
    blog_content_md = extract_blog_content(full_md)
    print(f"\nExtracted {len(blog_content_md.split())} words of blog content.")

    # Convert to HTML
    blog_content_html = md_to_html(blog_content_md)

    # Build footer with slug substituted
    footer_html = build_footer_html(SLUG)

    # Combine post body + footer
    full_html = blog_content_html + "\n\n" + footer_html

    print(f"HTML content ready ({len(full_html)} chars).")

    # Upload image
    media_id = upload_image(BANNER_PATH)

    # Create post
    post_data = create_post(full_html, media_id)
    post_id   = post_data["id"]
    post_url  = post_data.get("link", "https://jareddsanborn.com/")

    # Verify live
    live_url = verify_post(post_id, post_url)

    print("\n" + "=" * 60)
    print("DONE")
    print(f"  Post ID : {post_id}")
    print(f"  Live URL: {live_url}")
    print("=" * 60)

    return {"post_id": post_id, "url": live_url, "media_id": media_id}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
