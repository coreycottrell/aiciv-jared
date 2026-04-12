#!/usr/bin/env python3
"""
Google Calendar OAuth2 Setup for Aether

This script performs one-time OAuth2 authentication to enable full Google Calendar
access as the account owner (purebrain@puremarketing.ai or associated account).

REQUIREMENTS:
1. OAuth2 credentials downloaded from Google Cloud Console
   - Project: aether-integration (or your project)
   - APIs & Services > Credentials > Create OAuth Client ID
   - Application type: Desktop app
   - Download JSON and save to: .credentials/oauth-credentials.json

2. Enable Google Calendar API in your Google Cloud project:
   - APIs & Services > Library > Search "Google Calendar API" > Enable

3. Run this script: python tools/gcal_oauth_setup.py

4. Visit the URL printed in your browser
   - Log in with the account that has the calendar
   - Grant Calendar access
   - If running on headed machine: auto-completes
   - If running headless: copy redirect URL and paste when prompted

USAGE:
    # Standard (tries local server first)
    python tools/gcal_oauth_setup.py

    # Force manual mode (for completely headless servers)
    python tools/gcal_oauth_setup.py --manual

Author: Aether
Date: 2026-02-11
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError:
    print("ERROR: Required libraries not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2")
    sys.exit(1)

# Base paths
BASE_PATH = Path(__file__).parent.parent
CREDENTIALS_DIR = BASE_PATH / ".credentials"
OAUTH_CREDS_FILE = CREDENTIALS_DIR / "oauth-credentials.json"
OAUTH_TOKEN_FILE = CREDENTIALS_DIR / "oauth-token-calendar.json"

# Scopes for Calendar access
SCOPES = [
    'https://www.googleapis.com/auth/calendar',           # Full calendar access
    'https://www.googleapis.com/auth/calendar.events',    # Events access
]


def check_existing_token():
    """Check if we already have a valid OAuth token."""
    if not OAUTH_TOKEN_FILE.exists():
        return None

    try:
        creds = Credentials.from_authorized_user_file(str(OAUTH_TOKEN_FILE), SCOPES)

        if creds.valid:
            print(f"[OK] Existing OAuth token is valid")
            print(f"     Token file: {OAUTH_TOKEN_FILE}")
            return creds

        if creds.expired and creds.refresh_token:
            print("[INFO] Token expired, refreshing...")
            creds.refresh(Request())
            save_token(creds)
            print(f"[OK] Token refreshed successfully")
            return creds

        print("[WARN] Token invalid and cannot be refreshed. Re-authenticating...")
        return None

    except Exception as e:
        print(f"[WARN] Error loading token: {e}")
        return None


def save_token(creds):
    """Save credentials to token file."""
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else SCOPES,
    }

    with open(OAUTH_TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

    # Secure the token file
    os.chmod(OAUTH_TOKEN_FILE, 0o600)
    print(f"[OK] Token saved to {OAUTH_TOKEN_FILE}")


def run_oauth_flow_local_server():
    """Run OAuth flow using local server."""
    print("\n" + "="*70)
    print("OAUTH2 AUTHENTICATION - Local Server Mode (Calendar)")
    print("="*70)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(OAUTH_CREDS_FILE),
        scopes=SCOPES
    )

    print("\n[STEP 1] Starting local server on http://localhost:8080")
    print("\n[STEP 2] Visit this URL to authorize (will be printed below):")
    print("         - Log in with the Google account that has your calendar")
    print("         - Grant all requested Calendar permissions")
    print("\n[WAITING] Server listening for OAuth callback...\n")

    try:
        creds = flow.run_local_server(
            host='localhost',
            port=8080,
            open_browser=False,
            authorization_prompt_message='Visit this URL to authorize:\n\n{url}\n',
            success_message='Authorization complete! You may close this window.',
            timeout_seconds=300
        )

        print("\n[OK] Authorization successful!")
        save_token(creds)
        return creds

    except Exception as e:
        print(f"\n[ERROR] Local server flow failed: {e}")
        print("\nTry running with --manual flag for manual copy-paste flow.")
        return None


def run_oauth_flow_manual():
    """Run OAuth flow with manual code entry."""
    print("\n" + "="*70)
    print("OAUTH2 AUTHENTICATION - Manual Mode (Calendar)")
    print("="*70)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(OAUTH_CREDS_FILE),
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    print("\n[STEP 1] Visit this URL in your browser:")
    print("         (Copy the entire URL below)")
    print("\n" + "-"*70)
    print(auth_url)
    print("-"*70)

    print("\n[STEP 2] Log in with the Google account that has your calendar")
    print("[STEP 3] Grant all requested Calendar permissions")
    print("[STEP 4] You will be redirected to a page showing an authorization code")
    print("         OR the URL will contain 'code=' parameter")

    print("\n[STEP 5] Paste the authorization code OR full redirect URL below:")

    user_input = input("\nAuthorization code or URL: ").strip()

    if user_input.startswith('http'):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(user_input)
        code = parse_qs(parsed.query).get('code', [None])[0]
        if not code:
            print("[ERROR] Could not extract code from URL")
            return None
    else:
        code = user_input

    try:
        flow.fetch_token(code=code)
        creds = flow.credentials

        print("\n[OK] Authorization successful!")
        save_token(creds)
        return creds

    except Exception as e:
        print(f"\n[ERROR] Failed to exchange code for token: {e}")
        return None


def verify_access(creds):
    """Verify that we have working Calendar access."""
    try:
        from googleapiclient.discovery import build
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        print("\n[VERIFY] Testing Calendar access...")

        service = build('calendar', 'v3', credentials=creds)

        # Get calendar list
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])

        print(f"[OK] Found {len(calendars)} calendars:")
        for cal in calendars[:5]:  # Show first 5
            primary = " (PRIMARY)" if cal.get('primary') else ""
            print(f"     - {cal.get('summary', 'Untitled')}{primary}")

        if len(calendars) > 5:
            print(f"     ... and {len(calendars) - 5} more")

        # Try to list upcoming events
        now = datetime.now(ZoneInfo('America/New_York')).isoformat()
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=3,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        print(f"[OK] Can read events. Found {len(events)} upcoming events.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"     - {event.get('summary', 'No title')} @ {start}")

        return True

    except Exception as e:
        print(f"[ERROR] Calendar access verification failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Set up OAuth2 authentication for Google Calendar'
    )
    parser.add_argument(
        '--manual',
        action='store_true',
        help='Use manual code entry (for completely headless servers)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Only verify existing token without re-authenticating'
    )
    parser.add_argument(
        '--refresh',
        action='store_true',
        help='Force token refresh'
    )

    args = parser.parse_args()

    print("\n" + "="*70)
    print("Google Calendar OAuth2 Setup for Aether")
    print("="*70)

    # Check for OAuth credentials file
    if not OAUTH_CREDS_FILE.exists():
        print(f"\n[ERROR] OAuth credentials file not found!")
        print(f"        Expected: {OAUTH_CREDS_FILE}")
        print("\nTo create OAuth credentials:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Select your project (e.g., aether-integration)")
        print("3. Click 'Create Credentials' > 'OAuth client ID'")
        print("4. Application type: 'Desktop app'")
        print("5. Download JSON and save to: .credentials/oauth-credentials.json")
        print("\nALSO: Make sure Google Calendar API is enabled:")
        print("      APIs & Services > Library > Google Calendar API > Enable")
        sys.exit(1)

    print(f"[OK] Found OAuth credentials: {OAUTH_CREDS_FILE}")

    # Check existing token
    creds = check_existing_token()

    if args.verify:
        if creds:
            verify_access(creds)
        else:
            print("[ERROR] No valid token to verify. Run without --verify to authenticate.")
        sys.exit(0 if creds else 1)

    if args.refresh and creds and creds.refresh_token:
        print("[INFO] Forcing token refresh...")
        creds.refresh(Request())
        save_token(creds)
        verify_access(creds)
        sys.exit(0)

    # If we don't have valid creds, run OAuth flow
    if not creds:
        if args.manual:
            creds = run_oauth_flow_manual()
        else:
            creds = run_oauth_flow_local_server()

        if not creds:
            print("\n[FAILED] Authentication failed.")
            sys.exit(1)

    # Verify access
    verify_access(creds)

    print("\n" + "="*70)
    print("SETUP COMPLETE")
    print("="*70)
    print(f"\nOAuth token saved to: {OAUTH_TOKEN_FILE}")
    print("\nThe gcal_manager.py will now automatically use OAuth credentials")
    print("for full Calendar access.")
    print("\nYou can now:")
    print("  python tools/gcal_manager.py calendars    # List calendars")
    print("  python tools/gcal_manager.py events       # List upcoming events")
    print("  python tools/gcal_manager.py today        # Today's events")
    print("  python tools/gcal_manager.py quick 'Meeting tomorrow at 3pm'")


if __name__ == '__main__':
    main()
