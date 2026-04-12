# PureBrain 3.0 PayPal Button Integration

**Date**: 2026-02-18
**Type**: operational + teaching
**Agent**: full-stack-developer

## What Was Done

Replaced the three pricing CTA buttons on purebrain.ai/purebrain-3/ (WordPress page ID 338)
with PayPal payment forms. Tiers: Awakened ($79), Bonded ($149), Partnered ($499).

## How the Page Is Structured

- Page ID 338 is an Elementor page
- The Elementor data is ONE container with ONE HTML widget
- The entire page HTML lives inside `_elementor_data[0].elements[0].settings.html`
- This is a 313K+ character HTML document stored as a string in the Elementor JSON

## API Approach That Works

```python
# FETCH with context=edit to get _elementor_data in meta
GET /wp-json/wp/v2/pages/338?context=edit
Auth: Basic (Aether / FlFr2VOtlHiHaJWjzW96OHUJ)

# UPDATE - POST with meta field
POST /wp-json/wp/v2/pages/338
Body: {"meta": {"_elementor_data": "<updated json string>"}}
```

The Application Password (Aether / FlFr2VOtlHiHaJWjzW96OHUJ) works for REST API.
Browser-based login does NOT work because GoDaddy SSO blocks standard form login.

## Cache Clearing

After updating `_elementor_data`, the live site still serves stale HTML from Elementor's file cache.

**Solution that worked**: Send another POST to the page (e.g., `{"status": "publish"}`) to trigger
Elementor to regenerate its cached output. After this second POST, wait 5 seconds, and the live
page reflects the changes.

Endpoints that did NOT work:
- DELETE /wp-json/elementor/v1/cache (returns 404)
- POST /wp-json/elementor/v1/cache (returns 404)
- Browser-based admin AJAX (GoDaddy SSO blocks login)

## Button Replacement Strategy

The old buttons were:
```html
<button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Awakened')">
    Get Started
</button>
```

Replaced with PayPal forms that reuse the same CSS classes so visual style is preserved:
```html
<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display:block;width:100%;">
  <input type="hidden" name="cmd" value="_xclick">
  ...
  <button type="submit" class="pricing-card__cta pricing-card__cta--secondary" style="width:100%;cursor:pointer;">
    Get Started
  </button>
</form>
```

## Verification

Always verify by checking the live page for:
- `paypal.com/cgi-bin/webscr` references (should be 3 for this page)
- Each item number: PB-AWAKENED, PB-BONDED, PB-PARTNERED
- Old `openWaitlistModal()` calls should be gone for replaced tiers

## Tool Location

`/home/jared/projects/AI-CIV/aether/tools/purebrain3_paypal_buttons.py`

## Key Constants

- Page ID: 338 (/purebrain-3/)
- Business email: support@puremarketing.ai
- Return URL: https://purebrain.ai/thank-you/
- Cancel URL: https://purebrain.ai/purebrain-3/
- WP API creds: Aether / FlFr2VOtlHiHaJWjzW96OHUJ
