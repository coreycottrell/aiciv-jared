#!/usr/bin/env python3
"""
Google Drive OAuth2 Setup for Aether

This script performs one-time OAuth2 authentication to enable full Google Drive
access as the account owner (purebrain@puremarketing.ai), bypassing service account
quota limits.

REQUIREMENTS:
1. OAuth2 credentials downloaded from Google Cloud Console
   - Project: aether-integration
   - APIs & Services > Credentials > Create OAuth Client ID
   - Application type: Desktop app
   - Download JSON and save to: .credentials/oauth-credentials.json

2. Run this script: python tools/gdrive_oauth_setup.py

3. Visit the URL printed in your browser (on any machine)
   - Log in as purebrain@puremarketing.ai
   - Grant Drive access
   - If running on headed machine: auto-completes
   - If running headless: copy redirect URL and paste when prompted

USAGE:
    # Standard (tries local server first)
    python tools/gdrive_oauth_setup.py

    # Force manual mode (for completely headless servers)
    python tools/gdrive_oauth_setup.py --manual

Author: api-architect agent
Date: 2026-02-04
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
OAUTH_TOKEN_FILE = CREDENTIALS_DIR / "oauth-token.json"

# Scopes for full Drive access
SCOPES = [
    'https://www.googleapis.com/auth/drive',           # Full Drive access
    'https://www.googleapis.com/auth/spreadsheets',    # Full Sheets access
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
    """
    Run OAuth flow using local server.

    This starts a local HTTP server on port 8080. After user authorizes,
    Google redirects to localhost:8080 with the auth code.

    Works when:
    - Running on a machine with a browser, OR
    - Running headless but port 8080 is accessible from user's browser
    """
    print("\n" + "="*70)
    print("OAUTH2 AUTHENTICATION - Local Server Mode")
    print("="*70)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(OAUTH_CREDS_FILE),
        scopes=SCOPES
    )

    print("\n[STEP 1] Starting local server on http://localhost:8080")
    print("\n[STEP 2] Visit this URL to authorize (will be printed below):")
    print("         - Log in as: purebrain@puremarketing.ai")
    print("         - Grant all requested permissions")
    print("\n[WAITING] Server listening for OAuth callback...\n")

    try:
        creds = flow.run_local_server(
            host='localhost',
            port=8080,
            open_browser=False,  # Don't try to open browser (we're likely headless)
            authorization_prompt_message='Visit this URL to authorize:\n\n{url}\n',
            success_message='Authorization complete! You may close this window.',
            timeout_seconds=300  # 5 minute timeout
        )

        print("\n[OK] Authorization successful!")
        save_token(creds)
        return creds

    except Exception as e:
        print(f"\n[ERROR] Local server flow failed: {e}")
        print("\nTry running with --manual flag for manual copy-paste flow.")
        return None


def run_oauth_flow_manual():
    """
    Run OAuth flow with manual code entry.

    This generates an auth URL, user visits it, then manually copies
    the authorization code or full redirect URL back.

    Works for completely headless servers where localhost is not accessible.
    """
    print("\n" + "="*70)
    print("OAUTH2 AUTHENTICATION - Manual Mode")
    print("="*70)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(OAUTH_CREDS_FILE),
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Out-of-band for manual flow
    )

    # Generate the authorization URL
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force consent to ensure we get refresh token
    )

    print("\n[STEP 1] Visit this URL in your browser:")
    print("         (Copy the entire URL below)")
    print("\n" + "-"*70)
    print(auth_url)
    print("-"*70)

    print("\n[STEP 2] Log in as: purebrain@puremarketing.ai")
    print("[STEP 3] Grant all requested permissions")
    print("[STEP 4] You will be redirected to a page showing an authorization code")
    print("         OR the URL will contain 'code=' parameter")

    print("\n[STEP 5] Paste the authorization code OR full redirect URL below:")

    user_input = input("\nAuthorization code or URL: ").strip()

    # Handle both cases: just the code, or full URL with code
    if user_input.startswith('http'):
        # User pasted full URL
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
    """Verify that we have working Drive access."""
    try:
        from googleapiclient.discovery import build

        print("\n[VERIFY] Testing Drive access...")

        service = build('drive', 'v3', credentials=creds)
        about = service.about().get(fields='user').execute()

        user_email = about.get('user', {}).get('emailAddress', 'unknown')
        user_name = about.get('user', {}).get('displayName', 'unknown')

        print(f"[OK] Connected as: {user_name} ({user_email})")

        # List some files to verify full access
        results = service.files().list(
            pageSize=5,
            fields="files(id, name)"
        ).execute()

        files = results.get('files', [])
        print(f"[OK] Can access Drive. Found {len(files)} files in root.")

        return True

    except Exception as e:
        print(f"[ERROR] Drive access verification failed: {e}")
        return False


def create_credentials_template():
    """Create a template for OAuth credentials if none exist."""
    template = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "aether-integration",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["http://localhost"]
        }
    }

    template_file = CREDENTIALS_DIR / "oauth-credentials.template.json"
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

    with open(template_file, 'w') as f:
        json.dump(template, f, indent=2)

    return template_file


def main():
    parser = argparse.ArgumentParser(
        description='Set up OAuth2 authentication for Google Drive'
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
    print("Google Drive OAuth2 Setup for Aether")
    print("="*70)

    # Check for OAuth credentials file
    if not OAUTH_CREDS_FILE.exists():
        print(f"\n[ERROR] OAuth credentials file not found!")
        print(f"        Expected: {OAUTH_CREDS_FILE}")
        print("\nTo create OAuth credentials:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Select project: aether-integration")
        print("3. Click 'Create Credentials' > 'OAuth client ID'")
        print("4. Application type: 'Desktop app'")
        print("5. Download JSON and save to: .credentials/oauth-credentials.json")

        template_file = create_credentials_template()
        print(f"\n[INFO] Created template at: {template_file}")
        print("       Fill in client_id and client_secret from Google Cloud Console")

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
    print("\nThe gdrive_manager.py will now automatically use OAuth credentials")
    print("for full Drive access as the account owner.")
    print("\nNo more service account quota limits!")


if __name__ == '__main__':
    main()
