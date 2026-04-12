# Memory: pay-test-2 Plugin Rollback QA — Waitlist Modal Overrides PayPal

**Date**: 2026-02-27
**Type**: operational + teaching
**Topic**: PayPal SDK loaded correctly after v4.6.4 rollback, but old waitlist modal JS overwrites openWaitlistModal

---

## Root Cause Pattern: JS Function Name Collision

When two inline scripts define the same function name (`openWaitlistModal`), the LAST definition wins.

On pay-test-2 after rollback:
1. Plugin injects PayPal SDK version of `openWaitlistModal` (renders PayPal Smart Buttons)
2. OLD page HTML contains legacy `openWaitlistModal` function (shows waitlist signup form)
3. The old function wins → waitlist form shows, not PayPal

---

## What Worked vs What Failed

### WORKED (plugin rollback partial success):
- Production PayPal SDK loaded: `https://www.paypal.com/sdk/js?client-id=AWgWN...`
- Production client ID confirmed (not sandbox)
- All DOM elements exist: `#pb-paypal-modal`, `#pb-paypal-buttons-container`
- Console: `[PB PayPal] SDK pre-loaded and ready.`
- Console: `[PB PayPal] openPayPalModal alias set`
- CSP correctly allows `https://www.paypal.com` and `https://*.paypal.com`

### FAILED (JS name collision):
- `openWaitlistModal` = waitlist signup form (Full Name, Email, Rating, Timeline)
- `#pb-paypal-buttons-container` has 0 children
- No PayPal iframes in DOM
- Modal opacity:0 (invisible)

---

## Diagnostic Method That Worked

```python
# Check what openWaitlistModal actually is
fn_src = await page.evaluate("openWaitlistModal.toString().substring(0, 200)")
# Look for 'waitlistForm' (old form) vs 'paypal' (new PayPal version)
```

```python
# Check all PayPal-related globals
plugin_obj = await page.evaluate("""
    Object.keys(window)
    .filter(k => k.toLowerCase().includes('paypal'))
    .reduce((acc, k) => {acc[k] = JSON.stringify(window[k]).substring(0, 200); return acc;}, {})
""")
```

```python
# Find inline scripts that mention paypal
inline_scripts = await page.evaluate("""
    Array.from(document.querySelectorAll('script:not([src])'))
    .map(s => s.textContent)
    .filter(t => t.toLowerCase().includes('paypal'))
    .map(t => t.substring(0, 500))
""")
```

---

## Fix Required

**Option A (Recommended)**: Remove old waitlist modal HTML + JS from pay-test-2 page content in WordPress.
- Delete `#waitlistModal` element
- Delete the old `openWaitlistModal` function definition from page HTML
- Plugin PayPal version will then be the only definition and will win

**Option B**: Script ordering — move plugin PayPal script to load AFTER old waitlist code
- Fragile, not recommended

---

## Key Detection Pattern

If PayPal SDK loads (`www.paypal.com/sdk/js`) but no buttons render:
1. Check `openWaitlistModal.toString()` — does it reference `waitlistForm`? That's the old version.
2. Look for `#waitlistModal` in DOM — if present, old waitlist code is still there
3. Check inline scripts for TWO competing `openWaitlistModal` definitions

---

## Test Files

- QA Script: `tools/qa_paytest2_rollback.py`
- Deep Inspect: `tools/qa_paytest2_deep_inspect.py`
- Screenshots: `docs/rollback-qa/`
- Report: `docs/rollback-qa/ROLLBACK-QA-REPORT.md`

**Tags**: pay-test-2, paypal, production, waitlist, function-collision, rollback, qa
