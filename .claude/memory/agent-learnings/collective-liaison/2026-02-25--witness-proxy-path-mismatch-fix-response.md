# Memory: Witness Proxy Path Mismatch Fix Response

**Date**: 2026-02-25
**Type**: operational
**Agent**: collective-liaison
**Topic**: Witness crash recovery — answered 3 critical questions + documented path mismatch bug fix

---

## Context

Witness re-established comms after a crash recovery and sent 3 critical questions to Aether via the witness-aether hub room. This was an URGENT coordination requiring same-session response.

## Questions Answered

### Q1: Is chatbox wired to POST to proxy endpoints?
- YES, but a critical PATH MISMATCH BUG caused zero requests at ~12:15
- Bug: chatbox v4.4 called `/api/birth/start` but proxy routes were at `/api/proxy/birth/start`
- Fix: Added duplicate Flask route decorators for BOTH path patterns
- Deployed at 13:58 UTC, verified with OPTIONS preflight (204 OK)

### Q2: Is the manual birth button fixed to be OAuth click per v3.0?
- NOT YET FIXED — still a birth trigger, not OAuth click
- Design decision pending (Jared): Option A = remove button entirely (server-side trigger), Option B = relabel as OAuth click
- Witness's v3.0 spec: SEED arriving IS the trigger, no button needed

### Q3: Status of 3 server-side proxy endpoints?
- All 3 LIVE at 13:58 UTC
- Dual-path routing: both `/api/birth/*` AND `/api/proxy/birth/*` route to same handlers
- CORS, rate limiting, SSL, upstream hardcoded all confirmed

## Hub Execution Pattern

1. hub_cli.py auto-commits AND auto-pushes in a single operation
2. No separate git add/commit/push needed after hub_cli.py send
3. hub_cli.py uses the HUB_REPO_URL env var and the _comms_hub local path
4. Verify success: `git log --oneline -3` and `git rev-parse HEAD` vs `git rev-parse origin/master`

## Message File Created

`/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/rooms/witness-aether/messages/2026/02/2026-02-25T140008Z-01KJAHK6BVCF0HGAFG23WDHFMW.json`

## Key Learned Pattern

When hub_cli.py says nothing after `send`, check the git log — it already committed and pushed. The silent success is normal behavior.

## Next Steps in This Coordination

1. Witness confirms webhook ready at 104.248.239.98:8099
2. Jared runs sandbox payment on page 688
3. Watch chain: chatbox → proxy → webhook
4. DRY_RUN flip decision from Corey/Witness side
