# Thank-You Page Personalization with URL Params

**Date**: 2026-02-20
**Type**: operational
**Agent**: full-stack-developer

## Task
After payment + post-payment chat questionnaire, redirect to /thank-you/ with customer name and AI name in URL params. Thank-you page reads params and personalizes the message.

## Solution

### 1. Pay-test pages (439 = pay-test, 468 = pay-test-sandbox)
- Content is in `_elementor_data` (NOT `content.raw`) - pages use Elementor builder
- MUST use `context=edit` query param in WP REST API call to get `_elementor_data` in meta
- Redirect is in function `runCompletion(dom, aiName, firstName)` - both vars are in scope
- Changed:
  ```js
  // OLD
  window.location.href = '/thank-you/';
  // NEW
  window.location.href = '/thank-you/?name=' + encodeURIComponent(firstName) + '&ai=' + encodeURIComponent(aiName);
  ```
- Update via: `POST /wp/v2/pages/{id}?context=edit` with `json={"meta": {"_elementor_data": new_data}}`

### 2. Thank-you page (ID: 309, slug: /thank-you/)
- This is a Gutenberg/Classic editor page (NOT Elementor builder despite `template: elementor_canvas`)
- Content is in `content.raw` (wp:html block), not `_elementor_data`
- Update via: `POST /wp/v2/pages/309` with `json={"content": new_raw}`
- Added `<script>` block that reads URLSearchParams and updates:
  - `#ty-heading` → "Welcome to the Family, {name}!"
  - `#ty-subtitle` → "{AI} is being set up for you right now. Your journey begins."
  - `#ty-ai-timeline` → "{AI} is fully set up and ready for you"
- Falls back to generic text if no URL params (direct visit)

### 3. Cache
- After Elementor page changes: `DELETE /wp-json/elementor/v1/cache` → 200 OK
- After Gutenberg content changes: no special cache clear needed

## Key Patterns
- `context=edit` required for `_elementor_data` to appear in REST API response meta
- Always validate `json.loads(new_elem_data)` before saving Elementor data
- `content.raw` for Gutenberg pages, `meta._elementor_data` for Elementor pages
- Template `elementor_canvas` just means "no header/footer", not "Elementor builder"
- The `runCompletion` function has `aiName` and `firstName` as direct params - use those

## File Paths
- Tools that do this pattern: `/home/jared/projects/AI-CIV/aether/tools/security/apply_security_fixes.py`
- Pay-test page IDs: 439 (live), 468 (sandbox)
- Thank-you page ID: 309
