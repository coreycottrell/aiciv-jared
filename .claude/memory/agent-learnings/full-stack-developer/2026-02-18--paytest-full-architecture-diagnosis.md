# Pay-Test Full Architecture Diagnosis & Verified State

**Date**: 2026-02-18
**Type**: teaching + operational
**Agent**: full-stack-developer

---

## The Architecture (Critical to Understand)

The pay-test page (ID 439) has a deeply nested HTML structure due to how GoDaddy+Elementor+WordPress interact.

### Live Page Structure (484K chars):
```
WordPress outer HTML wrapper (Doc 1: pos 0-78875)
└─ elementor-439 div (pay-test's Elementor container)
   └─ Container c4d524c → Widget 292c72a
      └─ Our widget HTML (Doc 2: pos 78875) = HEAD section only (67K CSS)
         ...then the actual body renders as elementor-11 injection...
└─ elementor-11 div (pos 146809) - this is the HOMEPAGE being injected
   └─ Widget 292c72a content (Doc 3: pos 147329) = FULL page content:
      - Hero, About, Capabilities, Pricing sections
      - Chat interface (chatMessages, userInput, submitBtn)
      - Main chat script (56K chars) with DOMContentLoaded wrapper
      - OLD waitlist modal (from embedded snapshot in DB widget)
      └─ After this: WP footer scripts + PAY-TEST SCRIPTS (PayPal + post-payment)
```

### DB Widget Structure (383K chars in _elementor_data):
```
Part A (0-67333): HEAD section (CSS only)
Part B (67333-284150): OLD EMBEDDED SNAPSHOT (captured live page HTML, 216K chars)
   - Contains: hero, about, pricing, chat sections
   - Has: OLD waitlist buttons (onclick="openWaitlistModal()")
   - Has: OLD chat script (with DOMContentLoaded wrapper since we fixed it)
   - Has: elementor-11 reference div → triggers homepage injection by WP
Part C (284150-383288): Footer scripts + PAY-TEST SCRIPTS
   - PAYPAL_CLIENT_ID = 'AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI' (REAL)
   - USE_SDK_APPROACH = true
   - PayPal popup script (30K) - overrides window.openWaitlistModal with PayPal
   - Post-payment chat flow (42K) - exports window.initPayTestFlow
   - Integration glue (3K) - wires payment → post-payment flow
```

## Current Verified State (2026-02-18 ~19:30 UTC)

All these were verified on live page (CF-Cache-Status: MISS = fresh):

| Check | Status |
|-------|--------|
| Real PayPal Client ID | ✓ AWgWNlBQ... |
| USE_SDK_APPROACH = true | ✓ |
| DOMContentLoaded on chat script | ✓ |
| Chat interface (chatMessages, userInput) | ✓ |
| Pricing section with PayPal buttons | ✓ |
| PayPal popup script (overrides openWaitlistModal) | ✓ |
| Post-payment flow (window.initPayTestFlow) | ✓ |
| Integration glue (onPaymentComplete) | ✓ |
| Primary API (api.puremarketing.ai) | ✓ Working |
| Fallback API (purebrain.workers.dev) | ✓ Working |
| Log server (89.167.19.20:8443) | ✓ Health OK |
| Script tags balanced | ✓ 49/49 |

## Key Gotchas

### Why elementor-11 (homepage) renders on pay-test page
The pay-test DB widget HTML (Part B) contains an embedded old page snapshot
that has `<div data-elementor-type="wp-post" data-elementor-id="11">` inside it.
When WordPress renders this widget, it sees the elementor-11 reference and renders
the HOMEPAGE content as an additional section after the pay-test content.

This means:
- Pay-test page renders TWO "full pages" (pay-test content + homepage)
- Some element IDs appear in both (but no functional chat/pricing duplicates)
- Homepage does NOT have PAY-TEST scripts, so they don't double-execute

### Why PAY-TEST SCRIPTS appear to be at two positions
The script appears at positions 385437 AND 462617 in the live page.
385437 = start of PAY-TEST SCRIPTS (in Part C of our widget)
462617 = END of PAY-TEST SCRIPTS (<!-- END PAY-TEST SCRIPTS --> comment)
These are the SAME script block, not a duplicate!

### How PayPal override works
The old snapshot (Part B) has buttons with `onclick="openWaitlistModal('Awakened')"`
The PayPal popup script (Part C) sets `window.openWaitlistModal = function(tier) { PayPal... }`
Since onclick calls are resolved at runtime (not at definition), clicking the old buttons
uses the PayPal override. This works correctly!

## Cache Clearing Sequence That Works

```python
# 1. Delete Elementor PHP cache
requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache", auth=creds)
# Returns: 200 (empty response body)

# 2. Touch page to update modification timestamp
requests.post("https://purebrain.ai/wp-json/wp/v2/pages/439", auth=creds, json={"status": "publish"})
# Returns: 200 with updated page JSON

# 3. Wait 5-10 seconds
time.sleep(10)

# 4. Verify: fetch live page, check CF-Cache-Status: MISS = fresh content
requests.get("https://purebrain.ai/pay-test/", headers={"Cache-Control": "no-cache"})
```

## What "Entire Page Not Working" Likely Means

Based on thorough diagnosis, the page structure is functional but complex.
If Jared sees it "not working" it may be:
1. **Stale Cloudflare cache** (31-day max-age) - fix: touch page + Elementor cache clear
2. **Visual issue with nested HTML** - the page embeds a full HTML doc inside another
   Browsers handle this but CSS from nested `<head>` may not apply consistently
3. **Old snapshot content conflicting** - Part B has OLD waitlist modal competing with PayPal
   The PayPal override WINS but the old modal div is present and might confuse users
4. **PayPal SDK loading** - with USE_SDK_APPROACH=true, PayPal SDK must load from paypal.com
   If blocked by browser/network, falls back to Approach B (form POST) gracefully

## Credentials

```
WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"  # Application password
PUREBRAIN_WP_APP_PASSWORD = 'FlFr2VOtlHiHaJWjzW96OHUJ'  # Same as above
Page ID: 439
```

## Tags

purebrain, pay-test, paypal, elementor, wordpress, architecture, cache, diagnosis, double-rendering
