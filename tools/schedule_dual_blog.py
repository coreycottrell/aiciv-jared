#!/usr/bin/env python3
"""
Dual Blog Scheduler - Schedule posts to both jareddsanborn.com and purebrain.ai
Usage: python3 tools/schedule_dual_blog.py "Title" content.md image.png "2026-02-16T14:00:00"
"""

import sys
import os
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

def load_env():
    """Load environment variables from .env file"""
    env_vars = {}
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars

def upload_image(site_url, auth, image_path):
    """Upload image to WordPress and return media ID"""
    filename = os.path.basename(image_path)

    with open(image_path, 'rb') as img:
        response = requests.post(
            f'{site_url}/wp-json/wp/v2/media',
            auth=auth,
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'image/png'
            },
            data=img.read()
        )

    if response.status_code == 201:
        return response.json().get('id')
    else:
        print(f"  Image upload error: {response.status_code}")
        print(f"  Response: {response.text}")
    return None

def schedule_post(site_url, auth, title, content, publish_datetime, image_id=None, template=None):
    """Schedule a blog post for future publication"""
    post_data = {
        'title': title,
        'content': content,
        'status': 'future',  # WordPress uses 'future' status for scheduled posts
        'date': publish_datetime  # ISO 8601 format in UTC
    }

    if image_id:
        post_data['featured_media'] = image_id

    if template:
        post_data['template'] = template

    response = requests.post(
        f'{site_url}/wp-json/wp/v2/posts',
        auth=auth,
        json=post_data
    )

    if response.status_code == 201:
        return response.json()
    else:
        print(f"  Create post error: {response.status_code}")
        print(f"  Response: {response.text}")
    return None

def schedule_to_both(title, content, publish_datetime, image_path=None):
    """Schedule post to both sites simultaneously"""
    env = load_env()

    # Site 1: jareddsanborn.com
    site1_url = 'https://jareddsanborn.com'
    site1_auth = HTTPBasicAuth(
        env.get('WORDPRESS_USER'),
        env.get('WORDPRESS_APP_PASSWORD')
    )

    # Site 2: purebrain.ai
    site2_url = 'https://purebrain.ai'
    site2_auth = HTTPBasicAuth(
        'Aether',
        env.get('PUREBRAIN_WP_APP_PASSWORD')
    )

    results = {'jareddsanborn.com': None, 'purebrain.ai': None}

    # Schedule to jareddsanborn.com
    print(f"\n📅 Scheduling to jareddsanborn.com for {publish_datetime}...")
    image1_id = None
    if image_path and os.path.exists(image_path):
        print("  Uploading image...")
        image1_id = upload_image(site1_url, site1_auth, image_path)
        if image1_id:
            print(f"  ✅ Image uploaded (ID: {image1_id})")

    post1 = schedule_post(site1_url, site1_auth, title, content, publish_datetime, image1_id)
    if post1:
        results['jareddsanborn.com'] = {
            'id': post1.get('id'),
            'url': post1.get('link'),
            'scheduled_for': post1.get('date'),
            'status': 'SCHEDULED'
        }
        print(f"  ✅ Scheduled: {post1.get('link')}")
        print(f"     Publishes at: {post1.get('date')}")
    else:
        results['jareddsanborn.com'] = {'status': 'FAILED'}
        print("  ❌ Failed to schedule")

    # Schedule to purebrain.ai
    print(f"\n📅 Scheduling to purebrain.ai for {publish_datetime}...")
    image2_id = None
    if image_path and os.path.exists(image_path):
        print("  Uploading image...")
        image2_id = upload_image(site2_url, site2_auth, image_path)
        if image2_id:
            print(f"  ✅ Image uploaded (ID: {image2_id})")

    post2 = schedule_post(site2_url, site2_auth, title, content, publish_datetime, image2_id)
    if post2:
        results['purebrain.ai'] = {
            'id': post2.get('id'),
            'url': post2.get('link'),
            'scheduled_for': post2.get('date'),
            'status': 'SCHEDULED'
        }
        print(f"  ✅ Scheduled: {post2.get('link')}")
        print(f"     Publishes at: {post2.get('date')}")
    else:
        results['purebrain.ai'] = {'status': 'FAILED'}
        print("  ❌ Failed to schedule")

    return results

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 schedule_dual_blog.py 'Title' content.md 'YYYY-MM-DDTHH:MM:SS' [image.png]")
        print("Example: python3 schedule_dual_blog.py 'My Post' blog.md '2026-02-16T14:00:00' header.png")
        print("Note: Time should be in UTC")
        sys.exit(1)

    title = sys.argv[1]
    content_file = sys.argv[2]
    publish_datetime = sys.argv[3]
    image_file = sys.argv[4] if len(sys.argv) > 4 else None

    # Validate datetime format
    try:
        datetime.fromisoformat(publish_datetime)
    except ValueError:
        print(f"Error: Invalid datetime format '{publish_datetime}'")
        print("Expected format: YYYY-MM-DDTHH:MM:SS (e.g., 2026-02-16T14:00:00)")
        sys.exit(1)

    with open(content_file, 'r') as f:
        content = f.read()

    results = schedule_to_both(title, content, publish_datetime, image_file)

    print("\n" + "="*60)
    print("SCHEDULING RESULTS:")
    print(json.dumps(results, indent=2))
