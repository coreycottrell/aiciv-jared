#!/usr/bin/env python3
"""
Fix: Inject blog post CSS into all CF Pages blog post HTML exports.

Root cause: Blog posts were exported from WordPress as bare HTML.
The pb-blog-post wrapper is present but there is no CSS. On WordPress,
styling was provided by the theme + pb-blog-styling plugin. On CF Pages
static hosting, we must embed the CSS in each file.

This script injects:
1. Font imports (Oswald + Plus Jakarta Sans)
2. Full .pb-blog-post scoped CSS
3. Body base styles (dark background, reset)
"""

import os
import re
from pathlib import Path

BLOG_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog")

# The CSS block to inject into every blog post <head>
BLOG_CSS_INJECTION = """
<!-- Blog Post Styling - injected 2026-03-12 -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&display=swap">
<style>
/* ============================================================
   PureBrain Blog Post Styles - CF Pages Static Version
   Scoped to .pb-blog-post (matches WordPress article wrapper)
   Colors: Blue #2a93c1 | Orange #f1420b | Dark #0a0a0f
   ============================================================ */

/* Body reset */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    background: #0a0a0f !important;
    color: #ffffff;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
}

/* Animated background layers */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: url('https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif') center center no-repeat;
    background-size: cover;
    opacity: 0.25;
    z-index: -2;
    pointer-events: none;
}

body::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(5, 8, 15, 0.60);
    z-index: -1;
    pointer-events: none;
}

/* ============================================================
   ARTICLE CONTAINER
   ============================================================ */
article.pb-blog-post {
    max-width: 760px;
    margin: 60px auto 80px;
    padding: 48px 40px;
    background: rgba(10, 15, 35, 0.55);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    border-radius: 16px;
    border: 1px solid rgba(42, 147, 193, 0.18);
    position: relative;
    z-index: 1;
}

@media (max-width: 800px) {
    article.pb-blog-post {
        margin: 20px 16px 60px;
        padding: 32px 24px;
    }
}

@media (max-width: 480px) {
    article.pb-blog-post {
        margin: 12px 10px 40px;
        padding: 24px 16px;
    }
}

/* ============================================================
   HEADINGS
   ============================================================ */
article.pb-blog-post h1 {
    font-family: 'Oswald', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.25;
    margin-bottom: 24px;
    letter-spacing: -0.02em;
}

article.pb-blog-post h2 {
    font-family: 'Oswald', sans-serif;
    font-size: 1.55rem;
    font-weight: 600;
    color: #ffffff;
    line-height: 1.3;
    margin-top: 48px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(42, 147, 193, 0.25);
    letter-spacing: -0.01em;
}

article.pb-blog-post h3 {
    font-family: 'Oswald', sans-serif;
    font-size: 1.2rem;
    font-weight: 600;
    color: #e8eaf0;
    margin-top: 32px;
    margin-bottom: 12px;
}

article.pb-blog-post h4,
article.pb-blog-post h5,
article.pb-blog-post h6 {
    font-family: 'Oswald', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #e8eaf0;
    margin-top: 24px;
    margin-bottom: 10px;
}

/* ============================================================
   BODY TEXT
   ============================================================ */
article.pb-blog-post p {
    font-size: 1.05rem;
    color: rgba(255, 255, 255, 0.88);
    line-height: 1.8;
    margin-bottom: 20px;
}

article.pb-blog-post strong {
    color: #ffffff;
    font-weight: 700;
}

article.pb-blog-post em {
    color: rgba(255, 255, 255, 0.75);
    font-style: italic;
}

/* ============================================================
   LINKS
   ============================================================ */
article.pb-blog-post a {
    color: #f1420b;
    text-decoration: none;
    border-bottom: 1px solid rgba(241, 66, 11, 0.4);
    transition: all 0.2s ease;
}

article.pb-blog-post a:hover {
    color: #ffffff;
    background: #f1420b;
    border-bottom-color: #f1420b;
    padding: 0 3px;
    border-radius: 3px;
}

/* ============================================================
   LISTS
   ============================================================ */
article.pb-blog-post ul,
article.pb-blog-post ol {
    padding-left: 28px;
    margin-bottom: 20px;
}

article.pb-blog-post ul {
    list-style: none;
    padding-left: 0;
}

article.pb-blog-post ul li {
    position: relative;
    padding-left: 24px;
    margin-bottom: 10px;
    color: rgba(255, 255, 255, 0.88);
    font-size: 1.05rem;
    line-height: 1.7;
}

article.pb-blog-post ul li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 10px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #f1420b;
}

article.pb-blog-post ol li {
    margin-bottom: 10px;
    color: rgba(255, 255, 255, 0.88);
    font-size: 1.05rem;
    line-height: 1.7;
    padding-left: 6px;
}

article.pb-blog-post ol li::marker {
    color: #2a93c1;
    font-weight: 700;
}

/* Nested lists */
article.pb-blog-post ul ul,
article.pb-blog-post ol ul {
    margin-top: 8px;
    margin-bottom: 4px;
}

article.pb-blog-post ul ul li::before {
    background: #2a93c1;
    width: 6px;
    height: 6px;
    top: 11px;
}

/* ============================================================
   HORIZONTAL RULES
   ============================================================ */
article.pb-blog-post hr {
    border: none;
    border-top: 1px solid rgba(42, 147, 193, 0.3);
    margin: 36px 0;
}

/* ============================================================
   BLOCKQUOTES
   ============================================================ */
article.pb-blog-post blockquote {
    border-left: 4px solid #f1420b;
    background: rgba(241, 66, 11, 0.06);
    padding: 16px 24px;
    margin: 28px 0;
    border-radius: 0 8px 8px 0;
}

article.pb-blog-post blockquote p {
    color: rgba(255, 255, 255, 0.9);
    font-style: italic;
    margin-bottom: 0;
}

/* ============================================================
   CODE
   ============================================================ */
article.pb-blog-post code {
    background: rgba(42, 147, 193, 0.12);
    color: #2a93c1;
    padding: 2px 7px;
    border-radius: 4px;
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 0.9em;
}

article.pb-blog-post pre {
    background: rgba(10, 15, 30, 0.8);
    border: 1px solid rgba(42, 147, 193, 0.2);
    border-radius: 8px;
    padding: 20px 24px;
    overflow-x: auto;
    margin: 24px 0;
}

article.pb-blog-post pre code {
    background: none;
    padding: 0;
    color: rgba(255, 255, 255, 0.85);
    font-size: 0.9rem;
}

/* ============================================================
   IMAGES
   ============================================================ */
article.pb-blog-post img {
    max-width: 100%;
    height: auto;
    border-radius: 10px;
    margin: 24px 0;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    display: block;
}

/* ============================================================
   TABLES
   ============================================================ */
article.pb-blog-post table {
    width: 100%;
    border-collapse: collapse;
    margin: 28px 0;
    font-size: 0.95rem;
}

article.pb-blog-post th {
    background: rgba(42, 147, 193, 0.15);
    color: #ffffff;
    font-family: 'Oswald', sans-serif;
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
    border-bottom: 2px solid rgba(42, 147, 193, 0.4);
}

article.pb-blog-post td {
    padding: 10px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.85);
    vertical-align: top;
}

article.pb-blog-post tr:hover td {
    background: rgba(42, 147, 193, 0.05);
}

/* ============================================================
   BYLINE / META (By Aether | PureBrain.ai | Date)
   ============================================================ */
article.pb-blog-post p:first-of-type strong {
    /* byline is usually the first <p><strong>By Aether...</strong></p> */
    color: rgba(255, 255, 255, 0.55);
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 0.03em;
}

/* ============================================================
   SOCIAL SHARE FOOTER (already in HTML - keep compatible)
   ============================================================ */
.pt-social-share {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px 0;
    margin: 28px 0 0;
    border-top: 2px solid rgba(42, 147, 193, 0.3);
    flex-wrap: wrap;
}

.pt-social-share span {
    font-weight: 600;
    color: #fff;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.pt-social-share a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: rgba(42, 147, 193, 0.15);
    color: #2a93c1;
    text-decoration: none;
    transition: all 0.3s;
    font-size: 18px;
    border: none !important;
    border-bottom: none !important;
    padding: 0 !important;
}

.pt-social-share a:hover {
    background: #2a93c1;
    color: #fff;
    transform: scale(1.1);
    border-bottom: none !important;
}

.pt-social-share a svg {
    width: 20px;
    height: 20px;
    fill: currentColor;
}

/* CTA block at bottom */
.blog-cta-block {
    margin-top: 40px;
}

.blog-cta-block p {
    margin-bottom: 12px;
}

/* ============================================================
   BACK TO BLOG NAV (nice to have)
   ============================================================ */
.pb-back-to-blog {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #2a93c1;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 32px;
    transition: color 0.2s;
    border-bottom: none !important;
}

.pb-back-to-blog:hover {
    color: #f1420b;
    background: transparent;
    padding: 0;
    border-bottom: none !important;
}

/* ============================================================
   SCROLLBAR
   ============================================================ */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: rgba(42, 147, 193, 0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a93c1; }
</style>
"""

