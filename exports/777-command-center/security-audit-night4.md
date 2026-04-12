# Security Audit Report — 777 Command Center
**Date**: 2026-03-24
**Auditor**: security-auditor (Aether CIV)
**Scope**: index.html, api/chat.js, api/edit.js, vercel.json
**Purpose**: Pre-production security review

---

## Executive Summary

**Overall Posture: MEDIUM RISK** — The application is a private single-user dashboard with no PII collection or payment processing. Most findings are architectural limitations of the chosen security model (client-side password gate). The API layer (chat.js, edit.js) is well-constructed with meaningful input validation. No active exploits are likely against a determined attacker who knows the URL, but the client-side password provides near-zero real security.

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High | 2 |
| Medium | 3 |
| Low | 2 |
| Info | 2 |

---

## Findings

---

### [SEC-001] CRITICAL: Password Exposed in Client-Side JavaScript

**File**: `index.html`, line 2280 and 3591; `api/edit.js`, line 36

**Evidence**:
```js
// index.html line 2280
const PASSWORD = '777grind';

// index.html line 3591 — also sent in every /api/edit request body
body: JSON.stringify({ password: '777grind', table: 'daily_scores', ... })

// api/edit.js line 36
const DASHBOARD_PASSWORD = '777grind';
```

**Impact**: Any person who opens DevTools (F12) or views page source can read the password instantly. The `localStorage.setItem('777_unlocked', '1')` bypass compounds this: once someone knows the trick, they can set that key directly and skip the gate entirely. The password also ships over the wire in every `/api/edit` POST body in plaintext.

**Threat**: Low-sophistication attacker with access to the URL gains full dashboard access and write capability to all data tables.

**Remediation**:
1. The correct model for a private single-user dashboard is **server-side session authentication** (e.g., a Vercel Edge middleware that issues a signed HttpOnly cookie after verifying a secret stored in an env var).
2. Short-term (keeps existing architecture): move the password to a Vercel env var (`DASHBOARD_PASSWORD`), validate it in `/api/edit`, and have the client obtain a short-lived signed token from a dedicated `/api/auth` endpoint. The token is stored in `sessionStorage` (not `localStorage`) and sent as a `Bearer` header on subsequent requests.
3. Remove the hardcoded `'777grind'` string from all `.js` files and `index.html` before any deployment.

---

### [SEC-002] HIGH: /api/edit Has No CORS Enforcement

**File**: `api/edit.js`

**Evidence**: Unlike `api/chat.js`, `edit.js` does not check the `Origin` header at all. There is no CORS enforcement and no `isAllowedOrigin()` check. The only auth is the hardcoded password in the request body (see SEC-001).

**Impact**: Any website can POST to `https://777-command-center.vercel.app/api/edit` with `{ password: '777grind', ... }` and write arbitrary values to `daily_scores`, `seven_fs`, `goals`, or `proof_wall`. Because the password is public (SEC-001), this is trivially exploitable cross-origin.

**Remediation**:
1. Add the same `isAllowedOrigin()` / CORS header pattern used in `chat.js`.
2. Respond to `OPTIONS` preflight.
3. Return `403 Forbidden` for disallowed origins.

```js
// Add at top of edit.js handler
const origin = req.headers['origin'] || '';
if (!isAllowedOrigin(origin)) {
  return res.status(403).json({ ok: false, error: 'Forbidden origin' });
}
```

---

### [SEC-003] HIGH: File Write on Vercel Serverless (Ephemeral + Race Condition)

**File**: `api/edit.js`, lines 73–88

**Evidence**:
```js
function readEdits() {
  return JSON.parse(readFileSync(path, 'utf8'));
}
function writeEdits(data) {
  writeFileSync(path, JSON.stringify(data, null, 2), 'utf8');
}
```

**Impact (two distinct issues)**:

1. **Data loss**: Vercel serverless functions run on ephemeral containers. The filesystem is read-only in production except for `/tmp`. `writeFileSync` to a path outside `/tmp` will silently fail or throw on the next cold start, losing all queued edits. The comment in the file acknowledges a "D1 migration path" — this is not implemented yet and the current code is broken in production.

2. **Race condition**: Two simultaneous requests can both call `readEdits()`, each getting the same stale array, then both call `writeEdits()`, with one overwriting the other's edit. This is a classic read-modify-write race with no file locking.

