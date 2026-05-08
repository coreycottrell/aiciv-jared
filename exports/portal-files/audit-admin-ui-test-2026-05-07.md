# Live UI Test — Admin Referrals Bug Fixes (Commit b98235f)

**Agent**: browser-vision-tester
**Date**: 2026-05-07
**URL**: https://staging.purebrain.ai/admin/referrals/
**Auth**: `pb_admin_token` from .env seeded via localStorage (bypassed login screen)

---

## TOP-LINE FINDING — BLOCKER

**Commit b98235f has NOT been deployed to staging.** Local main is 16 commits ahead of `origin/main`; CF Pages auto-deploys from `origin/main`. The fix is in working tree only.

```
$ git status -sb
## main...origin/main [ahead 16]

$ grep -c "syncSplitRowsFromDOM" exports/cf-pages-deploy/admin/referrals/index.html  → 5  (local)
$ curl -s https://staging.purebrain.ai/admin/referrals/ | grep -c "syncSplitRowsFromDOM"  → 0  (deployed)
$ curl -s https://purebrain.ai/admin/referrals/  | grep -c "syncSplitRowsFromDOM"          → 0  (production)
```

`deployed_fixes.json` (live page source check):
```json
{"syncSplitRowsFromDOM": false, "admin-api failed": false, "PUT fallback": false, "Fallback: loaded": false, "_displayName": false}
```

---

## TEST RESULTS

### Test 1 — Autocomplete CORS fallback: **BLOCKED-AT-INFRASTRUCTURE**
- Token-seed succeeded (login screen bypassed; dashboard rendered).
- Every admin-api call CORS-blocked. Console (file: `console.log`):
  > `Access to fetch at 'https://portal.purebrain.ai/api/admin/affiliates' from origin 'https://staging.purebrain.ai' has been blocked by CORS policy: Request header field authorization is not allowed by Access-Control-Allow-Headers in preflight response.`
- Stats, affiliates, payouts, leaderboard, clients — ALL fail with same CORS error.
- Table empty (0 rows) → cannot click partner row to open detail panel → cannot reach autocomplete field.
- Screenshot: `02-after-affiliates-load.png` shows dashboard with all `--` tiles and empty Recent Activity.
- Bug 1 fix would have run on `/api/admin/clients` — that endpoint is one of the CORS-blocked. The intended fallback (`/api/admin/affiliates`) is **also CORS-blocked**, so even with the fix shipped, fallback would also fail on staging.

### Test 2 — Split row persistence: **BLOCKED** (cannot open partner panel without table data)

### Test 3 — PATCH→PUT fallback chain: **BLOCKED** (cannot reach Save button)

---

## OTHER BUGS SPOTTED

1. **CORS preflight rejects `Authorization` header on portal worker** — affects ALL admin endpoints from any origin ≠ portal.purebrain.ai. Worker `Access-Control-Allow-Headers` does not include `authorization`. This is a worker-side fix, separate from the three bugs in this commit.
2. **Bug 1's fallback uses `/api/admin/affiliates`** — same worker, same CORS policy → fallback would also fail on staging until the worker CORS header is fixed.
3. **Login flow now goes to `portal.purebrain.ai/api/login`** (not the bearer token UI). Worked around with localStorage seed of `pb_admin_token`. Test scripts must use key `pb_admin_token` (not `admin_token`).
4. **No console errors are surfaced to the operator UI** — toasts only fire on `r.ok=false`, but CORS failures throw before that. User sees empty dashboard with no error state.

---

## RECOMMENDATION — **NO. Not ready to promote.**

**Do not promote to production.** Two hard blockers:

1. **The commit is not pushed.** `git push origin main` required before CF Pages will see it. Currently testing pre-fix HTML.
2. **Worker-side CORS fix required.** Even with the JS fix shipped, every admin call from `staging.purebrain.ai` → `portal.purebrain.ai` is preflight-rejected. The Bug 1 fallback path will fail identically until the worker adds `authorization` to `Access-Control-Allow-Headers` (and includes the staging origin).

**Order of operations to unblock testing:**
1. Push `b98235f` to origin/main → CF Pages deploys fixed HTML.
2. ST# fixes worker CORS (`Access-Control-Allow-Headers: authorization, content-type` + allow staging origin) → table populates, modals open.
3. Re-run this test → all three fixes can finally be verified end-to-end.

Alternative: test on production-equivalent origin (purebrain.ai) where CORS is same-origin and works, but that requires the deploy first regardless.

---

## EVIDENCE

- Screenshots: `audit-admin-ui-test-screenshots-2026-05-07/01-initial-load.png` (login screen), `02-after-affiliates-load.png` (dashboard, all empty), `09-final-state.png`
- Console log: `audit-admin-ui-test-screenshots-2026-05-07/console.log`
- Network log: `audit-admin-ui-test-screenshots-2026-05-07/network.json` (empty — all blocked at preflight)
- Deployed-fix marker check: `audit-admin-ui-test-screenshots-2026-05-07/deployed_fixes.json`
- Test script: `/tmp/test_admin_referrals.py`

## Memory Written
Path: `.claude/memory/agent-learnings/browser-vision-tester/2026-05-07--admin-referrals-cors-deploy-blocker.md`
Type: gotcha + technique
Topic: Always verify deployment freshness AND worker CORS before declaring UI bugs fixed; localStorage key for admin panel auth is `pb_admin_token` not `admin_token`.
