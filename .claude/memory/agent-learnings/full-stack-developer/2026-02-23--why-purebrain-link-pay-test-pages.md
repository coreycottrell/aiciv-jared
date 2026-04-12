# Why PureBrain Comparison Link - Pay-Test Pages Update

**Date**: 2026-02-23
**Type**: operational
**Topic**: Adding/updating comparison link on all 4 pay-test Elementor pages

## Task Summary

Updated the "See How PureBrain Compares" link on all 4 pay-test pages to match exact HTML spec.

## Pages Updated

| Page ID | Slug | Section ID |
|---------|------|------------|
| 439 | pay-test | why_pb_439 |
| 468 | pay-test-sandbox | why_pb_468 |
| 689 | pay-test-2 | why_pb_689 |
| 688 | pay-test-sandbox-2 | why_pb_688 |

Note: Pages 689 and 688 were found via API search (`/wp/v2/pages?search=pay-test`).

## Key Finding

All 4 pages ALREADY had a why_pb section from a previous deployment. The sections had slightly different styling (padding:30px, margin-top:20px, font-size:15px, background:#080a12, extra font-family). Updated to exact spec:
- padding:24px 20px
- margin-top:16px
- font-size:14px
- transition:color 0.2s
- No background override (transparent)

## Elementor Data Access Pattern

- Must use `?context=edit` query param to get `_elementor_data` in meta response
- `_elementor_data` is NOT exposed in default API response
- Standard POST to `/wp/v2/pages/{id}` with `meta: {_elementor_data: ...}` works for updates
- DELETE `/elementor/v1/cache` returns 200 with empty body (not JSON) - parse error is harmless

## Section Structure (Elementor)

```
section (id=why_pb_{page_id})
  └─ column (id=why_pb_col_{page_id})
       └─ widget (id=why_pb_html_{page_id}, elType=widget, widgetType=html)
            └─ settings.html = "<div>...</div>"
```

## Cloudflare / Python 403 Issue

urllib.request gets 403 from Cloudflare without proper User-Agent.
Fix: Add `'User-Agent': 'curl/7.88.1'` to request headers.

## Cache Clear

After updating _elementor_data, always clear: `DELETE /wp-json/elementor/v1/cache`
This returns 200 with empty body - not JSON, so don't try to parse response as JSON.
