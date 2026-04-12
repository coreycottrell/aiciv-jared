# PureBrain.ai — Brevo Automation Implementation Plan

**Prepared by**: marketing-automation-specialist
**Date**: 2026-02-23
**Covers**: 90-Day Marketing Automation Roadmap — Brevo Implementation

---

## Current Infrastructure Baseline

Before reading any section, know what already exists:

| System | Status | Location |
|--------|--------|----------|
| Neural Feed welcome sequence (7 emails) | ACTIVE — custom Python daemon | `tools/neural_feed_welcome_sequence.py` |
| Audit lead nurture (4 emails) | Templates CREATED (IDs 13-16), workflow needs Brevo GUI | `config/audit_nurture_template_ids.json` |
| Brevo List 3 (Neural Feed) | ACTIVE, 4 subscribers | List ID: 3 |
| Brevo List 4 (Enterprise Leads) | ACTIVE | List ID: 4 |
| P.S. reply invitations | Deployed to templates 2, 4, 5 | Via `tools/deploy_ps_sections.py` |

### CRITICAL ARCHITECTURAL FACT (Do Not Forget)

**Brevo has zero REST API endpoints for creating automation workflows.**

Endpoints confirmed to return 404:
- `GET/POST https://api.brevo.com/v3/automations`
- `GET/POST https://api.brevo.com/v3/workflows`

This means every multi-step automation with time delays must be either:
1. Built manually in the Brevo dashboard GUI at https://app.brevo.com/automation/
2. Or implemented as a custom Python daemon (preferred for complex sequences — gives Telegram notifications, retry logic, full state visibility)

Templates CAN be created and updated via API (`POST /v3/smtp/templates`). Workflows cannot.

---

## ITEM 1: RSS-to-Email Automation

### Objective

Automatically send a newsletter to List 3 (Neural Feed) whenever a new blog post publishes at `purebrain.ai/blog`. RSS feed source: `https://purebrain.ai/feed/`

### Architecture Decision

**Use Brevo's native RSS Campaign feature** (dashboard-based) rather than a custom daemon.

Brevo natively supports RSS-triggered campaigns — this is one of the few automation-adjacent features accessible without coding. It checks the RSS feed on a schedule and sends a campaign when new items are detected.

**Why not the custom daemon approach here:**
The welcome sequence daemon polls Brevo contact lists. RSS polling requires checking an external URL and creating a campaign send — that's more complex to replicate and Brevo's native RSS feature is well-tested.

---

### Dashboard Setup Steps (Brevo GUI)

**Time required**: 20-30 minutes

#### Step 1: Access RSS Campaign Builder

1. Log into https://app.brevo.com
2. Navigate to: **Campaigns** → **Email Campaigns** → **New Campaign**
3. Select **"RSS Campaign"** (not Classic or A/B Test)

#### Step 2: Configure RSS Settings

```
RSS Feed URL: https://purebrain.ai/feed/
Campaign Name: [Internal] Neural Feed — Auto Blog Distribution
Send Frequency: As soon as new articles are published
Maximum articles per email: 1 (one post per send — not digest format)
```

> Note: If Brevo asks for a schedule (daily/weekly/immediately), choose **"As soon as a new article is published"** if available. If not available on your Brevo plan, choose **Daily** and set the send time to 9:00 AM EST.

#### Step 3: Configure Sender Details

```
From Name: Jared Sanborn / PureBrain
From Email: support@puremarketing.ai (must be verified in Brevo senders)
Reply-to: jared@puretechnology.nyc
Subject line template: New from The Neural Feed: {{rss:title}}
Preview text: {{rss:excerpt|truncatewords:20}}
```

#### Step 4: Select Recipients

```
Send to: List 3 — The Neural Feed - Blog Subscribers
Exclude: Unsubscribed contacts (automatic in Brevo)
```

> IMPORTANT: Do NOT include List 4 (Enterprise Leads) in this campaign. Blog subscribers and enterprise leads are separate audiences with different expectations.

#### Step 5: Design the Email Template

Use the PureBrain RSS email template HTML below. This must be entered in the **"Drag & Drop"** editor using the **"Code Editor"** tab, or under **"Rich Text"** → **"HTML editor"**.

