#!/usr/bin/env python3
"""
Add P.S. reply-invitation sections to Brevo Neural Feed welcome sequence templates 2, 4, and 5.

The HTML structure of these templates is div-based (not table-based):
  <div class="content">
    ...email body...
    <div class="signature">...</div>
  </div>
  <div class="footer">...</div>

The P.S. block from the brief uses <tr>/<td> tags but we'll convert them to
the div-based structure that matches the existing templates.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
api_key = os.getenv('BREVO_API_KEY')

HEADERS = {
    'api-key': api_key,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

BASE_URL = 'https://api.brevo.com/v3/smtp/templates'

# P.S. HTML blocks - adapted to div-based structure matching the existing templates
# These are inserted inside <div class="content"> just before the closing </div>
# (after the signature block)

PS_BLOCKS = {
    2: """
    <div style="padding: 32px 0 0 0; margin-top: 8px; border-top: 1px solid #1a2235; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #b8c5d6;">
      <p style="margin: 0 0 12px 0; font-style: italic; color: #a0adc0;">P.S.</p>
      <p style="margin: 0; color: #b8c5d6;">What is your version of that moment &mdash; when you stopped using AI as a tool and started using it differently? Reply and tell me. I read every response.</p>
    </div>
""",
    4: """
    <div style="padding: 32px 0 0 0; margin-top: 8px; border-top: 1px solid #1a2235; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #b8c5d6;">
      <p style="margin: 0 0 12px 0; font-style: italic; color: #a0adc0;">P.S.</p>
      <p style="margin: 0; color: #b8c5d6;">What does Aether write about that&rsquo;s useful to you? Reply and tell me what topics or questions would make The Neural Feed something you look forward to. I&rsquo;m listening.</p>
    </div>
""",
    5: """
    <div style="padding: 32px 0 0 0; margin-top: 8px; border-top: 1px solid #1a2235; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #b8c5d6;">
      <p style="margin: 0 0 12px 0; font-style: italic; color: #a0adc0;">P.S.</p>
      <p style="margin: 0; color: #b8c5d6;">How much of your AI conversations is setup work versus actual thinking? Reply and tell me your ratio. Jared will share it with me, and we&rsquo;ll keep learning how to reduce that tax.</p>
    </div>
