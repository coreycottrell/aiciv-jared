# Homepage Clone + Waitlist Pricing Changes

**Date**: 2026-03-01
**Agent**: dept-systems-technology
**Type**: pattern + gotcha

## What Was Done

### Phase 1: Clone homepage to /2
- Homepage is page ID 11, elementor_canvas template
- Clone created as page ID 1128 with password "purebrain2024backup"
- WordPress DOES NOT allow numeric slugs (e.g., "2") via REST API — they conflict with post IDs
- Solution: used `add_rewrite_rule('^2/?$', 'index.php?page_id=1128', 'top')` in plugin v4.7.7
- Deployed plugin via WP admin plugin editor (web login required, not app password)
- Flushed rewrite rules via admin options-permalink.php form submit
- Result: purebrain.ai/2 serves the password-protected clone correctly

### Phase 2: Main homepage modifications
- Only 2 changes made to page 11
- Changes applied to `_elementor_data` at `ed[0]['elements'][0]['settings']['html']` (326k char HTML blob)
- After update: cleared Elementor cache via DELETE /wp-json/elementor/v1/cache

## Key Patterns

### WordPress Numeric Slug Workaround
- Problem: REST API converts slug "2" to "2-2" (collision with post ID namespace)
- Solution: `add_rewrite_rule('^2/?$', 'index.php?page_id={ID}', 'top')` + flush
- flush_rewrite_rules() triggered by hitting options-permalink.php admin page

### Plugin Deployment Pattern
- WP App Password (env: PUREBRAIN_WP_APP_PASSWORD) = for REST API only
- WP Web Password (env: PUREBRAIN_WP_PASSWORD) = for admin panel login
- Plugin file update: POST to /wp-admin/plugin-editor.php with form nonce
- Get nonce from GET /wp-admin/plugin-editor.php?file=...
- Form field names: newcontent, action=update, file, plugin, nonce, Submit

### Finding Elementor HTML Content
- Full page HTML lives in: `elementor_data[0]['elements'][0]['settings']['html']`
- Always use `?context=edit` on REST GET to get meta including _elementor_data
- After modifying: re-serialize to JSON, POST to pages endpoint, clear elementor cache

### Pricing HTML Patterns (for future reference)
- Pricing section: `<section class="pricing-section" id="pricing">`
- Price container end: `</span>\n                    </div>\n                    <ul class="pricing-card__features">`
- Custom/Enterprise: `<span class="pricing-card__custom">Custom</span>\n                    </div>\n                    <ul class="pricing-card__features">`
- CTA buttons: `class="pricing-card__cta pricing-card__cta--secondary"` or `--primary`

## Results
- purebrain.ai/2 = password protected backup of original homepage (ID: 1128, pw: purebrain2024backup)
- purebrain.ai = 5x "NO PAYMENT TODAY" labels + 5x "Reserve Your Spot" buttons
- Verified via live HTTP check AND playwright browser test
- Plugin v4.7.7 deployed (adds rewrite rule for /2)
