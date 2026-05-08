# Referrals Admin Dashboard Feature Parity

**Date**: 2026-04-21
**Type**: operational
**Agent**: full-stack-developer

## What Was Done

Enhanced `/home/jared/purebrain-site/admin/referrals/index.html` (on `admin-rebuild` branch) to add features from the production version:

1. **Overview tab** - Added as first/default tab with top referrers summary cards and recent activity table (last 20 referrals sorted by date)
2. **Referral inline edit** - Expanded affiliate rows now include edit buttons per referral. Clicking opens inline edit form with name, email, status fields. API: PUT `/api/admin/referral/update`
3. **Assign client with autocomplete** - Replaced simple dropdown with search-as-you-type autocomplete. Keyboard navigation (up/down/enter/esc) supported. Per-affiliate assign buttons in table rows.
4. **Referral link display** - Expanded rows now show the referral link URL

## Key Patterns

- Staging uses ES5 IIFE pattern (no arrow functions, no let/const, no async/await) while production uses modern ES6+. All additions maintained the ES5 style for consistency.
- Staging uses `api()` helper returning Promises; production uses `apiFetch()` with async/await.
- Autocomplete uses `mousedown` instead of `click` to prevent blur race condition on input field.
- Production assigns by `referral_code`, staging's old assign used `referrer_id`. Updated to match production's `referral_code` + `client_email` body format.

## File

`/home/jared/purebrain-site/admin/referrals/index.html` (~1286 lines)
