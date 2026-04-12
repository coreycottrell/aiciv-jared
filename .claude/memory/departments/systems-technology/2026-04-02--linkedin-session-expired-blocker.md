# LinkedIn Session Cookie Expiration Blocker

**Date**: 2026-04-02
**Agent**: dept-systems-technology
**Type**: operational
**Topic**: LinkedIn cookies expired, PureSurf cannot auto-login

---

## Problem

LinkedIn session cookies for `jared-linkedin` PureSurf profile expired between April 3 session and April 2 session. LinkedIn remembers the account (email masked as `s*****@puremarketing.ai`) but requires password re-entry.

## Key Findings

1. PureSurf loads 27 cookies for the profile but LinkedIn considers them expired
2. LinkedIn login page shows "Welcome back" with password field only (remembers account)
3. "Continue with Google" SSO opens a popup that PureSurf headless mode cannot handle
4. No LinkedIn password is stored anywhere in the project (.env, config/, .credentials/)
5. Google App Password (SMTP) in .env is NOT usable for LinkedIn or Google SSO

## Resolution Options

1. **Store LINKEDIN_PASSWORD in .env** for automated login via PureSurf evaluate
2. **Manual GoLogin session** to refresh cookies and export to PureSurf
3. **Build auto-login into PureSurf** social adapter (POST /social/adapters/linkedin/login)

## Cookie Expiration Timeline

- LinkedIn session cookies typically expire after 24-48 hours of inactivity
- Need a mechanism to refresh cookies automatically (cron job that navigates to LinkedIn daily?)
- Or need persistent credentials stored for re-authentication

## Files

- Screenshot: `/home/jared/exports/portal-files/linkedin-login-state.png`
