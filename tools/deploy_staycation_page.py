#!/usr/bin/env python3
"""Deploy Staycation Breaks AI Blueprint to purebrain.ai as a password-gated page."""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load credentials
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = os.getenv('PUREBRAIN_WP_USER', 'Aether')
WP_APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD')

if not WP_APP_PASSWORD:
    print("ERROR: PUREBRAIN_WP_APP_PASSWORD not found in .env")
    sys.exit(1)

# Read the HTML file
html_path = '/home/jared/projects/AI-CIV/aether/exports/client-marketing/staycation-breaks/graham-martin-ai-blueprint.html'
with open(html_path, 'r', encoding='utf-8') as f:
    raw_html = f.read()

print(f"Read HTML file: {len(raw_html)} characters")

# Wrap in wp:html block (per WP HTML DEPLOYMENT RULE)
wrapped_content = f"<!-- wp:html -->\n{raw_html}\n<!-- /wp:html -->"

print(f"Wrapped content: {len(wrapped_content)} characters")

# WordPress API endpoint
WP_API = "https://purebrain.ai/wp-json/wp/v2/pages"

# Page payload
payload = {
    "title": "PureBrain for Staycation Breaks",
    "slug": "purebrain-for-staycation-breaks",
    "content": wrapped_content,
    "status": "publish",
    "password": "StaycationAI2026",
    "template": "",  # default template, NOT elementor_canvas
}

print("\nDeploying to WordPress...")
print(f"  Title: {payload['title']}")
print(f"  Slug: {payload['slug']}")
print(f"  Status: {payload['status']}")
print(f"  Password protected: Yes (StaycationAI2026)")
print(f"  Template: default")

response = requests.post(
    WP_API,
    json=payload,
    auth=(WP_USER, WP_APP_PASSWORD),
    headers={"Content-Type": "application/json"},
    timeout=60
)

print(f"\nHTTP Status: {response.status_code}")

if response.status_code in (200, 201):
    data = response.json()
    page_id = data.get('id')
    page_link = data.get('link')
    page_slug = data.get('slug')
    page_status = data.get('status')
    page_title = data.get('title', {}).get('rendered', '')

    print("\n=== DEPLOYMENT SUCCESS ===")
    print(f"Page ID: {page_id}")
    print(f"Title: {page_title}")
    print(f"Slug: {page_slug}")
    print(f"Status: {page_status}")
    print(f"URL: {page_link}")
    print(f"Password: StaycationAI2026")
    print(f"Template: {data.get('template', 'default')}")

    # Write summary for verification
    summary = {
        "page_id": page_id,
        "url": page_link,
        "slug": page_slug,
        "status": page_status,
        "password": "StaycationAI2026",
        "template": data.get('template', ''),
        "title": page_title,
    }
    with open('/home/jared/projects/AI-CIV/aether/exports/client-marketing/staycation-breaks/deployment-result.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print("\nResult saved to exports/client-marketing/staycation-breaks/deployment-result.json")

else:
    print(f"\nERROR: Deployment failed")
    print(f"Response body: {response.text[:2000]}")
    sys.exit(1)
