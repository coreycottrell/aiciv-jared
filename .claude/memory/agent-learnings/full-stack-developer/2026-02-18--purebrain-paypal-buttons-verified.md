# PayPal Buttons Verification - purebrain.ai/purebrain-3

**Date**: 2026-02-18
**Type**: operational
**Topic**: PayPal buttons verified working on purebrain-3 page

---

## Summary

Verified all 3 PayPal purchase buttons on purebrain.ai/purebrain-3 (page ID: 338).

## Findings

All 3 PayPal forms are present, correctly configured, and use proper HTML form POST approach.

### Tier 1: Awakened
- Amount: $79.00 USD
- item_name: Pure Brain Awakened
- item_number: PB-AWAKENED
- Button text: "Get Started"
- Button class: pricing-card__cta--secondary

### Tier 2: Bonded
- Amount: $149.00 USD
- item_name: Pure Brain Bonded
- item_number: PB-BONDED
- Button text: "Activate Now"
- Button class: pricing-card__cta--primary (featured/highlighted)

### Tier 3: Partnered
- Amount: $499.00 USD
- item_name: Pure Brain Partnered
- item_number: PB-PARTNERED
- Button text: "Get Started"
- Button class: pricing-card__cta--secondary

### Common Configuration (all 3)
- Form action: https://www.paypal.com/cgi-bin/webscr
- Method: POST
- Target: _blank (opens PayPal in new tab)
- Business email: support@puremarketing.ai
- Return URL: https://purebrain.ai/thank-you/
- Cancel return: https://purebrain.ai/purebrain-3/
- No shipping: 1

## How to Verify

```bash
curl -s -u 'Aether:FlFr2VOtlHiHaJWjzW96OHUJ' \
  'https://purebrain.ai/wp-json/wp/v2/pages?slug=purebrain-3&_fields=id,slug,content' \
  | python3 -c "
import json, re, sys
data = json.load(sys.stdin)
forms = re.findall(r'<form[^>]*paypal[^>]*>.*?</form>', data[0]['content']['rendered'], re.IGNORECASE | re.DOTALL)
print(f'Found {len(forms)} PayPal forms')
"
```

## Reference Page (purebrain-2-0)
- Page ID: 174
- Also has PayPal buttons (4 forms: Starter, Pro, Enterprise, Ultimate - different tier naming)
- The purebrain-3 buttons match the spec exactly (3 tiers, correct business email, correct return URL)
