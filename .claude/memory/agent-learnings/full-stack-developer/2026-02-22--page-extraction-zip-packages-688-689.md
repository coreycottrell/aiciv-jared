# Memory: Page Extraction ZIP Packages - Pages 688 & 689

**Date**: 2026-02-22
**Type**: operational
**Topic**: Full code extraction from WP pages 688/689 into handoff ZIP packages for Corey/AICIV

## What Was Done

Extracted ALL code components from two WordPress pages and packaged them as ZIP files for handoff to Corey and A-C-Gee to continue the PureBrain product build.

## Pages Extracted

| Page ID | Slug | ZIP File | Size |
|---------|------|----------|------|
| 688 | pay-test-sandbox-2 | `exports/pure-test-sandbox-2.zip` | 37.7 MB |
| 689 | pay-test-2 | `exports/pure-test-2.zip` | 0.52 MB |

The size difference is because sandbox-2 includes 74 v3 test screenshots (37MB of PNGs).

## What Each Package Contains

- `page{id}_full_api_response.json` - Full REST API response (1.2MB)
- `page{id}_elementor_data.json` - Elementor page builder JSON (440KB)
- `page{id}_rendered.html` - Full rendered HTML (384KB)
- `page{id}_metadata.json` - WordPress metadata (slug, status, template, password)
- `page{id}_all_meta.json` - All WP custom fields (Yoast, Elementor settings)
- `scripts/` - 14 JavaScript files extracted from rendered HTML
- `styles/` - 6 CSS files extracted from rendered HTML
- `elementor-widget-scripts/` - Scripts from Elementor JSON
- `screenshots/` - 74 v3 test screenshots (sandbox only)

## Key Script Identification

| Script Name | Size | What It Is |
|-------------|------|------------|
| `script-01-main-page.js` | 57KB | Pre-payment page JS (canvas, orbs, awakening flow) |
| `script-pay-test-chat-flow-v2.js` | 46KB | POST-PAYMENT CHAT FLOW v2 (questionnaire → curtain → Telegram → Claude Max) |
| `script-paypal-popup-integration.js` | 31KB (sandbox) / 31KB (live) | PayPal SDK integration |
| `script-integration-glue.js` | 4KB | Wires PayPal success → chat flow launch |

## Extraction Pattern Used

```python
# Fetch page
curl -s -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" \
  "https://purebrain.ai/wp-json/wp/v2/pages/{id}?context=edit"

# context=edit is REQUIRED to get password field and _elementor_data in meta

# Extract scripts via regex
script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL)

# Elementor data is in page_data['meta']['_elementor_data'] as JSON string
elementor_data = json.loads(page_data['meta']['_elementor_data'])
```

## Gotcha: Metadata Size Bug

The `extract_metadata()` function initially included `meta._elementor_data` (440KB) in the metadata file, making it 466KB instead of 1KB. Fixed by explicitly excluding `_elementor_data` from the metadata extract.

## Architecture Summary (for Corey/AICIV)

```
User → pre-payment page (57KB main JS)
     → PayPal popup (31KB)
     → onPaymentComplete() callback (4KB glue)
     → initPayTestFlow() (46KB v2 chat flow)
     → Questionnaire → Curtain → Telegram → Claude Max → Complete
```

## CSS Variables Required
```css
--bright-orange: #f1420b
--light-blue: #2a93c1
--dark: #0a0a0a
```

## File Paths
- Sandbox-2 package dir: `exports/package-sandbox-2/`
- Test-2 package dir: `exports/package-test-2/`
- Sandbox ZIP: `exports/pure-test-sandbox-2.zip`
- Test-2 ZIP: `exports/pure-test-2.zip`
