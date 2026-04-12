# CRITICAL: Session Close Overwrites Profile Cookies

**Date**: 2026-04-06
**Type**: operational (CRITICAL GOTCHA)
**Agent**: dept-marketing-advertising
**Topic**: BaaS session close saves browser cookies back to profile, destroying synced auth tokens

## The Problem

When a BaaS session is closed (DELETE /sessions/{id}), it saves ALL current browser cookies back to the profile's `cookies.json`. If the browser was on a LOGIN PAGE (because the previous token was expired/invalid), it saves cookies that do NOT contain `li_at` -- effectively destroying the fresh token that was synced.

## Timeline of Failure

1. **22:13 UTC**: Jared syncs fresh li_at via cookie sync (39 cookies synced, 43 total)
2. **22:07 UTC** (approx): Prior session already existed (created 20 min earlier with stale token)
3. **22:07-22:22**: Session navigated to feed, got redirected to login (li_at invalid)
4. **22:22 UTC**: Session closed, saving 41 cookies from login page state (NO li_at)
5. **22:23 UTC**: cookies.json overwritten with login-page cookies
6. **Result**: Fresh li_at token DESTROYED

## The Rule (PERMANENT)

**NEVER close a session that landed on a login page.** The saved cookies will overwrite the profile and destroy any valid auth token.

**Before creating a session after a fresh sync:**
1. Check `GET /api/v1/profiles/{name}/cookies` to verify li_at is present
2. Only THEN create a session
3. After navigate, immediately verify `document.title` is NOT "LinkedIn Login"
4. If login page detected: destroy session WITHOUT saving cookies (if possible)

## How to Verify li_at Before Session Create

```bash
curl -s "http://157.180.69.225:8901/api/v1/profiles/jared-linkedin-fresh/cookies" \
  -H "x-api-key: API_KEY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
cookies = data.get('cookies', [])
li_at = [c for c in cookies if c.get('name') == 'li_at']
if li_at:
    print(f'li_at FOUND: domain={li_at[0].get(\"domain\")} val={str(li_at[0].get(\"value\",\"\"))[:30]}...')
else:
    print('NO li_at - DO NOT CREATE SESSION')
"
```

## Feature Request for BaaS

Add a `save_cookies: false` option to DELETE /sessions/{id} so we can destroy a session without overwriting the profile cookies when we know the session is in a bad state.
