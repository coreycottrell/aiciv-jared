# SEO + Schema AIO Update — 3 PureBrain.ai Pages

**Date**: 2026-02-27
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Setting featured_media, Yoast SEO meta, excerpts, and JSON-LD schema on WP pages via REST API

---

## What Was Done

Updated 3 purebrain.ai pages in one deployment run:

| Page | ID | Featured Media | Schema Type |
|------|----|----------------|-------------|
| Tim Cook (`/your-ai-tim-cook/`) | 993 | 997 (amplify-founder) | Service |
| Pitch (`/pitch/`) | 1001 | 999 (vc-hero) | SoftwareApplication |
| Portfolio (`/portfolio/`) | 1006 | 1004 (portfolio-hero) | Service + OfferCatalog |

## Key Pattern: Yoast Meta via REST API (pages use context=edit)

For PAGES (not posts), Yoast meta keys ARE exposed in the REST API when using `context=edit`.
A simple PUT to `/wp-json/wp/v2/pages/{id}` with `meta: { '_yoast_wpseo_title': '...' }` works.

This is different from the previous finding about posts (2026-02-23 memory) which required the custom plugin endpoint.
The difference may be: pages use `register_rest_field` differently, or the Yoast plugin version changed.

**Always verify with a fresh GET after PUT — the returned JSON confirms what actually saved.**

## Fields Set Per Page

Each page received ALL of:
- `featured_media` (integer media ID)
- `excerpt` (plain text, no HTML)
- `meta._yoast_wpseo_title`
- `meta._yoast_wpseo_metadesc`
- `meta._yoast_wpseo_opengraph-title`
- `meta._yoast_wpseo_opengraph-description`
- `meta._yoast_wpseo_opengraph-image` (full URL)
- `meta._yoast_wpseo_opengraph-image-id` (string, not int)
- `meta._yoast_wpseo_twitter-title`
- `meta._yoast_wpseo_twitter-description`
- `meta._yoast_wpseo_twitter-image` (full URL)
- `meta._yoast_wpseo_twitter-image-id` (string, not int)

Note: image-id fields take STRING values (not integers).

## Schema Injection Pattern

Pages end with `<!-- /wp:html -->`. Schema is inserted just before this closing tag.

```python
CLOSING_TAG = '<!-- /wp:html -->'
last_idx = raw_content.rfind(CLOSING_TAG)
new_content = raw_content[:last_idx] + '\n' + schema_block + '\n' + raw_content[last_idx:]
```

Use `rfind` (not `find`) in case there are multiple wp:html blocks — inject before the LAST one.

## Verification

36/36 checks passed across all 3 pages. All meta fields confirmed set via fresh GET.

---

**End of Memory**
