# GA4 Conversion Events Wiring — purebrain.ai

**Date**: 2026-04-15
**Type**: operational + gotcha
**Tags**: ga4, gtm, analytics, conversions, cf-pages, wordpress-divergence

## Context

Task: wire GA4 conversion events (`form_submit`, `sign_up`, `purchase`, `chat_open`) on purebrain.ai. Prior audit showed 43 form-starts / 0 completions — zero standard GA4 events were being pushed.

## What Shipped

New file `js/ga4-conversions.js` pushes GA4 standard events to dataLayer for GTM `GTM-WTDXL4VJ` (already installed site-wide) to forward to GA4 property `525007539`.

Events wired:
- `form_submit`: global capture-phase `submit` listener (skips PayPal hidden form)
- `sign_up`: fires on `/thank-you/` when URL has `?tier=`
- `purchase`: exposed as `window.ga4TrackPurchase`, called from `onPaymentComplete` in `js/payment-glue.js`
- `chat_open`: exposed as `window.ga4TrackChatOpen`, called from `startConversation` in `js/homepage-chat.js`

Tier → USD value map hard-coded in ga4-conversions.js.

## Files Edited (CF Pages tree)

- NEW: `exports/cf-pages-deploy/js/ga4-conversions.js`
- `exports/cf-pages-deploy/js/payment-glue.js` (+ ga4TrackPurchase call inside onPaymentComplete)
- `exports/cf-pages-deploy/js/homepage-chat.js` (+ ga4TrackChatOpen call inside startConversation)
- `exports/cf-pages-deploy/index.html` (+ `<script src="/js/ga4-conversions.js">`)
- `exports/cf-pages-deploy/thank-you/index.html` (+ same script tag)

Backups: `.bak-2026-04-15-ga4-conversions` suffix on all modified files.

Deploy ID: `1a9a2b47-f92c-4a8b-8a3a-b2f1d5986e2a` (purebrain-staging project).
CF cache purged for deployed URLs.

## CRITICAL GOTCHA — production purebrain.ai is WordPress, not CF Pages

Verified by HTTP headers:
- `curl -I https://purebrain.ai/js/ga4-conversions.js` → `content-type: text/html`, `cache-control: public, max-age=14400` (WordPress fallback)
- `curl -I https://purebrain-staging.pages.dev/js/ga4-conversions.js` → `content-type: text/javascript`, correct file, 5564 bytes

`exports/cf-pages-deploy/index.html` has DIVERGED from live homepage HTML:
- Local file has `form_submit_success` dataLayer push (added presumably during a prior session) that is NOT on live homepage
- Live purebrain.ai homepage is served by WordPress origin through CF proxy
- Blog posts (`/blog/*`) DO serve from CF Pages (confirmed via March 19 audit: 333ms vs 7,164ms homepage)
- `/thank-you/` — needs to be verified which origin serves it

**Implication**: CF Pages deploy fires events ONLY where CF Pages is actually the origin (blog posts, `purebrain-staging.pages.dev`, and any route not intercepted by WordPress). The homepage + waitlist form + chat widget on live purebrain.ai will NOT fire the new events until the WordPress homepage is updated.

## Path Forward for Jared

Two options to get events firing on the WordPress-served homepage:

1. **Add tags directly in GTM** (preferred, no WP touch):
   - Configure GTM-WTDXL4VJ with:
     - Custom Event trigger → `form_submit_success` (already being pushed by live homepage at line 11397)
     - GA4 Event tag → `form_submit` mapping
   - GTM already has dataLayer access; this is a GTM UI change only.
   - For `purchase`: GTM needs to listen for PayPal success — the live homepage has `onPaymentComplete` inline but doesn't push any dataLayer event on success. Requires WP edit OR new tag in a WP plugin (gtm4wp).

2. **Edit WordPress homepage Elementor HTML widget** to include `<script src="/js/ga4-conversions.js" defer>` — more invasive, requires Yoast/Elementor editing skill.

3. **Short path for missing events**: add `<script>` via WordPress Customizer → Additional Head Scripts (if gtm4wp supports), inlining the ga4-conversions.js body.

## GA4 Conversion Marking (Jared action, UI only)

After events start flowing, Jared must:
- GA4 Admin → Events → wait 24-48h for events to appear
- Click the toggle under "Mark as conversion" for: `form_submit`, `sign_up`, `purchase`, `chat_open`
- No API call available from our current service account scope for this step.

## Verification commands

```bash
# Preview URL (works):
curl -s "https://purebrain-staging.pages.dev/js/ga4-conversions.js" | head -5
curl -s "https://purebrain-staging.pages.dev/" | grep -c "ga4-conversions.js"

# Production (currently WordPress-served — will NOT contain our script):
curl -sI "https://purebrain.ai/js/ga4-conversions.js"  # content-type: text/html = WordPress fallback
```

## DebugView Test Plan

Once production is actually updated:
- Open `https://purebrain.ai/?gtm_debug=1` in browser with GA4 DebugView open
- Submit waitlist form → expect `form_submit` in DebugView
- Click "Awaken Your PURE BRAIN" → expect `chat_open`
- Complete sandbox PayPal payment → expect `purchase` then redirect → `sign_up` on thank-you
