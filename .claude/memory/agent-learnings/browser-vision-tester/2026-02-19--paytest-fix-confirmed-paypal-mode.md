# pay-test Fix Confirmed: Buttons Now Call openPayPalModal

**Date**: 2026-02-19
**Type**: operational + technique
**Topic**: Confirmed openPayPalModal fix applied to purebrain.ai/pay-test/ pricing buttons

---

## What Changed

Between the morning test and afternoon verification:
- BEFORE: All 5 buttons called `openWaitlistModal()` (waitlist mode)
- AFTER: 4 payment tier buttons call `openPayPalModal()`, Enterprise correctly calls `openWaitlistModal()`

## Current Button State (Verified)

```
Awakened  ($79)  -> openPayPalModal('Awakened')   [FIXED]
Bonded    ($149) -> openPayPalModal('Bonded')      [FIXED]
Partnered ($499) -> openPayPalModal('Partnered')   [FIXED]
Unified   ($999) -> openPayPalModal('Unified')     [FIXED]
Enterprise       -> openWaitlistModal('Enterprise') [Correct - sales flow]
```

## Page Password Form Submission (CRITICAL TECHNIQUE)

The pay-test page requires a WordPress page password. The form structure:
- Form class: `post-password-form`
- Form action: `https://purebrain.ai/wp-login.php?action=postpass`
- Password field: `#pwbox-439` (input type=password, name=post_password)
- Submit: `input[type="submit"]` with value "Enter"

**CORRECT submission method** (JS form.submit() - bypasses visibility issues):
```python
page.fill('#pwbox-439', PAGE_PASSWORD)
page.evaluate("() => { var f = document.querySelector('.post-password-form'); if (f) f.submit(); }")
time.sleep(5)  # Wait for redirect
```

**WRONG methods that fail**:
- `submit.click()` - Playwright timeout (element "not visible")
- `querySelector('button')` - finds site search button instead of Enter button
- `querySelector('input[type=submit], button[type=submit]')` - works in code but Playwright click fails

## PayPal Modal in Headless

When `openPayPalModal('Awakened')` is called in headless Playwright:
- `#pb-paypal-modal`: visible (display changes from none to block)
- Tier name: "Pure Brain" (not "Pure Brain -- Awakened") - needs conversation context to set
- Price: "$0/mo" - needs conversation context to set dynamic pricing
- PayPal Zoid button: DOES NOT render in headless (requires GPU)

**In real browser**: Modal shows correct tier/price, PayPal Subscribe button renders (confirmed in paypal_modal_awakened.png)

## GoDaddy Rate Limiting

After 3-4 rapid page loads with automated traffic:
- Returns 429 error
- Shows "Please verify you are human" CAPTCHA page
- Resolution: Wait 5-10 minutes before retrying

Best practice: Keep test runs to 1-2 passes, not repeated rapid runs.

## Exit Popup

- Element: `#exitPopup` with class `exit-popup`
- Trigger: `mouseout` on document with `clientY < 10`
- Guard: `state.exitIntentEnabled` must be `true` (only set after conversation completes)
- Session guard: `sessionStorage.exitPopupShown` prevents repeat

## Files

- Verification report: `/home/jared/projects/AI-CIV/aether/exports/paytest-paypal-verification-report-2026-02-19-fresh.md`
- Test script: `/home/jared/projects/AI-CIV/aether/tests/test_paytest_final_verify.py`
- Screenshots: `/home/jared/projects/AI-CIV/aether/tools/screenshots/paytest-verify-v2/`
- Key screenshot (PayPal works): `tools/screenshots/paytest-pricing-buttons-2026-02-19/paypal_modal_awakened.png`

---

**Tags**: purebrain, pay-test, paypal, openPayPalModal, fix-confirmed, page-password, form-submit, rate-limiting
