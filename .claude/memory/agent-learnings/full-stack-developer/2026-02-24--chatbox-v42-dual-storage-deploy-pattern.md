# Chatbox v4.2 Deployment - Dual WordPress Storage Pattern

**Date**: 2026-02-24
**Type**: teaching
**Topic**: WordPress Elementor pages store scripts in TWO places - both must be updated

---

## The Root Cause of v4.1 Failing to Deploy

The previous deploy script (`deploy_chatbox_v4.py`) only updated `_elementor_data` (the Elementor JSON meta stored in `wp_postmeta`). It correctly verified v4.2 was in `_elementor_data` after deployment.

BUT WordPress also stores the page content in `wp_posts.post_content` (accessible as `content.raw` via REST API). This "classic" post content had the old v4.1 script with `WITNESS_WEBHOOK_HOST = 'http://104.248.239.98:8099'`.

**How Elementor serves the page**:
- In production: Elementor's JS frontend reads `_elementor_data` → serves v4.2 (correct)
- Via REST API `content.rendered`: WordPress renders `post_content` → served v4.1 (old!)
- Password-protected pages: Cloudflare caches the login wall, not the content

## The Fix

Must update BOTH data stores:
1. `_elementor_data` (meta field) - via `PUT /wp-json/wp/v2/pages/{id}` with `meta: {_elementor_data: ...}`
2. `content.raw` (post content) - via `PUT /wp-json/wp/v2/pages/{id}` with `content: "..."`

## Verification Pattern

After any chatbox deployment, verify against ALL three data sources:
1. `meta._elementor_data` - what Elementor renders in production
2. `content.raw` - the fallback post content
3. `content.rendered` - WordPress-rendered HTML (check script block size > 80KB)

```python
r = requests.get(f'{WP_BASE}/pages/{page_id}?context=edit', auth=AUTH)
page = r.json()
elem_data = page['meta']['_elementor_data']        # Elementor JSON
content_raw = page['content']['raw']               # Post content
content_rendered = page['content']['rendered']     # Rendered HTML
```

## Cloudflare Cache Note

Pages 688 and 689 are password-protected. Cloudflare edge caches the password wall (~120KB page).
The actual page content is only served to authenticated visitors and is ~424KB.
The `CF-Cache-Status: HIT` on the public URL is normal/expected and does NOT indicate the script is wrong.
Elementor cache (`DELETE /elementor/v1/cache`) handles the Elementor-side cache.

## Script Size Reference
- Source JS: 83,003 chars
- In `content.rendered` script block: ~84,928 chars (HTML escaping adds ~2KB)
- Previous v4.1: 79,744 chars (sanitizeText was missing)

## Pages
- 688: purebrain.ai/pay-test-sandbox-2/ (QA/test)
- 689: purebrain.ai/pay-test/ (live)

## Key Security Changes in v4.2
- CRIT-003: `WITNESS_WEBHOOK_HOST` → `'https://api.purebrain.ai'` (was `'http://104.248.239.98:8099'`)
- CRIT-004: `sanitizeText()` helper added, `aiName` sanitized at all entry points
- MED-003: `window.payTestData` removed from global window exports
