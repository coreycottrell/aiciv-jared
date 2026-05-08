# Security Posture BOOP — 2026-05-02

## Summary
Reviewed last 5 commits (2026-04-30 → 2026-05-02). Found 2 P1 issues + 2 P2.

## P1: BaaS key rotation REVERTED in working tree (uncommitted)
**File**: `exports/cf-pages-deploy/777-command-center/index.html` line 7023
**Diff vs HEAD**: `-YCCs6vt... +WtHJY1zr...` (active key REPLACED with rotated/dead key)
**Background**: 95499ee (2026-04-30) rotated this exact key. Working-tree change reverses fix.
**Impact**: If deployed to 777.purebrain.ai, calendar widget breaks AND security commit work is undone.
**Action**: ST# — investigate where the bad key was reintroduced (likely copy-paste from .bak file). Re-apply rotation before any deploy.

## P1: agentmail-webhook deployed with auth disabled ("learning mode")
**File**: `workers/agentmail-webhook/src/worker.js` lines 292-313 (introduced 1601cf1, 2026-04-30)
**Issue**: Webhook secret check logs mismatch but ALWAYS proceeds. Comment: "TODO: tighten once we confirm AgentMail's exact header format".
**Exploitation (no auth required)**:
- POST forged "MAGIC LINK from Witness" → fires welcome emails to attacker-controlled addresses (phishing vector via our own Brevo)
- Pollutes D1 `magic_links` + `clients` (overwrites ai_name/magic_link for any email)
- Sends arbitrary HTML Telegram messages to Jared (chat_id 548906264)
- Costs: Brevo email sends, D1 writes
**Action**: ST# — close auth gap NOW. Either reject on missing/mismatched secret, or add HMAC signature verification per AgentMail docs.

## P1: agentmail-webhook /api/magic-link/:uuid email enumeration
**File**: `workers/agentmail-webhook/src/worker.js` lines 545-582
**Issue**: `GET /api/magic-link/:uuid?email=victim@example.com` falls through to `WHERE LOWER(human_email) = LOWER(?)` (Try 3, line 567-571). Combined with `Access-Control-Allow-Origin: *`, ANY website can retrieve any customer's magic link by knowing their email.
**Impact**: Magic links = container/portal access. This is account takeover.
**Action**: ST# — bind polling to a server-issued one-time pickup token (set at PayPal webhook time, returned to thank-you page only), not freely-queryable email lookup.

## P2: agentmail-webhook env mutation creates concurrency race
**File**: `workers/agentmail-webhook/src/worker.js` lines 616-619
**Issue**: `handleProcessEmail` does `env.AGENTMAIL_WEBHOOK_SECRET = null; await handleWebhook(...); env.AGENTMAIL_WEBHOOK_SECRET = originalSecret;`. In Cloudflare Workers, `env` is per-isolate — concurrent webhook calls during admin call window inherit `null` secret and bypass auth.
**Action**: Pass an explicit `bypassSecret` flag through handleWebhook signature instead of mutating shared env. (Moot once P1 #2 is fixed since auth is currently a no-op anyway.)

## P2: paypal-webhook signature verification stubbed
**File**: `workers/paypal-webhook/src/worker.js` lines 164-183 (introduced 1601cf1)
**Issue**: `verifyWebhook` only checks header presence. `WEBHOOK_SECRET` mismatch is logged but not rejected. No PayPal cert/HMAC signature verification.
**Impact**: Forged `BILLING.SUBSCRIPTION.ACTIVATED` events can inject fake clients into D1; forged `PAYMENT.SALE.COMPLETED` can inflate `total_paid` (which feeds revenue dashboards). Mitigated somewhat by transmission-id idempotency + production-only webhook URL knowledge, but not by cryptography.
**Action**: ST# — implement PayPal v1/notifications/verify-webhook-signature server-side call (or local cert verification). Not urgent if URL is unguessable, but should ship before public attestation of revenue numbers.

## Process gaps observed
1. The 95499ee commit verification claim ("1 occurrence of active key per file") was satisfied at commit time but wasn't repeated post-merge — file picked up uncommitted changes that reintroduced dead key. **Add a CI grep for known-rotated keys.**
2. Workers shipped with TODO comments for security ("learning mode", "log but don't reject") suggest the BUILD→SECURITY→QA→SHIP flow was abbreviated. Recommend OP# verify each new worker passed the SECURITY gate before being marked SHIPPED.

## CVE check
No actively-exploited CVEs flagged for this stack since last BOOP. Cloudflare Workers runtime + D1 + Brevo SDK + Google Sheets API — no advisories on dependency manifests reviewed.
