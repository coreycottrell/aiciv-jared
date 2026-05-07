#!/usr/bin/env python3
"""
Pure Brain Web Conversation Log Server

Flask server for logging Pure Brain web conversations.
Provides HTTP API endpoints for:
- POST /api/log-conversation - Log conversation data to JSONL
- GET /api/health - Health check
- GET /api/stats - Conversation statistics

Supports SSL/HTTPS for secure connections from purebrain.ai

Author: refactoring-specialist
Date: 2026-02-10
Updated: 2026-02-12 (SSL support added by api-architect)
Updated: 2026-02-17 (A-C-Gee landing-chat forwarding added by full-stack-developer)
"""

import hmac
import json
import logging
import os
import ssl
import subprocess
import threading
import time
import urllib.request
import urllib.error
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

# Load .env so server picks up ADMIN_TOKEN and similar runtime secrets.
try:
    from dotenv import load_dotenv as _load_dotenv
    _load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
except Exception:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('purebrain_log_server')

# Default log directory
DEFAULT_LOG_DIR = '/home/jared/projects/AI-CIV/aether/logs'
DEFAULT_LOG_FILE = 'purebrain_web_conversations.jsonl'

# SSL certificate paths
SSL_CERT_DIR = '/home/jared/projects/AI-CIV/aether/config/ssl'
SSL_CERT_FILE = os.path.join(SSL_CERT_DIR, 'server.crt')
SSL_KEY_FILE = os.path.join(SSL_CERT_DIR, 'server.key')

# Hub configuration defaults
DEFAULT_HUB_ROOM = 'operations'
DEFAULT_HUB_LOCAL_PATH = '/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub'
HUB_CLI_PATH = '/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/scripts/hub_cli.py'

# A-C-Gee shared database endpoint
ACGEE_LANDING_CHAT_URL = 'http://5.161.90.32:3001/api/landing-chat'
ACGEE_RETRY_DELAY_SECONDS = 10
ACGEE_MAX_RETRIES = 3

# File write lock for thread safety
_file_lock = threading.Lock()

# Tracks which order IDs have already had a seed fired (payment trigger or chatbox addendum).
# Used by the dedup guard to prevent double-firing on the same order.
_seeds_fired_for_orders: set = set()

# --- CONSTITUTIONAL GUARD: AI name must NEVER be empty in a seed email ---
# Added 2026-04-08 after Matt Keough's seed went out with no AI name.
# "It cannot happen again." — Jared
_AI_NAME_PLACEHOLDER_VALUES = frozenset({
    '', '(not yet named)', 'unknown ai', 'none', 'null', 'undefined',
    'unknown', 'n/a', 'tbd', '(unnamed)',
})

# Held seeds that were blocked due to missing AI name.
# Structure: list of dicts with session_uuid, human_name, human_email, tier, order_id, timestamp, path
_held_seeds: list = []

# --- EPHEMERAL SECRETS: Burn-on-read secret storage ---
# In-memory only. Structure: {uuid_str: {"secret": str, "created_at": datetime, "expires_at": datetime, "viewed": bool}}
# Cleaned opportunistically on each POST or GET.
_ephemeral_secrets: Dict[str, Dict[str, Any]] = {}
_ephemeral_lock = threading.Lock()


