# Browser Payment Autofill Suppression on Chat Input Fields

**Date**: 2026-03-22
**Type**: teaching
**Topic**: How to suppress browser payment autofill dropdowns on chat input fields co-located with PayPal widgets

## Problem
When PayPal/payment elements exist on a page, Chrome/browsers aggressively offer payment autofill on ALL input fields on that page — including chat text inputs. The previous `autocomplete="off"` was insufficient because Chrome ignores it when payment context is detected.

## Solution
Three-layer fix on each chat input:
1. `autocomplete="one-time-code"` — tells Chrome "this is a one-time code, not payment"
2. `data-lpignore="true"` — suppresses LastPass/1Password overlays
3. `data-form-type="other"` — additional signal to password managers

For JS-created inputs (like `#ptc-input` textarea): set these as JS properties/attributes immediately after `textarea.id = 'ptc-input'`.

## Files Affected (all contain chat inputs needing this fix)
- `exports/cf-pages-deploy/pay-test-sandbox-3/index.html` — `#userInput` (HTML) + `#ptc-input` (JS)
- `exports/cf-pages-deploy/pay-test-sandbox-4/index.html` — same pattern
- `exports/cf-pages-deploy/live/index.html` — same pattern
- `exports/cf-pages-deploy/awakened/index.html` — same pattern
- `exports/cf-pages-deploy/partnered/index.html` — same pattern
- `exports/cf-pages-deploy/unified/index.html` — same pattern
- `exports/cf-pages-deploy/index.html` — `#userInput` only (no ptc-input)

## Files Without Chat Inputs (no fix needed)
- `pay-test/index.html` — no chat input found
- `pay-test-sandbox/index.html` — no chat input found

## Input IDs to Know
- `#userInput` — the pre-chat questionnaire input (HTML `<input type="text">` in a `<form>`)
- `#ptc-input` — the post-portal chat textarea (created via JS: `document.createElement('textarea')`)

## Pattern for ptc-input JS fix
```js
textarea.id = 'ptc-input';
textarea.autocomplete = 'one-time-code';
textarea.setAttribute('data-lpignore', 'true');
textarea.setAttribute('data-form-type', 'other');
textarea.rows = 1;
```

## Deploy Command
```bash
CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true
```
Note: CF Pages auto-invalidates cache per deployment — no zone-level purge needed.
