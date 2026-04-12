# ST Dept Memory: Referral System Full E2E Audit
**Date**: 2026-03-14
**Type**: audit + simulation
**Status**: 3 critical gaps found, 5 gaps total

## What Was Tested
Full live API test suite against localhost:8097. All 20+ test scenarios run with actual curl commands + DB verification.

## Key Findings

### WORKING
- All referral API endpoints respond correctly
- pay-test-sandbox-3 onPaymentComplete DOES call /api/referral/complete (previous gap FIXED)
- Commission recording works with idempotent order_id deduplication
- Full Alice->Bob->Charlie simulation completed successfully
- Admin dashboard accessible (bearer OR admin_token query param)
- Payout request flow works with $25 min threshold

### GAPS

**GAP 1 — CRITICAL SECURITY**: /api/referral/commission has NO auth check
- Anyone can POST fake commissions for known payer emails
- Fix: Add check_auth(request) to api_referral_record_commission
- Also: Add Authorization header in purebrain_log_server.py commission notification (~line 1273)

**GAP 2 — Auto-create referral code on purchase**: NOT IMPLEMENTED
- Users must manually sign up as affiliates
- Jared wants: new portal users auto-get a referral code
- Fix: After payment verification in log_server, call /api/referral/register for payer

**GAP 3 — Foreign keys OFF**: PRAGMA foreign_keys = 0
- Orphaned records accumulate silently
- Fix: Add PRAGMA foreign_keys = ON in _init_referral_db()

**GAP 4 — WAL mode not enabled**: journal_mode = delete
- In-flight writes lost on server kill (observed during audit: 8 test records lost)
- Fix: Add PRAGMA journal_mode = WAL in _init_referral_db()

**GAP 5 — PayPal email field**: /api/referral/paypal-email uses "email" not "referral_code"
- Check affiliate-portal.html JS sends correct field name

## Architecture Notes
- Commission flow: payment verified → log_server calls /api/referral/commission → portal_server issues reward
- Portal restarts frequently (portal-health-check.timer every 2 min)
- DB: /home/jared/purebrain_portal/referrals.db (single file, no backup)

## Files
- Full audit report: exports/departments/systems-technology/2026-03-14--referral-system-e2e-audit.md
- Portal server: /home/jared/purebrain_portal/portal_server.py
- Log server: /home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py (commission ~line 1263)
- Payment page: exports/cf-pages-deploy/pay-test-sandbox-3/index.html (onPaymentComplete ~line 17143)
