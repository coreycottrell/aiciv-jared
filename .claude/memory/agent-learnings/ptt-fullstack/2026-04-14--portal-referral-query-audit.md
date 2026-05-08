# Portal referral dashboard query audit — 2026-04-14

## Task
Patch alleged JOIN bugs in `portal_server.py` `api_referral_dashboard` (line 4036):
- paypal placeholder leak in `referred_name`
- "—" earnings on Converted rows that should show $1.75

## Finding: NO BUGS IN QUERY LAYER

### Queries are structurally identical
- `api_referral_dashboard` (portal_server.py:4127-4138)
- `api_admin_affiliates` (portal_server.py:5174-5184)

Both LEFT JOIN `commission_payments cp ON cp.referral_id = ref.id`, SUM `cp.commission_value` as earnings, GROUP BY `ref.id`.

Only diff: public adds `NOT (ref.status='rejected' AND ref.referred_email LIKE 'paypal_%@pending')` filter.

### DB state (clean)
- 0 rows with `referred_name LIKE 'paypal_%'` or `referred_email LIKE 'paypal_%'`
- 0 rows with value 1.75 in rewards or commission_payments
- All 26 referrals status='completed'
- Only distinct commission values: 7.45, 3.725
- One legit "—" row: id=77 trevor schoessow (referrer_id=25) — completed but NO reward + NO commission_payment (data integrity issue, not query bug). Admin view shows identical "—"

## Hypothesis for reported symptoms
Stale browser/CF cache showing pre-cleanup state. DB was cleaned by admin before my investigation.

## Lesson
`sqlite3` CLI not installed on this machine — use `python3 -c "import sqlite3; ..."` instead.

## Files referenced
- /home/jared/purebrain_portal/portal_server.py (382KB, 9006 lines)
- /home/jared/purebrain_portal/referrals.db

## Did not
- Edit portal_server.py
- Create backup (no edit needed)
- Restart service
- Run curl verification (no patch deployed)

## Recommendation to Jared
1. Hard-refresh /refer/ + flush CF cache on /api/referral/dashboard
2. Decide action for orphan referral id=77 (trevor schoessow)
3. If symptoms persist with fresh curl output, re-open with evidence
