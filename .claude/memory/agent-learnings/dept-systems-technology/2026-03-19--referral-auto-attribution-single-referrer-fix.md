# Referral Auto-Attribution & Single-Referrer Enforcement Fix

**Date**: 2026-03-19
**Type**: operational + teaching
**Topic**: Referral auto-attribution broken (401 auth), single-referrer enforcement, duplicate cleanup

## Root Causes Found

### Issue 1: Auto-Attribution Not Working on Payment
The /api/referral/complete endpoint in portal_server.py had check_auth(request) at the top.
This requires a Bearer token. But the browser JS on all landing pages calls this endpoint with a
plain fetch() — no auth header. Every call got 401 Unauthorized. Referrals were never recorded
automatically after payment.

Fix: Removed check_auth guard from api_referral_complete. This endpoint is intentionally
public — the referral_code itself acts as the credential (only valid codes proceed past the DB lookup).
Compare to /api/referral/track which was already public.

### Issue 2: Harrison Under Wrong Referrer
Harrison (harrison@bisnce.com) needed to be under Alex Logie (PB-K22P).
When diagnosed, Harrison was ALREADY correctly assigned to PB-K22P (done earlier in today's session).
No additional action needed — DB state was correct.

### Issue 3: Single-Referrer Not Enforced
The assign endpoint (/api/admin/referral/assign) only checked for the target referrer records.
It never checked if the client was ALREADY under a different referrer. This allowed the same email
to appear in multiple referrers conversion counts simultaneously.

Fix applied to two places:
1. api_referral_complete — now DELETEs any other referrer records for this email before inserting
2. api_admin_referral_assign — same DELETE logic; returns removed_prior count in response

Retroactive cleanup: fred@mypetcredentials.com had duplicate records under PB-V2CJ (id=21)
and PB-AYXE (id=22). Kept PB-AYXE (most recent), deleted PB-V2CJ record.

## Code Changes
File: /home/jared/purebrain_portal/portal_server.py
Backup: /home/jared/purebrain_portal/portal_server.py.bak.referral-auth-singleref-fix-20260319

Key SQL pattern for single-referrer enforcement:
    DELETE FROM referrals
    WHERE referred_email = ? COLLATE NOCASE
      AND referrer_id != ?

## Verification Results
- curl POST /api/referral/complete without auth returned 200 ok (was 401)
- Assign test: assigning same email to new referrer removes old record, removed_prior=1 in response
- DB final state: 0 clients under multiple referrers
- Harrison: 1 record only, under PB-K22P (Alexander Logie)

## Lesson: Browser vs Admin Endpoints
When an endpoint is called from browser JS (no auth headers available), do NOT put check_auth on it.
Browser-called endpoints: public. Admin/portal-called endpoints: require auth.
/api/referral/track and /api/referral/complete are both browser-called -> both should be public.
/api/admin/referral/assign is portal-called with admin token -> stays auth-gated.
