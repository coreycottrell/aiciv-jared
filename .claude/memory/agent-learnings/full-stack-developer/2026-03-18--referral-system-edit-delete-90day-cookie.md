# Referral System: Edit/Delete API + 90-Day Cookie

**Date**: 2026-03-18
**Type**: operational
**Topic**: PureBrain referral admin — edit/delete endpoints and cookie duration extension

## What Was Done

### Task 1: portal_server.py — 3 new admin API endpoints

Added before `serve_admin_referrals` function:

- `PUT /api/admin/affiliate/update` — updates user_name, user_email, paypal_email for a referrer by referral_code
- `DELETE /api/admin/affiliate/delete` — deletes referrer row; optionally cascades to referrals, referral_clicks, rewards, commission_payments
- `PUT /api/admin/referral/update` — updates referred_email, referred_name, status on a referrals row by id

All use `check_auth(request)` pattern (Bearer token from `.portal-token`). Routes added to the Route list with `methods=["PUT/DELETE", "OPTIONS"]`.

Also fixed `api_admin_affiliates` to include `ref.id` in the history SELECT query so the HTML can use referral IDs for the edit endpoint.

### Task 2: admin-referrals.html UI

- Added `btn-icon` / `btn-icon.danger` CSS classes for small icon action buttons
- Added `inline-edit-row` / `inline-edit-form` CSS for inline edit rows
- Added `#confirm-overlay` modal for delete confirmation
- Updated affiliate table from 9 to 10 columns (added "Actions" column)
- Affiliate rows now have edit (✏️) and delete (🗑️) icon buttons — hidden when `IS_READONLY`
- Inline edit row per affiliate (toggled by edit button), fields: Name, Email, PayPal Email
- `renderHistoryTable` updated to accept `affIdx` param; adds edit button per referral row when not read-only
- Inline edit row per referral (Name, Email, Status select)
- JS functions: `openAffiliateEdit`, `closeAffiliateEdit`, `saveAffiliateEdit`, `openAffiliateDelete`, `closeConfirm`, `openReferralEdit`, `closeReferralEdit`, `saveReferralEdit`
- All write-action buttons use `action-btn-write` class and `style="display:${IS_READONLY?'none':''}"` to hide in viewer mode

### Task 3: Cookie expiry 30 → 90 days

Files changed:
- `/home/jared/projects/AI-CIV/aether/exports/app-purebrain-ai-full-repo/wordpress-plugins/purebrain-referral/purebrain-referral-system.php` — line ~202
- 23 files under `exports/cf-pages-deploy/` — bulk `sed -i` on `expires.setDate(expires.getDate() + 30)`

`PAYOUT_COOLDOWN_DAYS = 30` in portal_server.py was intentionally left unchanged (payout cooldown, not tracking duration).

## Patterns / Gotchas

- The `_referral_db()` context manager uses WAL + foreign_keys ON — always use it for referral DB access
- `check_auth()` checks `Authorization: Bearer {token}` header OR `?token=` query param
- Viewer tokens use `_is_valid_admin_token()` + `_is_admin_token_readonly()` — new write endpoints only need `check_auth()` (main bearer)
- `commission_payments` table referenced in cascade delete — may or may not exist depending on migration state; the DELETE will succeed gracefully if the table doesn't exist (FK constraint only)
- CF pages files are standalone HTML — referral cookie code is embedded inline, not in a separate JS file
