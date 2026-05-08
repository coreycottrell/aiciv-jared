# /refer/ Logout button + forgot-password referral_code fix

**Date**: 2026-04-14
**Type**: operational
**Topic**: Adding visible logout + fixing forgot-password backend to support referral_code payload

## What was done

1. **Logout button UI** added to `exports/cf-pages-deploy/refer/index.html` inside `#pb-ref-dashboard-content` (line ~513). Small bordered text link on right side of a new header row; left side shows "Signed in as <code>". Calls existing `window.pbLogout()`. Hover color swaps to #f1420b.

2. **Populate user-code element**: Added `document.getElementById('pb-dash-user-code').textContent = d.referral_code` in loadDashboard success block (~line 1040).

3. **forgot-password.js backend** was rejecting `{referral_code: "PB-XXXX"}` with 400 even though the frontend (`pbForgotSubmit`) sends that payload when input matches `/^(PB-)?[A-Za-z0-9]{4,10}$/i`. Fixed by adding referral_code → user_email lookup before the existing email path.

## Deploy

- Deploy ID: `b7a64ed6-096f-40e0-9085-dcaaa64315ec`
- Files: `refer/index.html`, `functions/api/referral/forgot-password.js`
- CF cache purged for /refer/

## Verification

- `curl https://purebrain.ai/refer/` shows `pbLogout` (2 refs), `Log out` (1), `pb-dash-user-code` (2).
- `POST /api/referral/forgot-password` with email, referral_code, or empty all return correct responses (200 / 200 / 400).

## Gotcha

`cf-deploy.py` expects paths relative to `exports/cf-pages-deploy/`, not absolute or from repo root.
