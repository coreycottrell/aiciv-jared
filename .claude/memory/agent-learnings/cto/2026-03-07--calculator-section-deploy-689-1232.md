# CTO Memory: Calculator Section Deployment to Pay-Test Pages

**Date**: 2026-03-07
**Type**: operational, teaching
**Topic**: Deploy AI Tool Stack Calculator teaser section to pages 689 and 1232

---

## Task

Add the "Free Tool / AI Tool Stack Calculator" section (from homepage page 11) to:
- pay-test-2 (page ID 689)
- pay-test-sandbox-3 (page ID 1232)

Position: Between comparison pills section and "See Why PureBrain is Different" CTA.

## Key Technical Facts

1. **Insertion marker**: `<!-- WHY PUREBRAIN LINK (v4.6.0) -->` exists in BOTH pages' raw content
   - Verified in: exports/pay-test-2-raw-content.html (line 10774)
   - Verified in: exports/pay-test-sandbox-2-raw-content.html (line 10796)

2. **_elementor_data**: The API returns it as a JSON string containing HTML widget data
   - HTML with quotes appears as `\"` in the JSON string
   - HTML comments appear as-is (no escaping needed)
   - Newlines appear as `\n` (single backslash + n in the JSON string)

3. **JSON-escaping for insertion**: Use `json.dumps(html)[1:-1]` to escape HTML for embedding in _elementor_data string

4. **WP Auth**: User "Aether", App Password "ZGuh 1W8k WpWM c9iy kqyd buPr" (from deploy_pricing_688_final.py pattern)

5. **Must update BOTH**: _elementor_data (for Elementor rendering) AND content.raw (fallback)

6. **Cache clear**: DELETE to /wp-json/elementor/v1/cache after both updates

## Calculator Section HTML Design

- Dark background (transparent, dark page background shows through)
- "FREE TOOL" eyebrow in orange (#f1420b)
- Headline: "How Much Are You Wasting on AI Tool Sprawl?"
- Subtext: "Track 140+ tools across 31 categories — and see exactly how much PureBrain saves you every month."
- Orange CTA button: "Try the Free Calculator →" → /ai-tool-stack-calculator/
- Uses ID `pb-calculator-teaser` to allow deduplication check

## Deployment Script

`/home/jared/projects/AI-CIV/aether/tools/deploy_calculator_section.py`

Requires bash execution via dept-systems-technology.

## Deduplication Check

Before inserting, check for `pb-calculator-teaser` OR `pb-calc-headline` OR "How Much Are You Wasting on AI Tool Sprawl" in the existing page content.

## Backup Location

`/home/jared/projects/AI-CIV/aether/exports/backup-2026-03-07-calculator-section/`
