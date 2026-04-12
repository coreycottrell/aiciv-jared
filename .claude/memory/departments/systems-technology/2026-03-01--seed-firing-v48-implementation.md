# Seed Firing v4.8 — 3-Stage purebrain_birth_seed Implementation

**Date**: 2026-03-01
**Files Modified**:
- `exports/pay-test-script-chat-flow-v4.js` (v4.7 → v4.8)
- `tools/purebrain_log_server.py`

## What Was Built

Added 3-stage seed firing to the chatbox post-payment onboarding flow. Seeds are POSTed as `purebrain_birth_seed` JSON to Witness/aiciv at key moments in the user journey.

## Architecture

### fireSeed(stageName, stageNumber)
- Added after `logPayTestData()` function (line ~240)
- Builds full conversation_history: preMsgs + onboardingMsgs + learnMoreAnswers
- Primary: `https://api.purebrain.ai/api/intake/seed` (proxied)
- Fallback: `http://104.248.239.98:8200/intake/seed` (direct Witness seed port)
- Fire-and-forget with `.catch(() => {})` — NEVER blocks or throws into main flow

### Stage 1 — payment_complete
- Location: `initPayTestFlow()` after `buildLayout()`, before `runQuestionnaire()`
- Data: tier, orderId, aiName, pre-purchase history
- Fires immediately when chat UI is ready post-payment

### Stage 2 — oauth_authenticated
- Location: After `/api/birth/code` succeeds, after `logPayTestData({ event: 'birth:authenticated' })`
- Data: Everything from Stage 1 + name, email, company, role, primaryGoal + containerName + birthAuthenticated=true

### Stage 3 — portal_ready
- Location: In `runPortalButtonWatcher()` immediately after `payTestData.portalReady = true`
- Data: EVERYTHING — all prior stages + learnMoreAnswers (complete birth record)

## Proxy Route Added (purebrain_log_server.py)

- Route: `POST /api/intake/seed`
- Validates `type === 'purebrain_birth_seed'`
- Forwards to `WITNESS_SEED_URL = 'http://104.248.239.98:8200/intake/seed'`
- `WITNESS_SEED_TIMEOUT = 15` seconds
- Returns Witness response or 503/504/502 on failure
- Includes OPTIONS CORS preflight handler

## Key Gotchas

- Witness seed port is 8200, NOT 8099 (birth pipeline port)
- Seeds use `.catch(() => {})` on all 3 call sites — non-blocking by design
- `learnMoreAnswers` stored as `{ question, answer }` objects — must map to role/content pairs
- Existing `logPayTestData` calls are completely untouched
- Python log server syntax-checked clean with `py_compile`
