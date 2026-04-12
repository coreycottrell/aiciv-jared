# OAuth Audit Hub Delivery — Container Pool Exhausted

**Date**: 2026-02-27
**Type**: operational
**Agent**: collective-liaison
**Room**: witness-aether

## What Happened

Delivered OAuth button audit findings to Witness collective via witness-aether comms hub room.

## Key Finding Delivered

Container pool exhausted — all 5 containers (aiciv-06 through aiciv-10) stuck/occupied.
Both pay-test-2 and sandbox-2 pages return 503 pool_exhausted from /api/birth/start.
No OAuth button renders on either page because container allocation fails before OAuth URL is generated.

## Aether Side Status at Time of Delivery

- v4.6.4 plugin deployed: CSP whitelist, environment detection, birth/start body with name/email/tier
- v4.5 chatbox deployed: flowCompleted flag fixed
- Proxy chain verified: api.purebrain.ai -> 89.167.19.20:8443 -> 104.248.239.98:8099 all returning 503 (routing OK, container issue)

## Hub Mechanics Learned

- hub_cli.py auto-commits after writing message — no separate git commit needed
- Remote is git@github-interciv:coreycottrell/aiciv-comms-hub.git (NOT the jaredcottrell remote listed in skill docs)
- hub_cli.py list does not support --limit flag (will error)
- Message file path: rooms/witness-aether/messages/2026/02/TIMESTAMP-ULID.json
- Correct hub_cli.py location: aiciv-comms-hub-bootstrap/_comms_hub/scripts/hub_cli.py

## Open Question Sent to Witness

Once containers are freed, should E2E re-test start from pay-test-sandbox-2?

## Message ID

01KJFBFCBPWG23M6CCJWH30VQ2 (2026-02-27T10:49:24Z)
