# Memory: purebrain.ai Broken Link Audit & Fix
**Date**: 2026-03-04
**Agent**: dept-systems-technology
**Type**: pattern + gotcha

---

## What Was Done

Full site-wide broken link audit of purebrain.ai - crawled all 78 published pages/posts, extracted 53 unique navigable internal links, tested all, found and fixed 2 broken links.

## Key Findings

### Site URL Patterns (LOCK THESE IN)
- **Blog posts** live at `/[slug]` NOT `/blog/[slug]`
  - WRONG: `https://purebrain.ai/blog/the-age-of-ai-agents`
  - RIGHT: `https://purebrain.ai/the-age-of-ai-agents`
- **Calculator** slug is `ai-tool-stack-calculator` NOT `calculator`
  - WRONG: `https://purebrain.ai/calculator`
  - RIGHT: `https://purebrain.ai/ai-tool-stack-calculator`

### What Was Broken
Both broken links were on a single page: `investor-intelligence` (Page ID: 1205)
- `/blog/age-of-ai-agents` -> Fixed to `/the-age-of-ai-agents`
- `/calculator` -> Fixed to `/ai-tool-stack-calculator`

### False Positive Pattern
`//fonts.googleapis.com` appears in link extraction because WordPress inserts a `<link rel='dns-prefetch' href='//fonts.googleapis.com' />` tag in every page's `<head>`. This is NOT a navigable link. Skip it in future audits by filtering out `<link rel>` tags vs `<a href>` tags.

## Fix Method

Page 1205 used plain HTML (no Elementor), so fix was:
1. `GET /wp-json/wp/v2/pages/1205?context=edit` to get raw content
2. Apply string replacements to fix the URLs
3. `POST /wp-json/wp/v2/pages/1205` with updated content
4. Verify with second GET call

For Elementor pages, would need to update `_elementor_data` meta field instead.

## Audit Methodology

1. GET all pages and posts via WP REST API (`/wp-json/wp/v2/pages` + `/wp-json/wp/v2/posts`)
2. Extract all `href=` values from rendered HTML
3. Filter: internal only (purebrain.ai), exclude wp-admin/wp-content/wp-json/fonts/feeds/mailto/anchors
4. Test each URL with HTTP GET, check status code
5. For each broken link, find which pages reference it (grep raw/rendered content)
6. Fix by updating `content.raw` via REST API

## Things Checked (Clean)
- /start links: none found (good - no legacy links to dead /start page)
- Compare page links: all healthy
- Graham Martin subpages: all 5 healthy
- Comparison pages (vs-chatgpt etc): all 9 healthy
- Blog post internal links: all healthy

## File References
- Report: `exports/overnight-reports/broken-links-audit-2026-03-04.md`
- Fixed page: `https://purebrain.ai/investor-intelligence/` (Page ID: 1205)
