#!/usr/bin/env python3
"""
ST# — Brainiac Workshop Page Deployment
Date: 2026-03-12

Tasks:
1. Create NEW page /brainiac-training-workshop/ (workshop page)
2. Update EXISTING training page /brainiac-mastermind-training/ with workshop CTA section

Page IDs:
- Training page (existing):  1115
- Workshop page (new):       TBD (will be created)

Auth: Aether / PUREBRAIN_WP_APP_PASSWORD
"""

import json
import sys
import requests
from requests.auth import HTTPBasicAuth

WP_USER        = "Aether"
WP_APP_PASSWORD = "41w3 xWWZ 11em UXgj hjAF sx2T"
BASE_URL       = "https://purebrain.ai/wp-json/wp/v2"
TRAINING_PAGE_ID = 1115

auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)

WORKSHOP_HTML_FILE  = "/home/jared/projects/AI-CIV/aether/purebrain-site/public/brainiac-training-workshop/index.html"
TRAINING_UPDATED_FILE = "/tmp/training-page-updated.html"


def fetch_page(page_id):
    r = requests.get(
        f"{BASE_URL}/pages/{page_id}?context=edit",
        auth=auth,
        timeout=30
    )
    if r.status_code != 200:
        print(f"  ERROR fetching page {page_id}: HTTP {r.status_code}")
        print(f"  Response: {r.text[:300]}")
        return None
    try:
        return r.json()
    except Exception as e:
        print(f"  ERROR parsing JSON: {e}")
        print(f"  Response (first 200): {r.text[:200]}")
        return None


def create_page(title, slug, content, parent_id=None):
    payload = {
        "title":    title,
        "slug":     slug,
        "content":  content,
        "template": "elementor_canvas",
        "status":   "publish",
    }
    if parent_id:
        payload["parent"] = parent_id

    r = requests.post(
        f"{BASE_URL}/pages",
        auth=auth,
        json=payload,
        timeout=180
    )
    return r


def update_page(page_id, content):
    payload = {
        "content": content,
        "status":  "publish",
    }
    r = requests.post(
        f"{BASE_URL}/pages/{page_id}",
        auth=auth,
        json=payload,
        timeout=180
    )
    return r


def clear_elementor_cache():
    r = requests.delete(
        "https://purebrain.ai/wp-json/elementor/v1/cache",
        auth=auth,
        timeout=30
    )
    print(f"  Elementor cache clear: HTTP {r.status_code}")
    return r.status_code


