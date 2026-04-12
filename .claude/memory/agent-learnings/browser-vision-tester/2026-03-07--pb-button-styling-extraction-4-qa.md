# pb-button-styling Plugin Extraction QA — #4

**Date**: 2026-03-07
**Type**: operational
**Topic**: QA results for security plugin extraction of button hover CSS into standalone plugin

## Context

Extraction #4 moved `pb-button-hover-v622` (button hover CSS) from the security plugin into a new standalone plugin called `pb-button-styling`. QA was run to confirm nothing broke.

## Results

11/12 PASS. 1 apparent FAIL was a wrong URL in the checklist (not a site regression).

### Key Findings

- `pb-button-hover-v622` style tag IS present on homepage — extraction succeeded
- Style tag ID pattern: `pb-button-hover-v622` found but `pb-button-hover-v622-css` (WP enqueue suffix) NOT found in source — style is being output inline or via a different ID convention
- REST API working: `/wp-json/wp/v2/posts` returns valid JSON
- Admin login accessible (redirects to wp-login.php, not blocked)
- Mobile video CSS (`pb-video-handler-css`) and JS (`pb-video-mobile-pause`) both present — no regression
- 301 redirect: `/ai-adoption-assessment` → `/ai-partnership-assessment/` working correctly
- Sandbox-3, Pay-test-2, Homepage, Blog listing all 200 OK

### Blog Post URL Note

QA checklist used slug `the-age-of-ai-agents-is-here` — this 404s (post doesn't exist at that slug).
Correct slug is `the-age-of-ai-agents` → returns 200. Pre-existing URL issue, NOT caused by extraction.

## Patterns for Future QA

- Always verify blog post slugs via REST API before hardcoding in QA scripts:
  `curl "https://purebrain.ai/wp-json/wp/v2/posts?search=keyword&per_page=3"`
- WP enqueue style IDs follow pattern `{handle}-css` — if style is inline (not enqueued via wp_enqueue_style), the `-css` suffix won't appear
- `domcontentloaded` + `?nocache=qa4` is the correct pattern for bypassing CDN cache
- Security plugin integrity tests (REST API + admin access) are fast and reliable smoke tests
