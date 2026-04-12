#!/usr/bin/env python3
"""
Dual Blog Publisher - Posts to BOTH purebrain.ai AND jaredsanborn.com

LOCKED IN per Jared's directive (2026-02-16):
- ALL blog posts go to BOTH sites simultaneously
- Upload featured image to both
- Return URLs from both for Bluesky thread
"""

import base64
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")


def get_auth_header(user: str, password: str) -> str:
    """Generate Basic Auth header."""
    credentials = f"{user}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def upload_media(api_base: str, headers: dict, image_path: Path, client: httpx.Client) -> int:
    """Upload featured image and return media ID."""
    url = f"{api_base}/media"

    # Read image
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # Prepare headers for upload
    upload_headers = {
        "Authorization": headers["Authorization"],
        "Content-Disposition": f'attachment; filename="{image_path.name}"',
        "Content-Type": "image/png" if image_path.suffix == ".png" else "image/jpeg"
    }

    response = client.post(url, headers=upload_headers, content=image_data)

    if response.status_code in [200, 201]:
        media_id = response.json().get("id")
        print(f"  ✅ Uploaded image, media ID: {media_id}")
        return media_id
    else:
        print(f"  ❌ Failed to upload image: {response.status_code}")
        print(f"     {response.text[:200]}")
        return None


def create_post(api_base: str, headers: dict, title: str, content: str,
                media_id: int, status: str, client: httpx.Client) -> dict:
    """Create a blog post."""
    url = f"{api_base}/posts"

    data = {
        "title": title,
        "content": content,
        "status": status,
        "featured_media": media_id if media_id else 0
    }

    response = client.post(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        post_data = response.json()
        return {
            "id": post_data.get("id"),
            "url": post_data.get("link"),
            "status": post_data.get("status")
        }
    else:
        print(f"  ❌ Failed to create post: {response.status_code}")
        print(f"     {response.text[:300]}")
        return None


def publish_to_both_sites(title: str, content_md: str, image_path: Path, status: str = "publish"):
    """
    Publish to BOTH purebrain.ai AND jaredsanborn.com

    Returns dict with both URLs.
    """

    # Convert markdown to HTML (basic conversion)
    content_html = markdown_to_html(content_md)

    results = {}

    # Site 1: jaredsanborn.com
    print("\n📝 Publishing to jaredsanborn.com...")
    try:
        api_base = "https://jareddsanborn.com/wp-json/wp/v2"
        headers = {
            "Authorization": get_auth_header(
                os.getenv("WORDPRESS_USER"),
                os.getenv("WORDPRESS_APP_PASSWORD")
            ),
            "Content-Type": "application/json"
        }

        with httpx.Client(timeout=60) as client:
            # Upload image
            media_id = upload_media(api_base, headers, image_path, client)

            # Create post
            result = create_post(api_base, headers, title, content_html, media_id, status, client)
            if result:
                results["jaredsanborn"] = result
                print(f"  ✅ Published: {result['url']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Site 2: purebrain.ai
    print("\n📝 Publishing to purebrain.ai...")
    try:
        api_base = "https://purebrain.ai/wp-json/wp/v2"
        headers = {
            "Authorization": get_auth_header(
                os.getenv("PUREBRAIN_WP_USER"),
                os.getenv("PUREBRAIN_WP_APP_PASSWORD")
            ),
            "Content-Type": "application/json"
        }

        with httpx.Client(timeout=60) as client:
            # Upload image
            media_id = upload_media(api_base, headers, image_path, client)

            # Create post
            result = create_post(api_base, headers, title, content_html, media_id, status, client)
            if result:
                results["purebrain"] = result
                print(f"  ✅ Published: {result['url']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    return results


# MANDATORY CTA - Added to ALL blog posts per Jared's directive (2026-02-16)
BLOG_CTA = """
<hr>
<p><strong>Ready to awaken your AI partner?</strong> <a href="https://purebrain.ai">Begin the process at PureBrain.ai</a></p>
<p>And if this perspective was valuable, <a href="https://www.linkedin.com/build-relation/newsletter-follow?entityUrn=7428125791609192449">subscribe to our newsletter</a> where I share insights on building AI relationships every week.</p>
"""

def markdown_to_html(md: str) -> str:
    """Basic markdown to HTML conversion."""
    import re

    html = md

    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Lists
    lines = html.split('\n')
    result = []
    in_list = False
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    if in_list:
        result.append('</ul>')
    html = '\n'.join(result)

    # Horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

    # Paragraphs (wrap non-tagged lines)
    lines = html.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            result.append(f'<p>{stripped}</p>')
        else:
            result.append(line)
    html = '\n'.join(result)

    # ALWAYS append the mandatory CTA
    html = html + BLOG_CTA

    return html


if __name__ == "__main__":
    # Test with the Enterprise AI blog post
    blog_dir = project_root / "exports/blog-content/2026-02-15-enterprise-ready-ai"

    # Read content
    content_path = blog_dir / "blog.md"
    with open(content_path) as f:
        content = f.read()

    # Extract title from first line
    lines = content.strip().split('\n')
    title = lines[0].replace('# ', '')

    # Image path
    image_path = blog_dir / "blog-header-corrected.png"

    print("=" * 60)
    print("DUAL BLOG PUBLISHER")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"Image: {image_path}")

    # Publish to both sites
    results = publish_to_both_sites(title, content, image_path, status="publish")

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for site, data in results.items():
        print(f"{site}: {data.get('url', 'FAILED')}")