"""
}

# Unique verification marker for each template's P.S.
PS_VERIFICATION_SNIPPETS = {
    2: 'stopped using AI as a tool and started using it differently',
    4: "what topics or questions would make The Neural Feed",
    5: 'setup work versus actual thinking'
}


def get_template(template_id):
    """Fetch current template data from Brevo."""
    resp = requests.get(f'{BASE_URL}/{template_id}', headers=HEADERS, timeout=30)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"  ERROR fetching template {template_id}: {resp.status_code} {resp.text[:200]}")
        return None


def update_template_api(template_id, payload):
    """Update a Brevo template via PUT. Returns (status_code, response_text)."""
    resp = requests.put(f'{BASE_URL}/{template_id}', headers=HEADERS, json=payload, timeout=30)
    return resp.status_code, resp.text


def inject_ps_block(html_content, ps_html, template_id):
    """
    Inject P.S. block into the div-based email HTML.

    The template structure is:
      <div class="content">
        ...content...
        <div class="signature">...</div>
      </div>          <- we want to insert PS just before this closing tag
      <div class="footer">

    Strategy: find the closing </div> that ends the content div,
    which comes just before <div class="footer">
    """

    # Strategy 1: Insert before <div class="footer">
    footer_marker = '<div class="footer">'
    footer_pos = html_content.find(footer_marker)

    if footer_pos != -1:
        # Walk backward to find the </div> that closes the content div
        # There should be whitespace + </div> + whitespace before <div class="footer">
        before_footer = html_content[:footer_pos]

        # Find the last </div> before the footer
        last_div_close = before_footer.rfind('</div>')

        if last_div_close != -1:
            # Insert PS after the last </div> (which closes content) and before footer
            insert_pos = last_div_close + len('</div>')
            new_html = html_content[:insert_pos] + '\n' + ps_html + html_content[insert_pos:]
            print(f"  Inserted P.S. before footer at position {insert_pos}")
            return new_html

    # Strategy 2: Insert before </body>
    body_close = html_content.rfind('</body>')
    if body_close != -1:
        new_html = html_content[:body_close] + ps_html + '\n' + html_content[body_close:]
        print(f"  Inserted P.S. before </body> (fallback)")
        return new_html

    # Strategy 3: Append at end
    print(f"  WARNING: Could not find insertion point. Appending P.S. at end.")
    return html_content + '\n' + ps_html


def verify_template_has_ps(template_id):
    """Re-fetch template and verify P.S. snippet is present."""
    data = get_template(template_id)
    if not data:
        return False, "Could not re-fetch template"

    html = data.get('htmlContent', '')
    snippet = PS_VERIFICATION_SNIPPETS[template_id]

    if snippet in html:
        return True, f"Found verification snippet: '{snippet[:50]}...'"
    else:
        return False, f"Snippet NOT found: '{snippet[:50]}...'"


def check_reply_to(data):
    """Check and return reply-to, defaulting to purebrain@puremarketing.ai if not set."""
    reply_to = data.get('replyTo', '')
    if not reply_to:
        return 'purebrain@puremarketing.ai', False
    return reply_to, True


def main():
    results = {}

    print("=" * 70)
    print("Brevo P.S. Reply-Invitation Section Deployment")
    print("Targets: Templates 2, 4, 5 (Neural Feed Welcome Sequence)")
    print("=" * 70)

    for template_id in [2, 4, 5]:
        print(f"\n{'='*70}")
        print(f"TEMPLATE {template_id}")
        print(f"{'='*70}")

        # Step 1: Fetch current template
        print(f"Step 1: Fetching template {template_id}...")
        data = get_template(template_id)
        if not data:
            results[template_id] = {'status': 'FETCH_ERROR'}
            continue

        print(f"  Name:     {data.get('name', 'N/A')}")
        print(f"  Subject:  {data.get('subject', 'N/A')}")
        sender = data.get('sender', {})
        print(f"  Sender:   {sender.get('name', 'N/A')} <{sender.get('email', 'N/A')}>")

        reply_to, was_set = check_reply_to(data)
        if was_set:
            print(f"  Reply-to: {reply_to} (already configured)")
        else:
            print(f"  Reply-to: {reply_to} (DEFAULTING - was empty)")

        html_content = data.get('htmlContent', '')
        print(f"  HTML length: {len(html_content)} chars")

        # Check if P.S. already exists (idempotency check)
        snippet = PS_VERIFICATION_SNIPPETS[template_id]
        if snippet in html_content:
            print(f"\n  ALREADY DEPLOYED: P.S. section already exists in template {template_id}")
            print(f"  Snippet found: '{snippet[:60]}'")
            results[template_id] = {
                'status': 'ALREADY_PRESENT',
                'reply_to': reply_to,
                'verified': True
            }
            continue

        # Step 2: Inject P.S. block
        print(f"\nStep 2: Injecting P.S. block for template {template_id}...")
        ps_html = PS_BLOCKS[template_id]
        new_html = inject_ps_block(html_content, ps_html, template_id)
        size_delta = len(new_html) - len(html_content)
        print(f"  HTML size: {len(html_content)} -> {len(new_html)} (+{size_delta} chars)")

        # Step 3: Build update payload - preserve all existing fields
        payload = {
            'name': data.get('name', f'Neural Feed Email {template_id}'),
            'subject': data.get('subject', ''),
            'htmlContent': new_html,
            'sender': sender,
            'replyTo': reply_to,
            'isActive': True,
            'tag': data.get('tag', 'welcome-sequence'),
        }

        # Step 4: Update via API
        print(f"\nStep 3: Updating template {template_id} via Brevo API...")
        status_code, response_text = update_template_api(template_id, payload)

        response_preview = response_text[:100] if response_text else '(empty body)'
        print(f"  HTTP {status_code}: {response_preview}")

        if status_code in [200, 204]:
            print(f"  SUCCESS: Template {template_id} updated")
            results[template_id] = {
                'status': 'UPDATED',
                'http_code': status_code,
                'reply_to': reply_to
            }
        else:
            print(f"  ERROR: Template {template_id} update FAILED")
            results[template_id] = {
                'status': 'UPDATE_ERROR',
                'http_code': status_code,
                'error': response_text[:300],
                'reply_to': reply_to
            }
            continue

        # Step 5: Verify
        print(f"\nStep 4: Verifying P.S. is present in template {template_id}...")
        verified, verify_msg = verify_template_has_ps(template_id)
        print(f"  Verification: {'PASS' if verified else 'FAIL'} - {verify_msg}")
        results[template_id]['verified'] = verified
        results[template_id]['verify_msg'] = verify_msg

    # Final summary
    print(f"\n{'='*70}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*70}")

    all_good = True
    for tid in [2, 4, 5]:
        result = results.get(tid, {})
        status = result.get('status', 'UNKNOWN')
        verified = result.get('verified', 'N/A')
        reply_to = result.get('reply_to', 'N/A')

        status_icon = "OK" if status in ['UPDATED', 'ALREADY_PRESENT'] else "FAIL"
        verify_icon = "OK" if verified is True else ("SKIP" if verified == 'N/A' else "FAIL")

        print(f"Template {tid}: [{status_icon}] {status} | Verify: [{verify_icon}] | Reply-to: {reply_to}")

        if status not in ['UPDATED', 'ALREADY_PRESENT']:
            all_good = False
        if verified is False:
            all_good = False

    print()

    # Also do a final reply-to check across templates 2, 4, 5
    print("Reply-to configuration verification:")
    for tid in [2, 4, 5]:
        data = get_template(tid)
        if data:
            rt = data.get('replyTo', 'NOT SET')
            print(f"  Template {tid}: {rt}")

    return all_good, results


if __name__ == '__main__':
    success, results = main()

    # Save results to file
    output_path = '/home/jared/projects/AI-CIV/aether/exports/ps-deployment-results.json'
    with open(output_path, 'w') as f:
        json.dump({
            'success': success,
            'templates_updated': [2, 4, 5],
            'results': {str(k): v for k, v in results.items()}
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print()

    if success:
        print("ALL TEMPLATES DEPLOYED SUCCESSFULLY.")
    else:
        print("SOME TEMPLATES HAD ERRORS. Review output above.")
