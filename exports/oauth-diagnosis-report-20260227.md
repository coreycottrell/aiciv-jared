# OAuth Button Diagnosis Report
**Date**: 2026-02-27
**Tester**: browser-vision-tester
**Pages tested**: pay-test-sandbox-2 (page 688) + pay-test-2 (page 689)
**Status**: ROOT CAUSE IDENTIFIED

---

## TL;DR — The Root Cause

**Both pages have the IDENTICAL script (v4.3.3, 88,337 bytes).**

The OAuth button is NOT broken in the UI code. It NEVER RENDERS because `/api/birth/start` fails with a CSP violation on sandbox and a 404 on production.

The OAuth button is dynamically created ONLY after `/api/birth/start` returns a valid OAuth URL. That call is failing at the network layer before any button can appear.

---

## What Actually Happens

### Flow (per script code comments)

```
User enters role (Q4)
  → runBirthInit() fires automatically
    → POST /api/birth/start { "container": "aiciv-07" }
      → Witness returns OAuth URL
        → Script injects "Authorize Keen's AI Brain →" button
          → User clicks it → opens claude.ai OAuth
```

**The OAuth button exists only after /api/birth/start succeeds.**

If /api/birth/start fails: the button never appears.

---

## Sandbox Page (pay-test-sandbox-2)

### What I saw

After entering role (CEO), the PTC showed:

```
"The next step in Keen's set up, Jared.
 I need to link Keen's intelligence now — this takes about 30 seconds. Reaching out to Keen's network…"

→ "Still connecting to Keen's network… attempt 1 timed out. Trying again."
→ "Still connecting to Keen's network… attempt 2 timed out. Trying again."
→ "Keen's network is temporarily unavailable. This can happen during high traffic. Tap the button below to try again."

Buttons shown: [Retry Connection →] [Continue without linking]
```

The OAuth button ("Authorize Keen's AI Brain →") was NEVER rendered.

### Console Errors (on sandbox)

```
ERROR: Connecting to 'https://89.167.19.20:8443/api/birth/start' violates the following
       Content Security Policy directive: "connect-src 'self' https://api.purebrain.ai
       https://api.puremarketing.ai ..."

ERROR: Fetch API cannot load https://89.167.19.20:8443/api/birth/start. Refused to connect
       because it violates the document's Content Security Policy.

ERROR: [ptc-v4] birth/start attempt 1/3 failed: Failed to fetch
ERROR: [ptc-v4] birth/start attempt 2/3 failed: Failed to fetch
ERROR: [ptc-v4] birth/start attempt 3/3 failed: Failed to fetch
```

### Why sandbox fails

The sandbox page script has `WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443'` (direct IP, per v4.3.1 changelog).

But the WordPress page's Content Security Policy does NOT include `https://89.167.19.20:8443` in its `connect-src` directive.

**CSP whitelist** (from error message):
- `https://api.purebrain.ai` ← allowed
- `https://api.puremarketing.ai` ← allowed
- `https://89.167.19.20:8443` ← BLOCKED

The script tries to reach the Witness directly via its IP, but WordPress's CSP header says no. All 3 retry attempts fail. The OAuth URL is never returned. The button never appears.

---

## Production Page (pay-test-2)

### What I saw

The production page uses the SAME 88,337-byte script. But:

The production script should use `WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai'` (the HTTPS proxy). However, when I tested `/api/birth/start` from the production page context:

```
POST https://purebrain.ai/api/birth/start
Response: 404
Body: (WordPress HTML — the WordPress 404 page)
```

### The Production Problem

The production page calls `https://purebrain.ai/api/birth/start` but that endpoint returns a **404 from WordPress**.

The `/api/birth/start` proxy is NOT configured on purebrain.ai's WordPress hosting. The endpoint `https://api.purebrain.ai/api/birth/start` (via the HTTPS proxy) might be correct, but the script may be routing the request through `purebrain.ai/api/birth/start` instead.

**Note**: I could not complete the full production questionnaire flow without real payment, so the exact network call the production page makes during the flow could not be confirmed. But the direct test of `/api/birth/start` from the production page context returned 404.

---

## Script Comparison

| Property | Sandbox | Production |
|----------|---------|------------|
| Script size | 88,337 bytes | 88,337 bytes |
| Script version | v4.3.3 | v4.3.3 |
| Same script? | YES — IDENTICAL |  |
| WITNESS_WEBHOOK_HOST (in script) | `https://89.167.19.20:8443` (per v4.3.1 comment) | same script, same value |
| What should be true | sandbox = direct IP, prod = api.purebrain.ai | These are supposed to be DIFFERENT |

