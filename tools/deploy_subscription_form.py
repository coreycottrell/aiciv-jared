#!/usr/bin/env python3
"""
deploy_subscription_form.py
===========================
Deploys The Neural Feed subscription form to PureBrain.ai WordPress.

What it does:
  1. Reads tools/subscription_form.html
  2. Injects the form into the blog page (ID 319) content
  3. Optionally updates blog post subscribe links to point to the form anchor
  4. Optionally injects a PHP functions.php snippet to stdout for copy-paste

Usage:
  python3 tools/deploy_subscription_form.py
  python3 tools/deploy_subscription_form.py --update-posts
  python3 tools/deploy_subscription_form.py --dry-run
  python3 tools/deploy_subscription_form.py --show-php-snippet

Auth:
  Reads PUREBRAIN_WP_APP_PASSWORD from .env (user: Aether)
  Site: https://purebrain.ai

Requirements:
  pip install requests python-dotenv
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Config ─────────────────────────────────────────────────────────────────
DOTENV_PATH   = Path('/home/jared/projects/AI-CIV/aether/.env')
FORM_HTML_PATH = Path('/home/jared/projects/AI-CIV/aether/tools/subscription_form.html')

WP_BASE       = 'https://purebrain.ai/wp-json/wp/v2'
WP_USER       = 'Aether'
BLOG_PAGE_ID  = 319
BLOG_POST_IDS = [381, 316, 373, 172, 98]  # All published posts

# Anchor injected into form section (used by post CTA links)
FORM_ANCHOR   = 'neural-feed-subscribe'

# Marker we add so idempotency checks work
FORM_MARKER   = '<!-- NEURAL-FEED-FORM -->'

# The old subscribe link pattern in blog posts
# We'll update it to point to /blog/#neural-feed-subscribe
OLD_SUBSCRIBE_HREF_PREFIX = 'https://purebrain.ai/blog/?utm_source=blog&utm_medium=cta&utm_campaign=newsletter'
NEW_SUBSCRIBE_HREF_PREFIX = 'https://purebrain.ai/blog/#neural-feed-subscribe?utm_source=blog&utm_medium=cta&utm_campaign=newsletter'

# PHP snippet for wp-config / functions.php
PHP_SNIPPET = '''
<?php
// ============================================================
// THE NEURAL FEED - Brevo Newsletter Integration
// Add this to: wp-config.php (the two define lines)
// and functions.php (everything else).
// ============================================================

// --- wp-config.php additions ---
// Replace these placeholder values with your real Brevo credentials.
// Find your API key at: https://app.brevo.com/settings/keys/api
// Find your list ID at: https://app.brevo.com/contact/list
define('BREVO_API_KEY', 'xkeysib-YOUR_API_KEY_HERE');
define('BREVO_LIST_ID', 0); // <-- set your list ID integer here

// --- functions.php additions ---

/**
 * Inject nonce for the Neural Feed subscribe form.
 * Runs on blog page (319) and all singular posts.
 */
add_action('wp_footer', function() {
    if (is_page(319) || is_singular('post')) {
        $nonce = wp_create_nonce('nf_subscribe');
        echo "<script>var nfData = { nonce: '" . esc_js($nonce) . "' };</script>\\n";
    }
});

/**
 * Handle AJAX subscription (works for both logged-in and anonymous visitors).
 */
add_action('wp_ajax_nf_subscribe',        'nf_handle_subscribe');
add_action('wp_ajax_nopriv_nf_subscribe', 'nf_handle_subscribe');

function nf_handle_subscribe() {
    // Verify nonce
    check_ajax_referer('nf_subscribe', 'nf_nonce');

    // Validate email
    $email = isset($_POST['nf_email']) ? sanitize_email(wp_unslash($_POST['nf_email'])) : '';
    if (!is_email($email)) {
        wp_send_json_error(['message' => 'Please enter a valid email address.']);
    }

    // Load credentials
    $api_key = defined('BREVO_API_KEY') ? BREVO_API_KEY : '';
    $list_id = defined('BREVO_LIST_ID') ? (int) BREVO_LIST_ID : 0;

    if (empty($api_key) || strpos($api_key, 'YOUR_API_KEY') !== false || $list_id < 1) {
        // Credentials not yet configured - fail gracefully
        wp_send_json_error(['message' => 'Newsletter service is being set up. Please try again soon.']);
    }

    // Call Brevo API
    $payload = [
        'email'         => $email,
        'listIds'       => [$list_id],
        'updateEnabled' => true,
        'attributes'    => ['SOURCE' => 'purebrain-blog'],
    ];

    $response = wp_remote_post('https://api.brevo.com/v3/contacts', [
        'headers' => [
            'api-key'      => $api_key,
            'Content-Type' => 'application/json',
            'Accept'       => 'application/json',
        ],
        'body'    => json_encode($payload),
        'timeout' => 15,
    ]);

    if (is_wp_error($response)) {
        wp_send_json_error(['message' => 'Could not reach newsletter service. Please try again.']);
    }

    $code = (int) wp_remote_retrieve_response_code($response);

    // 201 = new contact created, 204 = existing contact updated
    if ($code === 201 || $code === 204) {
        wp_send_json_success(['message' => "You\\'re in. Look for your first issue this Friday."]);
    } elseif ($code === 400) {
        $body = json_decode(wp_remote_retrieve_body($response), true);
        $msg  = isset($body['message']) ? sanitize_text_field($body['message']) : 'Invalid request.';
        wp_send_json_error(['message' => $msg]);
    } else {
        wp_send_json_error(['message' => 'Unexpected error (' . $code . '). Please try again shortly.']);
    }
}
'''


# ── Utilities ───────────────────────────────────────────────────────────────

def load_credentials() -> tuple[str, requests.auth.HTTPBasicAuth]:
    """Load WordPress credentials from .env."""
    load_dotenv(DOTENV_PATH)
    password = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
    if not password:
        print('[ERROR] PUREBRAIN_WP_APP_PASSWORD not found in .env', file=sys.stderr)
        sys.exit(1)
    return password, requests.auth.HTTPBasicAuth(WP_USER, password)


def get_post(auth: requests.auth.HTTPBasicAuth, endpoint: str) -> dict:
    """Fetch a page or post via WP REST API with context=edit."""
    url = f'{WP_BASE}/{endpoint}?context=edit'
    resp = requests.get(url, auth=auth, timeout=30)
    resp.raise_for_status()
    return resp.json()


def update_content(auth: requests.auth.HTTPBasicAuth, endpoint: str, content: str, dry_run: bool) -> bool:
    """
    POST updated content to WordPress REST API.
    Returns True on success.
    """
    if dry_run:
        print(f'  [DRY RUN] Would POST to {WP_BASE}/{endpoint}')
        return True

    url = f'{WP_BASE}/{endpoint}'
    resp = requests.post(url, auth=auth, json={'content': content}, timeout=30)

    if resp.status_code in (200, 201):
        return True
    else:
        print(f'  [ERROR] HTTP {resp.status_code}: {resp.text[:300]}', file=sys.stderr)
        return False


def load_form_html() -> str:
    """Read the subscription form HTML snippet."""
    if not FORM_HTML_PATH.exists():
        print(f'[ERROR] Form file not found: {FORM_HTML_PATH}', file=sys.stderr)
        sys.exit(1)
    return FORM_HTML_PATH.read_text(encoding='utf-8')


# ── Blog Page Injection ──────────────────────────────────────────────────────

def inject_into_blog_page(auth: requests.auth.HTTPBasicAuth, dry_run: bool) -> bool:
    """
    Inject the subscription form into the blog page (ID 319).

    Strategy:
      - If FORM_MARKER already present: skip (idempotent).
      - Otherwise: append the form (wrapped in FORM_MARKER comment) after the
        last </article> or before the </div> that closes the .purebrain-blog wrapper.
        Fallback: append to end of content.
    """
    print(f'\n[Blog Page] Fetching page ID {BLOG_PAGE_ID}...')
    page    = get_post(auth, f'pages/{BLOG_PAGE_ID}')
    content = page['content']['raw']
    title   = page.get('title', {}).get('rendered', 'unknown')

    print(f'  Title: {title}')
    print(f'  Content length: {len(content)} chars')

    # Idempotency check
    if FORM_MARKER in content:
        print('  [SKIP] Form already injected (FORM_MARKER found). Nothing to do.')
        return True

    form_html = load_form_html()
    wrapped_form = f'\n\n{FORM_MARKER}\n{form_html}\n{FORM_MARKER}\n'

    # Try to inject after posts list / before social footer
    # Look for the social links section as the natural injection point
    insertion_targets = [
        # After the blog posts grid, before social footer
        '</div>\n\n<div class="social-links"',
        # Fallback: just before the color-fix style block at the end
        '\n<style>\n/* ========== BLOG PAGE COLOR FIXES',
        # Last resort: before final </div>
        '\n</div>\n</div>\n</div>',  # closing the main purebrain-blog wrapper
    ]

    updated = None
    for target in insertion_targets:
        if target in content:
            updated = content.replace(target, wrapped_form + target, 1)
            print(f'  Injecting before: {repr(target[:60])}...')
            break

    if updated is None:
        # Absolute fallback: append
        print('  No suitable insertion point found - appending to end.')
        updated = content.rstrip() + wrapped_form

    if dry_run:
        print('  [DRY RUN] Would write updated content.')
        print(f'  New content length: {len(updated)} chars')
        return True

    print(f'  Posting updated page...')
    ok = update_content(auth, f'pages/{BLOG_PAGE_ID}', updated, dry_run=False)
    if ok:
        print(f'  [OK] Blog page updated successfully.')
    return ok


# ── Blog Post CTA Link Update ────────────────────────────────────────────────

def update_post_subscribe_link(
    auth: requests.auth.HTTPBasicAuth,
    post_id: int,
    dry_run: bool
) -> bool:
    """
    In a blog post's CTA block, update the subscribe-to-newsletter link
    from /blog/?utm_... to /blog/#neural-feed-subscribe?utm_...
    """
    print(f'\n[Post {post_id}] Fetching...')
    post    = get_post(auth, f'posts/{post_id}')
    content = post['content']['raw']
    title   = post.get('title', {}).get('rendered', 'unknown')

    print(f'  Title: {title}')

    # Find existing subscribe links in this post
    if OLD_SUBSCRIBE_HREF_PREFIX not in content:
        print(f'  [SKIP] No matching subscribe link found in post {post_id}.')
        return True  # Not an error - link may already be updated or absent

    # Check if already updated
    if '#neural-feed-subscribe' in content:
        print(f'  [SKIP] Link already has anchor #{FORM_ANCHOR}.')
        return True

    # Replace the link href to include the anchor
    # Pattern: href="https://purebrain.ai/blog/?utm_source=blog&utm_medium=cta&utm_campaign=newsletter&utm_content=SLUG"
    # Replace:  https://purebrain.ai/blog/?   ->  https://purebrain.ai/blog/#neural-feed-subscribe?
    updated = content.replace(
        'https://purebrain.ai/blog/?utm_source=blog&utm_medium=cta&utm_campaign=newsletter',
        'https://purebrain.ai/blog/#neural-feed-subscribe?utm_source=blog&utm_medium=cta&utm_campaign=newsletter'
    )

    if updated == content:
        print(f'  [SKIP] Replacement produced no change.')
        return True

    count = content.count('https://purebrain.ai/blog/?utm_source=blog&utm_medium=cta&utm_campaign=newsletter')
    print(f'  Updating {count} subscribe link(s) to include #{FORM_ANCHOR} anchor.')

    ok = update_content(auth, f'posts/{post_id}', updated, dry_run)
    if ok and not dry_run:
        print(f'  [OK] Post {post_id} updated.')
    return ok


# ── PHP Snippet Printer ──────────────────────────────────────────────────────

def print_php_snippet():
    """Print the WordPress PHP integration snippet to stdout."""
    print('\n' + '='*68)
    print('  PHP SNIPPET FOR WORDPRESS (functions.php + wp-config.php)')
    print('='*68)
    print(PHP_SNIPPET)
    print('='*68)
    print('\nSteps:')
    print('  1. Add the two define() lines to wp-config.php')
    print('     (replace placeholder values with real Brevo credentials)')
    print('  2. Add the add_action() and function nf_handle_subscribe() code')
    print('     to your theme\'s functions.php (or a custom plugin).')
    print('  3. In wp-config.php, set BREVO_LIST_ID to your actual list integer ID.')
    print('  4. Test by submitting the form with a real email address.')
    print('\nBrevo credentials:')
    print('  API key: https://app.brevo.com/settings/keys/api')
    print('  List ID: https://app.brevo.com/contact/list')


# ── Verification ─────────────────────────────────────────────────────────────

def verify_blog_page(auth: requests.auth.HTTPBasicAuth):
    """Re-fetch the blog page and confirm the form marker is present."""
    print(f'\n[Verify] Fetching blog page {BLOG_PAGE_ID}...')
    page    = get_post(auth, f'pages/{BLOG_PAGE_ID}')
    content = page['content']['raw']

    if FORM_MARKER in content:
        anchor_present = f'id="{FORM_ANCHOR}"' in content
        form_present   = 'nf-subscribe-form' in content
        print(f'  [OK] FORM_MARKER found in blog page content.')
        print(f'  [{"OK" if anchor_present else "WARN"}] Form anchor id="{FORM_ANCHOR}": {"present" if anchor_present else "MISSING"}')
        print(f'  [{"OK" if form_present else "WARN"}] nf-subscribe-form element: {"present" if form_present else "MISSING"}')
    else:
        print('  [FAIL] FORM_MARKER not found in blog page. Injection may have failed.')
        return False
    return True


def verify_posts(auth: requests.auth.HTTPBasicAuth, post_ids: list[int]):
    """Verify subscribe links in posts contain the anchor."""
    print(f'\n[Verify Posts]')
    for pid in post_ids:
        post    = get_post(auth, f'posts/{pid}')
        content = post['content']['raw']
        has_anchor = f'#neural-feed-subscribe' in content
        has_old    = OLD_SUBSCRIBE_HREF_PREFIX in content and '#neural-feed-subscribe' not in content
        print(f'  Post {pid}: anchor={"YES" if has_anchor else "no"}, old_link={"YES (needs update)" if has_old else "no"}')
        time.sleep(1)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Deploy The Neural Feed subscription form to PureBrain.ai WordPress.'
    )
    parser.add_argument(
        '--update-posts',
        action='store_true',
        help='Also update blog post CTA links to point to the form anchor.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing to WordPress.'
    )
    parser.add_argument(
        '--show-php-snippet',
        action='store_true',
        help='Print the WordPress PHP snippet (for functions.php) and exit.'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only run verification checks, no modifications.'
    )
    parser.add_argument(
        '--post-ids',
        nargs='+',
        type=int,
        default=BLOG_POST_IDS,
        help=f'Post IDs to update when --update-posts is set. Default: {BLOG_POST_IDS}'
    )
    args = parser.parse_args()

    # Show PHP snippet and exit if requested
    if args.show_php_snippet:
        print_php_snippet()
        return

    # Load credentials
    _, auth = load_credentials()

    if args.dry_run:
        print('[DRY RUN MODE] No changes will be written to WordPress.\n')

    # ── Verify only ────────────────────────────────────────────────────────
    if args.verify_only:
        verify_blog_page(auth)
        if args.update_posts:
            verify_posts(auth, args.post_ids)
        return

    # ── Deploy form to blog page ───────────────────────────────────────────
    ok_page = inject_into_blog_page(auth, dry_run=args.dry_run)
    if not ok_page:
        print('[ERROR] Blog page injection failed. Aborting.', file=sys.stderr)
        sys.exit(1)

    if not args.dry_run:
        time.sleep(2)  # brief pause between API calls

    # ── Update post CTA links ──────────────────────────────────────────────
    if args.update_posts:
        print(f'\n[Posts] Updating subscribe links in {len(args.post_ids)} post(s)...')
        results = {}
        for pid in args.post_ids:
            results[pid] = update_post_subscribe_link(auth, pid, dry_run=args.dry_run)
            if not args.dry_run:
                time.sleep(2)

        failed = [pid for pid, ok in results.items() if not ok]
        if failed:
            print(f'\n[WARN] These posts had update errors: {failed}')
        else:
            print(f'\n[OK] All {len(args.post_ids)} post(s) processed.')

    # ── Verification ──────────────────────────────────────────────────────
    if not args.dry_run:
        print('\n' + '='*60)
        print('VERIFICATION')
        print('='*60)
        time.sleep(2)
        page_ok = verify_blog_page(auth)
        if args.update_posts:
            time.sleep(1)
            verify_posts(auth, args.post_ids)

    # ── Next steps ────────────────────────────────────────────────────────
    print('\n' + '='*60)
    print('NEXT STEPS')
    print('='*60)
    print("""
1. BREVO BACKEND (required for form to actually subscribe people):
   Run with --show-php-snippet to see the WordPress PHP code.
   Add it to functions.php after Jared sets up Brevo credentials.

2. BREVO CREDENTIALS (Jared needs to provide):
   - API key from: https://app.brevo.com/settings/keys/api
   - List ID from: https://app.brevo.com/contact/list
   Add to wp-config.php:
     define('BREVO_API_KEY', 'xkeysib-...');
     define('BREVO_LIST_ID', YOUR_LIST_ID);

3. TEST THE FORM:
   Visit https://purebrain.ai/blog/#neural-feed-subscribe
   Submit with a test email. Check Brevo contacts list.

4. VERIFY LIVE:
   python3 tools/deploy_subscription_form.py --verify-only
""")

    print('[DONE]')


if __name__ == '__main__':
    main()
