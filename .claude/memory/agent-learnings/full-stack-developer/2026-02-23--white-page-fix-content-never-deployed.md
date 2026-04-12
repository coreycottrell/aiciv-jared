# White Page Fix: Content Was Never Deployed

**Date**: 2026-02-23
**Type**: operational
**Topic**: WordPress white/blank page root cause - empty content

## Root Cause

Pages 825 and 826 on purebrain.ai were showing blank white pages because the HTML content was **never deployed** to WordPress. The source HTML files existed at `exports/client-marketing/` but were never pushed via the REST API.

- Page template (`elementor_canvas`) was set correctly on both pages
- The magic cursor and body background overrides were already in the HTML files
- Content length via API was literally 0 bytes

## Diagnosis Steps Used

1. `GET /wp/v2/pages/{id}` - check template, status, content length
2. Content length = 0 immediately reveals the problem
3. No need to investigate CSS, elementor data, or theme conflicts

## Fix Applied

```python
# Wrap HTML in wp:html block and POST to the pages API
content = '<!-- wp:html -->' + html_string + '<!-- /wp:html -->'
requests.post(f'{base}/pages/{id}', auth=auth, json={
    'content': content,
    'template': 'elementor_canvas',
    'status': 'draft',  # or 'publish'
    'password': 'duckdive2024'  # for password-protected pages
})
```

## Important: Password-Protected Pages in REST API

When checking content of password-protected draft pages WITHOUT `context=edit`, the REST API returns empty content (by WordPress design - protects the content). ALWAYS use `?context=edit` when diagnosing password-protected pages:

```python
requests.get(f'{base}/pages/825?context=edit', auth=auth)
```

## Pages Fixed

- **Page 825** (client-report-duckdive): Draft, password=duckdive2024, 68KB DuckDive report
- **Page 826** (ai-website-execution): Published live, 37KB PayPal execution services page

## What Was Already Correct (No Action Needed)

- Both pages had `template: elementor_canvas` - CORRECT
- Both HTML files had `body { background: var(--bg-primary) !important; }` - CORRECT
- Both HTML files had magic cursor override CSS - CORRECT
- No Elementor data conflicts (pages had no Elementor data at all)

## Lesson

When a page shows blank/white: **check content length first** via REST API. If 0, the content was never deployed - skip all CSS/template debugging and just deploy the content.
