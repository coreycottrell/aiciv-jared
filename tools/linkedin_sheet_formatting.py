#!/usr/bin/env python3
"""
Apply conditional formatting to LinkedIn Post Content Calendar spreadsheet.
Colors column L (Status) based on values:
  Draft     = Yellow
  Approved  = Blue
  Scheduled = Light blue/cyan
  Posted    = Green
  Failed    = Red
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

SPREADSHEET_ID = "1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4"
TAB_NAME = "NEW LINKEDIN POST CONTENT CALENDAR"


def get_credentials():
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
        raise FileNotFoundError("No gdrive_token.json found.")

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

    return creds


def get_sheet_id(service, spreadsheet_id, tab_name):
    """Get the sheetId for a given tab name."""
    resp = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in resp['sheets']:
        if sheet['properties']['title'] == tab_name:
            return sheet['properties']['sheetId']
    raise ValueError(f"Tab '{tab_name}' not found. Available: {[s['properties']['title'] for s in resp['sheets']]}")


def build_condition_rule(sheet_id, text, color_rgb):
    """Build a conditional formatting rule for column L (index 11), rows 2+."""
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": 1,       # Skip header row
                    "startColumnIndex": 11,    # Column L (0-indexed)
                    "endColumnIndex": 12,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_EQ",
                        "values": [{"userEnteredValue": text}]
                    },
                    "format": {
                        "backgroundColor": {
                            "red": color_rgb[0],
                            "green": color_rgb[1],
                            "blue": color_rgb[2],
                        }
                    }
                }
            },
            "index": 0
        }
    }


def main():
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    # Get the sheet ID for the target tab
    sheet_id = get_sheet_id(service, SPREADSHEET_ID, TAB_NAME)
    print(f"Found tab '{TAB_NAME}' with sheetId: {sheet_id}")

    # First, clear any existing conditional formatting on column L
    # Get existing rules
    resp = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets.conditionalFormats,sheets.properties.sheetId"
    ).execute()

    delete_requests = []
    for sheet in resp.get('sheets', []):
        if sheet['properties']['sheetId'] == sheet_id:
            existing_rules = sheet.get('conditionalFormats', [])
            # Delete existing rules on column L (reverse order to maintain indices)
            for i in range(len(existing_rules) - 1, -1, -1):
                for r in existing_rules[i].get('ranges', []):
                    if r.get('startColumnIndex') == 11 and r.get('endColumnIndex') == 12:
                        delete_requests.append({
                            "deleteConditionalFormatRule": {
                                "sheetId": sheet_id,
                                "index": i
                            }
                        })
                        break

    if delete_requests:
        print(f"Removing {len(delete_requests)} existing conditional format rules on column L...")
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": delete_requests}
        ).execute()

    # Define status colors (RGB 0-1 scale)
    status_colors = {
        "Draft":     (1.0, 0.95, 0.6),      # Yellow
        "Approved":  (0.44, 0.58, 0.86),     # Blue
        "Scheduled": (0.68, 0.85, 0.95),     # Light blue/cyan
        "Posted":    (0.57, 0.82, 0.57),     # Green
        "Failed":    (0.92, 0.49, 0.49),     # Red
    }

    # Build add requests
    add_requests = []
    for status, rgb in status_colors.items():
        add_requests.append(build_condition_rule(sheet_id, status, rgb))

    print(f"Applying {len(add_requests)} conditional formatting rules...")
    result = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": add_requests}
    ).execute()

    print(f"Success! {len(result.get('replies', []))} rules applied.")
    print("\nFormatting applied to column L (Status):")
    for status, rgb in status_colors.items():
        print(f"  {status:12s} -> RGB({rgb[0]:.2f}, {rgb[1]:.2f}, {rgb[2]:.2f})")


if __name__ == "__main__":
    main()
