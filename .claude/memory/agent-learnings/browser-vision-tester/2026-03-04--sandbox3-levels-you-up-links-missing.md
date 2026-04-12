# Memory: Sandbox-3 QA - "How This Levels You Up" Links Not Deployed

**Date**: 2026-03-04
**Agent**: browser-vision-tester
**Type**: operational + gotcha
**Tags**: browser-vision, visual-testing, purebrain, paytest, sandbox3, pricing, links

---

## Task Summary

QA verification of sandbox-3 pay test page (purebrain.ai/pay-test-sandbox-3/) checking 6 criteria including new "How This Levels You Up" links below the $499 Partnered and $999 Unified CTA buttons.

---

## Key Finding: Links Not In Page Source At All

Searched the entire page HTML (document.documentElement.innerHTML) for:
- "How This Levels You Up" text — NOT FOUND
- "levels-you-up" in any href — NOT FOUND
- "partnered-how" in any href — NOT FOUND
- "unified-how" in any href — NOT FOUND

The links were requested to be added but had NOT been deployed to the page. The pricing card currently only has "Activate Your AI Now" buttons with no secondary links.

## What Passed

- Dark background: rgb(10, 14, 26) confirmed
- 3 tiers in DOM: Awakened $149, Partnered $499, Unified $999 (plus Enterprise)
- PayPal $499 Partnered modal: fully functional (PayPal + SEPA + card + simulate button)
- Chatbox (.chat-container): display:block, present

## Sandbox-3 Pricing Structure (Current)

Confirmed via DOM inspection (pricing is JS-gated, display:none by default):
- `window.revealPricing()` is the reveal function (not showPricing)
- Grid class: `.pricing-grid--4tier` (3 columns at desktop despite name)
- Button IDs: `proCta` (Awakened), `partnerCta` (Partnered), `unifiedCta` (Unified)
- Button text: "Activate Your AI Now" (not "Reserve Your AI Now" from main site)
- Strike prices shown: $197 (was), $579 (was), $1089 (was)

## "Your AI Is Born" Celebration Modal

When revealPricing() triggers, a celebration overlay fires on top of the pricing section:
- Title: "Your AI is born."
- Subtitle: "Welcome to the beginning of something extraordinary."
- Button: "SEE WHAT YOUR AI CAN DO ->"

This is expected behavior - it's the transition animation from the chatbox flow into the pricing reveal. It dismisses when the user clicks the button.

## CAPTCHA Rate Limiting

After multiple rapid page loads from same IP during testing, Cloudflare/GoDaddy triggers a CAPTCHA ("Please verify you are human"). This is why later screenshots showed CAPTCHA instead of the site. To avoid this: space page loads by at least 30 seconds between loads, or use a fresh session.

## Screenshots

Key evidence in: `/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-qa-20260304/`
- `07_pricing_forced_visible.png` — 3 tiers behind celebration overlay
- `12_after_499_click.png` — PayPal modal fully functional

## Full Report

`/home/jared/projects/AI-CIV/aether/exports/sandbox3-qa-report-20260304.md`
