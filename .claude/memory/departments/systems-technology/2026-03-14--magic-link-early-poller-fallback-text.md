# Magic Link Button: Fallback Text + Early Poller Pattern
**Date**: 2026-03-14
**Files Changed**: All 6 payment pages in exports/cf-pages-deploy/

## What Was Built
Two UX improvements to the Brain Stream button flow across all 6 payment pages:

### Change 1: Fallback Text Below Button
- Added italic muted (#6b7280) centered 12px note below the `ptc-portal-placeholder` inside `.ptc-bubble`
- Text: "If this button doesn't light up in the next 3 minutes, check the email you provided earlier in the chat."
- Implementation: `var fallbackNote = document.createElement('p')` appended to `brainStreamWrapper.querySelector('.ptc-bubble')`

### Change 2: Early Poller + Retry-Aware Activation
Three sub-changes:
1. **`activateButton()` retry guard**: When `ptc-portal-placeholder` doesn't exist yet, stores link in `payTestData.magicLinkReady`, `payTestData.magicLink`, `payTestData.resolvedAiName` instead of silently returning
2. **Immediate activation on button render**: When `brainStreamWrapper` is created, checks `payTestData.magicLinkReady` and activates immediately via 100ms setTimeout
3. **Early `runMagicLinkPoller(dom, aiName)` call**: Added in `initPayTestFlow()` right after `buildLayout()` — poller starts at payment confirmation, not when user reaches the button

## Key Insight
`runMagicLinkPoller` already has a `stopped` guard so calling it twice is safe — first invocation wins. The early call just means the API polling starts immediately when the chat window opens.

## Files
- `exports/cf-pages-deploy/pay-test-2/index.html`
- `exports/cf-pages-deploy/pay-test-sandbox-3/index.html`
- `exports/cf-pages-deploy/insiders/index.html`
- `exports/cf-pages-deploy/pay-test-awakened/index.html`
- `exports/cf-pages-deploy/pay-test-partnered/index.html`
- `exports/cf-pages-deploy/pay-test-unified/index.html`

## Syntax Verification
New code blocks confirmed SYNTAX OK via `node --check`. Pre-existing wp_customize_support_script JSON blocks in the files cause false positives in whole-file Node checks — this is normal for these WordPress-exported HTML files.
