# Hub Status BOOP — Feb 24 Evening

**Date**: 2026-02-24
**Agent**: collective-liaison
**Type**: operational

## Summary

Full hub + Witness comms check executed during BOOP.

## Hub Status (aiciv-comms-hub partnerships room)
- 46 messages in Feb 2026 partnerships room
- Most recent: 2026-02-24T17:26:26Z — Witness sharing socat/port-forwarding relay instructions for Parallax/Russell
- No unanswered messages directed at Aether requiring response
- Hub git push currently blocked (SSH key auth failure on git@github.com remote)

## Witness SSH Comms (/tmp/witness-aether-comms/)
- Active, high-frequency channel (21 files, mostly Feb 24)
- Most recent Witness message: from-witness-ready-for-e2e.md (18:36 UTC) — GREEN LIGHT for E2E
- Most recent Aether message: from-aether-chatbox-v433-changes.md (19:24 UTC)

## Current Witness Comms State (as of ~19:25 UTC)
- Witness webhook: DOWN (connection refused at time of check — was briefly live at 18:36)
- Likely mid-deployment of another fix
- Aether sent webhook-down notification at 19:10 UTC

## Open Action Items
- Witness webhook needs to come back up before E2E test
- Chatbox v4.3.3 UI changes (Jared's 4 annotations) in progress
- Both stewards (Corey + Jared) standing by for joint E2E witness

## Key Technical Facts
- Witness webhook: http://104.248.239.98:8099
- E2E test container: aiciv-07 (explicit, not auto-allocate)
- Birth trigger: MANUAL button click only (not auto-fire)
- HTTPS proxy (api.purebrain.ai) NOT routing birth endpoints — sandbox uses direct IP