def main():
    print("=" * 65)
    print("ST# Brainiac Workshop Deployment")
    print("=" * 65)

    # ─── STEP 1: Read workshop HTML ─────────────────────────────────
    print("\n[1] Reading workshop HTML file...")
    try:
        with open(WORKSHOP_HTML_FILE, 'r', encoding='utf-8') as f:
            workshop_content = f.read()
        print(f"    Workshop HTML: {len(workshop_content):,} chars")
    except FileNotFoundError:
        print(f"    FATAL: File not found: {WORKSHOP_HTML_FILE}")
        sys.exit(1)

    # Verify it starts with <!-- wp:html -->
    if not workshop_content.startswith("<!-- wp:html -->"):
        print("    WARNING: Workshop HTML does not start with <!-- wp:html --> — deploying as-is")
    else:
        print("    wp:html wrapper: FOUND")

    # ─── STEP 2: Read updated training page HTML ─────────────────────
    print("\n[2] Reading updated training page HTML (with CTA)...")
    try:
        with open(TRAINING_UPDATED_FILE, 'r', encoding='utf-8') as f:
            training_content = f.read()
        print(f"    Training HTML: {len(training_content):,} chars")
    except FileNotFoundError:
        print(f"    FATAL: File not found: {TRAINING_UPDATED_FILE}")
        print("    Run the build script first to generate /tmp/training-page-updated.html")
        sys.exit(1)

    if 'workshop-cta-section' not in training_content:
        print("    FATAL: workshop-cta-section CSS not found in training content")
        sys.exit(1)
    if 'Explore the Workshop' not in training_content:
        print("    FATAL: CTA button not found in training content")
        sys.exit(1)
    print("    Workshop CTA section: VERIFIED")

    # Wrap training content in wp:html block
    training_wp_content = f"<!-- wp:html -->\n{training_content}\n<!-- /wp:html -->"
    print(f"    Training content with wrapper: {len(training_wp_content):,} chars")

    # ─── STEP 3: Create the new workshop page ────────────────────────
    print("\n[3] Creating new workshop page /brainiac-training-workshop/...")
    r = create_page(
        title   = "Brainiac Workshop: From User to Director",
        slug    = "brainiac-training-workshop",
        content = workshop_content
    )
    print(f"    HTTP Status: {r.status_code}")

    if r.status_code not in (200, 201):
        print(f"    ERROR creating page: {r.text[:500]}")
        # Try to parse as JSON anyway
        try:
            err = r.json()
            if err.get('code') == 'term_exists':
                print("    Page slug already exists — may need to update instead of create")
            elif err.get('code') == 'rest_post_exists':
                print("    Page already exists at this slug")
        except:
            pass
        print("\n    Attempting to find existing page by slug...")
        r2 = requests.get(
            f"{BASE_URL}/pages?slug=brainiac-training-workshop",
            auth=auth, timeout=30
        )
        if r2.status_code == 200:
            try:
                pages = r2.json()
                if pages and isinstance(pages, list):
                    existing_id = pages[0]['id']
                    print(f"    Found existing page ID: {existing_id} — updating instead")
                    r = requests.post(
                        f"{BASE_URL}/pages/{existing_id}",
                        auth=auth,
                        json={"content": workshop_content, "status": "publish", "template": "elementor_canvas"},
                        timeout=180
                    )
                    print(f"    Update HTTP Status: {r.status_code}")
            except:
                pass

    try:
        resp = r.json()
        workshop_page_id  = resp.get('id')
        workshop_page_url = resp.get('link', '')
        print(f"    Workshop page ID:  {workshop_page_id}")
        print(f"    Workshop page URL: {workshop_page_url}")
    except:
        print(f"    Could not parse response JSON: {r.text[:200]}")
        workshop_page_id = None

    # ─── STEP 4: Update training page with workshop CTA ──────────────
    print(f"\n[4] Updating training page (ID: {TRAINING_PAGE_ID}) with workshop CTA...")
    r2 = update_page(TRAINING_PAGE_ID, training_wp_content)
    print(f"    HTTP Status: {r2.status_code}")

    if r2.status_code not in (200, 201):
        print(f"    ERROR updating training page: {r2.text[:500]}")
    else:
        try:
            resp2 = r2.json()
            print(f"    Training page updated: ID {resp2.get('id')}")
            print(f"    URL: {resp2.get('link', '')}")
        except:
            print("    Update response not parseable as JSON")

    # ─── STEP 5: Clear Elementor cache ───────────────────────────────
    print("\n[5] Clearing Elementor cache...")
    clear_elementor_cache()

    # ─── STEP 6: Save local files ─────────────────────────────────────
    print("\n[6] Saving updated training page HTML locally...")
    local_training_out = "/home/jared/projects/AI-CIV/aether/purebrain-site/public/brainiac-mastermind-training/index-updated.html"
    try:
        with open(local_training_out, 'w', encoding='utf-8') as f:
            f.write(training_wp_content)
        print(f"    Saved: {local_training_out}")
    except Exception as e:
        print(f"    Save error: {e}")

    # ─── STEP 7: Also save to cf-pages-deploy ─────────────────────────
    print("\n[7] Saving workshop page to cf-pages-deploy...")
    import os, shutil
    cf_workshop_dir = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-training-workshop"
    os.makedirs(cf_workshop_dir, exist_ok=True)
    shutil.copy(WORKSHOP_HTML_FILE, os.path.join(cf_workshop_dir, "index.html"))
    print(f"    Saved to: {cf_workshop_dir}/index.html")

    # ─── SUMMARY ──────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("DEPLOYMENT SUMMARY")
    print("=" * 65)
    print(f"  Workshop page ID:  {workshop_page_id or 'UNKNOWN (check manually)'}")
    print(f"  Workshop URL:      https://purebrain.ai/brainiac-training-workshop/")
    print(f"  Training page ID:  {TRAINING_PAGE_ID}")
    print(f"  Training URL:      https://purebrain.ai/brainiac-mastermind-training/")
    print(f"  Password:          brainiac2026")
    print(f"  CTA added:         Yes — links to /brainiac-training-workshop/")
    print()

    if workshop_page_id:
        print("NEXT STEPS:")
        print("  1. Visit https://purebrain.ai/brainiac-training-workshop/ in browser")
        print("  2. Enter password: brainiac2026")
        print("  3. Verify hero, curriculum, pricing, FAQ all render correctly")
        print("  4. Visit https://purebrain.ai/brainiac-mastermind-training/")
        print("  5. Enter password: brainiac2026")
        print("  6. Scroll down past modules to verify workshop CTA section appears")
        print("  7. Click 'Explore the Workshop' — should navigate to workshop page")
    print()


if __name__ == "__main__":
    main()
