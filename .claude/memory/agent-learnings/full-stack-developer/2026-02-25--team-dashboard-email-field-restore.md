# Team Dashboard Email Field Restore

**Date**: 2026-02-25
**Type**: operational
**Topic**: Restoring email domain-whitelist login field to team-dashboard-v4.html

## What Was Done

Restored the email address field to the team dashboard login form at:
`/home/jared/projects/AI-CIV/aether/exports/team-dashboard-v4.html`

Three changes made:

### 1. HTML Form (line ~2063)
Added `<div class="login-form-group">` with `id="login-email"` between the name autocomplete field and the password field. Updated the password field comment from "Field 2" to "Field 3" to stay consistent.

### 2. handleLogin() JS (~line 3204)
- Added `const email = document.getElementById('login-email').value.trim().toLowerCase();`
- Updated empty-check from `!name || !password` → `!name || !email || !password`
- Added domain validation block with `allowedDomains` array:
  - puretechnology.nyc, puretechnology.ai, puremarketing.ai, purebrain.ai, jareddsanborn.com, pureinfluence.ai
- NOTE: Old version had `puretek.co` — replaced with new list above

### 3. initAutocomplete() mousedown handler (~line 3302)
Added email auto-fill when user clicks autocomplete item:
```javascript
const emailInput = document.getElementById('login-email');
if (emailInput && m.email) emailInput.value = m.email;
```
Focus still goes to password field after auto-fill.

## Deployment
- Netlify site: `d2556d0a-5333-47ca-a8d6-8add4141f090`
- URL: https://pure-tech-dashboard.netlify.app
- Auth token env var: `NETLIFY_AUTH_TOKEN` (NOT sourced via .env — must set explicitly due to .env parse errors)
- Deploy command: `NETLIFY_AUTH_TOKEN=... npx netlify-cli deploy --prod --dir=/tmp/dashboard-deploy --site=...`
- Copy HTML to `/tmp/dashboard-deploy/index.html` first

## Gotcha: .env source errors
`source .env` throws errors for comment lines with special chars — NETLIFY_AUTH_TOKEN ends up unset.
Solution: Extract the value directly from .env with grep and set explicitly.
