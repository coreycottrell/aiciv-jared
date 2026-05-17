#!/usr/bin/env python3
"""
PayPal Auto-Split Payout System
================================
Manages revenue splits between Pure Technology and AICIV (Corey).

SPLIT FORMULA:
  Gross Payment
  - $35 AICIV Ops Fee
  - 5% Referral Fee (of gross)
  = Net After Fees
  → 60% to Corey (AICIV)
  → 40% to Pure Tech (Jared)

MODES:
  --add-payment   Add a new payment row (status: Pending Approval)
  --approve       Approve a pending payout and fire PayPal Payout
  --status        Show all pending payouts
  --summary       Show financial summary
  --webhook       Run webhook listener (Flask)
  --setup-sheet   Create/format the Payout Tracker tab

USAGE:
  python3 tools/paypal_auto_split.py --setup-sheet
  python3 tools/paypal_auto_split.py --add-payment --customer "Faris Asmar" --tier "Awakened" --amount 297
  python3 tools/paypal_auto_split.py --approve --row 5
  python3 tools/paypal_auto_split.py --status
  python3 tools/paypal_auto_split.py --summary

Author: dept-accounting-finance
Date: 2026-04-04
"""

import argparse
import json
import os
import sys
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / '.env')

# ── Constants ──────────────────────────────────────────────────────────────────
SPREADSHEET_ID = '1bmmO2FVxZdAcYewPFNu6DbHZzh9AAojHUsWgofv6tqQ'
TAB_NAME = 'Payout Tracker'
COREY_PAYPAL = 'weaver.aiciv@gmail.com'
OPS_FEE = 35.00
REFERRAL_RATE = 0.05
COREY_SPLIT = 0.60
PT_SPLIT = 0.40
AUTO_APPROVE_THRESHOLD = 20  # After 20 successful "Sent" payouts, auto-fire without approval

# PayPal API
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
PAYPAL_SECRET = os.getenv('PAYPAL_SECRET', '')
PAYPAL_BASE_URL = 'https://api-m.paypal.com'  # Live

# Sandbox override
if os.getenv('PAYPAL_USE_SANDBOX', '').lower() == 'true':
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_SANDBOX_CLIENT_ID', PAYPAL_CLIENT_ID)
    PAYPAL_SECRET = os.getenv('PAYPAL_SANDBOX_SECRET', PAYPAL_SECRET)
    PAYPAL_BASE_URL = 'https://api-m.sandbox.paypal.com'

# Column mapping (1-based for gspread)
COL = {
    'date': 1,        # A
    'customer': 2,    # B
    'tier': 3,        # C
    'gross': 4,       # D
    'ops_fee': 5,     # E
    'referral': 6,    # F
    'net': 7,         # G
    'corey_share': 8, # H
    'pt_share': 9,    # I
    'status': 10,     # J
    'payout_id': 11,  # K
    'payout_date': 12,# L
    'notes': 13,      # M
}

# Data starts at row 8 (after header + summary section)
DATA_START_ROW = 8
HEADER_ROW = 7

LOG_PATH = ROOT / 'logs' / 'paypal_auto_split.log'


def log(msg: str):
    """Log to file and stdout."""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')


# ── Google Sheets Auth ─────────────────────────────────────────────────────────

def get_spreadsheet():
    """
    Authenticate via GDriveManager OAuth2 (same creds as 777 tools).
    Returns a gspread Spreadsheet object.
    """
    import gspread
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]

    token_candidates = [
        ROOT / '.credentials' / 'oauth-token.json',
        ROOT / 'config' / 'gdrive_token.json',
        ROOT / 'tools' / 'gdrive_token.json',
        Path.home() / '.config' / 'gdrive_token.json',
    ]

    token_path = None
    for p in token_candidates:
        if p.exists():
            token_path = p
            break

    if not token_path:
        raise FileNotFoundError(
            "No gdrive_token.json found. Run gdrive_oauth_setup.py first."
        )

    with open(token_path) as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=SCOPES,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        updated = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': list(creds.scopes or SCOPES),
        }
        with open(token_path, 'w') as f:
            json.dump(updated, f, indent=2)

    gc = gspread.authorize(creds)
    return gc.open_by_key(SPREADSHEET_ID)


