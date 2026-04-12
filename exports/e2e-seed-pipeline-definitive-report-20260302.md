# E2E Seed Pipeline — Definitive Verification Report

**Date**: 2026-03-02 15:35 UTC
**Tester**: Aether (direct API simulation + background browser agent)
**Purpose**: Verify all data fires correctly for Monday go-live

---

## VERDICT: BACKEND PIPELINE CONFIRMED — GO

All 8 backend endpoints work correctly through the Cloudflare tunnel. Data flows through the complete chain: Browser → Cloudflare → Log Server → File Logs → Telegram → A-C-Gee → Hub → Witness.

---

## Test Results

| # | Endpoint | Method | Status | Data Landed | Forwarding |
|---|----------|--------|--------|-------------|------------|
| 1 | /api/health | GET | 200 OK | — | — |
| 2 | /api/log-conversation (pre-payment) | POST | 200 OK | conversations.jsonl ✅ | A-C-Gee ✅, Hub ✅ |
| 3 | /api/verify-payment | POST | 200 OK | payments.jsonl ✅ | — |
| 4 | /api/log-pay-test (q:name) | POST | 200 OK | pay_test.jsonl ✅ | Telegram ✅ |
| 5 | /api/log-pay-test (q:complete) | POST | 200 OK | pay_test.jsonl ✅ | Telegram ✅ |
| 6 | /api/log-conversation (full Q&A) | POST | 200 OK | conversations.jsonl ✅ | A-C-Gee ✅, Hub ✅ |
| 7 | /api/birth/start → Witness | POST | 200 OK | — | Proxy → 37.27.237.109:8099 ✅ |
| 8 | /api/log-pay-test (flow:complete) | POST | 200 OK | pay_test.jsonl ✅ | Telegram ✅ |

---

## Actual Seed Architecture (Corrected)

**IMPORTANT**: Previous browser agent reports mentioned a `fireSeed()` function and `intake/seed` endpoint. These DO NOT EXIST in the chatbox code. The actual mechanism is:

### logPayTestData() — fires at 23 trigger points
Sends to BOTH endpoints via `Promise.allSettled` (fire-and-forget, 4s timeout):
1. `POST https://api.purebrain.ai/api/log-pay-test` — form data (tier, orderId, name, email, etc.)
2. `POST https://api.purebrain.ai/api/log-conversation` — messages array (conversation history)

### Trigger points (from chatbox JS v4.7):
- Pre-payment: conversation_start, message_exchange (multiple)
- Payment: verify-payment (separate call)
- Post-payment Q&A: questionnaire:name, questionnaire:email, questionnaire:company, questionnaire:role, questionnaire:complete
- Birth: birth:init:start, birth:start:url_ready OR birth:start:failed
- OAuth: birth:authenticated, birth:code:failed
- Portal: portal:timeout, portal:ready
- Flow: flow:start, flow:complete, flow:error, curtain:complete, telegram:complete

### Birth Pipeline
- `POST ${WITNESS_WEBHOOK_HOST}/api/birth/start` with `{name, email, human_name, tier}`
- `WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443'` (our server, proxies to Witness Hetzner)
- Proxy: localhost:8443 → 37.27.237.109:8099
- Returns: `{status: "url_ready", oauth_url: "...", container: "aiciv-XX"}`

---

## Data Landing Verification

### conversations.jsonl
```
15:35:03 | conversation_start | 2 msgs  | session=pb-e2e-direct-1772465702
15:35:07 | questionnaire:complete | 10 msgs | session=pb-e2e-direct-1772465702
```

### pay_test.jsonl
```
15:35:04 | questionnaire:name     | name=Hannah Test | flowCompleted=False
15:35:06 | questionnaire:complete | name=Hannah Test | email=hannah@test.com | flowCompleted=True
```

### payments.jsonl
```
15:35:03 | orderId=E2E-DIRECT-1772465703 | tier=Awakened | amount=79.00 | verified=True
```

---

## Forwarding Chain Confirmation

| Destination | Status | Evidence |
|-------------|--------|----------|
| File logs (3 JSONL files) | ✅ | All entries confirmed in files |
| Telegram notifications | ✅ | "Telegram notification sent" at 15:35:05 and 15:35:06 |
| A-C-Gee (sister collective) | ✅ | "A-C-Gee forward success" x3 |
| Hub (operations room) | ✅ | "Forwarded to hub → operations" x3 |
| Witness birth pipeline | ✅ | "Birth/start proxy: status=200" |

---

## Browser Test Limitation

GoDaddy's bot protection triggered a CAPTCHA ("Please verify you are human") after multiple automated password attempts from the server IP. This blocks all Playwright-based browser testing.

**Impact**: Cannot test the actual PayPal sandbox UI flow automatically.

**Recommendation**: Jared should do one manual test from his phone:
1. Go to purebrain.ai/pay-test-sandbox-2/
2. Enter password: PureBrain.ai253443$$
3. Go through chatbox → Activate Now → PayPal checkout
4. Use sandbox credentials: sb-c89tj49549583@personal.example.com / Z0+6<dS
5. Complete payment → watch Telegram for seed notifications
6. Go through post-payment Q&A → verify final seed fires

---

## Known Issues for Go-Live

### NONE BLOCKING

| Issue | Severity | Status |
|-------|----------|--------|
| Birth/start takes ~30s | INFO | Normal — Witness container allocation is slow by design |
| Old fallback seed URL (104.248.239.98:8200) dead | LOW | Not used — primary (api.purebrain.ai) works. Clean up later. |
| CAPTCHA blocks automated testing | INFO | Only affects automated testing, not real users |

---

## Session Details

- Direct API test session: `pb-e2e-direct-1772465702`
- Browser agent session: `purebrain_1772465708586_lalem6ypj` (still active)
- Birth containers allocated today: aiciv-12, aiciv-13, aiciv-14 (test only)
- Log server PID: running on port 8443 (aether-logserver.service)
