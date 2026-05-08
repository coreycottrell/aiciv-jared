---
date: 2026-05-04
agent: security-engineer-tech
boop: security-posture-boop
window: 2026-04-29 → 2026-05-04 (last 7 days of commits)
---

# Security Posture BOOP — 2026-05-04

## Scope reviewed
10 commits since 2026-04-29. Two new Cloudflare Workers added to production
(`agentmail-webhook`, `paypal-webhook` — committed together as 1601cf1), plus
one credential rotation (95499ee), one onboarding-spec fix (607437e), one
777-api alias addition (83eccfc), and SEO content. Focus: auth-adjacent and
money-flow paths.

## 🚨 Findings

### F1 — agentmail-webhook ships in "learning mode" with auth disabled
**Severity:** CRITICAL · **Commit:** 1601cf1 · **File:** `workers/agentmail-webhook/src/worker.js:309-312`

```js
// For now, log mismatch but DON'T reject — we need to see real payloads first
if (!matched) {
  console.log('[agentmail-webhook] Webhook secret not matched in any header — proceeding anyway (learning mode)');
}
```

Worker is deployed at `onboarding-api.purebrain.ai/webhook`. Any unauthenticated
POST that mimics the AgentMail payload shape can:
- Forge a "magic link" email from "Witness" (only checks subject + sender substring)
- Trigger `welcome-email-api` to send our branded welcome email to any address
  the attacker chooses, embedding an attacker-controlled `magic_link` URL
- Insert arbitrary rows into D1 `magic_links` table
- Spam Telegram (`chat_id 548906264`)

This is a phishing-amplifier-as-a-service from our own infrastructure.

**Fix:** Hard-fail when `AGENTMAIL_WEBHOOK_SECRET` is set and no header matches.
Log → 401 Unauthorized. Move "learning mode" behind an env flag default-off.

### F2 — paypal-webhook signature verification is a stub
**Severity:** HIGH · **Commit:** 1601cf1 · **File:** `workers/paypal-webhook/src/worker.js:164-183`

`verifyWebhook()` returns `true` in every branch. Missing header → true.
Secret mismatch → true ("Log but don't reject"). No PayPal CERT/transmission
signature check (PayPal docs require `paypal-auth-algo`, `paypal-cert-url`,
`paypal-transmission-sig` validation). Forged events could create fake clients
and drive `total_paid` increments.

**Fix:** Implement PayPal's `notifications/verify-webhook-signature` API call
or fail-closed on missing/mismatched secret.

### F3 — Magic link disclosure by email parameter
**Severity:** MEDIUM · **Commit:** 1601cf1 · **File:** `workers/agentmail-webhook/src/worker.js:545-582`

`GET /api/magic-link/:uuid?email=…` resolves three lookup strategies, including
`LOWER(human_email) = LOWER(?)`. No auth, no rate limit, returns the live
magic link. Anyone who guesses a customer email can enumerate their auth token.

**Fix:** Require the UUID match (drop the email-only fallback), or pair email
with a short-lived poll token issued on the thank-you page.

### F4 — CORS `*` on auth-adjacent endpoints
**Severity:** MEDIUM · **Commit:** 1601cf1 · **File:** `workers/agentmail-webhook/src/worker.js:114, 664`

Every response (including the magic link poll) sets
`Access-Control-Allow-Origin: *`. Any victim's browser on any site can fetch
their magic link if F3 holds.

**Fix:** Restrict to `https://*.purebrain.ai` and the thank-you page origin.

### F5 — Sandbox regex matches substring
**Severity:** LOW · **File:** `workers/agentmail-webhook/src/worker.js:50`

`/example\.com/i` matches anywhere in the email string, not just the domain.
An attacker can craft `attackerexample.com@gmail.com` to redirect a real
welcome email to `jared@puretechnology.nyc` instead of the intended customer,
or vice-versa to bypass sandbox handling.

**Fix:** Anchor with `/@.+example\.com$/i`.

### F6 — Telegram parse_mode: 'HTML' with unsanitized email content
**Severity:** LOW · **File:** `workers/agentmail-webhook/src/worker.js:351-356, 374-378, 518-527`

Email subject/body/sender are interpolated into HTML-parsed Telegram messages.
A crafted email can render arbitrary markup or break the alert pipeline.

**Fix:** Switch to `parse_mode: 'MarkdownV2'` with escaping, or strip `<>&`.

### F7 — PureSurf BaaS key still client-side (acknowledged)
**Severity:** LOW (tracked) · **Commit:** 95499ee

Rotation replaced a dead key with an active one in 3 client-side dashboards.
TODO in commit message: migrate behind a Worker proxy. Not a regression, but
the active key is still extractable from any browser viewing the 777 dashboard.

## ✅ Healthy

- `workers/777-sheets-api` `/api/sheet` alias (83eccfc) inherits the
  `authenticate()` middleware on `/api/*` and the `ALLOWED_SPREADSHEETS`
  whitelist. Clean.
- `/insiders/awakened/` restoration (607437e) realigned the page with
  ONBOARDING-SPEC-DEFINITIVE.md. Constitutional violation closed.
- PayPal double-count fix (1601cf1) is correct logic — INSERT now sets
  `total_paid=0`, only `PAYMENT.SALE.COMPLETED` increments.
- No new third-party dependencies introduced (CF Workers are native JS, no
  npm install). No new CVE exposure surface from this window.

## 🔁 Engineering-flow gap

Per CLAUDE.md: `SPEC → CTO REVIEW → BUILD → SECURITY → QA → SHIP`.
Commit 1601cf1 ships two new internet-facing webhooks to production custom
domains with auth verification explicitly disabled in code comments
("learning mode", "allow through to avoid losing events"). The SECURITY step
appears to have been skipped — this is exactly the gap the constitutional
flow exists to prevent. Recommend retroactive security gate before any
further onboarding-pipeline Worker changes.

## Recommended next BOOPs
1. ST# / WTT — patch F1 + F2 fail-closed before Monday.
2. ST# — patch F3 (drop email fallback) + F4 (CORS allowlist) same PR.
3. ST# — file ticket for PureSurf BaaS Worker-proxy migration (F7) with
   target date.