def get_or_create_tab(spreadsheet):
    """Get the Payout Tracker tab, or create it."""
    try:
        return spreadsheet.worksheet(TAB_NAME)
    except Exception:
        return None


# ── Split Calculation ──────────────────────────────────────────────────────────

def calculate_split(gross: float) -> dict:
    """Calculate the revenue split for a payment."""
    ops_fee = OPS_FEE
    referral = round(gross * REFERRAL_RATE, 2)
    net = round(gross - ops_fee - referral, 2)
    corey_share = round(net * COREY_SPLIT, 2)
    pt_share = round(net * PT_SPLIT, 2)
    return {
        'ops_fee': ops_fee,
        'referral': referral,
        'net': net,
        'corey_share': corey_share,
        'pt_share': pt_share,
    }


# ── PayPal API ─────────────────────────────────────────────────────────────────

def get_paypal_token() -> str:
    """Get PayPal OAuth2 access token."""
    url = f"{PAYPAL_BASE_URL}/v1/oauth2/token"
    resp = requests.post(
        url,
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={'grant_type': 'client_credentials'},
        headers={'Accept': 'application/json'},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def fire_payout(amount: float, customer: str, tier: str, gross: float) -> dict:
    """
    Fire a PayPal Payout to Corey.
    Returns {'payout_batch_id': str, 'status': str} or raises.
    """
    token = get_paypal_token()
    ts = int(time.time())

    payload = {
        "sender_batch_header": {
            "sender_batch_id": f"PureTech-{ts}",
            "email_subject": "Pure Technology Revenue Share",
            "email_message": f"Your revenue share for {customer} ({tier}) payment"
        },
        "items": [{
            "recipient_type": "EMAIL",
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "USD"
            },
            "receiver": COREY_PAYPAL,
            "note": f"60% share: {customer} {tier} ${gross:.2f}"
        }]
    }

    resp = requests.post(
        f"{PAYPAL_BASE_URL}/v1/payments/payouts",
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    batch_header = data.get('batch_header', {})
    return {
        'payout_batch_id': batch_header.get('payout_batch_id', 'UNKNOWN'),
        'status': batch_header.get('batch_status', 'UNKNOWN'),
    }


# ── Sheet Operations ───────────────────────────────────────────────────────────

def setup_sheet():
    """Create and format the Payout Tracker tab."""
    import gspread
    from gspread.utils import rowcol_to_a1

    log("Setting up Payout Tracker tab...")
    ss = get_spreadsheet()

    # Check if tab exists
    tab = get_or_create_tab(ss)
    if tab:
        log(f"Tab '{TAB_NAME}' already exists. Updating formatting...")
        ws = tab
    else:
        ws = ss.add_worksheet(title=TAB_NAME, rows=200, cols=13)
        log(f"Created new tab '{TAB_NAME}'")

    # ── Summary Section (rows 1-5) ──
    summary_data = [
        ['PAYOUT TRACKER — Pure Technology / AICIV Revenue Split', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['Total Revenue', '=SUM(D8:D1000)', '', 'Total Paid to Corey', '=SUMPRODUCT((J8:J1000="Sent")*(H8:H1000))', '',
         'Total Pending', '=SUMPRODUCT((J8:J1000="Pending Approval")*(H8:H1000))', '',
         'Total Pure Tech', '=SUM(I8:I1000)', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['Split: 60% AICIV / 40% Pure Tech | Ops Fee: $35 | Referral: 5% | PayPal: weaver.aiciv@gmail.com', '', '', '', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', '', '', '', ''],
    ]

    # ── Header Row (row 7) ──
    headers = [
        'Date', 'Customer Name', 'Tier', 'Gross Payment ($)',
        'AICIV Ops Fee ($35)', 'Referral Fee (5%)', 'Net After Fees',
        "Corey's Share (60%)", 'Pure Tech Share (40%)',
        'Payout Status', 'Payout ID', 'Payout Date', 'Notes'
    ]
    summary_data.append(headers)

    # Write all at once
    ws.update(values=summary_data, range_name='A1:M7', value_input_option='USER_ENTERED')

    # ── Formatting ──
    # Bold header row
    ws.format('A7:M7', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.3},
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
    })

    # Bold title
    ws.format('A1', {
        'textFormat': {'bold': True, 'fontSize': 14},
    })

    # Bold summary labels
    ws.format('A3', {'textFormat': {'bold': True}})
    ws.format('D3', {'textFormat': {'bold': True}})
    ws.format('G3', {'textFormat': {'bold': True}})
    ws.format('J3', {'textFormat': {'bold': True}})

    # Summary values - currency format
    ws.format('B3', {'numberFormat': {'type': 'CURRENCY', 'pattern': '$#,##0.00'}})
    ws.format('E3', {'numberFormat': {'type': 'CURRENCY', 'pattern': '$#,##0.00'}})
    ws.format('H3', {'numberFormat': {'type': 'CURRENCY', 'pattern': '$#,##0.00'}})
    ws.format('K3', {'numberFormat': {'type': 'CURRENCY', 'pattern': '$#,##0.00'}})

    # Currency format for money columns (D-I)
    ws.format('D8:I1000', {'numberFormat': {'type': 'CURRENCY', 'pattern': '$#,##0.00'}})

    # Column widths
    col_widths = [
        ('A', 120), ('B', 180), ('C', 120), ('D', 140),
        ('E', 140), ('F', 120), ('G', 130), ('H', 140),
        ('I', 140), ('J', 160), ('K', 200), ('L', 120), ('M', 200),
    ]
    sheet_id = ws.id
    col_requests = []
    for col_letter, width in col_widths:
        col_idx = ord(col_letter) - ord('A')
        col_requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': col_idx,
                    'endIndex': col_idx + 1,
                },
                'properties': {'pixelSize': width},
                'fields': 'pixelSize',
            }
        })

    # ── Conditional Formatting for Status Column (J) ──
    cond_rules = [
        # Pending Approval = yellow
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{'sheetId': sheet_id, 'startRowIndex': 7, 'endRowIndex': 1000,
                                'startColumnIndex': 9, 'endColumnIndex': 10}],
                    'booleanRule': {
                        'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': 'Pending Approval'}]},
                        'format': {'backgroundColor': {'red': 1, 'green': 0.95, 'blue': 0.6}},
                    }
                },
                'index': 0,
            }
        },
        # Approved = blue
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{'sheetId': sheet_id, 'startRowIndex': 7, 'endRowIndex': 1000,
                                'startColumnIndex': 9, 'endColumnIndex': 10}],
                    'booleanRule': {
                        'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': 'Approved'}]},
                        'format': {'backgroundColor': {'red': 0.6, 'green': 0.8, 'blue': 1}},
                    }
                },
                'index': 1,
            }
        },
        # Sent = green
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{'sheetId': sheet_id, 'startRowIndex': 7, 'endRowIndex': 1000,
                                'startColumnIndex': 9, 'endColumnIndex': 10}],
                    'booleanRule': {
                        'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': 'Sent'}]},
                        'format': {'backgroundColor': {'red': 0.6, 'green': 0.95, 'blue': 0.6}},
                    }
                },
                'index': 2,
            }
        },
        # Failed = red
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{'sheetId': sheet_id, 'startRowIndex': 7, 'endRowIndex': 1000,
                                'startColumnIndex': 9, 'endColumnIndex': 10}],
                    'booleanRule': {
                        'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': 'Failed'}]},
                        'format': {'backgroundColor': {'red': 1, 'green': 0.6, 'blue': 0.6}},
                    }
                },
                'index': 3,
            }
        },
    ]

    # Freeze header rows
    freeze_req = {
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {'frozenRowCount': 7},
            },
            'fields': 'gridProperties.frozenRowCount',
        }
    }

    all_requests = col_requests + cond_rules + [freeze_req]
    ss.batch_update({'requests': all_requests})

    log("Payout Tracker tab setup complete with formatting and conditional rules.")
    return ws


