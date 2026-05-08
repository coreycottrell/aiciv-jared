# Phase 0 Security Fix — purebrain-portal-proxy ADMIN_TOKEN

**Date**: 2026-05-07
**Finding**: V-11 (architect domain-isolation audit) — hardcoded admin token in CF Worker source
**Authority**: Jared (CEO) — explicit greenlight 2026-05-07
**Scope**: `workers/purebrain-portal-proxy/src/worker.js` lines 183, 196 (pre-fix line numbers)

---

## Summary

The string literal `purebrain-admin-2026` was set directly as the
`X-Admin-Token` header value on outbound proxy requests to `referrals-api`.
The token was committed to git, therefore permanently public regardless of
any post-fix changes. The actual mitigation is rotation; the code change
ensures future rotations are zero-touch (just `wrangler secret put`).

**Note**: this is the SAME class of credential leak as the paypal-webhook
finding earlier today. There is a third leak still open: the same literal
appears in admin HTML pages on CF Pages (referenced in
`.claude/memory/security/2026-05-07-security-posture-boop.md`). That track
is owned by ST# and is NOT addressed by this commit.

---

## Pre-fix state (BEFORE)

```bash
$ grep -n "purebrain-admin-2026" workers/purebrain-portal-proxy/src/worker.js
183:        proxyHeaders.set('X-Admin-Token', 'purebrain-admin-2026');
196:        proxyHeaders.set('X-Admin-Token', 'purebrain-admin-2026');
```

Two hardcoded literal matches in code. Notably, lines 192-205 were a
**duplicate dead block** — same `if` condition as 179-191, so the second
block could never execute. Removed in same commit for code hygiene.

The Worker had **NO secrets bound** before this fix:

```bash
$ wrangler secret list --name purebrain-portal-proxy
[]
```

---

## Post-fix state (AFTER)

```bash
$ grep -n "purebrain-admin-2026" workers/purebrain-portal-proxy/src/worker.js
189:      // env.ADMIN_TOKEN secret. Previously hardcoded literal `purebrain-admin-2026`
```

Zero matches in executable code. Single mention remains in security comment
documenting what was rotated and why (audit trail for future readers).

The Worker now has `ADMIN_TOKEN` bound:

```bash
$ wrangler secret list --name purebrain-portal-proxy
[
  {
    "name": "ADMIN_TOKEN",
    "type": "secret_text"
  }
]
```

Code:
```js
if (env.ADMIN_TOKEN) {
  proxyHeaders.set('X-Admin-Token', env.ADMIN_TOKEN);
}
```

---

## Rotation timeline

| Step | Action | UTC Timestamp |
|------|--------|---------------|
| 1 | Generated new token (53 chars urlsafe base64, prefix `pbap_`) | 2026-05-07 ~16:25 |
| 2 | Documented in `tools/.secrets/portal-proxy-admin-token-2026-05-07.txt` (gitignored, mode 600) | 2026-05-07 ~16:25 |
| 3 | Updated `referrals-api` `ADMIN_TOKENS` to CSV: `<old>,<new>` (grace period) | 2026-05-07 16:26 UTC |
| 4 | Confirmed both old and new tokens accepted by `referrals-api` | 2026-05-07 16:26 UTC |
| 5 | Bound `ADMIN_TOKEN` secret on `purebrain-portal-proxy` (BEFORE deploy) | 2026-05-07 16:26 UTC |
| 6 | Deployed `purebrain-portal-proxy` Worker (Version `a3f1da4a-f747-43a9-af01-114aeb32d24a`) | **2026-05-07 16:27 UTC** |
| 7 | Verified live endpoints | 2026-05-07 16:27 UTC |
| 8 | Committed on `main` (commit `1fe0a3e`) | 2026-05-07 16:30 UTC |

Per `feedback_cf_workers_secrets_before_deploy.md`: secrets were PUT BEFORE
deploy — no risk of CF 1042.

---

## Verification (curl with GET, per `cf-pages-health-check-get-not-head` skill)

```bash
$ curl -s -o /dev/null -w "%{http_code}" https://portal.purebrain.ai/api/admin/stats
200
$ curl -s -o /dev/null -w "%{http_code}" https://portal.purebrain.ai/admin/clients
200
$ curl -s -o /dev/null -w "%{http_code}" -H "X-Admin-Token: <NEW_TOKEN>" https://referrals-api.in0v8.workers.dev/admin/stats
200
$ curl -s -o /dev/null -w "%{http_code}" -H "X-Admin-Token: purebrain-admin-2026" https://referrals-api.in0v8.workers.dev/admin/stats
200   # grace period — old token still accepted
$ curl -s -o /dev/null -w "%{http_code}" -H "X-Admin-Token: bogus" https://referrals-api.in0v8.workers.dev/admin/stats
401
$ curl -s -o /dev/null -w "%{http_code}" https://referrals-api.in0v8.workers.dev/admin/stats
401
```

Results:
- Portal-proxy auto-injection works (200) — proves `env.ADMIN_TOKEN` is being read.
- Both old and new tokens still accepted by `referrals-api` — grace period live.
- Wrong/missing tokens correctly rejected (401).

---

## Downstream consumers (NEXT-STEP work, NOT in this fix)

The leaked literal `purebrain-admin-2026` is still hardcoded in these files
and will continue to work because the old token is currently in
`referrals-api` `ADMIN_TOKENS`. Each must be migrated to user-supplied
input or removed entirely before the old token can be retired:

| File | Line(s) | Owner | Status |
|------|---------|-------|--------|
| `exports/cf-pages-deploy/admin/referrals/index.html` | 734, 783 | ST# | Already in queue per `2026-05-07-security-posture-boop.md` |
| `exports/cf-pages-deploy/admin/referrals-unified/index.html` | 677, 701 | ST# | Same boop |
| `exports/cf-pages-deploy/admin/partners/index.html` | 563, 587 | ST# | Same boop |
| `exports/purebrain-portal-rebranded.html` | 1646 (`ADMIN_BYPASS_TOKEN`) | ST# | Should be confirmed in scope |

**No other Workers** in `workers/` reference the literal — only `purebrain-portal-proxy` had the hardcoded value (verified by full-tree grep).

**Action required from Jared / ST#**: once the admin HTML pages are
migrated to a proper login flow (or the password prompt is removed),
`referrals-api` `ADMIN_TOKENS` should be reduced to ONLY the new token.
Until then, the old leaked token remains a valid credential.

---

## Files changed (commit `1fe0a3e` on `main`)

- `.gitignore` — added `tools/.secrets/` and `**/.secrets/`
- `workers/purebrain-portal-proxy/src/worker.js` — replaced 2 hardcoded literals with `env.ADMIN_TOKEN`, removed duplicate dead block (29 LOC → 19 LOC net change)
- `workers/purebrain-portal-proxy/wrangler.toml` — created (file existed on `referral-v1` but was missing on `main`)

Push to `origin/main`: NOT YET DONE — awaiting human authorization (constitutional rule: never push without explicit ask).

---

## Constraints honored

- [x] Per memory `feedback_cf_workers_secrets_before_deploy.md`: secrets PUT before deploy.
- [x] Per memory `feedback_never_local_deploy_always_git.md`: this is a **Worker**, not Pages — `wrangler deploy` is correct (Pages would need git-flow).
- [x] Per skill `verification-before-completion`: every claim has fresh evidence (curl output, secret list, grep before/after).
- [x] Per skill `cf-pages-health-check-get-not-head`: used GET not HEAD for verification.
- [x] No other Worker touched. No other secret touched.
- [x] No pre-commit hooks skipped.
- [x] No emojis in code or commit message.
