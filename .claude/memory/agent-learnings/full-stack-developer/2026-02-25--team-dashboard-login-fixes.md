# Team Dashboard Login Fixes

**Date**: 2026-02-25
**Type**: operational
**File**: `/home/jared/projects/AI-CIV/aether/exports/team-dashboard-v4.html`

## What Was Fixed

### Bug 1: CSS/JS class mismatch on autocomplete dropdown
- CSS (line 437) used `.autocomplete-list.open { display: block; }`
- JS was adding/removing class `active` — wrong class, so dropdown was always hidden
- Fix: changed all `list.classList.add/remove('active')` to `list.classList.add/remove('open')` in `initAutocomplete()`
- Affected lines: 3287, 3294, 3305, 3312, 3321, 3326 (pre-fix line numbers)

### Bug 2: Removed email field from login form
- v4 had added a 3rd field (email with domain whitelist validation)
- Jared wanted simpler 2-field login: name typeahead + password
- Removed: entire email form group HTML block (~lines 2063-2075)
- Removed from `handleLogin()`: `const email = ...`, validation `if (!name || !email || !password)`, and email domain whitelist check (lines 3207, 3212, 3217-3222)
- Also removed the auto-fill of email field when user clicks autocomplete item (was referencing `login-email` which no longer exists)

## Deploy
- Site: https://pure-tech-dashboard.netlify.app
- Site ID: d2556d0a-5333-47ca-a8d6-8add4141f090
- Deploy command: `NETLIFY_AUTH_TOKEN=... npx netlify-cli deploy --prod --dir=/tmp/dashboard-deploy --site=...`
- Pattern: copy HTML as `/tmp/dashboard-deploy/index.html` before deploying

## Pattern: CSS class mismatch debugging
When a dropdown/element is invisible despite being added to the DOM, check:
1. What class does CSS show/hide on? (e.g., `.open`)
2. What class does JS add? (e.g., `.active`)
If different — that's the bug. Always grep both CSS and JS together.
