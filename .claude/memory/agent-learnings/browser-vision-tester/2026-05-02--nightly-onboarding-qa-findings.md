# Nightly Onboarding QA -- 2026-05-02

**Type**: operational
**Topic**: PureBrain payment + onboarding pipeline E2E QA findings

## Context
Nightly E2E test of all payment pages per ONBOARDING-SPEC-DEFINITIVE.md.
Used Playwright + raw HTML inspection. Did NOT submit real payments.

## Critical Findings

### 1. /insiders/awakened/ -- HTTP 404 (PAGE MISSING)
- URL: https://purebrain.ai/insiders/awakened/
- Local source exists at exports/cf-pages-deploy/insiders/awakened/index.html
- BUT: not deployed to production (returns 404)
- Likely cause: deployed to staging only, not purebrain-production (per Apr 15 incident pattern)
- BOOP context flagged this as "silently rotting to homepage clone" -- it's actually 404 now

### 2. /insiders/ -- WRONG PRICING + WRONG PLAN ID (CONSTITUTIONAL VIOLATION)
- Spec requires: Awakened $149.00, plan P-2SA65600MT088594TNGLTFKY
- Live serves: Awakened $74.50, plan P-8AU4270420374002JNGY3VYQ
- Visual price shown: $74 ("pricing-card__amount")
- This is a real-money page using a non-spec PayPal subscription plan
- Spec section 4 violation
- This means actual customers paying through /insiders/ are being charged HALF and routed to a non-canonical plan

### 3. /insiders/pay-test-awakened/ -- FORBIDDEN POST-PAYMENT CHATBOX MARKERS
- launchPostPaymentFlow: PRESENT (must be REMOVED per spec section 16 + Rule 5)
- _postPaymentLaunched: PRESENT (must be REMOVED)
- postPaymentOverlay: absent (good)
- fireSeed: NOT PRESENT in HTML (concerning -- seed flow may be broken on this page)
- /thank-you/ redirect: present (good)
- Pricing + plan IDs: correct ($149, P-2SA65600...)

### 4. /pay-test-sandbox-5/ -- INCOMPLETE
- No PRICES object, no PLAN_IDS, no /thank-you/ redirect, no fireSeed
- Listed in spec section 1 sandbox pages but appears non-functional / placeholder

## Verified Clean (PASS)

- / (homepage): PRICES correct, PLAN_IDS correct, /thank-you/ redirect present, fireSeed present
- /live/: same as homepage, clean
- /awakened/, /partnered/, /unified/: PRICES + PLAN_IDS correct
- /home-test/: clean ($149, correct plan IDs)
- /home-test-sandbox/: $149 prices correct, PLAN_IDS empty (sandbox = uses one-time flow per spec note)
- /pay-test-sandbox-3/: $149 prices, PLAN_IDS empty (sandbox)
- /home-test-live-1/: $1.00 across tiers (per spec -- "$1 one-time test"), PLAN_IDS empty
- /thank-you/: parses URL params, polling logic present, magic-link wiring confirmed

## Console / Asset Issues (informational, not failures)
- /awakened/, /partnered/, /unified/, /insiders/ all reference wp-emoji-release.min.js -> 404 (legacy WP artifact, not a constitutional fail)
- R2 video assets PureResearch.ai-1.mp4 + Pure-Brain-Demo-Video-real-compression-and-sizing.mp4 -- ERR_ABORTED on every page (likely due to network-idle wait cancelling video preload, not server-side error -- worth follow-up but not blocking)

## Test Methodology
- Playwright headless chromium, 30s page load + networkidle wait
- Validated: PRICES JS object, PLAN_IDS JS object, /thank-you/ redirect string, fireSeed reference, forbidden post-payment markers, consent checkbox pre-checked, HTTP status, console errors, failed requests
- Initial visible-price check produced false positives (prices hidden behind naming chatbox per spec) -- pivoted to HTML source inspection of PRICES/PLAN_IDS objects which is the constitutional source of truth

## Files
- Test runner: /tmp/nightly-onboarding-qa/qa_runner.py
- Results JSON: /tmp/nightly-onboarding-qa/results.json
- Screenshots: /tmp/nightly-onboarding-qa/*.png

## Drift Response Required
- 1 critical pricing/plan drift on /insiders/ -> alert Jared, route to ST# for fix (NEVER auto-fix pricing per nightly guard rules)
- 1 missing page on /insiders/awakened/ -> route to ST# for redeploy to purebrain-production
- 1 forbidden post-payment markers on /insiders/pay-test-awakened/ -> route to ST# for cleanup
- This crosses the "3+ failures" threshold per NIGHTLY-ONBOARDING-GUARD.md -> alert Jared urgently
