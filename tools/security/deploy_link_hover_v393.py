#!/usr/bin/env python3
"""
Deploy blog comment section link hover fix (v3.9.3) to ALL blog posts on BOTH sites.

PROBLEM FIXED:
  v3.9.2 CSS only targets links inside .post-content / .entry-content /
  .elementor-widget-theme-post-content.
  The WordPress comment form area (#respond / .comment-respond) is OUTSIDE those
  wrappers, so "Leave a Reply" section links (log out?, cancel reply, etc.) still
  show orange text on orange background on hover — invisible.

WHAT THIS SCRIPT DOES:
  1. Remove old <style id="pb-link-hover-v392"> blocks from post content
  2. Prepend new <style id="pb-link-hover-v393"> that includes ALL v3.9.2 rules
     PLUS new #respond / .comment-respond rules covering:
       - body.single-post #respond a:hover
       - body.single-post .comment-respond a:hover
       - body.single-post .logged-in-as a:hover
       - body.single-post .comment-reply-title a:hover
  3. Clear Elementor cache on each site (DELETE /elementor/v1/cache)
  4. Live-verify at least 2 posts per site

EXCLUSIONS (same as v3.9.2):
  - [href*="awakening"]  → CTA button
  - [rel="tag"]          → Tag pills
  - .aether-transparency__cta-btn → Transparency section CTA
  - Nav links / footer links are NOT in #respond so no additional exclusions needed

Sites:
  - purebrain.ai     (user=Aether, PUREBRAIN_WP_APP_PASSWORD)
  - jareddsanborn.com (user=jared, WORDPRESS_APP_PASSWORD)

Author: full-stack-developer agent
Date:   2026-02-22
Version: 3.9.3
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
        "user": _env("WORDPRESS_USER"),  # AetherPureBrain.ai — from .env WORDPRESS_USER
        "password": _env("WORDPRESS_APP_PASSWORD"),
    },
]

# ---------------------------------------------------------------------------
# Style block constants
# ---------------------------------------------------------------------------
OLD_STYLE_ID = "pb-link-hover-v392"
NEW_STYLE_ID = "pb-link-hover-v393"

# v3.9.3: All v3.9.2 rules PLUS comment section (#respond) link hover rules.
# The #respond / .comment-respond area is OUTSIDE .post-content so v3.9.2
# selectors never targeted those links.
NEW_STYLE_BLOCK = """\
<style id="pb-link-hover-v393">
/* BLOG IN-TEXT LINK HOVER — v3.9.3
   Extends v3.9.2: adds comment form area (#respond) link hover rules.
   Links in "Leave a Reply" section are in #respond / .comment-respond,
   outside .post-content — so they need separate selectors.
   Exclusions: CTA (#awakening), tag pills ([rel=tag]), transparency CTA.
*/

/* === POST CONTENT LINKS (v3.9.2 rules — unchanged) === */
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

/* === CTA BUTTON — white text always === */
body.single-post a[href*="awakening"] {
    color: #ffffff !important;
}
body.single-post a[href*="awakening"]:hover {
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    background-color: #2a93c1 !important;
    color: #ffffff !important;
    text-decoration: none !important;
}

