# Cloudinary Video Migration to WordPress Media Library

**Date**: 2026-02-20
**Type**: operational + teaching
**Agent**: full-stack-developer

## Task Completed

Migrated background and demo video URLs from disabled Cloudinary account to WordPress media library across all 6 purebrain.ai pages.

## Old URLs (Dead - Cloudinary account disabled)

- Background: `https://res.cloudinary.com/dq06qxzhz/video/upload/v1769961538/PureResearch.ai_1_nzlral.mp4`
- Demo: `https://res.cloudinary.com/dq06qxzhz/video/upload/v1770156001/Pure_Brain_Demo_Video_nyjoon.mp4`

## New URLs (WordPress media library)

- Background (WP ID 554): `https://purebrain.ai/wp-content/uploads/2026/02/PureResearch.ai-1.mp4`
- Demo (WP ID 551): `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Demo-Video-real-compression-and-sizing.mp4`

## Pages Updated (All 6)

| Page ID | Name | Result |
|---------|------|--------|
| 11 | Homepage | UPDATED + VERIFIED |
| 174 | PureBrain 2.0 | UPDATED + VERIFIED |
| 338 | PureBrain 3.0 | UPDATED + VERIFIED |
| 383 | PureBrain 4.0 | UPDATED + VERIFIED |
| 439 | pay-test | UPDATED + VERIFIED |
| 468 | pay-test-sandbox | UPDATED + VERIFIED |

Both `_elementor_data` (primary - what renders) and `content.raw` (completeness) updated on each page.

## Auth Gotcha (CRITICAL)

WordPress app passwords must include spaces when passed to Basic Auth.
The `.env` value `FlFr2VOtlHiHaJWjzW96OHUJ` must be passed as `FlFr 2VOt lHiH aJWj zW96 OHUJ`.

Without spaces: 401 `rest_forbidden_context` even for administrator role users.
With spaces: 200 OK, full edit context access.

## Procedure Used

1. Query `GET /wp-json/wp/v2/media?per_page=20&orderby=date&order=desc&media_type=video` to find new video URLs
2. For each page: `GET /wp-json/wp/v2/pages/{id}?context=edit` (with spaced app password)
3. Extract `meta._elementor_data` string
4. `str.replace(OLD_URL, NEW_URL)` - simple string replacement works because URLs aren't JSON-encoded differently
5. `json.loads(new_str)` to validate JSON before saving
6. `PUT /wp-json/wp/v2/pages/{id}` with `{'meta': {'_elementor_data': new_str}, 'content': new_content}`
7. `DELETE /elementor/v1/cache` to clear Elementor's render cache
8. Re-fetch each page and verify new URLs present, old URLs absent

## Teaching

- WordPress app password format: store without spaces, use with spaces in HTTP Basic Auth header
- Simple `str.replace()` is safe for URL replacement in Elementor data - no regex needed
- Always validate JSON with `json.loads()` BEFORE the PUT call
- The `context=edit` parameter is required to get `_elementor_data` in the meta
- Clear Elementor cache AFTER all page updates (one call clears all)
