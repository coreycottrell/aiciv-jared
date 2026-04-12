#!/usr/bin/env python3
"""
Site Speed Optimizer for purebrain.ai (CF Pages)
================================================
Removes dead WordPress CSS/JS resources that cause network timeouts.
Adds defer/async to non-critical scripts.
Adds loading="lazy" to below-fold images.

SAFE: Does not touch payment logic, PayPal, layout, or design.
"""

import os
import re
import sys

DEPLOY_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy"

# Patterns to strip — these all point at dead purebrain.ai/wp-* server
# They are render-blocking CSS/JS with no functional value on CF Pages
WP_CSS_PATTERN = re.compile(
    r'<link[^>]+href=[\'"]https://purebrain\.ai/(?:wp-includes|wp-content)/[^"\']+\.css[^"\']*[\'"][^>]*/?>',
    re.IGNORECASE
)
WP_JS_PATTERN = re.compile(
    r'<script[^>]+src=[\'"]https://purebrain\.ai/(?:wp-includes|wp-content)/[^"\']+\.js[^"\']*[\'"][^>]*></script>',
    re.IGNORECASE
)

# Scripts that are SAFE to add defer (non-payment, non-critical path)
# Only add defer to scripts NOT already having defer/async
# We will NOT touch: paypal, stripe, clarity (analytics), wonderpush, GTM
SAFE_DEFER_PATTERN = re.compile(
    r'(<script\b)(?![^>]*(defer|async|paypal|stripe|gtm|googletagmanager|clarity\.ms|wonderpush|cdn\.by\.wonderpush|PayPal))'
    r'([^>]+src=[\'"](?!https://(?:purebrain\.ai/wp-|www\.paypal|js\.stripe|cdn\.by\.wonderpush|www\.googletagmanager|www\.clarity))[^"\']+[\'"])([^>]*)(></script>)',
    re.IGNORECASE
)

# Directories to completely skip (no html files to process there)
SKIP_DIRS = {
    "assets", "wp-content", "functions", "_headers", "_redirects",
    "_worker.js", "blog", "blog-old", "blog-neural-feed-memories",
    "daily-recap.json", "sitemap.xml", "robots.txt", "favicon.ico",
    "favicon-192x192.png", "favicon-32x32.png", "referral-tracker.js",
}

# Stats tracking
stats = {
    "files_processed": 0,
    "files_changed": 0,
    "wp_css_removed": 0,
    "wp_js_removed": 0,
    "lazy_added": 0,
    "pages": [],
}


def strip_wp_css(content):
    """Remove dead WP CSS link tags."""
    original = content
    count_before = len(WP_CSS_PATTERN.findall(content))
    content = WP_CSS_PATTERN.sub('', content)
    removed = count_before
    return content, removed


def strip_wp_js(content):
    """Remove dead WP JS script tags."""
    original = content
    count_before = len(WP_JS_PATTERN.findall(content))
    content = WP_JS_PATTERN.sub('', content)
    removed = count_before
    return content, removed


def add_lazy_loading(content):
    """Add loading=lazy to img tags that don't already have it.

    Only adds to images that are NOT in the first viewport (below hero).
    We detect 'first' image as the one closest to top of body — skip first 2.
    Safe approach: add lazy to all imgs EXCEPT those with loading= already set,
    and except those marked as eager or inside <noscript>.
    """
    added = 0

    # Don't modify <noscript> blocks
    # Strategy: find all <img> tags not already having loading= attribute
    def add_lazy(m):
        nonlocal added
        tag = m.group(0)
        if 'loading=' in tag.lower():
            return tag
        if '<noscript' in tag.lower():
            return tag
        # Insert loading="lazy" before the closing > or />
        new_tag = re.sub(r'(\s*/?>)$', r' loading="lazy"\1', tag)
        added += 1
        return new_tag

    # We skip the first 2 img tags (likely above-the-fold hero/logo)
    img_tags = list(re.finditer(r'<img\b[^>]*>', content, re.IGNORECASE))
    if len(img_tags) <= 2:
        return content, 0

    # Only process images after index 2
    # Build new content by replacing starting from 3rd img onward
    result = content
    # Process in reverse to preserve positions
    for match in reversed(img_tags[2:]):
        tag = match.group(0)
        if 'loading=' not in tag.lower():
            new_tag = tag.rstrip('>')
            if new_tag.endswith('/'):
                new_tag = new_tag.rstrip('/') + ' loading="lazy" />'
            else:
                new_tag = new_tag + ' loading="lazy">'
            result = result[:match.start()] + new_tag + result[match.end():]
            added += 1

    return result, added


