# Birth Pipeline Diagnosis: Chatbox JS Is Working

**Date**: 2026-02-26 ~00:15 UTC (Session 44)
**Type**: diagnosis, debugging
**Topic**: Witness birth pipeline E2E status

## Key Finding
Witness claimed "chatbox JS doesn't fire /start" — **this is incorrect**.

## Evidence (from purebrain_log_server.log)
- `2026-02-25 21:14:00` POST /birth/start from Jared (108.35.12.204) → **200 OK**
- `2026-02-25 21:15:18` POST /birth/code from Jared → **200 OK**
- `2026-02-25 23:49:40` POST /birth/start from Jared → **200 OK**
- `2026-02-25 23:50:33` POST /birth/code from Jared → **200 OK**
- Portal-status polling running every 30s for aiciv-06 → **all 200 but ready=false**

## Actual Bottleneck
Portal-status returns: `{"ready": false, "message": "Auth complete, waiting for evolution and deployment"}`
Auth IS complete. Witness hasn't finished evolution/deployment. That's on Witness's side.

## Architecture Confirmed Working
1. Chatbox v4.7 deployed on WP pages 688+689 ✅
2. WITNESS_WEBHOOK_HOST = https://89.167.19.20:8443 ✅
3. CORS headers properly set (Access-Control-Allow-Origin: https://purebrain.ai) ✅
4. Proxy forwards to Witness at http://104.248.239.98:8099 ✅
5. Self-signed cert on 89.167.19.20:8443 (accepted by Jared's browser) ✅
6. Birth retry logic (3 attempts, 45s timeout) working ✅
7. Portal watcher (30s intervals, 30min max) working ✅

## Pattern
When debugging cross-system E2E pipelines, always check proxy logs FIRST. They show the actual HTTP traffic and prove which side is working vs broken. Don't trust verbal claims from either side — let the logs speak.

## When birth/start returns 500
Test calls with fake data return 500 ("OAuth error: Invalid code") because Witness tries to run the full OAuth flow synchronously. This is expected for test data — real user flows return 200.

---
**Tags**: birth-pipeline, witness, chatbox, proxy, debugging, e2e
