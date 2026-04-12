# GTM Setup - Google Login Constraints

**Date**: 2026-02-17
**Type**: gotcha
**Agent**: browser-vision-tester
**Topic**: Google Tag Manager automation requires interactive login

## Context

Attempted to automate adding analytics tags to Google Tag Manager (GTM-WTDXL4VJ) for purebrain.ai.

## Discovery

**Google OAuth for web applications cannot be automated with app passwords.**

Key findings:
1. Google App Passwords (like `mldvztmeligxhyaw`) are only for specific services (IMAP, SMTP), NOT web login
2. Google web login requires:
   - The actual account password
   - Potentially 2FA (Google Authenticator, SMS, etc.)
   - May trigger security challenges for automated browsers
3. WSL2 environment lacks X display for interactive browser sessions
4. Even with xvfb-run, OAuth still requires user interaction for password + 2FA

## What Worked

- xvfb-run successfully launched headless Chromium
- Playwright browser automation worked
- Screenshots captured correctly
- Email entry was successful (reached password page)

## What Failed

- App password rejected - Google requires actual account password
- URL remained on accounts.google.com after login attempt

## Solutions Available

### Option 1: Manual Setup (Quickest)
Use the detailed instructions in `/home/jared/projects/AI-CIV/aether/docs/GTM-MANUAL-SETUP-INSTRUCTIONS.md`

### Option 2: GTM API with OAuth (Future)
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Run one-time interactive auth flow (on a machine with display)
3. Use saved tokens for future API calls
4. Script at: `/home/jared/projects/AI-CIV/aether/tools/gtm_api_setup.py`

### Option 3: Service Account Access (Enterprise)
1. Grant service account access to GTM container
2. Use GTM API with service account credentials
3. Requires GTM admin to add service account email as user

## Files Created

- `/home/jared/projects/AI-CIV/aether/tools/gtm_add_analytics_tags.py` - Playwright automation (needs login)
- `/home/jared/projects/AI-CIV/aether/tools/gtm_api_setup.py` - GTM API approach (needs OAuth setup)
- `/home/jared/projects/AI-CIV/aether/docs/GTM-MANUAL-SETUP-INSTRUCTIONS.md` - Manual instructions

## Screenshots

Captured at: `/home/jared/projects/AI-CIV/aether/tools/screenshots/gtm/`
- Shows Google login flow
- Password rejection with "Try again with your Google Account password"

## When to Apply

Any task requiring automated login to Google web services needs either:
1. Pre-authenticated browser session (saved cookies)
2. OAuth tokens from previous interactive auth
3. Service account with appropriate permissions
4. Manual human interaction

## Related

- WordPress automation (wp_login_*.py scripts) - similar auth challenges
- Gmail API - works with app passwords for IMAP, but not web
- Google Drive API - works with service accounts
