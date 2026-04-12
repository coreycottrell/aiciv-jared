#!/usr/bin/env python3
"""
Blog Distribution Pipeline
Detects newly published WordPress posts and distributes to all platforms.

Usage:
  python blog_distribution_pipeline.py check    # Check for new posts & distribute
  python blog_distribution_pipeline.py status   # Show pipeline status
  python blog_distribution_pipeline.py test     # Test with most recent post (dry-run)
"""

import os
import sys
import json
import httpx
import base64
import hashlib
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / '.env')

# State file to track distributed posts
STATE_FILE = PROJECT_ROOT / '.blog_distribution_state.json'

# WordPress config
WP_URL = 'https://jareddsanborn.com'
WP_USER = os.getenv('WORDPRESS_USER')
WP_PASS = os.getenv('WORDPRESS_APP_PASSWORD')

# Bluesky config
BSKY_HANDLE = os.getenv('BSKY_USERNAME', 'jaredsanborn.bsky.social')
BSKY_PASSWORD = os.getenv('BSKY_PASSWORD')

# Twitter config (optional)
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

# Telegram config
TG_CONFIG_PATH = PROJECT_ROOT / 'config/telegram_config.json'

# Newsletter config
NEWSLETTER_URL = 'https://www.linkedin.com/build-relation/newsletter-follow?entityUrn=7428125791609192449'
NEWSLETTER_CTA = '\n\n---\n\n📬 Get insights like this weekly in your inbox:\n{}'.format(NEWSLETTER_URL)


