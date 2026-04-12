# Memory: OAuth Button Not Appearing — Root Cause: Container Pool Exhausted

**Date**: 2026-02-27
**Type**: teaching + operational
**Topic**: OAuth button never appears because /api/birth/start returns 503 pool_exhausted

---

## The Bug

Users click "Begin Awakening", go through name/email/company/role questions, but the OAuth button never appears. Instead, they see the retry loop or nothing.

---

## Root Cause Confirmed (Feb 27 v2 audit)

### Both pages have the same failure

The Witness server's container pool is exhausted:

```json
{"error":"No containers available","pool":["aiciv-06","aiciv-07","aiciv-08","aiciv-09","aiciv-10"],"status":"pool_exhausted"}
```

HTTP 503 returned by:
- `https://89.167.19.20:8443/api/birth/start` — responds in 0.23s
- `https://api.purebrain.ai/api/birth/start` — responds in 0.40s via Cloudflare
- `http://104.248.239.98:8099/api/birth/start` — responds in <1s

Previously (earlier today), these same endpoints were timing out entirely (status 000).
Now they're responding instantly with 503 pool_exhausted.

---

## What "pool_exhausted" Means

The Witness server manages a pool of Docker containers (aiciv-06 through aiciv-10).
When /birth/start is called, it tries to spin up a container for the user.
If ALL containers in the pool are already in use (or reserved/stuck), it returns 503.

Fix: The Witness admin (Jared/full-stack-developer) needs to:
1. Check container status: which containers are stuck/in-use
2. Reset/release stuck containers
3. OR increase pool size by adding more aiciv containers

---

## Both Pages Are Identical in Behavior

- sandbox-2 and pay-test-2 have the same PTC v4 script
- Both use `WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai'`
- Both hit the same Witness backend
- Both fail with pool_exhausted

Jared's hypothesis that "sandbox-2 might work but pay-test-2 doesn't" is NOT confirmed.
Both pages fail for the same reason at the backend.

---

## Playwright Testing Limitation Discovered

Cloudflare WAF blocks headless browser attempts when they:
1. Submit the WP post password form and then navigate
2. Trigger network idle detection

The WAF sees the headless browser pattern and serves "Please verify you are human" CAPTCHA.

Workaround: Use short timeout + no navigation interception. The first test run (before rate limit)
got through with `wait_until="domcontentloaded"` + manual `page.wait_for_timeout(5000)`.

After WAF rate limit kicks in: tests return 429 and hit the CAPTCHA page.
Wait ~30min between headless test runs to avoid WAF block.

---

## Key Backend Test Commands

```bash
# Test birth/start - CORRECT payload
curl -X POST https://api.purebrain.ai/api/birth/start \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","human_name":"Test User","tier":"awakened"}' \
  --max-time 15

# Direct IP
curl -X POST https://89.167.19.20:8443/api/birth/start \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","human_name":"Test User","tier":"awakened"}' \
  --insecure --max-time 12

# Health check (working)
curl https://89.167.19.20:8443/api/health --insecure
curl https://api.purebrain.ai/api/health
curl http://104.248.239.98:8099/api/health
```

---

## What the Chat Flow Looks Like

The "Begin Awakening" button click fires `startConversation()` in the PTC script.
The chat walks through name → email → company → role, then auto-fires `runBirthInit()`.
`runBirthInit()` POSTs to /api/birth/start with the user's name, email, tier.
If 503, the chatbox shows retry messages and "Retry Connection" / "Continue without linking" buttons.
No OAuth button ever appears — OAuth URL comes BACK from /birth/start response.

**Tags**: purebrain, pay-test, oauth, birth-pipeline, witness, pool-exhausted, 503, containers, aiciv