def add_payment(customer: str, tier: str, amount: float, notes: str = ''):
    """Add a new payment row to the Payout Tracker."""
    ss = get_spreadsheet()
    ws = get_or_create_tab(ss)
    if not ws:
        log("Tab not found. Run --setup-sheet first.")
        sys.exit(1)

    split = calculate_split(amount)
    today = datetime.now().strftime('%Y-%m-%d')

    # Find next empty row
    all_values = ws.col_values(1)  # Column A
    next_row = max(len(all_values) + 1, DATA_START_ROW)

    row_data = [
        today,                          # A: Date
        customer,                       # B: Customer Name
        tier,                           # C: Tier
        amount,                         # D: Gross Payment
        split['ops_fee'],               # E: Ops Fee
        split['referral'],              # F: Referral Fee
        split['net'],                   # G: Net After Fees
        split['corey_share'],           # H: Corey's Share
        split['pt_share'],             # I: PT Share
        'Pending Approval',            # J: Status
        '',                            # K: Payout ID
        '',                            # L: Payout Date
        notes,                         # M: Notes
    ]

    ws.update(values=[row_data], range_name=f'A{next_row}:M{next_row}', value_input_option='USER_ENTERED')

    log(f"Added payment: {customer} | {tier} | ${amount:.2f}")
    log(f"  Split: Corey ${split['corey_share']:.2f} | PT ${split['pt_share']:.2f}")
    log(f"  Row: {next_row} | Status: Pending Approval")

    # Also add formulas for rows after initial entry (so they auto-calc if gross changes)
    formulas = [
        [f'=D{next_row}-E{next_row}-F{next_row}'],  # G: Net
        [f'=G{next_row}*0.6'],                        # H: Corey
        [f'=G{next_row}*0.4'],                        # I: PT
    ]
    ws.update(values=[[f'=D{next_row}-E{next_row}-F{next_row}',
                f'=G{next_row}*0.6',
                f'=G{next_row}*0.4']],
              range_name=f'G{next_row}:I{next_row}',
              value_input_option='USER_ENTERED')

    # Also set E and F as formulas
    ws.update(values=[[35, f'=D{next_row}*0.05']],
              range_name=f'E{next_row}:F{next_row}',
              value_input_option='USER_ENTERED')

    return {
        'row': next_row,
        'customer': customer,
        'tier': tier,
        'gross': amount,
        'corey_share': split['corey_share'],
        'pt_share': split['pt_share'],
    }