/* === COMMENT SECTION LINKS (v3.9.3 NEW) ===
   Covers: "Log out?" link in .logged-in-as,
           "Cancel reply" link in .comment-reply-title,
           any other links in the comment form / respond area.
   Nav links and footer links are NOT in #respond so no exclusion needed there.
*/
body.single-post #respond a,
body.single-post .comment-respond a,
body.single-post .logged-in-as a,
body.single-post .comment-reply-title a {
    transition: background-color 0.2s ease, color 0.2s ease !important;
}
body.single-post #respond a:hover,
body.single-post .comment-respond a:hover,
body.single-post .logged-in-as a:hover,
body.single-post .comment-reply-title a:hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
}
</style>
"""

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


def wp_delete(url: str, auth_header: str) -> dict:
    """Send a DELETE request (used for Elementor cache flush)."""
    headers = {
        "Authorization": auth_header,
        "User-Agent": "Mozilla/5.0",
    }
    req = urllib.request.Request(url, method="DELETE", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        return {"error": f"HTTP {e.code}", "body": body}
    except Exception as ex:
        return {"error": str(ex)}


# ---------------------------------------------------------------------------
# Content manipulation
# ---------------------------------------------------------------------------


def strip_old_style_block(content: str) -> str:
    """Remove v3.9.2 block (and any stray v3.9.3 blocks for idempotency)."""
    for style_id in [OLD_STYLE_ID, NEW_STYLE_ID]:
        content = re.sub(
            rf'<style id="{re.escape(style_id)}">.*?</style>\s*',
            "",
            content,
            flags=re.DOTALL,
        )
    return content


def apply_all_fixes_to_content(content: str) -> str:
    """Strip old style block and prepend the v3.9.3 block."""
    content = strip_old_style_block(content)
    content = NEW_STYLE_BLOCK + content
    return content


def content_needs_update(content: str) -> bool:
    """Return True if v3.9.3 is absent or v3.9.2 is still present."""
    has_v393 = NEW_STYLE_ID in content
    has_v392 = OLD_STYLE_ID in content
    return not has_v393 or has_v392


# ---------------------------------------------------------------------------
# Elementor cache flush
# ---------------------------------------------------------------------------


def flush_elementor_cache(base_url: str, auth_header: str, site_name: str):
    """Flush Elementor's PHP rendering cache via REST API DELETE."""
    url = f"{base_url}/wp-json/elementor/v1/cache"
    print(f"  Flushing Elementor cache at {url} ...")
    result = wp_delete(url, auth_header)
    if "error" in result:
        print(f"  [WARN] Elementor cache flush: {result}")
    else:
        print(f"  [OK] Elementor cache flushed: {result}")


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
    print(f"  Applying: strip v392, inject v393 (post-content + comment #respond rules)")

    for post in posts:
        post_id = post["id"]
        slug = post.get("slug", "?")
        content_raw = post.get("content", {}).get("raw", "")

        if not content_raw:
            content_raw = post.get("content", {}).get("rendered", "")
            if content_raw:
                print(f"  [WARN] Post {post_id} ({slug}): raw empty, using rendered")

        if not content_raw:
            print(f"  [SKIP] Post {post_id} ({slug}): empty content")
            results["skipped"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": "skipped_empty"})
            continue

        if not content_needs_update(content_raw):
            print(f"  [SKIP] Post {post_id} ({slug}): already v393, no v392")
            results["skipped"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": "already_v393"})
            continue

        new_content = apply_all_fixes_to_content(content_raw)

        try:
            patch_url = f"{base_url}/wp-json/wp/v2/posts/{post_id}"
            updated = wp_post(patch_url, auth_header, {"content": new_content}, method="PATCH")
            updated_raw = updated.get("content", {}).get("raw", "")

            checks = {
                "has_v393": NEW_STYLE_ID in updated_raw,
                "no_v392": OLD_STYLE_ID not in updated_raw,
                "has_respond_selector": "#respond a:hover" in updated_raw,
                "has_post_content_selector": ".post-content" in updated_raw,
            }
            all_pass = all(checks.values())
            status_icon = "OK" if all_pass else "WARN"

            print(
                f"  [{status_icon}]  Post {post_id} ({slug}): "
                f"v393={checks['has_v393']}, no_v392={checks['no_v392']}, "
                f"respond={checks['has_respond_selector']}, "
                f"post_content={checks['has_post_content_selector']}"
            )

            if all_pass:
                results["updated"] += 1
                results["posts"].append({"id": post_id, "slug": slug, "status": "updated"})
            else:
                results["errors"] += 1
                results["posts"].append(
                    {"id": post_id, "slug": slug, "status": "verify_failed", "checks": checks}
                )
        except urllib.error.HTTPError as http_err:
            body = http_err.read().decode("utf-8", errors="replace")[:300]
            print(f"  [ERR]  Post {post_id} ({slug}): HTTP {http_err.code} — {body}")
            results["errors"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": f"http_{http_err.code}"})
        except Exception as ex:
            print(f"  [ERR]  Post {post_id} ({slug}): {ex}")
            results["errors"] += 1
            results["posts"].append({"id": post_id, "slug": slug, "status": "error"})

        time.sleep(0.4)

    print(
        f"\n  Summary: total={results['total']} updated={results['updated']} "
        f"skipped={results['skipped']} errors={results['errors']}"
    )
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
                "v393_block_present":    NEW_STYLE_ID in html,
                "v392_block_absent":     OLD_STYLE_ID not in html,
                "respond_selector":      "#respond a:hover" in html,
                "comment_respond_selector": ".comment-respond a:hover" in html,
                "post_content_selector": "body.single-post .post-content" in html,
                "white_text_on_hover":   "color: #ffffff !important" in html,
                "orange_bg_hover":       "background-color: #f1420b !important" in html,
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
    print("Blog Fix v3.9.3 Deployment")
    print("Fixes: Comment section (#respond) link hover — white text on orange background")
    print("=" * 60)

    all_results = []
    all_live_issues = []

    for site in SITES:
        if not site["password"]:
            print(f"\n[SKIP] {site['name']}: password not found in .env")
            continue

        auth_header = make_auth_header(site["user"], site["password"])

        # Step 1: Fix post CSS style blocks
        print(f"\n--- Step 1: Inject v3.9.3 CSS into all posts on {site['name']} ---")
        result = process_site_posts(site)
        all_results.append(result)

        # Step 2: Flush Elementor cache
        print(f"\n--- Step 2: Flush Elementor cache on {site['name']} ---")
        flush_elementor_cache(site["base_url"], auth_header, site["name"])

        # Brief pause between sites
        time.sleep(1)

    # Live verification
    print(f"\n{'='*60}")
    print("Live Verification (fetching rendered pages)")
    print("Note: CDN may serve cached pages. Hard-refresh or incognito to verify if checks fail.")
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
        live_fails = [i for i in all_live_issues if "error" not in i]
        live_errors = [i for i in all_live_issues if "error" in i]
        print(f"\nDB UPDATES OK but {len(all_live_issues)} LIVE VERIFICATION ISSUE(S):")
        for issue in all_live_issues:
            print(f"  {issue}")
        print("(May be CDN cache — hard-refresh or incognito to confirm)")
    else:
        print(f"\nALL CHECKS PASSED ({total_updated} posts updated across {len(all_results)} sites)")
        print("\nFixed:")
        print("  - Comment form links (#respond / .comment-respond) now show white text on orange hover")
        print("  - 'Log out?' (.logged-in-as a) and 'Cancel reply' (.comment-reply-title a) covered")
        print("  - All v3.9.2 post-content rules retained")


if __name__ == "__main__":
    main()
