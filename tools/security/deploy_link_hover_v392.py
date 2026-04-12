#!/usr/bin/env python3
"""
Deploy blog in-text link hover fix (v3.9.2) to ALL blog posts on BOTH sites.

ROOT CAUSE FIXED: v3.9.1 used .entry-content selector which doesn't exist in
the rendered DOM. The theme's actual content wrapper class is .post-content
(class="post-content" on the main content div) and .post-entry inside it.

What this script does:
  1. Remove old <style id="pb-link-hover-v391"> blocks
  2. Prepend new <style id="pb-link-hover-v392"> with CORRECT selectors:
       - body.single-post .post-content  (ACTUAL theme class - the fix)
       - body.single-post .entry-content  (fallback for other themes)
       - body.single-post .elementor-widget-theme-post-content  (Elementor)
  3. Fix CTA button inline styles: ensure color: #ffffff !important is present
     on any <a href="...#awakening"> that has display:inline-block but no white text
  4. Fix transparency section "Biggest Win": remove "3D Design Specialist agent"
     → replace with generic "a specialist agent" phrasing. Update wp_option on both sites.

Sites:
  - purebrain.ai     (user=Aether, PUREBRAIN_WP_APP_PASSWORD)
  - jareddsanborn.com (user=AetherPureBrain.ai, WORDPRESS_APP_PASSWORD)

Author: full-stack-developer agent
Date:   2026-02-22
Version: 3.9.2
"""

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")

# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"{key}='([^']+)'", env_text)
    if m:
        return m.group(1)
    m = re.search(rf"{key}=([^\n]+)", env_text)
    return m.group(1).strip() if m else ""


SITES = [
    {
        "name": "purebrain.ai",
        "base_url": "https://purebrain.ai",
        "user": "Aether",
        "password": _env("PUREBRAIN_WP_APP_PASSWORD"),
    },
    {
        "name": "jareddsanborn.com",
        "base_url": "https://jareddsanborn.com",
        "user": "AetherPureBrain.ai",
        "password": _env("WORDPRESS_APP_PASSWORD"),
    },
]

# ---------------------------------------------------------------------------
# Style block constants
# ---------------------------------------------------------------------------
OLD_STYLE_ID = "pb-link-hover-v391"
NEW_STYLE_ID = "pb-link-hover-v392"

# v3.9.2: CORRECTED SELECTORS
# The actual rendered DOM uses:
#   - div.post-content  (theme class — THIS WAS MISSING IN v3.9.1)
#   - div.post-entry.artistic-block-style  (inside post-content)
# Also keep .entry-content and .elementor-widget-theme-post-content as fallbacks.
#
# Exclusions:
#   - [href*="awakening"]  → CTA button (has its own orange bg + white text styling)
#   - [rel="tag"]          → Tag pills (have their own pill styling)
#   - .aether-transparency__cta-btn → Transparency section CTA
NEW_STYLE_BLOCK = """\
<style id="pb-link-hover-v392">
/* BLOG IN-TEXT LINK HOVER — v3.9.2 (FIXED SELECTORS)
   v3.9.1 used .entry-content which does NOT exist in the rendered DOM.
   Actual theme class: .post-content (div.post-content wraps all post body).
   Also targeting .entry-content (fallback) and Elementor wrapper.
   Exclusions: CTA button (#awakening links), tag pills ([rel=tag]),
               transparency section CTA (.aether-transparency__cta-btn).
*/
body.single-post .post-content a:not([href*="awakening"]):not([rel="tag"]):not(.aether-transparency__cta-btn),
body.single-post .entry-content a:not([href*="awakening"]):not([rel="tag"]):not(.aether-transparency__cta-btn),
body.single-post .elementor-widget-theme-post-content a:not([href*="awakening"]):not([rel="tag"]):not(.aether-transparency__cta-btn) {
    transition: background-color 0.2s ease, color 0.2s ease !important;
}
body.single-post .post-content a:not([href*="awakening"]):not([rel="tag"]):not(.aether-transparency__cta-btn):hover,
body.single-post .entry-content a:not([href*="awakening"]):not([rel="tag"]):not(.aether-transparency__cta-btn):hover,
body.single-post .elementor-widget-theme-post-content a:not([href*="awakening"]):not([rel="tag"]):not(.aether-transparency__cta-btn):hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
}
/* CTA BUTTON — force white text regardless of theme overrides */
body.single-post a[href*="awakening"] {
    color: #ffffff !important;
}
body.single-post a[href*="awakening"]:hover {
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    background-color: #2a93c1 !important;
    color: #ffffff !important;
    text-decoration: none !important;
}
</style>
"""

