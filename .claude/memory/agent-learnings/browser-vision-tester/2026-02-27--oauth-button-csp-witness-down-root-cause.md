# Memory: OAuth Button Not Rendering — Root Cause Diagnosis

**Date**: 2026-02-27
**Type**: teaching + operational
**Topic**: OAuth button on post-payment chatbox not working — root cause: /api/birth/start failing at network layer

---

## The Bug: OAuth Button Never Appears

The v4.3.3 PTC script dynamically creates the OAuth button ONLY after `/api/birth/start` returns a valid OAuth URL. If that API call fails, no button is ever rendered.

This is why both pages appear "broken" — it's not a UI bug, it's a backend connectivity bug.

---

## Root Cause: Dual Failure

### Sandbox (pay-test-sandbox-2, page 688)

**Failure**: Content Security Policy blocks fetch to Witness IP

The sandbox script's `WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443'` (direct IP).
WordPress CSP does NOT whitelist `89.167.19.20:8443` in `connect-src`.
Result: All 3 fetch attempts fail with CSP violation.

Console errors:
```
ERROR: Connecting to 'https://89.167.19.20:8443/api/birth/start' violates CSP
ERROR: [ptc-v4] birth/start attempt 1/3 failed: Failed to fetch
ERROR: [ptc-v4] birth/start attempt 2/3 failed: Failed to fetch
ERROR: [ptc-v4] birth/start attempt 3/3 failed: Failed to fetch
```

Additionally: `POST https://89.167.19.20:8443/api/birth/start` from server-side curl TIMES OUT — the Witness server is DOWN or not accepting connections.

### Production (pay-test-2, page 689)

**Failure**: `api.purebrain.ai` proxy times out

Direct test of `POST https://api.purebrain.ai/api/birth/start` — connects to Cloudflare (172.67.160.10) but the backend never responds. Exit code 28 (timeout).

Additionally: `POST https://purebrain.ai/api/birth/start` (same-origin request pattern) returns 404 from WordPress.

---

## Both Scripts Are Identical

- Script size: 88,337 bytes on BOTH pages
- Script version: v4.3.3 on BOTH pages
- They should be different (sandbox = direct IP, prod = api.purebrain.ai proxy)
- But both pages have the SAME script deployed

---

## What the Error Looks Like to Users

After entering their role/title, the chatbox shows:
```
"The next step in Keen's set up, Jared.
 I need to link Keen's intelligence now — this takes about 30 seconds. Reaching out to Keen's network…"
"Still connecting to Keen's network… attempt 1 timed out. Trying again."
"Still connecting to Keen's network… attempt 2 timed out. Trying again."
"Keen's network is temporarily unavailable. This can happen during high traffic.
 Tap the button below to try again."
```

Buttons shown: [Retry Connection →] [Continue without linking]
NO OAuth button appears.

---

## What Needs to Be Fixed

1. **Witness server at 89.167.19.20:8443** — TIMED OUT from server curl. Is it down?
2. **api.purebrain.ai backend** — Times out. Is the proxy up?
3. **Both scripts same** — Production script should use `https://api.purebrain.ai` not the raw IP
4. **CSP** — Sandbox CSP must whitelist the Witness IP if it's going to be used directly

---

## Test Commands

```bash
# Test Witness direct
curl -X POST https://89.167.19.20:8443/api/birth/start \
  -H "Content-Type: application/json" -d '{"container":"aiciv-07"}' --insecure --max-time 10

# Test api.purebrain.ai proxy
curl -X POST https://api.purebrain.ai/api/birth/start \
  -H "Content-Type: application/json" -d '{"container":"aiciv-07"}' --max-time 10

# Test log server (same IP, port 8443 - this one WAS working)
curl -X GET https://89.167.19.20:8443/api/health --insecure --max-time 5
```

---

## Testing Patterns Confirmed

- Sandbox payment bypass: Works when /api/verify-payment returns success-like response (400 with error triggers partial behavior)
- PTC loads after bypass: YES (`ptc-wrapper` appears)
- Questionnaire: Name, email, company, role all work
- `/api/birth/start` always called immediately after role is submitted (v4.3.3 behavior: auto-fires, no button)
- After 3 failed attempts: "Retry Connection" and "Continue without linking" buttons appear

---

## Screenshots (Evidence)

- `exports/screenshots/oauth-diagnosis-20260227/sandbox-v3-ptc-05-post-role-oauth-check.png` — failure state visual
- `exports/screenshots/oauth-diagnosis-20260227/sandbox-v3-ptc-07-auth-btn-0.png` — retry loop visual

**Tags**: purebrain, pay-test, oauth, birth-pipeline, csp, witness, down, v4.3.3, root-cause
