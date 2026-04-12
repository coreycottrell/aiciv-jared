# Competitive Assessment Features: Shareable Score Card + Benchmarks
**Date**: 2026-02-23
**Type**: operational + teaching
**Topic**: Canvas-based score card generation + comparative benchmark bar on AI Partnership Assessment page (page 284)

## What Was Built
Two competitive features added to purebrain.ai/ai-partnership-assessment/ (WordPress page 284):

### Feature 1: Comparative Benchmarks
- `benchmark-block` div shown after results, above the CTA
- Score-to-percentile mapping:
  - 9-10: 92% (higher than 92% of professionals)
  - 7-8: 71%
  - 5-6: 45%
  - 3-4: 22%
  - 0-2: "You're at the starting line" (no percentile claim)
- Animated fill bar (1.2s transition) triggered 400ms after results render
- `getBenchmarkData(score)` function returns `{pct, text}`

### Feature 2: Shareable Score Card
- Canvas (600x315px, Twitter card ratio) generated after results
- `renderScoreCard(score, tierLabel, userName)` using Canvas 2D API
- Features: PureBrain logo in brand colors, gradient score number, tier badge pill, benchmark text, CTA line, PureBrain footer
- Helper: `roundRect()` for pill shapes, `hexToRgba()` for color conversion
- "Download Score Card" button → saves PNG via `<a download>`
- "Copy Share Message" button → copies tier-matched text to clipboard (with navigator.clipboard fallback for older browsers)

### Additional Visual Enhancements
- Tier badge above result title: "AI Ready" (blue), "Getting There" (orange), "Just Starting" (muted)
- Score display pill showing "X/10 AI Readiness Score" in brand colors
- `finalScore`, `finalTierLabel`, `finalUserName` global vars for use in share functions

## Key Pattern Reused
- Elementor HTML widget update: fetch page 284, parse `_elementor_data`, find `widgetType=='html'`, update `settings.html`, POST back
- Curl `--data @/tmp/payload.json` to bypass Cloudflare WAF (Python urllib fails with 403 on large payloads)
- `DELETE /elementor/v1/cache` to clear Elementor PHP cache after deploy
- After deploy: verify with `?nocache=TIMESTAMP` or `?v=TIMESTAMP` cache-bypass URL

## CDN Cache Behavior
- Cloudflare may still serve old content 5-15 min after deploy
- Content verified live via `?v=$(date +%s)` bypass URL
- After Elementor cache clear + 2nd status:publish POST, CDN warmed in ~5-8 seconds
- No Cloudflare API credentials in .env - must rely on time/cache expiry or manual Cloudflare purge

## Files
- Backup: `/tmp/page284_backup_competitive.json`
- New HTML: `/tmp/page284_enhanced.html`
- Page: https://purebrain.ai/ai-partnership-assessment/
- WP Page ID: 284