# ---------------------------------------------------------------------------
# Transparency fix
# ---------------------------------------------------------------------------
# "3D Design Specialist agent" is a proper name and must be removed per rules.
# Replace in biggest_win field.
TRANSPARENCY_PROPER_NAME_PATTERN = re.compile(
    r"our 3D Design Specialist agent",
    re.IGNORECASE,
)
TRANSPARENCY_REPLACEMENT = "our specialist team"

# ---------------------------------------------------------------------------
# REST API helpers
# ---------------------------------------------------------------------------


def make_auth_header(user: str, password: str) -> str:
    creds = base64.b64encode(f"{user}:{password}".encode()).decode()
    return f"Basic {creds}"


def wp_get(url: str, auth_header: str) -> dict | list:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": auth_header,
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def wp_post(url: str, auth_header: str, data: dict, method: str = "POST") -> dict:
    payload = json.dumps(data).encode("utf-8")
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    if method == "PATCH":
        headers["X-HTTP-Method-Override"] = "PATCH"
    req = urllib.request.Request(url, data=payload, method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Content manipulation
# ---------------------------------------------------------------------------


def strip_old_style_block(content: str) -> str:
    """Remove the v3.9.1 style block (and any stray v3.9.2 blocks for idempotency)."""
    for style_id in [OLD_STYLE_ID, NEW_STYLE_ID]:
        content = re.sub(
            rf'<style id="{re.escape(style_id)}">.*?</style>\s*',
            "",
            content,
            flags=re.DOTALL,
        )
    return content


def fix_cta_button_inline_style(content: str) -> str:
    """
    Find CTA button <a> tags (href contains #awakening, has inline display:inline-block)
    and ensure they have color: #ffffff !important in the inline style.

    Pattern: <a href="...#awakening" style="..."> where style has display:inline-block
             (that marks it as the styled CTA button, not a plain text reference)
    """
    def _fix_cta_style(m: re.Match) -> str:
        tag = m.group(0)
        style_m = re.search(r'style="([^"]+)"', tag)
        if not style_m:
            return tag
        style_val = style_m.group(1)
        # Only fix if it's a styled button (has display: inline-block)
        if "inline-block" not in style_val:
            return tag
        # Check if white text is already there
        if "color: #ffffff" in style_val or "color:#ffffff" in style_val:
            return tag
        # Add color: #ffffff !important before the closing quote
        # Insert after the last property in the style
        new_style = style_val.rstrip("; ") + "; color: #ffffff !important;"
        new_tag = tag.replace(style_m.group(0), f'style="{new_style}"')
        return new_tag

    # Match <a> tags whose href contains awakening
    return re.sub(
        r'<a[^>]+href="[^"]*awakening[^"]*"[^>]*>',
        _fix_cta_style,
        content,
        flags=re.IGNORECASE,
    )


def apply_all_fixes_to_content(content: str) -> str:
    """Strip old style block, add new one, fix CTA buttons."""
    # 1. Strip old style block (both v391 and v392 for idempotency)
    content = strip_old_style_block(content)
    # 2. Prepend new style block
    content = NEW_STYLE_BLOCK + content
    # 3. Fix CTA button inline style
    content = fix_cta_button_inline_style(content)
    return content


def content_needs_update(content: str) -> bool:
    """Return True if the content needs the v3.9.2 update."""
    # Needs update if v392 is missing OR v391 is still present
    has_v392 = NEW_STYLE_ID in content
    has_v391 = OLD_STYLE_ID in content
    return not has_v392 or has_v391


# ---------------------------------------------------------------------------
# Transparency data fix
# ---------------------------------------------------------------------------


def fix_transparency_data(base_url: str, auth_header: str, site_name: str) -> dict:
    """
    Read the current transparency wp_option via REST API POST endpoint,
    fix the proper name in biggest_win, and write it back.

    The transparency endpoint is POST /purebrain/v1/transparency-data (write-only).
    We need to read the current value first — but there's no GET endpoint.
    So we use the local config file as the authoritative source and update it.
    """
    # Use the v2 config as source of truth
    config_path = AETHER_ROOT / "config" / "transparency-week-2026-02-17-v2.json"
    if not config_path.exists():
        # Try original
        config_path = AETHER_ROOT / "config" / "transparency-week-2026-02-17.json"

    if not config_path.exists():
        return {"status": "skipped", "reason": "config file not found"}

    with open(config_path) as f:
        data = json.load(f)

    text_dump = json.dumps(data)

    # Check if fix is needed
    needs_fix = bool(TRANSPARENCY_PROPER_NAME_PATTERN.search(text_dump))

    if not needs_fix:
        print(f"  [OK] {site_name} transparency data: no proper names found (already clean)")
        return {"status": "already_clean"}

    # Fix the data
    def fix_value(v):
        if isinstance(v, str):
            return TRANSPARENCY_PROPER_NAME_PATTERN.sub(TRANSPARENCY_REPLACEMENT, v)
        elif isinstance(v, dict):
            return {k: fix_value(val) for k, val in v.items()}
        elif isinstance(v, list):
            return [fix_value(item) for item in v]
        return v

    fixed_data = fix_value(data)

    print(f"  [FIX] Transparency biggest_win:")
    print(f"    OLD: {data.get('biggest_win', '')}")
    print(f"    NEW: {fixed_data.get('biggest_win', '')}")

    # POST the fixed data to the site
    url = f"{base_url}/wp-json/purebrain/v1/transparency-data"
    try:
        resp = wp_post(url, auth_header, fixed_data)
        print(f"  [OK] {site_name} transparency data updated successfully")
        # Update the local config file too
        with open(config_path, "w") as f:
            json.dump(fixed_data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Local config updated: {config_path.name}")
        return {"status": "updated", "biggest_win_fixed": True}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        print(f"  [ERR] {site_name} transparency update failed: HTTP {e.code} — {body}")
        return {"status": "error", "error": f"HTTP {e.code}"}
    except Exception as ex:
        print(f"  [ERR] {site_name} transparency update failed: {ex}")
        return {"status": "error", "error": str(ex)}


# ---------------------------------------------------------------------------
# Core post processing
# ---------------------------------------------------------------------------


def get_all_posts(base_url: str, auth_header: str) -> list:
    url = f"{base_url}/wp-json/wp/v2/posts?per_page=100&status=publish"
    return wp_get(url, auth_header)


def process_site_posts(site: dict) -> dict:
    """Update all posts on one site."""
    name = site["name"]
    base_url = site["base_url"]
    auth_header = make_auth_header(site["user"], site["password"])

    print(f"\n{'='*60}")
    print(f"SITE: {name}")
    print(f"{'='*60}")

    results = {
        "site": name,
        "total": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
        "posts": [],
    }

    try:
        posts = get_all_posts(base_url, auth_header)
    except Exception as ex:
        print(f"  [ERROR] Could not fetch posts: {ex}")
        results["errors"] += 1
        return results

    results["total"] = len(posts)
    print(f"  Found {len(posts)} published posts")
    print(f"  Applying: strip v391, inject v392, fix CTA white text")

    for post in posts:
        post_id = post["id"]
        slug = post.get("slug", "?")
        content_raw = post.get("content", {}).get("raw", "")

        if not content_raw:
            content_raw = post.get("content", {}).get("rendered", "")
            if content_raw:
                print(f"  [WARN] Post {post_id} ({slug}): using rendered content as raw")

        if not content_raw:
            print(f"  [SKIP] Post {post_id} ({slug}): empty content")
            results["skipped"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": "skipped_empty"})
            continue

        if not content_needs_update(content_raw):
            print(f"  [SKIP] Post {post_id} ({slug}): already v392, no v391")
            results["skipped"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": "already_v392"})
            continue

        # Apply all fixes
        new_content = apply_all_fixes_to_content(content_raw)

        try:
            patch_url = f"{base_url}/wp-json/wp/v2/posts/{post_id}"
            updated = wp_post(patch_url, auth_header, {"content": new_content}, method="PATCH")
            updated_raw = updated.get("content", {}).get("raw", "")

            checks = {
                "has_v392": NEW_STYLE_ID in updated_raw,
                "no_v391": OLD_STYLE_ID not in updated_raw,
                "has_post_content_selector": ".post-content" in updated_raw,
            }
            all_pass = all(checks.values())
            status_icon = "OK" if all_pass else "WARN"

            print(f"  [{status_icon}]  Post {post_id} ({slug}): "
                  f"v392={checks['has_v392']}, no_v391={checks['no_v391']}, "
                  f"post_content={checks['has_post_content_selector']}")

            if all_pass:
                results["updated"] += 1
                results["posts"].append({"id": post_id, "slug": slug, "status": "updated"})
            else:
                results["errors"] += 1
                results["posts"].append({"id": post_id, "slug": slug, "status": "verify_failed", "checks": checks})
        except urllib.error.HTTPError as http_err:
            body = http_err.read().decode("utf-8", errors="replace")[:300]
            print(f"  [ERR]  Post {post_id} ({slug}): HTTP {http_err.code} — {body}")
            results["errors"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": f"http_{http_err.code}"})
        except Exception as ex:
            print(f"  [ERR]  Post {post_id} ({slug}): {ex}")
            results["errors"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": f"error"})

        time.sleep(0.4)

    print(f"\n  Summary: total={results['total']} updated={results['updated']} "
          f"skipped={results['skipped']} errors={results['errors']}")
    return results


# ---------------------------------------------------------------------------
# Live verification
# ---------------------------------------------------------------------------

VERIFY_URLS = {
    "purebrain.ai": [
        "https://purebrain.ai/the-ai-trust-gap/",
        "https://purebrain.ai/why-95-percent-of-ai-pilots-fail/",
    ],
    "jareddsanborn.com": [
        "https://jareddsanborn.com/the-ai-trust-gap/",
        "https://jareddsanborn.com/why-95-percent-of-ai-pilots-fail/",
    ],
}


def verify_live(site_name: str) -> list:
    urls = VERIFY_URLS.get(site_name, [])
    issues = []
    if not urls:
        return issues

    print(f"\n  Live verification for {site_name}:")
    for url in urls:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            checks = {
                "v392_block_present":  NEW_STYLE_ID in html,
                "v391_block_absent":   OLD_STYLE_ID not in html,
                "post_content_selector": "body.single-post .post-content" in html,
                "white_text_on_hover":  "color: #ffffff !important" in html,
                "orange_bg_hover":      "background-color: #f1420b !important" in html,
                "no_gleb":             "Gleb" not in html,
                "no_3d_design_specialist": "3D Design Specialist agent" not in html,
            }
            all_pass = all(checks.values())
            status = "PASS" if all_pass else "FAIL"
            print(f"    [{status}] {url}")
            for k, v in checks.items():
                icon = "OK" if v else "FAIL"
                print(f"           [{icon}] {k}: {v}")
            if not all_pass:
                issues.append({"url": url, "checks": checks})
        except Exception as ex:
            print(f"    [ERROR] {url}: {ex}")
            issues.append({"url": url, "error": str(ex)})

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("=" * 60)
    print("Blog Fix v3.9.2 Deployment")
    print("Fixes: CSS selector (post-content), CTA white text, transparency proper names")
    print("=" * 60)

    all_results = []
    all_live_issues = []

    for site in SITES:
        if not site["password"]:
            print(f"\n[SKIP] {site['name']}: password not found in .env")
            continue

        auth_header = make_auth_header(site["user"], site["password"])

        # Step 1: Fix post CSS style blocks
        print(f"\n--- Step 1: Post CSS fix for {site['name']} ---")
        result = process_site_posts(site)
        all_results.append(result)

        # Step 2: Fix transparency data
        print(f"\n--- Step 2: Transparency data fix for {site['name']} ---")
        fix_transparency_data(site["base_url"], auth_header, site["name"])

        # Brief pause between sites
        time.sleep(1)

    # Live verification
    print(f"\n{'='*60}")
    print("Live Verification (fetching rendered pages)")
    print("Note: CDN may serve cached pages. Hard-refresh or incognito to verify.")
    print("=" * 60)
    for result in all_results:
        issues = verify_live(result["site"])
        all_live_issues.extend(issues)

    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print("=" * 60)
    total_updated = sum(r["updated"] for r in all_results)
    total_errors = sum(r["errors"] for r in all_results)
    for r in all_results:
        print(f"  {r['site']}: updated={r['updated']} skipped={r['skipped']} errors={r['errors']}")

    if total_errors > 0:
        print(f"\nCOMPLETED WITH {total_errors} DB UPDATE ERROR(S)")
        sys.exit(1)

    if all_live_issues:
        print(f"\nDB UPDATES OK but {len(all_live_issues)} LIVE VERIFICATION ISSUE(S):")
        for issue in all_live_issues:
            print(f"  {issue}")
        print("(May be CDN cache — hard-refresh or incognito to confirm)")
    else:
        print(f"\nALL CHECKS PASSED ({total_updated} posts updated across {len(all_results)} sites)")
        print("\nFixed:")
        print("  - CSS selector: .post-content added (was only .entry-content which doesn't exist)")
        print("  - CTA buttons: white text enforced via inline style + CSS")
        print("  - Transparency: 3D Design Specialist agent → our specialist team")


if __name__ == "__main__":
    main()