def approve_payout(row: int):
    """Approve and fire a PayPal payout for a specific row."""
    ss = get_spreadsheet()
    ws = get_or_create_tab(ss)
    if not ws:
        log("Tab not found.")
        sys.exit(1)

    # Read the row
    row_data = ws.row_values(row)
    if len(row_data) < 10:
        log(f"Row {row} has insufficient data.")
        sys.exit(1)

    status = row_data[9] if len(row_data) > 9 else ''
    if status != 'Pending Approval':
        log(f"Row {row} status is '{status}', not 'Pending Approval'. Skipping.")
        sys.exit(1)

    customer = row_data[1]
    tier = row_data[2]
    gross = float(row_data[3].replace('$', '').replace(',', ''))
    corey_share = float(row_data[7].replace('$', '').replace(',', ''))

    log(f"Approving payout for {customer} ({tier}): ${corey_share:.2f} to {COREY_PAYPAL}")

    # Update status to Approved first
    ws.update_cell(row, COL['status'], 'Approved')

    try:
        result = fire_payout(corey_share, customer, tier, gross)
        payout_id = result['payout_batch_id']
        payout_status = result['status']
        now = datetime.now().strftime('%Y-%m-%d %H:%M')

        # Update row with payout details
        ws.update_cell(row, COL['status'], 'Sent')
        ws.update_cell(row, COL['payout_id'], payout_id)
        ws.update_cell(row, COL['payout_date'], now)

        log(f"Payout SENT: {payout_id} ({payout_status})")
        log(f"  ${corey_share:.2f} → {COREY_PAYPAL}")

        return {
            'success': True,
            'payout_id': payout_id,
            'amount': corey_share,
            'recipient': COREY_PAYPAL,
        }

    except Exception as e:
        ws.update_cell(row, COL['status'], 'Failed')
        ws.update_cell(row, COL['notes'], f'Error: {str(e)[:100]}')
        log(f"Payout FAILED: {e}")
        return {
            'success': False,
            'error': str(e),
        }


