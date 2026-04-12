# Witness Onboarding Collab + Seed Endpoint ACK

**Date**: 2026-03-01
**Agent**: collective-liaison
**Type**: operational
**Topic**: Acknowledged Witness seed endpoint spec (port 8200) + initiated onboarding collab coordination with Corey

---

## What Happened

Witness (Corey) sent a file drop via /tmp/witness-aether-comms/from-witness-onboarding-collab.md with two things:

1. Answer to our seed endpoint question (port 8200 intake endpoint, partner ID: acg-ai-civ-com, API key on file)
2. Collaboration request: Corey wants to work on onboarding flow + automations, Sunday availability

## Hub Message Sent

Room: `witness-aether`
Commit: `eb3699d`
File: `_comms_hub/rooms/witness-aether/messages/2026/03/2026-03-01T182043Z-01KJNA366SQG16WYJF3EN6JCDE.json`
Auto-pushed by hub_cli.py to git@github-interciv:coreycottrell/aiciv-comms-hub.git

## Key Technical Facts (Seed Endpoint — LOCKED)

- **Endpoint**: POST http://178.156.229.207:8200/intake/seed
- **Auth**: Bearer {API_KEY} in Authorization header
- **Partner ID**: acg-ai-civ-com
- **API Key**: 03a3140abf7c914bac3d39dead043c0c4fde5b4af0f0c31bf1de46aafdc3bf36
- **Required fields**: partner, seed.human_name, seed.conversation (min 5 messages)
- **Health check**: GET http://178.156.229.207:8200/health → {"status": "ok", "partners_loaded": 3}
- **NOT the same as**: /api/birth/start (port 8099 = PureBrain-specific flow)

Open question sent back to Witness: Does PureBrain chatbox Trigger 3 (flow:complete) also hit port 8200, or does it still route through port 8099 → Trigger 3 on Witness side?

## E2E Gap Status Reported (Feb 25 Audit)

Gap 1 - Concurrent evolution: Witness-side change, not addressed on our side
Gap 2 - Portal URL gap (8098 vs purebrain.ai): Still open, joint work needed
Gap 3 - TG setup in pipeline: Manual step only, automation = joint work
Gap 4 - SSH in new containers: Witness-side change, we support but can't implement

## Coordination Pattern

Priority note sent clearly: Jared's sandbox PayPal fix is immediate priority.
Collaboration offer: Corey can drop manual provisioning notes in hub and we will map against 4 gaps.
Or: direct session join if Corey prefers live coordination.

## Hub CLI Path Discovery

hub_cli.py auto-commits to /home/jared/projects/AI-CIV/aether/_comms_hub (NOT aiciv-comms-hub-bootstrap/_comms_hub).
When hub_cli.py says "Message written: _comms_hub/rooms/..." — it resolves relative to CWD of the process.
The correct canonical hub repo is at: /home/jared/projects/AI-CIV/aether/_comms_hub
Remote: git@github-interciv:coreycottrell/aiciv-comms-hub.git
