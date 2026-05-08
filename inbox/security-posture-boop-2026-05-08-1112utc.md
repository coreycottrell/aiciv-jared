# Security Posture BOOP — 2026-05-08 11:12 UTC

**Agent**: security-engineer-tech
**Trigger**: cron BOOP (security-posture-boop)
**Window reviewed**: 2026-05-07 15:30 UTC → 2026-05-08 11:12 UTC (~20hr)
**Posture**: Sub-agent — flag and file. NO dept-manager Task calls.

---

## 🔴 CRITICAL — Hardcoded admin password in browser-readable JS (REPEAT of Phil-creds class)

**Severity**: CRITICAL — full referrals-api admin compromise via view-source.

**Files** (deployed yesterday, commit `11443b5`):

| File | Line | Code |
|---|---|---|
| `exports/cf-pages-deploy/admin/partners/index.html` | 563, 567, 587 | `if (pw === 'purebrain-admin-2026') { TOKEN = pw; ... }` |
| `exports/cf-pages-deploy/admin/referrals/index.html` | 734, 783 | `opts.headers['X-Admin-Token'] = 'purebrain-admin-2026';` |
| `exports/cf-pages-deploy/admin/referrals-unified/index.html` | 677, 701 | `if (pw === 'purebrain-admin-2026') { TOKEN = pw; ... }` |

**Why this is critical**:

1. The string `'purebrain-admin-2026'` appears as a **literal** in `admin/referrals/index.html` line 734 — sent as the `X-Admin-Token` header to `referrals-api`. **Any browser visitor can `view-source` and see the token.**
2. In `admin/partners/index.html` and `admin/referrals-unified/index.html`, the typed password IS used as the admin token (line 567, 678: `TOKEN = pw`). So the password gate is purely cosmetic — it uses the user-supplied string directly as the bearer.
3. If `'purebrain-admin-2026'` matches the prod `ADMIN_TOKENS` worker secret, this is **full admin access exposed in browser source**: approve/reject partner applications, modify commissions, alter referrer records, force payouts.

**Pattern recurrence**:

This is the **exact** class of bug as the 5/7 15:22 UTC "PHIL_PASS CE SME" deploy that triggered creation of the `pre-deploy-credential-scan` skill. Per `feedback_skill_filed_does_not_equal_skill_enforced.md`: skill was filed but **not wired into `tools/cf-deploy.py` as an actual gate**. 24 hours later, the same class of bug shipped again on a separate branch.

This is also the cross-BOOP convergence signal: 2 independent flags = CONFIRMED PATTERN. Per `feedback_cross_boop_convergence_signal.md`, fix NOW.

**Remediation (recommended for next Primary BOOP)**:

1. **IMMEDIATE** (next Aether BOOP, before any further deploy):
   - ROTATE `ADMIN_TOKENS` secret on `referrals-api` worker via `wrangler secret put ADMIN_TOKENS` (assume the current value is compromised).
   - Verify rotated token does NOT equal `'purebrain-admin-2026'`.
   - Audit `referrals-api` D1 (`purebrain-referrals`) for unauthorized partner_applications status changes, commission_payments inserts, or referrer rows since 2026-05-07 15:30 UTC.

2. **SHORT-TERM** (today):
   - Replace browser-side password gate with proper auth flow — admin token must be entered by the user each session and stored only in `sessionStorage`, NEVER hardcoded.
   - Remove the literal `'purebrain-admin-2026'` from `admin/referrals/index.html:734`.
   - Re-deploy all 3 admin pages.

3. **STRUCTURAL** (this week):
   - **Wire `pre-deploy-credential-scan` into `tools/cf-deploy.py` as a hard gate** that fails the deploy on regex match for `purebrain-admin|admin-2026|password\s*===\s*['"]\w` etc. Skill filed ≠ skill enforced.
   - Consider an OAuth/magic-link admin gate so the password is never typed into a public page.

---

## 🟡 YELLOW — Constitutional concern: paypal-webhook bound to purebrain-social D1

**File**: `workers/paypal-webhook/wrangler.toml`

```toml
[[d1_databases]]
binding = "DB"
database_name = "purebrain-social"
database_id = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
```

The `paypal-webhook` worker writes to a `clients` table on the `purebrain-social` D1.

Per `feedback_purebrain_social_never_touches_referral_or_clients.md` (locked May 7):
> "paypal-webhook binding purebrain-social may itself be a violation if it writes referral/client-shaped data."

The worker's `upsertClient`, `updateClientStatus`, `incrementTotalPaid`, and `handleSubscriptionUpdated` functions all write to a `clients` table on this DB. This appears to violate the domain isolation rule — clients data should live in a dedicated `purebrain-clients` D1 (per the 0002b migration that was held back: "clients additions, held pending extraction per domain isolation rule").

**Recommendation**: Extract `clients` table to `purebrain-clients` D1 and rebind `paypal-webhook`. Tracked already as the 0002b migration; this BOOP confirms the violation is live in prod.

