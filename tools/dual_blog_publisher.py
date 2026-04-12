#!/usr/bin/env python3
"""
Dual Blog Publisher - Posts to both jareddsanborn.com and purebrain.ai
Usage: python3 tools/dual_blog_publisher.py "Title" content.md image.png
"""

import sys
import os
import requests
from requests.auth import HTTPBasicAuth
import json

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
    return None

def create_post(site_url, auth, title, content, image_id=None, status='publish', template=None):
    """Create a blog post"""
    post_data = {
        'title': title,
        'content': content,
        'status': status
    }

    if image_id:
        post_data['featured_media'] = image_id

    # Set template (e.g., 'elementor_canvas' for PureBrain posts)
    if template:
        post_data['template'] = template

    response = requests.post(
        f'{site_url}/wp-json/wp/v2/posts',
        auth=auth,
        json=post_data
    )

    if response.status_code == 201:
        return response.json()
    return None

def publish_to_both(title, content, image_path=None, status='publish'):
    """Publish post to both sites simultaneously"""
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
        env.get('PUREBRAIN_WP_APP_PASSWORD', 'I9jppb5dpNyfdQihehsBV0k7')
    )
    
    results = {'jareddsanborn.com': None, 'purebrain.ai': None}
    
    # Publish to jareddsanborn.com
    print(f"\n📝 Publishing to jareddsanborn.com...")
    image1_id = None
    if image_path and os.path.exists(image_path):
        print("  Uploading image...")
        image1_id = upload_image(site1_url, site1_auth, image_path)
    
    post1 = create_post(site1_url, site1_auth, title, content, image1_id, status)
    if post1:
        results['jareddsanborn.com'] = {
            'id': post1.get('id'),
            'url': post1.get('link'),
            'status': 'SUCCESS'
        }
        print(f"  ✅ Published: {post1.get('link')}")
    else:
        results['jareddsanborn.com'] = {'status': 'FAILED'}
        print("  ❌ Failed to publish")
    
    # Publish to purebrain.ai
    print(f"\n📝 Publishing to purebrain.ai...")
    image2_id = None
    if image_path and os.path.exists(image_path):
        print("  Uploading image...")
        image2_id = upload_image(site2_url, site2_auth, image_path)
    
    # Use default template - styling via Additional CSS (elementor_canvas removes too much)
    post2 = create_post(site2_url, site2_auth, title, content, image2_id, status)
    if post2:
        results['purebrain.ai'] = {
            'id': post2.get('id'),
            'url': post2.get('link'),
            'status': 'SUCCESS'
        }
        print(f"  ✅ Published: {post2.get('link')}")
    else:
        results['purebrain.ai'] = {'status': 'FAILED'}
        print("  ❌ Failed to publish")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 dual_blog_publisher.py 'Title' content.md [image.png]")
        sys.exit(1)
    
    title = sys.argv[1]
    content_file = sys.argv[2]
    image_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    with open(content_file, 'r') as f:
        content = f.read()
    
    results = publish_to_both(title, content, image_file)
    
    print("\n" + "="*50)
    print("RESULTS:")
    print(json.dumps(results, indent=2))
