# Pay-Test-5 PayPal Fix — 2026-03-10

**Type**: gotcha + fix
**Agent**: dept-systems-technology
**Page**: purebrain.ai/pay-test-5/ (page ID: 1527)

## Problem
pay-test-5 Elementor widget contained an entire embedded WordPress page render (800KB)
inside the HTML widget. This happened because the page was created by saving a full
browser-rendered WordPress page HTML directly into the Elementor HTML widget — creating
a "page within a page" structure.

- PT5 widget: 799KB (embedded full WordPress page + actual page content)
- PT2 widget: 359KB (clean: fonts/CSS + actual page content only)

## Root Cause
The PT5 HTML widget started with:
`<style>/* === HOMEPAGE FIX 2026-03-10 === */</style><!DOCTYPE html><html lang="en-US">...`

The full WordPress admin bar, head tags, body tags, CSS, and JS were all embedded
inside the Elementor widget, making the page bloated and structurally wrong.

## Fix Applied
Replaced PT5's Elementor widget HTML with PT2's clean Elementor widget HTML.
Both pages have identical actual content (hero, sections, pricing, scripts).

API endpoint used:
- `POST https://purebrain.ai/wp-json/wp/v2/pages/1527` (update)
- `DELETE https://purebrain.ai/wp-json/elementor/v1/cache` (cache clear)
- Auth: user "Aether", PUREBRAIN_WP_APP_PASSWORD from .env

## Page IDs (Corrected from task description)
- pay-test-2 actual ID: **689** (task said 823 — was wrong)
- pay-test-5 actual ID: **1527** (correct)

## Verification Results
All 5 checks PASS after fix:
1. openPayPalModal exists (6 occurrences)
2. PayPal SDK Integration script present
3. Post-Payment Chat Flow script present
4. Integration Glue script present
5. No "Reserve Keen Now" buttons anywhere

## Notes
- "Reserve Keen Now" was never on the live page — Jared may have seen a cached/old version
- The pricing section buttons say "Reserve Your AI Now" calling `openWaitlistModal()`
- The PayPal SDK Integration script overrides `window.openWaitlistModal` with real PayPal checkout
- The Enterprise tier button intentionally shows a "Let's Talk" waitlist form (correct)
- PayPal client ID: live (not sandbox), starts with AWgWNlBQ...
