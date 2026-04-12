# purebrain.ai Speed Audit - 2026-03-12

## Summary
Full speed audit of purebrain.ai conducted. Key architectural facts confirmed.

## Architecture Confirmed
- purebrain.ai = GoDaddy WordPress hosting (NOT this VPS)
- This VPS = portal.purebrain.ai nginx proxy + portal_server.py (port 8097)
- Cloudflare sits in front of both
- CF cache-control: DYNAMIC - no HTML edge caching

## Key Findings

### CRITICAL
1. Admin bar HTML in public pages — WP thinks every visitor is logged in (was exported while logged in). Loads 78 extra wp-includes JS files + Gutenberg block editor on every anonymous page view.
2. Zero Cloudflare HTML caching — max-age=0, must-revalidate, DYNAMIC. Every request hits WP origin.

### HIGH
3. Homepage 674KB HTML, pay-test-2 794KB HTML (blog = 73KB by comparison — much cleaner)
4. Two background videos: 86MB + 70MB from R2, both potentially autoloading
5. Static asset cache only 4 hours (should be 1 year for versioned files)
6. 4 Google Fonts requests loading Roboto/Roboto Slab/Plus Jakarta Sans/Oswald with all weights

### MEDIUM
7. GoDaddy stock photos inline script (60KB) loads on all frontend pages — WP admin only feature
8. Zero WebP images — all PNG and JPG
9. Spirograph PNG loaded 7x on pay-test-2 (likely loop bug)
10. VPS disk at 77% (28/38GB used)

## Performance Numbers
- Homepage TTFB: 0.23s (from VPS — real user will be slower)
- pay-test-2: 0.18s TTFB
- Blog pages: 0.15-0.22s (cleaner, lighter)
- 110 external JS references on homepage and pay-test-2

## Quick Wins (in priority order)
1. Enable Cloudflare Cache Rule for HTML (15 min, 3-5x improvement)
2. Re-export CF Pages while logged OUT (30 min, removes 78 admin JS references)
3. Consolidate Google Fonts to 1 request (30 min, 200-500ms faster render)
4. Video preload=none + poster images (1 hour)
5. wp_dequeue admin-only scripts from frontend (1 hour)

## Report Location
/home/jared/projects/AI-CIV/aether/exports/speed-audit-2026-03-12.md
