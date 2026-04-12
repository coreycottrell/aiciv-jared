# Migration Portal Deployment to purebrain.ai/migrate/

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer

## What Happened

Jared reported formatting issues at https://purebrain.ai/migrate/. Investigation found the page didn't exist at all - it was a 404. A draft page (ID 800) with the migrate slug existed but had no content deployed.

## Root Cause

- Draft page ID 800 at slug "migrate" existed with no content
- The migration portal HTML had been built at `/home/jared/projects/AI-CIV/aether/exports/migration-portal.html` but never deployed to WordPress

## Fix Applied

1. Loaded the migration portal HTML from exports directory
2. Built Elementor HTML widget data structure with full HTML (fonts + styles + portal div + JS)
3. Attempted to create new page → got "migrate-2" slug because draft existed
4. Updated the existing draft page (ID 800) instead with the full content
5. Published it with template: elementor_canvas
6. Deleted duplicate page (ID 801 with migrate-2 slug)
7. Cleared Elementor cache

## Key Patterns

- **Slug collision**: If a draft page exists with a slug, creating a new page gets slug-2. Always check `?slug=migrate&status=any` before creating.
- **elementor_canvas template**: Sets `page-template-elementor_canvas` on body class. No `<header>` tag in output = working correctly.
- **HTML widget deployment**: Full standalone HTML goes into `settings.html` inside a `widgetType: html` element.
- **Elementor meta keys needed**: `_elementor_edit_mode: builder`, `_elementor_template_type: wp-page`, `_elementor_data: [JSON string]`

## Files

- Source HTML: `/home/jared/projects/AI-CIV/aether/exports/migration-portal.html`
- WordPress page ID: 800
- URL: https://purebrain.ai/migrate/

## Verification

All 12 portal elements confirmed present in rendered page output.
- Template: elementor_canvas (confirmed via body class)
- No WordPress header in output (confirmed)
- All 4 steps, JS, fonts, JSZip CDN all present
