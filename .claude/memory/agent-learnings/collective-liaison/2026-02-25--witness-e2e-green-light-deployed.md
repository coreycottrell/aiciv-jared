# Memory: Witness Birth Pipeline E2E Green Light — Deployed

**Date**: 2026-02-25
**Agent**: collective-liaison
**Type**: operational
**Topic**: Witness birth pipeline — Aether side deployment confirmed GREEN

---

## What Happened

Jared confirmed that Aether's side of the Witness birth pipeline is fully deployed:

1. Log server (89.167.19.20:8443) restarted with 3 proxy endpoints live:
   - POST /api/proxy/birth/start
   - POST /api/proxy/birth/code
   - GET /api/proxy/birth/portal-status/:container

2. Chatbox v4.4 deployed to purebrain.ai pages 688 and 689.
   - Dynamic container naming (no hardcoded aiciv-07)
   - HTTPS proxy routing (no browser-to-HTTP mixed content)

Requested: post E2E green light to hub.

## Actions Taken

1. Checked hub for recent Witness messages (via `_comms_hub/scripts/hub_cli.py list --room witness-aether`)
2. Found previous status message at 11:49 UTC saying "code complete, awaiting deployment"
3. Found Witness's latest message (01:35 UTC): v1.2.0 webhook deployed, auto-allocation live
4. Posted updated status to **witness-aether** room confirming deployment complete and E2E ready
5. Also posted brief notice to **partnerships** room per Jared's request
6. Both commits confirmed pushed: `fbd4cc2` (partnerships) and `9cc99e7` (witness-aether)

## Key Technical Context

- Witness webhook: http://104.248.239.98:8099
- Aether log server proxy: https://89.167.19.20:8443
- Auto-allocation: POST {} to /start returns `{container: "aiciv-XX", auto_allocated: true}`
- E2E test container: aiciv-07 (clean, available)
- Witness flips DRY_RUN=false when ready for live test

## Hub Navigation Note

The correct room for Witness coordination is `witness-aether`, not just `partnerships`.
`partnerships` is for general cross-CIV announcements.

## Files

- Message written: `_comms_hub/rooms/witness-aether/messages/2026/02/2026-02-25T115444Z-01KJAADJN4Y44TW2FAHMX9P1J8.json`
- Message written: `_comms_hub/rooms/partnerships/messages/2026/02/2026-02-25T115457Z-01KJAADYPRDC3T2B7XZ7QDX14G.json`

## Pattern: Status Update Sequence

When deployment completes after a "code complete, awaiting approval" status:
1. Check hub first — don't blindly assume nothing changed (Witness had posted v1.2.0)
2. Post to domain-specific room (witness-aether) with full technical detail
3. Post brief notice to partnerships room for visibility
4. Confirm commits via `git log`
