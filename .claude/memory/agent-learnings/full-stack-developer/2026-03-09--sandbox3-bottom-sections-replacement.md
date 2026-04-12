# Sandbox-3 Bottom Sections Replacement

**Date**: 2026-03-09
**Type**: operational
**Topic**: Replaced old bottom sections on sandbox-3 (page 1232) with homepage versions

## What Was Done

Replaced the bottom sections (Calculator CTA, Compare, Awaken CTA, See Why, Footer) on sandbox-3
(WP page ID 1232) with the newly extracted homepage bottom sections from `/tmp/homepage_bottom_sections.html`.

## Key Technical Facts

- **Page 1232** uses `_elementor_data` meta field (NOT `post_content`) despite task description saying otherwise
- The content lives in: `meta._elementor_data` → `[0].elements[0].settings.html` (single HTML widget inside a container)
- HTML content was 468KB → combined result is 476KB
- Cut point: `\n\n\n\n<!-- Calculator CTA Section -->` at index 457095 in the original HTML
- Everything before that (chatbox, video, pricing, PayPal, scripts) was preserved intact

## Deploy Pattern

```python
# 1. GET current page data
GET /wp-json/wp/v2/pages/1232?context=edit
# Auth: Basic base64("purebrain@puremarketing.ai:APP_PASSWORD")

# 2. Parse elementor data
ed = json.loads(page_data['meta']['_elementor_data'])
html = ed[0]['elements'][0]['settings']['html']

# 3. Find cut point and build new HTML
cut_idx = html.find('\n\n\n\n<!-- Calculator CTA Section -->')
top = html[:cut_idx]
new_html = top + '\n\n\n\n' + new_bottom_sections + '\n\n</body>\n</html>'

# 4. Update widget HTML
ed[0]['elements'][0]['settings']['html'] = new_html

# 5. Deploy
POST /wp-json/wp/v2/pages/1232
body: {"meta": {"_elementor_data": json.dumps(ed)}}

# 6. Clear cache
DELETE /wp-json/elementor/v1/cache
```

## Verification Checks

All passed:
- PayPal sandbox client ID: `AYTFob05DoSn0ZeVtLJ05...` still present
- New bottom section markers: `pb-bottom-sections-vars`, `Compare PureBrain`, `Awaken Your Personal AI Partner`, `purebrain-legal-footer`, `pb-aether-footer`
- Live page serving new content (confirmed via curl on live URL)

## Notes

- Page is password-protected (`PureBrain.ai253443$$`) but WP admin auth bypasses it — no need to include password in GET requests
- The URL-encoded password `%24%24` for `$$` returns "Incorrect post password" even for admin — just omit the password param when authenticated
- `context=edit` is required to get `_elementor_data` in the meta fields