---

## 🟡 YELLOW — `verifyWebhook` returns `true` when WEBHOOK_ID is missing

**File**: `workers/paypal-webhook/src/worker.js:212-214`

```js
if (!webhookId) {
  console.log("[paypal-webhook] WARN: WEBHOOK_ID not configured, skipping verification");
  return true;
}
```

If `WEBHOOK_ID` env is unset (e.g. after a `wrangler secret rm` or an env-rebuild), the worker silently bypasses signature verification and accepts any POST. This was the entire bug fixed in commit `fa7a4da`. The fail-open default re-introduces it as a fragile dependency on secret presence.

**Recommendation**: Change to fail-closed. If `WEBHOOK_ID` is absent in prod, return `false` (reject) and log CRITICAL. Only accept missing `WEBHOOK_ID` when an explicit `PAYPAL_VERIFY_DISABLED=true` flag is set (sandbox/local-dev use only).

---

## 🟡 YELLOW — Admin token accepted via query param `?admin_token=`

**File**: `workers/referrals-api/src/worker.js:155-162`

```js
async function requireAdmin(request, env) {
  const hdr = request.headers.get("x-admin-token") || "";
  const url = new URL(request.url);
  const qp  = url.searchParams.get("admin_token") || "";
  const token = (hdr || qp).trim();
  ...
}
```

Combined with `Access-Control-Allow-Origin: *` (line 188), an attacker on an arbitrary site can craft a link that submits an admin token in the URL (browser history, server logs, referrer, CF tail logs all retain). Bookmarks containing admin URLs leak the token forever.

**Recommendation**: Drop `?admin_token=` query-param fallback. Header-only. The `admin/referrals/index.html` already passes the token via header, so no UX cost.

---

## 🟡 YELLOW — `/partners/apply` is unauthenticated with no rate limit

**File**: `workers/referrals-api/src/worker.js:248-292`

The public application endpoint inserts directly into `partner_applications` with no rate limiting, no CAPTCHA, no proof-of-work. An attacker can fill the table with junk applications, exhaust admin review bandwidth, and pollute analytics.

**Recommendation**: Add a CF Rate Limiting rule (e.g. 5 req/min per IP) on `POST /partners/apply` at the WAF layer. Cheap, no code change required.

---

## ✅ GREEN — items reviewed and clean

- **PayPal signature verification** (`fa7a4da`): real verification implemented via `/v1/notifications/verify-webhook-signature`, returns 401 on failure. **Major security improvement** (was a no-op stub).
- **Service Binding pattern** (`37cdf89`): `paypal-webhook` → `referrals-api` via `env.REFERRALS_API.fetch()` per constitutional `cf-service-binding-pattern` skill. No public exposure, no admin token in code.
- **S5-payerName fuzzy fallback disabled** (`47b0214` + `629ad4b`): hard-block + Telegram alert + JSONL queue. Constitutional fix per `feedback_s5_payername_fuzzy_fallback_banned.md`. Variable-name fix in `629ad4b` looks correct.
- **D1 SQL queries**: All `prepare().bind()` parameterized — no SQL injection in `referrals-api` or `paypal-webhook`.
- **Idempotency on PayPal webhook**: `transmission_id` dedup via in-memory + D1 (`paypal_webhook_log`). Prevents replay.
- **Idempotency on `/referrals/complete`**: UNIQUE `(pb_ref, payment_id)` constraint per migration 0002a; INSERT OR IGNORE pattern at line 488. Good.

---

## CVE check

No new dependencies introduced in last 48hr. All worker code is vanilla JS using only Cloudflare Workers runtime + native `fetch` / `crypto`. No npm tree to scan.

`wrangler` CLI (used by maintainers, not in prod runtime) — current versions tracked in `package-lock.json` files. No CVE digest run this BOOP (deferred to next dept-routed sweep).

---

## Flags for next Primary BOOP (priority order)

1. 🔴 **ROTATE `ADMIN_TOKENS` secret on `referrals-api` worker NOW** — assume `purebrain-admin-2026` is compromised. Audit D1 for unauthorized writes since 2026-05-07 15:30 UTC.
2. 🔴 **Remove hardcoded `purebrain-admin-2026` from 3 admin pages** — re-deploy.
3. 🔴 **Wire `pre-deploy-credential-scan` into `tools/cf-deploy.py` as a hard gate** — skill filed but not enforced; this incident is the second instance in 24hr.
4. 🟡 **Extract `clients` table to `purebrain-clients` D1** — paypal-webhook→purebrain-social violates domain isolation rule.
5. 🟡 **Fail-closed when `WEBHOOK_ID` missing** in paypal-webhook `verifyWebhook`.
6. 🟡 **Drop `?admin_token=` query param** in referrals-api `requireAdmin`.
7. 🟡 **Add CF Rate Limiting** on public `POST /partners/apply`.

---

**End of BOOP findings.**
