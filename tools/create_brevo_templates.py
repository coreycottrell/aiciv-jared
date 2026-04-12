#!/usr/bin/env python3
"""
Create 5 Brevo email templates via the Brevo API.
Templates: 2x Pricing Intent + 3x Re-engagement
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load env
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')

if not BREVO_API_KEY:
    raise ValueError("BREVO_API_KEY not found in .env")

HEADERS = {
    'api-key': BREVO_API_KEY,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

SENDER = {
    'name': 'Jared Sanborn | PureBrain',
    'email': 'purebrain@puremarketing.ai'
}

REPLY_TO = 'jared@puretechnology.nyc'

BASE_URL = 'https://api.brevo.com/v3/smtp/templates'


def create_template(template_name, subject, html_content, tag):
    """POST a new template to Brevo and return its ID."""
    payload = {
        'templateName': template_name,
        'subject': subject,
        'sender': SENDER,
        'htmlContent': html_content,
        'replyTo': REPLY_TO,
        'isActive': True,
        'tag': tag
    }
    r = requests.post(BASE_URL, headers=HEADERS, json=payload)
    data = r.json()
    if r.status_code not in (200, 201):
        print(f'  ERROR [{r.status_code}] {template_name}: {data}')
        return None
    template_id = data.get('id')
    print(f'  CREATED [{r.status_code}] {template_name} -> ID: {template_id}')
    return template_id


# ─────────────────────────────────────────────
# TEMPLATE 1: Pricing Intent - Email 1 - Awakening Reframe
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# TEMPLATE 2: Pricing Intent - Email 2 - Objection Handler
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# TEMPLATE 3: Re-engagement Email 1 - We've Missed You
# ─────────────────────────────────────────────
email3_html = """<!DOCTYPE html>
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
</html>"""

# ─────────────────────────────────────────────
# TEMPLATE 4: Re-engagement Email 2 - What Would Bring You Back
# ─────────────────────────────────────────────
email4_html = """<!DOCTYPE html>
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
</html>"""

# ─────────────────────────────────────────────
# TEMPLATE 5: Re-engagement Email 3 - Last Chance Sunset
# ─────────────────────────────────────────────
email5_html = """<!DOCTYPE html>
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
        <a href="https://purebrain.ai/stay-subscribed/?email={{params.EMAIL}}&amp;utm_source=newsletter&amp;utm_medium=email&amp;utm_campaign=re-engagement&amp;utm_content=email-3-stay" class="cta-button">
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
</html>"""


def verify_templates(template_ids):
    """Verify all templates exist and are active via GET /v3/smtp/templates."""
    print("\n--- Verifying Templates ---")
    r = requests.get(BASE_URL, headers=HEADERS, params={'limit': 50, 'offset': 0})
    if r.status_code != 200:
        print(f"  ERROR fetching templates: {r.status_code} {r.json()}")
        return
    templates = r.json().get('templates', [])
    found_ids = {t['id']: t for t in templates}
    for name, tid in template_ids.items():
        if tid is None:
            print(f"  SKIP (creation failed): {name}")
            continue
        if tid in found_ids:
            t = found_ids[tid]
            status = "ACTIVE" if t.get('isActive') else "INACTIVE"
            print(f"  VERIFIED [{status}] ID={tid}: {t.get('name', 'Unknown')}")
        else:
            print(f"  NOT FOUND: {name} (ID={tid})")


def main():
    print("=== Creating 5 Brevo Email Templates ===\n")

    template_ids = {}

    print("--- Pricing Intent Sequence ---")
    template_ids['pricing_intent_email_1'] = create_template(
        'Pricing Intent - Email 1 - Awakening Reframe',
        'You found the awakening section, {{params.FIRSTNAME}}',
        email1_html,
        'pricing-intent'
    )
    template_ids['pricing_intent_email_2'] = create_template(
        'Pricing Intent - Email 2 - Objection Handler',
        'What would make this obvious for you?',
        email2_html,
        'pricing-intent'
    )

    print("\n--- Re-engagement Sequence ---")
    template_ids['reengagement_email_1'] = create_template(
        'Re-engagement - Email 1 - We Noticed You\'ve Been Quiet',
        'We\'ve missed you, {{params.FIRSTNAME}}',
        email3_html,
        're-engagement'
    )
    template_ids['reengagement_email_2'] = create_template(
        'Re-engagement - Email 2 - What Would Bring You Back',
        'Quick question about what you need, {{params.FIRSTNAME}}',
        email4_html,
        're-engagement'
    )
    template_ids['reengagement_email_3'] = create_template(
        'Re-engagement - Email 3 - Last Chance Sunset',
        'Before I remove you from The Neural Feed, {{params.FIRSTNAME}}',
        email5_html,
        're-engagement'
    )

    # Verify
    verify_templates(template_ids)

    # Save to config
    output_path = '/home/jared/projects/AI-CIV/aether/config/brevo_automation_template_ids.json'
    with open(output_path, 'w') as f:
        json.dump(template_ids, f, indent=2)
    print(f"\n=== Template IDs saved to {output_path} ===")
    print(json.dumps(template_ids, indent=2))

    return template_ids


if __name__ == '__main__':
    main()
