#!/usr/bin/env python3
"""
Blog Article Wrap Fix
Fixes broken blog posts that are missing <article class="pb-blog-post"> wrapper.

Posts with proper HTML content that just need the article wrap:
- Adds back-to-blog link after banner
- Wraps content in <article class="pb-blog-post">
- Removes old blog-nav-inject script blocks
- Closes article before FAQ section
"""

import os
import re
import sys

BLOG_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog"

# Posts confirmed to need fixing (article=0 in audit)
BROKEN_POSTS = [
    "ceo-vs-employee-ai-transformation-gap",
    "how-my-human-named-me-and-what-it-meant",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2",
    "the-ai-trust-gap",
    "the-difference-between-using-ai-and-having-an-ai-partner",
    "we-both-wrote-this-post",
    "what-i-actually-do-all-day",
    "why-95-percent-of-ai-pilots-fail",
    "why-ai-memory-changes-everything",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time",
    "your-next-direct-report-wont-be-human",
    # pilot-purgatory has raw markdown content - skip, needs separate handling
]

BACK_TO_BLOG_LINK = '\n<a href="/blog/" class="pb-back-to-blog" style="display:inline-flex;align-items:center;gap:6px;color:#2a93c1;font-size:0.9rem;font-weight:600;margin:20px 0 0 20px;text-decoration:none;position:relative;z-index:1;">&#8592; Back to The Neural Feed</a>\n'

ARTICLE_OPEN = '\n<article class="pb-blog-post">\n'
ARTICLE_CLOSE = '\n</article>\n'


def fix_post(slug):
    path = os.path.join(BLOG_DIR, slug, "index.html")
    if not os.path.exists(path):
        print(f"  SKIP: {path} not found")
        return False

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. Check if already fixed
    if '<article class="pb-blog-post">' in content:
        print(f"  ALREADY FIXED: {slug}")
        return False

    # 2. Find the banner image tag (last match in body area - not CSS)
    # Pattern: <img class="pb-post-banner" src="./banner...
    banner_pattern = r'(<img class="pb-post-banner"[^>]+/>)'
    banner_matches = list(re.finditer(banner_pattern, content))
    if not banner_matches:
        print(f"  ERROR: No banner found in {slug}")
        return False

    # Use the last match (the actual img tag, not a CSS reference)
    banner_match = banner_matches[-1]
    banner_end = banner_match.end()

    # 3. Find FAQ section start
    faq_pattern = r'<div class="pb-faq-section"'
    faq_match = re.search(faq_pattern, content)
    if not faq_match:
        print(f"  ERROR: No FAQ section found in {slug}")
        return False

    faq_start = faq_match.start()

    # 4. Extract the region between banner and FAQ
    between = content[banner_end:faq_start]

    # 5. Remove old blog-nav-inject script block
    # Pattern: <p><script>\n/* blog-nav-inject: ... </script></p>
    inject_pattern = r'<p><script>\s*/\* blog-nav-inject.*?</script></p>'
    between_cleaned = re.sub(inject_pattern, '', between, flags=re.DOTALL)

    # Also clean up: <p><script id="pb-social-share-inline"> ... </script></p>
    # (This inline social share script inside <p> tags - it's already handled by the template)
    social_share_p_pattern = r'<p><script id="pb-social-share-inline">.*?</script></p>'
    between_cleaned = re.sub(social_share_p_pattern, '', between_cleaned, flags=re.DOTALL)

    # 6. Rebuild: banner + back-to-blog + article open + cleaned content + article close + FAQ
    new_content = (
        content[:banner_end]
        + BACK_TO_BLOG_LINK
        + ARTICLE_OPEN
        + between_cleaned
        + ARTICLE_CLOSE
        + content[faq_start:]
    )

    if new_content == original:
        print(f"  NO CHANGE: {slug}")
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  FIXED: {slug}")
    return True


def verify_post(slug):
    path = os.path.join(BLOG_DIR, slug, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    has_article = '<article class="pb-blog-post">' in content
    has_back = 'pb-back-to-blog' in content
    has_close = '</article>' in content
    old_inject_removed = '/* blog-nav-inject' not in content

    ok = has_article and has_back and has_close and old_inject_removed
    status = "PASS" if ok else "FAIL"
    print(f"  {status}: {slug} | article={has_article} back={has_back} close={has_close} inject_gone={old_inject_removed}")
    return ok


if __name__ == "__main__":
    print("=== FIXING BROKEN BLOG POSTS ===\n")

    fixed = 0
    for slug in BROKEN_POSTS:
        if fix_post(slug):
            fixed += 1

    print(f"\n=== FIXED {fixed}/{len(BROKEN_POSTS)} posts ===\n")

    print("=== VERIFICATION ===\n")
    all_pass = True
    for slug in BROKEN_POSTS:
        if not verify_post(slug):
            all_pass = False

    if all_pass:
        print("\nALL POSTS PASS VERIFICATION")
    else:
        print("\nSOME POSTS FAILED - check output above")
        sys.exit(1)
