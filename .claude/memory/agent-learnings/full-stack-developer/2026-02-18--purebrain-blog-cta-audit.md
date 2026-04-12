# Memory: purebrain.ai Blog CTA Audit
**Date**: 2026-02-18
**Type**: operational
**Topic**: WordPress REST API blog audit - CTA inventory for purebrain.ai

## What Was Done
Audited all 5 published blog posts on purebrain.ai via WordPress REST API.
Auth: `("Aether", "FlFr2VOtlHiHaJWjzW96OHUJ")` at `https://purebrain.ai/wp-json/wp/v2/posts`

## Key Findings
- 5 total posts (IDs: 381, 316, 373, 172, 98)
- 0 posts use target CTA "Start Your AI Partnership"
- 3 posts use old CTA "Begin the process at PureBrain.ai" (IDs: 381, 316, 98)
- 1 post (ID: 373) is missing ALL CTAs - most urgent fix needed
- 1 post (ID: 172) uses non-standard CTA phrasing "Explore the possibilities"

## Standard CTA Template (target state)
```
Ready to awaken your AI partner? [Start Your AI Partnership](https://purebrain.ai/)

And if this perspective was valuable, [subscribe to our newsletter](URL) where I share insights on building AI relationships every week.
```

## Output Files
- Audit report: `/home/jared/projects/AI-CIV/aether/exports/blog-audit-2026-02-18.md`
- Raw JSON: `/home/jared/projects/AI-CIV/aether/exports/blog-posts-raw.json`

## API Pattern That Works
```python
import requests
auth = ("Aether", "FlFr2VOtlHiHaJWjzW96OHUJ")
resp = requests.get(
    "https://purebrain.ai/wp-json/wp/v2/posts?status=publish&per_page=100&page=1&context=edit",
    auth=auth, timeout=30
)
# Returns full HTML content in post["content"]["rendered"]
# Only 5 posts so no pagination needed (page 2 returns 400)
```

## Dead End Noted
The `context=edit` parameter is required to get full raw content. Without it, some fields are stripped.
