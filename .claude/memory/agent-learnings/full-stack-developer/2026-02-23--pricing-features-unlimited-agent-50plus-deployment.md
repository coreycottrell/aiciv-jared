# Pricing Feature Update: Unlimited Agent Creation + 50+ Agent Simultaneous Deployment

**Date**: 2026-02-23
**Type**: operational
**Topic**: Adding two key differentiator features to all pricing pages on purebrain.ai

## What Was Done

Updated all pricing pages to replace the old single feature "Unlimited agents: 10 running simultaneously" with TWO separate features:
1. "Unlimited agent creation"
2. "50+ agent simultaneous deployment"

These features are shown in the Awakened ($79) tier. Higher tiers inherit them.

## Pages Updated

| Page | ID | Method | Notes |
|------|-----|--------|-------|
| Homepage (pure-brain-agentic-ai-partner) | 11 | Elementor meta + raw content | 5 occurrences each (4 blue + 1 orange) |
| pay-test | 439 | Elementor meta + raw content | 5 occurrences each |
| pay-test-sandbox | 468 | Elementor meta + raw content | 5 occurrences each |
| pay-test-2 | 689 | Elementor meta + raw content | 5 occurrences each |
| pay-test-sandbox-2 | 688 | Elementor meta + raw content | 5 occurrences each |
| purebrain-2-0 | 174 | Elementor meta + raw content | 5 occurrences each |
| purebrain-4 | 383 | Elementor meta only | Different structure - replaced "10 specialist agents" + "Limited autonomous workflows" |

## Pages Checked - No Changes Needed
- Assessment page (403): Pricing in description-only form, no feature bullets
- Thank-you page (309): No pricing features
- Competitor exodus pages (752-760): No pricing features in WP data
- Competitor exodus HTML files (exports/): No pricing mentions
- Calculator (exports/ai-tool-stack-calculator-v3.html): Updated "10 AI agents" to include both features

## Critical Technical Pattern

**Elementor pages have TWO storage locations that must BOTH be updated:**
1. `meta._elementor_data` - The Elementor JSON (text is JSON-escaped with `\\"`)
2. `content.raw` - The WordPress post content (plain HTML)

If you only update `_elementor_data` and not `content.raw`, the page will still show old text in some render paths. Always update BOTH.

**The update method:**
```python
# Update Elementor data
requests.put(f'{BASE_URL}/{page_id}', auth=AUTH, 
    json={'meta': {'_elementor_data': new_elementor_data}})

# Update raw content separately  
requests.put(f'{BASE_URL}/{page_id}', auth=AUTH,
    json={'content': new_raw_content})
```

## Color Variants in Pricing Cards

The pricing pages use TWO color variants for feature list items:
- `pricing-card__feature--blue` (Awakened, Partnered, Unified tiers)
- `pricing-card__feature--orange` (Bonded/featured tier)

Both variants must be updated independently when changing feature text.

## Old vs New Text

Old: `Unlimited agents: 10 running simultaneously` (single feature)
New: Two features:
- `Unlimited agent creation`
- `50+ agent simultaneous deployment`

## Verification Steps

After update, always verify:
1. Both features appear in `meta._elementor_data`
2. Both features appear in `content.raw`
3. Old text is gone from both locations
4. Clear Elementor cache: `DELETE /wp-json/elementor/v1/cache`
5. Live HTTP check: `curl -s "https://purebrain.ai/" | grep "Unlimited agent creation"`
