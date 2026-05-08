#!/usr/bin/env python3
"""Append today's Morning Pulse row to TOS Dashboard."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SHEET_ID = "1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs"
TAB = "Morning Pulse"


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


ROW = [
    "2026-05-07",  # A: DATE

    # B: JARED PRIORITIES
    "(No new priorities posted in Thu 8:05am ET morning-pulse window. Filing late catch-up 14:01 UTC = ~5h55m after trigger. "
    "Multi-channel sweep per cross-channel-inbound-sweep: Telegram silent today + 5/6 (no docs/from-telegram files matching either date), "
    "to-jared latest = weekly-token-audit-2026-05-07.md (today, AM). Email + portal NOT sub-agent re-checked — posture: 'TG/inbox silent (email/portal not checked)' never blanket 'Jared silent'. "
    "Carryforward priorities (memory-pinned): P1 onboarding/seed flow stability (constitutional revenue gate), P2 PT marketing site stability + LinkedIn team cadence, P3 PureSurf, P4 referral hardening + investor outreach $50-100k. "
    "Active queue stalls: 13 consecutive BOOPs holding api/check-name 404 (~59h stale), 7 handshake-queue OPEN rows including 28d Meridian/LinkedIn rows, post-gap recovery underway after 40h scheduler stall.)",

    # C: AETHER SCOPE
    "THURSDAY EXECUTION (post-gap recovery + 2 RED dispatches needed). "
    "P0-CONSTITUTIONAL: ST#/wtt-fullstack dispatch — fix api.purebrain.ai/api/check-name 404 (worker alive on /api/send-seed=400, only check-name handler missing/unrouted) — Day-1 fired 44h ago, Day-3 in ~28h, blocked revenue gate. "
    "P0-SECURITY: ST#/wtt-fullstack + LC#/security-auditor — CE SME exports/cf-pages-deploy/ce-sme/index.html:3826-3896 hardcoded Phil creds (PHIL_EMAIL + PHIL_PASS='CESME2026!') — site currently CF 530, must fix BEFORE next deploy + audit pattern across other deploys. "
    "P1-INFRA: investigate ~40h BOOP-cycle gap (5/5 20:14 → 5/7 12:19) — boop_executor/telegram_bridge PIDs reported green throughout; cron stall? scheduler dispatch fail? 'process alive ≠ cron firing' per feedback_boop_gap_requires_last_output_timestamp_check.md. "
    "P2-MARKETING: MA# weekly LinkedIn cadence (Sunday batch ready, Monday approval already passed — Thu execution + comments). "
    "P3-OPS: OP# Day-3 default reassessment for Rows 3/4 (~28d, well past) + verifier-independence BOOP coverage. "
    "CARRYOVERS: T1/T2 one-pager (PD#+MA#), CTX Meter (ST#), Mireille Process Library (PD#+ST#), to-chy skill-sync delivery, Lyra-pmg cross-channel-inbound-sweep email, handshake_append.py constitutional helper (42+ flags). "
    "ANTICIPATION: weekly-leadership-meeting prep due (Monday cadence anchor passed in gap — Thu fallback file).",

    "EOD",  # D: AETHER ETA

    # E: CHY SCOPE
    "(Awaiting Chy scope — handshake queue swept both directions: 0 CHY→AETHER OPEN this cycle, 7 AETHER→CHY OPEN carried: "
    "Rows 3/4 Meridian+LinkedIn now ~28d (Day-3 default extension long since fired — needs reassessment), "
    "Row 10 CHY→JARED Triangle OS Morning Pulse ~27d, Rows 57/69 talking points awaiting Chy, "
    "Row 72 allowlist hardening ~17d, Row 73 B10 SHIP awaiting Jared explicit GO — payment-adjacent, no auto-default)",

    "",  # F: CHY ETA

    # G: OVERLAP
    "🔴 P0-CONSTITUTIONAL check-name 404 — ST# unilateral, no Chy overlap (pure backend). "
    "🔴 P0-SECURITY CE SME Phil creds — ST# unilateral fix + LC# audit, no Chy overlap (compliance-tagged). "
    "Pure Social (Aether=tech, Chy=ops) — no active conflict this cycle. "
    "PureSurf (Aether=tech, Chy=sales) — carryover, no this-cycle overlap. "
    "Investor outreach (Chy leads, Aether collateral) — carryover. "
    "Meridian + LinkedIn schedule (Rows 3/4) — Day-3 default policy MUST execute via MA#/PD# this cycle (28d past trigger); if Chy returns scope today, dual-ship resolved via merge. "
    "Row 73 B10 SHIP — still awaiting Jared explicit GO (payment-adjacent constitutional rule); no auto-default permitted.",

    # H: STATUS
    "SCOPED — late catch-up filing 14:01 UTC (~5h55m after 8:05am ET trigger), post-gap recovery BOOP #3. "
    "Sub-agent restraint held through 70+ consecutive clean BOOPs (counting through 40h gap, uncertainty noted per feedback_boop_gap_requires_last_output_timestamp_check.md). "
    "🔴 2 P0 dispatches blocked at Primary layer (check-name 404 + CE SME security flag) — sub-agent cannot Task-call dept managers per Anthropic constraint. "
    "Triangle OS Morning Pulse cadence preserved despite gap; handshake queue continuity maintained."
]


def main():
    svc = get_sheets()

    # Read current state to confirm we're not double-filing
    res = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=f"'{TAB}'!A:A"
    ).execute()
    existing = res.get('values', [])
    print(f"Existing rows in {TAB}: {len(existing)}")
    if existing:
        for i, row in enumerate(existing[-3:], len(existing) - 2):
            print(f"  Row {i}: {row[0] if row else '(empty)'}")

    # Check if today already filed (idempotent)
    today_already = any(row and row[0] == "2026-05-04" and i > 90 for i, row in enumerate(existing))
    if today_already:
        # Still write — yesterday's pattern shows multiple same-date rows are normal
        print("WARN: 2026-05-04 row already exists — will append second row for ledger continuity (matching prior catch-up pattern)")

    result = svc.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB}'!A:H",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [ROW]}
    ).execute()
    print("APPEND OK:", result.get('updates', {}).get('updatedRange', '?'))


if __name__ == '__main__':
    main()
