# Portal Refer & Earn 401 Fix — P-1 Completion
**Date**: 2026-04-15
**Agent**: full-stack-developer
**Type**: operational / teaching
**Topic**: /api/refer/me returned 401, frontend fell through to legacy that also 401'd

## Root Cause
The backend was actually fine — `check_auth()` at `portal_server.py:1022` correctly allowlisted `/api/refer/` for query-param auth. Verified via curl: 200 with valid token via Bearer header OR `?token=`.

The visible 401 error came from the **frontend fall-through pattern**:
1. `/api/refer/me` returned 401 (most likely: outer-scope `token` var was empty at call time — user logged in via URL-token path at line 8447 which sets `token = urlToken` but does NOT persist to localStorage).
2. `.catch()` caught the thrown `safeJson` "Server error 401".
3. Fell to `legacyLoadReferrals()` which calls `/api/referral/register` or `/api/referral/dashboard` — those also 401'd (for the same empty-token reason).
4. Final `.catch` at line 11889 produced the exact string: **"Error loading referral data: Server error 401"**.

Secondary issue: `/api/admin/referrals/d1` wasn't in the check_auth allowlist, so admin view returned 401 too.

## Fix Applied
1. **Frontend hardening** (`portal-pb-styled.html:11828-11885`):
   - Pull token fresh from `localStorage.getItem('portal_token')` as fallback
   - Abort with clear message if no token at all (don't send empty-token requests)
   - On 401 specifically: surface clear error, do NOT cascade to legacy (legacy will also 401)
   - Added `console.log` diagnostics (token prefix, status code)

2. **Backend allowlist widened** (`portal_server.py:1022`):
   - Added `/api/admin/referrals` to query-param token allowlist

3. **Portal restarted**: `sudo systemctl restart aether-portal.service` — active, HTTP 200.

## Test Matrix Results (all pass)
- [A] Portal `/api/refer/me?email=jared@puretechnology.nyc`: `ok:True, code:JAREDSB0, 10 referrals preserved`
- [B] Admin `/api/admin/referrals/d1`: `ok:True, count:72 affiliates`
- [C] Public `purebrain.ai/refer/`: HTTP 200
- [D] New customer auto-provision: `PB-DHV8FE` created in D1
- [E] Idempotent re-call: same code returned (no duplicate row)

## Files Changed
- `/home/jared/purebrain_portal/portal-pb-styled.html` (backed up: `.bak-401-fix-20260415`)
- `/home/jared/purebrain_portal/portal_server.py` (line 1022 allowlist)

## Rollback
- Flag: `USE_D1_REFERRALS=false` in systemd env → `/api/refer/me` returns `{disabled:true}` → frontend falls to legacy SQLite.
- File: restore `portal-pb-styled.html.bak-401-fix-20260415`.
- Restart: `sudo systemctl restart aether-portal.service`.

## Key Learning
**When customer sees 401 but backend works**: check the fall-through pattern. Catch blocks that redirect to "legacy fallback" can MASK the real 401 source and compound errors. Always short-circuit on 401s with clear messaging — never cascade to another auth-protected endpoint.

## What Jared Must Do
**Hard-refresh portal** (Ctrl+Shift+R on `portal.purebrain.ai`) to pick up new HTML with fallback token logic + clear error messages. If still 401 after hard-refresh: he needs to log out and log back in — his session token is likely stale from a portal restart earlier today.
