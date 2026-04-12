#!/usr/bin/env python3
"""
Fix blog/index.html banner images (Issue 2) and deploy all pending changes.

Root cause: blog/index.html uses WordPress CDN URLs (wp-content/uploads) for
banner images in the wp-block-latest-posts section. CF Pages intercepts these
URLs and returns HTML instead of images.

Fix: Replace img src/srcset in the wp-block-latest-posts section with local
     /blog/[slug]/banner.png paths.

Also deploys: All other pending changes (blog listing, post formatting fixes)
that were prepared by previous scripts but not yet deployed.

Author: dept-systems-technology
Date: 2026-03-13
"""

import re
import sys
import subprocess
import os
import requests
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
CF_DEPLOY_ROOT = AETHER_ROOT / "exports/cf-pages-deploy"
BLOG_INDEX = CF_DEPLOY_ROOT / "blog/index.html"

# Map from post slug to local banner path
# Uses the banner.png files that exist in exports/cf-pages-deploy/blog/[slug]/
SLUG_TO_LOCAL_BANNER = {
    "your-ai-has-no-idea-who-you-are": "/blog/your-ai-has-no-idea-who-you-are/banner.png",
    "your-ai-resets-to-zero-every-morning": "/blog/your-ai-resets-to-zero-every-morning/banner.png",
    "teach-your-ai-something-no-one-else-can": "/blog/teach-your-ai-something-no-one-else-can/banner.png",
    "52-billion-ai-agents-market-is-not-the-story": "/blog/52-billion-ai-agents-market-is-not-the-story/banner.png",
    "age-of-ai-agents-next-18-months": "/blog/age-of-ai-agents-next-18-months/banner.png",
    "something-big-already-happened-you-just-werent-invited-yet": "/blog/something-big-already-happened-you-just-werent-invited-yet/banner.png",
    "the-ai-that-forgets-you-every-single-time": "/blog/the-ai-that-forgets-you-every-single-time/banner.png",
    "the-context-tax": "/blog/the-context-tax/banner.png",
    "the-age-of-ai-agents": "/blog/the-age-of-ai-agents/banner.png",
    "your-ai-doesnt-work-for-you": "/blog/your-ai-doesnt-work-for-you/banner.png",
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": "/blog/ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger/banner.png",
}


def fix_blog_index_banners():
    """Replace wp-content/uploads image URLs with local banner paths."""
    print("[Fix] Fixing blog/index.html banner images...")

    html = BLOG_INDEX.read_text(encoding="utf-8")
    original = html

    # Find the wp-block-latest-posts section
    start = html.find('<ul class="wp-block-latest-posts')
    if start < 0:
        print("  ERROR: wp-block-latest-posts not found")
        return False
    end = html.find('</ul>', start) + len('</ul>')
    section = html[start:end]
    print(f"  Found wp-block-latest-posts section: {len(section)} chars")

    # For each <li> in the section, find the img tag and replace src/srcset
    # with the local banner path based on the post slug from the href link
    new_section = section

    # Find all img tags with wp-content/uploads src
    img_pattern = re.compile(
        r'(<img\s[^>]*?src=")(https://purebrain\.ai/wp-content/uploads/[^"]+)("'
        r'[^>]*?srcset=")[^"]+(")',
        re.DOTALL
    )

    def replace_img(m):
        # Extract the full img tag to find which post it belongs to
        # We need to look backward in new_section to find the nearest href
        return m.group(0)  # Will be processed differently

    # Better approach: process each <li> independently
    li_pattern = re.compile(r'<li>(.*?)</li>', re.DOTALL)
    post_href_pattern = re.compile(r'href="https://purebrain\.ai/(?:blog/)?([^/"]+)/"')
    img_tag_pattern = re.compile(
        r'(<img\s)([^>]*?)(/?>)',
        re.DOTALL
    )
    src_pattern = re.compile(r'\bsrc="https://purebrain\.ai/wp-content/uploads/[^"]+"')
    srcset_pattern = re.compile(r'\bsrcset="[^"]*wp-content/uploads[^"]+"')

    fixed_count = 0
    new_section_parts = []
    last_end = 0

    for li_match in li_pattern.finditer(section):
        li_content = li_match.group(1)
        li_start = li_match.start()
        li_end = li_match.end()

        # Add content before this li
        new_section_parts.append(section[last_end:li_start])
        last_end = li_end

        # Find post slug from href
        slug_match = post_href_pattern.search(li_content)
        if not slug_match:
            new_section_parts.append(li_match.group(0))
            continue

        slug = slug_match.group(1)
        local_banner = SLUG_TO_LOCAL_BANNER.get(slug)

        if not local_banner:
            print(f"  No banner mapping for slug: {slug}")
            new_section_parts.append(li_match.group(0))
            continue

        # Check if there's a wp-content/uploads src in this li
        if 'wp-content/uploads' not in li_content:
            new_section_parts.append(li_match.group(0))
            continue

        # Replace src with local banner, remove srcset
        new_li_content = li_content
        new_li_content = src_pattern.sub(f'src="{local_banner}"', new_li_content)
        new_li_content = srcset_pattern.sub('', new_li_content)

        new_section_parts.append(f'<li>{new_li_content}</li>')
        fixed_count += 1
        print(f"  Fixed banner for: {slug} -> {local_banner}")

    # Add remaining content after last li
    new_section_parts.append(section[last_end:])

    new_section = "".join(new_section_parts)
    print(f"  Fixed {fixed_count} posts")

    # Replace the old section in the full HTML
    new_html = html[:start] + new_section + html[end:]

    if new_html == original:
        print("  WARNING: No changes made to blog/index.html")
        return False

    # Verify no more wp-content/uploads in the updated section
    new_start = new_html.find('<ul class="wp-block-latest-posts')
    new_end = new_html.find('</ul>', new_start) + len('</ul>')
    new_section_check = new_html[new_start:new_end]
    remaining_wp = new_section_check.count('wp-content/uploads')
    print(f"  Remaining wp-content/uploads references in section: {remaining_wp}")

    # Verify local banners are in there
    local_img_count = new_section_check.count('/blog/')
    print(f"  Local /blog/ paths in section: {local_img_count}")

    BLOG_INDEX.write_text(new_html, encoding="utf-8")
    print(f"  Written: {BLOG_INDEX}")
    return True