# Back-to-blog nav to inject just after <body> + <article> opening
BACK_NAV = '<a href="/blog/" class="pb-back-to-blog" style="display:inline-flex;align-items:center;gap:6px;color:#2a93c1;font-size:0.9rem;font-weight:600;margin:20px 0 0 20px;text-decoration:none;position:relative;z-index:1;">&#8592; Back to The Neural Feed</a>\n'


def fix_blog_post(html_path: Path) -> bool:
    """
    Inject blog CSS into a blog post index.html.
    Returns True if modified, False if already had CSS injected.
    """
    content = html_path.read_text(encoding="utf-8")

    # Skip if already injected
    if "Blog Post Styling - injected 2026-03-12" in content:
        print(f"  SKIP (already fixed): {html_path.parent.name}")
        return False

    # Inject CSS before closing </head>
    if "</head>" not in content:
        print(f"  ERROR: no </head> found in {html_path}")
        return False

    content = content.replace("</head>", BLOG_CSS_INJECTION + "</head>", 1)

    # Add back-to-blog nav after <body> opening (before <article>)
    # Insert just before <article class="pb-blog-post">
    content = content.replace(
        '<article class="pb-blog-post">',
        BACK_NAV + '<article class="pb-blog-post">',
        1
    )

    html_path.write_text(content, encoding="utf-8")
    print(f"  FIXED: {html_path.parent.name}")
    return True


def main():
    print("=== Blog Post CSS Injection ===")
    print(f"Blog directory: {BLOG_DIR}")
    print()

    fixed = 0
    skipped = 0
    errors = 0

    # Process each blog post subdirectory
    for post_dir in sorted(BLOG_DIR.iterdir()):
        if not post_dir.is_dir():
            continue  # skip index.html at blog root

        html_file = post_dir / "index.html"
        if not html_file.exists():
            print(f"  ERROR: no index.html in {post_dir.name}")
            errors += 1
            continue

        try:
            result = fix_blog_post(html_file)
            if result:
                fixed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR processing {post_dir.name}: {e}")
            errors += 1

    print()
    print(f"=== Summary ===")
    print(f"Fixed:   {fixed}")
    print(f"Skipped: {skipped}")
    print(f"Errors:  {errors}")
    print(f"Total:   {fixed + skipped + errors}")

    return errors == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
