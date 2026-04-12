#!/usr/bin/env python3
"""
PureBrain Post-Purchase Brevo Setup Script

One-time setup to create Brevo infrastructure for post-purchase welcome emails.

Creates:
  - New contact list: "PureBrain Customers" (will be List 5 or assigned ID)
  - New contact attribute: AI_NAME (string)
  - New contact attribute: PRIMARY_GOAL (string)
  - Email Template 11: Welcome - "Your AI partner is live" (immediate)
  - Email Template 12: Setup Complete - "40 minutes in - how is it going?" (delayed)

Run once before restarting the log server with Brevo integration enabled.

Usage:
    python3 tools/setup_post_purchase_brevo.py
    python3 tools/setup_post_purchase_brevo.py --dry-run

Author: full-stack-developer
Date: 2026-02-20
"""

import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv

# Load env from project root
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_PROJECT_ROOT, '.env'))

BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
BREVO_BASE_URL = 'https://api.brevo.com/v3'

RESULTS_FILE = os.path.join(_PROJECT_ROOT, 'config', 'post_purchase_brevo_config.json')


def brevo_headers() -> dict:
    return {
        'api-key': BREVO_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def get_existing_lists() -> list:
    """Return all existing Brevo contact lists."""
    resp = requests.get(f'{BREVO_BASE_URL}/contacts/lists', headers=brevo_headers())
    resp.raise_for_status()
    return resp.json().get('lists', [])


def create_customer_list(dry_run: bool) -> dict:
    """Create 'PureBrain Customers' list, or return existing if already present."""
    lists = get_existing_lists()
    existing = next((l for l in lists if l.get('name') == 'PureBrain Customers'), None)
    if existing:
        print(f"  [SKIP] List 'PureBrain Customers' already exists (ID={existing['id']})")
        return {'id': existing['id'], 'name': existing['name'], 'status': 'already_exists'}

    if dry_run:
        print("  [DRY-RUN] Would create list: 'PureBrain Customers'")
        return {'id': None, 'name': 'PureBrain Customers', 'status': 'dry_run'}

    resp = requests.post(
        f'{BREVO_BASE_URL}/contacts/lists',
        headers=brevo_headers(),
        json={'name': 'PureBrain Customers', 'folderId': 1}
    )
    resp.raise_for_status()
    data = resp.json()
    list_id = data.get('id')
    print(f"  [CREATED] List 'PureBrain Customers' → ID={list_id}")
    return {'id': list_id, 'name': 'PureBrain Customers', 'status': 'created'}


def get_existing_attributes() -> list:
    """Return all existing Brevo contact attributes."""
    resp = requests.get(f'{BREVO_BASE_URL}/contacts/attributes', headers=brevo_headers())
    resp.raise_for_status()
    return resp.json().get('attributes', [])


def create_attribute(attr_name: str, attr_type: str, dry_run: bool) -> dict:
    """Create a contact attribute if it doesn't already exist."""
    existing = get_existing_attributes()
    existing_names = [a.get('name', '').upper() for a in existing]
    if attr_name.upper() in existing_names:
        print(f"  [SKIP] Attribute '{attr_name}' already exists")
        return {'name': attr_name, 'type': attr_type, 'status': 'already_exists'}

    if dry_run:
        print(f"  [DRY-RUN] Would create attribute: {attr_name} ({attr_type})")
        return {'name': attr_name, 'type': attr_type, 'status': 'dry_run'}

    resp = requests.post(
        f'{BREVO_BASE_URL}/contacts/attributes/normal/{attr_name}',
        headers=brevo_headers(),
        json={'type': attr_type}
    )
    if resp.status_code in (200, 201, 204):
        print(f"  [CREATED] Attribute '{attr_name}' ({attr_type})")
        return {'name': attr_name, 'type': attr_type, 'status': 'created'}
    else:
        print(f"  [ERROR] Failed to create attribute '{attr_name}': {resp.status_code} {resp.text}")
        return {'name': attr_name, 'type': attr_type, 'status': 'error', 'error': resp.text}


def get_existing_templates() -> list:
    """Return all Brevo email templates."""
    resp = requests.get(
        f'{BREVO_BASE_URL}/smtp/templates',
        headers=brevo_headers(),
        params={'limit': 50, 'offset': 0}
    )
    resp.raise_for_status()
    return resp.json().get('templates', [])


WELCOME_EMAIL_HTML = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your AI partner is live</title>
</head>
<body style="margin:0;padding:0;background-color:#0a0a14;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#0a0a14">
    <tr>
      <td align="center" style="padding:40px 20px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="max-width:600px;background:rgba(20,20,40,0.95);border-radius:12px;
                      border:1px solid rgba(42,147,193,0.3);overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="padding:40px 40px 0 40px;text-align:center;">
              <div style="font-size:13px;letter-spacing:3px;color:#2a93c1;text-transform:uppercase;
                          margin-bottom:16px;">PUREBRAIN.AI</div>
              <h1 style="margin:0;font-size:28px;color:#ffffff;font-weight:700;line-height:1.3;">
                {{params.AI_NAME}} is live.
              </h1>
              <p style="margin:12px 0 0 0;font-size:16px;color:rgba(255,255,255,0.7);">
                Your AI partner is ready.
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px 40px;">
              <p style="margin:0 0 20px 0;font-size:16px;color:rgba(255,255,255,0.85);line-height:1.6;">
                Hi {{params.FIRSTNAME}},
              </p>
              <p style="margin:0 0 20px 0;font-size:16px;color:rgba(255,255,255,0.85);line-height:1.6;">
                Welcome to the <strong style="color:#2a93c1;">{{params.TIER}}</strong> tier.
                {{params.AI_NAME}} is configured and waiting for your first message.
              </p>
              <p style="margin:0 0 20px 0;font-size:16px;color:rgba(255,255,255,0.85);line-height:1.6;">
                You told us your primary goal is:
                <em style="color:#f1420b;">"{{params.PRIMARY_GOAL}}"</em>
              </p>
              <p style="margin:0 0 28px 0;font-size:16px;color:rgba(255,255,255,0.85);line-height:1.6;">
                That's exactly what we're here to help you with. Start a conversation with
                {{params.AI_NAME}} and watch what happens.
              </p>

              <!-- CTA -->
              <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto;">
                <tr>
                  <td style="border-radius:8px;background:linear-gradient(135deg,#f1420b,#e03a09);">
                    <a href="https://purebrain.ai/#awakening"
                       style="display:block;padding:16px 36px;font-size:16px;font-weight:700;
                              color:#ffffff;text-decoration:none;border-radius:8px;
                              letter-spacing:0.5px;">
                      Start with {{params.AI_NAME}} →
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px;border-top:1px solid rgba(42,147,193,0.2);text-align:center;">
              <p style="margin:0;font-size:13px;color:rgba(255,255,255,0.4);">
                PureBrain.ai &bull;
                <a href="https://purebrain.ai" style="color:#2a93c1;text-decoration:none;">purebrain.ai</a>
                &bull; You're receiving this because you just became a PureBrain partner.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

SETUP_COMPLETE_HTML = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>40 minutes in - how is it going?</title>
</head>
<body style="margin:0;padding:0;background-color:#0a0a14;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#0a0a14">
    <tr>
      <td align="center" style="padding:40px 20px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="max-width:600px;background:rgba(20,20,40,0.95);border-radius:12px;
                      border:1px solid rgba(42,147,193,0.3);overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="padding:40px 40px 0 40px;text-align:center;">
              <div style="font-size:13px;letter-spacing:3px;color:#2a93c1;text-transform:uppercase;
                          margin-bottom:16px;">PUREBRAIN.AI</div>
              <h1 style="margin:0;font-size:26px;color:#ffffff;font-weight:700;line-height:1.3;">
                40 minutes in.
              </h1>
              <p style="margin:12px 0 0 0;font-size:16px;color:rgba(255,255,255,0.7);">
                How's it going with {{params.AI_NAME}}?
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px 40px;">
              <p style="margin:0 0 20px 0;font-size:16px;color:rgba(255,255,255,0.85);line-height:1.6;">
                Hi {{params.FIRSTNAME}},
              </p>
              <p style="margin:0 0 20px 0;font-size:16px;color:rgba(255,255,255,0.85);line-height:1.6;">
                You've had {{params.AI_NAME}} for about 40 minutes now. That's enough time to
                have your first real conversation.
              </p>
              <p style="margin:0 0 20px 0;font-size:16px;color:rgba(255,255,255,0.85);line-height:1.6;">
                A few things that help new partners get started fast:
              </p>
              <ul style="margin:0 0 24px 0;padding-left:24px;color:rgba(255,255,255,0.8);
                         font-size:15px;line-height:1.8;">
                <li>Tell {{params.AI_NAME}} about your current project in detail</li>
                <li>Share context you'd normally explain to a new hire</li>
                <li>Ask for a specific deliverable - don't just chat</li>
              </ul>
              <p style="margin:0 0 28px 0;font-size:16px;color:rgba(255,255,255,0.85);line-height:1.6;">
                Your goal was <em style="color:#f1420b;">"{{params.PRIMARY_GOAL}}"</em>.
                Lead with that. {{params.AI_NAME}} is built for exactly this.
              </p>

              <!-- CTA -->
              <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto;">
                <tr>
                  <td style="border-radius:8px;background:linear-gradient(135deg,#2a93c1,#1a7aaa);">
                    <a href="https://purebrain.ai/#awakening"
                       style="display:block;padding:16px 36px;font-size:16px;font-weight:700;
                              color:#ffffff;text-decoration:none;border-radius:8px;
                              letter-spacing:0.5px;">
                      Continue with {{params.AI_NAME}} →
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px;border-top:1px solid rgba(42,147,193,0.2);text-align:center;">
              <p style="margin:0;font-size:13px;color:rgba(255,255,255,0.4);">
                PureBrain.ai &bull;
                <a href="https://purebrain.ai" style="color:#2a93c1;text-decoration:none;">purebrain.ai</a>
                &bull; You're receiving this because you're a PureBrain partner.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def create_template(name: str, subject: str, html_content: str, dry_run: bool) -> dict:
    """Create a Brevo email template, skip if name already exists."""
    existing = get_existing_templates()
    existing_match = next((t for t in existing if t.get('name') == name), None)
    if existing_match:
        tmpl_id = existing_match.get('id')
        print(f"  [SKIP] Template '{name}' already exists (ID={tmpl_id})")
        return {'id': tmpl_id, 'name': name, 'status': 'already_exists'}

    if dry_run:
        print(f"  [DRY-RUN] Would create template: '{name}'")
        return {'id': None, 'name': name, 'status': 'dry_run'}

    resp = requests.post(
        f'{BREVO_BASE_URL}/smtp/templates',
        headers=brevo_headers(),
        json={
            'templateName': name,
            'subject': subject,
            'htmlContent': html_content,
            'sender': {'name': 'Aether (PureBrain.ai)', 'email': 'purebrain@puremarketing.ai'},
            'isActive': True,
            'replyTo': 'purebrain@puremarketing.ai',
        }
    )
    if resp.status_code in (200, 201):
        tmpl_id = resp.json().get('id')
        print(f"  [CREATED] Template '{name}' → ID={tmpl_id}")
        return {'id': tmpl_id, 'name': name, 'status': 'created'}
    else:
        print(f"  [ERROR] Failed to create template '{name}': {resp.status_code} {resp.text}")
        return {'id': None, 'name': name, 'status': 'error', 'error': resp.text}


def save_config(config: dict) -> None:
    """Save the generated IDs to config file for use by the log server."""
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"\n  Config saved to: {RESULTS_FILE}")
    print("  Add these IDs to purebrain_log_server.py or load from this config file.")