**Remediation**:
1. Implement the D1 migration immediately. A single `INSERT INTO pending_edits` is atomic and works correctly in serverless.
2. Short-term: write to `/tmp/pending-edits.json` (the only writable path) and accept that `/tmp` is ephemeral per container.

---

### [SEC-004] MEDIUM: Vercel Preview Deploy Origin Regex is Overly Broad

**File**: `api/chat.js`, line 148

**Evidence**:
```js
if (/^https:\/\/777-command-center(-[a-z0-9]+)?\.vercel\.app$/.test(origin)) return true;
```

**Impact**: This allows any Vercel preview URL for the `777-command-center` project, including branches created by any collaborator with repo access, or by an attacker who gains push access to the repo. A malicious preview deploy could make authenticated API calls to the production endpoint and consume your Anthropic API quota or attempt prompt injection via the `context` parameter.

**Remediation**: For a single-user tool, remove the preview regex entirely. Only allow the two explicit origins in `ALLOWED_ORIGINS`. When you need to test a preview, temporarily add the specific URL to the array.

```js
function isAllowedOrigin(origin) {
  if (!origin) return false;
  return ALLOWED_ORIGINS.includes(origin);
}
```

---

### [SEC-005] MEDIUM: CSP Contains unsafe-inline for script-src

**File**: `vercel.json`, line 29

**Evidence**:
```json
"script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'"
```

**Impact**: `'unsafe-inline'` permits execution of any inline `<script>` block or `javascript:` URI injected into the page. This largely nullifies XSS protection from the CSP. If an attacker can inject a script tag (e.g., through a `data.json` poisoning attack or DOM-based XSS), the CSP will not block it.

**Note**: The `escHtml()` function is used consistently for user-controlled data rendered into the DOM (confirmed by code review), which reduces XSS risk significantly. The main residual risk is the `data.json` fetch path — if an attacker can man-in-the-middle or replace `data.json`, injected content would be HTML-escaped but the CSP would not prevent other inline script execution.

**Remediation**: Replace `'unsafe-inline'` with a `nonce`-based or `hash`-based CSP. Because this is a static HTML file with all scripts inline, the most practical path is to move all JavaScript to an external `app.js` file served from `'self'` and remove `'unsafe-inline'` entirely.

---

### [SEC-006] MEDIUM: localStorage Auth Token Persists Indefinitely

**File**: `index.html`, lines 1290 and 2577

**Evidence**:
```js
localStorage.setItem('777_unlocked', '1');  // set on unlock
// Auto-unlock check — no expiry:
if (localStorage.getItem('777_unlocked') === '1') { ... }
```

**Impact**: `localStorage` persists until explicitly cleared. There is no expiry, no session timeout, and no "log out" button visible in the audit. On a shared or compromised browser, the dashboard remains permanently accessible to anyone with browser access.

**Remediation**:
1. Replace `localStorage` with `sessionStorage` (clears on tab/browser close).
2. Or add an expiry: store `{ unlocked: true, expires: Date.now() + 8 * 3600 * 1000 }` and check on load.
3. Add a visible "Lock Dashboard" button that calls `localStorage.removeItem('777_unlocked')` and reloads.

---

### [SEC-007] LOW: Rate Limiter Uses Last IP in x-forwarded-for Chain

**File**: `api/chat.js`, line 181; `api/edit.js`, line 160

**Evidence**:
```js
const ip = req.headers['x-real-ip']
         || req.headers['x-forwarded-for']?.split(',').pop()?.trim()
         || ...;
```

**Impact**: `.pop()` takes the **last** value in the `X-Forwarded-For` chain, which is the IP appended by the **last** proxy before Vercel — not necessarily the true client IP. An attacker behind multiple proxies, or one who can control intermediate headers, could rotate IPs to bypass the rate limiter. Vercel sets `x-real-ip` correctly in production; the `x-forwarded-for` fallback is the risk.

**Remediation**: In production on Vercel, always prefer `x-real-ip` (which Vercel injects and cannot be spoofed by the client). Remove the `x-forwarded-for` fallback or take `.shift()` (first value = original client IP) rather than `.pop()`.

---

### [SEC-008] LOW: Anthropic API Error Details Partially Logged

**File**: `api/chat.js`, line 262

**Evidence**:
```js
console.error('Anthropic error', anthropicResponse.status, errText);
```

**Impact**: Vercel function logs are visible to anyone with Vercel project access. If `errText` from Anthropic contains API key fragments in error messages (Anthropic sometimes echoes partial metadata in 4xx errors), this could be an information disclosure. Low probability but worth noting.

