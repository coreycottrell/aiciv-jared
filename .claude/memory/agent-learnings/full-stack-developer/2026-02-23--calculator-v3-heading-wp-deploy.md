# Memory: Calculator V3 Heading Update + WordPress Deployment

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer

## What Was Done

1. Updated heading text in `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`:
   - Line 6 `<title>`: Changed to "Free AI Tool Stack Calculator - 140+ Tools | Stop Paying for 31 Categories | PureBrain.ai"
   - Line 8 `og:title`: Changed to "Free AI Tool Stack Calculator - 140+ Tools — How Much Are You Wasting?"
   - Line 13 CSS comment block: Changed to "FREE AI TOOL STACK CALCULATOR - 140+ TOOLS"
   - Line 1443 eyebrow div: Changed to "Free AI Tool Stack Calculator - 140+ Tools"
   - Also updated JS comment block (line ~1676) from V3 naming

2. Deployed to WordPress as new page:
   - URL: https://purebrain.ai/ai-tool-stack-calculator/
   - Page ID: 777
   - Template: elementor_canvas
   - Status: publish (no password protection)
   - Deployed via WP REST API POST to `/wp/v2/pages`
   - Content wrapped in `<!-- wp:html -->` block
   - Used Python urllib for deployment (88KB file, JSON-safe approach)

3. Injected Calculator CTA section into 5 pages via Elementor data:
   - Homepage (ID 11): DONE
   - pay-test (ID 439): DONE
   - pay-test-sandbox (ID 468): DONE
   - pay-test-2 (ID 689): DONE
   - pay-test-sandbox-2 (ID 688): DONE
   - CTA section inserted at position -1 (second to last, above footer section)
   - CTA anchor ID: `pb-calc-cta`

## CTA Section Design

Placed ABOVE the footer (insert at len-1 position in Elementor sections array):
- Dark gradient background matching PureBrain palette
- Blue eyebrow label "Free Tool"
- H2: "How Much Are You Wasting on AI Tool Sprawl?"
- Subtext: "Track 140+ tools across 31 categories..."
- Orange CTA button linking to https://purebrain.ai/ai-tool-stack-calculator/

## Technical Patterns

### Large HTML to WordPress
- Read file in Python, build JSON payload with json.dumps()
- POST to `/wp-json/wp/v2/pages` with `Authorization: Basic base64(user:pass)`
- Wrap content in `<!-- wp:html -->\n[content]\n<!-- /wp:html -->`
- Template `elementor_canvas` = no theme wrapper, full-width

### Elementor Injection
- GET page with `?context=edit` to get `_elementor_data` from `meta`
- Parse JSON string → modify array → json.dumps() → POST back via `meta._elementor_data`
- ALWAYS validate with json.loads(json.dumps(data)) before writing
- Idempotency check: search for unique anchor ID before inserting
- Clear Elementor cache after: `DELETE /wp-json/elementor/v1/cache`

### Cache Behavior
- Cloudflare CDN caches front-end pages; WordPress DB update is immediate
- Verify data was saved by reading back meta via API (not by curl-ing the public URL)
- `has_cta` check against meta is the authoritative verification

## Verification
- Calculator page live: HTTP 200 at https://purebrain.ai/ai-tool-stack-calculator/
- Eyebrow text confirmed in live HTML: "Free AI Tool Stack Calculator &#8211; 140+ Tools"
- All 5 pages: `has_cta=True` confirmed via API meta read-back
- Elementor cache cleared: HTTP 200
