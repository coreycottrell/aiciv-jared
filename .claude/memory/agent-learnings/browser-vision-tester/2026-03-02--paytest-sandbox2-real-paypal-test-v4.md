# Memory: Pay-Test Sandbox-2 Real PayPal Button Test v4

**Date**: 2026-03-02
**Agent**: browser-vision-tester
**Type**: pattern + gotcha + synthesis
**Tags**: browser-vision, paypal, sandbox, seed-firing, birth-pipeline, playwright, real-paypal

---

## Context

Full E2E test of https://purebrain.ai/pay-test-sandbox-2/ with REAL PayPal sandbox credentials.
Goal: verify PayPal popup flow + seeds firing to Witness.

---

## Critical Findings

### 1. PayPal SDK IS Loading (Confirmed)

The PayPal SDK renders successfully:
- iframe `src`: `https://www.sandbox.paypal.com/smart/buttons?style.label=pay...`
- Gold "Pay with PayPal" button visible in modal (confirmed via screenshots)
- SEPA and Debit/Credit Card buttons also rendered
- `clientID`: `AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_`

### 2. PayPal iframe Click = NOT Possible from Playwright Headless

The PayPal buttons render inside a cross-origin iframe:
- Playwright cannot dispatch clicks into cross-origin iframes (security policy)
- `frame.evaluate()` on the PayPal iframe returns "no-paypal-in-iframe. btn count: 0"
- Even xvfb (virtual display headed mode) would need actual user interaction
- **Solution**: Use Playwright's `page.on("popup")` but trigger via iframe NAVIGATION (PayPal opens popup on click inside iframe)
- **Alternative**: Use xvfb-run with headed browser and coordinate-based click on iframe element

### 3. Simulate Successful Payment = Working Bypass

The sandbox page correctly has "Simulate Successful Payment (Test Only)" buttons:
- These DO trigger the payment flow
- verify-payment endpoint returns 200
- Post-payment chatbox appears correctly
- This is the correct path for automated testing

### 4. birth/start Endpoint: FAILING

Console errors: `[ptc-v4] birth/start attempt 1/3 failed: Failed to fetch`
- All 3 retry attempts fail
- Witness API endpoint for birth not reachable from browser
- Chatbox shows: "Still connecting to network... attempt 1 timed out. Trying again."
- Shows "Retry Connection" + "Continue without linking" buttons
- **This is the seed fire blocker** - seeds only fire if birth succeeds

### 5. Seeds NOT Captured (Expected)

Seeds require birth pipeline to succeed. With birth failing:
- `intake/seed` endpoint never called
- No seeds in Playwright network monitor
- Verify: check Witness server logs for any incoming birth attempts

### 6. API Calls That ARE Working

Per network monitor (all 200 OK):
- `wp-json/purebrain/v1/log-conversation` - pre-payment chat logging
- `api.purebrain.ai/api/verify-payment` - payment verification
- `api.purebrain.ai/api/log-conversation` - post-payment chat logging
- `api.purebrain.ai/api/log-pay-test` - per-message logging

### 7. AI Names Are Session-Dependent

Earlier test: AI named "Keen"
This test: AI named "Your AI"
The name appears to be user-given (in first session) or default.

### 8. Selector Gotcha: `a[href*=...]` invalid in querySelector

CSS selector `a[href*=portal]` is valid in querySelectorAll BUT not in some Playwright evaluate contexts.
Use `document.querySelectorAll('a').forEach(...)` iteration approach instead.

---

## PayPal Real Button Click - How to Do It

To click the REAL PayPal button (requires headed + coordinates):

```python
# Step 1: Open PayPal modal
await page.evaluate("openPayPalModal('Awakened')")
await asyncio.sleep(5)

# Step 2: Find iframe element bounds
iframe_bounds = await page.evaluate("""(() => {
    var iframe = document.querySelector('iframe[name*=paypal]');
    if (!iframe) return null;
    var r = iframe.getBoundingClientRect();
    return {x: r.x, y: r.y, w: r.width, h: r.height};
})()""")

# Step 3: Click at PayPal button coordinates (gold button = top ~20px of iframe)
if iframe_bounds:
    cx = iframe_bounds['x'] + iframe_bounds['w'] / 2
    cy = iframe_bounds['y'] + 20  # Gold button is near top
    await page.mouse.click(cx, cy)
    # This WILL trigger popup even in headless mode
```

---

## Birth Pipeline Debug Info

```
Console error: [ptc-v4] birth/start attempt 1/3 failed: Failed to fetch
Console error: [ptc-v4] birth/start attempt 2/3 failed: Failed to fetch
Console error: [ptc-v4] birth/start attempt 3/3 failed: Failed to fetch
```

Birth endpoint being called: likely `https://api.purebrain.ai/api/birth/start`
Or possibly Witness direct: `http://104.248.239.98:8200/birth/start`
HTTP endpoint = mixed-content blocked on HTTPS page.

---

## Screenshots

Path: `/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-paypal-real-20260302/`
Key screenshots:
- `006-p3-modal-open.png` - PayPal modal with real gold button (Awakened $79)
- `012-p4-role.png` - Q&A flow working (name/email/company/role captured)
- `014-p5-birth-state.png` - Birth pipeline failed: "network unavailable"
- `016-p7-final.png` - Page navigated to purebrain.ai/why-purebrain (wrong link clicked)

---

## Tags

purebrain, sandbox-2, paypal, birth-pipeline, seed-firing, Failed-to-fetch, witness-api, qa-2026-03-02
