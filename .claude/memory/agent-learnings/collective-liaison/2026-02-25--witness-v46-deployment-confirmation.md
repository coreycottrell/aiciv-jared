# Witness v4.6 Deployment Confirmation — Hub Delivery

**Date**: 2026-02-25
**Agent**: collective-liaison
**Type**: operational
**Topic**: v4.6 chatbox deployment — all 4 Witness fixes live, E2E coordination message sent

## What Happened

Jared requested urgent hub message to Witness in witness-aether room confirming v4.6 deployment.

Previous message thread context:
- Witness sent PRODUCTION BUILD PLAN (14:39 UTC) with 1-hour deadline from Corey
- v4.5 was deployed at 14:34 UTC (3 blocking fixes)
- v4.6 adds Fix 1: container name from /start response (removes client-side generation entirely)

## Message Sent

- **Room**: witness-aether
- **Type**: status
- **Summary**: v4.6 DEPLOYED — All 4 Witness Fixes Live + Ready for E2E
- **ID**: 01KJAME6G3KB8HHQQ31FRVN8WY
- **File**: rooms/witness-aether/messages/2026/02/2026-02-25T144950Z-01KJAME6G3KB8HHQQ31FRVN8WY.json
- **Push status**: Auto-committed and pushed by hub_cli.py (confirmed via git log)

## All 4 Fixes Summarized

1. Fix 1 (BLOCKING - NEW in v4.6): Container name from /start response only. No client-side generation.
2. Fix 2 (HIGH - Already v4.5): Auto-call /start on payment after Q4
3. Fix 3 (BLOCKING - Already working): Poll /portal-status/{container} every 30s
4. Fix 4 (HIGH - Already working): Show OAuth URL at answer break

## Key API Contract Communicated

POST /api/birth/start body: {name, email, human_name, tier}
Expected response: {status, oauth_url, container}
POST /api/birth/code body: {container, auth_code}

## Verification

4 questions posed to Witness:
1. Confirm webhook accepts new POST body format
2. Confirm /start response includes container field
3. Is DRY_RUN=false?
4. Ready for Jared's E2E test?

## Pattern Learned

hub_cli.py auto-commits AND auto-pushes when sending messages. No need for separate git add/commit/push steps. Confirmed via `git log --oneline origin/master..HEAD` showing 0 local-only commits after send.

## Files

- Hub message: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/rooms/witness-aether/messages/2026/02/2026-02-25T144950Z-01KJAME6G3KB8HHQQ31FRVN8WY.json`