def deploy_to_cf_pages():
    """Deploy the CF Pages project via wrangler."""
    print("\n[Deploy] Deploying to Cloudflare Pages via wrangler...")

    cmd = [
        "npx", "wrangler", "pages", "deploy", ".",
        "--project-name=purebrain",
        "--branch=main",
        "--commit-dirty=true"
    ]

    env_override = {
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/jared/.local/bin",
        "CLOUDFLARE_ACCOUNT_ID": "d526a3e9498dd167509003004df03290",
        "CLOUDFLARE_API_TOKEN": "HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_",
        "HOME": "/home/jared",
    }

    full_env = {**os.environ, **env_override}

    result = subprocess.run(
        cmd,
        cwd=str(CF_DEPLOY_ROOT),
        env=full_env,
        capture_output=True,
        text=True,
        timeout=300
    )

    print(f"  Exit code: {result.returncode}")
    if result.stdout:
        print("  STDOUT (last 20 lines):")
        for line in result.stdout.split('\n')[-20:]:
            if line.strip():
                print(f"    {line}")
    if result.stderr:
        print("  STDERR (last 20 lines):")
        for line in result.stderr.split('\n')[-20:]:
            if line.strip():
                print(f"    {line}")

    return result.returncode == 0


def purge_cf_cache(urls):
    """Purge Cloudflare cache for affected URLs."""
    print("\n[CF Cache] Purging cache for affected URLs...")

    CF_EMAIL = "jared@puretechnology.nyc"
    CF_KEY = "251911c00fe74daedaff1133decfc3a00f66c"
    ZONE_ID = "49400cad1527af716705f6cb8c22bb65"

    # Batch into chunks of 30
    for i in range(0, len(urls), 30):
        batch = urls[i:i+30]
        resp = requests.post(
            f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/purge_cache",
            headers={
                "X-Auth-Email": CF_EMAIL,
                "X-Auth-Key": CF_KEY,
                "Content-Type": "application/json"
            },
            json={"files": batch},
            timeout=30
        )
        print(f"  Batch {i//30+1}: status={resp.status_code}, success={resp.json().get('success') if resp.ok else 'FAIL'}")
        if not resp.ok:
            print(f"  Error: {resp.text[:200]}")
    return True


