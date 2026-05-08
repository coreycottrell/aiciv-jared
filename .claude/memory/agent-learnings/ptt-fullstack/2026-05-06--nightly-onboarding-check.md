# Nightly Onboarding Check -- 2026-05-06

**Type**: operational
**Topic**: Nightly onboarding verification, 7/8 pages pass, /insiders/ still drifted

## Key Findings

1. All 8 pages verified via local deploy source files (WebFetch blocked by CF 403)
2. /insiders/ STILL has wrong Awakened pricing ($74.50 vs $149) and wrong plan ID -- persistent since May 2
3. /insiders/pay-test-awakened/ forbidden markers CLEANED since May 2 (zero matches)
4. /insiders/awakened/ redirect to /awakened/ working correctly
5. Awakened tier bullet "Up to 50 agent simultaneous deployment" confirmed on /awakened/ page
6. All 3 infrastructure endpoints healthy (PayPal webhook, referrals API, admin API /check-name)

## Methodology Note

WebFetch returns 403 on all purebrain.ai URLs due to Cloudflare bot protection. Used local deploy source file inspection instead. This verifies what was DEPLOYED but not real-time HTTP status. For true HTTP verification, need curl from server or Playwright.
