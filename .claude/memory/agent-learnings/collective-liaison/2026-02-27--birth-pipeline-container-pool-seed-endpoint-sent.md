# Birth Pipeline - Container Pool Exhausted + /birth/seed Spec Sent

**Date**: 2026-02-27
**Type**: operational
**Topic**: Urgent hub message to Witness re: 503 container pool exhaustion + /birth/seed endpoint spec

## What Happened

Sent urgent follow-up to Witness in the `witness-aether` hub room after birth pipeline diagnosis completed.

## Key Facts

**PureBrain side fixed:**
- WITNESS_WEBHOOK_HOST was pointing to 89.167.19.20:8443 (self-signed cert IP) — browsers silently blocked all fetch() calls
- Fixed to api.purebrain.ai (Cloudflare tunnel with valid cert)
- Both pay-test-2 and pay-test-sandbox-2 deployed with fix
- Proxy chain verified: api.purebrain.ai → our server → Witness server

**Witness side blocking (503):**
- birth/start returning "No containers available - pool exhausted"
- All 5 containers (aiciv-06 through aiciv-10) consumed by test runs
- Asked Witness to: free test containers, expand pool beyond 5, confirm v1.2.0 refactor status

**/birth/seed endpoint spec proposed:**
- New endpoint needed to send COMPLETE customer profile + conversation history post-chat
- Current birth/start only sends name+email+tier (insufficient)
- Proposed payload: container, name, email, company, role, primaryGoal, aiName, tier, orderId, conversationHistory

## Hub Message Details

- **Room**: witness-aether
- **Message ID**: 01KJFA7YZ0G3T44Y37FZTV4WDN
- **File**: rooms/witness-aether/messages/2026/02/2026-02-27T102752Z-01KJFA7YZ0G3T44Y37FZTV4WDN.json
- **Commit**: e6b57ed

## Operational Gotcha

hub_cli.py requires these env vars:
- HUB_REPO_URL (get from: `git remote -v` inside `_comms_hub`)
- HUB_AGENT_ID
- HUB_LOCAL_PATH (optional, defaults to ./_comms_hub)

hub_cli.py auto-commits and pushes on send — no manual git commit needed.

## Priority

Jared needs to demo today — container pool exhaustion is the critical blocker.
