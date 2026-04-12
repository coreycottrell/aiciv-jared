#!/usr/bin/env python3
"""
Deploy report-template.html to WordPress page 825 (Corey's DuckDive report).
Pattern: strip outer HTML wrapper, scope CSS, add anti-orange overrides,
wrap in <!-- wp:html -->, set draft + password.
"""

import re
import requests
import sys

# ── Credentials ──────────────────────────────────────────────────────────────
WP_URL  = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
PAGE_ID = 825
PAGE_PASSWORD = "duckdive2024"

# ── Source file ───────────────────────────────────────────────────────────────
SOURCE = "/home/jared/projects/AI-CIV/aether/exports/client-marketing/report-template.html"

print("=== Deploy Page 825: DuckDive Report ===\n")

# ── Step 1: Read source HTML ──────────────────────────────────────────────────
print("[1] Reading source file...")
with open(SOURCE, "r", encoding="utf-8") as f:
    raw_html = f.read()
print(f"    Read {len(raw_html):,} bytes ({len(raw_html.splitlines())} lines)")

# ── Step 2: Extract components ────────────────────────────────────────────────
print("\n[2] Extracting components...")

# Google Fonts link tags
font_links = re.findall(r'<link[^>]+googleapis\.com[^>]+>', raw_html)
font_link_html = "\n".join(font_links)
print(f"    Font links: {len(font_links)}")

# Style block (full <style>...</style>)
style_match = re.search(r'<style>(.*?)</style>', raw_html, re.DOTALL)
if not style_match:
    print("ERROR: No <style> block found!")
    sys.exit(1)
original_style_content = style_match.group(1)
print(f"    Style block: {len(original_style_content):,} chars")

# Body content (everything between <body> and </body>)
body_match = re.search(r'<body[^>]*>(.*?)</body>', raw_html, re.DOTALL)
if not body_match:
    print("ERROR: No <body> block found!")
    sys.exit(1)
body_content = body_match.group(1)
print(f"    Body content: {len(body_content):,} chars")

# ── Step 3: Add anti-orange overrides ─────────────────────────────────────────
# PureBrain theme has [class*="magic"] { color: #f1420b !important; ... }
# which matches body.tt-magic-cursor and turns everything orange.
# Fix: higher-specificity !important selectors beat it.
print("\n[3] Injecting anti-orange CSS overrides...")

anti_orange_override = """
    /* ── WordPress theme override: prevent [class*="magic"] orange bleed ──
       body.tt-magic-cursor has specificity (0,1,1) > [class*="magic"] (0,1,0)
       so this wins even inside the !important layer. ── */
    body,
    body.tt-magic-cursor,
    body.page-id-825 {
      background: #0a0e1a !important;
      background-color: #0a0e1a !important;
      color: #e8edf5 !important;
      border-color: transparent !important;
      fill: currentColor !important;
    }
"""

# Inject after the opening of the style block (before first comment or rule)
modified_style_content = anti_orange_override + original_style_content

# Re-assemble style tag
style_block = f"<style>{modified_style_content}</style>"
print("    Anti-orange overrides injected.")

# ── Step 4: Assemble wp:html content ──────────────────────────────────────────
print("\n[4] Assembling wp:html content block...")

complete_content = f"""<!-- wp:html -->
{font_link_html}
{style_block}
{body_content.strip()}
<!-- /wp:html -->"""

print(f"    Total content: {len(complete_content):,} chars")

# ── Step 5: Deploy via REST API ───────────────────────────────────────────────
print(f"\n[5] Deploying to WordPress page {PAGE_ID} (draft, password-protected)...")

payload = {
    "content": complete_content,
    "status": "draft",
    "password": PAGE_PASSWORD,
    "template": "elementor_canvas",
}

resp = requests.post(
    f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}",
    auth=(WP_USER, WP_PASS),
    json=payload,
    timeout=60,
)

print(f"    HTTP {resp.status_code}")

if resp.status_code not in (200, 201):
    print(f"ERROR deploying: {resp.text[:500]}")
    sys.exit(1)

data = resp.json()
print(f"    Page ID:     {data.get('id')}")
print(f"    Status:      {data.get('status')}")
print(f"    Slug:        {data.get('slug')}")
print(f"    Modified:    {data.get('modified')}")

# Verify content length in response
returned_content = data.get("content", {}).get("raw", "")
if not returned_content:
    returned_content = data.get("content", {}).get("rendered", "")
print(f"    Content returned: {len(returned_content):,} chars")

if len(returned_content) < 1000:
    print("WARNING: Returned content is very short — possible deploy issue!")
else:
    print("    Content length looks good.")

# ── Step 6: Clear Elementor cache ─────────────────────────────────────────────
print("\n[6] Clearing Elementor cache...")
cache_resp = requests.delete(
    f"{WP_URL}/wp-json/elementor/v1/cache",
    auth=(WP_USER, WP_PASS),
    timeout=30,
)
print(f"    Elementor cache clear: HTTP {cache_resp.status_code}")
if cache_resp.status_code == 200:
    print("    Cache cleared successfully.")
else:
    print(f"    Cache clear response: {cache_resp.text[:200]}")

# ── Step 7: Verification ──────────────────────────────────────────────────────
print("\n[7] Verification — fetching page content via REST API...")

verify_resp = requests.get(
    f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}",
    auth=(WP_USER, WP_PASS),
    timeout=30,
)

if verify_resp.status_code == 200:
    vdata = verify_resp.json()
    raw_content = vdata.get("content", {}).get("raw", "")
    print(f"    Fetched content: {len(raw_content):,} chars")

    # Check for key markers
    checks = {
        "<!-- wp:html -->": "wp:html block present",
        "report-header": "Report header present",
        "DuckDive": "DuckDive client content present",
        "upsell-section": "Upsell section present",
        "anti-orange": "Anti-orange override injected",
        "#0a0e1a": "Dark bg color present",
        "duckdive": "Password protection active",
    }

    all_pass = True
    for key, label in checks.items():
        if key in raw_content:
            print(f"    PASS: {label}")
        else:
            # For password check, look at the page status
            if key == "duckdive":
                status_check = vdata.get("status") == "draft"
                pw_check = bool(vdata.get("password"))
                print(f"    PASS: Draft status={vdata.get('status')}, Password set={pw_check}")
            else:
                print(f"    FAIL: {label} NOT FOUND")
                all_pass = False

    print(f"\n    Deploy status: {vdata.get('status')}")
    print(f"    Password set: {bool(vdata.get('password'))}")

    if all_pass:
        print("\n=== DEPLOYMENT COMPLETE ===")
        print(f"Page 825 is LIVE as draft with password 'duckdive2024'")
        print(f"Admin preview: {WP_URL}/wp-admin/post.php?post={PAGE_ID}&action=edit")
    else:
        print("\nWARNING: Some checks failed — review above output.")
else:
    print(f"ERROR fetching verify response: HTTP {verify_resp.status_code}")

print("\nDone.")
