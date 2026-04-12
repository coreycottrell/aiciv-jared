#!/usr/bin/env python3
"""
RSS-to-Email Daemon for PureBrain Neural Feed
Polls purebrain.ai/feed/ and sends Brevo campaign emails when new posts detected.
Run as part of purebrain_log_server.py daemon thread.

Author: full-stack-developer
Date: 2026-02-23
"""

import json
import logging
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

logger = logging.getLogger('rss_to_email')

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
RSS_URL = 'https://purebrain.ai/feed/'
STATE_FILE = '/home/jared/projects/AI-CIV/aether/config/rss_email_state.json'
POLL_INTERVAL_SECONDS = 3600  # Check every hour
LIST_3_ID = 3
# CRITICAL: support@puremarketing.ai is NOT verified in Brevo. Use purebrain@ instead.
SENDER_EMAIL = 'purebrain@puremarketing.ai'
SENDER_NAME = 'Jared Sanborn / PureBrain'

BREVO_HEADERS = {
    'api-key': BREVO_API_KEY,
    'Content-Type': 'application/json',
}


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------

def load_state() -> dict:
    """Load seen post GUIDs and sent campaign history from disk."""
    if Path(STATE_FILE).exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f'[RSS] Failed to load state file: {e}')
    return {'seen_guids': [], 'sent_campaigns': []}


def save_state(state: dict) -> None:
    """Persist state to disk atomically."""
    try:
        tmp_path = STATE_FILE + '.tmp'
        with open(tmp_path, 'w') as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, STATE_FILE)
    except IOError as e:
        logger.error(f'[RSS] Failed to save state file: {e}')


# ---------------------------------------------------------------------------
# RSS feed fetching
# ---------------------------------------------------------------------------

def _strip_html(text: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r'<[^<]+?>', '', text)


