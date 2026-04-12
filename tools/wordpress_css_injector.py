#!/usr/bin/env python3
"""
WordPress CSS Injector - Adds custom CSS via Customizer API
Bypasses Elementor HTML stripping by using site-wide CSS
"""

import os
import requests
from requests.auth import HTTPBasicAuth

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

def get_current_css(site_url, auth):
    """Get current custom CSS from WordPress"""
    response = requests.get(
        f'{site_url}/wp-json/wp/v2/settings',
        auth=auth
    )
    if response.status_code == 200:
        return response.json()
    return None

def inject_blog_page_css():
    """Inject CSS for blog page video background and icon"""
    env = load_env()

    site_url = 'https://purebrain.ai'
    auth = HTTPBasicAuth(
        'Aether',
        env.get('PUREBRAIN_WP_APP_PASSWORD', 'I9jppb5dpNyfdQihehsBV0k7')
    )

    # CSS that targets the blog page specifically
    blog_css = """
/* PureBrain Blog Page - Video Background & Icon */
/* Only applies to /blog page */
body.page-id-95 {
    position: relative;
    background: #0a0a0a !important;
}

/* Video background container */
body.page-id-95::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('https://res.cloudinary.com/dq06qxzhz/video/upload/v1770156001/Pure_Brain_Demo_Video_nyjoon.jpg') center/cover no-repeat;
    opacity: 0.3;
    z-index: -2;
    pointer-events: none;
}

/* Dark overlay */
body.page-id-95::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(10,10,10,0.9) 0%, rgba(20,30,40,0.85) 100%);
    z-index: -1;
    pointer-events: none;
}

/* Pure Tech icon badge - top right */
body.page-id-95 .elementor-location-header::after {
    content: '';
    position: fixed;
    top: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    background: url('https://purebrain.ai/wp-content/uploads/2026/02/cropped-cropped-MA1.BI-1.2.4-002-211107-Icon-PT.png') center/contain no-repeat;
    z-index: 9999;
    pointer-events: none;
    filter: drop-shadow(0 0 10px rgba(42,147,193,0.5));
}

/* Ensure content is readable */
body.page-id-95 .elementor-section {
    background: transparent !important;
}

body.page-id-95 .elementor-widget-container {
    color: #ffffff;
}

body.page-id-95 h1,
body.page-id-95 h2,
body.page-id-95 h3 {
    color: #ffffff !important;
}

body.page-id-95 p {
    color: rgba(255,255,255,0.9) !important;
}

body.page-id-95 a {
    color: #2a93c1 !important;
}

body.page-id-95 a:hover {
    color: #f1420b !important;
}
"""

    print("Attempting to inject CSS via WordPress REST API...")

    # Try to update via custom CSS endpoint
    # First, let's check what endpoints are available
    response = requests.get(f'{site_url}/wp-json/', auth=auth)

    if response.status_code == 200:
        print("Connected to WordPress API")

        # Try the settings endpoint
        settings = get_current_css(site_url, auth)
        if settings:
            print(f"Current settings retrieved: {list(settings.keys())}")

    # Alternative: Create a custom CSS post
    # WordPress stores custom CSS in wp_posts with post_type = 'custom_css'
    css_post = {
        'title': 'purebrain-blog-custom',
        'content': blog_css,
        'status': 'publish',
        'post_type': 'custom_css'
    }

    # Check if custom CSS post exists
    response = requests.get(
        f'{site_url}/wp-json/wp/v2/posts',
        auth=auth,
        params={'search': 'blog-page-custom-css', 'status': 'any'}
    )

    print(f"API Response: {response.status_code}")

    # Output the CSS for manual addition
    print("\n" + "="*60)
    print("CSS TO ADD VIA WORDPRESS CUSTOMIZER")
    print("="*60)
    print("\nGo to: Appearance > Customize > Additional CSS")
    print("Paste the following CSS:\n")
    print(blog_css)
    print("\n" + "="*60)

    # Save CSS to file for reference
    css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            'exports', 'purebrain-blog-custom.css')
    with open(css_path, 'w') as f:
        f.write(blog_css)
    print(f"\nCSS also saved to: {css_path}")

    return blog_css

if __name__ == "__main__":
    inject_blog_page_css()