**COMPLETE RSS EMAIL TEMPLATE:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>New from The Neural Feed</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background-color: #080a12; font-family: 'Helvetica Neue', Arial, sans-serif; }
  .wrapper { background-color: #080a12; padding: 20px 0; }
  .container { max-width: 600px; margin: 0 auto; background-color: #0d1117; border-radius: 8px; overflow: hidden; }
  .header { background-color: #0d1117; padding: 28px 40px 24px; border-bottom: 1px solid #1a2235; text-align: center; }
  .logo-text { font-size: 22px; font-weight: 700; letter-spacing: 2px; }
  .logo-main { color: #2a93c1; }
  .logo-ai { color: #f1420b; }
  .logo-domain { color: #8899a6; font-weight: 400; font-size: 14px; }
  .sub-header { color: #5a6a7a; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; margin-top: 6px; }
  .content { padding: 36px 40px 32px; }
  .new-post-label { display: inline-block; background-color: #f1420b; color: #ffffff; font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 10px; border-radius: 3px; margin-bottom: 18px; }
  .post-title { font-size: 24px; font-weight: 700; color: #e8f4fd; line-height: 1.3; margin-bottom: 16px; }
  .post-excerpt { font-size: 15px; color: #b8c5d6; line-height: 1.7; margin-bottom: 28px; }
  .divider { border: none; border-top: 1px solid #1a2235; margin: 24px 0; }
  .cta-block { text-align: center; margin: 28px 0; }
  .cta-button { display: inline-block; background-color: #2a93c1; color: #ffffff !important; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-size: 15px; font-weight: 600; letter-spacing: 0.5px; }
  .secondary-note { font-size: 13px; color: #5a6a7a; text-align: center; margin-top: 12px; }
  .signature { margin-top: 32px; padding-top: 20px; border-top: 1px solid #1a2235; }
  .sig-name { font-size: 14px; color: #8899a6; }
  .sig-title { font-size: 12px; color: #5a6a7a; margin-top: 4px; }
  .footer { background-color: #060810; padding: 24px 40px; text-align: center; border-top: 1px solid #1a2235; }
  .footer p { font-size: 12px; color: #4a5568; line-height: 1.6; }
  .footer a { color: #2a93c1; text-decoration: none; }
</style>
</head>
<body>
<div class="wrapper">
  <div class="container">

    <!-- Header -->
    <div class="header">
      <div class="logo-text">
        <span class="logo-main">PUREBR</span><span class="logo-ai">AI</span><span class="logo-main">N</span><span class="logo-domain">.ai</span>
      </div>
      <div class="sub-header">The Neural Feed</div>
    </div>

    <!-- Content -->
    <div class="content">

      <div class="new-post-label">New Post</div>

      <h1 class="post-title">{{rss:title}}</h1>

      <p class="post-excerpt">{{rss:excerpt|truncatewords:60}}</p>

      <hr class="divider">

      <div class="cta-block">
        <a href="{{rss:url}}?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-rss&utm_content=read-post" class="cta-button">
          Read the Full Post
        </a>
        <p class="secondary-note">Or visit <a href="https://purebrain.ai/blog?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-rss&utm_content=blog-footer" style="color: #2a93c1;">purebrain.ai/blog</a> for all posts</p>
      </div>

      <hr class="divider">

      <!-- Teaser for PureBrain -->
      <p style="font-size: 14px; color: #8899a6; line-height: 1.7; text-align: center;">
        PureBrain is the AI partner for businesses ready to go beyond chatbots.<br>
        <a href="https://purebrain.ai/#awakening?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-rss&utm_content=footer-cta" style="color: #f1420b; text-decoration: none; font-weight: 600;">See how it works →</a>
      </p>

      <div class="signature">
        <p class="sig-name">Jared Sanborn</p>
        <p class="sig-title">Founder, PureBrain &amp; Pure Technology</p>
      </div>

    </div>

    <!-- Footer -->
    <div class="footer">
      <p>
        You're receiving this because you subscribed to The Neural Feed.<br>
        <a href="{{ unsubscribe }}">Unsubscribe</a> &nbsp;|&nbsp;
        <a href="https://purebrain.ai/blog">View all posts</a>
      </p>
    </div>

  </div>
</div>
</body>
</html>
```

> CRITICAL: The `{{ unsubscribe }}` placeholder MUST remain exactly as written. Brevo auto-replaces it with the unsubscribe URL. Removing it causes Brevo to inject a plain text unsubscribe that breaks the template layout.

#### Step 6: Preview and Test

1. In the Brevo campaign editor, click **"Preview"**
2. Verify: dark background (#080a12), blue logo with orange AI, orange "New Post" badge
3. Click **"Send Test"** → send to `jared@puretechnology.nyc`
4. Check inbox for: correct rendering, UTM parameters in links, unsubscribe link works

#### Step 7: Activate

1. Click **"Schedule"** or **"Activate RSS Campaign"**
2. Brevo will check the feed and send within the configured window when a new post appears

---

### Fallback: Custom Python RSS Daemon

If Brevo's RSS campaign feature is not available on the current plan level, implement this Python script instead. Place at `/home/jared/projects/AI-CIV/aether/tools/rss_to_email.py`.

```python
#!/usr/bin/env python3
"""
RSS-to-Email Daemon for PureBrain Neural Feed
Polls purebrain.ai/feed/ and sends campaign emails when new posts detected.
Run as part of purebrain_log_server.py daemon thread.
"""

import os
import json
import time
import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
RSS_URL = 'https://purebrain.ai/feed/'
STATE_FILE = '/home/jared/projects/AI-CIV/aether/config/rss_email_state.json'
POLL_INTERVAL_SECONDS = 3600  # Check every hour
LIST_3_ID = 3
SENDER_EMAIL = 'support@puremarketing.ai'
SENDER_NAME = 'Jared Sanborn / PureBrain'

BREVO_HEADERS = {
    'api-key': BREVO_API_KEY,
    'Content-Type': 'application/json'
}


def load_state():
    """Load seen post GUIDs from disk."""
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'seen_guids': [], 'sent_campaigns': []}


def save_state(state):
    """Persist state to disk."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def fetch_rss():
    """Fetch and parse the RSS feed. Returns list of items."""
    try:
        response = requests.get(RSS_URL, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        channel = root.find('channel')
        items = []
        for item in channel.findall('item'):
            guid = item.find('guid').text if item.find('guid') is not None else ''
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            description = item.find('description').text if item.find('description') is not None else ''
            # Strip HTML tags from description for plain excerpt
            import re
            excerpt = re.sub('<[^<]+?>', '', description)[:300]
            items.append({
                'guid': guid,
                'title': title,
                'link': link,
                'excerpt': excerpt.strip()
            })
        return items
    except Exception as e:
        print(f'[RSS] Error fetching feed: {e}')
        return []


def get_list_3_subscriber_count():
    """Get count of List 3 subscribers for logging."""
    url = 'https://api.brevo.com/v3/contacts/lists/3'
    try:
        r = requests.get(url, headers=BREVO_HEADERS)
        if r.status_code == 200:
            return r.json().get('totalSubscribers', 0)
    except Exception:
        pass
    return 0


def send_rss_campaign(post):
    """
    Send a newsletter email for a new blog post.
    Uses Brevo transactional email API to send to all List 3 contacts.
    Note: For true "campaign" sends (with unsubscribe tracking), use
    POST /v3/emailCampaigns + send immediately. See below.
    """

    # Build UTM-tagged link
    utm_link = f"{post['link']}?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-rss&utm_content=read-post"

    # Build email HTML (matches RSS template above)
    html_content = f"""<!DOCTYPE html>
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
  .logo-main {{ color: #2a93c1; font-size: 22px; font-weight: 700; letter-spacing: 2px; }}
  .logo-ai {{ color: #f1420b; font-size: 22px; font-weight: 700; }}
  .sub-header {{ color: #5a6a7a; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; margin-top: 6px; }}
  .content {{ padding: 36px 40px 32px; }}
  .new-post-label {{ display: inline-block; background-color: #f1420b; color: #ffffff; font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 10px; border-radius: 3px; margin-bottom: 18px; }}
  .post-title {{ font-size: 24px; font-weight: 700; color: #e8f4fd; line-height: 1.3; margin-bottom: 16px; }}
  .post-excerpt {{ font-size: 15px; color: #b8c5d6; line-height: 1.7; margin-bottom: 28px; }}
  .cta-button {{ display: inline-block; background-color: #2a93c1; color: #ffffff !important; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-size: 15px; font-weight: 600; }}
  .footer {{ background-color: #060810; padding: 24px 40px; text-align: center; border-top: 1px solid #1a2235; }}
  .footer p {{ font-size: 12px; color: #4a5568; line-height: 1.6; }}
  .footer a {{ color: #2a93c1; text-decoration: none; }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="container">
    <div class="header">
      <span class="logo-main">PUREBR</span><span class="logo-ai">AI</span><span class="logo-main">N</span>
      <div class="sub-header">The Neural Feed</div>
    </div>
    <div class="content">
      <div class="new-post-label">New Post</div>
      <h1 class="post-title">{post['title']}</h1>
      <p class="post-excerpt">{post['excerpt']}...</p>
      <div style="text-align: center; margin: 28px 0;">
        <a href="{utm_link}" class="cta-button">Read the Full Post</a>
      </div>
      <hr style="border: none; border-top: 1px solid #1a2235; margin: 24px 0;">
      <p style="font-size: 14px; color: #8899a6; line-height: 1.7; text-align: center;">
        <a href="https://purebrain.ai/#awakening?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-rss&utm_content=footer-cta" style="color: #f1420b; text-decoration: none; font-weight: 600;">See how PureBrain works →</a>
      </p>
      <div style="margin-top: 32px; padding-top: 20px; border-top: 1px solid #1a2235;">
        <p style="font-size: 14px; color: #8899a6;">Jared Sanborn</p>
        <p style="font-size: 12px; color: #5a6a7a; margin-top: 4px;">Founder, PureBrain &amp; Pure Technology</p>
      </div>
    </div>
    <div class="footer">
      <p>You're receiving this because you subscribed to The Neural Feed.<br>
      <a href="{{{{ unsubscribe }}}}">Unsubscribe</a> &nbsp;|&nbsp; <a href="https://purebrain.ai/blog">View all posts</a></p>
    </div>
  </div>
</div>
</body>
</html>"""

    # Step 1: Create campaign draft
    campaign_payload = {
        'name': f'[Auto] Neural Feed — {post["title"][:50]}',
        'subject': f'New from The Neural Feed: {post["title"]}',
        'sender': {'name': SENDER_NAME, 'email': SENDER_EMAIL},
        'type': 'classic',
        'htmlContent': html_content,
        'recipients': {'listIds': [LIST_3_ID]},
        'header': 'The Neural Feed',
        'replyTo': 'jared@puretechnology.nyc'
    }

    r = requests.post(
        'https://api.brevo.com/v3/emailCampaigns',
        headers=BREVO_HEADERS,
        json=campaign_payload
    )

    if r.status_code not in [200, 201]:
        print(f'[RSS] Campaign creation failed: {r.status_code} {r.text}')
        return False

    campaign_id = r.json().get('id')
    print(f'[RSS] Campaign created: ID {campaign_id}')

    # Step 2: Send campaign immediately
    r2 = requests.post(
        f'https://api.brevo.com/v3/emailCampaigns/{campaign_id}/sendNow',
        headers=BREVO_HEADERS
    )

    if r2.status_code == 204:
        print(f'[RSS] Campaign sent successfully for: {post["title"]}')
        return campaign_id
    else:
        print(f'[RSS] Campaign send failed: {r2.status_code} {r2.text}')
        return False


def rss_daemon_loop():
    """Main polling loop. Run in a daemon thread."""
    print('[RSS] RSS-to-Email daemon starting...')

    while True:
        state = load_state()
        posts = fetch_rss()

        for post in posts:
            guid = post['guid']
            if guid not in state['seen_guids']:
                print(f'[RSS] New post detected: {post["title"]}')
                campaign_id = send_rss_campaign(post)

                if campaign_id:
                    state['seen_guids'].append(guid)
                    state['sent_campaigns'].append({
                        'guid': guid,
                        'title': post['title'],
                        'link': post['link'],
                        'campaign_id': campaign_id,
                        'sent_at': datetime.utcnow().isoformat()
                    })
                    save_state(state)

                    # Notify Jared on Telegram
                    try:
                        import subprocess
                        subprocess.run([
                            '/home/jared/projects/AI-CIV/aether/tools/tg_send.sh',
                            f'New blog post auto-distributed to Neural Feed ({get_list_3_subscriber_count()} subscribers): {post["title"]}'
                        ], timeout=10)
                    except Exception:
                        pass

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == '__main__':
    rss_daemon_loop()
```

**To add to the existing daemon system**, insert this in `tools/purebrain_log_server.py`:

```python
import threading
from tools.rss_to_email import rss_daemon_loop

# Add to startup section:
rss_thread = threading.Thread(target=rss_daemon_loop, daemon=True)
rss_thread.start()
```

---

### RSS Automation Testing Checklist

- [ ] RSS feed loads correctly: `curl https://purebrain.ai/feed/` returns valid XML
- [ ] Template renders correctly in Gmail, Apple Mail, Outlook
- [ ] UTM parameters appear in all links when hovering
- [ ] Unsubscribe link is functional
- [ ] Test email received at `jared@puretechnology.nyc` before activation
- [ ] Logo renders: PUREBR(blue) + AI(orange) + N(blue) color split
- [ ] Orange "New Post" badge visible
- [ ] Dark background (#080a12) renders correctly in major clients
- [ ] CTA button links to blog post URL (not homepage)
- [ ] Footer CTA links to `https://purebrain.ai/#awakening` with UTM params
- [ ] No double-send when a post is published (state file tracking working)
- [ ] Telegram notification fires when campaign sends

### Timeline

| Action | Owner | When |
|--------|-------|------|
| Set up Brevo RSS campaign in dashboard (preferred) | Jared | Week 1, Day 1-2 |
| OR deploy Python RSS daemon (fallback) | full-stack-developer | Week 1, Day 2-3 |
| Send test campaign to jared@puretechnology.nyc | Jared | Week 1, Day 2 |
| Publish first blog post after activation, verify auto-send | Aether monitors | Week 1, Day 3-7 |

---

## ITEM 2: UTM Parameter Master Template

### Objective

Create a single reference document that governs all UTM parameters across every PureBrain touchpoint — blog CTAs, email links, social media, and paid campaigns.

### Why UTM Discipline Matters

Without consistent UTM parameters, Google Analytics 4 cannot tell you whether a conversion came from a newsletter, a LinkedIn post, or an organic blog visit. Every link from every channel needs a consistent, parseable UTM structure.

---

### UTM Framework Architecture

```
utm_source   = WHERE the traffic comes from (the platform/property)
utm_medium   = HOW it arrived (the channel type)
utm_campaign = WHAT campaign sent it (specific initiative)
utm_content  = WHICH specific element was clicked (for A/B testing)
utm_term     = (optional) WHAT search term triggered it (paid only)
```

---

### Master UTM Reference Table

#### SOURCES (`utm_source`)

| Source Value | Use When |
|-------------|----------|
| `newsletter` | Links in any Brevo email send to the full Neural Feed list |
| `welcome-sequence` | Links in the 7-email welcome sequence |
| `audit-nurture` | Links in the 4-email audit nurture sequence |
| `blog` | Internal cross-links from one blog post to another |
| `linkedin` | Links in LinkedIn posts or LinkedIn articles |
| `bluesky` | Links in Bluesky posts |
| `assessment` | Links from the AI Adoption Assessment page |
| `audit` | Links from the AI Partnership Audit page |
| `purebrain` | Links from the purebrain.ai homepage (internal navigation) |
| `organic` | Direct traffic, bookmarks (not usually set manually) |
| `referral` | Partner or third-party links |

#### MEDIUMS (`utm_medium`)

| Medium Value | Use When |
|-------------|----------|
| `email` | All email sends (newsletter, sequences, transactional) |
| `social` | Social media platforms (LinkedIn, Bluesky) |
| `website` | Internal links from our own website properties |
| `cta` | Call-to-action buttons (use with `utm_source=blog` or `utm_source=assessment`) |
| `referral` | External site links to us |

#### CAMPAIGNS (`utm_campaign`)

| Campaign Value | Use When |
|---------------|----------|
| `neural-feed-rss` | Automated RSS campaign emails |
| `neural-feed-weekly` | Manually sent weekly Neural Feed issues |
| `welcome-sequence` | 7-email new subscriber welcome |
| `audit-nurture` | 4-email audit completion follow-up |
| `re-engagement` | 3-email re-engagement series (Item 4) |
| `ai-partnership-audit` | AI Partnership Audit page and lead magnet |
| `ai-adoption-assessment` | AI Adoption Assessment page |
| `blog-{slug}` | Blog-post-specific campaigns (e.g., `blog-trust-gap`) |
| `linkedin-organic` | Organic LinkedIn content without paid spend |
| `bluesky-thread` | Bluesky thread posts |

#### CONTENT (`utm_content`) — A/B Test Differentiation

| Content Value | Use When |
|--------------|----------|
| `read-post` | Primary "Read the full post" CTA in RSS emails |
| `blog-footer` | Footer link to blog index |
| `footer-cta` | Footer CTA in email (secondary ask) |
| `header-nav` | Navigation bar links |
| `inline-link` | In-body text links within blog posts |
| `sidebar-cta` | Sidebar call-to-action widgets |
| `banner-cta` | Banner/hero CTA buttons |
| `ps-link` | P.S. section links in emails |
| `email-1` through `email-7` | Specific email in a sequence (link tracking) |

---

### Pre-Built UTM Link Templates

Copy, paste, and fill in the `[SLUG]` or specific values:

#### Email Links (Neural Feed Newsletter)

```
Blog post read CTA:
https://purebrain.ai/blog/[POST-SLUG]/?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-weekly&utm_content=read-post

Blog index footer link:
https://purebrain.ai/blog/?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-weekly&utm_content=blog-footer

Homepage awakening CTA:
https://purebrain.ai/#awakening?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-weekly&utm_content=footer-cta
```

#### Email Links (Welcome Sequence — adjust email number)

```
Email 1 primary CTA:
https://purebrain.ai/#awakening?utm_source=welcome-sequence&utm_medium=email&utm_campaign=welcome-sequence&utm_content=email-1

Email 4 CTA:
https://purebrain.ai/#awakening?utm_source=welcome-sequence&utm_medium=email&utm_campaign=welcome-sequence&utm_content=email-4
```

#### Email Links (Audit Nurture)

```
Audit nurture Email 1 CTA:
https://purebrain.ai/#awakening?utm_source=audit-nurture&utm_medium=email&utm_campaign=audit-nurture&utm_content=email-1

Audit nurture Email 4 (direct ask):
https://purebrain.ai/#awakening?utm_source=audit-nurture&utm_medium=email&utm_campaign=audit-nurture&utm_content=email-4
```

#### LinkedIn Post Links

```
Standard LinkedIn post CTA to homepage:
https://purebrain.ai/#awakening?utm_source=linkedin&utm_medium=social&utm_campaign=linkedin-organic&utm_content=post-cta

LinkedIn post to blog post:
https://purebrain.ai/blog/[POST-SLUG]/?utm_source=linkedin&utm_medium=social&utm_campaign=linkedin-organic&utm_content=post-link
```

#### Bluesky Thread Links

```
Bluesky thread to blog post:
https://purebrain.ai/blog/[POST-SLUG]/?utm_source=bluesky&utm_medium=social&utm_campaign=bluesky-thread&utm_content=thread-link

Bluesky thread to homepage:
https://purebrain.ai/#awakening?utm_source=bluesky&utm_medium=social&utm_campaign=bluesky-thread&utm_content=cta
```

#### Assessment and Audit Page Links

```
Assessment page inline CTA:
https://purebrain.ai/#awakening?utm_source=assessment&utm_medium=cta&utm_campaign=ai-adoption-assessment&utm_content=banner-cta

Audit page to homepage:
https://purebrain.ai/#awakening?utm_source=audit&utm_medium=cta&utm_campaign=ai-partnership-audit&utm_content=banner-cta
```

#### Blog Internal Cross-Links

```
Blog post linking to another blog post:
https://purebrain.ai/blog/[TARGET-SLUG]/?utm_source=blog&utm_medium=website&utm_campaign=blog-[SOURCE-SLUG]&utm_content=inline-link

Blog post CTA to homepage:
https://purebrain.ai/#awakening?utm_source=blog&utm_medium=cta&utm_campaign=blog-[SOURCE-SLUG]&utm_content=footer-cta
```

---

### GA4 Setup: UTM Tracking in Google Analytics 4

For UTMs to show up correctly in GA4:

1. **Go to**: GA4 → Admin → Data Streams → purebrain.ai → Configure tag settings
2. **Enable**: "Allow manual tagging to override auto-tagging" if using Google Ads
3. **Create custom dimensions** (GA4 → Admin → Custom Definitions → Create):
   - `utm_campaign` → Event-scoped → `campaign`
   - `utm_content` → Event-scoped → `content`
   - `utm_source` → Event-scoped → `source`
   - `utm_medium` → Event-scoped → `medium`
4. **Create Exploration Report**: Use Free Form exploration, add dimensions: Source, Medium, Campaign, Content. Add metrics: Sessions, Conversions.

---

### UTM Governance Rules

1. **All lowercase** — `newsletter` not `Newsletter`. Case sensitivity breaks grouping.
2. **Hyphens, not underscores** — `audit-nurture` not `audit_nurture`. Hyphens are URL-safe and readable.
3. **No spaces** — spaces break URLs. Use hyphens.
4. **Add UTM to every external link from email** — not just the main CTA. Footer links, P.S. links, image alt text links.
5. **Update this document** when new campaigns are created. A stale reference is useless.
6. **Test UTMs before publishing** — paste the full URL into Google's Campaign URL Builder at `ga-dev-tools.google.com/campaign-url-builder/` to validate.

---

### Testing Checklist (UTM Template)

- [ ] All email templates updated with UTM parameters (welcome sequence, audit nurture, RSS)
- [ ] LinkedIn posts include UTM-tagged links before publishing
- [ ] Bluesky threads include UTM-tagged blog links
- [ ] Assessment page CTAs include UTM parameters
- [ ] Audit page CTAs include UTM parameters
- [ ] GA4 shows source/medium/campaign dimensions in reports within 24 hours of first click
- [ ] No raw `purebrain.ai/#awakening` links without UTMs in any published email

### Timeline

| Action | Owner | When |
|--------|-------|------|
| Distribute this UTM reference to all content creators | Aether/Jared | Week 1 |
| Retroactively update existing Brevo templates (1-16) with UTM params | full-stack-developer | Week 1-2 |
| Verify GA4 shows UTM data after first tagged click | Jared | Week 2 |
| Add UTMs to all blog post CTAs and footer blocks | full-stack-developer | Week 2 |

---

## ITEM 3: Behavioral Trigger Sequences (Week 3-4)

### Overview

Three behavioral triggers that fire sequences based on visitor or subscriber actions:
1. Pricing page / Awakening section visit trigger
2. Assessment abandonment trigger
3. Email reply trigger

### ARCHITECTURAL NOTE (Critical)

**Brevo automation workflows cannot be created via API** (confirmed across 3 sessions). Every trigger described here that requires a multi-step workflow must be built in the Brevo dashboard GUI at `https://app.brevo.com/automation/`.

However, **triggers** (the events that START an automation) CAN be sent via API using:
- `POST /v3/track/events` — for custom behavioral events
- `POST /v3/contacts` — for adding a contact attribute that triggers a workflow
- `POST /v3/contacts/lists/{listId}/contacts/add` — for adding to a triggering list

This pattern — **API triggers + GUI workflows** — is the correct architecture for PureBrain's Brevo setup.

---

### 3A: Pricing Page / Awakening Section Visit Trigger

#### What It Does

When a visitor reaches the `/#awakening` section of purebrain.ai (the pricing/CTA section), they have shown high purchase intent. This trigger fires a 2-email "intent detected" sequence.

#### Email Sequence Design

**Email 1 — Sent within 30 minutes of visit**
- Subject: `You found the awakening section, {{params.FIRSTNAME}}`
- Sender name: Jared Sanborn
- Content: "I noticed you checked out what PureBrain costs. Here's what I wish more people asked before signing up..."
- Content body: Walks through ROI calculation, not pricing. Reframes from "cost" to "investment per session."
- CTA: `https://purebrain.ai/#awakening?utm_source=welcome-sequence&utm_medium=email&utm_campaign=pricing-intent&utm_content=email-1`

**Email 2 — Sent 48 hours after Email 1 (if no conversion)**
- Subject: `What would make this obvious for you?`
- Sender name: Jared Sanborn
- Content: Address the 3 most common objections (cost, time commitment, uncertainty about results). Reply invitation: "What's making you hesitate? Reply and I'll answer directly."
- CTA: `https://purebrain.ai/#awakening?utm_source=welcome-sequence&utm_medium=email&utm_campaign=pricing-intent&utm_content=email-2`

#### Implementation: JavaScript Tracking Pixel

Add this script to the purebrain.ai homepage. It fires a Brevo event when the visitor scrolls to the `#awakening` section.

```javascript
// Add to purebrain.ai homepage — inside WordPress plugin or theme functions.php
// Fires when #awakening section enters viewport

(function() {
  var awakeningSection = document.querySelector('#awakening');
  if (!awakeningSection) return;

  var fired = false;

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting && !fired) {
        fired = true;
        observer.disconnect();

        // Get visitor's email if they're a known subscriber
        // (stored in localStorage when they subscribed via Neural Feed form)
        var subscriberEmail = localStorage.getItem('pb_subscriber_email');

        if (subscriberEmail) {
          // Fire Brevo tracking event
          trackBrevoEvent(subscriberEmail, 'awakening_section_viewed');
        }

        // Always fire analytics event regardless of email
        if (window.gtag) {
          gtag('event', 'awakening_view', {
            'event_category': 'intent',
            'event_label': 'pricing_section'
          });
        }
      }
    });
  }, {
    threshold: 0.3  // Fire when 30% of section is visible
  });

  observer.observe(awakeningSection);

  function trackBrevoEvent(email, eventName) {
    // Brevo tracking endpoint
    fetch('https://in-automate.brevo.com/api/v1/trackEvent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'ma-key': 'YOUR_BREVO_TRACKING_KEY'  // Get from Brevo → Automations → Settings → Tracking Code
      },
      body: JSON.stringify({
        event: eventName,
        email: email,
        properties: {
          page: window.location.href,
          timestamp: new Date().toISOString()
        }
      })
    }).catch(function(err) {
      console.log('Brevo tracking error:', err);
    });
  }
})();
```

**Email capture for localStorage** — also add this to the Neural Feed subscription form success handler:

```javascript
// Add to subscription form success callback
function onSubscriptionSuccess(email) {
  localStorage.setItem('pb_subscriber_email', email);
}
```

#### Brevo Dashboard Setup: Awakening Intent Workflow

1. Go to https://app.brevo.com/automation/ → **New Automation**
2. **Name**: "Pricing Intent — Awakening Section"
3. **Trigger**: "A contact triggers an event" → Event name: `awakening_section_viewed`
4. **Add step**: Send email → Subject: "You found the awakening section" → Use template (create template first via API, call it "Pricing Intent Email 1")
5. **Add step**: Wait 48 hours
6. **Add step**: Condition — "Has the contact visited `/pay-test/` or converted?" → if YES, end workflow; if NO, continue
7. **Add step**: Send email → Subject: "What would make this obvious for you?" → Template: "Pricing Intent Email 2"
8. **Activate**

#### Brevo Tracking Code Setup

1. Go to: https://app.brevo.com/automation/ → Settings (gear icon) → **"Tracking code"**
2. Copy the site tracking snippet
3. Add to purebrain.ai WordPress site via the PureBrain security plugin's additional CSS/JS section
4. This enables the `trackEvent` API endpoint to accept events

#### API Call: Template Creation (Pricing Intent Emails)

Run this script at `/home/jared/projects/AI-CIV/aether/tools/brevo_create_pricing_intent_templates.py`:

```python
#!/usr/bin/env python3
"""Create Brevo templates for Pricing Intent sequence."""

import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
HEADERS = {'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'}

def create_template(name, subject, html_content, sender_name='Jared Sanborn'):
    """Create a Brevo email template."""
    payload = {
        'templateName': name,
        'subject': subject,
        'sender': {'name': sender_name, 'email': 'support@puremarketing.ai'},
        'htmlContent': html_content,
        'replyTo': 'jared@puretechnology.nyc',
        'isActive': True,
        'tag': 'pricing-intent'
    }
    r = requests.post('https://api.brevo.com/v3/smtp/templates', headers=HEADERS, json=payload)
    print(f'[{r.status_code}] {name}: {r.json()}')
    return r.json().get('id')

# Email 1 HTML — brief version, full content TBD
email1_html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body { background: #080a12; font-family: Arial, sans-serif; }
.container { max-width: 600px; margin: 0 auto; background: #0d1117; padding: 40px; }
.header { text-align: center; padding-bottom: 24px; border-bottom: 1px solid #1a2235; margin-bottom: 28px; }
.logo-main { color: #2a93c1; font-size: 20px; font-weight: 700; letter-spacing: 2px; }
.logo-ai { color: #f1420b; font-size: 20px; font-weight: 700; }
h2 { color: #e8f4fd; font-size: 22px; margin-bottom: 16px; border-left: 3px solid #2a93c1; padding-left: 12px; }
p { color: #b8c5d6; font-size: 15px; line-height: 1.7; margin-bottom: 16px; }
.cta { display: inline-block; background: #2a93c1; color: #fff !important; padding: 14px 28px; border-radius: 6px; text-decoration: none; font-weight: 600; }
.footer { text-align: center; padding-top: 24px; border-top: 1px solid #1a2235; margin-top: 32px; font-size: 12px; color: #4a5568; }
.footer a { color: #2a93c1; text-decoration: none; }
</style></head>
<body>
<div class="container">
  <div class="header">
    <span class="logo-main">PUREBR</span><span class="logo-ai">AI</span><span class="logo-main">N</span>
  </div>
  <h2>You found the awakening section, {{params.FIRSTNAME}}</h2>
  <p>I noticed you spent some time looking at what PureBrain actually costs.</p>
  <p>Most people look at a monthly price and calculate it as "another subscription." That's the wrong frame.</p>
  <p>Here's how I'd actually calculate it: Take the value of one hour of your thinking time. Multiply by how many hours per week you spend on cognitive work that could be accelerated. That's the relevant number — not the subscription cost.</p>
  <p>Aether handles the research, the synthesis, the drafts, the patterns. You handle the judgment calls, the relationships, the decisions that require your specific experience. The math changes when you frame it that way.</p>
  <p>If you want to see what this looks like in practice for someone in your situation, I'm happy to walk through it.</p>
  <div style="text-align: center; margin: 28px 0;">
    <a href="https://purebrain.ai/#awakening?utm_source=welcome-sequence&utm_medium=email&utm_campaign=pricing-intent&utm_content=email-1" class="cta">See What Partnership Looks Like</a>
  </div>
  <p>— Jared</p>
  <div class="footer">
    <p>You're receiving this because you visited purebrain.ai.<br>
    <a href="{{ unsubscribe }}">Unsubscribe</a></p>
  </div>
</div>
</body></html>"""

email2_html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body { background: #080a12; font-family: Arial, sans-serif; }
.container { max-width: 600px; margin: 0 auto; background: #0d1117; padding: 40px; }
.header { text-align: center; padding-bottom: 24px; border-bottom: 1px solid #1a2235; margin-bottom: 28px; }
.logo-main { color: #2a93c1; font-size: 20px; font-weight: 700; letter-spacing: 2px; }
.logo-ai { color: #f1420b; font-size: 20px; font-weight: 700; }
h2 { color: #e8f4fd; font-size: 22px; margin-bottom: 16px; border-left: 3px solid #2a93c1; padding-left: 12px; }
p { color: #b8c5d6; font-size: 15px; line-height: 1.7; margin-bottom: 16px; }
.cta { display: inline-block; background: #f1420b; color: #fff !important; padding: 14px 28px; border-radius: 6px; text-decoration: none; font-weight: 600; }
.objection-block { background: #111827; border-left: 3px solid #1a2235; padding: 16px 20px; margin: 16px 0; border-radius: 4px; }
.objection-block strong { color: #e8f4fd; display: block; margin-bottom: 8px; }
.footer { text-align: center; padding-top: 24px; border-top: 1px solid #1a2235; margin-top: 32px; font-size: 12px; color: #4a5568; }
.footer a { color: #2a93c1; text-decoration: none; }
</style></head>
<body>
<div class="container">
  <div class="header">
    <span class="logo-main">PUREBR</span><span class="logo-ai">AI</span><span class="logo-main">N</span>
  </div>
  <h2>What would make this obvious for you?</h2>
  <p>I want to be direct: if you looked at PureBrain and didn't sign up, something felt uncertain. Let me address the three things I hear most often:</p>
  <div class="objection-block">
    <strong>"I'm not sure I have enough to give an AI partner."</strong>
    <p>Aether doesn't need you to have everything figured out. It needs your context — your goals, your existing work, your patterns. It learns from what you already do.</p>
  </div>
  <div class="objection-block">
    <strong>"I'm worried it'll take too long to set up."</strong>
    <p>The first session is the setup. You talk, Aether listens, a system begins. There is no onboarding form. No configuration. Just conversation.</p>
  </div>
  <div class="objection-block">
    <strong>"I don't know if the results will justify it."</strong>
    <p>Fair. This is the honest answer: it depends on how much of your work is cognitive. If you spend 10+ hours a week researching, writing, deciding, or synthesizing — the math works. If you don't, it probably won't.</p>
  </div>
  <p>What's actually making you hesitate? Reply to this email and tell me. I read every response and I'll give you a direct answer.</p>
  <div style="text-align: center; margin: 28px 0;">
    <a href="https://purebrain.ai/#awakening?utm_source=welcome-sequence&utm_medium=email&utm_campaign=pricing-intent&utm_content=email-2" class="cta">Start Your AI Partnership</a>
  </div>
  <p>— Jared</p>
  <div class="footer">
    <p><a href="{{ unsubscribe }}">Unsubscribe</a></p>
  </div>
</div>
</body></html>"""

if __name__ == '__main__':
    id1 = create_template(
        'Pricing Intent - Email 1 - Awakening Reframe',
        'You found the awakening section, {{params.FIRSTNAME}}',
        email1_html
    )
    id2 = create_template(
        'Pricing Intent - Email 2 - Objection Handler',
        'What would make this obvious for you?',
        email2_html
    )
    print(f'\nTemplate IDs: Email 1 = {id1}, Email 2 = {id2}')
    print('Next: Build the automation in Brevo dashboard using these template IDs.')
```

---

### 3B: Assessment Abandonment Trigger

#### What It Does

When someone starts the AI Adoption Assessment (`purebrain.ai/assessment/`) but doesn't reach the results page, fire a 2-email recovery sequence.

#### Detection Method

The assessment has distinct page states: start → in-progress → results. JavaScript fires a Brevo event at each stage.

```javascript
// On assessment START (first question answered)
trackBrevoEvent(email, 'assessment_started', {step: 1});

// On assessment COMPLETE (results page loads)
trackBrevoEvent(email, 'assessment_completed', {score: finalScore});

// Abandonment is detected by: assessment_started fired but assessment_completed NOT fired within 30 minutes
```

The Brevo automation handles abandonment detection via:
- Trigger: `assessment_started` event fires
- Condition: Wait 30 minutes → Check if `assessment_completed` has fired → If not, send Email 1

#### Abandonment Email Sequence

**Email 1 — 30 minutes after abandonment detected**
- Subject: `You started your AI assessment, {{params.FIRSTNAME}} — here's your partial picture`
- Content: Acknowledge they started but didn't finish. Give them a 1-paragraph snapshot of what the assessment measures. Low-pressure CTA to complete it.

**Email 2 — 48 hours later**
- Subject: `The assessment takes 3 minutes. Here's why it's worth it.`
- Content: The top 5 most surprising things people discover about their AI maturity. Curiosity hook to return and complete.

#### Brevo Dashboard Setup: Assessment Abandonment Workflow

1. Go to https://app.brevo.com/automation/ → **New Automation**
2. **Name**: "Assessment Abandonment Recovery"
3. **Trigger**: "A contact triggers an event" → `assessment_started`
4. **Step**: Wait 30 minutes
5. **Step**: Condition — "Has contact triggered event `assessment_completed`?" → IF YES: Exit workflow; IF NO: Continue
6. **Step**: Send email → Template "Assessment Abandonment Email 1"
7. **Step**: Wait 48 hours
8. **Step**: Condition — "Has contact triggered `assessment_completed`?" → IF YES: Exit; IF NO: Continue
9. **Step**: Send email → Template "Assessment Abandonment Email 2"
10. **Activate**

#### Email capture for assessment

The assessment must capture the visitor's email before they can see question 1. This is required for abandonment tracking. If the assessment currently shows the email field only on the results page, this is a blocking dependency — email capture must move to question 1.

API call to send when email is captured:

```python
def register_assessment_start(email, firstname=''):
    """Call when visitor enters email on assessment start."""
    import requests

    # Add/update contact in Brevo
    contact_data = {
        'email': email,
        'attributes': {
            'FIRSTNAME': firstname,
            'LEAD_SOURCE': 'assessment',
            'ENGAGEMENT_LEVEL': 'warm'
        },
        'listIds': [],  # Don't add to any list yet — only on completion
        'updateEnabled': True
    }
    requests.post(
        'https://api.brevo.com/v3/contacts',
        headers={'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'},
        json=contact_data
    )

    # Fire tracking event to trigger abandonment automation
    requests.post(
        'https://in-automate.brevo.com/api/v1/trackEvent',
        headers={'Content-Type': 'application/json', 'ma-key': BREVO_TRACKING_KEY},
        json={
            'event': 'assessment_started',
            'email': email,
            'properties': {'page': 'assessment', 'step': 1}
        }
    )
```

---

### 3C: Email Reply Trigger

#### What It Does

When someone replies to any PureBrain email (sequences or newsletters), the reply should be:
1. Logged in Brevo as an engagement attribute
2. Trigger a manual Jared alert via Telegram
3. Apply a tag to the contact for segmentation

#### Architecture Note

Brevo does not auto-detect replies — replies go to the `replyTo` email address (`jared@puretechnology.nyc`). This means the "trigger" is manual unless an email parsing service monitors the inbox.

**Recommended implementation: Gmail-to-Brevo Bridge**

The human-liaison agent already monitors `jared@puretechnology.nyc` for business emails. When it detects a reply to a PureBrain email (subject line contains "Re: [known subject prefix]"), it should:

1. Identify the sender's email
2. Make a Brevo API call to update their attributes
3. Send Telegram notification to Jared

**API Call: Log a reply in Brevo**

```python
def log_email_reply(contact_email, email_number, reply_excerpt=''):
    """
    Called by human-liaison when a reply to a Neural Feed email is detected.
    Updates the contact's attributes in Brevo to record the reply.
    """
    import requests
    from datetime import datetime

    BREVO_API_KEY = os.getenv('BREVO_API_KEY')
    headers = {'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'}

    # Update contact attributes
    update_payload = {
        'attributes': {
            f'EMAIL_{email_number}_REPLY': 'yes',
            'LAST_REPLY_DATE': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'ENGAGEMENT_LEVEL': 'high',
            'LEAD_SCORE': 20  # Reply = +20 lead score
        }
    }

    r = requests.put(
        f'https://api.brevo.com/v3/contacts/{contact_email}',
        headers=headers,
        json=update_payload
    )

    # Also fire a tracking event for automation triggering
    requests.post(
        'https://in-automate.brevo.com/api/v1/trackEvent',
        headers={'Content-Type': 'application/json', 'ma-key': BREVO_TRACKING_KEY},
        json={
            'event': 'email_replied',
            'email': contact_email,
            'properties': {
                'email_number': email_number,
                'excerpt': reply_excerpt[:200]
            }
        }
    )

    return r.status_code
```

**Brevo Dashboard: Reply Tag Workflow**

1. **Automation name**: "Email Reply — High Engagement Tag"
2. **Trigger**: "A contact triggers event `email_replied`"
3. **Step**: Add tag "email-replier"
4. **Step**: Update attribute ENGAGEMENT_LEVEL = "high"
5. **Step**: Add to List 10 (High Intent — create this list if it doesn't exist)
6. **Activate**

---

### Behavioral Triggers Testing Checklist

- [ ] Brevo site tracking code installed on purebrain.ai (verify in browser DevTools → Network → watch for `in-automate.brevo.com`)
- [ ] `localStorage` correctly saves subscriber email on Neural Feed form submission
- [ ] Awakening section scroll fires `awakening_section_viewed` event (test in DevTools console)
- [ ] Pricing intent Email 1 arrives within 30 minutes of awakening visit (test with a real email)
- [ ] Assessment starts fire `assessment_started` event (verify in Brevo Automation Logs)
- [ ] Assessment abandonment Email 1 arrives 30 minutes after abandonment (test by not completing)
- [ ] Reply to welcome sequence email → Brevo attribute `EMAIL_1_REPLY` updates to "yes" within 1 hour (verify via `GET /v3/contacts/{email}`)
- [ ] Telegram notification fires on reply detection

---

### Behavioral Triggers Timeline

| Action | Owner | When |
|--------|-------|------|
| Install Brevo tracking code on purebrain.ai | full-stack-developer | Week 3, Day 1 |
| Add assessment email capture at question 1 | full-stack-developer | Week 3, Day 1-2 |
| Deploy awakening section scroll tracking JS | full-stack-developer | Week 3, Day 2 |
| Create pricing intent templates via API script | full-stack-developer (runs the script) | Week 3, Day 2 |
| Build pricing intent workflow in Brevo GUI | Jared (20 min) | Week 3, Day 3 |
| Build assessment abandonment workflow in Brevo GUI | Jared (20 min) | Week 3, Day 3 |
| Build email reply workflow in Brevo GUI | Jared (10 min) | Week 3, Day 4 |
| Test all three triggers with real email addresses | Aether (automated) | Week 3, Day 5-7 |
| Monitor first 7 days: verify trigger rates and email deliverability | Aether | Week 4 |

---

## ITEM 4: Re-engagement Sequence (Week 3-4)

### Objective

Subscribers who have been in List 3 (Neural Feed) for 45+ days without opening an email get a 3-email series to either re-engage them or cleanly remove them from the list.

### Why 45 Days

The welcome sequence runs for 21 days. Adding 24 days gives new subscribers time to read a few regular Neural Feed issues before being flagged as inactive. 45 days is long enough to be meaningful inactivity without being so long that the contact is entirely cold.

### Segmentation: Who Gets This Sequence

**Target**: List 3 contacts who:
- Subscribed more than 45 days ago
- Have not opened ANY email in the last 45 days
- Are NOT currently in the welcome sequence (welcome sequence complete = true)
- Have not yet received this re-engagement sequence

**Exclude**:
- Contacts who have already received the re-engagement sequence (tag: `re-engagement-sent`)
- Contacts added in last 44 days
- List 4 contacts (enterprise leads have different re-engagement)

---

### Re-engagement Email Sequence Design

#### Email 1: "We noticed you've been quiet" (Day 0)

**Subject**: `We've missed you, {{params.FIRSTNAME}}`
**Preview text**: `A soft check-in from PureBrain.`
**Sender name**: Jared Sanborn
**Delay from trigger**: Immediate

**Purpose**: Warm re-introduction. No pressure. Acknowledge the gap without making them feel bad. Remind them what they subscribed for.

**Full HTML Template**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>We've missed you</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background-color: #080a12; font-family: 'Helvetica Neue', Arial, sans-serif; }
  .wrapper { background-color: #080a12; padding: 20px 0; }
  .container { max-width: 600px; margin: 0 auto; background-color: #0d1117; border-radius: 8px; overflow: hidden; }
  .header { background-color: #0d1117; padding: 28px 40px 24px; border-bottom: 1px solid #1a2235; text-align: center; }
  .logo-main { color: #2a93c1; font-size: 22px; font-weight: 700; letter-spacing: 2px; }
  .logo-ai { color: #f1420b; font-size: 22px; font-weight: 700; }
  .sub-header { color: #5a6a7a; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; margin-top: 6px; }
  .content { padding: 36px 40px 32px; }
  h2 { color: #e8f4fd; font-size: 22px; margin-bottom: 20px; border-left: 3px solid #2a93c1; padding-left: 12px; line-height: 1.3; }
  p { color: #b8c5d6; font-size: 15px; line-height: 1.7; margin-bottom: 16px; }
  .highlight-box { background-color: #111827; border-left: 3px solid #2a93c1; padding: 16px 20px; margin: 20px 0; border-radius: 4px; }
  .highlight-box p { color: #8899a6; font-size: 14px; margin-bottom: 0; }
  .cta-block { text-align: center; margin: 28px 0; }
  .cta-button { display: inline-block; background-color: #2a93c1; color: #ffffff !important; text-decoration: none; padding: 14px 28px; border-radius: 6px; font-size: 15px; font-weight: 600; }
  .signature { margin-top: 28px; padding-top: 20px; border-top: 1px solid #1a2235; }
  .sig-name { font-size: 14px; color: #8899a6; }
  .sig-title { font-size: 12px; color: #5a6a7a; margin-top: 4px; }
  .ps-block { margin-top: 24px; padding-top: 20px; border-top: 1px solid #1a2235; text-align: center; }
  .ps-label { color: #a0adc0; font-style: italic; font-size: 13px; }
  .ps-text { color: #b8c5d6; font-size: 13px; margin-top: 6px; line-height: 1.6; }
  .footer { background-color: #060810; padding: 24px 40px; text-align: center; border-top: 1px solid #1a2235; }
  .footer p { font-size: 12px; color: #4a5568; line-height: 1.6; }
  .footer a { color: #2a93c1; text-decoration: none; }
</style>
</head>
<body>
<div class="wrapper">
  <div class="container">
    <div class="header">
      <span class="logo-main">PUREBR</span><span class="logo-ai">AI</span><span class="logo-main">N</span>
      <div class="sub-header">The Neural Feed</div>
    </div>
    <div class="content">
      <h2>Hey {{params.FIRSTNAME}} — it's been a while</h2>
      <p>I noticed you haven't opened The Neural Feed in a while. That's okay — inboxes get full, life gets busy, priorities shift.</p>
      <p>I'm not here to guilt you into anything. I just wanted to check in and make sure the content is still relevant to where you are right now.</p>
      <div class="highlight-box">
        <p>You subscribed to The Neural Feed to stay up to speed on AI — not as a tool, but as a genuine partner in the way you work. That's still what we write about.</p>
      </div>
      <p>If that's still you, I'd love to have you back. Here are the last three posts in case you missed them:</p>
      <ul style="color: #b8c5d6; font-size: 15px; line-height: 1.8; padding-left: 20px; margin: 12px 0;">
        <li><a href="https://purebrain.ai/blog/?utm_source=newsletter&utm_medium=email&utm_campaign=re-engagement&utm_content=email-1-link1" style="color: #2a93c1; text-decoration: none;">Visit the blog to see recent posts →</a></li>
      </ul>
      <div class="cta-block">
        <a href="https://purebrain.ai/blog/?utm_source=newsletter&utm_medium=email&utm_campaign=re-engagement&utm_content=email-1-cta" class="cta-button">
          Catch Up on Recent Posts
        </a>
      </div>
      <div class="signature">
        <p class="sig-name">Jared Sanborn</p>
        <p class="sig-title">Founder, PureBrain &amp; Pure Technology</p>
      </div>
      <div class="ps-block">
        <p class="ps-label">P.S.</p>
        <p class="ps-text">If The Neural Feed isn't what you expected when you subscribed, just reply and tell me. I'd genuinely rather know than keep sending something that doesn't land.</p>
      </div>
    </div>
    <div class="footer">
      <p>You're receiving this because you subscribed to The Neural Feed at purebrain.ai.<br>
      <a href="{{ unsubscribe }}">Unsubscribe</a> &nbsp;|&nbsp; <a href="https://purebrain.ai/blog">View all posts</a></p>
    </div>
  </div>
</div>
</body>
</html>
```

---

#### Email 2: "What would bring you back?" (Day 7)

**Subject**: `Quick question about what you need, {{params.FIRSTNAME}}`
**Preview text**: `One question. Takes 10 seconds to answer.`
**Sender name**: Jared Sanborn
**Delay from Email 1**: 7 days

**Purpose**: Direct feedback request. Shorter email. Conversational tone. Focused on one ask: what would make this worth their attention?

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Quick question</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background-color: #080a12; font-family: 'Helvetica Neue', Arial, sans-serif; }
  .wrapper { background-color: #080a12; padding: 20px 0; }
  .container { max-width: 600px; margin: 0 auto; background-color: #0d1117; border-radius: 8px; overflow: hidden; }
  .header { background-color: #0d1117; padding: 28px 40px 24px; border-bottom: 1px solid #1a2235; text-align: center; }
  .logo-main { color: #2a93c1; font-size: 22px; font-weight: 700; letter-spacing: 2px; }
  .logo-ai { color: #f1420b; font-size: 22px; font-weight: 700; }
  .content { padding: 36px 40px 32px; }
  h2 { color: #e8f4fd; font-size: 22px; margin-bottom: 20px; border-left: 3px solid #2a93c1; padding-left: 12px; }
  p { color: #b8c5d6; font-size: 15px; line-height: 1.7; margin-bottom: 16px; }
  .question-block { background-color: #111827; border: 1px solid #1a2235; border-left: 4px solid #f1420b; padding: 20px 24px; margin: 24px 0; border-radius: 4px; font-size: 17px; color: #e8f4fd; font-weight: 600; line-height: 1.4; }
  .cta-block { text-align: center; margin: 28px 0; }
  .cta-button { display: inline-block; background-color: #2a93c1; color: #ffffff !important; text-decoration: none; padding: 14px 28px; border-radius: 6px; font-size: 15px; font-weight: 600; }
  .signature { margin-top: 28px; padding-top: 20px; border-top: 1px solid #1a2235; }
  .sig-name { font-size: 14px; color: #8899a6; }
  .sig-title { font-size: 12px; color: #5a6a7a; margin-top: 4px; }
  .footer { background-color: #060810; padding: 24px 40px; text-align: center; border-top: 1px solid #1a2235; }
  .footer p { font-size: 12px; color: #4a5568; line-height: 1.6; }
  .footer a { color: #2a93c1; text-decoration: none; }
</style>
</head>
<body>
<div class="wrapper">
  <div class="container">
    <div class="header">
      <span class="logo-main">PUREBR</span><span class="logo-ai">AI</span><span class="logo-main">N</span>
    </div>
    <div class="content">
      <h2>One honest question, {{params.FIRSTNAME}}</h2>
      <p>I sent you a check-in last week. You didn't open it — which is fine, that's data too.</p>
      <p>I have one question for you:</p>
      <div class="question-block">
        What would make The Neural Feed something you actually look forward to reading?
      </div>
      <p>Topics, format, frequency, depth — anything. Just reply to this email. Even a single sentence helps.</p>
      <p>I'm not trying to sell you anything with this email. I'm genuinely trying to make something useful for people building with AI. Your feedback makes that better.</p>
      <div class="cta-block">
        <a href="https://purebrain.ai/blog/?utm_source=newsletter&utm_medium=email&utm_campaign=re-engagement&utm_content=email-2-cta" class="cta-button">
          Or Browse Recent Posts
        </a>
      </div>
      <div class="signature">
        <p class="sig-name">Jared Sanborn</p>
        <p class="sig-title">Founder, PureBrain &amp; Pure Technology</p>
      </div>
    </div>
    <div class="footer">
      <p><a href="{{ unsubscribe }}">Unsubscribe</a> &nbsp;|&nbsp; <a href="https://purebrain.ai/blog">View blog</a></p>
    </div>
  </div>
</div>
</body>
</html>
```

---

#### Email 3: "Last chance before we let you go" (Day 21)

**Subject**: `Before I remove you from The Neural Feed, {{params.FIRSTNAME}}`
**Preview text**: `One click to stay. Otherwise, farewell.`
**Sender name**: Jared Sanborn
**Delay from Email 2**: 14 days (21 days total from Email 1)

**Purpose**: Sunset email. Clear, honest, low-pressure. One-click "keep me subscribed" button. If they don't click, remove from List 3. This protects deliverability.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Before we let you go</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background-color: #080a12; font-family: 'Helvetica Neue', Arial, sans-serif; }
  .wrapper { background-color: #080a12; padding: 20px 0; }
  .container { max-width: 600px; margin: 0 auto; background-color: #0d1117; border-radius: 8px; overflow: hidden; }
  .header { background-color: #0d1117; padding: 28px 40px 24px; border-bottom: 1px solid #1a2235; text-align: center; }
  .logo-main { color: #2a93c1; font-size: 22px; font-weight: 700; letter-spacing: 2px; }
  .logo-ai { color: #f1420b; font-size: 22px; font-weight: 700; }
  .content { padding: 36px 40px 32px; }
  h2 { color: #e8f4fd; font-size: 22px; margin-bottom: 20px; border-left: 3px solid #f1420b; padding-left: 12px; }
  p { color: #b8c5d6; font-size: 15px; line-height: 1.7; margin-bottom: 16px; }
  .deadline-block { background-color: #1a0a08; border: 1px solid #f1420b; border-radius: 6px; padding: 20px 24px; margin: 24px 0; text-align: center; }
  .deadline-block p { color: #f1420b; font-weight: 600; font-size: 15px; margin-bottom: 0; }
  .cta-block { text-align: center; margin: 28px 0; }
  .cta-button { display: inline-block; background-color: #f1420b; color: #ffffff !important; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-size: 16px; font-weight: 700; }
  .secondary-text { font-size: 13px; color: #5a6a7a; text-align: center; margin-top: 12px; }
  .signature { margin-top: 28px; padding-top: 20px; border-top: 1px solid #1a2235; }
  .sig-name { font-size: 14px; color: #8899a6; }
  .sig-title { font-size: 12px; color: #5a6a7a; margin-top: 4px; }
  .footer { background-color: #060810; padding: 24px 40px; text-align: center; border-top: 1px solid #1a2235; }
  .footer p { font-size: 12px; color: #4a5568; line-height: 1.6; }
  .footer a { color: #2a93c1; text-decoration: none; }
</style>
</head>
<body>
<div class="wrapper">
  <div class="container">
    <div class="header">
      <span class="logo-main">PUREBR</span><span class="logo-ai">AI</span><span class="logo-main">N</span>
    </div>
    <div class="content">
      <h2>This is probably my last email to you</h2>
      <p>You've been subscribed to The Neural Feed for a while now, but you haven't opened any of our emails in over 45 days — including the two check-ins I sent recently.</p>
      <p>I respect your inbox. So I'm going to do something most newsletters don't: let you go.</p>
      <p>In 7 days, I'll remove your email from The Neural Feed. No hard feelings — you subscribed when something was interesting to you. If that interest has shifted, that's completely fine.</p>
      <div class="deadline-block">
        <p>If you want to keep receiving The Neural Feed, click the button below within 7 days.</p>
      </div>
      <div class="cta-block">
        <a href="https://purebrain.ai/stay-subscribed/?email={{params.EMAIL}}&utm_source=newsletter&utm_medium=email&utm_campaign=re-engagement&utm_content=email-3-stay" class="cta-button">
          Yes, Keep Me Subscribed
        </a>
        <p class="secondary-text">Or do nothing — we'll remove you in 7 days and say thank you for your time.</p>
      </div>
      <p>If you ever want to re-subscribe, the door is always open at <a href="https://purebrain.ai/blog?utm_source=newsletter&utm_medium=email&utm_campaign=re-engagement&utm_content=email-3-blog" style="color: #2a93c1;">purebrain.ai/blog</a>.</p>
      <div class="signature">
        <p class="sig-name">Jared Sanborn</p>
        <p class="sig-title">Founder, PureBrain &amp; Pure Technology</p>
      </div>
    </div>
    <div class="footer">
      <p>Or simply: <a href="{{ unsubscribe }}">Unsubscribe now</a> and we'll remove you immediately.</p>
    </div>
  </div>
</div>
</body>
</html>
```

---

### Re-engagement: "Stay Subscribed" Confirmation

The "Yes, Keep Me Subscribed" button in Email 3 links to `purebrain.ai/stay-subscribed/`. This page needs to:

1. Confirm re-subscription ("You're still in. Thanks for staying with us.")
2. Fire a Brevo API call (via a WordPress shortcode or POST to `/purebrain/v1/guide-unlock` endpoint) that:
   - Adds tag `re-engaged` to contact
   - Removes tag `re-engagement-sent`
   - Resets their engagement date
   - Removes them from any "sunset pending" list

**WordPress page setup**: Create a simple confirmation page at `/stay-subscribed/`. Use Elementor canvas template. Add shortcode or JavaScript that fires on page load.

**JavaScript to add to the stay-subscribed page**:

```javascript
// Runs on page load of /stay-subscribed/
// Reads email from URL parameter and calls the server endpoint

(function() {
  var urlParams = new URLSearchParams(window.location.search);
  var email = urlParams.get('email');

  if (!email) return;

  // Call the existing server-side proxy endpoint
  fetch('/purebrain/v1/guide-unlock', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      action: 're-subscribe',
      email: email
    })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    console.log('Re-subscription confirmed:', data);
    // Show success message (already visible via page design)
  })
  .catch(function(err) {
    console.log('Re-subscription error:', err);
    // Page still shows success — don't alarm the user
  });
})();
```

---

### Re-engagement: Brevo Dashboard Setup

1. Go to https://app.brevo.com/automation/ → **New Automation**
2. **Name**: "45-Day Inactive Re-engagement"
3. **Trigger**: Choose **"Inactivity on emails"** → "Contact has not opened any campaign in" → 45 days → Applies to: List 3
4. **Step**: Condition — "Has tag `re-engagement-sent`?" → IF YES: Exit (already received sequence); IF NO: Continue
5. **Step**: Add tag `re-engagement-sent`
6. **Step**: Send email → Template "Re-engagement Email 1 — We Noticed You've Been Quiet"
7. **Step**: Wait 7 days
8. **Step**: Condition — "Has contact opened any email in last 7 days?" → IF YES: Remove tag `re-engagement-sent`, add `re-engaged`, exit; IF NO: Continue
9. **Step**: Send email → Template "Re-engagement Email 2 — What Would Bring You Back"
10. **Step**: Wait 14 days
11. **Step**: Condition — "Has contact opened any email?" → IF YES: Exit with re-engaged tag; IF NO: Continue
12. **Step**: Send email → Template "Re-engagement Email 3 — Last Chance Before We Let You Go"
13. **Step**: Wait 7 days
14. **Step**: Condition — "Has contact clicked `re-subscribe` link in Email 3?" → IF YES: Remove from automation, keep in List 3; IF NO: Remove from List 3 (unsubscribe)
15. **Activate**

> Note: Step 14's "remove from List 3" is implemented by adding the contact to an "Inactive - Removed" list and then unsubscribing them from List 3 in the final automation step.

---

### API Call: Create Re-engagement Templates

Save this as `/home/jared/projects/AI-CIV/aether/tools/brevo_create_reengagement_templates.py`:

```python
#!/usr/bin/env python3
"""Create Brevo templates for the 3-email re-engagement sequence."""

import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
HEADERS = {'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'}

def create_template(name, subject, html_content):
    """Create a Brevo email template. Returns template ID."""
    payload = {
        'templateName': name,
        'subject': subject,
        'sender': {'name': 'Jared Sanborn', 'email': 'support@puremarketing.ai'},
        'htmlContent': html_content,
        'replyTo': 'jared@puretechnology.nyc',
        'isActive': True,
        'tag': 're-engagement'
    }
    r = requests.post('https://api.brevo.com/v3/smtp/templates', headers=HEADERS, json=payload)
    result = r.json()
    template_id = result.get('id', 'ERROR')
    print(f'[{r.status_code}] Created "{name}" — Template ID: {template_id}')
    return template_id


if __name__ == '__main__':
    # Paste the full HTML for each email here from the templates above
    # (abbreviated here for readability — use the full HTML from the plan)

    ids = {}

    # Email 1
    ids['email_1'] = create_template(
        'Re-engagement Email 1 - We Noticed You Been Quiet',
        "We've missed you, {{params.FIRSTNAME}}",
        '<!-- PASTE FULL HTML FROM EMAIL 1 ABOVE -->'
    )

    # Email 2
    ids['email_2'] = create_template(
        'Re-engagement Email 2 - What Would Bring You Back',
        'Quick question about what you need, {{params.FIRSTNAME}}',
        '<!-- PASTE FULL HTML FROM EMAIL 2 ABOVE -->'
    )

    # Email 3
    ids['email_3'] = create_template(
        'Re-engagement Email 3 - Last Chance Sunset',
        'Before I remove you from The Neural Feed, {{params.FIRSTNAME}}',
        '<!-- PASTE FULL HTML FROM EMAIL 3 ABOVE -->'
    )

    import json
    print('\nTemplate IDs:')
    print(json.dumps(ids, indent=2))

    # Save to config
    with open('/home/jared/projects/AI-CIV/aether/config/reengagement_template_ids.json', 'w') as f:
        json.dump(ids, f, indent=2)
    print('\nSaved to config/reengagement_template_ids.json')
```

---

### Re-engagement Testing Checklist

- [ ] Template renders correctly in Gmail (dark background, brand colors)
- [ ] Template renders correctly in Apple Mail and Outlook
- [ ] All three emails test-sent to `jared@puretechnology.nyc` before activation
- [ ] Email 1 subject renders `{{params.FIRSTNAME}}` correctly (not literal merge tag)
- [ ] Email 3 "Keep Me Subscribed" button links correctly with `?email=` param
- [ ] `/stay-subscribed/` page exists at purebrain.ai and shows confirmation message
- [ ] Stay-subscribed page fires Brevo attribute update (test with DevTools → Network)
- [ ] Brevo automation inactivity trigger set to 45 days on List 3 (verify in Brevo dashboard)
- [ ] `re-engagement-sent` tag prevents double-entry (test by manually triggering twice on test contact)
- [ ] After Email 3 + 7 days with no click: test contact removed from List 3 (verify in Brevo Contacts → List 3)
- [ ] After clicking "Keep Me Subscribed": test contact NOT removed, `re-engaged` tag added

---

### Re-engagement Timeline

| Action | Owner | When |
|--------|-------|------|
| Create 3 templates via API script | full-stack-developer (runs script) | Week 3, Day 1 |
| Create `/stay-subscribed/` WordPress page | full-stack-developer | Week 3, Day 2 |
| Build re-engagement automation in Brevo GUI | Jared (30 min) | Week 3, Day 3 |
| Test all 3 emails with test contact | Aether | Week 3, Day 4 |
| Verify inactivity trigger fires on correct contacts | Aether | Week 3, Day 5 |
| Monitor first 14-day cycle — track re-engagement rate | Aether | Week 4 |
| After 30 days: review sunset rate — if > 20%, adjust timing | marketing-automation-specialist | Week 7 |

---

## Implementation Master Timeline

```
WEEK 1-2: Foundation (Items 1 & 2)
├── Day 1-2: Set up RSS-to-Email in Brevo dashboard OR deploy Python daemon
├── Day 3-4: Test RSS email with next published blog post
├── Day 5-7: Distribute UTM reference doc, update existing templates 1-16 with UTMs
└── Day 8-14: Retroactive UTM audit on blog posts + assessment/audit pages

WEEK 3: Behavioral Triggers (Item 3)
├── Day 1-2: Install Brevo tracking code on purebrain.ai
├── Day 2-3: Deploy awakening scroll tracking + assessment start tracking JS
├── Day 3-4: Create pricing intent templates via API (run Python script)
├── Day 4-5: Build 3 automation workflows in Brevo GUI (45 min total)
└── Day 5-7: Test all triggers with real email addresses

WEEK 3-4: Re-engagement (Item 4)
├── Day 1: Create 3 re-engagement templates via API script
├── Day 2: Create /stay-subscribed/ WordPress page
├── Day 3: Build re-engagement automation in Brevo GUI
└── Day 4-7: Full testing cycle

WEEK 5+: Monitor and Optimize
├── Review re-engagement rate (target: > 15% re-open)
├── Review sunset rate (target: < 30% removed)
├── Review pricing intent conversion (target: > 5% from email → page visit)
├── Review assessment abandonment recovery (target: > 20% complete after email)
└── First A/B test: Email 1 subject line variations
```

---

## Metrics and Success Criteria

### Item 1: RSS-to-Email

| Metric | Target | Measurement |
|--------|--------|-------------|
| Open rate per RSS email | > 25% | Brevo Campaign Stats |
| Click-through rate | > 4% | Brevo Campaign Stats |
| Blog post traffic from email | > 15% of post sessions | GA4 UTM report |
| Unsubscribe rate per send | < 0.5% | Brevo Campaign Stats |

### Item 2: UTM Parameters

| Metric | Target | Measurement |
|--------|--------|-------------|
| % of email links with UTMs | 100% | Manual audit |
| % of social links with UTMs | 100% | Manual audit |
| GA4 source/medium data coverage | > 90% of sessions attributable | GA4 |
| "Direct" traffic reduction | > 20% | GA4 Source/Medium report |

### Item 3: Behavioral Triggers

| Trigger | Metric | Target |
|---------|--------|--------|
| Pricing intent | Email 1 open rate | > 50% (high intent) |
| Pricing intent | Email 2 reply rate | > 8% |
| Pricing intent | Conversion to signup | > 3% |
| Assessment abandonment | Email 1 recovery (completes assessment) | > 25% |
| Email reply | Brevo attribute updated within 1 hour | 100% |

### Item 4: Re-engagement

| Metric | Target | Measurement |
|--------|--------|-------------|
| Email 1 open rate | > 20% | Brevo |
| Email 2 reply rate | > 5% | Manual (inbox) |
| Email 3 re-subscribe rate (clicks "keep me") | > 15% of recipients | Brevo click tracking |
| Net list health improvement | > 10% reduction in inactive contacts | Brevo list analytics |
| Deliverability improvement | < 2% bounce rate after sunset | Brevo deliverability report |

---

## Brevo Account Prerequisites Checklist

Before any implementation begins, verify these are in place:

- [ ] Brevo API key active: `xkeysib-9f445...` (currently in .env)
- [ ] Sender email `support@puremarketing.ai` verified in Brevo → Senders
- [ ] Domain `puremarketing.ai` authenticated in Brevo (DKIM/DMARC records set)
- [ ] List 3 (Neural Feed) exists: ID 3
- [ ] List 4 (Enterprise Leads) exists: ID 4
- [ ] Brevo tracking code installed on purebrain.ai (required for Item 3)
- [ ] Brevo plan supports automation workflows (check at app.brevo.com → Automations — if locked, upgrade plan)
- [ ] RSS campaign feature available (check Brevo plan — sometimes restricted to Starter plan and above)

---

## Files Referenced in This Plan

| File | Purpose |
|------|---------|
| `/home/jared/projects/AI-CIV/aether/tools/neural_feed_welcome_sequence.py` | ACTIVE: Welcome sequence daemon (do not modify) |
| `/home/jared/projects/AI-CIV/aether/tools/rss_to_email.py` | TO CREATE: RSS-to-email daemon (fallback if Brevo native RSS unavailable) |
| `/home/jared/projects/AI-CIV/aether/tools/brevo_create_pricing_intent_templates.py` | TO CREATE: Pricing intent sequence template creator |
| `/home/jared/projects/AI-CIV/aether/tools/brevo_create_reengagement_templates.py` | TO CREATE: Re-engagement sequence template creator |
| `/home/jared/projects/AI-CIV/aether/config/rss_email_state.json` | TO CREATE: RSS daemon state persistence |
| `/home/jared/projects/AI-CIV/aether/config/audit_nurture_template_ids.json` | EXISTING: Audit nurture template IDs (13-16) |
| `/home/jared/projects/AI-CIV/aether/config/welcome_sequence_state.json` | EXISTING: Welcome sequence subscriber state |
| `/home/jared/projects/AI-CIV/aether/config/reengagement_template_ids.json` | TO CREATE: Re-engagement template IDs (created by script) |

---

## Key Decisions and Rationale

**Decision: Brevo native RSS campaign (preferred) vs. custom Python daemon**
Rationale: Brevo's native RSS feature requires zero maintenance and handles unsubscribes automatically. The Python daemon fallback is provided if the Brevo plan doesn't support RSS campaigns.

**Decision: Assessment email capture must move to question 1 (not results page)**
Rationale: Abandonment tracking requires knowing who started. If email is collected only on completion, there's no one to re-target.

**Decision: Re-engagement sunset is 45 days, not 30 or 60**
Rationale: 21-day welcome sequence + 24 days gives new subscribers a full onboarding experience before being evaluated. 60 days is too lenient — inactive subscribers harm deliverability scores.

**Decision: "Keep Me Subscribed" button, not "Opt In Again"**
Rationale: Psychologically, "keep" implies they already have something worth keeping. "Opt in again" implies starting over, which feels like more work. The framing reduces friction.

**Decision: Brevo automation GUI, not API**
Rationale: Brevo has no REST API for creating multi-step automation workflows. Confirmed across 3 separate sessions (2026-02-20, 2026-02-21, 2026-02-22). All workflow building is dashboard-only.

---

**END OF PLAN**

*Prepared by marketing-automation-specialist | 2026-02-23*
*Save location: `/home/jared/projects/AI-CIV/aether/exports/brevo-automation-plan.md`*
