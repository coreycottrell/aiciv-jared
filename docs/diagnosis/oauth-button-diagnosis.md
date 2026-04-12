# OAuth Button Diagnosis: pay-test-2 vs pay-test-sandbox-2

**Date**: 2026-02-27
**Investigator**: browser-vision-tester
**Pages**: 689 (pay-test-2) and 688 (pay-test-sandbox-2)
**Status**: Root cause confirmed — three compounding issues identified

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/browser-vision-tester/` for pay-test, oauth, auth, sandbox
- Found: 14 prior entries from today (2026-02-27) covering two earlier diagnosis cycles
- Applying: Pool exhaustion pattern, CSP analysis, script identity findings from prior work

---

## Executive Summary

The OAuth button does NOT appear on EITHER page. The failure is NOT a code difference between the two pages — it is a backend outage. The Witness server (104.248.239.98:8099) that generates OAuth URLs is DOWN and unreachable.

**Bottom line**: The OAuth button is dynamically created ONLY after `/api/birth/start` returns a valid OAuth URL. If that call fails, no button ever renders. Both pages fail for the same backend reason.

---

## Page Comparison: What IS Different

### Script Size Difference

| Property | Page 689 (pay-test-2) | Page 688 (pay-test-sandbox-2) |
|----------|----------------------|-------------------------------|
| Total content length | 433,361 chars | 434,116 chars |
| Large PTC script size | 269,139 chars | 269,908 chars |
| Script MD5 | `532a5e98d0931abf68a68fecb0c6aeec` | `fcbfd3403421b101f6db3f5348d36ca4` |

The ONLY code difference between the two pages is a 22-line sandbox mode banner HTML block that exists only on page 688:

```html
<div id="sandbox-banner" style="position:fixed; top:0; background:#f1420b; ...">
    SANDBOX MODE - No real charges will occur.
</div>
<div style="height:44px;"></div>
```

This cosmetic banner has NO effect on OAuth functionality.

### PayPal Client ID Difference

| Page | PayPal Client ID | Type |
|------|-----------------|------|
| 689 (pay-test-2) | `AWgWNlBQAy5BMXKB5xbaMwSk...` | PRODUCTION |
| 688 (pay-test-sandbox-2) | `AYTFob05DoSn0ZeVtLJ05duKw...` | SANDBOX |

This is correct — sandbox uses sandbox PayPal credentials, production uses live credentials.

### WITNESS_WEBHOOK_HOST (BOTH PAGES IDENTICAL)

Both pages use:
```javascript
const WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443';
```

This points to the log server, which proxies to Witness at `http://104.248.239.98:8099`.

---

## Why the OAuth Button Doesn't Appear: Three Issues

### Issue 1: WITNESS_WEBHOOK_HOST Points to Direct IP (CSP VIOLATION)

**Severity**: CRITICAL

The pages call `WITNESS_WEBHOOK_HOST` which is `https://89.167.19.20:8443`.

The WordPress CSP `connect-src` whitelist is:
```
connect-src 'self'
  https://api.purebrain.ai         <- ALLOWED
  https://api.puremarketing.ai     <- ALLOWED
  https://pure-brain-dashboard-api.purebrain.workers.dev  <- ALLOWED
  https://www.paypal.com           <- ALLOWED
  ...
  (89.167.19.20:8443 is NOT listed)   <- BLOCKED
```

Any browser-side `fetch()` to `https://89.167.19.20:8443/api/birth/start` will be blocked by the browser's CSP enforcement before the request even leaves the browser.

**Note**: The log server at 89.167.19.20:8443 IS a valid proxy for birth/start (it has the `/api/birth/start` route). The problem is the CSP does not whitelist this IP, so browsers block the call.

**Fix**: Change `WITNESS_WEBHOOK_HOST` on both pages from `https://89.167.19.20:8443` to `https://api.purebrain.ai` (which IS in the CSP whitelist and also proxies to the same Witness backend).

### Issue 2: Witness Backend Server is DOWN

**Severity**: CRITICAL

The Witness server at `http://104.248.239.98:8099` is completely unreachable:
- `/api/health` → HTTP 000 (connection refused/timeout)
- `/api/birth/start` → HTTP 000 (connection refused/timeout)

Even if the CSP issue is fixed, the proxy at `api.purebrain.ai` would forward to this dead Witness server and still return a timeout.

```bash
# Tested 2026-02-27 17:01 UTC — all return HTTP 000:
curl http://104.248.239.98:8099/api/health      # TIMEOUT
curl https://89.167.19.20:8443/api/birth/start  # TIMEOUT (proxied to 104.248.239.98:8099)
curl https://api.purebrain.ai/api/birth/start   # TIMEOUT (proxied to 104.248.239.98:8099)
```

The log server at 89.167.19.20:8443 is healthy (health check returns 200), but its birth/start proxy target is dead.

**What users see** (from PTC v4 script after 3 failed attempts):
```
"Still connecting to Keen's network… attempt 1 timed out. Trying again."
"Still connecting to Keen's network… attempt 2 timed out. Trying again."
"Keen's network is temporarily unavailable."
[Retry Connection] [Continue without linking]
```
No OAuth button ever appears.