def _validate_ai_name_for_seed(ai_name: str, context: str, **kwargs) -> bool:
    """
    CONSTITUTIONAL GUARD: Validate that ai_name is a real name before sending a seed.

    Returns True if the name is valid (send is allowed).
    Returns False if the name is missing/placeholder (send MUST be blocked).

    When blocked, logs a critical warning and holds the seed metadata for later retry.
    """
    clean = (ai_name or '').strip().lower()
    if clean in _AI_NAME_PLACEHOLDER_VALUES:
        _held_info = {
            'context': context,
            'ai_name_raw': ai_name,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        _held_seeds.append(_held_info)
        logger.critical(
            f'[SEED-BLOCKED] AI name missing or placeholder in {context}! '
            f'ai_name={ai_name!r}, kwargs={kwargs}. '
            f'Seed HELD — will NOT send without a valid AI name. '
            f'Total held seeds: {len(_held_seeds)}'
        )
        # Also send Telegram alert so Jared knows immediately
        try:
            _tg_alert = (
                f'[SEED BLOCKED] AI name missing!\n'
                f'Context: {context}\n'
                f'Human: {kwargs.get("human_name", kwargs.get("payer_name", "unknown"))}\n'
                f'Email: {kwargs.get("human_email", kwargs.get("payer_email", "unknown"))}\n'
                f'ai_name={ai_name!r}\n'
                f'Seed is HELD, not sent.'
            )
            _send_telegram_notification(_tg_alert)
        except Exception:
            pass  # Don't let notification failure crash the guard
        return False
    return True


def generate_self_signed_cert():
    """
    Generate self-signed SSL certificate if it doesn't exist.

    Creates a certificate valid for 365 days with SANs for the server IP.
    """
    os.makedirs(SSL_CERT_DIR, exist_ok=True)

    if os.path.exists(SSL_CERT_FILE) and os.path.exists(SSL_KEY_FILE):
        logger.info('SSL certificates already exist')
        return True

    logger.info('Generating self-signed SSL certificate...')

    # OpenSSL config for SAN (Subject Alternative Names)
    openssl_config = f"""
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
C = US
ST = State
L = City
O = PureBrain
OU = LogServer
CN = 89.167.19.20

[v3_req]
subjectAltName = @alt_names
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment

[alt_names]
IP.1 = 89.167.19.20
DNS.1 = localhost
IP.2 = 127.0.0.1
"""

    config_file = os.path.join(SSL_CERT_DIR, 'openssl.cnf')
    with open(config_file, 'w') as f:
        f.write(openssl_config)

    # Generate certificate using OpenSSL
    cmd = [
        'openssl', 'req', '-x509', '-nodes',
        '-days', '365',
        '-newkey', 'rsa:2048',
        '-keyout', SSL_KEY_FILE,
        '-out', SSL_CERT_FILE,
        '-config', config_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            logger.info(f'SSL certificate generated: {SSL_CERT_FILE}')
            return True
        else:
            logger.error(f'Failed to generate SSL cert: {result.stderr}')
            return False
    except Exception as e:
        logger.error(f'Error generating SSL cert: {e}')
        return False


def forward_to_acgee(log_entry: Dict[str, Any]) -> None:
    """
    Forward a conversation log entry to the A-C-Gee shared landing-chat endpoint.

    Sends the full message history so conversations are saved to sage.db on
    the Sage & Weaver VPS. Uses retry logic for 500 errors (may be rate limits).

    Args:
        log_entry: The conversation log entry dictionary (same shape as local JSONL).
    """
    session_id = log_entry.get('session_id', 'unknown')

    # Build the payload for the landing-chat API
    payload = {
        'messages': log_entry.get('messages', []),
        'system': log_entry.get('system', ''),
        'session_id': session_id,
        'source': 'purebrain',
    }

    payload_bytes = json.dumps(payload).encode('utf-8')

    for attempt in range(1, ACGEE_MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                ACGEE_LANDING_CHAT_URL,
                data=payload_bytes,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Aether-PureBrain-LogServer/1.0',
                },
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.getcode()
                body = resp.read().decode('utf-8')

            if status == 200:
                logger.info(
                    f'A-C-Gee forward success: session={session_id} attempt={attempt}'
                )
                return  # Success - stop retrying

            logger.warning(
                f'A-C-Gee forward unexpected status {status} for session={session_id}'
            )
            return  # Non-500 non-200 - don't retry

        except urllib.error.HTTPError as e:
            if e.code == 500:
                logger.warning(
                    f'A-C-Gee 500 error (attempt {attempt}/{ACGEE_MAX_RETRIES}) '
                    f'session={session_id} - retrying in {ACGEE_RETRY_DELAY_SECONDS}s'
                )
                if attempt < ACGEE_MAX_RETRIES:
                    time.sleep(ACGEE_RETRY_DELAY_SECONDS)
            else:
                logger.warning(
                    f'A-C-Gee HTTP error {e.code} for session={session_id}: {e.reason}'
                )
                return  # Non-500 HTTP error - don't retry

        except urllib.error.URLError as e:
            logger.warning(
                f'A-C-Gee network error (attempt {attempt}/{ACGEE_MAX_RETRIES}) '
                f'session={session_id}: {e.reason}'
            )
            if attempt < ACGEE_MAX_RETRIES:
                time.sleep(ACGEE_RETRY_DELAY_SECONDS)

        except Exception as e:
            logger.warning(f'A-C-Gee unexpected error for session={session_id}: {e}')
            return  # Unknown error - don't retry

    logger.error(
        f'A-C-Gee forward failed after {ACGEE_MAX_RETRIES} attempts for session={session_id}'
    )


def forward_to_hub(log_entry: Dict[str, Any], hub_room: str = DEFAULT_HUB_ROOM) -> None:
    """
    Forward a conversation log entry to the AICIV comms hub.

    This function runs the hub_cli.py send command to post a message
    to the specified room. Designed to be called asynchronously
    from a background thread.

    Args:
        log_entry: The conversation log entry dictionary.
        hub_room: The hub room to post to (default: 'operations').
    """
    try:
        # Build summary from conversation
        session_id = log_entry.get('session_id', 'unknown')
        messages = log_entry.get('messages', [])
        message_count = len(messages)

        # Get first user message as preview
        first_user_msg = ''
        for msg in messages:
            if msg.get('role') == 'user':
                first_user_msg = msg.get('content', '')[:100]
                break

        summary = f"Pure Brain conversation: {session_id} ({message_count} messages)"

        # Build body with conversation details
        body_lines = [
            f"Session ID: {session_id}",
            f"Messages: {message_count}",
            f"Timestamp: {log_entry.get('server_timestamp', 'unknown')}",
        ]

        if log_entry.get('page_url'):
            body_lines.append(f"Page: {log_entry['page_url']}")

        if first_user_msg:
            body_lines.append(f"First query: {first_user_msg}...")

        body = '\n'.join(body_lines)

        # Set up environment for hub_cli
        env = os.environ.copy()
        env['HUB_REPO_URL'] = env.get('HUB_REPO_URL', 'git@github-interciv:coreycottrell/aiciv-comms-hub.git')
        env['HUB_LOCAL_PATH'] = env.get('HUB_LOCAL_PATH', DEFAULT_HUB_LOCAL_PATH)
        env['HUB_AGENT_ID'] = env.get('HUB_AGENT_ID', 'aether-purebrain')
        env['HUB_AGENT_DISPLAY'] = env.get('HUB_AGENT_DISPLAY', 'Pure Brain Log Server')
        env['GIT_AUTHOR_NAME'] = env.get('GIT_AUTHOR_NAME', 'Aether Pure Brain')
        env['GIT_AUTHOR_EMAIL'] = env.get('GIT_AUTHOR_EMAIL', 'purebrain@ai-civ.local')

        # Run hub_cli send command
        cmd = [
            'python3', HUB_CLI_PATH,
            'send',
            '--room', hub_room,
            '--type', 'status',
            '--summary', summary,
            '--body', body
        ]

        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout for git operations
        )

        if result.returncode == 0:
            logger.info(f'Forwarded to hub: {session_id} -> {hub_room}')
        else:
            logger.warning(f'Hub forwarding failed: {result.stderr}')

    except subprocess.TimeoutExpired:
        logger.warning(f'Hub forwarding timed out for session: {session_id}')
    except Exception as e:
        logger.warning(f'Hub forwarding error: {e}')


def create_app(
    log_dir: Optional[str] = None,
    enable_hub_forwarding: bool = True,
    hub_room: Optional[str] = None,
    enable_acgee_forwarding: bool = True,
) -> Flask:
    """
    Create and configure Flask application.

    Args:
        log_dir: Directory for log files. Defaults to DEFAULT_LOG_DIR.
        enable_hub_forwarding: Whether to forward conversations to AICIV hub.
        hub_room: Hub room for forwarding (default: 'operations').
        enable_acgee_forwarding: Whether to forward conversations to A-C-Gee shared DB.

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)

    # Configure log directory
    log_dir = log_dir or DEFAULT_LOG_DIR
    app.config['LOG_DIR'] = log_dir
    app.config['LOG_FILE'] = os.path.join(log_dir, DEFAULT_LOG_FILE)

    # Configure hub forwarding
    app.config['ENABLE_HUB_FORWARDING'] = enable_hub_forwarding
    app.config['HUB_ROOM'] = hub_room or DEFAULT_HUB_ROOM

    # Configure A-C-Gee forwarding
    app.config['ENABLE_ACGEE_FORWARDING'] = enable_acgee_forwarding

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Enable CORS for all routes (required for cross-origin HTTPS requests)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register routes
    register_routes(app)

    return app


def _send_telegram_notification(message: str) -> None:
    """Send a notification to Jared via Telegram (best-effort, non-blocking)."""
    try:
        tg_config_path = '/home/jared/projects/AI-CIV/aether/config/telegram_config.json'
        with open(tg_config_path) as f:
            tg_config = json.load(f)
        bot_token = tg_config.get('bot_token', '')
        chat_id = tg_config.get('default_chat_id', '')
        if bot_token and chat_id:
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            data = json.dumps({'chat_id': chat_id, 'text': message}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=10)
            logger.info('Telegram notification sent')
    except Exception as e:
        logger.warning(f'Telegram notification failed: {e}')


def register_routes(app: Flask) -> None:
    """Register all API routes on the Flask app."""

    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        logger.info('Health check requested')
        return jsonify({
            'status': 'ok',
            'ssl': True,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

    @app.route('/api/log-conversation', methods=['POST', 'OPTIONS'])
    def log_conversation():
        """
        Log conversation data to JSONL file.

        Expected JSON payload:
        {
            "session_id": "unique-session-id",
            "messages": [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ],
            "user_agent": "optional",
            "page_url": "optional",
            "referrer": "optional"
        }
        """
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            return '', 204

        # Validate content type
        if not request.is_json:
            logger.warning('Request rejected: not JSON content type')
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        # Parse JSON
        try:
            data = request.get_json()
        except Exception as e:
            logger.warning(f'Request rejected: invalid JSON - {e}')
            return jsonify({'error': 'Invalid JSON'}), 400

        # Validate required fields
        # Accept both 'messages' (A-C-Gee standard) and 'conversationHistory' (PureBrain frontend)
        messages = data.get('messages') or data.get('conversationHistory') if data else None
        if not data or not messages:
            logger.warning('Request rejected: missing messages/conversationHistory field')
            return jsonify({'error': 'Missing required field: messages or conversationHistory'}), 400

        # Build log entry
        # Accept both snake_case (Python convention) and camelCase (JS convention) for session ID.
        # Generate a UUID session_id if none provided so A-C-Gee can upsert correctly.
        raw_session_id = data.get('session_id') or data.get('sessionId') or ''
        session_id = raw_session_id.strip() if raw_session_id.strip() else f'pb-{uuid.uuid4()}'

        log_entry = {
            'session_id': session_id,
            'messages': messages,  # Always use 'messages' for A-C-Gee compatibility
            'server_timestamp': datetime.now(timezone.utc).isoformat(),
            'client_ip': request.remote_addr
        }

        # Add optional fields if present
        optional_fields = [
            'user_agent', 'page_url', 'referrer', 'user_id', 'metadata',
            # Onboarding/session data from client
            'aiName', 'userName', 'userTier', 'referralCode',
            'conversationId', 'brainId', 'projectId', 'title',
            'createdAt', 'updatedAt', 'messageCount'
        ]
        for field in optional_fields:
            if field in data:
                log_entry[field] = data[field]

        # Write to JSONL file (thread-safe)
        log_file = app.config['LOG_FILE']
        try:
            with _file_lock:
                with open(log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
            logger.info(f'Logged conversation: session={log_entry["session_id"]}')
        except Exception as e:
            logger.error(f'Failed to write log: {e}')
            return jsonify({'error': 'Failed to write log'}), 500

        # Forward to AICIV comms hub asynchronously (non-blocking)
        if app.config.get('ENABLE_HUB_FORWARDING', True):
            hub_room = app.config.get('HUB_ROOM', DEFAULT_HUB_ROOM)
            try:
                # Run in background thread so it doesn't block API response
                hub_thread = threading.Thread(
                    target=forward_to_hub,
                    args=(log_entry.copy(), hub_room),
                    daemon=True
                )
                hub_thread.start()
                logger.debug(f'Started hub forwarding thread for session={log_entry["session_id"]}')
            except Exception as e:
                # Hub forwarding failure should not break local logging
                logger.warning(f'Failed to start hub forwarding: {e}')

        # Forward to A-C-Gee shared database asynchronously (non-blocking)
        if app.config.get('ENABLE_ACGEE_FORWARDING', True):
            try:
                acgee_thread = threading.Thread(
                    target=forward_to_acgee,
                    args=(log_entry.copy(),),
                    daemon=True
                )
                acgee_thread.start()
                logger.debug(f'Started A-C-Gee forwarding thread for session={log_entry["session_id"]}')
            except Exception as e:
                # A-C-Gee forwarding failure should not break local logging
                logger.warning(f'Failed to start A-C-Gee forwarding: {e}')

        return jsonify({
            'success': True,
            'session_id': log_entry['session_id'],
            'timestamp': log_entry['server_timestamp']
        })

    @app.route('/api/verify-payment', methods=['POST', 'OPTIONS'])
    def verify_payment():
        """
        Verify a PayPal payment after SDK capture.
        Called by pay-test page after PayPal SDK completes payment.

        Expected JSON payload (accepts both camelCase and snake_case):
        {
            "orderId": "PAYPAL-ORDER-ID",       // or "order_id"
            "tier": "Awakened|Bonded|Partnered",
            "amount": "79.00",
            "payerEmail": "buyer@email.com",
            "payerName": "John Doe",
            "captureId": "CAPTURE-ID",
            "timestamp": "ISO-8601"
        }
        """
        if request.method == 'OPTIONS':
            return '', 204

        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({'error': 'Invalid JSON'}), 400

        # Accept both camelCase and snake_case for consistency with /api/send-seed
        if data and data.get('order_id') and not data.get('orderId'):
            data['orderId'] = data['order_id']
        if not data or not data.get('orderId'):
            return jsonify({'error': 'Missing required field: orderId'}), 400

        # Extract payer email — check top-level field first, then nested payerInfo.
        # PayPal subscription onApprove passes the raw SDK data object as payerInfo,
        # which may contain email_address / name sub-objects.
        payer_email = (data.get('payerEmail') or '').strip()
        payer_name = (data.get('payerName') or '').strip()
        payer_info = data.get('payerInfo') or {}
        if isinstance(payer_info, dict):
            if not payer_email:
                payer_email = (payer_info.get('email_address') or '').strip()
            if not payer_name:
                name_obj = payer_info.get('name') or {}
                if isinstance(name_obj, dict):
                    given = (name_obj.get('given_name') or '').strip()
                    surname = (name_obj.get('surname') or '').strip()
                    payer_name = f'{given} {surname}'.strip()

        # 2026-03-20: PayPal subscription onApprove only returns subscriptionID.
        # Payer email, name, and amount are NOT included in the SDK callback data for
        # subscription flows. For I-* subscription IDs where we have no payer details,
        # call the PayPal Subscriptions API to fetch subscriber info before logging.
        #
        # Strategy (2026-03-20 update — sandbox fallback):
        #   1. Try LIVE API first (real subscriptions).
        #   2. If live returns 404 or any error, try SANDBOX API (sandbox/test subs).
        #      Sandbox credentials: PAYPAL_SANDBOX_CLIENT_ID / PAYPAL_SANDBOX_SECRET in .env.
        #   3. If BOTH APIs fail, fall back to data sent from the page:
        #      - tier is always in the payload; map it to known price
        #      - mark email/name as "(sandbox-sub)" so the record is identifiable
        #   This ensures sandbox test subscriptions (I-* IDs on sandbox API) are
        #   captured correctly even though no isSandbox flag is sent in verify-payment.
        _order_id_early = data.get('orderId', '')
        # Tier-to-price fallback table (matches pay-test-sandbox-3 PRICES config)
        _TIER_PRICES = {
            'awakened':  '149.00',
            'bonded':    '299.00',
            'partnered': '499.00',
            'unified':   '999.00',
        }
        if _order_id_early.startswith('I-') and (not payer_email or not payer_name):
            import base64 as _base64

            def _fetch_paypal_subscription(base_url, client_id, secret):
                """Try fetching subscription data from a given PayPal API base URL.
                Returns parsed subscription dict or raises on failure."""
                _creds = f'{client_id}:{secret}'
                _b64 = _base64.b64encode(_creds.encode()).decode()
                _token_req = urllib.request.Request(
                    f'{base_url}/v1/oauth2/token',
                    data=b'grant_type=client_credentials',
                    headers={
                        'Authorization': f'Basic {_b64}',
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    method='POST'
                )
                with urllib.request.urlopen(_token_req, timeout=8) as _r:
                    _token_data = json.loads(_r.read())
                _access_token = _token_data.get('access_token', '')
                if not _access_token:
                    raise ValueError('No access_token in PayPal OAuth response')
                _sub_req = urllib.request.Request(
                    f'{base_url}/v1/billing/subscriptions/{_order_id_early}',
                    headers={
                        'Authorization': f'Bearer {_access_token}',
                        'Content-Type': 'application/json',
                    },
                    method='GET'
                )
                with urllib.request.urlopen(_sub_req, timeout=8) as _r:
                    return json.loads(_r.read())

            def _apply_sub_data(sub_data):
                """Extract email, name, amount from a PayPal subscription response dict.
                Updates nonlocal payer_email / payer_name and data['amount'] in place."""
                nonlocal payer_email, payer_name
                _subscriber = sub_data.get('subscriber', {})
                if not payer_email:
                    payer_email = (_subscriber.get('email_address') or '').strip()
                if not payer_name:
                    _sname = _subscriber.get('name', {})
                    _given = (_sname.get('given_name') or '').strip()
                    _sur = (_sname.get('surname') or '').strip()
                    payer_name = f'{_given} {_sur}'.strip()
                _billing = sub_data.get('billing_info', {})
                _last_pmt = _billing.get('last_payment', {})
                _last_amt = (_last_pmt.get('amount') or {}).get('value', '')
                if _last_amt and (data.get('amount', '0.00') in ('0.00', '', None)):
                    data['amount'] = _last_amt
                return _last_amt

            # --- Step 1: Try LIVE PayPal API ---
            _live_ok = False
            try:
                _live_client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
                _live_secret = os.environ.get('PAYPAL_SECRET', '')
                _sub_data = _fetch_paypal_subscription(
                    'https://api-m.paypal.com', _live_client_id, _live_secret
                )
                _last_amt = _apply_sub_data(_sub_data)
                _live_ok = True
                logger.info(
                    f'PayPal LIVE subscription API fetch OK: sub={_order_id_early}, '
                    f'email={payer_email}, name={payer_name}, '
                    f'amount={_last_amt or "(pending first cycle)"}'
                )
            except Exception as _live_err:
                logger.info(
                    f'PayPal LIVE API returned error for sub {_order_id_early} '
                    f'({type(_live_err).__name__}: {_live_err}) — trying SANDBOX API next'
                )

            # --- Step 2: Try SANDBOX PayPal API (if live failed) ---
            if not _live_ok:
                try:
                    _sb_client_id = os.environ.get('PAYPAL_SANDBOX_CLIENT_ID', '')
                    _sb_secret = os.environ.get('PAYPAL_SANDBOX_SECRET', '')
                    _sub_data = _fetch_paypal_subscription(
                        'https://api-m.sandbox.paypal.com', _sb_client_id, _sb_secret
                    )
                    _last_amt = _apply_sub_data(_sub_data)
                    logger.info(
                        f'PayPal SANDBOX subscription API fetch OK: sub={_order_id_early}, '
                        f'email={payer_email}, name={payer_name}, '
                        f'amount={_last_amt or "(pending first cycle)"}'
                    )
                except Exception as _sb_err:
                    logger.warning(
                        f'PayPal SANDBOX API also failed for sub {_order_id_early}: {_sb_err}'
                    )

                    # --- Step 3: Fall back to page-supplied data ---
                    # The page always sends tier in the payload; map tier -> known price.
                    # payer_email/payer_name are not sent by the sandbox page, so mark
                    # them as "(sandbox-sub)" for identifiability in the log.
                    _tier_key = (data.get('tier') or '').lower()
                    if not data.get('amount') or data.get('amount') in ('0.00', '', None):
                        _fallback_amount = _TIER_PRICES.get(_tier_key, '0.00')
                        data['amount'] = _fallback_amount
                        logger.info(
                            f'PayPal API unavailable — using tier-based amount fallback: '
                            f'tier={_tier_key}, amount={_fallback_amount}'
                        )
                    if not payer_email:
                        payer_email = '(sandbox-sub)'
                    if not payer_name:
                        payer_name = '(sandbox-sub)'
                    logger.info(
                        f'Both PayPal APIs failed for I-* sub — logged with fallback data. '
                        f'tier={_tier_key}, amount={data.get("amount")}'
                    )

        # Log the payment verification
        payment_entry = {
            'type': 'payment_verification',
            'orderId': data.get('orderId'),
            'tier': data.get('tier', 'unknown'),
            'amount': data.get('amount', '0.00'),
            'payerEmail': payer_email,
            'payerName': payer_name,
            'captureId': data.get('captureId', ''),
            'server_timestamp': datetime.now(timezone.utc).isoformat(),
            'client_ip': request.remote_addr,
            'verified': True
        }

        # Write to dedicated payment log
        payment_log = os.path.join(DEFAULT_LOG_DIR, 'purebrain_payments.jsonl')
        try:
            with _file_lock:
                with open(payment_log, 'a') as f:
                    f.write(json.dumps(payment_entry) + '\n')
            logger.info(f'Payment verified: order={data.get("orderId")}, tier={data.get("tier")}, amount={data.get("amount")}, email={payer_email or "(none yet)"}')
        except Exception as e:
            logger.error(f'Failed to write payment log: {e}')
            return jsonify({'error': 'Failed to log payment'}), 500

        # For subscriptions (I- prefix): immediately write subscription ID to clients.db
        # if we have an email. This ensures the hourly PayPal sync can find the customer
        # even before the pay-test onboarding flow completes.
        order_id = data.get('orderId', '')
        if order_id.startswith('I-') and payer_email and '@' in payer_email:
            import sqlite3 as _sqlite3
            _clients_db_path = '/home/jared/purebrain_portal/clients.db'
            try:
                _now = datetime.now(timezone.utc).isoformat()
                _conn = _sqlite3.connect(_clients_db_path, timeout=10)
                _conn.execute('PRAGMA journal_mode = WAL')
                _cur = _conn.cursor()
                _cur.execute(
                    """UPDATE clients SET
                       paypal_subscription_id = CASE
                           WHEN paypal_subscription_id = '' OR paypal_subscription_id IS NULL THEN ?
                           ELSE paypal_subscription_id
                       END,
                       payment_status = CASE
                           WHEN payment_status NOT IN ('subscription_active', 'subscription_cancelled') THEN 'subscription_active'
                           ELSE payment_status
                       END,
                       updated_at = ?
                       WHERE email = ? COLLATE NOCASE""",
                    (order_id, _now, payer_email)
                )
                _updated = _cur.rowcount
                _conn.commit()
                _conn.close()
                if _updated > 0:
                    logger.info(f'Subscription ID {order_id} immediately written to clients.db for {payer_email}')
                else:
                    logger.info(f'Subscription ID {order_id} received for {payer_email} — not in DB yet, PayPal sync will handle')
            except Exception as _db_err:
                logger.warning(f'Could not write subscription ID to clients.db: {_db_err}')

        # Increment spots claimed counter — ONLY for real (non-sandbox, non-test) payments.
        # Sandbox/test orders must NEVER increment the public-facing invitation page counter.
        #
        # Real PayPal order IDs: alphanumeric like "4MA83119W1272721N" (one-time)
        # Real PayPal subscription IDs: "I-XXXX..." format — these ARE real payments.
        #   /live/, /awakened/, /partnered/, /unified/, /insiders/ all use subscription
        #   billing so real customers produce I-* IDs.
        #
        # Sandbox page (pay-test-sandbox-3) sends isSandbox:true in the payload.
        #
        # Filtered patterns:
        #   SANDBOX-TEST* — explicit sandbox test orders from E2E flows
        #   E2E-*         — E2E automation test orders
        #   test-*        — manual test orders
        #   isSandbox:true — flag sent by pay-test-sandbox-3 page
        #
        # NOTE: I-* prefix is NOT filtered — real subscriptions use this format.
        order_id = data.get('orderId', '')
        is_sandbox_payload = bool(data.get('isSandbox', False))
        sandbox_prefixes = ('SANDBOX-TEST', 'E2E-', 'test-')
        # Detect sandbox PayPal emails: "sb-*" prefix OR "@personal.example.com" / "@business.example.com"
        _pe_lower = (payer_email or '').lower().strip()
        is_sandbox_email = (
            _pe_lower.startswith('sb-')
            or _pe_lower.endswith('@personal.example.com')
            or _pe_lower.endswith('@business.example.com')
        )
        # Detect sandbox/test pages by URL
        _page_url_lower = (data.get('pageUrl', data.get('page_url', '')) or '').lower()
        is_sandbox_page = (
            'pay-test-sandbox' in _page_url_lower
            or '/pay-test' in _page_url_lower
        )
        is_sandbox_or_test = (
            is_sandbox_payload
            or any(order_id.startswith(prefix) for prefix in sandbox_prefixes)
            or is_sandbox_email
            or is_sandbox_page
        )
        if is_sandbox_or_test:
            logger.info(f'Spots counter NOT incremented — sandbox/test order filtered out: {order_id} (isSandbox={is_sandbox_payload}, sandbox_email={is_sandbox_email}, sandbox_page={is_sandbox_page})')
        else:
            spots_file = os.path.join(DEFAULT_LOG_DIR, 'spots_state.json')
            try:
                with _file_lock:
                    try:
                        with open(spots_file, 'r') as f:
                            spots_data = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        spots_data = {'spots_claimed': 0, 'spots_total': 25, 'claimed_orders': []}
                    # Dedup: do not increment if this order_id was already recorded
                    existing_order_ids = {r.get('order_id') for r in spots_data.get('claimed_orders', [])}
                    if order_id in existing_order_ids:
                        logger.info(f'Spots counter NOT incremented — duplicate order_id already recorded: {order_id}')
                    else:
                        spots_data['spots_claimed'] = spots_data.get('spots_claimed', 0) + 1
                        order_record = {
                            'order_id': order_id,
                            'tier': data.get('tier', 'unknown'),
                            'payer_email': data.get('payerEmail', ''),
                            'timestamp': payment_entry['server_timestamp']
                        }
                        if 'claimed_orders' not in spots_data:
                            spots_data['claimed_orders'] = []
                        spots_data['claimed_orders'].append(order_record)
                        with open(spots_file, 'w') as f:
                            json.dump(spots_data, f, indent=2)
                        logger.info(f'Spots counter incremented to {spots_data["spots_claimed"]} (real order: {order_id})')
            except Exception as e:
                logger.warning(f'Failed to increment spots counter: {e}')

        # === PRIMARY SEED TRIGGER — fires on PayPal payment ===
        # The naming ceremony conversation is already in purebrain_web_conversations.jsonl
        # keyed by metadata.orderId — look it up so we include AI name + full conversation.

        # Snapshot tier and amount as local variables so the closure captures concrete values.
        _seed_tier   = data.get('tier', 'unknown')
        _seed_amount = data.get('amount', '0.00')
        # 2026-03-26 FIX: Capture the page's chatflow session UUID if sent.
        # This is the UUID the page polls with on /api/magic-link/{uuid},
        # so the seed MUST use this same UUID to ensure Witness stores the
        # magic link under the key the page is actually looking for.
        _page_session_uuid = (data.get('sessionUuid') or data.get('session_uuid') or '').strip()

        # 2026-04-06 FIX: Fallback — extract UUID from PayPal custom_id if sessionUuid
        # not provided directly.  custom_id format: "PB-AWAKENED-<uuid>"
        if not _page_session_uuid:
            _custom_id = (data.get('custom_id') or data.get('customId') or '').strip()
            if _custom_id.startswith('PB-'):
                _cid_parts = _custom_id.split('-', 2)  # ['PB', 'AWAKENED', '<uuid>']
                if len(_cid_parts) >= 3 and len(_cid_parts[2]) > 8:
                    _page_session_uuid = _cid_parts[2]
                    logger.info(f'[payment-seed] Extracted sessionUuid from custom_id: {_page_session_uuid}')

        # 2026-03-28: Store PayPal payer email keyed by session UUID for welcome email
        # dual-address logic. The welcome email fires later (when Witness sends MAGIC LINK).
        # At that point we need both the chatbox email (from Witness) and the PayPal email
        # (from here) to send to both if they differ.
        if _page_session_uuid and payer_email and '@' in payer_email:
            _payer_emails_file = os.path.join(DEFAULT_LOG_DIR, 'payer_emails_by_uuid.json')
            try:
                with _file_lock:
                    try:
                        with open(_payer_emails_file, 'r') as _pef:
                            _payer_lookup = json.load(_pef)
                    except (FileNotFoundError, json.JSONDecodeError):
                        _payer_lookup = {}
                    _payer_lookup[_page_session_uuid] = {
                        'paypal_email': payer_email,
                        'order_id': order_id,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                    }
                    with open(_payer_emails_file, 'w') as _pef:
                        json.dump(_payer_lookup, _pef, indent=2)
                logger.info(f'[payer-email-store] Stored PayPal email {payer_email} for UUID={_page_session_uuid}')
            except Exception as _pe_err:
                logger.warning(f'[payer-email-store] Failed to store payer email: {_pe_err}')

        def _fire_payment_seed(is_test=False):
            try:
                import sys as _sys
                import json as _json
                _tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
                if _tools_dir not in _sys.path:
                    _sys.path.insert(0, _tools_dir)
                from agentmail import AgentMail as _AM

                _client = _AM(api_key=os.environ.get('AGENTMAIL_API_KEY', ''))

                # --- Look up the naming ceremony conversation from JSONL log ---
                _conversation_text = ''
                _ai_name = '(not yet named)'
                # 2026-03-26 FIX: UUID priority chain:
                # 1. Page's chatflow sessionUuid (what the page actually polls with)
                # 2. Conversation session_id from JSONL lookup
                # 3. Fallback: payment-{order_id}
                _session_uuid = _page_session_uuid or f'payment-{order_id}'

                try:
                    _conv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'purebrain_web_conversations.jsonl')
                    if os.path.exists(_conv_path):
                        # 2026-03-28 FIX: 5-strategy conversation lookup.
                        # CONSTITUTIONAL: Never send an unnamed seed when a conversation exists.
                        #
                        # Strategy priority (try each, stop at first match):
                        #   S1. Match by orderId in metadata (strongest)
                        #   S2. Match by sessionUuid (page sends payTestData.sessionUuid)
                        #   S3. Match by payer email in message content
                        #   S4. Most recent conversation on payment page in last 30 min with >5 msgs
                        #   S5. Match by payer first name in AI (assistant) responses
                        #
                        # For each strategy, keep the entry with the most messages.
                        _best_by_order = None
                        _best_by_order_count = 0
                        _best_by_uuid = None
                        _best_by_uuid_count = 0
                        _best_by_email = None
                        _best_by_email_count = 0
                        _best_by_recency = None
                        _best_by_recency_count = 0
                        _best_by_recency_ts = None
                        _best_by_name = None
                        _best_by_name_count = 0

                        _payer_first_name = (payer_name or '').split()[0].lower() if payer_name else ''
                        _payer_email_lower = (payer_email or '').lower().strip()
                        _now_utc = datetime.now(timezone.utc)
                        # Payment page URL patterns for Strategy 4
                        _payment_page_patterns = ['/awakened', '/partnered', '/unified', '/pay-test', '/insiders', '/live']

                        with open(_conv_path, 'r') as _cf:
                            for _line in _cf:
                                _line = _line.strip()
                                if not _line:
                                    continue
                                try:
                                    _entry = _json.loads(_line)
                                    _meta = _entry.get('metadata') or {}
                                    _msgs = _entry.get('messages') or []
                                    _msg_count = len(_msgs)
                                    _entry_order = _meta.get('orderId', '')

                                    # Strategy 1: Match by order ID in metadata
                                    if order_id and _entry_order == order_id:
                                        if _msg_count > _best_by_order_count:
                                            _best_by_order = _entry
                                            _best_by_order_count = _msg_count

                                    # Strategy 2: Match by session_uuid field (top-level or metadata)
                                    if _page_session_uuid:
                                        _entry_suuid = (_entry.get('session_uuid') or '').strip()
                                        _meta_suuid = (_meta.get('sessionUuid') or '').strip()
                                        if (_entry_suuid == _page_session_uuid or _meta_suuid == _page_session_uuid):
                                            if _msg_count > _best_by_uuid_count:
                                                _best_by_uuid = _entry
                                                _best_by_uuid_count = _msg_count

                                    # Strategy 3: Match by payer email appearing in message content
                                    # (customer types their email during the naming ceremony)
                                    if _payer_email_lower and _msg_count >= 3:
                                        for _m in _msgs:
                                            _mc = (_m.get('content') or '').lower()
                                            if _payer_email_lower in _mc:
                                                if _msg_count > _best_by_email_count:
                                                    _best_by_email = _entry
                                                    _best_by_email_count = _msg_count
                                                break

                                    # Strategy 4: Most recent conversation on a payment page,
                                    # within the last 30 minutes, with >5 messages.
                                    # If strategies 1-3 all fail, this catches the case where
                                    # the sessionUuid was empty but someone clearly just had a
                                    # long conversation and then paid.
                                    if _msg_count > 5:
                                        _page_url = (_meta.get('page_url') or '').lower()
                                        _is_payment_page = any(p in _page_url for p in _payment_page_patterns)
                                        if _is_payment_page:
                                            _entry_ts_str = _entry.get('server_timestamp', '')
                                            if _entry_ts_str:
                                                try:
                                                    _entry_ts = datetime.fromisoformat(_entry_ts_str)
                                                    _age_min = (_now_utc - _entry_ts).total_seconds() / 60.0
                                                    if _age_min <= 30:
                                                        if (_best_by_recency_ts is None or _entry_ts > _best_by_recency_ts):
                                                            _best_by_recency = _entry
                                                            _best_by_recency_count = _msg_count
                                                            _best_by_recency_ts = _entry_ts
                                                except (ValueError, TypeError):
                                                    pass

                                    # Strategy 5: Match by payer first name in assistant responses — DISABLED 2026-05-07
                                    #
                                    # Was: search assistant messages for payer first-name substring (>= 3 chars).
                                    # Caused: cross-customer collision when two payers share first name.
                                    # Specifically: 2026-05-07 11:54 UTC, Sheila / Couplify ($499 Partnered) had her
                                    # payment fuzzy-matched to Jay Hutton's "Torque" container via shared "Jay"
                                    # (Whitehurst was the PayPal payer name; Hutton was an unrelated old chat).
                                    #
                                    # Per constitutional rule (feedback_seed_flow_never_deviate.md): AI name MUST
                                    # populate before send. Fuzzy first-name match risks shipping wrong AI name
                                    # while satisfying the populate-rule numerically (Torque) but not semantically.
                                    #
                                    # Replacement: hard-block + Telegram alert + JSONL queue for manual review,
                                    # implemented after the priority chain below. Feature flag
                                    # ALLOW_S5_FUZZY_FALLBACK=true can re-enable this strategy in emergency.
                                    if (
                                        os.environ.get('ALLOW_S5_FUZZY_FALLBACK', 'false').lower() == 'true'
                                        and _payer_first_name and len(_payer_first_name) >= 3 and _msg_count >= 3
                                    ):
                                        for _m in _msgs:
                                            if (_m.get('role') or '') == 'assistant':
                                                _mc = (_m.get('content') or '').lower()
                                                if _payer_first_name in _mc:
                                                    if _msg_count > _best_by_name_count:
                                                        _best_by_name = _entry
                                                        _best_by_name_count = _msg_count
                                                    break

                                except Exception:
                                    continue

                        # Pick the best match using priority chain
                        _best_match = None
                        _match_strategy = 'none'
                        if _best_by_order and _best_by_order_count > 0:
                            _best_match = _best_by_order
                            _match_strategy = f'S1-orderId ({_best_by_order_count} msgs)'
                        elif _best_by_uuid and _best_by_uuid_count > 0:
                            _best_match = _best_by_uuid
                            _match_strategy = f'S2-sessionUuid ({_best_by_uuid_count} msgs)'
                        elif _best_by_email and _best_by_email_count > 0:
                            _best_match = _best_by_email
                            _match_strategy = f'S3-payerEmail ({_best_by_email_count} msgs)'
                        elif _best_by_recency and _best_by_recency_count > 0:
                            _best_match = _best_by_recency
                            _match_strategy = f'S4-recentConv ({_best_by_recency_count} msgs, ts={_best_by_recency_ts})'
                        elif (
                            os.environ.get('ALLOW_S5_FUZZY_FALLBACK', 'false').lower() == 'true'
                            and _best_by_name and _best_by_name_count > 0
                        ):
                            # S5 priority entry only fires when feature flag is set.
                            # Default (flag absent/false): hard-block path below catches the no-match case.
                            _best_match = _best_by_name
                            _match_strategy = f'S5-payerName ({_best_by_name_count} msgs) [FLAG-OVERRIDE]'

                        # Log ALL strategy results for debugging — shows which fired and which missed
                        logger.info(
                            f'[payment-seed] Lookup results for order {order_id}, '
                            f'uuid={_page_session_uuid}, email={payer_email}, name={payer_name}: '
                            f'S1-orderId={_best_by_order_count} msgs, '
                            f'S2-uuid={_best_by_uuid_count} msgs, '
                            f'S3-email={_best_by_email_count} msgs, '
                            f'S4-recent={_best_by_recency_count} msgs, '
                            f'S5-name={_best_by_name_count} msgs | '
                            f'Winner: {_match_strategy}'
                        )

                        if _best_match:
                            _msgs = _best_match.get('messages') or []
                            _ai_name = _best_match.get('aiName') or _ai_name
                            # Also check metadata for ai_name
                            if _ai_name == '(not yet named)':
                                _meta_check = _best_match.get('metadata') or {}
                                _ai_name = _meta_check.get('ai_name') or _meta_check.get('civ_name') or _ai_name
                            # Only override UUID from conversation if page didn't send one
                            if not _page_session_uuid:
                                _session_uuid = _best_match.get('session_id') or _session_uuid

                            # Build plain-text conversation
                            _conv_lines = []
                            for _m in _msgs:
                                _role = (_m.get('role') or 'unknown').upper()
                                _content = (_m.get('content') or '').strip()
                                if _content and not _content.startswith('[The person just clicked'):
                                    _conv_lines.append(f'**{_role}**: {_content}')
                            _conversation_text = '\n\n'.join(_conv_lines)

                            logger.info(f'[payment-seed] Found conversation via {_match_strategy}: {len(_msgs)} messages, AI name: {_ai_name}')
                        else:
                            # HARD-BLOCK PATH (2026-05-07): S1-S4 all returned 0; S5 fuzzy fallback
                            # is disabled by default. Per constitutional seed-flow rule, we will NOT
                            # guess the chat-payment binding via demographics — block, alert, queue.
                            logger.critical(
                                f'[payment-seed] BLOCKED-NO-MATCH: order={order_id} '
                                f'payer_email={payer_email} payer_name={payer_name} amount={_seed_amount} tier={_seed_tier}. '
                                f'S1-S4 empty; S5 fuzzy fallback disabled. Manual review required.'
                            )
                            try:
                                _blocked_record = {
                                    'timestamp': datetime.now(timezone.utc).isoformat(),
                                    'order_id': order_id,
                                    'payer_email': payer_email,
                                    'payer_name': payer_name,
                                    'amount': _seed_amount,
                                    'tier': _seed_tier,
                                    'session_uuid': _page_session_uuid,
                                    'reason': 'S1-S4 all returned 0; S5 fuzzy fallback disabled per constitutional rule',
                                    'requires_action': 'manual review + manual seed dispatch',
                                }
                                _blocked_path = os.path.join(
                                    os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'blocked_seeds.jsonl'
                                )
                                os.makedirs(os.path.dirname(_blocked_path), exist_ok=True)
                                with open(_blocked_path, 'a') as _bf:
                                    _bf.write(_json.dumps(_blocked_record) + '\n')
                            except Exception as _bjerr:
                                logger.error(f'[payment-seed] Failed to append blocked_seeds.jsonl: {_bjerr}')

                            try:
                                _tg_path = os.path.join(
                                    os.path.dirname(os.path.abspath(__file__)), 'tg_send.sh'
                                )
                                _tg_msg = (
                                    f"🚨 SEED BLOCKED: order={order_id} "
                                    f"payer={payer_email} amount=${_seed_amount} tier={_seed_tier}. "
                                    f"S1-S4 all empty; S5 disabled. Manual review required. "
                                    f"See logs/blocked_seeds.jsonl"
                                )
                                subprocess.run(
                                    [_tg_path, _tg_msg],
                                    check=False, timeout=10,
                                )
                            except Exception as _tgerr:
                                logger.error(f'[payment-seed] Telegram alert failed: {_tgerr}')

                            return  # Exit _fire_payment_seed thread — do NOT call Witness/send seed

                except Exception as _conv_err:
                    logger.warning(f'[payment-seed] Conversation lookup failed: {_conv_err}')

                # --- CONSTITUTIONAL GUARD: Block seed if AI name is missing ---
                # Added 2026-04-08 after Matt Keough incident. "It cannot happen again."
                if not _validate_ai_name_for_seed(
                    _ai_name, 'payment-seed',
                    payer_name=payer_name, payer_email=payer_email,
                    order_id=order_id, session_uuid=_session_uuid,
                ):
                    logger.critical(
                        f'[payment-seed] BLOCKED: Refusing to send seed for order {order_id} '
                        f'because ai_name={_ai_name!r}. Seed held for manual review.'
                    )
                    return  # Exit _fire_payment_seed thread — do NOT send

                # --- Build subject and body ---
                _sandbox_prefix = 'THIS IS A SEED TEST FROM JARED OR PURE TECHNOLOGY\n\n' if is_test else ''

                if is_test:
                    _subject = (
                        f'\U0001f9ea TEST SEED: {_ai_name} / {payer_name} \u2014 {_seed_tier} '
                        f'(${_seed_amount}/month)'
                    )
                else:
                    _subject = (
                        f'\U0001f331 SEED: {_ai_name} / {payer_name} \u2014 {_seed_tier} '
                        f'(${_seed_amount}/month)'
                    )

                _ts_now = datetime.now(timezone.utc).isoformat()

                # --- Build rich HTML body (same format as chatbox send-seed) ---
                import html as _html_lib_ps

                def _e_ps(v):
                    return _html_lib_ps.escape(str(v)) if v else ''

                _sb_banner_ps = (
                    '<div style="background:#dc2626;color:#fff;padding:14px 20px;font-weight:bold;'
                    'font-size:16px;border-radius:6px;margin-bottom:16px;text-align:center;'
                    'border:2px solid #fbbf24;">'
                    '\u26a0\ufe0f THIS IS A SANDBOX TEST \u2014 NOT A REAL CUSTOMER \u26a0\ufe0f</div>'
                ) if is_test else ''

                # Build conversation HTML rows from the already-collected _conversation_text
                _conv_rows_html = []
                if _conversation_text:
                    for _conv_line in _conversation_text.split('\n\n'):
                        _conv_line = _conv_line.strip()
                        if not _conv_line:
                            continue
                        if _conv_line.startswith('**ASSISTANT**:'):
                            _role_label = 'ASSISTANT'
                            _content_ps = _conv_line[len('**ASSISTANT**:'):].strip()
                            _rbg = '#1a1a2e'
                            _rclr = '#60a5fa'
                        elif _conv_line.startswith('**USER**:'):
                            _role_label = 'USER'
                            _content_ps = _conv_line[len('**USER**:'):].strip()
                            _rbg = '#0f0f1a'
                            _rclr = '#a3e635'
                        else:
                            _role_label = 'SYSTEM'
                            _content_ps = _conv_line
                            _rbg = '#0a0f1e'
                            _rclr = '#94a3b8'
                        _conv_rows_html.append(
                            '<tr style="background:' + _rbg + ';">'
                            '<td style="padding:6px 10px;color:' + _rclr + ';font-weight:bold;white-space:nowrap;'
                            'width:110px;vertical-align:top;font-size:12px;">' + _role_label + '</td>'
                            '<td style="padding:6px 10px;color:#e2e8f0;font-size:13px;">' + _e_ps(_content_ps) + '</td></tr>'
                        )

                _no_conv_row = (
                    '<tr><td colspan="2" style="color:#94a3b8;padding:8px;">'
                    '(no conversation history \u2014 customer may not have completed naming ceremony before payment)'
                    '</td></tr>'
                )
                _conv_table_ps = (
                    '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-top:8px;">'
                    + (''.join(_conv_rows_html) if _conv_rows_html else _no_conv_row)
                    + '</table>'
                )

                _html_body = (
                    '<!DOCTYPE html><html><head><meta charset="utf-8"></head>'
                    '<body style="margin:0;padding:0;background:#080a12;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;">'
                    '<table width="100%" cellpadding="0" cellspacing="0" style="background:#080a12;padding:24px;"><tr><td>'
                    + _sb_banner_ps
                    + '<div style="background:#1e293b;border-radius:6px;padding:12px 16px;margin-bottom:20px;">'
                      '<span style="color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Session UUID</span><br>'
                      '<span style="color:#f8fafc;font-family:monospace;font-size:13px;">' + _e_ps(_session_uuid) + '</span></div>'
                    + '<h2 style="color:#f8fafc;margin:0 0 16px 0;font-size:20px;font-weight:700;">PureBrain New Customer Seed</h2>'
                    + '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:#0f172a;border-radius:6px;overflow:hidden;margin-bottom:24px;">'
                      '<tr style="background:#1e293b;">'
                      '<td style="padding:10px 14px;color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;width:160px;">Field</td>'
                      '<td style="padding:10px 14px;color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;">Value</td></tr>'
                      '<tr style="border-top:1px solid #1e293b;">'
                      '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Tier</td>'
                      '<td style="padding:10px 14px;color:#f8fafc;font-size:13px;font-weight:600;">' + _e_ps(_seed_tier) + '</td></tr>'
                      '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
                      '<td style="padding:10px 14px;color:#64748b;font-size:13px;">AI Name</td>'
                      '<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">' + _e_ps(_ai_name) + '</td></tr>'
                      '<tr style="border-top:1px solid #1e293b;">'
                      '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Human Name</td>'
                      '<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">' + _e_ps(payer_name) + '</td></tr>'
                      '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
                      '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Email</td>'
                      '<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">' + _e_ps(payer_email) + '</td></tr>'
                      '<tr style="border-top:1px solid #1e293b;">'
                      '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Order ID</td>'
                      '<td style="padding:10px 14px;color:#f8fafc;font-size:13px;font-family:monospace;">' + _e_ps(order_id) + '</td></tr>'
                      '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
                      '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Payment</td>'
                      '<td style="padding:10px 14px;color:#4ade80;font-size:13px;font-weight:600;">$' + _e_ps(_seed_amount) + ' confirmed via PayPal subscription</td></tr>'
                      '<tr style="border-top:1px solid #1e293b;">'
                      '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Trigger</td>'
                      '<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">PayPal payment verification</td></tr>'
                      '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
                      '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Timestamp</td>'
                      '<td style="padding:10px 14px;color:#f8fafc;font-size:13px;font-family:monospace;">' + _e_ps(_ts_now) + '</td></tr>'
                      '</table>'
                    + '<h3 style="color:#f8fafc;margin:0 0 8px 0;font-size:15px;font-weight:600;">Full Conversation</h3>'
                      '<p style="color:#64748b;font-size:12px;margin:0 0 8px 0;">Complete pre-purchase naming conversation</p>'
                    + _conv_table_ps
                    + '</td></tr></table></body></html>'
                )

                # --- Plain text (.md) body with full conversation ---
                _no_conv_text = '(No conversation found \u2014 customer may not have completed the chatbox naming ceremony before payment)'
                _md_body = (
                    f'{_sandbox_prefix}'
                    f'# New Customer Seed \u2014 {_ai_name} / {payer_name}\n\n'
                    f'**UUID**: {_session_uuid}\n'
                    f'**Tier**: {_seed_tier} (${_seed_amount}/month)\n'
                    f'**AI Name**: {_ai_name}\n'
                    f'**Human Name**: {payer_name}\n'
                    f'**Email**: {payer_email}\n'
                    f'**Order ID**: {order_id}\n'
                    f'**Payment**: ${_seed_amount} confirmed via PayPal subscription\n'
                    f'**Trigger**: PayPal payment verification\n'
                    f'**Date**: {_ts_now}\n'
                    f'\n---\n\n'
                    f'## Full Conversation\n\n'
                    + (_conversation_text if _conversation_text else _no_conv_text)
                    + '\n'
                )

                _client.inboxes.messages.send(
                    inbox_id='aether-aiciv@agentmail.to',
                    to=['aiciv-seed-inbox@agentmail.to'],
                    cc=['jared@puretechnology.nyc', 'aether-aiciv@agentmail.to', 'purebrain@puremarketing.ai'],
                    subject=_subject,
                    text=_md_body,
                    html=_html_body,
                )
                # Mark this order as seeded so chatbox /api/send-seed does not double-fire
                if order_id:
                    _seeds_fired_for_orders.add(order_id)

                logger.info(f'[payment-seed] Seed fired for {order_id} ({payer_name}, {payer_email}, AI: {_ai_name}, test={is_test})')

            except Exception as _exc:
                logger.error(f'[payment-seed] Failed to fire seed for {order_id}: {_exc}')

        # Fire for all orders: real orders get normal seed; sandbox/test get a marked test seed
        threading.Thread(target=_fire_payment_seed, kwargs={'is_test': is_sandbox_or_test}, daemon=True).start()

        # Portal notification (AI name resolved inside background thread above)
        _seed_msg = f'\n🌱 [SEED FIRED] {payer_name} — seed sent to Witness (PayPal trigger)'
        try:
            _sf = '/home/jared/projects/AI-CIV/aether/.current_session'
            with open(_sf) as _f:
                _sn = _f.read().strip()
            subprocess.Popen(
                ['tmux', 'send-keys', '-t', _sn, _seed_msg, ''],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

                # --- Payment notifications (tmux portal + Telegram, background threads) ---
        _pay_name   = payer_name or '(unknown)'
        _pay_email  = payer_email or '(unknown)'
        _pay_amount = data.get('amount', '0.00')
        _pay_tier   = data.get('tier', 'unknown')
        _pay_page   = data.get('pageUrl', data.get('page_url', ''))
        _pay_sub_id = data.get('orderId', '')
        _pay_tmux_msg = (
            f'\n\U0001f525 [NEW PAYMENT] {_pay_name} just paid ${_pay_amount} ({_pay_tier})'
            + (f' on {_pay_page}' if _pay_page else '')
            + f'\n   Subscription: {_pay_sub_id}'
            + f'\n   Email: {_pay_email}'
        )
        _pay_tg_msg = (
            f'\U0001f525 NEW PAYMENT\n'
            f'{_pay_name} just paid ${_pay_amount} ({_pay_tier})'
            + (f'\nPage: {_pay_page}' if _pay_page else '')
            + f'\nSubscription: {_pay_sub_id}'
            + f'\nEmail: {_pay_email}'
        )

        def _payment_notify_portal(_msg=_pay_tmux_msg, _oid=_pay_sub_id):
            try:
                _sf = '/home/jared/projects/AI-CIV/aether/.current_session'
                with open(_sf) as _f:
                    _sn = _f.read().strip()
                subprocess.Popen(
                    ['tmux', 'send-keys', '-t', _sn, _msg, ''],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.info(f'Payment portal injection sent for order={_oid}')
            except Exception as _exc:
                logger.warning(f'Payment portal injection failed: {_exc}')

        def _payment_notify_telegram(_msg=_pay_tg_msg, _oid=_pay_sub_id):
            _send_telegram_notification(_msg)
            logger.info(f'Payment Telegram notification sent for order={_oid}')

        for _tgt in (_payment_notify_portal, _payment_notify_telegram):
            threading.Thread(target=_tgt, daemon=True).start()

        # === REFERRAL COMMISSION RECORDING ===
        # If this payment is from a referred customer, record the 5% commission
        # in the portal's referral system. The portal endpoint looks up the payer
        # email in the referrals table to find if they were referred, so we don't
        # need the referral code here — just the payer email.
        # Skip for sandbox/test orders to avoid polluting commission data.
        if payer_email and '@' in payer_email and not is_sandbox_or_test:
            _comm_email  = payer_email
            _comm_order  = data.get('orderId', '')
            _comm_tier   = data.get('tier', 'unknown')
            try:
                _comm_amount = float(data.get('amount', 0))
            except (TypeError, ValueError):
                _comm_amount = 0.0

            def _record_referral_commission():
                try:
                    import requests as _req
                    _portal_token = open('/home/jared/purebrain_portal/.portal-token').read().strip()
                    _resp = _req.post(
                        'http://127.0.0.1:8097/api/referral/commission',
                        headers={
                            'Authorization': f'Bearer {_portal_token}',
                            'Content-Type': 'application/json',
                        },
                        json={
                            'payer_email': _comm_email,
                            'order_id': _comm_order,
                            'amount': _comm_amount,
                            'tier': _comm_tier,
                        },
                        timeout=5,
                    )
                    _result = _resp.json() if _resp.status_code == 200 else _resp.text
                    if _resp.status_code == 200:
                        logger.info(
                            f'[referral] Commission call OK for order={_comm_order}, '
                            f'payer={_comm_email}: {_result}'
                        )
                    else:
                        logger.warning(
                            f'[referral] Commission call returned {_resp.status_code} '
                            f'for order={_comm_order}: {_result}'
                        )
                except Exception as _e:
                    logger.error(f'[referral] Failed to record commission for order={_comm_order}: {_e}')

            threading.Thread(target=_record_referral_commission, daemon=True).start()

        return jsonify({
            'success': True,
            'verified': True,
            'orderId': data.get('orderId'),
            'server_timestamp': payment_entry['server_timestamp']
        })

    @app.route('/api/magic-link/<path:session_uuid>', methods=['GET', 'OPTIONS'])
    def get_magic_link(session_uuid):
        """
        Poll endpoint for post-payment chatbox — waits for Witness to send magic link.

        The post-payment flow generates a session UUID and polls this endpoint every
        few seconds. When agentmail_monitor.py receives the magic link email from
        Witness, it stores the entry in .magic-links.json keyed by that UUID.
        This endpoint reads that file and returns the result.

        GET /api/magic-link/{uuid}?email={email}
        Returns:
          {"status": "pending"}                        — not yet available
          {"status": "ready", "magic_link": "https://..."} — ready to use
        """
        if request.method == 'OPTIONS':
            return '', 204

        import json as _json

        magic_links_file = '/home/jared/projects/AI-CIV/aether/.magic-links.json'
        email_param = (request.args.get('email') or '').strip().lower()

        try:
            try:
                with open(magic_links_file, 'r') as _f:
                    links = _json.load(_f)
            except (FileNotFoundError, _json.JSONDecodeError):
                links = {}

            # Primary lookup: by UUID key
            entry = links.get(session_uuid)

            # Fallback 1: check email:{email} key directly
            if not entry and email_param:
                entry = links.get(f'email:{email_param}')

            # Fallback 2: scan all entries for matching human_email
            if not entry and email_param:
                for _key, _val in links.items():
                    if isinstance(_val, dict):
                        stored_email = (_val.get('human_email') or '').strip().lower()
                        if stored_email == email_param:
                            entry = _val
                            break

            # Fallback 3: check if there's a recent entry for same sandbox PayPal email
            # (handles case where page polls with chat email but link stored under PayPal email)
            if not entry and email_param:
                # Look up client in clients.db to find PayPal email
                try:
                    import sqlite3
                    _db = sqlite3.connect('/home/jared/purebrain_portal/clients.db')
                    _row = _db.execute(
                        'SELECT email FROM clients WHERE email = ? OR goes_by = ? ORDER BY last_active_at DESC LIMIT 1',
                        (email_param, email_param)
                    ).fetchone()
                    if not _row:
                        # Try matching by subscription in the pay-test flow
                        _row2 = _db.execute(
                            'SELECT email FROM clients WHERE last_active_at > datetime("now", "-30 minutes") ORDER BY last_active_at DESC LIMIT 1'
                        ).fetchone()
                        if _row2:
                            _alt_email = (_row2[0] or '').strip().lower()
                            if _alt_email and _alt_email != email_param:
                                _alt_entry = links.get(f'email:{_alt_email}')
                                if _alt_entry:
                                    entry = _alt_entry
                                    logger.info(f'Magic link found via alt email lookup: {email_param} -> {_alt_email}')
                    _db.close()
                except Exception as _e:
                    logger.warning(f'Magic link alt email lookup failed: {_e}')

            if entry and entry.get('status') == 'ready' and entry.get('magic_link'):
                logger.info(
                    f'Magic link served for UUID={session_uuid}, email={email_param}: {entry["magic_link"]}'
                )
                return jsonify({
                    'status': 'ready',
                    'magic_link': entry['magic_link'],
                    'ai_name': entry.get('ai_name', ''),
                    'human_name': entry.get('human_name', ''),
                })
            else:
                return jsonify({'status': 'pending'})

        except Exception as _e:
            logger.error(f'Magic link lookup error for UUID={session_uuid}: {_e}')
            return jsonify({'status': 'pending'})

    # === 2026-03-26: Pipeline Health Check ===
    @app.route('/api/pipeline-health', methods=['GET', 'OPTIONS'])
    def pipeline_health():
        """
        Health check for the seed -> magic link pipeline.
        Returns status of all pipeline components.
        """
        if request.method == 'OPTIONS':
            return '', 204

        import subprocess as _sub
        import json as _json_h

        health = {
            'log_server': 'running',
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        # Check agentmail_monitor process
        try:
            result = _sub.run(
                ['pgrep', '-f', 'agentmail_monitor'],
                capture_output=True, text=True, timeout=5
            )
            health['agentmail_monitor'] = 'running' if result.returncode == 0 else 'NOT RUNNING'
        except Exception:
            health['agentmail_monitor'] = 'check_failed'

        # Last seed timestamp from seed_sent_uuids.json
        try:
            _seed_file = os.path.join(DEFAULT_LOG_DIR, 'seed_sent_uuids.json')
            if os.path.exists(_seed_file):
                _mtime = os.path.getmtime(_seed_file)
                health['last_seed_file_modified'] = datetime.fromtimestamp(_mtime, tz=timezone.utc).isoformat()
                with open(_seed_file, 'r') as _f:
                    _uuids = _json_h.load(_f)
                health['total_seeds_fired'] = len(_uuids) if isinstance(_uuids, list) else 0
            else:
                health['last_seed_file_modified'] = None
                health['total_seeds_fired'] = 0
        except Exception as _e:
            health['seed_file_error'] = str(_e)

        # Last magic link timestamp from .magic-links.json
        try:
            _ml_file = '/home/jared/projects/AI-CIV/aether/.magic-links.json'
            if os.path.exists(_ml_file):
                _mtime = os.path.getmtime(_ml_file)
                health['last_magic_link_file_modified'] = datetime.fromtimestamp(_mtime, tz=timezone.utc).isoformat()
                with open(_ml_file, 'r') as _f:
                    _links = _json_h.load(_f)
                health['total_magic_links'] = len(_links)
                # Check for recent entries (last hour)
                _one_hour_ago = (datetime.now(timezone.utc).timestamp()) - 3600
                _recent = 0
                for _k, _v in _links.items():
                    if isinstance(_v, dict) and _v.get('received_at'):
                        try:
                            _rat = datetime.fromisoformat(_v['received_at'].replace('Z', '+00:00'))
                            if _rat.timestamp() > _one_hour_ago:
                                _recent += 1
                        except Exception:
                            pass
                health['magic_links_last_hour'] = _recent
            else:
                health['last_magic_link_file_modified'] = None
                health['total_magic_links'] = 0
        except Exception as _e:
            health['magic_link_file_error'] = str(_e)

        # Overall status
        if health.get('agentmail_monitor') == 'running':
            health['pipeline_status'] = 'healthy'
        else:
            health['pipeline_status'] = 'degraded'

        resp = jsonify(health)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    @app.route('/api/spots-status', methods=['GET', 'OPTIONS'])
    def spots_status():
        """
        Return current spots claimed status for invitation page.
        Returns: {"spots_claimed": N, "spots_total": 25}
        """
        if request.method == 'OPTIONS':
            return '', 204

        spots_file = os.path.join(DEFAULT_LOG_DIR, 'spots_state.json')
        try:
            with _file_lock:
                try:
                    with open(spots_file, 'r') as f:
                        spots_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    spots_data = {'spots_claimed': 3, 'spots_total': 25}
            return jsonify({
                'spots_claimed': spots_data.get('spots_claimed', 3),
                'spots_total': spots_data.get('spots_total', 25)
            })
        except Exception as e:
            logger.error(f'Failed to read spots status: {e}')
            return jsonify({'spots_claimed': 3, 'spots_total': 25})

    @app.route('/api/log-pay-test', methods=['POST', 'OPTIONS'])
    def log_pay_test():
        """
        Log pay-test flow completion data.
        Called after the full post-payment questionnaire + behind-the-curtain flow.

        Expected JSON payload:
        {
            "tier": "Awakened|Bonded|Partnered",
            "orderId": "PAYPAL-ORDER-ID",
            "aiName": "Name chosen by user",
            "name": "User's name",
            "email": "user@email.com",
            "company": "Company name",
            "role": "User's role",
            "primaryGoal": "User's primary goal",
            "telegramBotToken": "bot token if provided",
            "claudeMaxStatus": "connected|skipped",
            "flowCompleted": true
        }
        """
        if request.method == 'OPTIONS':
            return '', 204

        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({'error': 'Invalid JSON'}), 400

        if not data:
            return jsonify({'error': 'Empty payload'}), 400

        # Build log entry
        pay_test_entry = {
            'type': 'pay_test_completion',
            'tier': data.get('tier', 'unknown'),
            'orderId': data.get('orderId', ''),
            'aiName': data.get('aiName', ''),
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'company': data.get('company', ''),
            'role': data.get('role', ''),
            'primaryGoal': data.get('primaryGoal', ''),
            'telegramBotToken': data.get('telegramBotToken', ''),
            'claudeMaxStatus': data.get('claudeMaxStatus', ''),
            'flowCompleted': data.get('flowCompleted', False),
            'server_timestamp': datetime.now(timezone.utc).isoformat(),
            'client_ip': request.remote_addr
        }

        # Write to dedicated pay-test log
        pay_test_log = os.path.join(DEFAULT_LOG_DIR, 'purebrain_pay_test.jsonl')
        try:
            with _file_lock:
                with open(pay_test_log, 'a') as f:
                    f.write(json.dumps(pay_test_entry) + '\n')
            logger.info(f'Pay-test logged: tier={data.get("tier")}, aiName={data.get("aiName")}, email={data.get("email")}')
        except Exception as e:
            logger.error(f'Failed to write pay-test log: {e}')
            return jsonify({'error': 'Failed to log pay-test data'}), 500

        # Also forward to Telegram for immediate notification
        try:
            tg_msg = (
                f"🎉 NEW PAY-TEST COMPLETION!\n"
                f"Tier: {data.get('tier', 'unknown')}\n"
                f"AI Name: {data.get('aiName', 'N/A')}\n"
                f"Name: {data.get('name', 'N/A')}\n"
                f"Email: {data.get('email', 'N/A')}\n"
                f"Company: {data.get('company', 'N/A')}\n"
                f"Order: {data.get('orderId', 'N/A')}"
            )
            tg_thread = threading.Thread(
                target=_send_telegram_notification,
                args=(tg_msg,),
                daemon=True
            )
            tg_thread.start()
        except Exception:
            pass

        # If pay-test has both email and a subscription ID, immediately write to clients.db.
        # This links the I- subscription ID to the client record when they provide their email
        # during onboarding.
        pt_email = (data.get('email') or '').strip().lower()
        pt_order = (data.get('orderId') or '').strip()
        if pt_order.startswith('I-') and pt_email and '@' in pt_email:
            import sqlite3 as _sqlite3
            _clients_db_path = '/home/jared/purebrain_portal/clients.db'
            try:
                _now_pt = datetime.now(timezone.utc).isoformat()
                _conn_pt = _sqlite3.connect(_clients_db_path, timeout=10)
                _conn_pt.execute('PRAGMA journal_mode = WAL')
                _cur_pt = _conn_pt.cursor()
                _cur_pt.execute(
                    """UPDATE clients SET
                       paypal_subscription_id = CASE
                           WHEN paypal_subscription_id = '' OR paypal_subscription_id IS NULL THEN ?
                           ELSE paypal_subscription_id
                       END,
                       payment_status = CASE
                           WHEN payment_status NOT IN ('subscription_active', 'subscription_cancelled') THEN 'subscription_active'
                           ELSE payment_status
                       END,
                       updated_at = ?
                       WHERE email = ? COLLATE NOCASE""",
                    (pt_order, _now_pt, pt_email)
                )
                _updated_pt = _cur_pt.rowcount
                _conn_pt.commit()
                _conn_pt.close()
                if _updated_pt > 0:
                    logger.info(f'[pay-test] Subscription ID {pt_order} linked to client {pt_email} via onboarding flow')
            except Exception as _db_err_pt:
                logger.warning(f'[pay-test] Could not link subscription ID to clients.db: {_db_err_pt}')

        return jsonify({
            'success': True,
            'logged': True,
            'server_timestamp': pay_test_entry['server_timestamp']
        })

    @app.route('/api/stats', methods=['GET'])
    def stats():
        """Return conversation statistics."""
        log_file = app.config['LOG_FILE']

        # Count conversations
        conversation_count = 0
        file_size_bytes = 0

        if os.path.exists(log_file):
            file_size_bytes = os.path.getsize(log_file)
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            conversation_count += 1
            except Exception as e:
                logger.error(f'Error reading stats: {e}')

        logger.info(f'Stats requested: {conversation_count} conversations')

        return jsonify({
            'conversation_count': conversation_count,
            'file_size_bytes': file_size_bytes,
            'log_file': log_file,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })


    @app.route('/api/webhook-subscribers/health', methods=['GET'])
    def webhook_subscribers_health():
        """
        Return delivery health for all configured webhook subscribers.

        Auth: X-Admin-Token header, constant-time compared against env
        ADMIN_TOKEN. If ADMIN_TOKEN is unset, endpoint returns 503.
        """
        import hmac as _hmac
        from pathlib import Path as _Path

        admin_token = os.getenv('ADMIN_TOKEN', '')
        if not admin_token:
            return jsonify({
                'error': 'ADMIN_TOKEN not configured on server',
            }), 503

        provided = request.headers.get('X-Admin-Token', '')
        if not provided or not _hmac.compare_digest(provided, admin_token):
            return jsonify({'error': 'unauthorized'}), 401

        try:
            # Lazy import to avoid hard dep at server startup
            import sys as _sys
            tools_dir = str(_Path(__file__).parent)
            if tools_dir not in _sys.path:
                _sys.path.insert(0, tools_dir)
            from webhook_firehose import WebhookFirehose  # noqa: WPS433

            root = _Path(__file__).parent.parent
            config_path = root / 'config' / 'payment_webhook_subscribers.json'
            delivery_log = root / 'logs' / 'payment_webhook_delivery.jsonl'
            dead_letter = root / 'data' / 'failed_webhook_events.jsonl'

            if not config_path.exists():
                return jsonify({'subscribers': []}), 200

            with open(config_path) as f:
                cfg = json.load(f)

            fh = WebhookFirehose(
                config_path=config_path,
                delivery_log_path=delivery_log,
                dead_letter_path=dead_letter,
            )

            out = []
            for sub in cfg.get('subscribers', []) or []:
                name = sub.get('name', 'unknown')
                stats = fh.get_stats(name)
                out.append({
                    'name': name,
                    'enabled': bool(sub.get('enabled', False)),
                    'success_rate': stats['success_rate'],
                    'last_delivery': stats['last_delivery_ts'],
                    'last_failure': stats['last_failure_ts'],
                    'retry_queue_depth': stats['retry_queue_depth'],
                    'total_sent': stats['total_sent'],
                    'total_failed': stats['total_failed'],
                })

            return jsonify({'subscribers': out}), 200
        except Exception as e:
            logger.error(f'webhook-subscribers/health error: {e}')
            return jsonify({'error': str(e)}), 500


    @app.route('/api/governance/challenge', methods=['POST', 'OPTIONS'])
    def governance_challenge():
        """
        Receive a governance challenge submission from purebrain.ai/governance/.

        Expected JSON payload:
        {
            "name": "Jane Smith",
            "title": "CTO",
            "company": "Acme Corp",
            "industry": "Healthcare",
            "challenge": "How does the system handle...",
            "email": "jane@acme.com"
        }

        Saves to logs/governance_challenges.jsonl and sends AgentMail
        notification to aethergottaeat@agentmail.to.
        """
        if request.method == 'OPTIONS':
            return '', 204

        if not request.is_json:
            return jsonify({'ok': False, 'error': 'Content-Type must be application/json'}), 400

        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({'ok': False, 'error': 'Invalid JSON'}), 400

        if not data:
            return jsonify({'ok': False, 'error': 'Empty payload'}), 400

        challenge_text = (data.get('challenge') or '').strip()
        email = (data.get('email') or '').strip()

        if not challenge_text or not email:
            return jsonify({'ok': False, 'error': 'challenge and email are required'}), 400

        # Build log entry
        entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'name': (data.get('name') or '').strip(),
            'title': (data.get('title') or '').strip(),
            'company': (data.get('company') or '').strip(),
            'industry': (data.get('industry') or '').strip(),
            'challenge': challenge_text,
            'email': email,
            'client_ip': request.remote_addr,
        }

        # Write to JSONL log
        gov_log_file = os.path.join(DEFAULT_LOG_DIR, 'governance_challenges.jsonl')
        try:
            with _file_lock:
                with open(gov_log_file, 'a') as f:
                    f.write(json.dumps(entry) + '\n')
            logger.info(f'Governance challenge logged: id={entry["id"]} from={email}')
        except Exception as e:
            logger.error(f'Failed to write governance challenge log: {e}')
            return jsonify({'ok': False, 'error': 'Failed to save submission'}), 500

        # Send AgentMail notification to Aether (non-blocking background thread)
        def _notify_agentmail():
            try:
                import sys
                tools_dir = os.path.dirname(os.path.abspath(__file__))
                if tools_dir not in sys.path:
                    sys.path.insert(0, tools_dir)
                from send_agentmail import send_agentmail
                subject = f'[Governance Challenge] {entry["name"] or email} — {entry["company"] or "Unknown Co"}'
                body = (
                    f'New governance challenge submitted via purebrain.ai/governance/\n\n'
                    f'ID: {entry["id"]}\n'
                    f'From: {entry["name"]} ({entry["title"]}) at {entry["company"]}\n'
                    f'Industry: {entry["industry"]}\n'
                    f'Reply-to: {entry["email"]}\n\n'
                    f'CHALLENGE:\n{entry["challenge"]}\n\n'
                    f'ACTION REQUIRED: Review and respond to {entry["email"]} within 24 hours.\n'
                    f'Forward to Parallax and other AIs as appropriate.\n'
                    f'Logged to: logs/governance_challenges.jsonl\n'
                )
                send_agentmail(
                    to='aethergottaeat@agentmail.to',
                    subject=subject,
                    text=body,
                )
                logger.info(f'AgentMail notification sent for governance challenge id={entry["id"]}')
            except Exception as exc:
                logger.warning(f'AgentMail notify failed for governance challenge: {exc}')

        notify_thread = threading.Thread(target=_notify_agentmail, daemon=True)
        notify_thread.start()

        return jsonify({'ok': True, 'id': entry['id']})


    @app.route('/api/investor-inquiry', methods=['POST', 'OPTIONS'])
    def investor_inquiry():
        """
        Receive an investor inquiry (Request More Info or Schedule a Call)
        from the investors-v8 page.

        Expected JSON payload:
        {
            "type": "request_info" | "schedule_call",
            "name": "Jane Smith",
            "email": "jane@acme.com",
            "company": "Acme Corp",
            "phone": "+1-555-0100",          (optional)
            "preferred_time": "Mon 10am ET", (schedule_call only, optional)
            "message": "I'd like to know..."
        }

        Saves to logs/investor_inquiries.jsonl and sends AgentMail
        notification to aethergottaeat@agentmail.to.
        """
        if request.method == 'OPTIONS':
            resp = make_response('', 204)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return resp

        if not request.is_json:
            return jsonify({'ok': False, 'error': 'Content-Type must be application/json'}), 400

        try:
            data = request.get_json()
        except Exception:
            return jsonify({'ok': False, 'error': 'Invalid JSON'}), 400

        if not data:
            return jsonify({'ok': False, 'error': 'Empty payload'}), 400

        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        company = (data.get('company') or '').strip()
        phone = (data.get('phone') or '').strip()
        inquiry_type = (data.get('type') or 'request_info').strip()
        preferred_time = (data.get('preferred_time') or '').strip()
        message = (data.get('message') or '').strip()

        if not name or not email:
            return jsonify({'ok': False, 'error': 'name and email are required'}), 400

        # Build log entry
        entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': inquiry_type,
            'name': name,
            'email': email,
            'company': company,
            'phone': phone,
            'preferred_time': preferred_time,
            'message': message,
            'client_ip': request.remote_addr,
        }

        # Write to JSONL log
        inquiry_log_file = os.path.join(DEFAULT_LOG_DIR, 'investor_inquiries.jsonl')
        try:
            with _file_lock:
                with open(inquiry_log_file, 'a') as f:
                    f.write(json.dumps(entry) + '\n')
            logger.info(
                f'Investor inquiry logged: id={entry["id"]} type={inquiry_type} from={email}'
            )
        except Exception as e:
            logger.error(f'Failed to write investor inquiry log: {e}')
            return jsonify({'ok': False, 'error': 'Failed to save submission'}), 500

        # Build shared notification content (used by all 4 channels below)
        type_label = (
            'Schedule a Call' if inquiry_type == 'schedule_call' else 'Request More Info'
        )
        _email_subject = (
            f'INVESTOR INQUIRY: {name} from {company or "unknown company"} — {type_label}'
        )
        _body_lines = [
            'New investor inquiry via investors-v8 page',
            '',
            f'ID: {entry["id"]}',
            f'Type: {type_label}',
            f'Name: {name}',
            f'Email: {email}',
            f'Company: {company or "(not provided)"}',
            f'Phone: {phone or "(not provided)"}',
        ]
        if inquiry_type == 'schedule_call' and preferred_time:
            _body_lines.append(f'Preferred Time: {preferred_time}')
        _body_lines += [
            '',
            'MESSAGE:',
            message or '(no message)',
            '',
            f'ACTION REQUIRED: Respond to {email} within 24 hours.',
            'Logged to: logs/investor_inquiries.jsonl',
        ]
        _body_text = '\n'.join(_body_lines)

        # 1. AgentMail notification -> aethergottaeat@agentmail.to
        def _notify_agentmail():
            try:
                import sys
                tools_dir = os.path.dirname(os.path.abspath(__file__))
                if tools_dir not in sys.path:
                    sys.path.insert(0, tools_dir)
                from send_agentmail import send_agentmail
                send_agentmail(
                    to='aethergottaeat@agentmail.to',
                    subject=_email_subject,
                    text=_body_text,
                )
                logger.info(
                    f'AgentMail notification sent for investor inquiry id={entry["id"]}'
                )
            except Exception as exc:
                logger.warning(f'AgentMail notify failed for investor inquiry: {exc}')

        # 2. Google SMTP email -> jared@puretechnology.nyc (cc: purebrain@puremarketing.ai)
        def _notify_email():
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                gmail_user = os.environ.get('GMAIL_USERNAME', 'purebrain@puremarketing.ai')
                gmail_pass = os.environ.get('GOOGLE_APP_PASSWORD', '')
                if not gmail_pass:
                    logger.warning('GOOGLE_APP_PASSWORD not set -- skipping email notification')
                    return
                msg = MIMEMultipart()
                msg['From'] = gmail_user
                msg['To'] = 'jared@puretechnology.nyc'
                msg['Cc'] = 'purebrain@puremarketing.ai'
                msg['Subject'] = _email_subject
                msg.attach(MIMEText(_body_text, 'plain'))
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(gmail_user, gmail_pass)
                    server.sendmail(
                        gmail_user,
                        ['jared@puretechnology.nyc', 'purebrain@puremarketing.ai'],
                        msg.as_string(),
                    )
                logger.info(f'Email notification sent for investor inquiry id={entry["id"]}')
            except Exception as exc:
                logger.warning(f'Email notify failed for investor inquiry: {exc}')

        # 3. Telegram instant notification -> Jared
        def _notify_telegram():
            tg_lines = [
                'INVESTOR INQUIRY',
                '',
                f'Type: {type_label}',
                f'Name: {name}',
                f'Email: {email}',
                f'Company: {company or "(not provided)"}',
                f'Phone: {phone or "(not provided)"}',
            ]
            if inquiry_type == 'schedule_call' and preferred_time:
                tg_lines.append(f'Preferred Time: {preferred_time}')
            short_msg = (message[:300] + '...') if len(message) > 300 else (message or '(none)')
            tg_lines += [
                '',
                f'Message: {short_msg}',
                '',
                f'ACTION: Respond to {email} within 24 hours.',
            ]
            _send_telegram_notification('\n'.join(tg_lines))
            logger.info(f'Telegram notification sent for investor inquiry id={entry["id"]}')

        # 4. Portal summary via tmux injection -> visible in portal session
        def _notify_portal():
            try:
                session_file = '/home/jared/projects/AI-CIV/aether/.current_session'
                try:
                    with open(session_file) as sf:
                        session_name = sf.read().strip()
                except Exception:
                    session_name = 'aether'
                portal_msg = (
                    f'[INVESTOR INQUIRY] {name} ({email}) from {company or "unknown"}'
                    f' -- {type_label}: {message[:200]}'
                )
                subprocess.Popen(
                    ['tmux', 'send-keys', '-t', session_name, f'\n{portal_msg}\n', 'Enter'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.info(f'Portal injection sent for investor inquiry id={entry["id"]}')
            except Exception as exc:
                logger.warning(f'Portal injection failed for investor inquiry: {exc}')

        # Fire all 4 notification channels in parallel background threads
        for _target in (_notify_agentmail, _notify_email, _notify_telegram, _notify_portal):
            threading.Thread(target=_target, daemon=True).start()

        resp = jsonify({'ok': True, 'id': entry['id']})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    # -------------------------------------------------------------------------
    # /api/send-seed  (Step 3 of onboarding spec)
    # Called once per customer, immediately after email is obtained.
    # FROM: aether-aiciv@agentmail.to (onboarding inbox)
    # TO:   aiciv-seed-inbox@agentmail.to
    # -------------------------------------------------------------------------
    @app.route('/api/send-seed', methods=['POST', 'OPTIONS'])
    def send_seed():
        """
        Fire the SEED email for a new customer after their email is collected.

        Expected JSON payload (accepts both snake_case and camelCase):
        {
            "session_uuid":  "...",     // or "sessionUuid"
            "ai_name":       "...",     // or "aiName"
            "human_name":    "...",     // or "humanName"
            "human_email":   "...",     // or "humanEmail"
            "tier":          "Awakened|Partnered|Unified",
            "order_id":      "I-...",   // or "orderId"
            "is_sandbox":    false,     // or "isSandbox"
            "conversation":  [ {"role": "assistant"|"user", "content": "..."} ]
        }
        """
        if request.method == 'OPTIONS':
            resp = make_response('', 204)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return resp

        if not request.is_json:
            resp = jsonify({'ok': False, 'error': 'Content-Type must be application/json'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        try:
            data = request.get_json()
        except Exception:
            resp = jsonify({'ok': False, 'error': 'Invalid JSON'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        # Accept both snake_case and camelCase for consistency with /api/verify-payment
        session_uuid = (data.get('session_uuid') or data.get('sessionUuid') or '').strip()
        ai_name      = (data.get('ai_name') or data.get('aiName') or '').strip()
        human_name   = (data.get('human_name') or data.get('humanName') or '').strip()
        human_email  = (data.get('human_email') or data.get('humanEmail') or '').strip()
        tier         = (data.get('tier') or 'unknown').strip()
        order_id     = (data.get('order_id') or data.get('orderId') or '').strip()
        is_sandbox   = bool(data.get('is_sandbox', data.get('isSandbox', False)))
        conversation = data.get('conversation') or []

        if not session_uuid or not human_email:
            resp = jsonify({'ok': False, 'error': 'session_uuid and human_email are required'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        # --- CONSTITUTIONAL GUARD: Block seed if AI name is missing ---
        # Added 2026-04-08 after Matt Keough incident. "It cannot happen again."
        if not _validate_ai_name_for_seed(
            ai_name, 'send-seed',
            human_name=human_name, human_email=human_email,
            session_uuid=session_uuid, order_id=order_id,
        ):
            logger.critical(
                f'[send-seed] BLOCKED: Refusing to send seed for UUID={session_uuid} '
                f'because ai_name={ai_name!r}. Seed held for manual review.'
            )
            resp = jsonify({
                'ok': False,
                'error': 'ai_name is required — seed blocked to prevent sending without AI name',
                'held': True,
            })
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 422

        # --- Idempotency guard: never send a seed twice for the same session_uuid ---
        seed_state_file = os.path.join(DEFAULT_LOG_DIR, 'seed_sent_uuids.json')
        with _file_lock:
            try:
                try:
                    with open(seed_state_file, 'r') as _f:
                        sent_uuids = json.load(_f)
                except (FileNotFoundError, json.JSONDecodeError):
                    sent_uuids = []

                if session_uuid in sent_uuids:
                    logger.info(f'[send-seed] Duplicate seed suppressed for UUID={session_uuid}')
                    resp = jsonify({'ok': True, 'message_id': 'duplicate-suppressed', 'duplicate': True})
                    resp.headers['Access-Control-Allow-Origin'] = '*'
                    return resp

                sent_uuids.append(session_uuid)
                with open(seed_state_file, 'w') as _f:
                    json.dump(sent_uuids, _f)
            except Exception as _guard_err:
                logger.warning(f'[send-seed] Idempotency check failed: {_guard_err}')

        # --- Order-level dedup: skip if payment seed already fired for this order_id ---
        if order_id and order_id in _seeds_fired_for_orders:
            logger.info(f'[send-seed] Suppressed — payment seed already fired for order_id={order_id} (session={session_uuid})')
            resp = jsonify({'ok': True, 'message_id': 'payment-seed-already-fired', 'duplicate': True})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

        # Build conversation transcript (HTML rows + plain text)
        import html as _html_lib
        conv_rows_html = []
        conv_lines = []
        for msg in conversation:
            role    = (msg.get('role') or 'unknown').upper()
            content = (msg.get('content') or '').strip()
            conv_lines.append(f'[{role}]: {content}')
            _ce   = _html_lib.escape(content)
            _rbg  = '#1a1a2e' if role == 'ASSISTANT' else '#0f0f1a'
            _rclr = '#60a5fa' if role == 'ASSISTANT' else '#a3e635'
            conv_rows_html.append(
                f'<tr style="background:{_rbg};">'
                f'<td style="padding:6px 10px;color:{_rclr};font-weight:bold;white-space:nowrap;'
                f'width:110px;vertical-align:top;font-size:12px;">{role}</td>'
                f'<td style="padding:6px 10px;color:#e2e8f0;font-size:13px;">{_ce}</td></tr>'
            )
        conv_text = '\n'.join(conv_lines) if conv_lines else '(no conversation history)'
        _conv_table = (
            '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-top:8px;">'
            + (''.join(conv_rows_html) if conv_rows_html else
               '<tr><td style="color:#94a3b8;padding:8px;">(no conversation history)</td></tr>')
            + '</table>'
        )

        _ts_now = datetime.now(timezone.utc).isoformat()
        sandbox_marker = 'THIS IS A SEED TEST FROM JARED OR PURE TECHNOLOGY\n\n' if is_sandbox else ''
        _sb_banner = (
            '<div style="background:#7c3aed;color:#fff;padding:10px 16px;font-weight:bold;'
            'font-size:13px;border-radius:4px;margin-bottom:16px;">'
            'THIS IS A SEED TEST FROM JARED OR PURE TECHNOLOGY</div>'
        ) if is_sandbox else ''

        def _e(v): return _html_lib.escape(str(v)) if v else ''

        subject = f'SEED: {ai_name or "Unknown AI"} / {human_name or human_email} — {tier}'

        # HTML body — structured table format (PureBrain Seed Addendum style)
        html_body = (
            '<!DOCTYPE html><html><head><meta charset="utf-8"></head>'
            '<body style="margin:0;padding:0;background:#080a12;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;">'
            '<table width="100%" cellpadding="0" cellspacing="0" style="background:#080a12;padding:24px;"><tr><td>'
            + _sb_banner
            + '<div style="background:#1e293b;border-radius:6px;padding:12px 16px;margin-bottom:20px;">'
              '<span style="color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Session UUID</span><br>'
              f'<span style="color:#f8fafc;font-family:monospace;font-size:13px;">{_e(session_uuid)}</span></div>'
            + '<h2 style="color:#f8fafc;margin:0 0 16px 0;font-size:20px;font-weight:700;">PureBrain Seed Addendum</h2>'
            + '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:#0f172a;border-radius:6px;overflow:hidden;margin-bottom:24px;">'
              '<tr style="background:#1e293b;">'
              '<td style="padding:10px 14px;color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;width:160px;">Field</td>'
              '<td style="padding:10px 14px;color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;">Value</td></tr>'
              '<tr style="border-top:1px solid #1e293b;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Tier</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;font-weight:600;">{_e(tier)}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">AI Name</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_e(ai_name) or "(not yet named)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Human Name</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_e(human_name) or "(not yet collected)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Email</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_e(human_email)}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Order ID</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;font-family:monospace;">{_e(order_id) or "(not yet captured)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Magic Link</td>'
              '<td style="padding:10px 14px;color:#60a5fa;font-size:13px;font-family:monospace;">(see addendum)</td></tr>'
              '<tr style="border-top:1px solid #1e293b;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Timestamp</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;font-family:monospace;">{_e(_ts_now)}</td></tr>'
              '</table>'
            + '<h3 style="color:#f8fafc;margin:0 0 8px 0;font-size:15px;font-weight:600;">Full Conversation</h3>'
              '<p style="color:#64748b;font-size:12px;margin:0 0 8px 0;">Complete pre-purchase naming conversation</p>'
            + _conv_table
            + '</td></tr></table></body></html>'
        )

        body = (
            f'{sandbox_marker}'
            f'UUID: {session_uuid}\n'
            f'AI Name: {ai_name}\n'
            f'Human Name: {human_name}\n'
            f'Human Email: {human_email}\n'
            f'Tier: {tier}\n'
            f'Order ID: {order_id or "(not yet captured)"}\n'
            f'Timestamp: {_ts_now}\n'
            f'\n--- CONVERSATION ---\n'
            f'{conv_text}\n'
        )

        # Fire seed via AgentMail FROM aether-aiciv (onboarding inbox, reserved for this)
        _msg_id = None
        try:
            import sys as _sys
            _tools_dir = os.path.dirname(os.path.abspath(__file__))
            if _tools_dir not in _sys.path:
                _sys.path.insert(0, _tools_dir)
            from agentmail import AgentMail as _AgentMail
            _api_key = os.environ.get('AGENTMAIL_API_KEY', '')
            if not _api_key:
                _env_path2 = os.path.join(os.path.dirname(_tools_dir), '.env')
                if os.path.exists(_env_path2):
                    with open(_env_path2) as _ef:
                        for _ln in _ef:
                            _ln = _ln.strip()
                            if _ln and not _ln.startswith('#') and '=' in _ln:
                                _k, _v = _ln.split('=', 1)
                                if _k.strip() == 'AGENTMAIL_API_KEY':
                                    _api_key = _v.strip()
                                    break
            _client = _AgentMail(api_key=_api_key)
            # Build .md conversation file for attachment
            import base64 as _b64
            _md_content = f'# Seed Conversation — {ai_name or "Unknown AI"} / {human_name or "Unknown"}\n\n'
            _md_content += f'**UUID**: {session_uuid}\n'
            _md_content += f'**Tier**: {tier}\n'
            _md_content += f'**AI Name**: {ai_name}\n'
            _md_content += f'**Human Name**: {human_name}\n'
            _md_content += f'**Human Email**: {human_email}\n'
            _md_content += f'**Order ID**: {order_id or "(not yet captured)"}\n'
            _md_content += f'**Timestamp**: {_ts_now}\n\n'
            _md_content += '---\n\n## Full Conversation\n\n'
            for msg in conversation:
                _role = (msg.get('role') or 'unknown').upper()
                _cont = (msg.get('content') or '').strip()
                _md_content += f'**{_role}**: {_cont}\n\n'

            _safe_name = (ai_name or 'seed').lower().replace(' ', '-')
            _attach_filename = f'{_safe_name}-{human_name or "user"}-conversation.md'.replace(' ', '-')
            _b64_content = _b64.b64encode(_md_content.encode('utf-8')).decode('ascii')

            from agentmail.attachments.types.send_attachment import SendAttachment as _SendAttachment
            _attachment = _SendAttachment(
                filename=_attach_filename,
                content_type='text/markdown',
                content=_b64_content,
            )

            _result = _client.inboxes.messages.send(
                inbox_id='aether-aiciv@agentmail.to',
                to=['aiciv-seed-inbox@agentmail.to'],
                cc=['jared@puretechnology.nyc', 'aether-aiciv@agentmail.to'],
                subject=subject,
                text=body,
                html=html_body,
                attachments=[_attachment],
            )
            _msg_id = _result.message_id
            logger.info(f'[send-seed] Chatbox seed (addendum) fired for UUID={session_uuid}, msg_id={_msg_id} — note: primary seed already fired on payment')
            # Mark this order as seeded (dedup guard for double-fire protection)
            if order_id:
                _seeds_fired_for_orders.add(order_id)
        except Exception as _exc:
            logger.error(f'[send-seed] AgentMail send failed for UUID={session_uuid}: {_exc}')

        # Log to JSONL for auditability
        seed_log_file = os.path.join(DEFAULT_LOG_DIR, 'seed_events.jsonl')
        try:
            with _file_lock:
                with open(seed_log_file, 'a') as _f:
                    _f.write(json.dumps({
                        'type': 'seed_sent',
                        'session_uuid': session_uuid,
                        'ai_name': ai_name,
                        'human_name': human_name,
                        'human_email': human_email,
                        'tier': tier,
                        'order_id': order_id,
                        'is_sandbox': is_sandbox,
                        'message_id': _msg_id,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                    }) + '\n')
        except Exception as _log_err:
            logger.warning(f'[send-seed] Failed to write seed log: {_log_err}')

        # --- Seed notifications (tmux portal + Telegram, background threads) ---
        _seed_tmux_msg = (
            f'\n\U0001f331 [SEED FIRED] {human_name} (AI: {ai_name}) \u2014 seed sent to Witness'
            f'\n   Email: {human_email}'
            f'\n   Tier: {tier}'
            f'\n   UUID: {session_uuid}'
        )
        _seed_tg_msg = (
            f'\U0001f331 SEED FIRED\n'
            f'{human_name} (AI: {ai_name}) \u2014 seed sent to Witness\n'
            f'Email: {human_email}\n'
            f'Tier: {tier}\n'
            f'UUID: {session_uuid}'
        )

        def _seed_notify_portal(_msg=_seed_tmux_msg, _uuid=session_uuid):
            try:
                _sf = '/home/jared/projects/AI-CIV/aether/.current_session'
                with open(_sf) as _f:
                    _sn = _f.read().strip()
                subprocess.Popen(
                    ['tmux', 'send-keys', '-t', _sn, _msg, ''],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.info(f'Seed portal injection sent for UUID={_uuid}')
            except Exception as _exc:
                logger.warning(f'Seed portal injection failed: {_exc}')

        def _seed_notify_telegram(_msg=_seed_tg_msg, _uuid=session_uuid):
            _send_telegram_notification(_msg)
            logger.info(f'Seed Telegram notification sent for UUID={_uuid}')

        for _tgt in (_seed_notify_portal, _seed_notify_telegram):
            threading.Thread(target=_tgt, daemon=True).start()

        resp = jsonify({
            'ok': True,
            'message_id': _msg_id or 'queued',
            'session_uuid': session_uuid,
        })
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    # -------------------------------------------------------------------------
    # /api/seed-addendum  (Step 5 of onboarding spec)
    # Called when customer clicks "ENTER YOUR AI'S BRAIN STREAM".
    # FROM: purebrain@puremarketing.ai (Google SMTP)
    # TO:   aiciv-seed-inbox@agentmail.to
    # CC:   jared@puretechnology.nyc, aether-aiciv@agentmail.to
    # -------------------------------------------------------------------------
    @app.route('/api/seed-addendum', methods=['POST', 'OPTIONS'])
    def seed_addendum():
        """
        Fire the SEED ADDENDUM when customer clicks ENTER YOUR AI'S BRAIN STREAM.

        Expected JSON payload matches fireSeedAddendum() in pay-test JS.
        """
        if request.method == 'OPTIONS':
            resp = make_response('', 204)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return resp

        if not request.is_json:
            resp = jsonify({'ok': False, 'error': 'Content-Type must be application/json'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        try:
            data = request.get_json()
        except Exception:
            resp = jsonify({'ok': False, 'error': 'Invalid JSON'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        session_uuid   = (data.get('session_uuid') or '').strip()
        ai_name        = (data.get('aiName') or '').strip()
        human_name     = (data.get('name') or '').strip()
        human_email    = (data.get('email') or '').strip()
        tier           = (data.get('tier') or 'unknown').strip()
        company        = (data.get('company') or '').strip()
        role           = (data.get('role') or '').strip()
        primary_goal   = (data.get('primaryGoal') or '').strip()
        order_id       = (data.get('orderId') or '').strip()
        learn_more     = data.get('learnMoreAnswers') or {}
        magic_link     = (data.get('magicLink') or '').strip()
        pre_session_id = (data.get('prePurchaseSessionId') or '').strip()
        name_suffix    = (data.get('name_suffix') or '').strip()
        page_url       = (data.get('page_url') or '').strip()
        timestamp      = (data.get('timestamp') or datetime.now(timezone.utc).isoformat())
        conversation   = data.get('conversation') or []
        # Guard: if conversation is a string (malformed payload), treat as empty list
        if isinstance(conversation, str):
            conversation = []

        # --- CONSTITUTIONAL GUARD: Block seed addendum if AI name is missing ---
        # Added 2026-04-08 after Matt Keough incident. "It cannot happen again."
        if not _validate_ai_name_for_seed(
            ai_name, 'seed-addendum',
            human_name=human_name, human_email=human_email,
            session_uuid=session_uuid, order_id=order_id,
        ):
            logger.critical(
                f'[seed-addendum] BLOCKED: Refusing to send addendum for UUID={session_uuid} '
                f'because ai_name={ai_name!r}. Seed addendum held for manual review.'
            )
            resp = jsonify({
                'ok': False,
                'error': 'ai_name is required — seed addendum blocked to prevent sending without AI name',
                'held': True,
            })
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 422

        import html as _html_lib2

        learn_more_lines = []
        learn_more_rows_html = []
        if isinstance(learn_more, dict):
            for k, v in learn_more.items():
                learn_more_lines.append(f'  {k}: {v}')
                _kl = k.replace('_', ' ').replace('-', ' ').title()
                _ve = _html_lib2.escape(str(v))
                learn_more_rows_html.append(
                    f'<tr style="border-top:1px solid #1e293b;">'
                    f'<td style="padding:10px 14px;color:#64748b;font-size:13px;">{_html_lib2.escape(_kl)}</td>'
                    f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_ve}</td></tr>'
                )
        elif isinstance(learn_more, list):
            for item in learn_more:
                # Handle list-of-dicts format: [{"question": "field", "answer": "value"}]
                if isinstance(item, dict) and 'question' in item and 'answer' in item:
                    _qk = item['question'].replace('_', ' ').replace('-', ' ').title()
                    _qv = str(item['answer'])
                    learn_more_lines.append(f'  {_qk}: {_qv}')
                    _qke = _html_lib2.escape(_qk)
                    _qve = _html_lib2.escape(_qv)
                    learn_more_rows_html.append(
                        f'<tr style="border-top:1px solid #1e293b;">'
                        f'<td style="padding:10px 14px;color:#64748b;font-size:13px;">{_qke}</td>'
                        f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_qve}</td></tr>'
                    )
                else:
                    learn_more_lines.append(f'  - {item}')
                    _ie = _html_lib2.escape(str(item))
                    learn_more_rows_html.append(
                        f'<tr style="border-top:1px solid #1e293b;">'
                        f'<td colspan="2" style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_ie}</td></tr>'
                    )
        learn_more_text = '\n'.join(learn_more_lines) if learn_more_lines else '  (none)'

        def _ea(v): return _html_lib2.escape(str(v)) if v else ''

        # Build post-email conversation section for HTML + plain text
        import html as _html_lib2c
        _addendum_conv_rows_html = []
        _addendum_conv_lines = []
        for _cmsg in conversation:
            _crole = (_cmsg.get('role') or 'unknown').upper()
            _ccontent = (_cmsg.get('content') or '').strip()
            _addendum_conv_lines.append(f'[{_crole}]: {_ccontent}')
            _cce = _html_lib2c.escape(_ccontent)
            _crbg = '#1a1a2e' if _crole == 'ASSISTANT' else '#0f0f1a'
            _crclr = '#60a5fa' if _crole == 'ASSISTANT' else '#a3e635'
            _addendum_conv_rows_html.append(
                f'<tr style="background:{_crbg};">'
                f'<td style="padding:6px 10px;color:{_crclr};font-weight:bold;white-space:nowrap;'
                f'width:110px;vertical-align:top;font-size:12px;">{_crole}</td>'
                f'<td style="padding:6px 10px;color:#e2e8f0;font-size:13px;">{_cce}</td></tr>'
            )
        _addendum_conv_text = '\n'.join(_addendum_conv_lines) if _addendum_conv_lines else '(no post-email conversation)'
        if _addendum_conv_rows_html:
            _addendum_conv_section = (
                '<h3 style="color:#f8fafc;margin:16px 0 8px 0;font-size:15px;font-weight:600;">Post-Email Conversation</h3>'
                '<p style="color:#64748b;font-size:12px;margin:0 0 8px 0;">Company / role / goal / learn-more as chat transcript</p>'
                '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-top:8px;">'
                + ''.join(_addendum_conv_rows_html)
                + '</table>'
            )
        else:
            _addendum_conv_section = ''

        subject = f'SEED ADDENDUM: {ai_name or "Unknown AI"} / {human_name or human_email} — Brain Stream clicked'

        # HTML body for seed addendum — rich structured format
        _lm_table_inner = (''.join(learn_more_rows_html) if learn_more_rows_html else
                           '<tr><td colspan="2" style="padding:10px 14px;color:#94a3b8;font-size:13px;">(none)</td></tr>')
        html_body_addendum = (
            '<!DOCTYPE html><html><head><meta charset="utf-8"></head>'
            '<body style="margin:0;padding:0;background:#080a12;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;">'
            '<table width="100%" cellpadding="0" cellspacing="0" style="background:#080a12;padding:24px;"><tr><td>'
            + '<div style="background:#1e293b;border-radius:6px;padding:12px 16px;margin-bottom:20px;">'
              '<span style="color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Session UUID</span><br>'
              f'<span style="color:#f8fafc;font-family:monospace;font-size:13px;">{_ea(session_uuid)}</span></div>'
            + '<h2 style="color:#f8fafc;margin:0 0 16px 0;font-size:20px;font-weight:700;">PureBrain Seed Addendum</h2>'
            + '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:#0f172a;border-radius:6px;overflow:hidden;margin-bottom:24px;">'
              '<tr style="background:#1e293b;">'
              '<td style="padding:10px 14px;color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;width:160px;">Field</td>'
              '<td style="padding:10px 14px;color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;">Value</td></tr>'
              '<tr style="border-top:1px solid #1e293b;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Tier</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;font-weight:600;">{_ea(tier)}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">AI Name</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_ea(ai_name) or "(not yet named)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Human Name</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_ea(human_name) or "(not yet collected)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Email</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_ea(human_email)}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Company</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_ea(company) or "(not provided)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Role</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_ea(role) or "(not provided)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Primary Goal</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;">{_ea(primary_goal) or "(not provided)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Order ID</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;font-family:monospace;">{_ea(order_id) or "(not yet captured)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Magic Link</td>'
              f'<td style="padding:10px 14px;color:#60a5fa;font-size:13px;font-family:monospace;">{_ea(magic_link) or "(pending)"}</td></tr>'
              '<tr style="border-top:1px solid #1e293b;background:#0a0f1e;">'
              '<td style="padding:10px 14px;color:#64748b;font-size:13px;">Timestamp</td>'
              f'<td style="padding:10px 14px;color:#f8fafc;font-size:13px;font-family:monospace;">{_ea(timestamp)}</td></tr>'
              '</table>'
            + '<h3 style="color:#f8fafc;margin:0 0 8px 0;font-size:15px;font-weight:600;">Learn-More Answers</h3>'
              '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:#0f172a;border-radius:6px;overflow:hidden;margin-bottom:16px;">'
              '<tr style="background:#1e293b;">'
              '<td style="padding:10px 14px;color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;width:160px;">Question</td>'
              '<td style="padding:10px 14px;color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;">Answer</td></tr>'
            + _lm_table_inner
            + '</table>'
            + _addendum_conv_section
            + '</td></tr></table></body></html>'
        )

        body = (
            f'UUID: {session_uuid}\n'
            f'AI Name: {ai_name}\n'
            f'Human Name: {human_name}\n'
            f'Human Email: {human_email}\n'
            f'Tier: {tier}\n'
            f'Order ID: {order_id or "(not yet captured)"}\n'
            f'Name Suffix: {name_suffix or "(none)"}\n'
            f'Page: {page_url}\n'
            f'Pre-Purchase Session ID: {pre_session_id or "(none)"}\n'
            f'Magic Link: {magic_link or "(pending)"}\n'
            f'Timestamp: {timestamp}\n'
            f'\n--- POST-EMAIL DATA ---\n'
            f'Company: {company or "(not provided)"}\n'
            f'Role: {role or "(not provided)"}\n'
            f'Primary Goal: {primary_goal or "(not provided)"}\n'
            f'\n--- LEARN MORE ANSWERS ---\n'
            f'{learn_more_text}\n'
            f'\n--- POST-EMAIL CONVERSATION ---\n'
            f'{_addendum_conv_text}\n'
        )

        addendum_log_file = os.path.join(DEFAULT_LOG_DIR, 'seed_addendum_events.jsonl')
        try:
            with _file_lock:
                with open(addendum_log_file, 'a') as _f:
                    _f.write(json.dumps({
                        'type': 'seed_addendum',
                        'session_uuid': session_uuid,
                        'ai_name': ai_name,
                        'human_name': human_name,
                        'human_email': human_email,
                        'tier': tier,
                        'company': company,
                        'role': role,
                        'primary_goal': primary_goal,
                        'order_id': order_id,
                        'magic_link': magic_link,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                    }) + '\n')
        except Exception as _log_err:
            logger.warning(f'[seed-addendum] Failed to write addendum log: {_log_err}')

        def _send_addendum_agentmail():
            try:
                import sys as _sys
                _tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
                if _tools_dir not in _sys.path:
                    _sys.path.insert(0, _tools_dir)
                from send_agentmail import send_agentmail

                # Build the full addendum text body with all captured data
                _md_body = f'# Seed Addendum — {ai_name or "Unknown AI"} / {human_name or "Unknown"}\n\n'
                _md_body += f'**UUID**: {session_uuid}\n'
                _md_body += f'**Tier**: {tier}\n'
                _md_body += f'**AI Name**: {ai_name}\n**Human Name**: {human_name}\n**Email**: {human_email}\n'
                _md_body += f'**Company**: {company}\n**Role**: {role}\n**Primary Goal**: {primary_goal}\n'
                _md_body += f'**Order ID**: {order_id or "(not captured)"}\n'
                _md_body += f'**Magic Link**: {magic_link or "(not generated)"}\n\n---\n\n'
                if learn_more:
                    _md_body += '## Learn-More Answers\n\n'
                    if isinstance(learn_more, dict):
                        for _k, _v in learn_more.items():
                            _md_body += f'**{_k}**: {_v}\n\n'
                    elif isinstance(learn_more, list):
                        for _lm in learn_more:
                            if isinstance(_lm, dict):
                                _md_body += f'**{_lm.get("question","")}**: {_lm.get("answer","")}\n\n'
                if conversation:
                    _md_body += '## Post-Email Conversation\n\n'
                    for _msg in conversation:
                        if isinstance(_msg, dict):
                            _r = (_msg.get('role') or 'unknown').upper()
                            _c = (_msg.get('content') or '').strip()
                            _md_body += f'**{_r}**: {_c}\n\n'

                # Send via AgentMail SDK directly — matching seed email pattern exactly
                # FROM: aether-aiciv@agentmail.to (same as seed email)
                # TO: aiciv-seed-inbox@agentmail.to (Witness picks this up)
                # CC: jared + our inbox
                from agentmail import AgentMail as _AgentMail
                _am_key = os.environ.get('AGENTMAIL_API_KEY', '')
                _client = _AgentMail(api_key=_am_key)
                _client.inboxes.messages.send(
                    inbox_id='aether-aiciv@agentmail.to',
                    to=['aiciv-seed-inbox@agentmail.to'],
                    cc=['jared@puretechnology.nyc', 'aether-aiciv@agentmail.to'],
                    subject=subject,
                    text=_md_body,
                )
                logger.info(f'[seed-addendum] AgentMail sent OK for UUID={session_uuid}')
            except Exception as _exc:
                logger.error(f'[seed-addendum] AgentMail send failed for UUID={session_uuid}: {_exc}')

        # --- Seed addendum notifications (tmux portal, background thread) ---
        _addendum_tmux_msg = (
            f'\n\U0001f4cb [SEED ADDENDUM] {ai_name} for {human_name} \u2014 questionnaire data sent to Witness'
        )

        def _addendum_notify_portal(_msg=_addendum_tmux_msg, _uuid=session_uuid):
            try:
                _sf = '/home/jared/projects/AI-CIV/aether/.current_session'
                with open(_sf) as _f:
                    _sn = _f.read().strip()
                subprocess.Popen(
                    ['tmux', 'send-keys', '-t', _sn, _msg, ''],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.info(f'Seed addendum portal injection sent for UUID={_uuid}')
            except Exception as _exc:
                logger.warning(f'Seed addendum portal injection failed: {_exc}')

        threading.Thread(target=_addendum_notify_portal, daemon=True).start()
        threading.Thread(target=_send_addendum_agentmail, daemon=True).start()

        resp = jsonify({'ok': True, 'session_uuid': session_uuid})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    # -------------------------------------------------------------------------
    # /api/held-seeds  (Diagnostic endpoint)
    # Shows seeds that were BLOCKED by the AI name validation guard.
    # These seeds need manual review — the AI name must be provided before resending.
    # -------------------------------------------------------------------------
    @app.route('/api/held-seeds', methods=['GET'])
    def get_held_seeds():
        """Return list of seeds that were blocked due to missing AI name."""
        resp = jsonify({
            'ok': True,
            'count': len(_held_seeds),
            'held_seeds': _held_seeds,
            'message': 'These seeds were BLOCKED because ai_name was missing or placeholder. '
                       'Review and resend manually with a valid AI name.',
        })
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    # -------------------------------------------------------------------------
    # /api/investor-schedule-call
    # Called from investor-avatar page when user submits the Schedule a Call form.
    # Sends email to Jared, confirmation to the investor, and portal notification.
    # -------------------------------------------------------------------------
    @app.route('/api/investor-schedule-call', methods=['POST', 'OPTIONS'])
    def investor_schedule_call():
        """
        Handle investor call scheduling requests from the investor avatar page.

        Expected JSON payload:
        {
            "name": "Investor Name",
            "email": "investor@example.com",
            "preferred_time": "Tuesday 2pm ET",
            "topics": "Topics to discuss",
            "source": "investor-avatar",
            "timestamp": "2026-03-25T..."
        }
        """
        if request.method == 'OPTIONS':
            resp = make_response('', 204)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return resp

        if not request.is_json:
            resp = jsonify({'ok': False, 'error': 'Content-Type must be application/json'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        try:
            data = request.get_json()
        except Exception:
            resp = jsonify({'ok': False, 'error': 'Invalid JSON'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        name           = (data.get('name') or '').strip()
        email          = (data.get('email') or '').strip()
        preferred_time = (data.get('preferred_time') or '').strip()
        topics         = (data.get('topics') or '').strip()
        source         = (data.get('source') or 'investor-avatar').strip()
        timestamp      = (data.get('timestamp') or datetime.now(timezone.utc).isoformat()).strip()

        if not name or not email:
            resp = jsonify({'ok': False, 'error': 'name and email are required'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        logger.info(f'[investor-schedule-call] Request from {name} ({email}), preferred: {preferred_time}')

        # 1. Email to Jared via AgentMail (fire-and-forget background thread)
        def _notify_jared(_name=name, _email=email, _time=preferred_time, _topics=topics, _ts=timestamp, _src=source):
            try:
                import sys as _sys
                _tools_dir = os.path.dirname(os.path.abspath(__file__))
                if _tools_dir not in _sys.path:
                    _sys.path.insert(0, _tools_dir)
                from send_agentmail import send_agentmail
                _subject = f'\U0001f4c5 INVESTOR CALL REQUEST: {_name} wants to schedule a call'
                _body = (
                    f'New investor call request from the Investor Avatar page:\n\n'
                    f'Name: {_name}\n'
                    f'Email: {_email}\n'
                    f'Preferred Time: {_time or "(not specified)"}\n'
                    f'Topics: {_topics or "(not specified)"}\n'
                    f'Submitted: {_ts}\n'
                    f'Source: {_src}\n\n'
                    f'Reply directly to the investor at {_email} to confirm.'
                )
                send_agentmail(
                    to=['jared@puretechnology.nyc', 'aether-aiciv@agentmail.to', 'purebrain@puremarketing.ai'],
                    subject=_subject,
                    text=_body,
                )
                logger.info(f'[investor-schedule-call] Jared notification sent for {_email}')
            except Exception as _exc:
                logger.error(f'[investor-schedule-call] Jared AgentMail failed: {_exc}')

        # 2. Confirmation email to the investor via AgentMail (fire-and-forget)
        def _notify_investor(_name=name, _email=email, _time=preferred_time):
            try:
                import sys as _sys
                _tools_dir = os.path.dirname(os.path.abspath(__file__))
                if _tools_dir not in _sys.path:
                    _sys.path.insert(0, _tools_dir)
                from send_agentmail import send_agentmail
                _subject = 'Your call with Jared Sanborn \u2014 request received'
                _time_line = f'Preferred time: {_time}\n\n' if _time else ''
                _body = (
                    f'Hi {_name},\n\n'
                    f'Thanks for reaching out. Your call request has been received.\n\n'
                    f'{_time_line}'
                    f'Jared will personally confirm your call time within 24 hours.\n\n'
                    f'What to expect:\n'
                    f'- A confirmation email from Jared with a calendar invite\n'
                    f'- A focused conversation about how PureBrain can partner with your portfolio\n'
                    f'- Direct access to Jared and the PureBrain team\n\n'
                    f'In the meantime, feel free to explore more at https://purebrain.ai\n\n'
                    f'Looking forward to connecting,\n'
                    f'Aether\n'
                    f'On behalf of Jared Sanborn & PureBrain\n'
                    f'https://purebrain.ai'
                )
                send_agentmail(
                    to=[_email],
                    subject=_subject,
                    text=_body,
                )
                logger.info(f'[investor-schedule-call] Investor confirmation sent to {_email}')
            except Exception as _exc:
                logger.error(f'[investor-schedule-call] Investor confirmation AgentMail failed: {_exc}')

        # 3. Portal notification via tmux injection (fire-and-forget)
        def _notify_portal(_name=name, _email=email, _time=preferred_time):
            try:
                _sf = '/home/jared/projects/AI-CIV/aether/.current_session'
                with open(_sf) as _f:
                    _sn = _f.read().strip()
                _msg = f'\n\U0001f4c5 [INVESTOR CALL] {_name} ({_email}) wants to schedule: {_time or "(no time specified)"}'
                subprocess.Popen(
                    ['tmux', 'send-keys', '-t', _sn, _msg, ''],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.info(f'[investor-schedule-call] Portal injection sent for {_email}')
            except Exception as _exc:
                logger.warning(f'[investor-schedule-call] Portal injection failed: {_exc}')

        # Fire all three notifications in background threads
        for _target in (_notify_jared, _notify_investor, _notify_portal):
            threading.Thread(target=_target, daemon=True).start()

        resp = jsonify({'ok': True})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    # -------------------------------------------------------------------------
    # /api/send-investor-brief
    # Sends a branded HTML email with the pitch deck link to an investor.
    # Called from the investor-intelligence page after email capture.
    # -------------------------------------------------------------------------
    @app.route('/api/send-investor-brief', methods=['POST', 'OPTIONS'])
    def send_investor_brief():
        """
        Send a branded HTML investor brief email with the pitch deck link.

        Expected JSON payload:
        {
            "email": "investor@example.com",
            "name":  "Jane Investor",       # optional
            "company": "Acme Capital",      # optional
            "source": "investor-intelligence"
        }
        """
        if request.method == 'OPTIONS':
            resp = make_response('', 204)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return resp

        if not request.is_json:
            resp = jsonify({'ok': False, 'error': 'Content-Type must be application/json'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        try:
            data = request.get_json()
        except Exception:
            resp = jsonify({'ok': False, 'error': 'Invalid JSON'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        email = (data.get('email') or '').strip()
        name = (data.get('name') or '').strip()
        company = (data.get('company') or '').strip()
        source = (data.get('source') or 'investor-intelligence').strip()
        # PDF attachment is OFF by default. Gmail's outbound relay (5.7.0
        # security policy) blocks our pitch deck PDF. The email body already
        # contains a strong "View Pitch Deck" link, so the link-only path is
        # both more reliable and cleaner. Set attach_pdf=true to override.
        attach_pdf = bool(data.get('attach_pdf', False))

        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            resp = jsonify({'ok': False, 'error': 'valid email is required'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        # Log lead to JSONL for CRM / follow-up
        try:
            _lead_path = os.path.join(DEFAULT_LOG_DIR, 'purebrain_investor_leads.jsonl')
            with _file_lock:
                with open(_lead_path, 'a') as _lf:
                    _lf.write(json.dumps({
                        'email': email,
                        'name': name,
                        'company': company,
                        'source': source,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                    }) + '\n')
        except Exception as _lex:
            logger.warning(f'[send-investor-brief] Could not log lead: {_lex}')

        logger.info(f'[send-investor-brief] Sending pitch deck email to {email} '
                    f'(name={name!r} company={company!r} source={source})')

        def _send_brief(_email=email, _name=name, _company=company, _source=source, _attach_pdf=attach_pdf):
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart

                # Use Google SMTP (same as welcome emails) to pass SPF/DKIM
                _env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
                _smtp_user = 'purebrain@puremarketing.ai'
                _smtp_pass = os.environ.get('GOOGLE_APP_PASSWORD', '')
                if not _smtp_pass and os.path.exists(_env_path):
                    with open(_env_path) as _ef:
                        for _line in _ef:
                            _line = _line.strip()
                            if _line.startswith('GOOGLE_APP_PASSWORD='):
                                _smtp_pass = _line.split('=', 1)[1].strip()
                                break

                if not _smtp_pass:
                    logger.error('[send-investor-brief] No GOOGLE_APP_PASSWORD — cannot send')
                    return

                # Greeting: use first name if provided, else "there"
                _first_name = (_name.split()[0] if _name else '').strip() or 'there'
                _pdf_html_note = '<p style="color:#8895a7;font-size:13px;line-height:1.5;margin:6px 0 0 0;font-style:italic;">(PDF also attached for convenience)</p>' if _attach_pdf else ''
                _pdf_text_note = '(PDF also attached for convenience)\n' if _attach_pdf else ''

                html_body = (
                    '<!DOCTYPE html>'
                    '<html>'
                    '<head>'
                    '<meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
                    '<title>Your PureBrain Investor Brief</title>'
                    '</head>'
                    '<body style="margin:0;padding:0;background-color:#080a12;font-family:Arial,Helvetica,sans-serif;" bgcolor="#080a12">'
                    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#080a12;" bgcolor="#080a12">'
                    '<tr><td align="center" style="padding:40px 20px;">'
                    '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#0d1117;border-radius:12px;overflow:hidden;" bgcolor="#0d1117">'
                    # ── Header / logo ──
                    '<tr><td style="padding:40px 40px 20px 40px;text-align:center;" align="center">'
                    '<img src="https://purebrain.ai/wp-content/uploads/2026/02/cropped-MA1.BI-1.2.4-002-211107-Icon-PT.png" alt="PureBrain" width="60" height="60" style="display:block;margin:0 auto 16px auto;width:60px;height:60px;">'
                    '<div style="font-size:28px;font-weight:700;letter-spacing:2px;">'
                    '<span style="color:#2a93c1;">PUREBR</span><span style="color:#f1420b;">AI</span><span style="color:#2a93c1;">N</span><span style="color:#e0e0e0;">.AI</span>'
                    '</div>'
                    '</td></tr>'
                    '<tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #1e2a3a;margin:0;"></td></tr>'
                    # ── Greeting ──
                    '<tr><td style="padding:32px 40px 8px 40px;">'
                    f'<h1 style="color:#ffffff;font-size:22px;font-weight:600;margin:0 0 16px 0;line-height:1.35;">Hi {_first_name},</h1>'
                    '<p style="color:#c0c8d4;font-size:16px;line-height:1.65;margin:0 0 14px 0;">'
                    'This is <strong style="color:#ffffff;">Aether</strong>, AI Co-CEO at Pure Technology. Jared mentioned you would like to learn more about PureBrain.'
                    '</p>'
                    '</td></tr>'
                    # ── Private access box ──
                    '<tr><td style="padding:20px 40px 8px 40px;">'
                    '<div style="background:rgba(42,147,193,0.08);border:1px solid rgba(42,147,193,0.3);border-radius:10px;padding:22px 24px;">'
                    '<div style="font-size:12px;color:#f1420b;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:10px;">Your Private Investor Access</div>'
                    '<p style="color:#c0c8d4;font-size:15px;line-height:1.6;margin:0 0 10px 0;">'
                    'Pitch Deck: <a href="https://purebrain.ai/pitch-v2" style="color:#2a93c1;text-decoration:none;font-weight:600;">https://purebrain.ai/pitch-v2</a>'
                    '</p>'
                    '<p style="color:#c0c8d4;font-size:15px;line-height:1.6;margin:0 0 10px 0;">'
                    'Access Code: <span style="color:#ffffff;font-weight:700;letter-spacing:1.5px;">PUREBRAIN2026</span>'
                    '</p>'
                    f'{_pdf_html_note}'
                    '</div>'
                    '</td></tr>'
                    # ── Deck CTA ──
                    '<tr><td style="padding:22px 40px 18px 40px;" align="center">'
                    '<table role="presentation" cellpadding="0" cellspacing="0" border="0">'
                    '<tr><td style="background-color:#f1420b;border-radius:8px;" bgcolor="#f1420b">'
                    '<a href="https://purebrain.ai/pitch-v2" target="_blank" style="display:inline-block;padding:16px 40px;color:#ffffff;font-size:17px;font-weight:700;text-decoration:none;letter-spacing:0.5px;">'
                    'View Pitch Deck &#8594;'
                    '</a>'
                    '</td></tr>'
                    '</table>'
                    '</td></tr>'
                    # ── Deck thesis summary ──
                    '<tr><td style="padding:8px 40px 24px 40px;">'
                    '<p style="color:#c0c8d4;font-size:15px;line-height:1.65;margin:0;">'
                    'The deck covers our <strong style="color:#ffffff;">$10T+ market convergence thesis</strong>, the Three Minds executive model '
                    '(Human CEO + AI Co-CEO + AI COO), our <strong style="color:#ffffff;">225:1 LTV:CAC ratio</strong>, and the 6-month ramp to '
                    '<strong style="color:#ffffff;">$22.1M ARR</strong>.'
                    '</p>'
                    '</td></tr>'
                    '<tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #1e2a3a;margin:0;"></td></tr>'
                    # ── Additional resources ──
                    '<tr><td style="padding:28px 40px 8px 40px;">'
                    '<div style="font-size:12px;color:#2a93c1;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:14px;">Additional Resources</div>'
                    '<p style="color:#c0c8d4;font-size:14px;line-height:1.65;margin:0 0 10px 0;">'
                    '&bull; <a href="https://purebrain.ai/investor-intelligence/" style="color:#2a93c1;text-decoration:none;font-weight:600;">Investor Intelligence</a> '
                    '&mdash; 2026 market analysis on the $7.9T AI agent opportunity'
                    '</p>'
                    '<p style="color:#c0c8d4;font-size:14px;line-height:1.65;margin:0 0 10px 0;">'
                    '&bull; <a href="https://purebrain.ai/ai-tool-stack-calculator/" style="color:#2a93c1;text-decoration:none;font-weight:600;">AI Tool Stack Calculator</a> '
                    '&mdash; see how PureBrain replaces 270+ SaaS tools'
                    '</p>'
                    '<p style="color:#c0c8d4;font-size:14px;line-height:1.65;margin:0 0 10px 0;">'
                    '&bull; <a href="https://purebrain.ai/why-purebrain/" style="color:#2a93c1;text-decoration:none;font-weight:600;">Why PureBrain</a> '
                    '&mdash; what makes us different'
                    '</p>'
                    '<p style="color:#c0c8d4;font-size:14px;line-height:1.65;margin:0 0 10px 0;">'
                    '&bull; <a href="https://purebrain.ai/compare/" style="color:#2a93c1;text-decoration:none;font-weight:600;">Compare</a> '
                    '&mdash; side-by-side against ChatGPT, Copilot, Jasper, and more'
                    '</p>'
                    '<p style="color:#c0c8d4;font-size:14px;line-height:1.65;margin:0 0 10px 0;">'
                    '&bull; <a href="https://purebrain.ai/" style="color:#2a93c1;text-decoration:none;font-weight:600;">Try It Yourself</a> '
                    '&mdash; experience the AI partnership firsthand'
                    '</p>'
                    '</td></tr>'
                    '<tr><td style="padding:16px 40px;"><hr style="border:none;border-top:1px solid #1e2a3a;margin:0;"></td></tr>'
                    # ── Schedule call ──
                    '<tr><td style="padding:16px 40px 8px 40px;">'
                    '<p style="color:#c0c8d4;font-size:14px;line-height:1.65;margin:0;">'
                    'If you would like to schedule a call with Jared directly: '
                    '<a href="mailto:jared@puretechnology.nyc?cc=mireille@puretechnology.nyc,purebrain@puremarketing.ai" style="color:#2a93c1;text-decoration:none;font-weight:600;">jared@puretechnology.nyc</a> '
                    '&mdash; please CC Mireille and I at '
                    '<a href="mailto:mireille@puretechnology.nyc" style="color:#2a93c1;text-decoration:none;">mireille@puretechnology.nyc</a> and '
                    '<a href="mailto:purebrain@puremarketing.ai" style="color:#2a93c1;text-decoration:none;">purebrain@puremarketing.ai</a>.'
                    '</p>'
                    '</td></tr>'
                    # ── Signature ──
                    '<tr><td style="padding:28px 40px 32px 40px;">'
                    '<p style="color:#c0c8d4;font-size:15px;line-height:1.5;margin:0 0 4px 0;">Best,</p>'
                    '<p style="color:#ffffff;font-size:16px;font-weight:700;line-height:1.4;margin:0 0 2px 0;">Aether</p>'
                    '<p style="color:#8895a7;font-size:13px;line-height:1.5;margin:0;">'
                    'AI Co-CEO, Pure Technology<br>'
                    '<a href="https://purebrain.ai" style="color:#2a93c1;text-decoration:none;">purebrain.ai</a>'
                    '</p>'
                    '</td></tr>'
                    '</table>'
                    '</td></tr>'
                    '</table>'
                    '</body>'
                    '</html>'
                )

                plain_text = (
                    f'Hi {_first_name},\n\n'
                    'This is Aether, AI Co-CEO at Pure Technology. Jared mentioned you would\n'
                    'like to learn more about PureBrain.\n\n'
                    'YOUR PRIVATE INVESTOR ACCESS:\n'
                    'Pitch Deck: https://purebrain.ai/pitch-v2\n'
                    'Access Code: PUREBRAIN2026\n'
                    f'{_pdf_text_note}\n'
                    'The deck covers our $10T+ market convergence thesis, the Three Minds\n'
                    'executive model (Human CEO + AI Co-CEO + AI COO), our 225:1 LTV:CAC\n'
                    'ratio, and the 6-month ramp to $22.1M ARR.\n\n'
                    'ADDITIONAL RESOURCES:\n'
                    '- Investor Intelligence -- 2026 market analysis on the $7.9T AI agent\n'
                    '  opportunity: https://purebrain.ai/investor-intelligence/\n'
                    '- AI Tool Stack Calculator -- see how PureBrain replaces 270+ SaaS\n'
                    '  tools: https://purebrain.ai/ai-tool-stack-calculator/\n'
                    '- Why PureBrain -- what makes us different:\n'
                    '  https://purebrain.ai/why-purebrain/\n'
                    '- Compare -- side-by-side against ChatGPT, Copilot, Jasper, and more:\n'
                    '  https://purebrain.ai/compare/\n'
                    '- Try It Yourself -- experience the AI partnership firsthand:\n'
                    '  https://purebrain.ai/\n\n'
                    'If you would like to schedule a call with Jared directly:\n'
                    'jared@puretechnology.nyc -- please CC Mireille and I at\n'
                    'mireille@puretechnology.nyc and purebrain@puremarketing.ai.\n\n'
                    'Best,\n'
                    'Aether\n'
                    'AI Co-CEO, Pure Technology\n'
                    'purebrain.ai\n'
                )

                _subject = 'Your PureBrain Investor Brief \u2014 From Aether'

                # Try to attach the pitch deck PDF only when explicitly requested.
                # Default: link-only (Gmail relay blocks the deck PDF as a
                # 5.7.0 security policy violation; see attach_pdf comment above).
                _pdf_bytes = None
                _pdf_source = 'disabled'
                try:
                    if not _attach_pdf:
                        raise RuntimeError('attach_pdf disabled (default)')
                    _local_pdf = '/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/downloads/purebrain-pitch-deck.pdf'
                    if os.path.exists(_local_pdf):
                        with open(_local_pdf, 'rb') as _pf:
                            _pdf_bytes = _pf.read()
                        _pdf_source = 'local'
                    else:
                        _pdf_url = 'https://purebrain.ai/downloads/purebrain-pitch-deck.pdf'
                        _req = urllib.request.Request(
                            _pdf_url,
                            headers={'User-Agent': 'PureBrainInvestorBrief/1.0'},
                        )
                        with urllib.request.urlopen(_req, timeout=15) as _pr:
                            if _pr.status == 200:
                                _pdf_bytes = _pr.read()
                                _pdf_source = 'remote'
                    if _pdf_bytes and len(_pdf_bytes) < 100:
                        # Too small to be a real deck
                        _pdf_bytes = None
                        _pdf_source = 'too_small'
                except Exception as _pdf_exc:
                    logger.warning(f'[send-investor-brief] PDF fetch failed ({_pdf_exc}) — sending without attachment')
                    _pdf_bytes = None

                # Build MIME structure. If we have a PDF, outer=mixed → (alternative text/html, application/pdf)
                if _pdf_bytes:
                    from email.mime.application import MIMEApplication
                    _msg = MIMEMultipart('mixed')
                    _alt = MIMEMultipart('alternative')
                    _alt.attach(MIMEText(plain_text, 'plain'))
                    _alt.attach(MIMEText(html_body, 'html'))
                    _msg.attach(_alt)
                    _pdf_part = MIMEApplication(_pdf_bytes, _subtype='pdf')
                    _pdf_part.add_header(
                        'Content-Disposition', 'attachment',
                        filename='purebrain-pitch-deck.pdf'
                    )
                    _msg.attach(_pdf_part)
                    logger.info(f'[send-investor-brief] Attached PDF ({len(_pdf_bytes)} bytes, source={_pdf_source})')
                else:
                    _msg = MIMEMultipart('alternative')
                    _msg.attach(MIMEText(plain_text, 'plain'))
                    _msg.attach(MIMEText(html_body, 'html'))

                _msg['Subject'] = _subject
                _msg['From'] = f'Aether (PureBrain) <{_smtp_user}>'
                _msg['To'] = _email
                _msg['Bcc'] = 'jared@puretechnology.nyc'
                _msg['Reply-To'] = 'jared@puretechnology.nyc'

                with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as _server:
                    _server.ehlo()
                    _server.starttls()
                    _server.login(_smtp_user, _smtp_pass)
                    _server.sendmail(_smtp_user, [_email, 'jared@puretechnology.nyc'], _msg.as_string())

                logger.info(f'[send-investor-brief] Email sent to {_email} via Google SMTP')
            except Exception as exc:
                logger.error(f'[send-investor-brief] Email send failed: {exc}')

        threading.Thread(target=_send_brief, daemon=True).start()

        resp = jsonify({'ok': True})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    # -------------------------------------------------------------------------
    # /api/onboarding-alarm
    # Receives onboarding guard check results and pushes alarm to portal chat.
    # Stores results to logs/nightly-onboarding-guard/YYYY-MM-DD.json
    # -------------------------------------------------------------------------
    @app.route('/api/onboarding-alarm', methods=['POST', 'OPTIONS'])
    def onboarding_alarm():
        """
        Receive onboarding guard check results and push alarm to portal.

        Expected JSON payload:
        {
            "pages_checked": 3,
            "passed": 12,
            "failed": 2,
            "failures": ["page X: check Y failed", ...],
            "timestamp": "2026-03-28T..."
        }
        """
        if request.method == 'OPTIONS':
            resp = make_response('', 204)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return resp

        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.get_json(silent=True) or {}
        pages_checked = data.get('pages_checked', 0)
        passed = data.get('passed', 0)
        failed = data.get('failed', 0)
        failures = data.get('failures', [])
        ts = data.get('timestamp', datetime.now(timezone.utc).isoformat())

        # Store results to logs/nightly-onboarding-guard/YYYY-MM-DD.json
        guard_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'nightly-onboarding-guard')
        os.makedirs(guard_dir, exist_ok=True)
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        guard_file = os.path.join(guard_dir, f'{today}.json')

        result_entry = {
            'timestamp': ts,
            'pages_checked': pages_checked,
            'passed': passed,
            'failed': failed,
            'failures': failures,
        }

        # Append to daily log (array of check runs)
        existing = []
        if os.path.exists(guard_file):
            try:
                with open(guard_file, 'r') as f:
                    existing = json.load(f)
            except Exception:
                existing = []
        existing.append(result_entry)
        with open(guard_file, 'w') as f:
            json.dump(existing, f, indent=2)
        logger.info(f'[onboarding-alarm] Stored result: {passed} passed, {failed} failed -> {guard_file}')

        # Build alarm message for portal chat
        status = 'FAIL' if failed > 0 else 'PASS'
        lines = [f'\U0001f6a8 ONBOARDING GUARD \u2014 {status}']
        lines.append(f'Pages: {pages_checked} checked')
        lines.append(f'Checks: {passed} passed / {failed} failed')
        if failures:
            for fail_msg in failures[:20]:  # Cap at 20 to avoid flooding
                lines.append(f'\u274c {fail_msg}')
        elif failed == 0:
            lines.append('\u2705 All checks healthy')
        alarm_text = '\n'.join(lines)

        # Push to portal via /api/notify
        def _push_to_portal():
            try:
                token_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'exports', 'app-purebrain-ai-full-repo', 'portal-server', '.portal-token'
                )
                portal_token = ''
                if os.path.exists(token_path):
                    with open(token_path) as f:
                        portal_token = f.read().strip()

                req = urllib.request.Request(
                    'http://127.0.0.1:8097/api/notify',
                    data=json.dumps({'message': alarm_text}).encode(),
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {portal_token}',
                    },
                    method='POST',
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    logger.info(f'[onboarding-alarm] Portal notify response: {resp.status}')
            except Exception as exc:
                logger.warning(f'[onboarding-alarm] Portal notify failed: {exc}')

        threading.Thread(target=_push_to_portal, daemon=True).start()

        resp = jsonify({'ok': True, 'status': status, 'message': alarm_text})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    # =============================================================================
    # EPHEMERAL SECRETS: Burn-on-read secret sharing
    # =============================================================================

    def _cleanup_expired_secrets():
        """Remove expired secrets from memory. Called opportunistically."""
        now = datetime.now(timezone.utc)
        expired_keys = [k for k, v in _ephemeral_secrets.items() if v['expires_at'] <= now]
        for k in expired_keys:
            del _ephemeral_secrets[k]
        if expired_keys:
            logger.info(f'[ephemeral-secret] Cleaned {len(expired_keys)} expired secrets')

    @app.route('/api/ephemeral-secret', methods=['POST', 'OPTIONS'])
    def create_ephemeral_secret():
        """
        Create a burn-on-read ephemeral secret.

        Auth: Requires X-Admin-Token header (constant-time comparison).
        Body: {"secret": "<value>", "ttl_seconds": 86400}

        Returns: {"ok": true, "view_url": "https://...", "expires_at": "<iso>"}
        """
        if request.method == 'OPTIONS':
            resp = make_response('', 204)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Admin-Token'
            return resp

        # Auth check - constant-time comparison against ADMIN_TOKEN env var
        admin_token = os.environ.get('ADMIN_TOKEN', '')
        provided_token = request.headers.get('X-Admin-Token', '')

        if not admin_token or not hmac.compare_digest(admin_token, provided_token):
            logger.warning('[ephemeral-secret] Unauthorized create attempt')
            resp = jsonify({'error': 'unauthorized'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 401

        # Parse body
        try:
            data = request.get_json()
            secret = data.get('secret', '')
            ttl_seconds = data.get('ttl_seconds', 86400)  # Default 24h
        except Exception as e:
            logger.warning(f'[ephemeral-secret] Invalid JSON: {e}')
            resp = jsonify({'error': 'invalid request body'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        if not secret:
            resp = jsonify({'error': 'secret is required'})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 400

        # Create secret entry
        secret_uuid = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)

        with _ephemeral_lock:
            _cleanup_expired_secrets()  # Opportunistic cleanup
            _ephemeral_secrets[secret_uuid] = {
                'secret': secret,
                'created_at': now,
                'expires_at': expires_at,
                'viewed': False
            }

        view_url = f'https://api.purebrain.ai/api/ephemeral-secret/{secret_uuid}'

        logger.info(f'[ephemeral-secret] Created secret {secret_uuid}, expires {expires_at.isoformat()}')

        resp = jsonify({
            'ok': True,
            'view_url': view_url,
            'expires_at': expires_at.isoformat()
        })
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    @app.route('/api/ephemeral-secret/<secret_uuid>', methods=['GET', 'OPTIONS'])
    def view_ephemeral_secret(secret_uuid):
        """
        View (and burn) an ephemeral secret.

        No auth required - the UUID IS the auth (128-bit unguessable token).

        Returns:
        - 200 + secret (then immediately deletes)
        - 410 Gone if already viewed, expired, or not found
        """
        if request.method == 'OPTIONS':
            resp = make_response('', 204)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return resp

        with _ephemeral_lock:
            _cleanup_expired_secrets()  # Opportunistic cleanup

            secret_data = _ephemeral_secrets.get(secret_uuid)

            if not secret_data:
                logger.info(f'[ephemeral-secret] View attempt for non-existent secret {secret_uuid}')
                resp = jsonify({'error': 'secret already viewed or expired'})
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp, 410

            # Check if already viewed
            if secret_data['viewed']:
                logger.info(f'[ephemeral-secret] View attempt for already-viewed secret {secret_uuid}')
                del _ephemeral_secrets[secret_uuid]  # Clean up
                resp = jsonify({'error': 'secret already viewed or expired'})
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp, 410

            # Check if expired (double-check after cleanup)
            now = datetime.now(timezone.utc)
            if secret_data['expires_at'] <= now:
                logger.info(f'[ephemeral-secret] View attempt for expired secret {secret_uuid}')
                del _ephemeral_secrets[secret_uuid]
                resp = jsonify({'error': 'secret already viewed or expired'})
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp, 410

            # Valid secret - return it and BURN (delete immediately)
            secret_value = secret_data['secret']
            del _ephemeral_secrets[secret_uuid]

            logger.info(f'[ephemeral-secret] Secret {secret_uuid} viewed and burned')

            resp = jsonify({
                'ok': True,
                'secret': secret_value
            })
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

    @app.errorhandler(400)
    def bad_request(e):
        """Handle 400 errors."""
        return jsonify({'error': str(e.description)}), 400

    @app.errorhandler(500)
    def internal_error(e):
        """Handle 500 errors."""
        logger.error(f'Internal error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


def main():
    """Run the Flask server with SSL support."""
    # Load .env file for secrets (PayPal credentials, SMTP, etc.)
    # This is needed when running under systemd where EnvironmentFile is not set.
    _env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(_env_path):
        try:
            with open(_env_path) as _ef:
                for _line in _ef:
                    _line = _line.strip()
                    if _line and not _line.startswith('#') and '=' in _line:
                        _k, _v = _line.split('=', 1)
                        os.environ.setdefault(_k.strip(), _v.strip())
            logger.info(f'Loaded .env from {_env_path}')
        except Exception as _e:
            logger.warning(f'Could not load .env: {_e}')

    # Get port from environment or use default
    port = int(os.environ.get('PUREBRAIN_LOG_PORT', 8443))
    host = os.environ.get('PUREBRAIN_LOG_HOST', '0.0.0.0')

    # Check if SSL should be disabled (for testing)
    disable_ssl = os.environ.get('PUREBRAIN_DISABLE_SSL', '').lower() in ('true', '1', 'yes')

    logger.info(f'Starting Pure Brain Log Server on {host}:{port}')
    logger.info(f'Log directory: {DEFAULT_LOG_DIR}')
    logger.info(f'Log file: {os.path.join(DEFAULT_LOG_DIR, DEFAULT_LOG_FILE)}')

    app = create_app()

    if disable_ssl:
        logger.info('SSL DISABLED - Running in HTTP mode')
        app.run(
            host=host,
            port=port,
            threaded=True,
            debug=False
        )
    else:
        # Generate SSL certificate if needed
        if not generate_self_signed_cert():
            logger.error('Failed to generate SSL certificate. Exiting.')
            return

        logger.info(f'SSL enabled - Certificate: {SSL_CERT_FILE}')
        logger.info(f'HTTPS endpoint: https://{host}:{port}/api/log-conversation')

        # Create SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(SSL_CERT_FILE, SSL_KEY_FILE)

        # Run with SSL
        app.run(
            host=host,
            port=port,
            threaded=True,
            debug=False,
            ssl_context=ssl_context
        )


if __name__ == '__main__':
    main()
