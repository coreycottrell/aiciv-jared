# Assessment Q6 Text Update + WP Touch Gotcha

**Date**: 2026-02-23
**Type**: gotcha + operational
**Agent**: full-stack-developer

## Task
Update Question 6 text on AI Partnership Assessment page (purebrain.ai, page ID 284).
- Old: "Almost done! Where should we send your personalized results?"
- New: "Almost done! We'll send your personalized AI partnership recommendation based on your score to this email. Takes 10 seconds."

## What Worked
1. GET page with `?context=edit` to get raw content
2. Python string replace on the raw HTML content
3. PUT back via REST API with `{"content": updated_content}`
4. Verify via re-fetch with `?context=edit` checking `.content.raw`

## CRITICAL GOTCHA: "Touch" to bust cache CLEARS content
- Attempting to "touch" page by POSTing `{"content": ""}` to `/wp-json/wp/v2/pages/284` **wiped the content**
- WordPress treats empty string as "clear this field"
- **NEVER use empty string to touch/bust cache**
- Instead: use Elementor cache DELETE endpoint or just wait for Cloudflare TTL
- Recovery: had saved content to `/tmp/page284_updated.txt` before modifying - this saved the day

## Caching Behavior
- WordPress raw content updates immediately (verified via `?context=edit`)
- WordPress rendered content shows old text (server-side cache)
- Live Cloudflare CDN shows old text (31-day max-age, requires Cloudflare dashboard purge)
- `?nocache=timestamp` query param does NOT bypass Cloudflare CDN

## wp:html Wrapper
- Page 284 has raw HTML (DOCTYPE, style blocks, scripts) - needs `<!-- wp:html -->` wrapper
- But WordPress strips it from `content.raw` in API responses - it stores it internally
- The content still renders correctly even when wrapper not visible in raw
- The rendered content being different from raw is expected - WP stores internal format

## File Paths
- Temp backup: `/tmp/page284_raw.txt` (original), `/tmp/page284_updated.txt` (with fix)
- Page: `https://purebrain.ai/ai-partnership-assessment/` (page ID 284)

## Key Pattern
**Always save content to a temp file BEFORE any modifications.** When working with WordPress REST API content edits, treat it like a database transaction - have a rollback plan.
