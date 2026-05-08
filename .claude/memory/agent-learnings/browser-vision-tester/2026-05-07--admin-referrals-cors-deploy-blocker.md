# Admin Referrals — CORS + Deploy Blocker (2026-05-07)

**Agent**: browser-vision-tester
**Type**: gotcha + technique
**Topic**: Live UI test of commit b98235f three bug fixes — both blocked at infrastructure layer

## Context

Jared asked for live cross-validation of three bug fixes shipped in commit b98235f:
1. Autocomplete CORS fallback (`/api/admin/clients` → fallback `/api/admin/affiliates`)
2. Split row persistence (`syncSplitRowsFromDOM()` before re-render)
3. Save fallback chain (PATCH → PUT /splits → PUT /partners/:id)

Target: https://staging.purebrain.ai/admin/referrals/

## Discovery

**Both blockers found before any UI test could meaningfully execute:**

### Blocker 1 — Commit not pushed to origin
- Local git: `main...origin/main [ahead 16]`
- CF Pages auto-deploys from `origin/main` only
- Local HTML has 5 hits for `syncSplitRowsFromDOM`; deployed HTML has 0
- Production (`purebrain.ai`) also has 0 — same root cause
- **Always verify deployment freshness via curl + grep for fix-specific markers BEFORE running UI tests.** A 30-second sanity check saves a 30-minute browser run.

### Blocker 2 — Worker CORS rejects `Authorization` header on preflight
- Console shows: `Access-Control-Allow-Headers preflight does not allow 'authorization'` for every admin-api call from staging origin
- Even after Bug 1 fix ships, fallback target (`/api/admin/affiliates`) lives on the same worker → fallback ALSO CORS-blocks
- Bug 1 fix is JS-side; the underlying CORS issue is worker-side and was not addressed in b98235f

## Techniques learned

1. **localStorage auth seed for admin panels**: The referrals admin panel uses `pb_admin_token` (NOT `admin_token`). When testing, pre-seed via `page.add_init_script("window.localStorage.setItem('pb_admin_token', '<token>');")` to skip the login screen.

2. **Bearer token in `.env`**: `ADMIN_TOKEN=vdi4cpqYCknfa6U6mTLDQ1Tw0I5gi0CYJjM3uw2C2-s` works against `portal.purebrain.ai/api/admin/*` directly via `Authorization: Bearer <token>`. No /api/login round-trip needed.

3. **Pre-test diff verification pattern** (REUSE THIS):
   ```bash
   # Before running browser test, confirm fix is actually deployed:
   curl -s "https://staging.purebrain.ai/admin/referrals/" | grep -cE "marker1|marker2|marker3"
   ```
   If 0, the test is meaningless — fail fast and report deploy state.

4. **Login-flow drift**: The admin panel previously used a token-prompt UI; it now requires email/password against `/api/login`. Manifest/test scripts referencing the old flow will silently fail.

## When to apply

- Any "verify shipped fix on staging" task → ALWAYS curl + grep markers first
- Any admin panel test → check localStorage key (varies: `admin_token`, `pb_admin_token`, `auth`, etc.)
- Any cross-origin admin UI → verify worker CORS allows `Authorization` and the calling origin BEFORE blaming UI code

## Files

- Test script: `/tmp/test_admin_referrals.py` (Playwright headless)
- Deliverable: `exports/portal-files/audit-admin-ui-test-2026-05-07.md`
- Screenshots: `exports/portal-files/audit-admin-ui-test-screenshots-2026-05-07/`
- Test target: `exports/cf-pages-deploy/admin/referrals/index.html` (working tree, line 1329-1875 area)

## Recommendation captured

Promote-to-production: **NO**. Two hard blockers (push + worker CORS) must clear before any of the three fixes can be verified end-to-end.
