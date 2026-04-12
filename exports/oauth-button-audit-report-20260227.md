# OAuth Button Audit Report
**Date**: 2026-02-27
**Tester**: browser-vision-tester
**Pages**: pay-test-sandbox-2, pay-test-2
**Status**: ROOT CAUSE FOUND

---

## Executive Summary

The OAuth/login button does not appear on either page. The root cause is NOT a UI bug. It is a backend infrastructure issue: **the Witness server's container pool is exhausted (503 pool_exhausted)**.

Both pages are identical in behavior. Neither works. This contradicts Jared's hypothesis that sandbox-2 might work — both fail for the same reason.

---

## What Happens to Users

1. User lands on page, sees hero section with "Awaken Your PURE BRAIN" button
2. User clicks "Begin Awakening" — chatbox opens
3. User answers name, email, company, role questions
4. After role is submitted, the script auto-fires `runBirthInit()` which POSTs to `/api/birth/start`
5. The server returns: `{"error":"No containers available","status":"pool_exhausted"}`
6. Chatbox shows: "Keen's network is temporarily unavailable"
7. Two buttons appear: [Retry Connection] [Continue without linking]
8. **No OAuth button ever appears** — the OAuth URL is returned inside the /birth/start response

---

## Root Cause: Container Pool Exhausted

### Witness Server Status

| Endpoint | Health | birth/start |
|----------|--------|-------------|
| `https://api.purebrain.ai/api/birth/start` | OK (200) | 503 pool_exhausted |
| `https://89.167.19.20:8443/api/birth/start` | OK (200) | 503 pool_exhausted |
| `http://104.248.239.98:8099/api/birth/start` | OK (200) | 503 pool_exhausted |

### Actual Response from Server

```json
{
  "error": "No containers available",
  "pool": ["aiciv-06", "aiciv-07", "aiciv-08", "aiciv-09", "aiciv-10"],
  "status": "pool_exhausted"
}
```

The Witness server has 5 containers in its pool (aiciv-06 through aiciv-10). All of them are currently in use or stuck. The server cannot start a new birth session.

### Earlier in the Day

Earlier this morning the same endpoints were TIMING OUT entirely (status 000, took 10-15 seconds). Now they respond quickly with 503. This suggests the server was previously unreachable, and has since come back up — but with all containers occupied.

---

## Page Comparison: sandbox-2 vs pay-test-2

| Aspect | sandbox-2 | pay-test-2 |
|--------|-----------|------------|
| HTTP status | 200 | 200 |
| Page loads | Yes | Yes |
| Chatbox present | Yes | Yes |
| "Begin Awakening" button | Yes | Yes |
| PTC script in DOM | Yes | Yes |
| `runBirthInit` in source | Yes | Yes |
| `WITNESS_WEBHOOK_HOST` | `https://api.purebrain.ai` | `https://api.purebrain.ai` |
| Script version | Same | Same |
| birth/start result | 503 pool_exhausted | 503 pool_exhausted |
| OAuth button appears | No | No |

**Conclusion: Both pages are identical. Neither works. The sandbox-2 vs pay-test-2 difference Jared noticed is not a code difference — both run the same PTC script and hit the same Witness backend.**

---

## Visual Evidence

### sandbox-2 Full Page View

The page renders correctly. Hero section visible. Chat widget section rendered. Orange branding matches spec. "SANDBOX MODE - No real charges" banner present at top.

### pay-test-2 Full Page View

Same layout, slightly different hero text ("YOUR BRAIN. YOUR AI." vs sandbox version). No sandbox banner (correct — this is production). Otherwise identical behavior.

### Chat Flow State

After clicking "Begin Awakening", the chatbox opens and shows the initial spinner. But because `startConversation()` depends on the PTC script loading properly (which requires the page password to work correctly in the browser), the chat questions themselves may not advance in Playwright testing due to WAF interference.

---

## Secondary Finding: WAF Blocking Headless Tests

Cloudflare's WAF is now actively blocking headless Playwright sessions after the first few requests. After the WP password form submit, Cloudflare serves a "Please verify you are human" CAPTCHA page instead of the real page content.

**Impact on testing**: Backend curl tests are reliable. Browser-based Playwright tests are intermittent.

**Workaround**: Test the backend API directly via curl (confirmed above). Wait 30+ minutes between headless browser test runs to avoid WAF rate limiting.

---

## CSP Errors (Non-blocking, Pre-existing)

Both pages have CSP errors that block Google Tag Manager and WonderPush scripts. These are pre-existing and unrelated to the OAuth issue. The CSP that matters is the `connect-src` which DOES allow `https://api.purebrain.ai` — so the fetch to birth/start should work once the pool is available.

---

## What Needs to Be Fixed

### Priority 1: Reset the Container Pool (Witness Server)

On the server at `104.248.239.98` or wherever the Witness server runs:

```bash
# Check which containers are stuck
docker ps -a | grep aiciv

# Restart stuck containers (replace with actual container names)
docker restart aiciv-06 aiciv-07 aiciv-08 aiciv-09 aiciv-10

# Or reset them through the Witness API if it has an admin endpoint
# Check with full-stack-developer / Witness team
```

The Witness API needs a way to release/reset containers when sessions expire or get stuck.

### Priority 2: Verify the Fix

Once containers are reset:

```bash
curl -X POST https://api.purebrain.ai/api/birth/start \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","human_name":"Test User","tier":"awakened"}'
```

Expected response: HTTP 200 with OAuth URL and container assignment.

### Priority 3: Add Container Health Monitoring

The pool should not silently exhaust. Aether's monitoring should alert when:
- Pool utilization > 80%
- /birth/start returns 503
- A container has been occupied for > 30 minutes (likely stuck)

---

## Screenshots Saved

Location: `/home/jared/projects/AI-CIV/aether/exports/screenshots/oauth-audit-20260227-v2/`

Key files:
- `sandbox2-03-full-page-full.png` — Full page visual, sandbox-2
- `paytest2-03-full-page-full.png` — Full page visual, pay-test-2
- `sandbox2-04-before-begin.png` — Before clicking Begin Awakening
- `sandbox2-05-after-begin.png` — After clicking Begin Awakening (chat widget)

---

## Escalation

This requires the **full-stack-developer** or **Witness team** to reset the container pool on the Witness server. browser-vision-tester has confirmed the diagnosis. No UI code changes are needed.

---

**Report by**: browser-vision-tester
**Memory written**: `.claude/memory/agent-learnings/browser-vision-tester/2026-02-27--oauth-button-pool-exhausted-root-cause.md`
