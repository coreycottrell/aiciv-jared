# Calculator Mobile: 3 Layout Fixes (Pills, Personalize Overlap, Footer Overlap)
**Date**: 2026-02-24
**Type**: teaching
**Topic**: Fixed 3 mobile layout issues on purebrain.ai/ai-tool-stack-calculator/ (page 777)

## Problems Fixed

### Issue 1: Preset Pills Stuck at Top of Screen
- **Root cause**: `.calc-presets` used `position: fixed; top: 0` on `@media (max-width: 960px)`
- **Fix**: Changed to `position: static` so pills flow naturally in the DOM — below the hero and personalize sections
- **Removed**: Fixed positioning properties (top, left, right, z-index, backdrop-filter, box-shadow, margin: 0)
- **Kept**: Horizontal scroll (overflow-x: auto, scrollbar-width: none, flex-wrap: nowrap)
- **Also removed**: `padding-top: 60px` from `.calc-wrap` on mobile (was compensating for fixed pills)
- **Also updated**: `adjustMobilePresetPadding()` JS function — made into a no-op since pills are now static

### Issue 2: Personalize Section Overlapping Bottom Bar
- **Root cause**: `.calc-personal-box` (last element in hero) had no bottom clearance for the fixed bottom bar
- **Fix**: Added `margin-bottom: 100px !important` to `.calc-personal-box` on mobile
- **Also**: Added `padding-bottom: 20px !important` override to `.calc-hero` on mobile

### Issue 3: Bottom Bar Overlapping Footer
- **Root cause**: `.calc-bottom-bar` used `bottom: 0` (sits right on viewport bottom), but `#purebrain-legal-footer` (WP plugin footer) appears below the page content
- **Legal footer anatomy**: `padding: 20px 0 24px`, text ~20px = ~64px total height
- **Fix**: Set `bottom: 64px !important` on `.calc-bottom-bar` — raises bar above the legal footer
- **Also**: Increased `body { padding-bottom }` to `150px !important` (72px bar + 64px footer + 14px gap)

## WP Footer Discovery
The `#purebrain-legal-footer` is injected by the purebrain security/legal plugin via `wp_footer` at priority 99.
Even on `elementor_canvas` template pages it appears.
CSS: `padding: 20px 0 24px; background: #0a0a0a`
Total height: ~64px on mobile

## Key Lessons
1. `position: fixed` pills at viewport top = they appear ABOVE everything including headings — bad on mobile
2. When pills become `static`, the JS `adjustMobilePresetPadding()` function should be a no-op (it was adding padding-top to .calc-wrap to compensate for fixed pills — no longer needed)
3. Fixed bars at `bottom: 0` will always collide with WP plugin footers — use a concrete `bottom` offset based on footer's known height
4. `!important` is needed on mobile overrides because existing CSS specificity from the same file can win

## Files Changed
- Source: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- Deployed: WP page 777 via REST API PUT (HTTP 200)
- Elementor cache cleared: HTTP 200
- Live verification: 7/7 meaningful checks PASS

## Verification Evidence
- Live URL: https://purebrain.ai/ai-tool-stack-calculator/
- `position: static` in presets mobile block: PASS
- `bottom: 64px !important` on bottom bar: PASS
- `padding-bottom: 150px !important` on body: PASS
- `margin-bottom: 100px !important` on personalize box: PASS
- `padding-top: 0` on calc-wrap (pills no longer need offset): PASS
- No nested `<html>` tag: PASS
- HTTP 200 on live page: PASS
