# LinkedIn li_at Cookie Expired - Traveling Comments Blocked

**Date**: 2026-04-05
**Agent**: dept-systems-technology
**Type**: operational
**Topic**: LinkedIn session cookie expired, preventing all authenticated actions

---

## Problem

Attempted to drop 3 traveling comments on LinkedIn (Branson, Grant, Sinek).
All LinkedIn navigations fail with "redirectLoop" error in Camoufox.

## Root Cause

The `li_at` session token in both `jared-linkedin` and `jared-linkedin-fresh` profiles has **expired server-side** at LinkedIn. The cookie value (`AQEDAQl3neYA-ELyAAABnU8KmXcAAAGdcxcdd1YAX87MyK5SiiMmDibv3wJuReJoHgDiqe9NbSruYO0bPvZDeSYMUzo3PSM1Ay07b9GSb--T8zLuBusLyN00Y0chMDXtcefu7MzFIsR0M54Lf03qVJ5C`) is no longer valid.

## Verification

- LinkedIn loads fine on clean session (no auth) = HTTP 200, shows "Log In or Sign Up"
- LinkedIn redirects to login with the stale li_at = redirect loop (login -> feed -> login)
- Proxy works fine (httpbin.org returns 200 with residential IP 199.219.219.94)
- Browser (Camoufox 0.4.11) works fine for non-LinkedIn sites
- Nathan's profile has a DIFFERENT li_at and may still work (different LinkedIn account)

## Key Technical Findings

1. **Native DB vs JSON overlay**: PureSurf uses `persistent_context` which creates Firefox profile dirs. Cookies exist in BOTH `cookies.json` (PureSurf overlay) AND `cookies.sqlite` (Firefox native). The `li_at` was only in `cookies.json`, NOT in `cookies.sqlite` - so Firefox never had it natively.

2. **Rate limiter tightening**: The tightening_factor was 1.2 from past 429s, which floors `max_per_minute` from 1 to 0 (`floor(1/1.2)=0`). Reset via: `PUT /rate-limits/linkedin.com` with `{"reset_tightening": true}`.

3. **Cookie injection to native DB**: Even after injecting `li_at` directly into `cookies.sqlite`, the redirect loop persisted. This confirms the token itself is expired, not a cookie loading issue.

## Fix Required

Jared must re-sync cookies from his browser where he's actively logged into LinkedIn:
- Use the PureSurf Chrome extension, or
- Use the PureSurf dashboard cookie paste, or  
- Use the bookmarklet to export cookies

The critical cookie is `li_at` (httpOnly, so bookmarklet won't capture it - need the Chrome extension).

## Rate Limiter Notes

- After 429s, tightening_factor increases. Use `reset_tightening: true` in PUT to reset.
- LinkedIn max_per_minute of 1 with tightening 1.2 = effective 0. Set base to 2+ or reset tightening.
- Total 429 count: 6 (accumulated across sessions)

## Files/Profiles Involved

- Profile: `jared-linkedin` (has li_at in cookies.json, now also in cookies.sqlite)
- Profile: `jared-linkedin-fresh` (had no li_at until spillover)
- Native DB: `/opt/baas/profiles/s_jared-linkedin/cookies.sqlite`
