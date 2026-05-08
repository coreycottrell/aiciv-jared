# Referral ↔ Portal Ties Diagnostic — 2026-04-15

Type: operational + teaching
Topic: Post-D1-unification, full trace of every portal touch on referral data

## Key findings (compressed)

1. **Customer Refer & Earn panel uses legacy path** — `portal-pb-styled.html:11823` calls `/api/referral/register` (SQLite write), then `/api/referral/dashboard` (D1 read via flag). First-time users 404 on D1 because the register route doesn't mirror to D1.

2. **`/api/refer/me` is mounted but dead code** — `custom/routes.py:489`. Zero UI callers.

3. **Auto-provision hook is bound to payment-sync batch importer, NOT real-time signup.** Both `INSERT INTO clients` sites (`portal_server.py:3345` and `:6105`) are inside `_sync_payment_activity` + `api_admin_clients_import`. No `/api/signup` or PayPal webhook exists in portal_server.py.

4. **SQLite-only writes that D1 never sees:**
   - `api_referral_register` (3884) — INSERT INTO referrers
   - `api_referral_paypal_email` (4544) — INSERT INTO referrers
   - `api_referral_complete` (4359) — INSERT INTO referrals
   - `api_referral_record_commission` (4432) — INSERT INTO commission_payments
   - `api_referral_leaderboard` (4554) — read-only but SQLite-bound

5. **CF Pages referral functions (14 files) all marked DEPRECATED 2026-04-14** — banners are stale; they were never reachable because `app.purebrain.ai` routes to VPS. Harmless but confusing.

6. **Admin side IS wired to D1** — `api_admin_affiliates` has D1 short-circuit at line 5184. Leaderboard is the one hole.

7. **Potential bug B-7: Payment-page `/api/referral/complete` chain may be broken.** Only known caller was the deprecated CF function. Separate audit of payment pages needed.

## Patch priority

P-1: Wire /api/refer/me into loadReferrals() [1-2h]
P-2: Audit payment page → /api/referral/complete chain [2-3h]
P-3: Mirror referrer/commission writes to D1 [3-4h]
Total: 6-9h for "Refer & Earn live on every customer portal, auto-provisioned, real-time."

## Files touched (read-only)

- portal_server.py
- custom/routes.py, custom/referral_autoprovision.py
- referrals_d1_client.py
- portal-pb-styled.html, admin-referrals.html
- exports/cf-pages-deploy/refer/index.html
- exports/cf-pages-deploy/functions/api/referral/*.js

## Deliverable

/home/jared/exports/portal-files/referral-portal-ties-diagnostic-2026-04-15.md

## Delegation constraint reminder

Constitutional: NEVER modify portal code without Aether routing. This was read-only per instruction. Do not auto-fix B-7 (payment chain) — that's a separate SECURITY/QA-gated engineering pass.
