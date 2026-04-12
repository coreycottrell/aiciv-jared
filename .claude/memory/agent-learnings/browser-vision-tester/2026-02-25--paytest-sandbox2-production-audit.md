# Memory: Pay-Test Sandbox-2 + Pay-Test-2 Visual Audit
**Date**: 2026-02-25
**Type**: operational + teaching
**Topic**: Comprehensive visual audit of pages 688 (sandbox) and 689 (production) — Feb 25 run

---

## Summary

Full visual audit of both pay-test pages. Both pages are in good shape. One broken image found on both.

---

## Key Findings

### 1. Both Pages Pass All Core Checks
- HTTP 200, not blank, correct branding, chat flow works, PayPal SDK loaded
- Mobile fully responsive at 375px (no horizontal scroll)
- PUREBR[blue]AI[orange]N[blue] branding correct on all instances

### 2. One Broken Image (Both Pages)
- URL: `https://purebrain.ai/wp-content/uploads/2026/02/MA1.BI-1.2.6-001-211107-Side-by-Side-Main-Orange-PT-scaled.png`
- This file is missing from the server — returns broken image on both pages
- Action: Re-upload to WP media at that exact path

### 3. Pricing Section Status (Expected)
- 5 cards confirmed: Awakened $79, Bonded $149, Partnered $499, Unified $999, Enterprise Custom
- `display: none` is CORRECT — JS reveals it after chat flow completes
- PayPal SDK loads with different client IDs (sandbox vs production) — correct

### 4. Console Errors (Pre-existing, Non-blocking)
- "SCC Library has already been loaded" — both pages, cosmetic duplicate script
- WonderPush mutex timeout — sandbox only, push notification library, no user impact
- No new console errors introduced since last audit

### 5. Sandbox Banner Confirmed Visually
- DOM script detection found false positive (found "SANDBOX" text in JS variable)
- Visual screenshot confirms orange "SANDBOX MODE - No real charges" bar IS rendering at top
- Test script needs to check for visible DOM text nodes, not innerHTML of `<html>`

---

## Test Configuration That Worked

- Single browser instance, reusing WP cookie between both pages (password set once)
- 20-second pause between desktop pages
- 30-second pause before mobile tests
- No WAF block encountered
- Browser args: `--no-sandbox --disable-dev-shm-usage`
- User agent: Chrome 121 Windows NT

---

## Selector Reference (Still Valid)

- Password field: `input[id^="pwbox-"]`
- Begin button: `.chat-initial__btn`
- Chat input: `#userInput`
- Pricing section: `.pricing-section`
- Pricing cards: `.pricing-card`

---

## Files

- Report: `exports/paytest-audit-report-20260225.md`
- Screenshots: `exports/screenshots/paytest-audit-20260225/` (14 files)
- Raw JSON: `exports/screenshots/paytest-audit-20260225/raw_results.json`
- Test script: `tools/audit_paytest_20260225.py`
