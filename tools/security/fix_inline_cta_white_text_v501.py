#!/usr/bin/env python3
"""
Fix: Blog Post Inline CTA Button — Invisible Text (orange-on-orange)
Version: 5.0.1
Date: 2026-02-24

ROOT CAUSE:
  Post 879 (PB) / Post 1195 (JDS) - "Your Next Direct Report Won't Be Human":
    Has an inline mid-content CTA: <p><a href="...#awakening">Take the free assessment →</a></p>
    The post's own CSS block has: #pb-agent-manager-post a { color: #f1420b !important }
    This makes the link text orange. The hover state (from plugin j3 hook) adds an
    orange background — creating orange-on-orange invisible text on hover.
    BUT: even in default state, it's just an orange text link with no button styling.
    Jared sees "orange text on orange background" — the hover state captures this.

  Post 606 (PB) / Post 1092 (JDS) - "Why 95% of AI Pilots Fail":
    Has TWO bare awakening links inside <p> tags with no styling.
    Same root cause.

FIX STRATEGY:
  1. Upgrade bare <p><a href="#awakening"> links to styled button HTML
     (matching the .cta-btn style used in footer CTAs)
  2. Add universal plugin CSS (v5.0.1) as a safety net for any future posts

AFFECTED POSTS:
  purebrain.ai:     Post 879, Post 606
  jareddsanborn.com: Post 1195, Post 1092
"""

import subprocess
import json
import re
import time
import os
import sys

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

PB_USER  = "Aether"
PB_PASS  = "FlFr2VOtlHiHaJWjzW96OHUJ"
PB_BASE  = "https://purebrain.ai"

JDS_USER = "AetherPureBrain.ai"
JDS_PASS = "u3GO 3dvG rUqG 3QgM EYqd 8KfP"
JDS_BASE = "https://jareddsanborn.com"

# The styled button HTML that replaces bare <p><a href="...#awakening">TEXT</a></p>
# Using <div> wrapper (not <p>) to avoid wpautop issues
# The button text from the original link is preserved

BUTTON_TEMPLATE = """<div class="pb-inline-cta" style="margin: 2rem 0; text-align: center;">
<a href="{url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #f1420b 0%, #d13608 100%); color: #ffffff !important; font-weight: 700; font-size: 1.05rem; border-radius: 8px; text-decoration: none !important; letter-spacing: 0.5px; transition: background 0.3s ease;">{text}</a>
</div>"""

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def wp_api(method, url, user, password, data=None):
    """Execute a WordPress REST API call using curl."""
    cmd = [
        "curl", "-s",
        "-X", method,
        "-u", f"{user}:{password}",
        "-H", "Content-Type: application/json",
    ]
    if data:
        cmd += ["--data", json.dumps(data)]
    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  curl error: {result.stderr}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  JSON parse error. Response: {result.stdout[:200]}")
        return None


def get_post(base_url, user, password, post_id):
    """Fetch a post with context=edit."""
    url = f"{base_url}/wp-json/wp/v2/posts/{post_id}?context=edit"
    return wp_api("GET", url, user, password)


def update_post(base_url, user, password, post_id, raw_content):
    """Update post content.raw via REST API."""
    url = f"{base_url}/wp-json/wp/v2/posts/{post_id}"
    data = {"content": raw_content}
    return wp_api("POST", url, user, password, data)


def fix_bare_awakening_links(raw_content):
    """
    Find all bare <p><a href="...#awakening">TEXT</a></p> patterns
    and replace them with styled button HTML.
    Returns (new_content, count_fixed).
    """
    # Pattern: <p> tag containing ONLY an awakening link (no other content except whitespace)
    # The link has no class="cta-btn" and no inline style with display:inline-block
    pattern = re.compile(
        r'<p>\s*(<a\s+href="([^"]*#awakening)"[^>]*>([^<]+)</a>)\s*</p>',
        re.DOTALL | re.IGNORECASE
    )

    count = 0
    result = raw_content

    for match in reversed(list(pattern.finditer(raw_content))):
        a_tag   = match.group(1)
        url     = match.group(2)
        text    = match.group(3).strip()

        # Skip if already has inline-block style (already a button)
        if 'inline-block' in a_tag or 'cta-btn' in a_tag:
            continue

        button_html = BUTTON_TEMPLATE.format(url=url, text=text)
        result = result[:match.start()] + button_html + result[match.end():]
        count += 1
        print(f"  Replaced: '{text[:60]}' → styled button")

    return result, count


