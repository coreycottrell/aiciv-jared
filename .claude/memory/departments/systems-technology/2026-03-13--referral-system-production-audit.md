# ST Dept Memory: Referral System Production Audit
**Date**: 2026-03-13
**Type**: audit
**Status**: Critical gap identified

## Findings Summary

- Referral page LIVE at purebrain.ai/refer/ — calls app.purebrain.ai (portal_server.py)
- Portal server is the authoritative backend (WP plugin never deployed — WAF blocked on 2026-03-05)
- Database: /home/jared/purebrain_portal/referrals.db (SQLite, 5 tables, functional)
- All API endpoints registered and responding
- PayPal credentials exist in .env but Payouts API not implemented (Phase 3b, by design)
- Manual payout bridge works: payout-requests.jsonl + Telegram notification to Jared

## CRITICAL BUG

**Payment pages do not call /api/referral/complete after payment success.**

The onPaymentComplete callback in pay-test-sandbox-3/index.html (and likely all other payment pages) NEVER fires the referral attribution. Referrers never earn money from real payments.

Fix: Add fetch to /api/referral/complete inside onPaymentComplete, passing getPbRef() code + payer email from payerInfo.

## Files

- Audit report: exports/departments/systems-technology/2026-03-13--referral-system-production-audit.md
- Plugin: tools/security/purebrain-referral/purebrain-referral-system.php (v2.2.0)
- Portal server: /home/jared/purebrain_portal/portal_server.py (routes at lines 2755-2765)
- Database: /home/jared/purebrain_portal/referrals.db
- Payout requests: /home/jared/purebrain_portal/payout-requests.jsonl
