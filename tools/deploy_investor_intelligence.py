#!/usr/bin/env python3
"""Deploy Investor Intelligence page to purebrain.ai WordPress."""

import os
import sys
import json
import requests
from pathlib import Path

# Load env
env_path = Path("/home/jared/projects/AI-CIV/aether/.env")
env_vars = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("export ") and "=" in line:
            line = line[7:]  # strip "export "
        if "=" in line and not line.startswith("#"):
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            env_vars[key] = val

PASS = env_vars.get("PUREBRAIN_WP_APP_PASSWORD", "")
if not PASS:
    print("ERROR: PUREBRAIN_WP_APP_PASSWORD not found in .env")
    sys.exit(1)

print(f"Password found: {len(PASS)} chars")

# Read HTML file
html_path = Path("/home/jared/projects/AI-CIV/aether/exports/purebrain-investor-intelligence.html")
html_content = html_path.read_text(encoding="utf-8")
print(f"HTML file read: {len(html_content)} chars ({len(html_content)//1024}KB)")

# Wrap in wp:html block
wrapped_content = f"<!-- wp:html -->\n{html_content}\n<!-- /wp:html -->"
print(f"Wrapped content: {len(wrapped_content)} chars")

# WordPress API endpoint
WP_BASE = "https://purebrain.ai/wp-json/wp/v2"
auth = ("Aether", PASS)

# Check if page exists
print("\nChecking for existing page...")
resp = requests.get(
    f"{WP_BASE}/pages",
    params={"slug": "investor-intelligence"},
    auth=auth,
    timeout=30
)
existing = resp.json()
print(f"Existing pages with slug: {len(existing)}")

page_data = {
    "title": "Investor Intelligence — The Age of AI Agents",
    "slug": "investor-intelligence",
    "content": wrapped_content,
    "status": "publish",
    "template": "elementor_canvas",
}

if existing:
    # Update existing
    page_id = existing[0]["id"]
    print(f"Updating existing page ID: {page_id}")
    resp = requests.post(
        f"{WP_BASE}/pages/{page_id}",
        auth=auth,
        json=page_data,
        timeout=120
    )
else:
    # Create new
    print("Creating new page...")
    resp = requests.post(
        f"{WP_BASE}/pages",
        auth=auth,
        json=page_data,
        timeout=120
    )

print(f"\nResponse status: {resp.status_code}")

if resp.status_code in (200, 201):
    result = resp.json()
    page_id = result.get("id")
    page_link = result.get("link", "")
    page_slug = result.get("slug", "")
    page_status = result.get("status", "")
    page_template = result.get("template", "")
    print(f"SUCCESS!")
    print(f"  Page ID: {page_id}")
    print(f"  URL: {page_link}")
    print(f"  Slug: {page_slug}")
    print(f"  Status: {page_status}")
    print(f"  Template: {page_template}")
    print(f"\nLIVE_URL: {page_link}")
else:
    print(f"ERROR: {resp.status_code}")
    print(resp.text[:2000])
    sys.exit(1)