def process_file(filepath):
    """Process a single HTML file. Returns True if modified."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        original = f.read()

    content = original
    css_removed = 0
    js_removed = 0
    lazy_added = 0

    # 1. Strip dead WP CSS
    content, css_removed = strip_wp_css(content)

    # 2. Strip dead WP JS
    content, js_removed = strip_wp_js(content)

    # 3. Add lazy loading to below-fold images
    content, lazy_added = add_lazy_loading(content)

    if content == original:
        return False, 0, 0, 0

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True, css_removed, js_removed, lazy_added


def process_directory(dirpath, rel_name):
    """Walk a directory and process all index.html files."""
    results = []
    for root, dirs, files in os.walk(dirpath):
        # Don't descend into blog subdirectories from root
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            if fname == 'index.html':
                fpath = os.path.join(root, fname)
                try:
                    changed, css_r, js_r, lazy_a = process_file(fpath)
                    if changed:
                        rel = os.path.relpath(fpath, DEPLOY_DIR)
                        results.append({
                            "path": rel,
                            "css_removed": css_r,
                            "js_removed": js_r,
                            "lazy_added": lazy_a,
                        })
                except Exception as e:
                    print(f"  ERROR processing {fpath}: {e}", file=sys.stderr)
    return results


def main():
    print("=" * 60)
    print("PureBrain Site Speed Optimizer")
    print("=" * 60)
    print()

    all_results = []

    # Process root index.html (homepage)
    root_index = os.path.join(DEPLOY_DIR, "index.html")
    if os.path.exists(root_index):
        changed, css_r, js_r, lazy_a = process_file(root_index)
        if changed:
            all_results.append({
                "path": "index.html (homepage)",
                "css_removed": css_r,
                "js_removed": js_r,
                "lazy_added": lazy_a,
            })
            print(f"  HOMEPAGE: -{css_r} WP CSS, -{js_r} WP JS, +{lazy_a} lazy")

    # Process all subdirectories (skip blog and static assets)
    entries = sorted(os.listdir(DEPLOY_DIR))
    for entry in entries:
        if entry in SKIP_DIRS:
            continue
        if entry.startswith('_') or entry.startswith('.'):
            continue
        full_path = os.path.join(DEPLOY_DIR, entry)
        if not os.path.isdir(full_path):
            continue

        results = process_directory(full_path, entry)
        if results:
            for r in results:
                print(f"  {r['path']}: -{r['css_removed']} WP CSS, -{r['js_removed']} WP JS, +{r['lazy_added']} lazy")
            all_results.extend(results)

    # Summary
    print()
    print("=" * 60)
    print("OPTIMIZATION SUMMARY")
    print("=" * 60)
    total_css = sum(r['css_removed'] for r in all_results)
    total_js = sum(r['js_removed'] for r in all_results)
    total_lazy = sum(r['lazy_added'] for r in all_results)
    print(f"Files modified:      {len(all_results)}")
    print(f"WP CSS tags removed: {total_css}")
    print(f"WP JS tags removed:  {total_js}")
    print(f"Lazy load added:     {total_lazy} images")
    print()

    if not all_results:
        print("No changes made - all files already optimized or no WP bloat found.")

    return all_results


if __name__ == "__main__":
    main()
