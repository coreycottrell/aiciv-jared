# Memory: CTA Link Fix - purebrain-4 to homepage
**Date**: 2026-02-19
**Type**: operational
**Topic**: Replacing all /purebrain-4/ test-page CTA links with correct homepage URLs

## Context
Jared identified that all "Start Your AI Partnership" CTA buttons were pointing to
`/purebrain-4/` (a test/dev page), not the live homepage `https://purebrain.ai/`.
Rule: purebrain-3, purebrain-4, pay-test = test pages only. Public CTAs must point to
homepage, thank-you page, or assessment pages only.

## What Was Done
Wrote and ran `/home/jared/projects/AI-CIV/aether/tools/fix_cta_links.py` to:
1. Fetch all published posts from both sites via WP REST API (context=edit)
2. Scan href values for bad patterns (/purebrain-4/, /purebrain-3/, /pay-test/)
3. Replace with correct UTM-tagged homepage URL
4. Verify each post after update by re-fetching and checking

## Results
- purebrain.ai: 6/6 posts changed and verified (IDs: 480, 381, 316, 373, 172, 98)
- jareddsanborn.com: 1/7 posts changed and verified (ID: 1069)
- 0 errors across both sites

## URL Pattern Used
```
OLD: https://purebrain.ai/purebrain-4/?utm_source=blog&utm_medium=cta&...
NEW: https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content={post_slug}
```

## Key Lessons
- Prior standardization (2026-02-18) had set all CTAs to /purebrain-4/ — that was the wrong target
- The fix is surgical: only href= values matching bad patterns are replaced
- Blog interlinking (/blog/) and newsletter CTAs were correctly left untouched
- /purebrain-4/ appeared on ALL 6 purebrain.ai posts simultaneously (prior standardization applied it uniformly)
- jareddsanborn.com only had 1 post (the newest one) containing a bad link
- Using post slug (from API response `post["slug"]`) gives cleaner UTM content values

## Script Location
`/home/jared/projects/AI-CIV/aether/tools/fix_cta_links.py`

## Report Location
`/home/jared/projects/AI-CIV/aether/exports/cta-link-fix-report.json`

## Auth Pattern (confirmed working)
```python
auth = ("Aether", os.getenv("PUREBRAIN_WP_APP_PASSWORD").strip("'"))
# purebrain.ai → base = "https://purebrain.ai/wp-json/wp/v2"

auth = ("jared", os.getenv("WORDPRESS_APP_PASSWORD").strip("'"))
# jareddsanborn.com → base = "https://jareddsanborn.com/wp-json/wp/v2"
```
