# Memory: Blog Lead Capture Systems (v3.5.0)

**Date**: 2026-02-21
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: Lead capture forms added to purebrain.ai blog via security plugin

---

## What Was Built

Three lead capture components added to `purebrain-security-plugin.php` v3.5.0.

### Capture Point 1: In-Content Subscribe Box
- **Trigger**: 50% scroll depth on `body.single-post` pages
- **Behavior**: Slides in from below, animated with CSS keyframes
- **Placement**: JS injects element before `.blog-cta-block`, or after `.post-content` as fallback
- **Design**: Dark card `#0d1117` bg, `#2a93c1` border, 12px border-radius
- **Dismiss**: X button, sets `localStorage['pb_inline_dismissed'] = Date.now()` for 7 days
- **Copy**: "Enjoying this? Aether writes more like this every week in The Neural Feed."
- **Element ID**: `#pb-lead-inline`

### Capture Point 2: Post-Read CTA Bar
- **Trigger**: 85% scroll depth (only if not already subscribed)
- **Behavior**: Fixed bottom bar slides up from viewport bottom
- **Design**: Dark bar, orange CTA button (`#f1420b`)
- **Dismiss**: X button, sets `localStorage['pb_bar_dismissed'] = Date.now()` for 14 days
- **Copy**: "You made it to the end. That means you take AI seriously. So does Aether."
- **Sub-copy**: "Get The Neural Feed — AI partnership insights from inside the partnership. Free."
- **Element ID**: `#pb-lead-bar`

### Capture Point 3: Subscriber Detection
- **Key**: `localStorage['pb_subscribed'] = 'true'` on successful submit
- **Effect**: Neither form shows if flag is set
- **Success message**: "Welcome to The Neural Feed. Check your inbox — Aether is waiting."

---

## Server-Side Brevo Proxy

**Route**: `POST /wp-json/pb-security/v1/subscribe`
**Namespace**: `pb-security/v1` (separate from existing `purebrain/v1` to keep concerns clean)
**Body**: `{ "email": "user@example.com" }`
**Rate limit**: 5 requests/IP/minute (via existing `purebrain_check_rate_limit()`)
**Brevo API**: POST to `https://api.brevo.com/v3/contacts` with `listIds: [3]` and `updateEnabled: true`
**Auth**: Reads `BREVO_API_KEY` constant from `wp-config.php`

### Critical: BREVO_API_KEY must be in wp-config.php

```php
define( 'BREVO_API_KEY', 'xkeysib-...' );
```

Without this, the proxy returns `success: true` silently (to preserve UX) but doesn't add to Brevo.
The key is in `.env` as `BREVO_API_KEY`. Needs to go into GoDaddy wp-config.php via File Manager.

---

## Architecture Decisions

### Why `pb-security/v1` vs `purebrain/v1`?
- Keeps lead capture concerns separate from proxy/logging/payment endpoints
- Easier to scan namespace endpoints in the future

### Why wp_footer priority 25?
- Loads after most content but before the blog nav menu JS (default priority)
- Ensures DOM is ready and `.blog-cta-block` exists when element injection runs

### Why not a modal/popup?
- Per the task spec: "subtle inline card (not a popup)"
- Inline boxes convert better than disruptive popups on content-heavy pages
- Less jarring UX for engaged readers

### Inline box injection strategy
- The JS moves `#pb-lead-inline` from its initial position (bottom of body) into the post content flow
- It targets `.blog-cta-block` as the preferred anchor (places box before it)
- Falls back to appending to `.post-content` if no CTA block found
- This means the box appears in the natural reading flow after 50% scroll threshold

### CSS keyframe animations
- `pb-slide-in`: inline box slides up from 12px below + fades
- `pb-bar-slide`: bar slides up from bottom of viewport + fades
- Both use CSS `animation` (one-shot) not `transition` — no JS class flipping needed for entry

### Scroll listener performance
- Uses `{ passive: true }` on scroll event listener
- One shared handler for both 50% and 85% thresholds
- Short-circuits with boolean flags (`inlineShown`, `barShown`) so each shows max once

---

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
  - Bumped: v3.4.0 → v3.5.0
  - Added: `pb-security/v1/subscribe` route registration
  - Added: `purebrain_brevo_subscribe()` PHP function
  - Added: Lead capture CSS via `wp_head` (priority 25)
  - Added: Lead capture HTML + JS via `wp_footer` (priority 25)

- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v350.py`
  - Deploy + verify script for v3.5.0
  - 41-check validation suite
  - Live verification: endpoint OPTIONS + blog post HTML scan

---

## Deployment Result

- Deploy: SUCCESS (Playwright, CodeMirror, WP plugin editor)
- Live endpoint: HTTP 200 at `/wp-json/pb-security/v1/subscribe`
- Blog post markup: All 5 presence checks passed
- Cache: Flushed via WP admin

---

## Outstanding Item

`BREVO_API_KEY` needs to be added to `wp-config.php` on GoDaddy:
```php
define( 'BREVO_API_KEY', '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' );
```

Until this is done, form submissions will work on the frontend (success message shows, `pb_subscribed` sets)
but no contact will be created in Brevo. This is intentional graceful degradation.

---

## Patterns Reused

- `purebrain_check_rate_limit()` — existing transient-based rate limiter works perfectly
- Playwright deploy pattern — identical to v3.3.0 / v3.4.0 deployers
- PHP `defined( 'CONSTANT_NAME' )` pattern for wp-config.php secrets — same as ACGEE_API_KEY
- `wp_footer` / `wp_head` hooks with `is_single()` guard — same pattern as FAQ accordion
- `updateEnabled: true` in Brevo body — handles duplicate emails gracefully
