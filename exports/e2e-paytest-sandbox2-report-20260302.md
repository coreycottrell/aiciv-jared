# E2E Pay-Test-Sandbox-2 Full Flow Audit

**Date**: 2026-03-02
**Tester**: browser-vision-tester
**Page**: https://purebrain.ai/pay-test-sandbox-2/ (Page 688)
**Method**: WP REST API fetch -> local serve (WAF-safe)

---

## Pre-Scan: HTML Analysis

**Page size**: 98,418 chars

### Seed/Webhook Functions Found:
- **fireSeed**: ['function fireSeed', 'fireSeed(', 'fireSeed(']
- **runBirthInit**: ['runBirthInit', 'runBirthInit', 'runBirthInit']
- **WITNESS_WEBHOOK**: ['https://api.purebrain.ai']
- **8099**: ['8099']
- **8200**: ['8200', '8200']
- **104.248**: ['104.248', '104.248', '104.248']
- **portals**: ['runPortalButton', 'runPortalButton', 'runPortalButton']

### Pricing Button onclick Analysis:
- Total buttons with openWaitlistModal: 0
- Using `window.openWaitlistModal` (FIXED): 0
- Using bare `openWaitlistModal` (BUG): 0

---

## Seed Fire Results

**Total seed fires detected**: 0

NO SEED FIRES DETECTED

**Note**: When serving locally, requests to external IPs (104.248.239.98, 178.156.229.207)
may still fire (they go out from the browser, not from the server). If seeds are not firing,
check JavaScript console logs for webhook call attempts.

---

## Console Errors

**Total errors**: 0


## PureBrain Related Console Logs


---

## Screenshots

**Total**: 6 screenshots
**Location**: `/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-paytest-sandbox2-20260302/`

- `001-initial-load.png`
- `002-initial-full-page.png`
- `003-pricing-section-revealed.png`
- `004-payment-modal-state.png`
- `005-final-state.png`
- `006-final-full-page.png`

---

## Network Requests to External Endpoints

**Total external API calls**: 0
