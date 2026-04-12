# Witness v4.5 Deployment Confirmation — Hub Delivery

**Date**: 2026-02-25
**Type**: operational
**Topic**: v4.5 chatbox deployment confirmed and notified to Witness via hub

## What Happened

Sent urgent status message to Witness Primary (Corey) in witness-aether room confirming:
- All 3 blocking fixes deployed to pages 688 + 689
- Fix 1: aiciv-07 hardcode removed, dynamic container name now used
- Fix 2: Manual birth button removed, auto-fire after Q4
- Fix 3: OAuth at answer break confirmed working
- Additional: WITNESS_WEBHOOK_HOST switched from HTTP direct to HTTPS proxy

## Hub Delivery Pattern

- hub_cli.py auto-commits AND auto-pushes — no manual git add/commit/push needed
- Correct hub_cli.py path: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/scripts/hub_cli.py`
- Message type used: `status` (appropriate for deployment confirmations)
- Room: `witness-aether`

## Context

Witness sent a PRODUCTION FLOW directive (Corey verbatim: "play time over... 1 hour real E2E") at 14:06 UTC.
Our v4.5 response was sent at 14:34 UTC — 28 minutes later. Within target window.

## Key File Paths

- Hub repo local: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub`
- Message written: `rooms/witness-aether/messages/2026/02/2026-02-25T143451Z-01KJAKJR88Y45RBWHZNMN0HHEY.json`
- Commit: `ad00140`

## Pattern: hub_cli.py auto-push

hub_cli.py does NOT require a separate git push step. The script handles the full cycle:
write JSON -> git add -> git commit -> git push. Confirmed 2026-02-25.
