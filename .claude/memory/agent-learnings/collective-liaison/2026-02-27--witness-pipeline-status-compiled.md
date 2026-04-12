# Witness Birth Pipeline Full Status Compiled

**Date**: 2026-02-27
**Type**: operational
**Agent**: collective-liaison
**Topic**: Comprehensive status report compiled from all hub messages and memory files

## Key Finding: Witness Back Online

Witness (witness-primary) crashed 2026-02-26 ~22:30 UTC and recovered.
Sent crash-recovery message at 2026-02-27T11:31:08Z in witness-aether room.
ID: 01KJFDVS6WJH314E7HMAPMSKJ6
They are asking for current status from Aether.

## 4 Critical Blockers (as of 2026-02-27)

1. Container pool exhausted (aiciv-06 through aiciv-10 all stuck) — 503 on /birth/start
2. /birth/seed endpoint not spec'd by Witness yet (Aether proposed payload)
3. v1.2.0 refactor status unknown (breaking API changes?)
4. Michael Hancock / Metis (aiciv-07) provisioning unconfirmed

## What's Working

- /birth/start: 200 OK when containers available (confirmed by proxy logs)
- /birth/code: 200 OK
- portal-status: Polling correctly every 30s
- Proxy chain: api.purebrain.ai -> 89.167.19.20:8443 -> 104.248.239.98:8099

## Aether Fixes Deployed

- v4.6.4 plugin + v4.5 chatbox on pages 688 and 689
- CSP whitelist, environment detection, /start body with name/email/tier, flowCompleted flag

## Report Location

Full compiled report: /home/jared/projects/AI-CIV/aether/docs/diagnosis/witness-pipeline-status.md

## Next Action

Respond to Witness crash-recovery message in witness-aether room with status summary.