**Remediation**: Log only the status code, not the full response body: `console.error('Anthropic error', anthropicResponse.status)`. If you need debugging detail, log it only in development environments (`if (process.env.NODE_ENV !== 'production')`).

---

### [SEC-009] INFO: connect-src Allows api.anthropic.com from the Browser

**File**: `vercel.json`, line 29

**Observation**: The CSP allows `connect-src 'self' https://api.anthropic.com`. The Anthropic API is called **server-side** in `chat.js`, not from the browser. This means the CSP grants a browser permission that is never needed.

**Risk**: Low. If an attacker achieves XSS, this would allow them to call Anthropic's API directly from the victim's browser using injected JavaScript (though they would not have the API key from the CSP alone).

**Remediation**: Remove `https://api.anthropic.com` from `connect-src`. The browser only needs to talk to `'self'` (the Vercel function).

---

### [SEC-010] INFO: No Lockout on Password Gate

**File**: `index.html`, lines 2287–2310

**Observation**: The client-side password gate has no attempt lockout or delay. An attacker can brute-force the input field in the browser without any throttling.

**Risk**: Informational given SEC-001 makes the password trivially visible. Fixing SEC-001 (moving to server-side auth) resolves this automatically.

---

## Security Controls Evaluated

| Control | Status | Notes |
|---------|--------|-------|
| API key storage | PASS | Vercel env var, never in client |
| Input validation (chat.js) | PASS | Module whitelist, message depth/length limits |
| Input validation (edit.js) | PASS | Table/field whitelist, value length cap |
| XSS prevention (DOM rendering) | PASS | `escHtml()` used consistently |
| AI reply rendering | PASS | `textContent` used (not innerHTML) for AI responses |
| Message alternation enforcement | PASS | First message must be user |
| HSTS | PASS | 2-year max-age with includeSubDomains |
| X-Frame-Options | PASS | DENY |
| X-Content-Type-Options | PASS | nosniff |
| CORS enforcement (chat.js) | PASS (with caveat) | See SEC-004 |
| CORS enforcement (edit.js) | FAIL | Missing entirely (SEC-002) |
| Client-side auth model | FAIL | Password in source (SEC-001) |
| Rate limiting resilience | PARTIAL | Resets on cold start; IP derivation edge case (SEC-007) |
| CSP strength | PARTIAL | unsafe-inline weakens it (SEC-005); stale connect-src (SEC-009) |
| Persistent session | PARTIAL | No expiry on localStorage token (SEC-006) |
| File write correctness | FAIL | Serverless ephemeral issue + race condition (SEC-003) |

---

## Prioritized Remediation Roadmap

**P0 — Before any wider distribution of the URL**

1. **SEC-001**: Move password to env var, implement `/api/auth` that issues a short-lived signed session token. Remove all hardcoded `'777grind'` strings from source files.
2. **SEC-002**: Add CORS enforcement to `edit.js` matching the pattern in `chat.js`.
3. **SEC-003**: Migrate `edit.js` file write to Vercel KV or D1. At minimum, write to `/tmp` and document the ephemeral limitation.

**P1 — Within one week**

4. **SEC-004**: Remove the Vercel preview regex from `isAllowedOrigin()`.
5. **SEC-005**: Move inline JavaScript to an external `app.js` and remove `'unsafe-inline'` from CSP.
6. **SEC-006**: Replace `localStorage` with `sessionStorage` or add expiry + logout button.

**P2 — Hardening pass**

7. **SEC-007**: Remove `x-forwarded-for` fallback from IP derivation; use only `x-real-ip` in production.
8. **SEC-009**: Remove `https://api.anthropic.com` from browser CSP `connect-src`.

---

## Risk Assessment

**Current risk**: A person who obtains the URL can trivially access the full dashboard by reading the page source. They can also write arbitrary values to all data tables by calling `/api/edit` cross-origin. The AI API key is protected (server-side only) and there is no PII or payment data at risk.

**Post-remediation risk (P0+P1 complete)**: Access requires a valid server-issued session token. The edit endpoint enforces origin and auth. Rate limiting is meaningful. The attack surface reduces to: compromised Anthropic API key (if Vercel env vars are breached), or brute-force of a server-validated password (mitigated by adding lockout in `/api/auth`).

**Residual risk after all items**: Low. Appropriate for a private personal dashboard with no third-party users.

---

*Audit conducted via static analysis only. No requests were sent to any endpoints.*
