# WordPress Page Cloning via REST API

**Date**: 2026-02-22
**Type**: teaching
**Topic**: How to clone Elementor pages via WordPress REST API

---

## What Worked

### Steps to Clone a WordPress/Elementor Page

1. **Find source page IDs**:
   ```bash
   GET /wp-json/wp/v2/pages?per_page=100&search=SLUG&context=edit
   ```

2. **Fetch full source page** (must include `context=edit` to get raw meta):
   ```bash
   GET /wp-json/wp/v2/pages/PAGE_ID?context=edit
   ```
   Key fields to extract:
   - `content.raw` - the rendered HTML
   - `meta._elementor_data` - Elementor JSON (large string, ~400K chars)
   - `meta._elementor_edit_mode` - always "builder"
   - `template` - must be "elementor_canvas" for no header/footer

3. **POST clone** with exact same meta:
   ```python
   clone_data = {
       'title': 'New Page Title',
       'slug': 'new-slug',
       'content': content_raw,
       'template': 'elementor_canvas',
       'status': 'draft',  # always draft first
       'meta': {
           '_elementor_data': elementor_data,
           '_elementor_edit_mode': 'builder',
           '_elementor_template_type': 'wp-page',
       }
   }
   requests.post('/wp-json/wp/v2/pages', auth=auth, json=clone_data)
   ```

4. **Clear Elementor cache** after creation:
   ```bash
   DELETE /wp-json/elementor/v1/cache
   ```

### Auth
- Auth: `('Aether', PUREBRAIN_WP_APP_PASSWORD)` from .env
- App password works for both GET (context=edit) and POST

---

## Pages Cloned This Session

| Source | Source ID | Clone | Clone ID | Status |
|--------|-----------|-------|----------|--------|
| pay-test-sandbox | 468 | pay-test-sandbox-2 | 688 | draft |
| pay-test | 439 | pay-test-2 | 689 | draft |

- Elementor data sizes: 425,699 chars and 423,284 chars - both copied exactly
- Preview via `?page_id=688` and `?page_id=689`

---

## Gotcha: 404 on POST

If you get `rest_no_route` 404 on POST, check that `base` variable doesn't have `/pages` appended twice. Common mistake: setting `base = 'https://...wp-json/wp/v2'` then doing `requests.post(base, ...)` vs `requests.post(f'{base}/pages', ...)`.

---

## What Was NOT Needed

- `_elementor_page_settings` was NULL on both source pages - not required for clone
- Yoast SEO meta not copied (not needed for functional clone)