def load_state():
    """Load distribution state (which posts have been distributed)."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {'distributed_posts': [], 'last_check': None}


def save_state(state):
    """Save distribution state."""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_wp_auth():
    """Get WordPress Basic Auth header."""
    token = base64.b64encode(f'{WP_USER}:{WP_PASS}'.encode()).decode()
    return {'Authorization': f'Basic {token}'}


def get_recent_posts(hours=24):
    """Get posts published in the last N hours."""
    with httpx.Client(timeout=30) as client:
        # Get published posts, sorted by date descending
        response = client.get(
            f'{WP_URL}/wp-json/wp/v2/posts',
            params={
                'status': 'publish',
                'per_page': 10,
                'orderby': 'date',
                'order': 'desc'
            },
            headers=get_wp_auth()
        )

        if response.status_code != 200:
            print(f'Error fetching posts: {response.status_code}')
            return []

        posts = response.json()
        recent = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        for post in posts:
            # Parse WordPress date (ISO format with timezone)
            pub_date_str = post.get('date_gmt', '')
            if pub_date_str:
                pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                if pub_date > cutoff:
                    recent.append({
                        'id': post['id'],
                        'title': post['title']['rendered'],
                        'url': post['link'],
                        'excerpt': post['excerpt']['rendered'][:200] if post.get('excerpt') else '',
                        'date': pub_date_str
                    })

        return recent


def create_bluesky_thread(post):
    """Create a Bluesky thread for the blog post."""
    title = post['title']
    url = post['url']

    # Create engaging thread with newsletter CTA
    thread_posts = [
        f"🆕 New blog post: {title}\n\nA thread on why this matters for AI adoption in business 🧵",
        f"The key insight: When you give your AI a name, you're not just personalizing it—you're creating accountability.\n\nYou start treating it like a team member, not a tool.",
        f"This changes everything:\n\n• You invest in training it\n• You give it context about your business\n• You expect consistency\n• You build trust over time",
        f"Read the full post: {url}",
        f"📬 Get insights like this weekly in your inbox:\n\n{NEWSLETTER_URL}\n\n#AI #Business #PureBrain"
    ]

    return thread_posts


def post_to_bluesky(post, dry_run=False):
    """Post thread to Bluesky."""
    if not BSKY_PASSWORD:
        print('  ⚠️  Bluesky: No credentials configured')
        return False

    thread = create_bluesky_thread(post)

    if dry_run:
        print('  📘 Bluesky (DRY RUN):')
        for i, text in enumerate(thread, 1):
            print(f'     Post {i}: {text[:80]}...')
        return True

    try:
        with httpx.Client(timeout=30) as client:
            # Authenticate
            auth_resp = client.post(
                'https://bsky.social/xrpc/com.atproto.server.createSession',
                json={'identifier': BSKY_HANDLE, 'password': BSKY_PASSWORD}
            )

            if auth_resp.status_code != 200:
                print(f'  ❌ Bluesky auth failed: {auth_resp.status_code}')
                return False

            session = auth_resp.json()
            did = session['did']
            access_jwt = session['accessJwt']
            headers = {'Authorization': f'Bearer {access_jwt}'}

            # Post thread
            parent_uri = None
            parent_cid = None
            root_uri = None
            root_cid = None

            for i, text in enumerate(thread):
                record = {
                    '$type': 'app.bsky.feed.post',
                    'text': text,
                    'createdAt': datetime.now(timezone.utc).isoformat(),
                }

                # Add reply reference for thread continuation
                if parent_uri and parent_cid:
                    record['reply'] = {
                        'root': {'uri': root_uri, 'cid': root_cid},
                        'parent': {'uri': parent_uri, 'cid': parent_cid}
                    }

                resp = client.post(
                    'https://bsky.social/xrpc/com.atproto.repo.createRecord',
                    headers=headers,
                    json={
                        'repo': did,
                        'collection': 'app.bsky.feed.post',
                        'record': record
                    }
                )

                if resp.status_code == 200:
                    result = resp.json()
                    parent_uri = result['uri']
                    parent_cid = result['cid']
                    if i == 0:
                        root_uri = parent_uri
                        root_cid = parent_cid
                else:
                    print(f'  ❌ Bluesky post {i+1} failed: {resp.status_code}')
                    return False

            print(f'  ✅ Bluesky: Thread posted ({len(thread)} posts)')
            return True

    except Exception as e:
        print(f'  ❌ Bluesky error: {e}')
        return False


def post_to_twitter(post, dry_run=False):
    """Post to Twitter/X using OAuth1."""
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        print('  ⚠️  Twitter: No API keys configured')
        print('     → Get keys at: https://developer.twitter.com')
        return False

    title = post['title']
    url = post['url']
    tweet = f"🆕 {title}\n\n{url}\n\n#AI #Business #PureBrain"

    if dry_run:
        print(f'  🐦 Twitter (DRY RUN): {tweet[:80]}...')
        return True

    try:
        import hmac
        import time
        import urllib.parse
        import secrets

        # OAuth1 signature generation
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = secrets.token_hex(16)

        # OAuth parameters
        oauth_params = {
            'oauth_consumer_key': TWITTER_API_KEY,
            'oauth_token': TWITTER_ACCESS_TOKEN,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': oauth_timestamp,
            'oauth_nonce': oauth_nonce,
            'oauth_version': '1.0'
        }

        # API endpoint
        api_url = 'https://api.twitter.com/2/tweets'
        method = 'POST'

        # Create signature base string
        all_params = oauth_params.copy()
        param_string = '&'.join(f'{urllib.parse.quote(k, safe="")}={urllib.parse.quote(str(v), safe="")}'
                                for k, v in sorted(all_params.items()))
        base_string = f'{method}&{urllib.parse.quote(api_url, safe="")}&{urllib.parse.quote(param_string, safe="")}'

        # Create signing key
        signing_key = f'{urllib.parse.quote(TWITTER_API_SECRET, safe="")}&{urllib.parse.quote(TWITTER_ACCESS_SECRET, safe="")}'

        # Generate signature
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), 'sha1').digest()
        ).decode()

        oauth_params['oauth_signature'] = signature

        # Create Authorization header
        auth_header = 'OAuth ' + ', '.join(
            f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(str(v), safe="")}"'
            for k, v in sorted(oauth_params.items())
        )

        with httpx.Client(timeout=30) as client:
            response = client.post(
                api_url,
                headers={
                    'Authorization': auth_header,
                    'Content-Type': 'application/json'
                },
                json={'text': tweet}
            )

            if response.status_code in [200, 201]:
                result = response.json()
                tweet_id = result.get('data', {}).get('id', 'unknown')
                print(f'  ✅ Twitter: Posted! Tweet ID: {tweet_id}')
                return True
            else:
                print(f'  ❌ Twitter: {response.status_code}')
                print(f'     {response.text[:200]}')
                return False

    except Exception as e:
        print(f'  ❌ Twitter error: {e}')
        return False


def create_linkedin_text(post):
    """Create LinkedIn-ready text for manual posting."""
    title = post['title']
    url = post['url']

    linkedin_text = f"""🆕 New on the blog: {title}

When was the last time you gave your AI a name?

Not a joke. Naming your AI changes how you interact with it.

It becomes a team member, not just a tool.

You start:
→ Training it properly
→ Giving it business context
→ Expecting consistency
→ Building real trust

My AI is named Aether. And yes, Aether helped write this post.

Read more: {url}

📬 Get insights like this weekly: {NEWSLETTER_URL}

#AI #Leadership #Business #PureBrain"""

    return linkedin_text


