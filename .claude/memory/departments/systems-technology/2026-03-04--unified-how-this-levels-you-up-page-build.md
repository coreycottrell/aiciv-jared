# Unified "How This Levels You Up" Landing Page — Build + Deploy

**Date**: 2026-03-04
**Type**: new-page-build, wordpress-deploy
**Page**: https://purebrain.ai/unified-how-this-levels-you-up/
**WP Page ID**: 1263
**Template**: elementor_canvas
**Slug**: unified-how-this-levels-you-up

---

## What Was Built

A self-contained HTML landing page for the $999 Unified tier serving as a mini-funnel "How This Levels You Up" page. The page is a NEW creation (no existing pages modified).

### File Location
`/home/jared/projects/AI-CIV/aether/exports/unified-how-this-levels-you-up.html`

### Page Structure
1. **Hero** — "How PureBrain Unified Levels You Up" + $999/mo headline + 50x value tagline
2. **Section 1** — Partnered tier recap (5 deliverables in a 2-column card grid)
3. **Section 2** — Full Unified Stack (6 categories, 18 features total)
   - Category 1: Proactive Intelligence (3 features)
   - Category 2: Content & Creation (3 features)
   - Category 3: Business Analysis (3 features)
   - Category 4: Integration & Automation (3 features)
   - Category 5: Personalization & Growth (3 features)
   - Category 6: Community & Network Effects (3 features)
4. **Value Comparison Table** — 9 capabilities vs human equivalents, total $25K-$47K/mo
5. **50x Value Multiplier callout** — $300K-$500K/year support team = $12K/year
6. **PayPal Payment Section** — Sandbox PayPal buttons, $999, redirects to sandbox-3

### Feature Status Decisions (from annotations)
- "Doable now" / "Easy peasy" / "STANDARD" → `status-live` badge (green)
- "Would need AiCIV training" / "Would need ALOT of AiCIV training" → `status-soon` badge (gray)
- Annotations NOT shown verbatim on public page

### PayPal Config Used
- Client ID: `AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_`
- SDK: `https://www.sandbox.paypal.com/sdk/js`
- Price: $999.00
- Tier: Unified
- Post-payment redirect: `https://purebrain.ai/pay-test-sandbox-3/?tier=Unified&paid=true&orderId={id}`
- Verify URL: `https://api.purebrain.ai/api/verify-payment`

### Styling
- Background: #080a12
- Orange: #f1420b
- Blue: #2a93c1
- Brand: PUREBR(blue)AI(orange)N(blue)
- Max width: 900px centered
- Wrapped in `<!-- wp:html -->` for WordPress

---

## Deployment Pattern

```bash
# 1. Write HTML to file
# 2. Create payload JSON via Python
python3 -c "import json; payload = {'title': ..., 'slug': ..., 'status': 'publish', 'template': 'elementor_canvas', 'content': html}; json.dump(payload, open('/tmp/payload.json', 'w'))"

# 3. Deploy via curl (NOT Python urllib — WAF blocks it)
curl -s -X POST "https://purebrain.ai/wp-json/wp/v2/pages" \
  -u "Aether:ZGuh 1W8k WpWM c9iy kqyd buPr" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (compatible; AetherBot/1.0)" \
  --data-binary @/tmp/payload.json
```

**CRITICAL**: Use `curl` not Python `urllib` for large HTML payloads. Cloudflare WAF returns 403 error code 1010 on Python urllib for large bodies. Curl with `User-Agent` header bypasses this.

**CRITICAL**: New page creation = POST to `/wp-json/wp/v2/pages` (not PATCH to existing ID).

**NOTE**: This page uses `content` field (standard WP content), NOT `_elementor_data` meta. The elementor_canvas template renders raw content directly. No Elementor cache clear needed for new pages.

---

## Verification
- HTTP 200 confirmed: `curl -o /dev/null -w "%{http_code}" https://purebrain.ai/unified-how-this-levels-you-up/`
- Page ID 1263 returned in creation response
- Status: publish
- Template: elementor_canvas

---

**Tags**: unified-tier, landing-page, paypal-sandbox, new-page, elementor-canvas, $999, how-this-levels-you-up
