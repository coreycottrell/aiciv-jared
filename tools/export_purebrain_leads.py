#!/usr/bin/env python3
"""
Pure Brain Leads Exporter

Exports AI names and conversation data from Pure Brain web conversations to:
1. CSV file (always created)
2. Google Sheets (optional, requires service account with shared sheet)

Usage:
    python3 tools/export_purebrain_leads.py                    # CSV only
    python3 tools/export_purebrain_leads.py --sheets SHEET_ID  # CSV + Google Sheets

The SHEET_ID is the long ID from your Google Sheets URL:
    https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit

To use Google Sheets:
1. Create a new Google Sheet
2. Share it with: aether-drive-access@aether-integration.iam.gserviceaccount.com (Editor)
3. Copy the sheet ID from the URL
4. Run: python3 tools/export_purebrain_leads.py --sheets YOUR_SHEET_ID
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Paths
BASE_PATH = Path(__file__).parent.parent
JSONL_PATH = BASE_PATH / "logs" / "purebrain_web_conversations.jsonl"
CSV_OUTPUT_PATH = BASE_PATH / "exports" / "purebrain_leads.csv"
CREDENTIALS_PATH = BASE_PATH / ".credentials" / "google-drive-service-account.json"

# Google Sheets scope
SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def load_conversations() -> List[Dict[str, Any]]:
    """Load all conversations from JSONL file."""
    conversations = []

    if not JSONL_PATH.exists():
        print(f"Error: JSONL file not found at {JSONL_PATH}")
        return conversations

    with open(JSONL_PATH, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                conversations.append(data)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping malformed line {line_num}: {e}")

    return conversations


def extract_leads(conversations: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Extract lead information from conversations."""
    leads = []

    for conv in conversations:
        # Get AI name (the key field Jared wants to see)
        ai_name = conv.get('aiName', '')

        # Get user name if provided
        user_name = conv.get('userName', '')

        # Get timestamp
        timestamp = conv.get('server_timestamp', '')
        if timestamp:
            # Parse and format nicely
            try:
                dt = datetime.fromisoformat(timestamp.replace('+00:00', '+0000').replace('Z', '+0000'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except (ValueError, TypeError):
                pass  # Keep original if parsing fails

        # Get session ID
        session_id = conv.get('session_id', 'unknown')

        # Get first user message (if any)
        first_user_message = ''
        messages = conv.get('messages', [])
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                # Truncate long messages
                if len(content) > 200:
                    content = content[:200] + '...'
                first_user_message = content
                break

        # Count messages
        message_count = len(messages)
        user_message_count = sum(1 for m in messages if m.get('role') == 'user')

        # Get IP (might be useful for deduplication)
        client_ip = conv.get('client_ip', '')

        # Only include entries that have meaningful data
        # (Skip entries that are just system messages with no user interaction)
        has_content = ai_name or user_name or first_user_message

        leads.append({
            'ai_name': ai_name,
            'user_name': user_name,
            'first_message': first_user_message,
            'timestamp': timestamp,
            'session_id': session_id,
            'message_count': str(message_count),
            'user_messages': str(user_message_count),
            'client_ip': client_ip,
            'has_content': 'Yes' if has_content else 'No'
        })

    return leads


def export_to_csv(leads: List[Dict[str, str]], output_path: Path) -> bool:
    """Export leads to CSV file."""
    # Ensure exports directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    headers = ['AI Name', 'User Name', 'First Message', 'Timestamp',
               'Session ID', 'Total Messages', 'User Messages', 'Client IP', 'Has Content']

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for lead in leads:
                writer.writerow([
                    lead['ai_name'],
                    lead['user_name'],
                    lead['first_message'],
                    lead['timestamp'],
                    lead['session_id'],
                    lead['message_count'],
                    lead['user_messages'],
                    lead['client_ip'],
                    lead['has_content']
                ])

        print(f"CSV exported to: {output_path}")
        return True
    except Exception as e:
        print(f"Error writing CSV: {e}")
        return False


def export_to_sheets(leads: List[Dict[str, str]], sheet_id: str) -> bool:
    """Export leads to Google Sheets."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        print("Google API libraries not installed.")
        print("Run: pip install google-auth google-api-python-client")
        return False

    if not CREDENTIALS_PATH.exists():
        print(f"Error: Credentials not found at {CREDENTIALS_PATH}")
        return False

    try:
        # Authenticate
        credentials = service_account.Credentials.from_service_account_file(
            str(CREDENTIALS_PATH),
            scopes=SHEETS_SCOPES
        )

        service = build('sheets', 'v4', credentials=credentials)

        # Prepare data
        headers = ['AI Name', 'User Name', 'First Message', 'Timestamp',
                   'Session ID', 'Total Messages', 'User Messages', 'Client IP', 'Has Content']

        values = [headers]
        for lead in leads:
            values.append([
                lead['ai_name'],
                lead['user_name'],
                lead['first_message'],
                lead['timestamp'],
                lead['session_id'],
                lead['message_count'],
                lead['user_messages'],
                lead['client_ip'],
                lead['has_content']
            ])

        # Clear existing data and write new data
        # First, clear the sheet
        service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range='Sheet1!A:Z'
        ).execute()

        # Write new data
        body = {'values': values}
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='Sheet1!A1',
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"Google Sheets updated: {result.get('updatedCells')} cells")
        print(f"View at: https://docs.google.com/spreadsheets/d/{sheet_id}")
        return True

    except Exception as e:
        print(f"Error updating Google Sheets: {e}")
        if 'HttpError' in str(type(e)):
            print("\nMake sure you've shared the sheet with:")
            print("  aether-drive-access@aether-integration.iam.gserviceaccount.com")
        return False


def print_summary(leads: List[Dict[str, str]]):
    """Print a summary of the leads data."""
    total = len(leads)
    with_ai_name = sum(1 for l in leads if l['ai_name'])
    with_user_name = sum(1 for l in leads if l['user_name'])
    with_content = sum(1 for l in leads if l['has_content'] == 'Yes')

    print("\n" + "="*50)
    print("PURE BRAIN LEADS SUMMARY")
    print("="*50)
    print(f"Total conversations:     {total}")
    print(f"With AI name set:        {with_ai_name}")
    print(f"With user name set:      {with_user_name}")
    print(f"With meaningful content: {with_content}")
    print("="*50)

    # Show AI names if any
    if with_ai_name > 0:
        print("\nAI Names Created:")
        ai_names = [l['ai_name'] for l in leads if l['ai_name']]
        for name in ai_names:
            print(f"  - {name}")


def main():
    parser = argparse.ArgumentParser(
        description='Export Pure Brain leads to CSV and optionally Google Sheets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--sheets', '-s',
        metavar='SHEET_ID',
        help='Google Sheet ID to export to (get from URL)'
    )
    parser.add_argument(
        '--csv-only', '-c',
        action='store_true',
        help='Export to CSV only (default if --sheets not specified)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=CSV_OUTPUT_PATH,
        help=f'CSV output path (default: {CSV_OUTPUT_PATH})'
    )

    args = parser.parse_args()

    print("Loading conversations...")
    conversations = load_conversations()

    if not conversations:
        print("No conversations found!")
        return 1

    print(f"Found {len(conversations)} conversation entries")

    print("Extracting lead information...")
    leads = extract_leads(conversations)

    # Print summary
    print_summary(leads)

    # Export to CSV (always)
    print("\nExporting to CSV...")
    csv_success = export_to_csv(leads, args.output)

    # Export to Google Sheets (if requested)
    if args.sheets:
        print("\nExporting to Google Sheets...")
        sheets_success = export_to_sheets(leads, args.sheets)
        if not sheets_success:
            return 1

    if csv_success:
        print("\nDone! Your leads are ready.")
        return 0
    return 1


if __name__ == '__main__':
    exit(main())
