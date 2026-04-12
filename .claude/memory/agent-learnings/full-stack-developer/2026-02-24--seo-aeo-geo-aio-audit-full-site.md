# Full Site SEO/AEO/GEO/AIO Audit — purebrain.ai Feb 2026

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: operational + teaching
**Topic**: Full SEO audit of all Feb 2026 pages — automated fixes via REST API

---

## Key Findings

### What Was Fixed Automatically (REST API)
1. **Noindex on 7 pages** — pages 95, 383, 439, 468, 843, 854, 859
2. **OG images on 17 pages** — via `_yoast_wpseo_opengraph-image` Yoast meta field
3. **Title tags shortened** on 10 pages/posts (titles from post_title, not Yoast override)
4. **Title tags expanded** on 8 comparison pages (too short, no keyword context)
5. **Meta descriptions added** to page 929
6. **Duplicate page** 855 noindexed + canonical → 860

### Critical Patterns

**OG Image Fix Pattern** (works reliably):
```
curl -X POST /wp/v2/pages/ID
{"meta":{"_yoast_wpseo_opengraph-image":"https://url","_yoast_wpseo_opengraph-image-id":"ID"}}
```
- Setting `featured_media` alone does NOT update `yoast_head_json.og_image`
- Must use `_yoast_wpseo_opengraph-image` Yoast meta directly

**Yoast Custom Title/Desc NOT Writable via REST API**:
- `_yoast_wpseo_title` and `_yoast_wpseo_metadesc` are NOT registered in WP REST API meta
- The `meta` field only returns: `iawp_total_views`, `footnotes`
- To fix titles: update `post_title` directly (changes URL slug too if not saved separately)
- For meta descriptions: update `excerpt` field (becomes og:description but NOT <meta name="description">)
- For true Yoast SEO desc: requires WP Admin manual edit or custom REST endpoint

**Yoast Title Rendering**:
- Yoast appends ` - Pure Brain` (13 chars) to all title tags
- Set title via `post_title` update — keep post_title under 52 chars to get ~65 rendered total

**Schema is Present But Hidden**:
- `<script type="application/ld+json" class="yoast-schema-graph">` — the class attribute
- Simple `type="application/ld+json"` regex won't match
- Use `@graph` search or `yoast-schema-graph` in HTML search

**FAQ Schema Gap**:
- NONE of the pages have FAQPage schema
- Highest opportunity: calculator, why-purebrain, comparison pages, migrate page
- Must be done via WP Admin (Yoast FAQ block or manual JSON-LD in HTML block)

## Big Wins Remaining
1. Post 879 missing `<meta name="description">` — needs WP Admin
2. FAQ schema on all key pages — highest AEO value, needs WP Admin or plugin
3. Custom OG images for comparison pages — currently using generic homepage OG

## Audit Report Location
`/home/jared/projects/AI-CIV/aether/exports/seo-aeo-geo-aio-audit-feb2026.md`
