# Admin Clients Recovery Strategy — CTO Analysis

**Date**: 2026-04-20
**Type**: operational + teaching
**Agent**: cto (via ptt-fullstack learning path)

## Root Cause

clients.db is ephemeral SQLite on the portal server. When portal_server.py process was killed, the DB was either:
1. Deleted (fresh init creates empty table)
2. Corrupted and recreated on restart

The auto-import loop (_auto_import_clients_loop) runs every 5 minutes and SHOULD repopulate from JSONL logs automatically. If it shows 0, the likely cause is that the import filters are excluding entries (sandbox emails, missing names, test order IDs).

## Data Sources Available

1. **purebrain_payments.jsonl** (65 lines) — 20+ real customer payments, ~34 sandbox "John Doe" entries
2. **purebrain_pay_test.jsonl** (233 lines) — Questionnaire progression data (name, email, AI name, company, role, goal)
3. **purebrain_web_conversations.jsonl** (4,667 lines) — Chat sessions, mostly noise for client import
4. **PayPal API** — Live subscription data (authoritative source for payment status)
5. **D1 purebrain-referrals** — 28 referral records (intact)

## Real Customers Identified (from payments log, non-sandbox)

Daniel Joshua Grand, Eric Turbaville, Donna Olson, Mark Rewers, Pia Knudsen, Ian Wheaton, Darren Rowan, Faris Asmar, Robert Sanchez, Bradley Nordal, Nidhin Nandakumar, Matthew Keough, Trevor Schoessow, Bryce Lohr, Joseph Diosana, Kirk Marcou, Gary Kohn + Jared Sanborn (internal test)

## Recovery Script

`/home/jared/purebrain_portal/recover_clients.py` — standalone Python3, reads same JSONL logs, uses same filtering logic as portal_server.py, writes to clients.db with proper schema. Run with --dry-run first.

## Strategic Recommendation: Migrate to D1

clients.db in SQLite = single point of failure. This is the SECOND time it's been lost. Migrate to D1 (purebrain-clients or add clients table to purebrain-referrals). The referral system already proved D1 works. This should be prioritized.
