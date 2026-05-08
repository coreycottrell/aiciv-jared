# Referral Dashboard vs Admin — Same Backend, Different Query

Type: operational
Date: 2026-04-14

## TL;DR
`/api/referral/dashboard` and `/api/admin/affiliates` both live in `/home/jared/purebrain_portal/portal_server.py`, both call `_referral_db()` (SQLite). The CF Pages D1 migration (`exports/cf-pages-deploy/functions/api/referral/dashboard.js` + `d1-migrations/0001-referral-schema.sql`) is prepared but NOT live. `app.purebrain.ai` still routes to the Python server.

## Functions
- `api_referral_dashboard` — line 4036
- `api_admin_affiliates` — line 5128

## Bug 1: paypal token in name field on /refer/ dashboard
Dashboard history query has filter:
```
AND NOT (r.status = 'rejected' AND r.referred_email LIKE 'paypal_%@pending')
```
This ONLY hides placeholders when status=rejected. When a paypal placeholder row gets flipped to `completed`/`converted`, it leaks through with `referred_name='paypal_xxx@pending'`. Admin has no filter at all (shows everything).

## Bug 2: $0 earnings on Converted rows
Dashboard history earnings → JOIN `commission_payments` (per-referral). Admin top-line earnings → SUM `rewards.reward_value` (different table). Data-layer gap: rows flipped to `completed` without a `commission_payments` insert.

## Fix Proposed (dashboard only, no DB writes)
1. Strengthen filter in counts + history to exclude `referred_email LIKE 'paypal_%@pending' OR referred_name LIKE 'paypal_%@pending'` regardless of status.
2. Null-coalesce display name when it matches placeholder pattern.
3. Separate AF# ticket: reconcile `referrals.status='completed'` vs `commission_payments` existence; backfill or revert status.

## Do NOT
- Modify D1. It's not serving traffic.
- Delete SQLite. It IS the live data source.
- Touch admin endpoint (working correctly).
