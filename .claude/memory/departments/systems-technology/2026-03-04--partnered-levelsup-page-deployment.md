# Partnered "How This Levels You Up" Page Deployment

**Date**: 2026-03-04
**Agent**: dept-systems-technology
**Type**: deployment

## What Was Built

New standalone landing/mini-funnel page for the $499 PureBrain Partnered tier.

**WordPress Details**:
- Page ID: 1262
- URL: https://purebrain.ai/partnered-how-this-levels-you-up/
- Slug: partnered-how-this-levels-you-up
- Template: elementor_canvas
- Status: publish

**HTML File**: `exports/partnered-how-this-levels-you-up.html`

## Page Structure

1. Hero (title, $25K-$47K value badge, $499 price, tagline, CTA scroll button)
2. Part A: 5 deliverable cards (outcome-focused reframing of Monthly Strategy, Custom Skill, 24/7 Support, Early Access, Quarterly Report)
3. Part B: 6 feature stack categories x 3 features each = 18 total features
4. Value comparison table (human equivalent costs vs $499)
5. PayPal payment section ($499, Partnered tier)
6. After payment: redirect to sandbox-3 with ?tier=Partnered&paid=true&orderId=XXX

## PayPal Integration Pattern

- Uses same sandbox client ID as sandbox-3: AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_
- SDK URL: https://www.sandbox.paypal.com/sdk/js?client-id=...&currency=USD&intent=capture
- Post-payment: pings VERIFY_URL (https://api.purebrain.ai/api/verify-payment) then redirects to sandbox-3
- Redirect format: https://purebrain.ai/pay-test-sandbox-3/?tier=Partnered&paid=true&orderId=XXX
- This offloads chatbox/onboarding logic to sandbox-3 (no duplication of 84K chatbox JS)

## Safety

- ZERO existing pages modified
- New page only
- elementor_canvas template (correct for standalone pages - strips WP theme chrome)
- Self-contained HTML in wp:html block (WP wpautop-safe)

## Key Design Patterns

- Brand: #080a12 bg, #f1420b orange, #2a93c1 blue
- PureBrain wordmark: PUREBR(blue)AI(orange)N(blue)
- CSS vars throughout (--orange, --blue, etc.)
- Responsive grid cards at 640px breakpoint
- All CSS inline in style tag (self-contained)
- No external fonts or dependencies beyond PayPal SDK