# ---------------------------------------------------------------------------
# MAIN SCRIPT
# ---------------------------------------------------------------------------

def process_post(site_name, base_url, user, password, post_id):
    print(f"\n{'='*60}")
    print(f"Processing {site_name} Post {post_id}")
    print(f"{'='*60}")

    # Fetch post
    post = get_post(base_url, user, password, post_id)
    if not post or 'content' not in post:
        print(f"  ERROR: Could not fetch post {post_id} from {site_name}")
        return False

    title = post.get('title', {}).get('raw', 'Unknown')
    raw   = post.get('content', {}).get('raw', '')
    print(f"  Title: {title}")
    print(f"  Content length: {len(raw)} chars")

    # Check for idempotency — skip if already fixed
    if 'pb-inline-cta' in raw:
        print(f"  SKIP: pb-inline-cta already present (already fixed)")
        return True

    # Apply fix
    new_raw, count = fix_bare_awakening_links(raw)

    if count == 0:
        print(f"  INFO: No bare awakening links found — post may already be correct")
        return True

    print(f"  Fixed {count} bare awakening link(s)")

    # Update post
    print(f"  Deploying update to {site_name} Post {post_id}...")
    result = update_post(base_url, user, password, post_id, new_raw)

    if not result or 'id' not in result:
        print(f"  ERROR: Update failed. Response: {str(result)[:200]}")
        return False

    print(f"  SUCCESS: Post {post_id} updated on {site_name}")
    return True


def verify_post(site_name, base_url, user, password, post_id):
    """Re-fetch post and confirm fix is applied."""
    print(f"\nVerifying {site_name} Post {post_id}...")
    post = get_post(base_url, user, password, post_id)
    if not post:
        print(f"  ERROR: Could not re-fetch post")
        return False

    raw = post.get('content', {}).get('raw', '')

    # Check no more bare awakening links
    bare_pattern = re.compile(
        r'<p>\s*<a\s+href="[^"]*#awakening"[^>]*>[^<]+</a>\s*</p>',
        re.DOTALL | re.IGNORECASE
    )
    bare_matches = bare_pattern.findall(raw)

    # Check pb-inline-cta present with white text
    has_inline_cta = 'pb-inline-cta' in raw
    has_white_text = 'color: #ffffff !important' in raw

    print(f"  Bare awakening links remaining: {len(bare_matches)}")
    print(f"  pb-inline-cta present: {has_inline_cta}")
    print(f"  White text style present: {has_white_text}")

    if len(bare_matches) == 0 and has_inline_cta and has_white_text:
        print(f"  PASS: Post {post_id} on {site_name} — button text is white ✓")
        return True
    else:
        print(f"  FAIL: Post {post_id} on {site_name} — verification failed")
        if bare_matches:
            for bm in bare_matches:
                print(f"    Still bare: {repr(bm[:200])}")
        return False


def main():
    print("=" * 60)
    print("INLINE CTA WHITE TEXT FIX — v5.0.1")
    print("Fixing orange-on-orange invisible button text")
    print("=" * 60)

    # Posts to fix
    tasks = [
        # (site_name, base_url, user, password, post_id)
        ("purebrain.ai",      PB_BASE,  PB_USER,  PB_PASS,  879),
        ("purebrain.ai",      PB_BASE,  PB_USER,  PB_PASS,  606),
        ("jareddsanborn.com", JDS_BASE, JDS_USER, JDS_PASS, 1195),
        ("jareddsanborn.com", JDS_BASE, JDS_USER, JDS_PASS, 1092),
    ]

    results = []
    for site_name, base_url, user, password, post_id in tasks:
        success = process_post(site_name, base_url, user, password, post_id)
        results.append((site_name, post_id, success))
        time.sleep(0.5)

    # Verification pass
    print(f"\n{'='*60}")
    print("VERIFICATION PASS")
    print(f"{'='*60}")

    verify_results = []
    for site_name, base_url, user, password, post_id in tasks:
        v = verify_post(site_name, base_url, user, password, post_id)
        verify_results.append((site_name, post_id, v))
        time.sleep(0.3)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    all_ok = True
    for site_name, post_id, ok in verify_results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {site_name} Post {post_id}")
        if not ok:
            all_ok = False

    if all_ok:
        print("\nAll posts fixed. Next: deploy plugin v5.0.1 with universal CSS rule.")
    else:
        print("\nSome posts failed — check errors above.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
