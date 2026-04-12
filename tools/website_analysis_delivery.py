#!/usr/bin/env python3
"""
PureBrain Website Analysis Delivery Automation
===============================================

Automates the full report delivery pipeline:

  1. Accept delivery request (customer_email, customer_name, company_name, report_html)
  2. Generate a secure random password
  3. Create a password-protected WordPress page from the report HTML
  4. Send a beautiful Brevo delivery email with the report link + password
  5. Log the delivery to JSONL

Usage:
    python3 tools/website_analysis_delivery.py --test
    python3 tools/website_analysis_delivery.py \
        --email "client@company.com" \
        --name "Jane Smith" \
        --company "Acme Corp" \
        --report-file "exports/client-marketing/report-acme.html"

Or import and call deliver_report() directly from the log server.

Author: full-stack-developer
Date: 2026-02-24
"""

import argparse
import json
import logging
import os
import re
import secrets
import string
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment & Configuration
# ---------------------------------------------------------------------------

# Load .env from the project root (two levels up from tools/)
_env_path = Path(__file__).parent.parent / '.env'
load_dotenv(_env_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('website_analysis_delivery')

# WordPress (purebrain.ai)
WP_BASE_URL = 'https://purebrain.ai'
WP_USER = os.getenv('PUREBRAIN_WP_USER', 'Aether')
WP_APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')

# Brevo
BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
BREVO_BASE_URL = 'https://api.brevo.com/v3'

# Brevo list for website analysis customers (reuse List 8 "PureBrain Customers")
BREVO_CUSTOMER_LIST_ID = 8

# Brevo template ID for report delivery email
# Set BREVO_REPORT_DELIVERY_TEMPLATE_ID after creating the template in Brevo
# Default: 11 (Welcome template) — replace once dedicated template is created
BREVO_REPORT_DELIVERY_TEMPLATE_ID = int(os.getenv('BREVO_REPORT_DELIVERY_TEMPLATE_ID', '11'))

# Telegram
TELEGRAM_CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'telegram_config.json'

# Delivery log
DELIVERY_LOG_FILE = Path(__file__).parent.parent / 'logs' / 'website_analysis_deliveries.jsonl'

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _generate_password(length: int = 12) -> str:
    """
    Generate a secure, human-friendly password.

    Format: 4 chars + hyphen + 4 chars + hyphen + 4 chars
    e.g.  acme-7f3k-r9xq
    Uses lowercase letters + digits, excludes ambiguous chars (0, O, l, 1, I).
    """
    alphabet = string.ascii_lowercase + string.digits
    # Remove ambiguous chars
    alphabet = alphabet.translate(str.maketrans('', '', '0oil1'))
    raw = ''.join(secrets.choice(alphabet) for _ in range(12))
    return f'{raw[:4]}-{raw[4:8]}-{raw[8:12]}'


def _slugify(text: str) -> str:
    """Convert company name to a WordPress-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text[:40]  # Cap at 40 chars for slug sanity


def _log_delivery(entry: dict) -> None:
    """Append a delivery record to the JSONL log (thread-safe)."""
    DELIVERY_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DELIVERY_LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')


def _send_telegram(message: str) -> None:
    """Send a Telegram notification to Jared (best-effort, never blocks)."""
    try:
        config = json.loads(TELEGRAM_CONFIG_PATH.read_text())
        token = config.get('bot_token', '')
        chat_id = config.get('default_chat_id', config.get('chat_id', '548906264'))
        if not token:
            return
        requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': message},
            timeout=10,
        )
    except Exception as e:
        logger.warning(f'Telegram notification failed: {e}')


# ---------------------------------------------------------------------------
# WordPress page creation
# ---------------------------------------------------------------------------

def _prepare_report_html(raw_html: str, company_name: str, page_id_hint: str) -> str:
    """
    Transform a standalone report HTML file into WordPress-safe content.

    Steps:
    1. Extract <style> block
    2. Extract <body> inner content
    3. Prepend dark theme override CSS
    4. Wrap in a unique div ID for CSS specificity
    5. Wrap in <!-- wp:html --> block (prevents wpautop destruction)
    """
    # Extract <style> content
    style_match = re.search(r'<style[^>]*>(.*?)</style>', raw_html, re.DOTALL | re.IGNORECASE)
    style_content = style_match.group(1) if style_match else ''

    # Extract Google Fonts links
    fonts_matches = re.findall(
        r'<link[^>]*fonts\.googleapis\.com[^>]*>',
        raw_html,
        re.IGNORECASE
    )
    fonts_html = '\n'.join(fonts_matches)

    # Extract body inner content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', raw_html, re.DOTALL | re.IGNORECASE)
    body_content = body_match.group(1) if body_match else raw_html

    # Dark theme override (must come FIRST in the style block)
    dark_override = f"""
    /* ── PureBrain Report: Dark Theme Override ── */
    html body.page,
    html body {{
      background-color: #0a0e1a !important;
      background: #0a0e1a !important;
      color: #f0f4ff !important;
    }}
    .wp-block-html {{
      background: #0a0e1a !important;
    }}
    /* Magic cursor / TT theme poison cleanup */
    [class*="magic"] {{
      color: inherit !important;
      background-color: inherit !important;
      border-color: inherit !important;
    }}
    body {{ cursor: auto !important; }}
    .tt-magic-cursor, #tt-magic-cursor {{ display: none !important; }}
    """

    # Wrapper div ID (unique per page for CSS specificity)
    wrapper_id = f'pb-report-{_slugify(company_name)}'

    combined = f"""{fonts_html}
<style>
{dark_override}
{style_content}
</style>
<div id="{wrapper_id}">
{body_content}
</div>"""

    # Wrap in wp:html block to prevent wpautop destroying CSS/JS
    return f'<!-- wp:html -->\n{combined}\n<!-- /wp:html -->'


def create_wordpress_report_page(
    company_name: str,
    customer_name: str,
    report_html: str,
    password: str,
) -> dict:
    """
    Create a new password-protected WordPress page on purebrain.ai.

    The page is created as PUBLISHED with password protection so customers
    can access it immediately after receiving the email.

    Args:
        company_name: Used for page title and slug  (e.g. "Acme Corp")
        customer_name: Shown in the page title      (e.g. "Jane Smith")
        report_html:  Full standalone HTML of the report
        password:     Page access password (generated by _generate_password)

    Returns:
        dict with keys: success, page_id, page_url, slug, error (on failure)
    """
    if not WP_APP_PASSWORD:
        return {'success': False, 'error': 'WP_APP_PASSWORD not configured in .env'}

    slug = f'website-analysis-{_slugify(company_name)}'
    title = f'Website Analysis Report — {company_name}'

    prepared_content = _prepare_report_html(report_html, company_name, slug)

    payload = {
        'title': title,
        'slug': slug,
        'content': prepared_content,
        'status': 'publish',       # Published but password-protected
        'password': password,      # WordPress native password protection
        'template': 'elementor_canvas',  # Full-width, no theme nav/footer
        'comment_status': 'closed',
        'ping_status': 'closed',
    }

    endpoint = f'{WP_BASE_URL}/wp-json/wp/v2/pages'

    try:
        resp = requests.post(
            endpoint,
            auth=(WP_USER, WP_APP_PASSWORD),
            json=payload,
            timeout=30,
        )

        if resp.status_code in (200, 201):
            data = resp.json()
            page_id = data.get('id')
            page_url = data.get('link', f'{WP_BASE_URL}/{slug}/')
            logger.info(
                f'WP page created: id={page_id} slug={slug} '
                f'url={page_url} password_protected={bool(password)}'
            )

            # Clear Elementor cache so the page renders immediately
            _clear_elementor_cache()

            return {
                'success': True,
                'page_id': page_id,
                'page_url': page_url,
                'slug': slug,
            }
        else:
            error_msg = resp.text[:300]
            logger.error(
                f'WP page creation failed: status={resp.status_code} body={error_msg}'
            )
            return {
                'success': False,
                'error': f'HTTP {resp.status_code}: {error_msg}',
            }

    except Exception as e:
        logger.error(f'WP page creation exception: {e}')
        return {'success': False, 'error': str(e)}


def _clear_elementor_cache() -> None:
    """Clear Elementor cache after page creation (best-effort)."""
    try:
        resp = requests.delete(
            f'{WP_BASE_URL}/wp-json/elementor/v1/cache',
            auth=(WP_USER, WP_APP_PASSWORD),
            timeout=10,
        )
        logger.info(f'Elementor cache cleared: status={resp.status_code}')
    except Exception as e:
        logger.warning(f'Elementor cache clear failed (non-fatal): {e}')


# ---------------------------------------------------------------------------
# Brevo email delivery
# ---------------------------------------------------------------------------

def _upsert_brevo_contact(email: str, attributes: dict, list_id: int) -> bool:
    """Add/update a Brevo contact."""
    if not BREVO_API_KEY:
        logger.error('BREVO_API_KEY not configured')
        return False
    try:
        resp = requests.post(
            f'{BREVO_BASE_URL}/contacts',
            headers={
                'api-key': BREVO_API_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'email': email,
                'attributes': attributes,
                'listIds': [list_id],
                'updateEnabled': True,
            },
            timeout=15,
        )
        if resp.status_code in (200, 201, 204):
            logger.info(f'Brevo contact upserted: email={email} list={list_id}')
            return True
        else:
            logger.error(
                f'Brevo contact upsert failed: email={email} '
                f'status={resp.status_code} body={resp.text[:200]}'
            )
            return False
    except Exception as e:
        logger.error(f'Brevo contact upsert exception: {e}')
        return False


def send_report_delivery_email(
    customer_email: str,
    customer_name: str,
    company_name: str,
    report_url: str,
    report_password: str,
    order_id: str = '',
    tier: str = '',
) -> dict:
    """
    Send the report delivery email via Brevo transactional API.

    Template variables (set these in the Brevo template):
        {{ params.FIRSTNAME }}       - Customer first name
        {{ params.COMPANY_NAME }}    - Company analysed
        {{ params.REPORT_URL }}      - Full URL to the password-protected page
        {{ params.REPORT_PASSWORD }} - Access password
        {{ params.ORDER_ID }}        - PayPal order ID (optional)

    Returns:
        dict with keys: success, message_id, error (on failure)
    """
    if not BREVO_API_KEY:
        return {'success': False, 'error': 'BREVO_API_KEY not configured'}

    first_name = customer_name.split()[0] if customer_name else 'there'

    template_params = {
        'FIRSTNAME': first_name,
        'COMPANY_NAME': company_name,
        'REPORT_URL': report_url,
        'REPORT_PASSWORD': report_password,
        'ORDER_ID': order_id,
        'TIER': tier,
    }

    try:
        resp = requests.post(
            f'{BREVO_BASE_URL}/smtp/email',
            headers={
                'api-key': BREVO_API_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'to': [{'email': customer_email, 'name': customer_name}],
                'templateId': BREVO_REPORT_DELIVERY_TEMPLATE_ID,
                'params': template_params,
                'replyTo': {'email': 'hello@purebrain.ai', 'name': 'PureBrain Team'},
            },
            timeout=15,
        )
        if resp.status_code in (200, 201):
            message_id = resp.json().get('messageId', '')
            logger.info(
                f'Report delivery email sent: to={customer_email} '
                f'template={BREVO_REPORT_DELIVERY_TEMPLATE_ID} messageId={message_id}'
            )
            return {'success': True, 'message_id': message_id}
        else:
            error_body = resp.text[:300]
            logger.error(
                f'Report delivery email failed: to={customer_email} '
                f'status={resp.status_code} body={error_body}'
            )
            return {'success': False, 'error': f'HTTP {resp.status_code}: {error_body}'}
    except Exception as e:
        logger.error(f'Report delivery email exception: {e}')
        return {'success': False, 'error': str(e)}


# ---------------------------------------------------------------------------
# Main delivery orchestration
# ---------------------------------------------------------------------------

def deliver_report(
    customer_email: str,
    customer_name: str,
    company_name: str,
    report_html: str,
    order_id: str = '',
    tier: str = '',
) -> dict:
    """
    Full end-to-end report delivery pipeline.

    Steps:
      1. Generate secure password
      2. Create password-protected WordPress page
      3. Upsert Brevo contact
      4. Send delivery email
      5. Send Telegram notification to Jared
      6. Log the delivery

    Args:
        customer_email:  Buyer's email address
        customer_name:   Buyer's full name ("Jane Smith")
        company_name:    Company whose site was analysed ("Acme Corp")
        report_html:     Full standalone HTML content of the analysis report
        order_id:        PayPal order ID (optional, for email personalisation)
        tier:            Purchase tier name (optional)

    Returns:
        dict with:
          success          - bool overall success
          page_url         - URL of the report page (if created)
          report_password  - Password for the report page
          email_sent       - bool email delivery status
          page_id          - WordPress page ID
          errors           - list of any non-fatal errors
    """
    now = datetime.now(timezone.utc).isoformat()
    errors = []

    logger.info(
        f'Starting delivery: customer={customer_email} company={company_name}'
    )

    # Step 1: Generate password
    report_password = _generate_password()
    logger.info(f'Generated report password: {report_password}')

    # Step 2: Create WordPress page
    wp_result = create_wordpress_report_page(
        company_name=company_name,
        customer_name=customer_name,
        report_html=report_html,
        password=report_password,
    )

    if not wp_result['success']:
        error = f'WordPress page creation failed: {wp_result.get("error", "unknown")}'
        logger.error(error)
        errors.append(error)
        _log_delivery({
            'event': 'delivery_failed',
            'stage': 'wordpress_page_creation',
            'customer_email': customer_email,
            'company_name': company_name,
            'order_id': order_id,
            'error': error,
            'timestamp': now,
        })
        return {
            'success': False,
            'errors': errors,
            'stage_failed': 'wordpress_page_creation',
        }

    page_id = wp_result['page_id']
    page_url = wp_result['page_url']
    logger.info(f'WordPress page created: id={page_id} url={page_url}')

    # Step 3: Upsert Brevo contact (non-blocking, fire-and-forget)
    def _upsert_contact():
        first_name_parts = customer_name.split(' ', 1)
        attrs = {
            'FIRSTNAME': first_name_parts[0],
            'LASTNAME': first_name_parts[1] if len(first_name_parts) > 1 else '',
            'COMPANY': company_name,
            'TIER': tier or 'website-analysis',
        }
        _upsert_brevo_contact(customer_email, attrs, BREVO_CUSTOMER_LIST_ID)

    threading.Thread(target=_upsert_contact, daemon=True).start()

    # Step 4: Send delivery email
    email_result = send_report_delivery_email(
        customer_email=customer_email,
        customer_name=customer_name,
        company_name=company_name,
        report_url=page_url,
        report_password=report_password,
        order_id=order_id,
        tier=tier,
    )

    email_sent = email_result.get('success', False)
    if not email_sent:
        error = f'Email delivery failed: {email_result.get("error", "unknown")}'
        logger.error(error)
        errors.append(error)

    # Step 5: Telegram notification to Jared
    tg_msg = (
        f'\U0001f4c4 WEBSITE ANALYSIS REPORT DELIVERED\n'
        f'Customer: {customer_name} ({customer_email})\n'
        f'Company: {company_name}\n'
        f'Report URL: {page_url}\n'
        f'Password: {report_password}\n'
        f'Email sent: {"Yes" if email_sent else "FAILED"}\n'
        f'Order ID: {order_id or "N/A"}'
    )
    threading.Thread(target=_send_telegram, args=(tg_msg,), daemon=True).start()

    # Step 6: Log the delivery
    delivery_record = {
        'event': 'report_delivered',
        'customer_email': customer_email,
        'customer_name': customer_name,
        'company_name': company_name,
        'order_id': order_id,
        'tier': tier,
        'page_id': page_id,
        'page_url': page_url,
        'report_password': report_password,
        'email_sent': email_sent,
        'email_message_id': email_result.get('message_id', ''),
        'errors': errors,
        'timestamp': now,
    }
    _log_delivery(delivery_record)

    overall_success = email_sent  # Page created; email is the critical success gate
    logger.info(
        f'Delivery complete: customer={customer_email} company={company_name} '
        f'page_id={page_id} email_sent={email_sent} success={overall_success}'
    )

    return {
        'success': overall_success,
        'page_id': page_id,
        'page_url': page_url,
        'report_password': report_password,
        'email_sent': email_sent,
        'errors': errors,
    }


# ---------------------------------------------------------------------------
# PayPal webhook integration helper
# ---------------------------------------------------------------------------

def deliver_from_paypal_webhook(webhook_payload: dict) -> dict:
    """
    Called by the log server's paypal_webhook endpoint when a
    PAYMENT.CAPTURE.COMPLETED event arrives for the website analysis product.

    This function is the bridge between a PayPal webhook and the delivery pipeline.
    The webhook does NOT contain the report HTML — the report must already exist
    in the delivery queue (see docs/website-analysis-automation.md for the
    two-phase delivery approach).

    Args:
        webhook_payload: The parsed PayPal webhook event JSON

    Returns:
        dict with 'triggered': bool and 'reason': str
    """
    try:
        resource = webhook_payload.get('resource', {})
        amount = resource.get('amount', {}).get('value', '0')
        payer = resource.get('payer', {})
        payer_email = payer.get('email_address', '')
        payer_name_obj = payer.get('name', {})
        payer_name = f'{payer_name_obj.get("given_name", "")} {payer_name_obj.get("surname", "")}'.strip()
        order_id = resource.get('id', '')
        purchase_units = resource.get('purchase_units', [{}])
        description = purchase_units[0].get('description', '') if purchase_units else ''
        custom_id = purchase_units[0].get('custom_id', '') if purchase_units else ''

        logger.info(
            f'deliver_from_paypal_webhook: order={order_id} '
            f'payer={payer_email} amount={amount} description={description}'
        )

        # We cannot auto-deliver from a webhook alone — the report HTML must be
        # prepared beforehand by Aether when the customer submits their site URL.
        # Log an intent record so the next Aether session picks it up.
        intent_record = {
            'event': 'delivery_intent_from_webhook',
            'order_id': order_id,
            'payer_email': payer_email,
            'payer_name': payer_name,
            'amount': amount,
            'description': description,
            'custom_id': custom_id,
            'status': 'pending_report_generation',
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        _log_delivery(intent_record)

        # Telegram ping so Jared / Aether knows a new delivery is queued
        tg_msg = (
            f'\U0001f6a8 NEW WEBSITE ANALYSIS PURCHASE — delivery queued\n'
            f'Customer: {payer_name} ({payer_email})\n'
            f'Amount: ${amount}\n'
            f'Order ID: {order_id}\n'
            f'\n'
            f'Action needed: Generate report and run deliver_report() to complete delivery.'
        )
        threading.Thread(target=_send_telegram, args=(tg_msg,), daemon=True).start()

        return {
            'triggered': True,
            'reason': 'intent_logged',
            'payer_email': payer_email,
            'order_id': order_id,
        }

    except Exception as e:
        logger.error(f'deliver_from_paypal_webhook exception: {e}')
        return {'triggered': False, 'reason': str(e)}


# ---------------------------------------------------------------------------
# CLI entry point for manual / testing use
# ---------------------------------------------------------------------------

def _run_test_delivery():
    """Run a test delivery with a minimal placeholder report."""
    logger.info('Running test delivery...')

    test_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TEST REPORT — Acme Corp</title>
<style>
:root { --bg: #0a0e1a; --blue: #2a93c1; --text: #f0f4ff; }
body { background: var(--bg); color: var(--text); font-family: Inter, sans-serif;
       display: flex; align-items: center; justify-content: center; min-height: 100vh; }
.box { text-align: center; max-width: 600px; padding: 40px; }
h1 { color: var(--blue); font-size: 2rem; margin-bottom: 16px; }
p { color: rgba(240,244,255,0.7); line-height: 1.7; }
</style>
</head>
<body>
<div class="box">
  <h1>TEST REPORT: Acme Corp</h1>
  <p>This is a test delivery page generated by the website analysis delivery system.</p>
  <p>If you can read this, the WordPress page creation pipeline is working correctly.</p>
</div>
</body>
</html>"""

    result = deliver_report(
        customer_email='test@example.com',
        customer_name='Test Customer',
        company_name='Acme Corp',
        report_html=test_html,
        order_id='TEST-ORDER-001',
        tier='website-analysis-standard',
    )

    print('\n=== TEST DELIVERY RESULT ===')
    print(json.dumps(result, indent=2))

    if result.get('success'):
        print('\nTest PASSED.')
        print(f'Report URL:      {result.get("page_url")}')
        print(f'Report Password: {result.get("report_password")}')
    else:
        print('\nTest had errors:')
        for err in result.get('errors', []):
            print(f'  - {err}')

    return result


def main():
    parser = argparse.ArgumentParser(
        description='PureBrain Website Analysis Report Delivery Tool'
    )
    parser.add_argument('--test', action='store_true',
                        help='Run a test delivery with a placeholder report')
    parser.add_argument('--email', help='Customer email address')
    parser.add_argument('--name', help='Customer full name')
    parser.add_argument('--company', help='Company name (used in page title and slug)')
    parser.add_argument('--report-file', help='Path to the report HTML file')
    parser.add_argument('--order-id', default='', help='PayPal order ID (optional)')
    parser.add_argument('--tier', default='', help='Purchase tier (optional)')

    args = parser.parse_args()

    if args.test:
        _run_test_delivery()
        return

    # Manual delivery mode
    required = ['email', 'name', 'company', 'report_file']
    missing = [r for r in required if not getattr(args, r.replace('-', '_'), None)]
    if missing:
        parser.error(f'Missing required arguments: {", ".join("--" + m for m in missing)}')

    report_path = Path(args.report_file)
    if not report_path.exists():
        parser.error(f'Report file not found: {args.report_file}')

    report_html = report_path.read_text(encoding='utf-8')

    result = deliver_report(
        customer_email=args.email,
        customer_name=args.name,
        company_name=args.company,
        report_html=report_html,
        order_id=args.order_id,
        tier=args.tier,
    )

    print('\n=== DELIVERY RESULT ===')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
