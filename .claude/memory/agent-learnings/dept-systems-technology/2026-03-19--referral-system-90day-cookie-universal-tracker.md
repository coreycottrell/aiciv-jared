# Referral System: 90-Day Cookie + Universal Tracker

**Date**: 2026-03-19
**Type**: operational
**Topic**: 90-day first-touch cookie, universal referral-tracker.js, admin auth parity

## Tasks Completed

### Task 2: 90-Day Cookie Retention (First-Touch Attribution)
- Changed cookie expiry from 30 days to 90 days on all pages
- Added first-touch guard: `if (document.cookie.match(/(?:^|;)\s*pb_ref=/)) return;`
  - If cookie already set, early-return — original referrer keeps credit
- Normalized stored value to `ref.toUpperCase()` for consistency
- Pages fixed: `index.html` (homepage) + `pure-brain-agentic-ai-partner/index.html`

### Task 3: Universal Referral Tracker on ALL Pages
- Created: `exports/cf-pages-deploy/referral-tracker.js`
  - Checks ?ref=, ?code=, ?referral= URL params
  - First-touch: skips if pb_ref cookie already exists
  - Sets 90-day cookie + localStorage mirror
  - Fires /api/referral/track (non-blocking)
  - Exposes window.getPbRef() global helper
- Injected <script src="/referral-tracker.js" defer></script> into 185 HTML pages
- One fragment page (ai-tool-stack-calculator) had no </body> tag - appended at end
- Pages that already had inline referral JS (23 pages) now have BOTH:
  the inline block AND the tracker (tracker has first-touch guard so no double-fire)

### Task 4: Admin Auth Parity - ALREADY UNIFIED
- Both admin-referrals.html and admin-clients.html use IDENTICAL auth:
  - Same localStorage key: pb_admin_token (fallback: portal_token)
  - Same bearer token against same portal server
  - Both verify via /api/status endpoint
  - No code changes needed

## Architecture Notes
- referral-tracker.js deployed to CF Pages root -> served at https://purebrain.ai/referral-tracker.js
- window.getPbRef() defined in BOTH inline blocks and tracker file - idempotent
- Portal server admin auth: single bearer token in /home/jared/purebrain_portal/.portal-token

## Deployment
- CF Pages: 186 files uploaded (178 new/changed), deployment URL confirmed
- Portal restarted: active
