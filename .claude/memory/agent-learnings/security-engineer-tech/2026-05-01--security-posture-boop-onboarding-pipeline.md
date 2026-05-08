# Security Posture BOOP — 2026-05-01

**Window**: Last 48h commits
**Reviewer**: security-engineer-tech (BOOP)

## Commits in scope

| Hash | Title | Risk |
|------|-------|------|
| `83eccfc` | fix(777-api): bind to TOS Dashboard sheet + add /api/sheet alias | 🟡 inherits MEDIUM auth bypass (pre-existing) |
| `08eb247` | seo: og:image on 21 comparison pages | 🟢 cosmetic |
| `95499ee` | fix(security): rotate dead PureSurf BaaS key | 🟡 stop-gap, root cause unfixed |
| `1601cf1` | feat: agentmail-webhook + paypal-webhook fixes | 🔴 NEW critical findings |

None of these passed through SECURITY → QA before merge per recent dept logs. Engineering flow (BUILD → SECURITY → QA → SHIP) was bypassed for the Apr 30 webhook worker — flagged.

## 🔴 CRITICAL findings (NEW code — `1601cf1`)

### C1. agentmail-webhook accepts unsigned webhooks ("learning mode")
**File**: `workers/agentmail-webhook/src/worker.js:294-313`
**Live URL**: `https://onboarding-api.purebrain.ai/webhook` (DEPLOYED, 2 magic links stored)
**Verified exploitable**: `curl -X POST -d '{"event":"test","data":{}}'` → HTTP 200, Telegram notif fired to Jared.

The secret check logs mismatches but proceeds anyway (line 311). Attacker can:
- POST forged Witness magic-link emails → arbitrary URLs flow through to `welcome-email-api` → land in legit customer inboxes branded as "your magic link". Domain rewrite only fires on `.ai-civ.com`; any other host passes through unmodified. **Customer phishing vector.**
- Spam Jared's Telegram (`TELEGRAM_CHAT_ID = 548906264`) with arbitrary text, hidden in HTML parse_mode.
- Insert arbitrary rows into `magic_links` D1 table; UPDATE `clients` rows by email (set ai_name, magic_link to attacker values).

**Fix**: Move secret check from "log" to "reject 401" before hitting D1. Use constant-time comparison (`crypto.subtle.timingSafeEqual` on equal-length buffers) — current code uses `.includes()` (line 304).

### C2. paypal-webhook has no real signature verification
**File**: `workers/paypal-webhook/src/worker.js:164-183`
**Verified**: header presence is the only check; comment line 178 explicitly says mismatched secret is "Log but don't reject".

PayPal's real verification needs `PAYPAL-AUTH-ALGO + PAYPAL-CERT-URL + PAYPAL-TRANSMISSION-ID + PAYPAL-TRANSMISSION-SIG + PAYPAL-TRANSMISSION-TIME` against PayPal's public cert OR a call to `/v1/notifications/verify-webhook-signature`. Neither is present.

Forged events allow:
- `BILLING.SUBSCRIPTION.ACTIVATED` → INSERT into `clients` with attacker email + tier "Awakened" / "Unified" → grants paid-tier access without payment.
- `PAYMENT.SALE.COMPLETED` → increments `total_paid` for any subscription_id → corrupts revenue records & analytics.
- Cancel/suspend/reactivate any client by guessing/scraping subscription IDs.

**Financial fraud + access fraud vector. Highest priority.**

**Fix**: Implement PayPal's verify-webhook-signature API call (cheap + correct), or import their cert and verify locally. Reject on failure with 401.

## 🟡 MEDIUM findings

### M1. 777-sheets-api auth bypassable via spoofed Origin
**File**: `workers/777-sheets-api/src/worker.js:198-211`
**Affected by**: `83eccfc` widened scope to TOS Dashboard + Team Whitelist + Personal OS Planner.

`authenticate()` returns true if `Origin === ALLOWED_ORIGIN` OR `origin.includes('localhost')` OR `origin.includes('127.0.0.1')`. CORS does not authenticate non-browser requests; `curl -H "Origin: https://localhost.attacker.com" ...` passes the check. The `localhost.evilsite.com` substring also matches.

**Impact**: Read/write to TOS Dashboard (Morning Pulse, Handshake Queue), Team Whitelist (auto-respond control), Personal OS Planner. Whitelist tampering enables team-comms abuse (force responses to attacker emails).

**Fix**: Require `X-API-Key` for ALL `/api/*` (drop the Origin/localhost fallbacks). Tighten `localhost` regex to `^https?://(localhost|127\.0\.0\.1)(:\d+)?$`.

### M2. Magic-link polling by email is unauthenticated harvest endpoint
**File**: `workers/agentmail-webhook/src/worker.js:545-582`

`GET /api/magic-link/:uuid?email=victim@example.com` returns the magic link if email matches in D1 (lines 567-571). Magic link IS the auth credential for the customer's container. CORS is `*` (line 114) so any malicious page in a customer's browser can fetch it.

**Impact**: If attacker knows a customer's email, account takeover.

**Fix**: Require either matching UUID (server-generated) OR a one-time signed token in the polling URL. Drop the email-fallback lookup entirely, OR rate-limit + require a per-session nonce.

### M3. Admin token bypass mutates env
**File**: `workers/agentmail-webhook/src/worker.js:615-620`

`handleProcessEmail` mutates `env.AGENTMAIL_WEBHOOK_SECRET = null` then restores. Workers isolate env per-invocation but this is a code smell — race-prone if any await unwinds before restore. Refactor `handleWebhook` to take `{ skipSecretCheck: true }` parameter instead.

### M4. PureSurf BaaS key rotation is a stop-gap, not a fix
**File**: `index.html`, `exports/cf-pages-deploy/777-command-center/index.html`, `exports/cf-pages-deploy/social.html` (per `95499ee`)

New active key `YCCs6vt...F6nuU` is hardcoded in client-side JS. Anyone who views source has it. Commit message acknowledges TODO to migrate behind worker proxy. Until then, the key is the next rotation event waiting to happen.

**Fix**: Track ST# ticket for `777-command-center` calendar widget worker proxy (same pattern as `workers/social-api/`). Set 14-day deadline.

## CVE check (deps)

- `path-to-regexp` 6.3.0 (admin-api) — patched (CVE-2024-45296 fixed in 6.3.0+). ✅
- No new external deps added in last 48h. Workers use Web Crypto + fetch only.

## Process flag

The agentmail-webhook + paypal-webhook landed Apr 30 in a single commit (`1601cf1`, 1187 LOC) without dept-routed SECURITY review. Both are payment-adjacent and customer-facing. This violates the engineering flow (BUILD → SECURITY → QA → SHIP). Recommend ST# routing for hardening before any further onboarding-pipeline changes.

## Recommended ST# routing (priority order)

1. 🔴 paypal-webhook real signature verification (financial fraud blocker)
2. 🔴 agentmail-webhook reject on missing/bad secret + constant-time compare
3. 🟡 magic-link polling: drop email-fallback or add nonce
4. 🟡 777-sheets-api: drop Origin/localhost fallbacks, require X-API-Key for /api/*
5. 🟡 PureSurf BaaS key worker-proxy migration
