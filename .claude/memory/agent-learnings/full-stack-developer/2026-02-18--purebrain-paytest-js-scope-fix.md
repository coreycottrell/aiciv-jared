# Memory: purebrain.ai/pay-test JS Scope Fix + Feature Build

**Date**: 2026-02-18
**Type**: teaching
**Agent**: full-stack-developer

## What Happened

Fixed a critical bug on purebrain.ai/pay-test (WordPress page ID 439) where the "See What [AI NAME] Can Do" button did nothing when clicked.

## Root Cause

The entire main JavaScript block was wrapped inside `document.addEventListener('DOMContentLoaded', function() { ... })`. This creates a closure scope. Functions like `showPersonalizedCapabilities()`, `revealPricing()`, `closeCelebrationAndShowPricing()`, etc. were defined INSIDE this closure and therefore NOT accessible from `onclick=""` HTML attributes, which execute in the global window scope.

The onclick handlers were silently failing - no errors, just nothing happening.

## Fix Applied

Added explicit `window.*` assignments INSIDE the DOMContentLoaded callback, just before its closing `});`:

```javascript
window.showPersonalizedCapabilities = showPersonalizedCapabilities;
window.revealPricing = revealPricing;
window.closeCelebrationAndShowPricing = closeCelebrationAndShowPricing;
window.closeExitPopup = closeExitPopup;
window.allowExit = allowExit;
window.closeWaitlistModal = closeWaitlistModal;
window.openVideoModal = openVideoModal;
window.closeVideoModal = closeVideoModal;
window._pbState = state;  // Also export state for other scripts
```

Also changed onclick attributes themselves to use `window.` prefix as defensive coding:
```html
onclick="window.showPersonalizedCapabilities()"
onclick="window.revealPricing()"
```

## WordPress Deployment Gotcha (CRITICAL)

This WordPress page uses Elementor. Changes to `content.raw` via REST API are NOT what gets served to users. The live page is rendered from `meta._elementor_data`.

**Must update BOTH**:
1. `POST /wp-json/wp/v2/pages/439` with `{"content": "..."}` - updates raw content
2. `POST /wp-json/wp/v2/pages/439` with `{"meta": {"_elementor_data": "..."}}` - updates what's ACTUALLY served
3. `DELETE /wp-json/elementor/v1/cache` - clears Elementor's render cache
4. Final `POST /wp-json/wp/v2/pages/439` with `{"status": "publish"}` to republish

The Elementor data is JSON containing one top-level element with nested elements. The main HTML/JS is in a widget with ID `292c72a` (type: html).

## Features Built

1. Renamed button: "Discover what [AI NAME] can do" (was "See What [AI NAME] Can Do")
2. Updated `showPersonalizedCapabilities()` to return two-part response (features + personalized outline)
3. New CTA button after capabilities: "See what [AI NAME] can do for you" → calls `revealPricing()`
4. Updated PayPal Client ID from placeholder to real: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI`
5. Fixed integration glue to use `window._pbState.aiName` instead of direct `state.aiName` reference

## Post-Payment Flow

Already existed as a full implementation in the page:
- `initPayTestFlow()` - Entry point (line ~9400)
- Phases: Questionnaire → Behind the Curtain (10 slides) → Telegram Setup → Claude Max → Completion
- Triggered by `window.onPaymentComplete` callback from PayPal integration
- Full-screen overlay, chat-based UI using `ptc-*` CSS classes

## File Locations

- Live page: https://purebrain.ai/pay-test/
- WordPress page ID: 439
- Elementor widget ID: 292c72a
- Auth: HTTPBasicAuth('Aether', read from .env PUREBRAIN_WP_APP_PASSWORD)
