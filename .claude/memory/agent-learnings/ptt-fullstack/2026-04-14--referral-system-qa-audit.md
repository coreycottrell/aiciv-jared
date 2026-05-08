# Referral System QA Audit — 2026-04-14

Type: operational
Topic: Health check of /refer/ and /admin/referrals after rendering bug report

## Screenshot (portal_20260414_191823_Screenshot...9.49.41AM.jpg)

It is the PUBLIC `/refer/` dashboard (logged in as JAREDSB0), NOT `/admin/referrals`.
Section: "Referral History" card. Jared drew arrows labelled **"wrong names"** (Person column) and **"missing earnings"** (Earnings column shows "—" or $7.45 that don't match expected values).

Visible rows:
- `paypal_l-guw94a3rk2ug@pending` — Converted — — — 2026-04-08  (malformed row: email-shaped name, no earnings, "Converted" status)
- Faris Asmar — Converted — — — 2026-04-18  (no earnings despite Converted)
- Travis Thompson — Converted — — — 2026-03-19
- Trini Morgane Vernaut — Converted — $7.45 — 2026-03-18
- John Parkins — Converted — $7.40 — 2026-03-18
- Linda Rosanio — Converted — $7.45
- Michael Hancock — Converted — $7.45
- Lucas Neuhofel — Converted — $7.45
- Bethanie Delloee — Converted — $7.45
- Jay Hutton — Converted — $3.73 — 2026-03-18

## Data Reality Check

`GET https://portal.purebrain.ai/api/referral/leaderboard` returns:
```
{"name":"MJ S","referral_code":"JAREDSB0","completed":10,"total_earned":70.78}
```
Leaderboard totals = 10 completed / $70.78. Screenshot shows ~8 paid rows summing to $55.93 + 2 zero-earning "Converted" rows. Missing $14.85 worth of earnings vs. leaderboard total. Names and amounts in dashboard appear to be genuine DB rows — the bug is that **earnings are missing on 2 rows that are marked "Converted"**, and one row has an email-template string as the "referred_name".

## Endpoints

- `GET https://app.purebrain.ai/api/referral/dashboard?referral_code=X&email=X` → 400 without both (returns history)
- `GET https://portal.purebrain.ai/api/referral/leaderboard` → 200, fine
- `GET /api/admin/affiliates?admin_token=...` → 401 without token (correct)
- `/api/referrals`, `/api/admin/referrals` → 404 (do not exist — only `/affiliates`, `/clients`, `/payouts`)

## Public /refer/ (PASS)
- HTTP 200, 76KB, 285ms
- History renders via `apiBase + '/dashboard'` on `app.purebrain.ai`
- Earnings formatted: `parseFloat(r.earnings||0) > 0 ? '$' + …toFixed(2) : '—'`  ← "—" is intentional when earnings==0

## Admin /admin/referrals (PASS structurally)
- HTTP 200, 54KB. Gated by admin_token.
- Renders from `/api/admin/affiliates` → each affiliate has `.history[]` with `referred_name`, `referred_email`, `status`, `created_at`, `earnings`

## Root Cause Hypothesis (Frontend vs Backend)

Frontend rendering is correct. Template uses `r.referred_name || r.referred_email || '—'`. The `paypal_l-guw94a3rk2ug@pending` string is a DB-level corruption: `referred_name` column was populated with a magic-link/pending-paypal token string instead of a real name. That's a **backend write bug**, not a rendering bug. Explains why cache purge + incognito didn't help.

The `Converted` + $0 rows ("Faris Asmar", "Travis Thompson") are a **commission-calculation gap**: status was flipped to completed without the earnings column being set (constitutional rule: $35 × 5% = $1.75 per referral minimum, 60/40 split to Corey/PT).

## Constitutional Check
- feedback_paypal_auto_split_constitutional.md: 5% referral = $1.75 on $35 ops. None of the $7.45 rows match that math — those reflect a prior higher commission rate or bundled amounts. Flag for verification against spreadsheet `1bmmO2FVxZdAcYewPFNu6DbHZzh9AAojHUsWgofv6tqQ`.

## Fix Routing
ST#/ptt-fullstack needs to:
1. Audit `referrals` table for rows where `status='completed' AND (earnings IS NULL OR earnings=0)` — backfill or revert status
2. Audit for rows where `referred_name` matches `/paypal_.*@pending/` or email-shaped — re-derive name from signup record
3. Verify commission math vs constitutional rule going forward