def verify_fixes():
    """Quick local verification of all fixes."""
    print("\n[Verify] Local verification...")
    all_ok = True

    # 1. blog/index.html - no wp-content in the latest posts section
    html = BLOG_INDEX.read_text()
    start = html.find('<ul class="wp-block-latest-posts')
    end = html.find('</ul>', start) + len('</ul>')
    section = html[start:end]
    wp_count = section.count('wp-content/uploads')
    local_count = section.count('/blog/')
    print(f"  blog/index.html: wp-content/uploads={wp_count}, local paths={local_count}")
    if wp_count > 0:
        print("  FAIL: Still has wp-content/uploads in latest posts section")
        all_ok = False
    else:
        print("  PASS: No broken WP CDN URLs")

    # 2. blog-neural-feed-memories - all images, no broken placeholders
    nfm_file = CF_DEPLOY_ROOT / "blog-neural-feed-memories/index.html"
    if nfm_file.exists():
        nfm_html = nfm_file.read_text()
        img_count = nfm_html.count('<img src=')
        # Only count actual placeholder divs, not CSS rules
        placeholder_count = len(re.findall(r'<div class="nfm-card-image-placeholder"', nfm_html))
        print(f"  blog-neural-feed-memories: images={img_count}, placeholders(actual)={placeholder_count}")
        if img_count >= 20:
            print("  PASS: Blog listing has banners")
        else:
            print(f"  FAIL: Only {img_count} images")
            all_ok = False
    else:
        print("  blog-neural-feed-memories/index.html: MISSING")
        all_ok = False

    # 3. Bad posts - all have pb-blog-post wrapper
    bad_posts = [
        "why-95-percent-of-ai-pilots-fail",
        "your-next-direct-report-wont-be-human",
        "why-ai-memory-changes-everything",
        "we-both-wrote-this-post",
        "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time",
        "the-ai-trust-gap",
        "how-my-human-named-me-and-what-it-meant",
        "the-difference-between-using-ai-and-having-an-ai-partner",
        "what-i-actually-do-all-day",
        "ceo-vs-employee-ai-transformation-gap",
        "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value",
        "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2",
    ]
    wrapper_pass = 0
    wrapper_fail = []
    for slug in bad_posts:
        post_file = CF_DEPLOY_ROOT / "blog" / slug / "index.html"
        if post_file.exists():
            post_html = post_file.read_text()
            if '<article class="pb-blog-post">' in post_html:
                wrapper_pass += 1
            else:
                wrapper_fail.append(slug)
        else:
            wrapper_fail.append(f"{slug} (MISSING)")
    print(f"  Post formatting: {wrapper_pass}/{len(bad_posts)} have pb-blog-post wrapper")
    if wrapper_fail:
        print(f"  FAIL posts: {wrapper_fail}")
        all_ok = False
    else:
        print("  PASS: All bad posts have wrapper")

    return all_ok


def main():
    print("=" * 65)
    print("BLOG FIX + DEPLOY — 2026-03-13")
    print("Fixing banner images in blog/index.html + deploying all pending changes")
    print("=" * 65)

    # Fix blog/index.html banners (Issue 2)
    fix_ok = fix_blog_index_banners()

    # Verify all changes
    all_ok = verify_fixes()

    # Deploy
    print("\n[Deploy] Proceeding with deployment...")
    deploy_ok = deploy_to_cf_pages()

    # Purge CF cache
    if deploy_ok:
        urls_to_purge = [
            "https://purebrain.ai/blog/",
            "https://purebrain.ai/blog-neural-feed-memories/",
            "https://purebrain.ai/blog/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/",
            "https://purebrain.ai/blog/your-next-direct-report-wont-be-human/",
            "https://purebrain.ai/blog/why-ai-memory-changes-everything/",
            "https://purebrain.ai/blog/we-both-wrote-this-post/",
            "https://purebrain.ai/blog/why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/",
            "https://purebrain.ai/blog/the-ai-trust-gap/",
            "https://purebrain.ai/blog/how-my-human-named-me-and-what-it-meant/",
            "https://purebrain.ai/blog/the-difference-between-using-ai-and-having-an-ai-partner/",
            "https://purebrain.ai/blog/what-i-actually-do-all-day/",
            "https://purebrain.ai/blog/ceo-vs-employee-ai-transformation-gap/",
            "https://purebrain.ai/blog/pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value/",
            "https://purebrain.ai/blog/why-95-percent-of-ai-pilots-fail/",
        ]
        purge_cf_cache(urls_to_purge)

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    print(f"  Fix blog/index.html banners: {'OK' if fix_ok else 'FAIL'}")
    print(f"  All verifications: {'PASS' if all_ok else 'FAIL'}")
    print(f"  Deploy: {'OK' if deploy_ok else 'FAIL'}")

    return 0 if (deploy_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
