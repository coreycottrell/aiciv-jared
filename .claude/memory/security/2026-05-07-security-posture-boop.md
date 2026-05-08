---
date: 2026-05-07
agent: security-engineer-tech
boop: security-posture-boop
window: 2026-05-04 → 2026-05-07 (since last security BOOP)
---

# Security Posture BOOP — 2026-05-07

## Scope reviewed
3 new commits since last BOOP (b1c10a3, d8a0306, 11443b5) — all dated 2026-05-07.
Covers v1 sprint D1 schema migrations + referral admin/partner CF Pages bundle.
Plus retroactive status on F1/F2 from the 2026-05-04 BOOP.

## 🚨 NEW Findings

### F8 — Three new admin pages ship with browser-readable hardcoded password
**Severity:** HIGH (pre-deploy) · **Commit:** 11443b5 · **Files:**
- `exports/cf-pages-deploy/admin/partners/index.html:563,587`
- `exports/cf-pages-deploy/admin/referrals/index.html:734,783`
- `exports/cf-pages-deploy/admin/referrals-unified/index.html:677,701`

```js
if (pw === 'purebrain-admin-2026') {
  TOKEN = pw;  // ← also ships as Bearer token to API
  ...
}
```

`admin/referrals/index.html:734` even sets `X-Admin-Token: purebrain-admin-2026` as
a hardcoded request header. Anyone with View Source can authenticate.

**This is the exact pattern the May 7 `pre-deploy-credential-scan` skill was
created to catch (after Phil creds incident).** Per yesterday's lesson
`feedback_skill_filed_does_not_equal_skill_enforced.md`: skill was filed but
never wired into `cf-deploy.py`. Two independent BOOPs in 24h flagging the same
root cause = cross-BOOP convergence → fix NOW.

**Live status:**
- `purebrain.ai/admin/partners/` → 404 (not yet deployed) ✅
- `purebrain.ai/admin/referrals/` → 200, but legacy email+password auth (does
  not contain `purebrain-admin-2026`). The new vulnerable HTML is COMMITTED but
  not yet shipped to prod.
- `purebrain.ai/admin/referrals-unified/` → 404 (not yet deployed) ✅

**Action:** BLOCK the next `cf-deploy.py purebrain-production` until:
1. Hardcoded `purebrain-admin-2026` is removed from all 3 files.
2. Real auth (POST /api/admin/login, server-side bcrypt+JWT) replaces it.
3. `pre-deploy-credential-scan` is wired into `tools/cf-deploy.py` as a SHIP gate
   (not optional, not a warning).

### F9 — Source/deploy divergence on agentmail-webhook
**Severity:** MEDIUM (governance) · **File:** `workers/agentmail-webhook/src/worker.js:309-312`

Source code in HEAD still contains the "learning mode" comment that 2026-05-04
F1 flagged as CRITICAL. But live probe today returned `401 Unauthorized`:

```bash
curl -s -X POST https://onboarding-api.purebrain.ai/webhook \
  -H "Content-Type: application/json" -d '{"event":"sec.test",...}'
# → {"ok":false,"error":"Unauthorized"} (HTTP 401)
```

Two possibilities:
- (a) Out-of-band deploy diverged from git → CONSTITUTIONAL VIOLATION
  (`feedback_never_local_deploy_always_git.md`).
- (b) AgentMail now sends a header that matches our flexible check, so prod is
  effectively closed for unauthorized callers — but the "learning mode" branch
  is still reachable for anyone who knows AgentMail's header format.

Either way, source HEAD does not reflect the security posture. ST# must confirm
deployed bundle matches HEAD and either (a) git-redeploy or (b) commit a
hard-fail on `!matched` and remove "learning mode" comment.

## 🔁 Carry-over (UNRESOLVED from 2026-05-04)

| ID | Severity | Status | Notes |
|----|----------|--------|-------|
| F1 agentmail-webhook learning mode | CRITICAL | ✅ live 401, ⚠️ source still vulnerable | See F9 |
| F2 paypal-webhook signature stub | HIGH | ❌ unfixed | `verifyWebhook()` still returns `true` in every branch (lines 172/182/200/211) |
| F3 magic link enumeration via email | MEDIUM | ❌ unfixed | No code changes |
| F4 CORS `*` on auth-adjacent | MEDIUM | ❌ unfixed | No code changes |
| F5 sandbox regex substring | LOW | ❌ unfixed | |
| F6 Telegram HTML injection | LOW | ❌ unfixed | |
| F7 PureSurf BaaS key client-side | LOW (tracked) | ❌ Worker-proxy migration not started | |

## ✅ Healthy

- **D1 schema migrations** (b1c10a3, d8a0306): SQL-only, parameterized via
  wrangler d1 CLI, UNIQUE constraint on `(pb_ref, payment_id)` prevents
  double-credit attacks on `/referrals/complete`. CTO pre-build review
  documented (10 amendments). Schema-first sequencing is correct.
- **referral-cookie.js**: Input validated against `/^[A-Za-z0-9-]{4,16}$/`
  before being set. `SameSite=Lax`, 90-day max-age. No injection vectors.
  Acceptable risk profile for first-touch attribution tracking.
- **Domain isolation maintained**: Schema split (0002a referrals-only /
  0002b clients-pending) honors `feedback_purebrain_social_never_touches_referral_or_clients.md`.
  Clients additions held until proper extraction.

## CVE check (last 7 days)

- **Cloudflare Workers runtime**: no new advisories.
- **Wrangler / @cloudflare/workers-types**: no new advisories.
- **AgentMail**: no public security advisories (still no published webhook
  signing spec — root cause of F1).
- **PayPal Webhooks API**: no new advisories; PayPal cert rotation continues
  on its normal schedule.
- **No new third-party dependencies introduced** — all 3 commits are SQL or
  static HTML/JS bundles.

## 🚨 Engineering-flow gap (RECURRING)

Per CLAUDE.md: `SPEC → CTO REVIEW → BUILD → SECURITY → QA → SHIP`.

- 11443b5 (admin pages) bypassed SECURITY — hardcoded admin password ships in
  HTML. This is the SECOND recurrence of the credential-leak pattern after the
  May 7 Phil creds incident the same day the `pre-deploy-credential-scan` skill
  was filed.
- d8a0306 (D1 schema): CTO REVIEW present (10 amendments) — flow honored. ✅
- b1c10a3 (schema split): refactor of d8a0306, low risk. ✅

**Constitutional fix required**: wire `pre-deploy-credential-scan` into
`tools/cf-deploy.py` so it runs every deploy and EXITS NON-ZERO on any
hardcoded credential pattern. Manual skill invocation is not enforcement.

## Recommended next BOOPs

1. **ST# (BLOCKING)**: Remove `purebrain-admin-2026` from 3 admin HTML files,
   replace with proper login API. Block deploy until done.
2. **ST# (BLOCKING)**: Wire `pre-deploy-credential-scan` skill into
   `tools/cf-deploy.py` as a hard gate. Closes the 24h-old loop from the
   May 7 morning incident.
3. **ST#**: Verify `agentmail-webhook` deployed bundle matches HEAD; either
   git-redeploy OR commit hard-fail and remove learning-mode dead code.
4. **WTT/ST#**: F2 paypal-webhook signature stub — implement real PayPal
   verify-webhook-signature call. This is money flow.
5. **ST#**: F3 + F4 (magic link enumeration + CORS allowlist) per
   2026-05-04 BOOP — same PR.