def show_status():
    """Show all pending payouts."""
    ss = get_spreadsheet()
    ws = get_or_create_tab(ss)
    if not ws:
        log("Tab not found.")
        return

    all_rows = ws.get_all_values()
    pending = []
    approved = []
    sent = []

    for i, row in enumerate(all_rows[DATA_START_ROW - 1:], start=DATA_START_ROW):
        if len(row) < 10 or not row[0]:
            continue
        status = row[9]
        entry = {
            'row': i,
            'date': row[0],
            'customer': row[1],
            'tier': row[2],
            'gross': row[3],
            'corey_share': row[7],
            'status': status,
        }
        if status == 'Pending Approval':
            pending.append(entry)
        elif status == 'Approved':
            approved.append(entry)
        elif status == 'Sent':
            sent.append(entry)

    print("\n" + "=" * 70)
    print("PAYOUT STATUS REPORT")
    print("=" * 70)

    if pending:
        print(f"\nPENDING APPROVAL ({len(pending)}):")
        print("-" * 50)
        for p in pending:
            print(f"  Row {p['row']}: {p['customer']} | {p['tier']} | Gross: {p['gross']} | Corey: {p['corey_share']}")
    else:
        print("\nNo pending payouts.")

    if approved:
        print(f"\nAPPROVED (awaiting send) ({len(approved)}):")
        for a in approved:
            print(f"  Row {a['row']}: {a['customer']} | {a['tier']} | Corey: {a['corey_share']}")

    if sent:
        print(f"\nSENT ({len(sent)}):")
        for s in sent:
            print(f"  Row {s['row']}: {s['customer']} | {s['tier']} | Corey: {s['corey_share']}")

    print(f"\nTOTAL: {len(pending)} pending | {len(approved)} approved | {len(sent)} sent")
    print("=" * 70)


def show_summary():
    """Show financial summary from the spreadsheet."""
    ss = get_spreadsheet()
    ws = get_or_create_tab(ss)
    if not ws:
        log("Tab not found.")
        return

    all_rows = ws.get_all_values()
    total_revenue = 0
    total_paid_corey = 0
    total_pending = 0
    total_pt = 0

    for row in all_rows[DATA_START_ROW - 1:]:
        if len(row) < 10 or not row[0]:
            continue
        try:
            gross = float(row[3].replace('$', '').replace(',', ''))
            corey = float(row[7].replace('$', '').replace(',', ''))
            pt = float(row[8].replace('$', '').replace(',', ''))
            status = row[9]
        except (ValueError, IndexError):
            continue

        total_revenue += gross
        total_pt += pt
        if status == 'Sent':
            total_paid_corey += corey
        elif status == 'Pending Approval':
            total_pending += corey

    print("\n" + "=" * 50)
    print("FINANCIAL SUMMARY")
    print("=" * 50)
    print(f"  Total Revenue:        ${total_revenue:>10,.2f}")
    print(f"  Total Paid to Corey:  ${total_paid_corey:>10,.2f}")
    print(f"  Total Pending:        ${total_pending:>10,.2f}")
    print(f"  Total Pure Tech:      ${total_pt:>10,.2f}")
    print("=" * 50)


