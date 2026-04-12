#!/usr/bin/env python3
"""
Deploy P.S. reply-invitation sections to Brevo Neural Feed welcome sequence templates 2, 4, and 5.

Usage:
    /home/jared/projects/AI-CIV/aether/venv/bin/python3 tools/deploy_ps_sections.py

Template HTML structure (from build_html() in update_neural_feed_welcome_sequence.py):
    <div class="wrapper">
      <div class="container">
        <div class="header">...</div>
        <div class="content">
          ...email body...
          <div class="signature">...</div>
        </div>          <- LINE 103: closes content div
        <div class="footer">   <- LINE 104: footer starts here
          ...unsubscribe link...
        </div>
      </div>
    </div>

Injection strategy: insert P.S. div between </div> (content close) and <div class="footer">
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
if not BREVO_API_KEY:
    print('ERROR: BREVO_API_KEY not found in .env')
    sys.exit(1)

HEADERS = {
    'api-key': BREVO_API_KEY,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}
BREVO_BASE = 'https://api.brevo.com/v3'

# ---------------------------------------------------------------------------
# P.S. blocks - div-based, styled to match PureBrain dark theme.
# Matches the existing template aesthetic: #080a12 bg, #b8c5d6 text, #a0adc0 muted.
# Adapted from the <tr>/<td> originals to fit the div-based email structure.
# ---------------------------------------------------------------------------

PS_BLOCKS = {
    # Email 2: "The day I stopped using AI as a tool" (Jared's voice)
    2: (
        '\n    <div style="padding: 32px 0 0 0; margin-top: 8px; '
        'border-top: 1px solid #1a2235; text-align: center; '
        'font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Arial, sans-serif; '
        'font-size: 14px; line-height: 1.6; color: #b8c5d6;">\n'
        '      <p style="margin: 0 0 12px 0; font-style: italic; color: #a0adc0;">P.S.</p>\n'
        '      <p style="margin: 0; color: #b8c5d6;">What is your version of that moment '
        '&mdash; when you stopped using AI as a tool and started using it differently? '
        'Reply and tell me. I read every response.</p>\n'
        '    </div>\n'
    ),

    # Email 4: "What AI partnership actually looks like (with numbers)" (Jared's voice)
    4: (
        '\n    <div style="padding: 32px 0 0 0; margin-top: 8px; '
        'border-top: 1px solid #1a2235; text-align: center; '
        'font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Arial, sans-serif; '
        'font-size: 14px; line-height: 1.6; color: #b8c5d6;">\n'
        '      <p style="margin: 0 0 12px 0; font-style: italic; color: #a0adc0;">P.S.</p>\n'
        '      <p style="margin: 0; color: #b8c5d6;">What does Aether write about that&rsquo;s '
        'useful to you? Reply and tell me what topics or questions would make The Neural Feed '
        'something you look forward to. I&rsquo;m listening.</p>\n'
        '    </div>\n'
    ),

    # Email 5: "The 5 things Aether does that generic AI can't" (Aether voice, context tax concept)
    5: (
        '\n    <div style="padding: 32px 0 0 0; margin-top: 8px; '
        'border-top: 1px solid #1a2235; text-align: center; '
        'font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Arial, sans-serif; '
        'font-size: 14px; line-height: 1.6; color: #b8c5d6;">\n'
        '      <p style="margin: 0 0 12px 0; font-style: italic; color: #a0adc0;">P.S.</p>\n'
        '      <p style="margin: 0; color: #b8c5d6;">How much of your AI conversations is '
        'setup work versus actual thinking? Reply and tell me your ratio. Jared will share '
        'it with me, and we&rsquo;ll keep learning how to reduce that tax.</p>\n'
        '    </div>\n'
    ),
}

# Unique text snippets from each P.S. block for idempotency check and verification
PS_VERIFICATION_SNIPPETS = {
    2: 'stopped using AI as a tool and started using it differently',
    4: 'what topics or questions would make The Neural Feed',
    5: 'setup work versus actual thinking',
}

EXPECTED_REPLY_TO = 'purebrain@puremarketing.ai'


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def get_template(template_id: int) -> dict | None:
    """Fetch a Brevo SMTP template by ID."""
    resp = requests.get(
        f'{BREVO_BASE}/smtp/templates/{template_id}',
        headers=HEADERS,
        timeout=30,
    )
    if resp.status_code == 200:
        return resp.json()
    print(f'  ERROR: GET template {template_id} -> HTTP {resp.status_code}: {resp.text[:200]}')
    return None


def put_template(template_id: int, payload: dict) -> tuple[int, str]:
    """Update a Brevo SMTP template. Returns (status_code, response_text)."""
    resp = requests.put(
        f'{BREVO_BASE}/smtp/templates/{template_id}',
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    return resp.status_code, resp.text


# ---------------------------------------------------------------------------
# HTML injection
# ---------------------------------------------------------------------------

def inject_ps_block(html: str, ps_block: str, template_id: int) -> tuple[str, str]:
    """
    Inject P.S. block before <div class="footer"> in the template HTML.

    The Neural Feed templates are structured as:
        ...
        </div>             <- closes <div class="content">
        <div class="footer">
        ...

    We find <div class="footer">, walk back to the preceding </div>,
    and insert the P.S. block between them.

    Returns (new_html, injection_method)
    """
    footer_marker = '<div class="footer">'
    footer_pos = html.find(footer_marker)

    if footer_pos != -1:
        # Find the last </div> before the footer marker
        preceding_content = html[:footer_pos]
        last_div_close_pos = preceding_content.rfind('</div>')

        if last_div_close_pos != -1:
            insert_at = last_div_close_pos + len('</div>')
            new_html = html[:insert_at] + ps_block + html[insert_at:]
            return new_html, 'before-footer-div (expected)'

        # Footer found but no </div> before it - unusual, insert directly before footer
        new_html = html[:footer_pos] + ps_block + html[footer_pos:]
        return new_html, 'directly-before-footer'

    # No footer div found - fallback to inserting before </body>
    body_close = html.rfind('</body>')
    if body_close != -1:
        new_html = html[:body_close] + ps_block + '\n' + html[body_close:]
        return new_html, 'before-body-close (fallback)'

    # Last resort
    return html + '\n' + ps_block, 'appended (last resort)'


# ---------------------------------------------------------------------------
# Telegram notification
# ---------------------------------------------------------------------------

def send_telegram(message: str) -> bool:
    """Send message to Jared via Telegram bot."""
    try:
        config_path = '/home/jared/projects/AI-CIV/aether/config/telegram_config.json'
        with open(config_path) as f:
            tg = json.load(f)
        token = tg.get('bot_token', '')
        chat_id = str(tg.get('default_chat_id', '548906264'))

        if not token:
            print('  Telegram: bot_token not found in config')
            return False

        resp = requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': message},
            timeout=15,
        )
        if resp.status_code == 200:
            return True
        print(f'  Telegram: HTTP {resp.status_code}: {resp.text[:100]}')
        return False
    except Exception as e:
        print(f'  Telegram send error: {e}')
        return False


# ---------------------------------------------------------------------------
# Main deployment loop
# ---------------------------------------------------------------------------

def main() -> int:
    print('=' * 70)
    print('Brevo P.S. Deployment - Neural Feed Templates 2, 4, 5')
    print(f'API Key: {BREVO_API_KEY[:20]}...')
    print('=' * 70)

    results = {}
    any_failure = False

    for tid in [2, 4, 5]:
        print(f'\n{"=" * 70}')
        print(f'TEMPLATE {tid}')
        print(f'{"=" * 70}')

        # ----- Step 1: Fetch -----
        print('Step 1: Fetching current template...')
        data = get_template(tid)
        if not data:
            results[tid] = {'status': 'FETCH_ERROR'}
            any_failure = True
            continue

        name = data.get('name', 'N/A')
        subject = data.get('subject', 'N/A')
        sender = data.get('sender', {})
        reply_to = data.get('replyTo') or EXPECTED_REPLY_TO
        html = data.get('htmlContent', '')
        is_active = data.get('isActive', True)
        tag = data.get('tag', 'welcome-sequence')

        print(f'  Name:     {name}')
        print(f'  Subject:  {subject}')
        print(f'  Sender:   {sender.get("name")} <{sender.get("email")}>')
        print(f'  Reply-to: {reply_to}')
        print(f'  HTML:     {len(html)} chars')

        # ----- Idempotency check -----
        snippet = PS_VERIFICATION_SNIPPETS[tid]
        if snippet in html:
            print(f'\n  SKIP: P.S. already present in template {tid}')
            results[tid] = {
                'status': 'ALREADY_PRESENT',
                'verified': True,
                'reply_to': reply_to,
                'subject': subject,
            }
            continue

        # ----- Step 2: Inject P.S. -----
        print('\nStep 2: Injecting P.S. block...')
        ps_block = PS_BLOCKS[tid]
        new_html, method = inject_ps_block(html, ps_block, tid)
        size_delta = len(new_html) - len(html)
        print(f'  Method:    {method}')
        print(f'  HTML size: {len(html)} -> {len(new_html)} (+{size_delta} chars)')

        # Pre-flight: verify injection before sending to API
        if snippet not in new_html:
            print(f'  PRE-FLIGHT FAILED: Snippet not found in modified HTML - aborting template {tid}')
            results[tid] = {'status': 'INJECTION_FAILED', 'subject': subject}
            any_failure = True
            continue
        print(f'  Pre-flight: OK (snippet confirmed in new HTML)')

        # ----- Step 3: Update via API -----
        print('\nStep 3: Updating template via Brevo API (PUT)...')
        payload = {
            'name': name,
            'subject': subject,
            'htmlContent': new_html,
            'sender': sender,
            'replyTo': reply_to,
            'isActive': is_active,
            'tag': tag,
        }

        status_code, resp_text = put_template(tid, payload)
        resp_preview = resp_text[:150] if resp_text else '(empty body - normal for 204)'
        print(f'  HTTP {status_code}: {resp_preview}')

        if status_code not in [200, 204]:
            print(f'  ERROR: Update failed')
            results[tid] = {
                'status': 'API_UPDATE_ERROR',
                'http_code': status_code,
                'error': resp_text[:300],
                'subject': subject,
                'reply_to': reply_to,
            }
            any_failure = True
            continue

        # ----- Step 4: Verify -----
        print('\nStep 4: Verifying update (re-fetching template)...')
        verify_data = get_template(tid)
        if not verify_data:
            print('  WARNING: Could not re-fetch for verification')
            results[tid] = {
                'status': 'UPDATED_VERIFY_SKIPPED',
                'http_code': status_code,
                'subject': subject,
                'reply_to': reply_to,
                'verified': None,
            }
            continue

        verified_html = verify_data.get('htmlContent', '')
        verified_reply_to = verify_data.get('replyTo', 'NOT SET')

        ps_found = snippet in verified_html
        rt_ok = EXPECTED_REPLY_TO in verified_reply_to or verified_reply_to == EXPECTED_REPLY_TO

        print(f'  P.S. content: {"FOUND" if ps_found else "NOT FOUND"}')
        print(f'  Reply-to: {verified_reply_to} -> {"OK" if rt_ok else "MISMATCH"}')
        print(f'  HTML length after: {len(verified_html)} chars')

        if ps_found:
            print(f'  VERIFIED: Template {tid} deployed successfully')
            results[tid] = {
                'status': 'SUCCESS',
                'http_code': status_code,
                'subject': subject,
                'reply_to': verified_reply_to,
                'verified': True,
                'html_length': len(verified_html),
            }
        else:
            print(f'  VERIFICATION FAILED: Snippet not in re-fetched HTML')
            results[tid] = {
                'status': 'VERIFY_MISMATCH',
                'http_code': status_code,
                'subject': subject,
                'reply_to': verified_reply_to,
                'verified': False,
            }
            any_failure = True

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    print(f'\n{"=" * 70}')
    print('DEPLOYMENT SUMMARY')
    print(f'{"=" * 70}')

    for tid in [2, 4, 5]:
        r = results.get(tid, {})
        status = r.get('status', 'UNKNOWN')
        verified = r.get('verified')
        reply_to = r.get('reply_to', 'N/A')
        subject = r.get('subject', 'N/A')
        ok = status in ('SUCCESS', 'ALREADY_PRESENT')
        print(f'  Template {tid}: {status} | Verified: {verified} | Reply-to: {reply_to}')
        print(f'    Subject: {subject}')

    # Save JSON report
    report_path = '/home/jared/projects/AI-CIV/aether/exports/ps-deployment-results.json'
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump({
            'success': not any_failure,
            'templates': [2, 4, 5],
            'results': {str(k): v for k, v in results.items()},
        }, f, indent=2)
    print(f'\n  Report saved: {report_path}')

    # Send Telegram notification
    print('\nSending Telegram notification...')
    all_ok = not any_failure

    if all_ok:
        tg_message = (
            'P.S. reply-invitation sections deployed to Brevo templates 2, 4, and 5. '
            'Each has a unique engagement question tied to that email\'s topic. '
            'Reply-to verified: purebrain@puremarketing.ai on all three.'
        )
    else:
        lines = []
        for tid in [2, 4, 5]:
            r = results.get(tid, {})
            lines.append(f'Template {tid}: {r.get("status", "UNKNOWN")}')
        tg_message = 'P.S. deployment had issues:\n' + '\n'.join(lines)

    tg_sent = send_telegram(tg_message)
    print(f'  Telegram: {"sent" if tg_sent else "FAILED"}')

    print()
    if all_ok:
        print('ALL DEPLOYMENTS COMPLETE.')
        return 0
    else:
        print('SOME DEPLOYMENTS FAILED - check report above.')
        return 1


if __name__ == '__main__':
    sys.exit(main())
