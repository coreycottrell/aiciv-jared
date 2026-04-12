# Chatbox v4.3.1 - Witness Direct IP Deploy to Sandbox

**Date**: 2026-02-24
**Type**: operational
**Topic**: Deploy WITNESS_WEBHOOK_HOST override to page 688 (sandbox) for E2E test

---

## What Was Done

Changed `WITNESS_WEBHOOK_HOST` in `exports/pay-test-script-chat-flow-v4.js` from:
- `'https://api.purebrain.ai'` → `'http://104.248.239.98:8099'`

This is a SANDBOX-ONLY change (page 688) for E2E testing with Witness direct IP.
Page 689 (production) remains on `https://api.purebrain.ai`.

## Version

Source file version: v4.3.1 (comment added to top of file)
- v4.3.1 note: "WITNESS_WEBHOOK_HOST reverted to http://104.248.239.98:8099 for direct E2E test"

## Files Changed

- `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js`
  - Line 2 header: v4.3 → v4.3.1
  - Line ~1859: WITNESS_WEBHOOK_HOST value changed

## Deployment

Deployed to page 688 (purebrain.ai/pay-test-sandbox-2/) only.

Used dual-store pattern (see 2026-02-24--chatbox-v42-dual-storage-deploy-pattern.md):
- `content.raw` updated: confirmed `WITNESS_WEBHOOK_HOST = 'http://104.248.239.98:8099'` at pos 404567
- `_elementor_data` updated: confirmed `WITNESS_WEBHOOK_HOST = 'http://104.248.239.98:8099'` at pos 431018

Elementor cache cleared: DELETE /wp-json/elementor/v1/cache → 200 OK

## Health Check

`curl http://104.248.239.98:8099/health` timed out - Witness server not running at time of deploy.
This is expected - Witness team (Corey) needs to have aiciv-07 container running for E2E test.

## Witness Birth Pipeline Endpoints (at direct IP)

- POST /api/birth/start (empty body = auto-allocate container)
- POST /api/birth/code (body: {container, auth_code})
- GET /api/birth/portal-status/{containerName}
- GET /health

## Key Notes

- The v4.2 comment block still mentions `https://api.purebrain.ai` - that is historical documentation (correct)
- Only the const assignment was changed (the one occurrence at the variable declaration)
- Log server endpoints (api.purebrain.ai) were NOT touched - those are separate
- Container aiciv-07 is pre-allocated and ready per Witness team