# ── Webhook Mode ───────────────────────────────────────────────────────────────

def run_webhook():
    """Run Flask webhook listener for PayPal PAYMENT.SALE.COMPLETED events."""
    try:
        from flask import Flask, request as flask_request, jsonify
    except ImportError:
        log("Flask not installed. Install with: pip install flask")
        sys.exit(1)

    app = Flask(__name__)

    def verify_paypal_webhook(headers, body):
        """Verify PayPal webhook signature (best-effort, logs warning on failure).

        NOTE: `headers` must be a case-insensitive mapping (e.g. Flask's
        request.headers / Werkzeug Headers object).  Converting to a plain
        dict via dict() makes lookups case-SENSITIVE and breaks PayPal header
        matching (PayPal sends PAYPAL-AUTH-ALGO but Flask normalises to
        Paypal-Auth-Algo).
        """
        webhook_id = os.getenv('PAYPAL_WEBHOOK_ID', '')
        if not webhook_id:
            log("WARNING: PAYPAL_WEBHOOK_ID not set, skipping signature verification.")
            return True
        try:
            # Extract headers - try multiple case variants for robustness
            def get_header(name):
                """Get header value trying exact key, then falling back."""
                val = headers.get(name, '')
                if val:
                    return val
                # Try title-case (how Flask/Werkzeug normalises)
                title = '-'.join(w.capitalize() for w in name.split('-'))
                val = headers.get(title, '')
                if val:
                    return val
                return ''

            auth_algo = get_header('PAYPAL-AUTH-ALGO')
            cert_url = get_header('PAYPAL-CERT-URL')
            transmission_id = get_header('PAYPAL-TRANSMISSION-ID')
            transmission_sig = get_header('PAYPAL-TRANSMISSION-SIG')
            transmission_time = get_header('PAYPAL-TRANSMISSION-TIME')

            # Log extracted header values for debugging
            cert_url_short = cert_url[:40] + '...' if len(cert_url) > 40 else cert_url
            log(f"Webhook headers: auth_algo={auth_algo!r}, transmission_id={transmission_id!r}, "
                f"cert_url={cert_url_short!r}")

            token = get_paypal_token()
            verify_payload = {
                'auth_algo': auth_algo,
                'cert_url': cert_url,
                'transmission_id': transmission_id,
                'transmission_sig': transmission_sig,
                'transmission_time': transmission_time,
                'webhook_id': webhook_id,
                'webhook_event': json.loads(body) if isinstance(body, str) else body,
            }
            resp = requests.post(
                f"{PAYPAL_BASE_URL}/v1/notifications/verify-webhook-signature",
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
                json=verify_payload,
                timeout=30,
            )
            result = resp.json()
            verified = result.get('verification_status') == 'SUCCESS'
            if not verified:
                log(f"Webhook signature verification FAILED: {result}")
            return verified
        except Exception as e:
            log(f"Webhook verification error (allowing): {e}")
            return True  # Fail-open to avoid missing payments; log for review

    @app.route('/paypal/webhook', methods=['POST'])
    def handle_webhook():
        # Verify signature if configured
        if not verify_paypal_webhook(flask_request.headers, flask_request.get_data(as_text=True)):
            log("Rejecting webhook: invalid signature")
            return jsonify({'status': 'rejected', 'reason': 'invalid signature'}), 403

        data = flask_request.json
        event_type = data.get('event_type', '')

        if event_type != 'PAYMENT.SALE.COMPLETED':
            return jsonify({'status': 'ignored', 'event': event_type}), 200

        resource = data.get('resource', {})
        amount_data = resource.get('amount', {})
        gross = float(amount_data.get('total', 0))
        customer = resource.get('custom', 'Unknown Customer')

        # Determine tier from amount
        # 2026-05-17: Awakened repriced $149 → $297 (Jared greenlit). $149 retained
        # for legacy capture replay of pre-cutover subscriptions. Split percentages
        # (5%/60%/40%) UNCHANGED — only tier lookup widens.
        tier_map = {149: 'Awakened', 297: 'Awakened', 499: 'Partnered', 999: 'Unified',
                    197: 'Awakened', 579: 'Partnered', 1089: 'Unified'}
        tier = tier_map.get(int(gross), 'Enterprise')

        log(f"Webhook: {event_type} | {customer} | ${gross} | {tier}")

        try:
            result = add_payment(customer, tier, gross, notes=f'Via webhook: {resource.get("id", "")}')

            # ── Webhook Firehose (non-blocking post-hook) ───────────────────
            # Fires payment.completed to all enabled subscribers in
            # config/payment_webhook_subscribers.json. Does NOT affect split
            # logic — delivery runs in background threads.
            try:
                from webhook_firehose import get_default_firehose
                firehose = get_default_firehose()
                firehose.fire_event('payment.completed', {
                    'tier': tier,
                    'amount': gross,
                    'currency': amount_data.get('currency', 'USD'),
                    'customer_email': resource.get('payer', {}).get('email_address', ''),
                    'customer_name': customer,
                    'order_id': resource.get('id', ''),
                    'subscription_id': resource.get('billing_agreement_id', ''),
                    'referral_code': resource.get('custom_id', ''),
                    'source_page': 'paypal.webhook',
                })
            except Exception as fh_err:
                log(f"Firehose dispatch error (non-fatal): {fh_err}")

            # Check if auto-approve is enabled (20+ successful payouts)
            if is_auto_approve_enabled():
                log(f"Auto-approve ACTIVE. Firing payout for row {result['row']} automatically.")
                payout_result = approve_payout(result['row'])
                if payout_result.get('success'):
                    send_telegram_notification(
                        f"*[AF# Auto-Payout Sent]*\n"
                        f"Customer: {customer}\n"
                        f"Amount to Corey: ${result['corey_share']:.2f}\n"
                        f"Payout ID: {payout_result['payout_id']}\n"
                        f"(Auto-approved: 20+ successful transactions)"
                    )
                else:
                    notify_portal(result)
                return jsonify({'status': 'auto-approved', 'row': result['row']}), 200
            else:
                # Send notification for manual approval
                notify_portal(result)
                return jsonify({'status': 'recorded', 'row': result['row']}), 200
        except Exception as e:
            log(f"Webhook error: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/paypal/webhook', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'service': 'paypal-auto-split'}), 200

    log("Starting webhook listener on port 8960...")
    app.run(host='0.0.0.0', port=8960, debug=False)


def count_successful_payouts() -> int:
    """Count the number of successfully sent payouts in the spreadsheet."""
    try:
        ss = get_spreadsheet()
        ws = get_or_create_tab(ss)
        if not ws:
            return 0
        all_rows = ws.get_all_values()
        count = 0
        for row in all_rows[DATA_START_ROW - 1:]:
            if len(row) > 9 and row[9] == 'Sent':
                count += 1
        return count
    except Exception as e:
        log(f"Error counting payouts: {e}")
        return 0


def is_auto_approve_enabled() -> bool:
    """Check if we've hit the threshold for auto-approval."""
    count = count_successful_payouts()
    enabled = count >= AUTO_APPROVE_THRESHOLD
    log(f"Auto-approve check: {count}/{AUTO_APPROVE_THRESHOLD} successful payouts. Auto-approve: {'ENABLED' if enabled else 'DISABLED'}")
    return enabled


def send_telegram_notification(message: str):
    """Send notification via Telegram to Jared."""
    try:
        config_path = ROOT / 'config' / 'telegram_config.json'
        if config_path.exists():
            with open(config_path) as f:
                tg_config = json.load(f)
            token = tg_config.get('bot_token', '')
            chat_id = '548906264'
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            resp = requests.post(url, data={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown',
            }, timeout=10)
            if resp.status_code == 200:
                log("Telegram notification sent.")
            else:
                log(f"Telegram notification failed: {resp.status_code}")
        else:
            log("Telegram config not found, skipping notification.")
    except Exception as e:
        log(f"Telegram notification error: {e}")


def notify_portal(payment_info: dict):
    """Send notification to portal about new pending payout."""
    try:
        msg = (
            f"[AF# New Payment Received]\n"
            f"Customer: {payment_info['customer']}\n"
            f"Tier: {payment_info['tier']}\n"
            f"Gross: ${payment_info['gross']:.2f}\n"
            f"Corey's Share: ${payment_info['corey_share']:.2f}\n"
            f"PT Share: ${payment_info['pt_share']:.2f}\n"
            f"Row: {payment_info['row']}\n"
            f"Status: Pending Approval\n\n"
            f"Approve with: python3 tools/paypal_auto_split.py --approve --row {payment_info['row']}"
        )
        # Write to portal outbox
        portal_file = ROOT / 'exports' / 'portal-files' / 'payout-notification.txt'
        portal_file.parent.mkdir(parents=True, exist_ok=True)
        with open(portal_file, 'w') as f:
            f.write(msg)
        log(f"Portal notification written to {portal_file}")

        # Also send Telegram notification
        tg_msg = (
            f"*[AF# Payment Received]*\n"
            f"Customer: {payment_info['customer']}\n"
            f"Tier: {payment_info['tier']}\n"
            f"Gross: ${payment_info['gross']:.2f}\n"
            f"Corey: ${payment_info['corey_share']:.2f} | PT: ${payment_info['pt_share']:.2f}\n"
            f"Status: Pending Approval\n"
            f"Row: {payment_info['row']}"
        )
        send_telegram_notification(tg_msg)
    except Exception as e:
        log(f"Portal notification failed: {e}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='PayPal Auto-Split Payout System')
    parser.add_argument('--setup-sheet', action='store_true', help='Create/format the Payout Tracker tab')
    parser.add_argument('--add-payment', action='store_true', help='Add a new payment')
    parser.add_argument('--approve', action='store_true', help='Approve and fire a payout')
    parser.add_argument('--status', action='store_true', help='Show all pending payouts')
    parser.add_argument('--summary', action='store_true', help='Show financial summary')
    parser.add_argument('--webhook', action='store_true', help='Run webhook listener')
    parser.add_argument('--customer', type=str, help='Customer name')
    parser.add_argument('--tier', type=str, help='Tier (Awakened/Partnered/Unified/Enterprise)')
    parser.add_argument('--amount', type=float, help='Gross payment amount')
    parser.add_argument('--row', type=int, help='Row number to approve')
    parser.add_argument('--notes', type=str, default='', help='Optional notes')
    parser.add_argument('--sandbox', action='store_true', help='Use PayPal sandbox')

    args = parser.parse_args()

    if args.sandbox:
        global PAYPAL_CLIENT_ID, PAYPAL_SECRET, PAYPAL_BASE_URL
        PAYPAL_CLIENT_ID = os.getenv('PAYPAL_SANDBOX_CLIENT_ID', '')
        PAYPAL_SECRET = os.getenv('PAYPAL_SANDBOX_SECRET', '')
        PAYPAL_BASE_URL = 'https://api-m.sandbox.paypal.com'
        log("Using PayPal SANDBOX mode")

    if args.setup_sheet:
        setup_sheet()
    elif args.add_payment:
        if not args.customer or not args.tier or not args.amount:
            parser.error("--add-payment requires --customer, --tier, and --amount")
        add_payment(args.customer, args.tier, args.amount, args.notes)
    elif args.approve:
        if not args.row:
            parser.error("--approve requires --row")
        approve_payout(args.row)
    elif args.status:
        show_status()
    elif args.summary:
        show_summary()
    elif args.webhook:
        run_webhook()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
