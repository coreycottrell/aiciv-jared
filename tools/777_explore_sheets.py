#!/usr/bin/env python3
"""
Quick exploration script to discover the actual sheet structure
before building the full data fetcher.
"""
import json
import sys

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

SPREADSHEET_ID = '1PlDMMDLgFGih66Ag5MvkwL1AYipZ8MqFECGh-5AS49o'
SERVICE_ACCOUNT_FILE = '/home/jared/projects/AI-CIV/aether/.credentials/google-drive-service-account.json'

def main():
    print("Connecting to Google Sheets...")
    # Try without delegation first — service account must be shared on the spreadsheet
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    gc = gspread.authorize(creds)

    print(f"Opening spreadsheet: {SPREADSHEET_ID}")
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)

    print(f"\nSpreadsheet title: {spreadsheet.title}")
    print(f"\nAll worksheets ({len(spreadsheet.worksheets())}):")
    for i, ws in enumerate(spreadsheet.worksheets()):
        print(f"  [{i}] id={ws.id} title='{ws.title}' rows={ws.row_count} cols={ws.col_count}")

    # Sample key sheets mentioned in the task
    target_sheets = [31, 37, 29, 15, 9, 10, 6, 11]
    # We'll look at sheets by index (0-based) and title pattern

    print("\n--- Sampling Sheet Content ---")
    for i, ws in enumerate(spreadsheet.worksheets()):
        # Only explore first 40 sheets for now
        if i > 45:
            break
        try:
            # Get just first 5 rows, 10 cols to understand structure
            vals = ws.get('A1:J5')
            print(f"\nSheet [{i}] '{ws.title}':")
            for row in vals[:3]:
                print(f"  {row[:8]}")
        except Exception as e:
            print(f"\nSheet [{i}] '{ws.title}': ERROR - {e}")

if __name__ == '__main__':
    main()
