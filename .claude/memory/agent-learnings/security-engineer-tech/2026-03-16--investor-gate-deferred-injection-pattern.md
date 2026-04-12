# Investor Portal Gate: Deferred Content Injection Pattern

**Date**: 2026-03-16
**Type**: technique
**Agent**: security-engineer-tech

## What Was Fixed

The investor portal at `exports/cf-pages-deploy/investors/index.html` had two vulnerabilities:
1. Sensitive financial content (sections 3-6) existed in the DOM at load time, just hidden by CSS (`opacity: 0`). Dev tools could reveal it instantly.
2. The password `pureinvestor2026` was stored in plaintext in a JS const.

## The Fix Pattern (Deferred DOM Injection + SHA-256 Hash)

**Step 1**: Remove sensitive section HTML from the document body. Replace with empty placeholder divs:
```html
<div id="gated-calculator" class="gated-section"></div>
```

**Step 2**: Store section HTML as base64 strings in a JS object (`GATED_CONTENT`). The sensitive content never appears in the raw HTML source.

**Step 3**: Password stored as SHA-256 hex string only. Verification uses `crypto.subtle.digest()` (Web Crypto API, available in all modern browsers including CF Pages). This is async — `checkGate()` must be `async`.

**Step 4**: `injectGatedContent()` calls `atob()` on each entry and sets `el.innerHTML`. Called before `unlockPortal()` animation AND in the auto-unlock path.

## Key Implementation Notes

- `crypto.subtle` requires HTTPS (CF Pages satisfies this). Would fail on plain HTTP localhost.
- Base64 is obfuscation, not encryption. A determined attacker with JS skills can still `atob()` the strings. This is appropriate for "meaningfully harder" client-side gating without a server.
- SHA-256 stored hash: attacker can hash arbitrary guesses, but can't reverse the hash to get the password.
- `initPortal()` runs AFTER injection (inside the 650ms gate animation timeout), so Chart.js finds the canvas elements correctly.
- The auto-unlock path (sessionStorage check) must also call `injectGatedContent()` before revealing the portal — this is a common omission bug.

## SHA-256 Hash for pureinvestor2026
`ac33e72f151c5707a15a46ca7aa929d7ffb674143d61bdd0a61fc8ebff0d4f28`

## File Modified
`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors/index.html`
