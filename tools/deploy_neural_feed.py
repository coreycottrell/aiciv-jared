#!/usr/bin/env python3
"""Deploy Neural Feed subscription form to purebrain.ai/blog (page 319).

Reads the form HTML from subscription_form.html and injects it into the
blog page content via WordPress REST API. Also updates blog post subscribe
links to point to the #neural-feed-subscribe anchor.

Usage:
    python3 tools/deploy_neural_feed.py              # Deploy form to blog page
    python3 tools/deploy_neural_feed.py --dry-run     # Preview without saving
    python3 tools/deploy_neural_feed.py --update-posts # Also update blog post links
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
BLOG_PAGE_ID = 319
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))
FORM_MARKER = '<!-- NEURAL-FEED-FORM -->'
FORM_FILE = Path(__file__).parent / 'subscription_form.html'


def get_page_content(page_id):
    """Fetch current page content."""
    r = requests.get(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        params={'context': 'edit'}
    )
    r.raise_for_status()
    data = r.json()
    return data['content']['raw']


def inject_form(content, form_html):
    """Inject the form HTML into the blog page content."""
    # If form already injected, replace it
    if FORM_MARKER in content:
        start = content.index(FORM_MARKER)
        end = content.index(FORM_MARKER, start + len(FORM_MARKER)) + len(FORM_MARKER)
        content = content[:start] + FORM_MARKER + '\n' + form_html + '\n' + FORM_MARKER + content[end:]
        print('[OK] Replaced existing Neural Feed form.')
        return content

    # Find a good injection point - before related posts or at end
    markers = [
        '<!-- FIX #3: RELATED POSTS',
        '<!-- /wp:latest-posts -->',
        '<!-- wp:separator',
    ]
    for marker in markers:
        if marker in content:
            idx = content.index(marker)
            content = (
                content[:idx]
                + FORM_MARKER + '\n'
                + form_html + '\n'
                + FORM_MARKER + '\n\n'
                + content[idx:]
            )
            print(f'[OK] Injected form before: {marker[:40]}...')
            return content

    # Fallback: append at end
    content = content + '\n\n' + FORM_MARKER + '\n' + form_html + '\n' + FORM_MARKER
    print('[OK] Appended form at end of content.')
    return content


def update_page(page_id, content, dry_run=False):
    """Update page content via REST API."""
    if dry_run:
        print(f'[DRY RUN] Would update page {page_id} ({len(content)} chars)')
        return True

    r = requests.post(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        json={'content': content}
    )
    if r.status_code in (200, 201):
        print(f'[OK] Updated page {page_id} ({len(content)} chars)')
        return True
    else:
        print(f'[ERROR] Failed to update page {page_id}: HTTP {r.status_code}')
        print(r.text[:500])
        return False


def clear_caches():
    """Clear WordPress and Elementor caches."""
    # Elementor cache (may not apply to blog page but doesn't hurt)
    r = requests.delete(f'{SITE}/wp-json/elementor/v1/cache', auth=AUTH)
    print(f'[CACHE] Elementor cache clear: HTTP {r.status_code}')

    # WP Super Cache or similar - try common endpoints
    for endpoint in ['/wp-json/wp-super-cache/v1/cache', '/wp-json/wp/v2/cache']:
        try:
            r = requests.delete(f'{SITE}{endpoint}', auth=AUTH, timeout=5)
            if r.status_code < 400:
                print(f'[CACHE] {endpoint}: HTTP {r.status_code}')
        except Exception:
            pass


def update_blog_posts(dry_run=False):
    """Update subscribe links on all blog posts to point to #neural-feed-subscribe."""
    print('\n--- Updating blog post subscribe links ---')
    page = 1
    updated = 0
    while True:
        r = requests.get(
            f'{SITE}/wp-json/wp/v2/posts',
            auth=AUTH,
            params={'per_page': 20, 'page': page, 'context': 'edit'}
        )
        if r.status_code != 200:
            break
        posts = r.json()
        if not posts:
            break

        for post in posts:
            content = post['content']['raw']
            old_links = [
                'href="https://purebrain.ai/blog/"',
                'href="/blog/"',
                'href="https://purebrain.ai/blog"',
                'href="/blog"',
            ]
            new_link = 'href="https://purebrain.ai/blog/#neural-feed-subscribe"'

            # Only update subscribe-related links (look for context clues)
            modified = False
            for old in old_links:
                # Only replace links that are near "subscribe" or "newsletter" text
                idx = 0
                while True:
                    idx = content.find(old, idx)
                    if idx == -1:
                        break
                    # Check surrounding 200 chars for subscribe/newsletter keywords
                    context_start = max(0, idx - 200)
                    context_end = min(len(content), idx + 200)
                    context = content[context_start:context_end].lower()
                    if any(kw in context for kw in ['subscribe', 'newsletter', 'neural feed', 'stay updated']):
                        content = content[:idx] + new_link + content[idx + len(old):]
                        modified = True
                    idx += len(new_link)

            if modified:
                if dry_run:
                    print(f'  [DRY RUN] Would update post {post["id"]}: {post["title"]["raw"][:50]}')
                else:
                    r2 = requests.post(
                        f'{SITE}/wp-json/wp/v2/posts/{post["id"]}',
                        auth=AUTH,
                        json={'content': content}
                    )
                    status = 'OK' if r2.status_code in (200, 201) else f'ERROR {r2.status_code}'
                    print(f'  [{status}] Post {post["id"]}: {post["title"]["raw"][:50]}')
                updated += 1

        page += 1

    print(f'[DONE] Updated {updated} posts')
    return updated


def verify_deployment():
    """Verify the form is visible on the live page."""
    r = requests.get(f'{SITE}/blog/', timeout=15)
    html = r.text
    checks = {
        'neural-feed-subscribe anchor': 'id="neural-feed-subscribe"' in html,
        'subscribe form present': 'nf-subscribe-form' in html,
        'Brevo API call': 'api.brevo.com' in html,
        'subscribe button': 'Subscribe Free' in html,
    }
    print('\n--- Verification ---')
    all_ok = True
    for check, result in checks.items():
        status = 'PASS' if result else 'FAIL'
        if not result:
            all_ok = False
        print(f'  [{status}] {check}')
    return all_ok


def main():
    parser = argparse.ArgumentParser(description='Deploy Neural Feed subscription form')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    parser.add_argument('--update-posts', action='store_true', help='Update blog post subscribe links')
    parser.add_argument('--verify-only', action='store_true', help='Only verify deployment')
    args = parser.parse_args()

    if args.verify_only:
        verify_deployment()
        return

    # Read form HTML
    if not FORM_FILE.exists():
        print(f'[ERROR] Form file not found: {FORM_FILE}')
        sys.exit(1)
    form_html = FORM_FILE.read_text()
    print(f'[OK] Read form HTML ({len(form_html)} chars)')

    # Get current blog page content
    print(f'[OK] Fetching blog page (ID {BLOG_PAGE_ID})...')
    content = get_page_content(BLOG_PAGE_ID)
    print(f'[OK] Current content: {len(content)} chars')

    # Inject form
    new_content = inject_form(content, form_html)

    # Update page
    success = update_page(BLOG_PAGE_ID, new_content, dry_run=args.dry_run)
    if not success:
        sys.exit(1)

    # Clear caches
    if not args.dry_run:
        clear_caches()

    # Update blog posts
    if args.update_posts:
        update_blog_posts(dry_run=args.dry_run)

    # Verify
    if not args.dry_run:
        import time
        print('\nWaiting 3 seconds for cache propagation...')
        time.sleep(3)
        verify_deployment()


if __name__ == '__main__':
    main()
