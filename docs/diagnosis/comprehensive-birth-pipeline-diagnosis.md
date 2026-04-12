# Comprehensive Birth Pipeline & OAuth Diagnosis
## 2026-02-27 — Multi-Agent Investigation Results

**Agents Deployed**: 7 (collective-liaison, browser-vision-tester x2, full-stack-developer x2, devops-engineer, code-archaeologist)

---

## EXECUTIVE SUMMARY

The OAuth button failure and birth pipeline issues have **three independent root causes**, all of which must be resolved for E2E testing:

1. **CSP Block** (GoDaddy restore side-effect) — Browser silently blocks all birth calls
2. **Witness Server Down** — 104.248.239.98:8099 unreachable for ~42 hours
3. **Container Pool Exhausted** — All 5 containers stuck from test runs

Additionally, two code gaps exist:
4. **`orderId` not passed** to post-payment flow (always null)
5. **`/birth/seed` not wired** at flow:complete (Trigger 3 doesn't exist)

---

## ROOT CAUSE #1: CSP BLOCK (Highest Priority Fix)

### The Problem
The page chatbox JS calls:
```javascript
const WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443';
```

But the plugin's Content Security Policy `connect-src` does NOT include `89.167.19.20:8443`:
```
connect-src 'self' https://api.purebrain.ai https://api.puremarketing.ai ... https://cdn.jsdelivr.net;
```

**Every `fetch()` call to birth/start, birth/code, and portal-status is silently blocked by the browser.**

### Why This Worked Before
- **v4.6.4** (running at 5am Feb 27) added `https://89.167.19.20:8443` to CSP connect-src
- **v4.6.3** (current after GoDaddy restore) does NOT have this line
- GoDaddy restore rolled plugin back to v4.6.3, removing the CSP whitelist

### Fix Options
| Option | Effort | Risk | Long-term |
|--------|--------|------|-----------|
| A) Re-add CSP line (deploy v4.6.4-minimal) | 1 line | Low | Medium |
| B) Change page JS to use `api.purebrain.ai` | 2 pages | Medium | Best |
| C) Add both (CSP + page JS update) | Both | Low | Best |

**Recommendation: Option A first (1-line plugin fix), then Option B when convenient.**

### The 1-Line Fix (Option A)
In the plugin CSP section, add to connect-src:
```php
.     "https://89.167.19.20:8443; "
```
This is exactly what v4.6.4 did. Everything else stays identical to v4.6.3.

---

## ROOT CAUSE #2: WITNESS SERVER DOWN

### Evidence
- `curl http://104.248.239.98:8099/health` → no response (connection refused/timeout)
- Log server shows 504 timeouts for `/api/birth/start` proxy calls
- Last successful `birth:start:url_ready`: 2026-02-25 23:49 UTC (~42 hours ago)
- Witness crash-recovery message at 2026-02-27 11:31 UTC (they recovered but containers still stuck)

### Action Required
Witness/Corey must restart the server at 104.248.239.98:8099 and free containers.

Hub message sent to witness-aether room (message ID: 01KJG0Z2ZVZ2Q0P8VN3MRVZE5Y) with full status update and 4 priority asks.

---

## ROOT CAUSE #3: CONTAINER POOL EXHAUSTED

All 5 containers (aiciv-06 through aiciv-10) are stuck from test runs:
- `/api/birth/start` returns `{"error": "No containers available", "reason": "pool_exhausted"}` (HTTP 503)
- OAuth URL never generated → OAuth button never renders
- This affects BOTH pages identically

---

## THE 3 TRIGGER POINTS — Detailed Status

### Trigger 1: Post-Payment → /birth/start
| Aspect | Status |
|--------|--------|
| Code wired? | YES — `runBirthInit()` sends `{name, email, human_name, tier}` |
| Proxy working? | YES — log server at 89.167.19.20:8443 forwards to 104.248.239.98:8099 |
| CSP allows? | NO — v4.6.3 blocks 89.167.19.20:8443 |
| Witness responds? | NO — server down + containers exhausted |
| Data reaches Witness? | NO — blocked at browser level |

