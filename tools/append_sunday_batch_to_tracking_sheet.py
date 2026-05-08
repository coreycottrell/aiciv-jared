#!/usr/bin/env python3
"""Append the Sunday May 4-10 batch entries to the LinkedIn tracking spreadsheet."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SHEET_ID = "1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4"
TAB = "Linkedin Post Content Calendar"


def get_sheets():
    token_path = ROOT / '.credentials' / 'oauth-token.json'
    with open(token_path) as f:
        token_data = json.load(f)
    creds = OAuthCredentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes'),
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('sheets', 'v4', credentials=creds)


def main():
    svc = get_sheets()

    # Read existing rows to find next POST ID
    res = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=f"'{TAB}'!A:A"
    ).execute()
    existing = res.get('values', [])
    # Find max POST N
    max_id = 0
    for row in existing:
        if row and row[0].startswith("POST "):
            try:
                max_id = max(max_id, int(row[0].split()[1]))
            except (ValueError, IndexError):
                pass
    next_id = max_id + 1
    print(f"Existing rows: {len(existing)}. Next POST ID: {next_id}")

    # Build rows to append: 7 blog promos + 14 standalones = 21 LinkedIn posts in tracking
    # (Blog content + newsletters tracked separately — this sheet is LinkedIn-post focused)
    days = [
        ("05/04/26", "Mon"),
        ("05/05/26", "Tue"),
        ("05/06/26", "Wed"),
        ("05/07/26", "Thu"),
        ("05/08/26", "Fri"),
        ("05/09/26", "Sat"),
        ("05/10/26", "Sun"),
    ]

    rows = []

    # Load post bodies from clean files
    sys.path.insert(0, str(ROOT / 'workers' / 'social-api'))
    import importlib
    import cleanup_and_repush
    importlib.reload(cleanup_and_repush)
    promos, standalones = cleanup_and_repush.load_li_post_bodies()

    standalone_slots = {
        1: [(None, 1)],
        2: [(2, 3)],
        3: [(4, 5)],
        4: [(6, 7)],
        5: [(8, 9)],
        6: [(10, 11)],
        7: [(12, 13)],
    }

    pid = next_id
    for day_idx, (date_str, dow) in enumerate(days, start=1):
        # Promo (paired with blog)
        if day_idx in promos:
            rows.append([
                f"POST {pid}",                                    # A: POST ID
                "May - AI Partnership & Compounding",             # B: Theme
                "AI Thought Leadership",                          # C: Lane
                date_str,                                         # D: Suggested Date
                "#AI #AIAgents #AIPartnership",                   # E: Hashtags
                promos[day_idx],                                  # F: Post Content
                "Draft",                                          # G: Status
                "", "", "", "", "", "", "",                       # H-N: metrics empty
            ])
            pid += 1
        # Standalones
        for slot1, slot2 in standalone_slots.get(day_idx, []):
            if slot1 and slot1 in standalones:
                rows.append([
                    f"POST {pid}",
                    "May - AI Partnership & Compounding",
                    "Founder Insight",
                    date_str,
                    "#AI #AIStrategy",
                    standalones[slot1],
                    "Draft",
                    "", "", "", "", "", "", "",
                ])
                pid += 1
            if slot2 and slot2 in standalones:
                rows.append([
                    f"POST {pid}",
                    "May - AI Partnership & Compounding",
                    "Founder Insight",
                    date_str,
                    "#AI #AIStrategy",
                    standalones[slot2],
                    "Draft",
                    "", "", "", "", "", "", "",
                ])
                pid += 1

    # Reserve standalone (B14)
    if 14 in standalones:
        rows.append([
            f"POST {pid}",
            "May - AI Partnership & Compounding (RESERVE)",
            "Founder Insight",
            "",  # no date — flex
            "#AI #AIAgents #Leadership #Delegation",
            standalones[14],
            "Draft",
            "", "", "", "", "", "", "",
        ])
        pid += 1

    print(f"Appending {len(rows)} rows...")
    result = svc.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB}'!A:N",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()
    updated = result.get('updates', {}).get('updatedRows', 0)
    print(f"Appended {updated} rows. Range: {result.get('updates', {}).get('updatedRange')}")


if __name__ == "__main__":
    main()