def send_telegram_notification(post, linkedin_text, results):
    """Send Telegram notification with results and LinkedIn text."""
    if not TG_CONFIG_PATH.exists():
        print('  ⚠️  Telegram: Config not found')
        return False

    try:
        config = json.loads(TG_CONFIG_PATH.read_text())
        bot_token = config.get('bot_token')
        chat_id = config.get('default_chat_id')  # Correct field name

        if not bot_token or not chat_id:
            print('  ⚠️  Telegram: Missing bot_token or chat_id')
            return False

        # Build status message
        status_lines = ['📢 **BLOG DISTRIBUTED**', '', f'**{post["title"]}**', post['url'], '']

        for platform, success in results.items():
            emoji = '✅' if success else '⚠️'
            status_lines.append(f'{emoji} {platform}')

        status_lines.extend(['', '---', '📋 **LinkedIn (copy-paste):**', '', linkedin_text])

        message = '\n'.join(status_lines)

        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f'https://api.telegram.org/bot{bot_token}/sendMessage',
                json={
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'Markdown',
                    'disable_web_page_preview': True
                }
            )

            if resp.status_code == 200:
                print('  ✅ Telegram: Notification sent')
                return True
            else:
                print(f'  ❌ Telegram: {resp.status_code}')
                return False

    except Exception as e:
        print(f'  ❌ Telegram error: {e}')
        return False


def distribute_post(post, dry_run=False):
    """Distribute a single post to all platforms."""
    print(f'\n📤 Distributing: {post["title"]}')
    print(f'   URL: {post["url"]}')
    print()

    results = {}

    # Bluesky
    results['Bluesky'] = post_to_bluesky(post, dry_run)

    # Twitter
    results['Twitter'] = post_to_twitter(post, dry_run)

    # LinkedIn (always create text, even in dry run)
    linkedin_text = create_linkedin_text(post)
    results['LinkedIn'] = True  # Text created successfully

    if dry_run:
        print(f'\n  📋 LinkedIn (copy-paste ready):')
        print('  ' + '-' * 40)
        for line in linkedin_text.split('\n'):
            print(f'  {line}')
        print('  ' + '-' * 40)

    # Telegram notification (skip in dry run)
    if not dry_run:
        send_telegram_notification(post, linkedin_text, results)

    return results


def cmd_check():
    """Check for new posts and distribute them."""
    print('🔍 Checking for newly published posts...')

    state = load_state()
    distributed_ids = set(state.get('distributed_posts', []))

    recent_posts = get_recent_posts(hours=24)

    if not recent_posts:
        print('   No posts published in the last 24 hours.')
        state['last_check'] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        return

    new_posts = [p for p in recent_posts if p['id'] not in distributed_ids]

    if not new_posts:
        print(f'   Found {len(recent_posts)} recent posts, all already distributed.')
        state['last_check'] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        return

    print(f'   Found {len(new_posts)} new posts to distribute!')

    for post in new_posts:
        results = distribute_post(post)

        # Mark as distributed
        state['distributed_posts'].append(post['id'])

        # Keep only last 100 post IDs
        if len(state['distributed_posts']) > 100:
            state['distributed_posts'] = state['distributed_posts'][-100:]

    state['last_check'] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    print('\n✅ Distribution complete!')


def cmd_status():
    """Show pipeline status."""
    print('📊 Blog Distribution Pipeline Status')
    print('=' * 50)

    state = load_state()

    print(f'\nLast check: {state.get("last_check", "Never")}')
    print(f'Posts distributed: {len(state.get("distributed_posts", []))}')

    print('\n📡 Platform Status:')
    print(f'  WordPress: {"✅ Configured" if WP_USER and WP_PASS else "❌ Missing credentials"}')
    print(f'  Bluesky:   {"✅ Configured" if BSKY_PASSWORD else "❌ Missing BSKY_PASSWORD"}')
    print(f'  Twitter:   {"✅ Configured" if TWITTER_API_KEY else "❌ Missing API keys"}')
    print(f'  Telegram:  {"✅ Configured" if TG_CONFIG_PATH.exists() else "❌ Missing config"}')
    print(f'  LinkedIn:  ✅ Manual (copy-paste text generated)')

    print('\n📝 Recent Posts:')
    recent = get_recent_posts(hours=168)  # Last week
    distributed_ids = set(state.get('distributed_posts', []))

    for post in recent[:5]:
        status = '✅' if post['id'] in distributed_ids else '⏳'
        print(f'  {status} [{post["id"]}] {post["title"][:50]}')


def cmd_test():
    """Test distribution with most recent post (dry run)."""
    print('🧪 Testing distribution pipeline (DRY RUN)')
    print('=' * 50)

    recent = get_recent_posts(hours=168)

    if not recent:
        print('No recent posts found.')
        return

    post = recent[0]
    distribute_post(post, dry_run=True)

    print('\n✅ Dry run complete - no actual posts made')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == 'check':
        cmd_check()
    elif cmd == 'status':
        cmd_status()
    elif cmd == 'test':
        cmd_test()
    else:
        print(f'Unknown command: {cmd}')
        print(__doc__)


if __name__ == '__main__':
    main()