def fetch_rss() -> list:
    """
    Fetch and parse the RSS feed.
    Returns a list of dicts: {guid, title, link, excerpt}.
    Returns empty list on any error (daemon must not crash on feed failures).
    """
    try:
        response = requests.get(RSS_URL, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        channel = root.find('channel')
        if channel is None:
            logger.error('[RSS] Feed parsed but <channel> element not found')
            return []
        items = []
        for item in channel.findall('item'):
            guid_el = item.find('guid')
            title_el = item.find('title')
            link_el = item.find('link')
            desc_el = item.find('description')

            guid = guid_el.text.strip() if guid_el is not None and guid_el.text else ''
            title = title_el.text.strip() if title_el is not None and title_el.text else ''
            link = link_el.text.strip() if link_el is not None and link_el.text else ''
            description = desc_el.text if desc_el is not None and desc_el.text else ''

            # Strip HTML tags and trim excerpt to 300 chars
            excerpt = _strip_html(description)[:300].strip()

            if guid and title and link:
                items.append({
                    'guid': guid,
                    'title': title,
                    'link': link,
                    'excerpt': excerpt,
                })

        logger.info(f'[RSS] Feed fetched: {len(items)} items')
        return items

    except requests.exceptions.RequestException as e:
        logger.error(f'[RSS] Network error fetching feed: {e}')
        return []
    except ET.ParseError as e:
        logger.error(f'[RSS] XML parse error: {e}')
        return []
    except Exception as e:
        logger.error(f'[RSS] Unexpected error fetching feed: {e}')
        return []


# ---------------------------------------------------------------------------
# Brevo helpers
# ---------------------------------------------------------------------------

def get_list_3_subscriber_count() -> int:
    """Get count of List 3 subscribers for Telegram notification."""
    try:
        r = requests.get(
            'https://api.brevo.com/v3/contacts/lists/3',
            headers=BREVO_HEADERS,
            timeout=10,
        )
        if r.status_code == 200:
            return r.json().get('totalSubscribers', 0)
    except Exception as e:
        logger.warning(f'[RSS] Could not fetch subscriber count: {e}')
    return 0


def _build_email_html(post: dict) -> str:
    """
    Build the full HTML for the campaign email.

    CRITICAL f-string note:
    - CSS braces must be doubled: {{ and }} to produce literal { and }
    - Brevo unsubscribe tag {{ unsubscribe }} needs quadruple braces in f-string:
      {{{{ unsubscribe }}}} → rendered as {{ unsubscribe }} in the HTML sent to Brevo
    """
    utm_link = (
        f"{post['link']}?utm_source=newsletter&utm_medium=email"
        f"&utm_campaign=neural-feed-rss&utm_content=read-post"
    )
    excerpt = post['excerpt']
    title = post['title']

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>New from The Neural Feed</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background-color: #080a12; font-family: 'Helvetica Neue', Arial, sans-serif; }}
  .wrapper {{ background-color: #080a12; padding: 20px 0; }}
  .container {{ max-width: 600px; margin: 0 auto; background-color: #0d1117; border-radius: 8px; overflow: hidden; }}
  .header {{ background-color: #0d1117; padding: 28px 40px 24px; border-bottom: 1px solid #1a2235; text-align: center; }}
  .logo-main {{ color: #2a93c1; font-size: 22px; font-weight: 700; letter-spacing: 2px; display: inline; }}
  .logo-ai {{ color: #f1420b; font-size: 22px; font-weight: 700; display: inline; }}
  .sub-header {{ color: #5a6a7a; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; margin-top: 6px; }}
  .content {{ padding: 36px 40px 32px; }}
  .new-post-label {{ display: inline-block; background-color: #f1420b; color: #ffffff; font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 10px; border-radius: 3px; margin-bottom: 18px; }}
  .post-title {{ font-size: 24px; font-weight: 700; color: #e8f4fd; line-height: 1.3; margin-bottom: 16px; }}
  .post-excerpt {{ font-size: 15px; color: #b8c5d6; line-height: 1.7; margin-bottom: 28px; }}
  .cta-button {{ display: inline-block; background-color: #2a93c1; color: #ffffff !important; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-size: 15px; font-weight: 600; letter-spacing: 0.5px; }}
  .footer {{ background-color: #060810; padding: 24px 40px; text-align: center; border-top: 1px solid #1a2235; }}
  .footer p {{ font-size: 12px; color: #4a5568; line-height: 1.6; }}
  .footer a {{ color: #2a93c1; text-decoration: none; }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="container">

    <!-- Header: PUREBR(blue) + AI(orange) + N(blue) brand rule -->
    <div class="header">
      <span class="logo-main">PUREBR</span><span class="logo-ai">AI</span><span class="logo-main">N</span>
      <div class="sub-header">The Neural Feed</div>
    </div>

    <!-- Content -->
    <div class="content">
      <div class="new-post-label">New Post</div>
      <h1 class="post-title">{title}</h1>
      <p class="post-excerpt">{excerpt}...</p>
      <hr style="border: none; border-top: 1px solid #1a2235; margin: 24px 0;">
      <div style="text-align: center; margin: 28px 0;">
        <a href="{utm_link}" class="cta-button">Read the Full Post</a>
        <p style="font-size: 13px; color: #5a6a7a; margin-top: 12px;">
          Or visit <a href="https://purebrain.ai/blog?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-rss&utm_content=blog-footer" style="color: #2a93c1;">purebrain.ai/blog</a> for all posts
        </p>
      </div>
      <hr style="border: none; border-top: 1px solid #1a2235; margin: 24px 0;">
      <p style="font-size: 14px; color: #8899a6; line-height: 1.7; text-align: center;">
        PureBrain is the AI partner for businesses ready to go beyond chatbots.<br>
        <a href="https://purebrain.ai/#awakening?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-rss&utm_content=footer-cta" style="color: #f1420b; text-decoration: none; font-weight: 600;">See how it works &#8594;</a>
      </p>
      <div style="margin-top: 32px; padding-top: 20px; border-top: 1px solid #1a2235;">
        <p style="font-size: 14px; color: #8899a6;">Jared Sanborn</p>
        <p style="font-size: 12px; color: #5a6a7a; margin-top: 4px;">Founder, PureBrain &amp; Pure Technology</p>
      </div>
    </div>

    <!-- Footer: Brevo unsubscribe tag uses quadruple braces in f-string -->
    <div class="footer">
      <p>
        You're receiving this because you subscribed to The Neural Feed.<br>
        <a href="{{{{ unsubscribe }}}}">Unsubscribe</a> &nbsp;|&nbsp;
        <a href="https://purebrain.ai/blog">View all posts</a>
      </p>
    </div>

  </div>
</div>
</body>
</html>"""


def send_rss_campaign(post: dict) -> int | bool:
    """
    Create and immediately send a Brevo campaign for a new blog post.

    Steps:
    1. POST /v3/emailCampaigns to create draft
    2. POST /v3/emailCampaigns/{id}/sendNow to send immediately

    Returns campaign_id (int) on success, False on failure.
    """
    if not BREVO_API_KEY:
        logger.error('[RSS] BREVO_API_KEY not configured — cannot send campaign')
        return False

    # Truncate campaign name to 50 chars to stay clean in Brevo UI
    short_title = post['title'][:50]
    utm_link = (
        f"{post['link']}?utm_source=newsletter&utm_medium=email"
        f"&utm_campaign=neural-feed-rss&utm_content=read-post"
    )

    html_content = _build_email_html(post)

    # Step 1: Create campaign draft
    campaign_payload = {
        'name': f'[Auto] Neural Feed — {short_title}',
        'subject': f'New from The Neural Feed: {post["title"]}',
        'sender': {'name': SENDER_NAME, 'email': SENDER_EMAIL},
        'type': 'classic',
        'htmlContent': html_content,
        'recipients': {'listIds': [LIST_3_ID]},
        'header': 'The Neural Feed',
        'replyTo': 'jared@puretechnology.nyc',
    }

    try:
        r = requests.post(
            'https://api.brevo.com/v3/emailCampaigns',
            headers=BREVO_HEADERS,
            json=campaign_payload,
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        logger.error(f'[RSS] Campaign creation request failed: {e}')
        return False

    if r.status_code not in (200, 201):
        logger.error(
            f'[RSS] Campaign creation failed: status={r.status_code} body={r.text[:300]}'
        )
        return False

    campaign_id = r.json().get('id')
    if not campaign_id:
        logger.error(f'[RSS] Campaign created but no ID in response: {r.text[:200]}')
        return False

    logger.info(f'[RSS] Campaign created: ID={campaign_id} title="{post["title"]}"')

    # Step 2: Send campaign immediately
    try:
        r2 = requests.post(
            f'https://api.brevo.com/v3/emailCampaigns/{campaign_id}/sendNow',
            headers=BREVO_HEADERS,
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        logger.error(f'[RSS] Campaign sendNow request failed: {e}')
        return False

    if r2.status_code == 204:
        logger.info(f'[RSS] Campaign sent successfully: ID={campaign_id} title="{post["title"]}"')
        return campaign_id
    else:
        logger.error(
            f'[RSS] Campaign sendNow failed: ID={campaign_id} '
            f'status={r2.status_code} body={r2.text[:300]}'
        )
        return False


# ---------------------------------------------------------------------------
# Telegram notification
# ---------------------------------------------------------------------------

def _notify_telegram(message: str) -> None:
    """Send a Telegram notification to Jared (best-effort, non-fatal)."""
    try:
        subprocess.run(
            ['/home/jared/projects/AI-CIV/aether/tools/tg_send.sh', message],
            timeout=10,
            capture_output=True,
        )
    except Exception as e:
        logger.warning(f'[RSS] Telegram notification failed: {e}')


# ---------------------------------------------------------------------------
# Main daemon loop
# ---------------------------------------------------------------------------

def rss_daemon_loop() -> None:
    """
    Main polling loop. Designed to run as a daemon thread.
    Polls the PureBrain RSS feed every hour, sends a Brevo campaign
    for any post whose GUID is not in the state file.
    Never raises — all errors are logged and the loop continues.
    """
    logger.info('[RSS] RSS-to-Email daemon starting (poll interval: 1 hour)')

    while True:
        try:
            state = load_state()
            posts = fetch_rss()

            for post in posts:
                guid = post['guid']
                if guid not in state['seen_guids']:
                    logger.info(f'[RSS] New post detected: "{post["title"]}" ({guid})')
                    campaign_id = send_rss_campaign(post)

                    if campaign_id:
                        # Mark as seen and record the sent campaign
                        state['seen_guids'].append(guid)
                        state['sent_campaigns'].append({
                            'guid': guid,
                            'title': post['title'],
                            'link': post['link'],
                            'campaign_id': campaign_id,
                            'sent_at': datetime.utcnow().isoformat() + 'Z',
                        })
                        save_state(state)

                        # Notify Jared
                        subscriber_count = get_list_3_subscriber_count()
                        _notify_telegram(
                            f'Neural Feed auto-distributed to {subscriber_count} subscribers: '
                            f'"{post["title"]}" — {post["link"]}'
                        )
                    else:
                        logger.warning(
                            f'[RSS] Campaign send failed for "{post["title"]}" — '
                            f'will retry next poll cycle'
                        )
                        # Do NOT add to seen_guids — retry on next poll

        except Exception as e:
            # Catch-all so a bug never kills the daemon thread
            logger.error(f'[RSS] Unexpected error in daemon loop: {e}', exc_info=True)

        time.sleep(POLL_INTERVAL_SECONDS)


# ---------------------------------------------------------------------------
# Standalone entry point (for manual testing)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    rss_daemon_loop()
