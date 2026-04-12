# PayPal Sandbox Fix: Page 688 (pay-test-sandbox-2)

**Date**: 2026-03-01
**Type**: gotcha + fix pattern
**Severity**: URGENT - was blocking sandbox payment testing

---

## Problem

Page 688 (pay-test-sandbox-2) was returning HTTP 404 and PayPal sandbox checkout was broken.

Two separate issues discovered:

### Issue 1: Page was in TRASH
- Status: `trash`, slug: `pay-test-sandbox-2__trashed`
- This is why the page was returning 404 completely
- Fix: `POST /wp-json/wp/v2/pages/688` with `{"status": "publish", "slug": "pay-test-sandbox-2"}`

### Issue 2: Production PayPal SDK URL in page content
- `_elementor_data` (496500 chars) contained `https://www.paypal.com/sdk/js` (production)
- Needed to be `https://www.sandbox.paypal.com/sdk/js` (sandbox)
- The `post_content` was NOT what Elementor rendered (see critical rule below)

---

## Critical Rules Confirmed

### Elementor renders from `_elementor_data`, NOT `post_content`
- Page 688 uses `elementor_canvas` template
- `_elementor_data` = 496500 chars (the real content)
- `post_content` = 436082 chars (NOT rendered by Elementor)
- Must update `meta._elementor_data` via REST API, not `content` field
- After updating: MUST clear Elementor cache via `DELETE /wp-json/elementor/v1/cache`

### Page in Trash = 404
- WP trash sets slug to `{slug}__trashed` and returns 404 on all public URLs
- Restore via: `POST /wp-json/wp/v2/pages/{id}` with `{"status": "publish", "slug": "{correct-slug}"}`

---

## Fix Applied

1. Restored page from trash: `POST /wp-json/wp/v2/pages/688` → `{"status": "publish", "slug": "pay-test-sandbox-2"}`
2. Updated `_elementor_data`: replaced `https://www.paypal.com/sdk/js` → `https://www.sandbox.paypal.com/sdk/js`
3. Cleared Elementor cache: `DELETE /wp-json/elementor/v1/cache`

---

## PayPal Sandbox Architecture (Page 688)

- **Sandbox Client ID**: `AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_`
- **PLAN_IDS**: All empty strings → uses `createOrder` (one-time capture), NOT `createSubscription`
- **Plugin override** (`pb-sandbox-override` in wp_footer): Also injects sandbox vars and `createOrder` buttons
- **Production page 689** (pay-test-2): Uses production PayPal SDK, UNTOUCHED

---

## Verification Evidence

- Page 688 live HTTP status: 200
- `sandbox.paypal.com occurrences`: 1 (only sandbox URL present)
- `production www.paypal.com/sdk/js occurrences`: 0 (production URL gone)
- Pricing tiers (Awakened, Bonded, Partnered): all present
- Page 689 live HTTP status: 200, unaffected

---

## Tags
paypal, sandbox, page-688, elementor, trash, rest-api, purebrain
