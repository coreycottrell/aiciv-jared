# Referral Dashboard vs Admin Affiliates — DB Split Confirmed — 2026-04-14

Type: operational
Topic: /api/referral/dashboard (D1) vs /api/admin/affiliates (VPS SQLite)

## Confirmed Diagnosis

- `app.purebrain.ai/api/referral/dashboard`
  - Served by CF Pages Functions: `exports/cf-pages-deploy/functions/api/referral/dashboard.js`
  - D1 binding: `REFERRAL_DB`
  - Joins `referrals LEFT JOIN commission_payments` for earnings
  - 401 without code+auth; returns 401 JSON `{"error":"authentication required..."}`

- `portal.purebrain.ai/api/admin/affiliates`
  - NOT present in CF Pages functions tree (grep -r admin/affiliates in exports → 0 hits)
  - Served by VPS portal server (container) against local SQLite
  - 401 without admin_token; returns `{"error":"unauthorized"}`

## Why Data Differs

Two separate databases that have drifted since CF migration (2026-04-06 referral-system-cf-pages-migration).
Admin view pulls legacy VPS rows. Public `/refer/` dashboard pulls D1 rows. Signup flow
may be writing only to one side.

## Why I Did NOT Auto-Repoint

- Constitutional: `feedback_never_deploy_to_container.md` — do not move public reads onto the VPS
- Constitutional: DB writes require Jared approval
- Unilateral repoint would break D1 signup writes that are now the system-of-record since Apr 6
- Correct fix is DB reconciliation + a decision on source-of-truth, not an endpoint swap

## Next Steps for Aether

1. Decide SoT: D1 is the post-migration canonical store → reconcile legacy VPS rows INTO D1
2. Rebuild `/api/admin/affiliates` as a CF Pages function reading from the same D1 `REFERRAL_DB`
3. Deprecate VPS portal-server affiliates endpoint once admin UI points to new route
4. Separate audit: `referred_name` corruption (`paypal_*@pending`) + `status=completed AND earnings=0` rows