**Fix**: The Witness server at 104.248.239.98:8099 needs to be restarted or the Docker containers need to be reset. This is a Witness admin task (Jared or full-stack-developer).

### Issue 3: Earlier Today — Container Pool Exhausted (Now Compounded by Server Down)

**Severity**: HIGH (earlier state)

An earlier audit (this morning) found the Witness server was responding with:
```json
{"error":"No containers available","pool":["aiciv-06","aiciv-07","aiciv-08","aiciv-09","aiciv-10"],"status":"pool_exhausted"}
HTTP 503
```

The server was alive but had no available containers. Since then, the server appears to have gone further down (now timing out entirely, not even returning 503).

---

## What OAuth Actually Does (Architecture Clarification)

For anyone confused about "OAuth button not working" — there is no static OAuth button in the HTML. The OAuth button is DYNAMICALLY CREATED by the PTC script:

```
Flow:
1. User completes chatbox (name, email, company, role)
2. PTC auto-fires runBirthInit()
3. runBirthInit() calls POST /api/birth/start (WITNESS_WEBHOOK_HOST)
4. Witness allocates a Docker container, generates Claude.ai OAuth URL
5. Witness returns: {"status":"url_ready","oauth_url":"https://claude.ai/oauth/authorize?..."}
6. PTC creates the OAuth button dynamically using that URL
7. User clicks OAuth button → goes to Claude.ai to authorize
```

If step 3 fails (CSP block OR Witness down), steps 4-7 never happen. No OAuth button appears.

There is no Google OAuth, no Google Sign In, no OAuth client ID on these pages. The "OAuth" is Claude.ai OAuth (for Claude API key generation via the Witness birth pipeline).

---

## No Differences in OAuth Implementation

The two pages have **identical OAuth logic**:
- Same `runBirthInit()` function (MD5 confirmed)
- Same `WITNESS_WEBHOOK_HOST` value
- Same MAX_BIRTH_RETRIES (3)
- Same error handling
- Same button creation logic
- Same `oauthUrl` validation (HTTPS + claude.ai/anthropic.com domain check)

The pages are functionally identical for the post-payment OAuth flow. The ONLY difference is the sandbox banner HTML (cosmetic) and the PayPal client ID (correct by design).

---

## What Needs to Be Fixed (Priority Order)

### Fix 1 (URGENT — Witness Admin):
Restart the Witness server at `104.248.239.98:8099`. It is completely down. Check if:
- The Docker service is stopped
- Containers are in an error state
- Port 8099 is not listening

```bash
# On Witness server (SSH to 104.248.239.98):
docker ps -a | grep aiciv
sudo systemctl status witness-server   # or however Witness is managed
curl http://localhost:8099/api/health  # test locally on Witness box
```

### Fix 2 (AFTER Fix 1 — Code Change on Both Pages):
Change `WITNESS_WEBHOOK_HOST` in both page 689 and 688 from:
```javascript
const WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443';
```
to:
```javascript
const WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai';
```

This ensures the browser's CSP will not block the fetch (api.purebrain.ai IS in connect-src). The log server will still proxy to Witness.

### Fix 3 (If Pool Was Exhausted Before Going Down):
After restarting Witness, verify containers are available:
```bash
curl http://104.248.239.98:8099/api/health
# Should show healthy containers
```
If pool is exhausted: release stuck containers or add more aiciv containers.

---

## Test Verification Commands (Run After Fixes)

```bash
# 1. Verify Witness is up
curl http://104.248.239.98:8099/api/health --max-time 10
# Expected: {"status":"ok",...}

# 2. Verify birth/start works via log server proxy
curl -X POST https://89.167.19.20:8443/api/birth/start \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","human_name":"Test","tier":"awakened"}' \
  --insecure --max-time 60
# Expected: {"status":"url_ready","oauth_url":"https://claude.ai/oauth/..."}

# 3. Verify birth/start works via api.purebrain.ai (CSP-safe path)
curl -X POST https://api.purebrain.ai/api/birth/start \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","human_name":"Test","tier":"awakened"}' \
  --max-time 60
# Expected: {"status":"url_ready","oauth_url":"https://claude.ai/oauth/..."}
```

---

## Playwright Testing Note

The WAF (GoDaddy) blocks headless browser attempts after 3+ password form submissions within ~30 minutes. Wait 15-20 minutes between automated test runs. Use the local serving workaround (WP REST API fetch + local Python server) to avoid WAF.

---

## File Locations

- This report: `docs/diagnosis/oauth-button-diagnosis.md`
- Prior memory entries:
  - `.claude/memory/agent-learnings/browser-vision-tester/2026-02-27--oauth-button-csp-witness-down-root-cause.md`
  - `.claude/memory/agent-learnings/browser-vision-tester/2026-02-27--oauth-button-pool-exhausted-root-cause.md`
  - `.claude/memory/agent-learnings/browser-vision-tester/2026-02-27--paytest2-chatbox-begin-awakening-verified.md`

---

**Diagnosis complete. The OAuth button failure is a backend issue, not a frontend code difference.**