**Critical finding**: The sandbox and production pages are using the IDENTICAL script file. Per the v4.3.1 changelog comment in the script, the sandbox page is supposed to use the direct IP (`http://104.248.239.98:8099` originally, now `https://89.167.19.20:8443`) and the production page is supposed to route through `https://api.purebrain.ai`.

If both pages got the same script deployed, the production page is also pointing to the raw Witness IP — which would explain why the OAuth button doesn't work on production either.

---

## Root Cause Summary

### Sandbox (pay-test-sandbox-2)
**Root cause**: Content Security Policy violation.
- Script calls `https://89.167.19.20:8443/api/birth/start`
- WordPress CSP does not whitelist this IP
- Browser blocks all 3 fetch attempts
- OAuth URL never returned → OAuth button never shown

### Production (pay-test-2)
**Root cause**: Either same CSP issue OR `/api/birth/start` endpoint not reachable.
- Direct test of `POST https://purebrain.ai/api/birth/start` → 404
- If production script also points to `89.167.19.20:8443` (same script), same CSP block
- Even if pointing to `api.purebrain.ai`, that endpoint may not be functional

---

## Fix Required

### Option A: Fix CSP (Sandbox — Immediate)

Add `https://89.167.19.20:8443` to the WordPress `connect-src` CSP directive on purebrain.ai.

Or change the sandbox script's `WITNESS_WEBHOOK_HOST` back to go through `https://api.purebrain.ai` (the proxy).

**The question is: is the Witness server at `89.167.19.20:8443` actually up and running?**

### Option B: Separate Scripts for Sandbox vs Production

The v4.3.1 changelog says sandbox uses direct IP and production uses the proxy. But right now BOTH pages have the identical 88,337-byte script. They need separate script versions:

- **Sandbox script**: `WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443'` (direct)
- **Production script**: `WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai'` (proxy)

AND the sandbox CSP must allow `89.167.19.20:8443`.

### Option C: Test if the Witness endpoint works at all

Before fixing the script/CSP, verify Witness is up:

```bash
curl -X POST https://89.167.19.20:8443/api/birth/start \
  -H "Content-Type: application/json" \
  -d '{"container": "aiciv-07"}' \
  --insecure
```

If this returns a valid OAuth URL, the Witness is healthy and the CSP is the only blocker.

If this fails too, the Witness server is down — fix that first.

---

## Evidence Screenshots

All screenshots in: `/home/jared/projects/AI-CIV/aether/exports/screenshots/oauth-diagnosis-20260227/`

| File | What it shows |
|------|--------------|
| `sandbox-v3-ptc-05-post-role-oauth-check.png` | The failure state: "Retry Connection" button instead of OAuth button |
| `sandbox-v3-ptc-07-auth-btn-0.png` | After retry: same failure, retrying /api/birth/start |
| `sandbox-v3-03-ptc-loaded.png` | PTC successfully loaded after sandbox payment bypass |
| `sandbox-06-after-js-click.png` | PayPal modal with "Simulate Successful Payment" button |
| `sandbox-07-after-sandbox-bypass.png` | PTC initial state — questionnaire started |

---

## What is Working

- Both pages: password unlock works
- Both pages: pre-payment Claude chat works (via api.puremarketing.ai)
- Sandbox: payment bypass works (sandbox bypass button renders and functions)
- Sandbox: PTC loads correctly after simulated payment
- Sandbox: Questionnaire flows (name, email, company, role) all work
- Both: api.purebrain.ai logging endpoints work (200 responses)
- PayPal SDK: Loads on both pages

---

## What is NOT Working

1. `POST /api/birth/start` on sandbox → CSP block (all 3 attempts fail)
2. `POST /api/birth/start` on production → 404 from WordPress
3. OAuth button → Never rendered (depends on /api/birth/start succeeding)
4. `POST /api/verify-payment` on sandbox → 400 (missing `order_id` field)

---

## Immediate Next Step

1. Check if Witness server at `89.167.19.20:8443` is alive (curl test above)
2. If alive: Add to CSP whitelist for sandbox, then test
3. If production script also uses the raw IP: Deploy separate production script with `WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai'`
4. Verify `https://api.purebrain.ai/api/birth/start` is working end-to-end

---

**End of report.**