### Trigger 2: OAuth Code → /birth/code
| Aspect | Status |
|--------|--------|
| Code wired? | YES — sends `{container, auth_code}` after user pastes code |
| Proxy working? | YES — same proxy chain |
| CSP allows? | NO — same CSP block |
| Witness responds? | NO — server down |
| Reachable? | NO — never gets here because Trigger 1 fails |

### Trigger 3: End of Chat → /birth/seed
| Aspect | Status |
|--------|--------|
| Code wired? | NO — flow:complete only logs to local server |
| Proxy exists? | NO — /birth/seed proxy not in log server |
| Witness endpoint? | NO — /birth/seed doesn't exist on Witness side |
| Spec agreed? | NO — payload proposed by Aether, awaiting Witness confirmation |

---

## CODE BUGS FOUND

### Bug 1: orderId Never Passed (P1)
In the integration glue script, `launchPostPaymentFlow` calls:
```javascript
initPayTestFlow(chatContainer, aiName, tier)
// Missing 4th argument: orderId
```
Function signature: `initPayTestFlow(chatContainer, aiName, tierPaid, orderId)`
Result: `payTestData.orderId = null` in every log entry.

### Bug 2: /birth/seed Not Wired (P2)
At flow:complete:
```javascript
payTestData.timestamps.flowComplete = new Date().toISOString();
await logPayTestData({ ...payTestData, event: 'flow:complete' });
// NO call to /birth/seed — conversation history + seed data stays local
```

---

## PAGE COMPARISON: 688 vs 689

Both pages have **identical chatbox code**. The only differences are:
- 22-line cosmetic sandbox banner on page 688
- Both use same `WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443'`
- Both use same `PAYPAL_CLIENT_ID` (production)
- Both have same birth pipeline flow

**The difference Jared observed** (OAuth working on sandbox but not production) was purely timing — containers were available when sandbox was tested, exhausted when production was tested.

---

## AETHER-SIDE INFRASTRUCTURE STATUS

| Component | Status |
|-----------|--------|
| Log server (89.167.19.20:8443) | HEALTHY (SSL ok) |
| Birth proxy /start | Configured, forwarding works when Witness responds |
| Birth proxy /code | Configured |
| Birth proxy /portal-status | Configured |
| Birth proxy /seed | NOT BUILT (awaiting Witness spec) |
| Conversation logging | Working — all events recorded |
| PayPal payment flow | Working (v4.6.3 restored) |
| CSP headers | Missing 89.167.19.20:8443 (needs 1-line fix) |
| Hub communication | Working — message sent to Witness |

---

## ACTION PLAN

### Immediate (Aether — with Jared approval)
1. Deploy 1-line CSP fix: add `89.167.19.20:8443` to connect-src
2. Fix orderId pass-through in page integration glue

### Waiting on Witness
3. Free containers aiciv-06 through aiciv-10
4. Restart server at 104.248.239.98:8099
5. Confirm v1.2.0 API contract
6. Spec /birth/seed endpoint

### After Witness Unblocked
7. E2E test birth pipeline on pay-test-sandbox-2
8. Wire /birth/seed call at flow:complete
9. Add /birth/seed proxy to log server
10. Full E2E production test on pay-test-2

---

## FILES REFERENCED

| File | Description |
|------|-------------|
| `exports/purebrain-security-plugin-v463.php` | LIVE plugin (missing CSP line) |
| `exports/purebrain-security-plugin-v464.php` | Has CSP fix (line 504) |
| `exports/pay-test-2-raw-content.html` | Page 689 full content (433K) |
| `exports/pay-test-sandbox-2-raw-content.html` | Page 688 full content (434K) |
| `tools/purebrain_log_server.py` | Log server + birth proxies (lines 1591-1740) |
| `docs/diagnosis/witness-pipeline-status.md` | Collective-liaison report |
| `docs/diagnosis/seed-pipeline-diagnosis.md` | Full-stack-developer report |
