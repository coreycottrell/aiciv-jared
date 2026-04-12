# Complete Onboarding Flow: Seed + Addendum Implementation

**Date**: 2026-03-20
**Type**: operational + teaching
**Topic**: Full implementation of the 8-step onboarding flow per spec

## What Was Implemented

### New Log Server Endpoints

/api/send-seed (Step 3):
- FROM: aether-aiciv@agentmail.to (AgentMail SDK with explicit inbox_id)
- TO: aiciv-seed-inbox@agentmail.to
- Idempotency: logs/seed_sent_uuids.json prevents duplicates per session_uuid
- Logs to: logs/seed_events.jsonl

/api/seed-addendum (Step 5):
- FROM: purebrain@puremarketing.ai (Google SMTP)
- TO: aiciv-seed-inbox@agentmail.to
- CC: jared@puretechnology.nyc, aether-aiciv@agentmail.to
- Logs to: logs/seed_addendum_events.jsonl

### JS fireSeed() added to all 6 pages:
- pay-test-sandbox-3, live, insiders, awakened, partnered, unified
- Fires immediately after payTestData.email = email in runQuestionnaire()
- _seedFired guard prevents double-fire in same page session

## Key Facts
- AgentMail from aether-aiciv: use inbox_id='aether-aiciv@agentmail.to' explicitly
- send_agentmail.py defaults to aethergottaeat - bypass it for seed sends
- Idempotency pattern: seed_sent_uuids.json in logs dir
- All verifications passed: both endpoints 200, logs written, CF Pages deployed
