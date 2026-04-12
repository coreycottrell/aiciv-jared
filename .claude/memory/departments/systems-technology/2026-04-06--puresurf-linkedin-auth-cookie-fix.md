# PureSurf LinkedIn Auth Cookie Fix

**Date**: 2026-04-06
**Type**: operational
**Server**: 157.180.69.225
**File**: /opt/baas/baas_server_simple.py
**Backup**: /opt/baas/baas_server_simple.py.bak.YYYYMMDDHHMMSS

## Problem
LinkedIn rejects li_at auth cookies when synced from Chrome to Camoufox sessions. Three root causes:
1. TLS fingerprint mismatch - cookies injected before TLS handshake
2. Cookie domain format differences between Chrome extension and Camoufox
3. Login redirect destroys good auth cookies on session close

## Fixes Applied (5 total)

### Fix 1: Cookie Injection Timing (in _launch)
- Changed flow: navigate to linkedin.com/robots.txt FIRST (establishes TLS) -> inject cookies -> navigate to /feed/
- If auth fails (redirect to login), navigates to about:blank to prevent cookie save from overwriting

### Fix 2: Cookie Domain Normalization (new _normalize_cookie_domains function)
- `.www.linkedin.com` -> `.linkedin.com` (except JSESSIONID which needs `.www.linkedin.com`)
- `www.linkedin.com` / `linkedin.com` -> `.linkedin.com`
- Removes Chrome extension fields (hostOnly, session, storeId, id)
- Validates sameSite values for Playwright compatibility

### Fix 3: Bulletproof Cookie Save Guard (in _save_cookies)
- Expanded login URL detection: /login, /uas/login, /signin, /auth, /checkpoint, /uas/authenticate
- Added page TITLE check for login indicators
- Blocks save if old profile had MORE auth cookies than new set (partial loss detection)
- Blocks save if li_at value looks cleared/invalid
- Detailed logging: COOKIE GUARD logs show old vs new auth counts

### Fix 4: Cookie Persistence Quality (in _save_cookies auth guard)
- Only saves if new cookies are BETTER than existing (not just different)
- Tracks auth cookie names: li_at, JSESSIONID, sid, auth_token, li_mc
- Compares old vs new auth cookie sets before allowing save

### Fix 5: Test Script
- Created /opt/baas/test_linkedin_auth.py
- Tests: session creation -> cookie check -> TLS establishment -> feed navigation -> auth verification
- Safe close: does NOT save cookies on auth failure

## Testing
After fresh Chrome cookie sync: `python3 /opt/baas/test_linkedin_auth.py jared-linkedin-fresh`
PASS = "Feed | LinkedIn" title, FAIL = login redirect

## Key Insight
The critical fix is #1 (timing). GoLogin/Multilogin establish TLS FIRST, then inject cookies. We were doing it backwards - injecting cookies into a context that hadn't yet spoken to LinkedIn's servers, so LinkedIn saw the cookie presented with a different TLS fingerprint than the one that originally created it.
