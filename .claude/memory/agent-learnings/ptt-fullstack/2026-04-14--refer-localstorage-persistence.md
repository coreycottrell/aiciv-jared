# Refer Page localStorage Persistence Fix

**Date**: 2026-04-14
**Type**: operational
**Topic**: /refer/ auto-login after first login (no URL param needed)
**File**: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/refer/index.html`
**Deploy ID**: 6cf72fea-82a8-42b8-bc8c-4021818040ce

## Problem

Users who logged in via `/refer/?code=PB-XXXX` could not return via plain `/refer/` without re-pasting the full URL. Session token was stored in `sessionStorage` (per-tab, cleared on tab close). On plain `/refer/` with no URL params, the bootstrap code (line 816-818) had no `code`/`email` to hand to `loadDashboard`, so the session branch still effectively failed — and a new tab always showed a blank login gate.

## Fix

1. Added `CODE_KEY = 'pb_affiliate_code'` in localStorage (persists across tab close, across devices unless cleared).
2. On successful login response, call `setStoredCode(data.referral_code)`.
3. At bootstrap (before branching on session), if no URL `code`/`email`, fall back to `localStorage.getItem('pb_affiliate_code')` and assign to `code` variable.
4. Exposed `window.pbLogout` that clears both sessionStorage token and localStorage code, redirects to `window.location.pathname`. No logout button exists in current UI — flagged as follow-up.
5. On 401/403 from dashboard API, also clear stored code (force re-login).

## Key Decisions

- **Code alone is NOT a credential.** Password still required on first visit per code. localStorage just avoids forcing URL paste.
- **No backend changes needed** — the `/api/referral/dashboard` endpoint already accepts `code` + `session_token`. Reused existing contract.
- **Reset link flow unaffected** — resetToken URL branch short-circuits before localStorage logic.

## Verification

- Backup: `exports/cf-pages-deploy/refer/index.html.bak-1776199774`
- pre-deploy-sync.sh completed (Chy's dirs synced, no conflict on refer/).
- cf-deploy.py deployed 1 changed file.
- CF cache purge via API: `{"success": true}` for `/refer/` + `/refer/index.html`.
- Live fetch `curl https://purebrain.ai/refer/` confirms 6 matches on new markers.

## Follow-ups

- **No logout button exists in /refer/**. Users can only clear via browser devtools or by using `pbLogout()` from console. Worth adding a small "Log out" link in the dashboard header — out of scope for this ticket.
- **Cross-device**: localStorage does not sync across devices. User must log in once per device/browser. Acceptable per original scope.