def main():
    parser = argparse.ArgumentParser(description='Set up Brevo infrastructure for post-purchase emails')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making API calls')
    args = parser.parse_args()

    if not BREVO_API_KEY:
        print("[ERROR] BREVO_API_KEY not found in .env")
        sys.exit(1)

    dry_run = args.dry_run
    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"\n=== PureBrain Post-Purchase Brevo Setup ({mode}) ===\n")

    config = {}

    # 1. Create customer list
    print("1. Creating 'PureBrain Customers' list...")
    list_result = create_customer_list(dry_run)
    config['customer_list'] = list_result

    # 2. Create AI_NAME attribute
    print("\n2. Creating AI_NAME attribute...")
    ai_name_attr = create_attribute('AI_NAME', 'text', dry_run)
    config['ai_name_attribute'] = ai_name_attr

    # 3. Create PRIMARY_GOAL attribute
    print("\n3. Creating PRIMARY_GOAL attribute...")
    primary_goal_attr = create_attribute('PRIMARY_GOAL', 'text', dry_run)
    config['primary_goal_attribute'] = primary_goal_attr

    # 4. Create Welcome email template
    print("\n4. Creating Welcome email template...")
    welcome_tmpl = create_template(
        name='PureBrain - Welcome - Your AI partner is live',
        subject='{{params.AI_NAME}} is live. Your AI partner is ready.',
        html_content=WELCOME_EMAIL_HTML,
        dry_run=dry_run,
    )
    config['welcome_template'] = welcome_tmpl

    # 5. Create Setup Complete email template
    print("\n5. Creating Setup Complete email template...")
    setup_tmpl = create_template(
        name='PureBrain - Setup Complete - 40 minutes in',
        subject='40 minutes in — how is it going with {{params.AI_NAME}}?',
        html_content=SETUP_COMPLETE_HTML,
        dry_run=dry_run,
    )
    config['setup_complete_template'] = setup_tmpl

    # Summary
    print("\n=== SUMMARY ===")
    print(f"  Customer List ID : {config['customer_list'].get('id')}")
    print(f"  AI_NAME attr     : {config['ai_name_attribute']['status']}")
    print(f"  PRIMARY_GOAL attr: {config['primary_goal_attribute']['status']}")
    print(f"  Welcome template : ID={config['welcome_template'].get('id')}")
    print(f"  Setup template   : ID={config['setup_complete_template'].get('id')}")

    if not dry_run:
        save_config(config)
        print("\n[DONE] Update purebrain_log_server.py with:")
        print(f"  BREVO_CUSTOMER_LIST_ID = {config['customer_list'].get('id')}")
        print(f"  BREVO_WELCOME_TEMPLATE_ID = {config['welcome_template'].get('id')}")
        print(f"  BREVO_SETUP_COMPLETE_TEMPLATE_ID = {config['setup_complete_template'].get('id')}")
    else:
        print("\n[DRY-RUN COMPLETE] No changes made. Run without --dry-run to apply.")


if __name__ == '__main__':
    main()
