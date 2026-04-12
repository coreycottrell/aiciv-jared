# Blog Publish: The AI That Knows You Before You Even Speak

**Date**: 2026-03-17
**Type**: operational
**Topic**: WordPress blog post publishing to jareddsanborn.com — duplicate detection pattern

## What Was Done

Attempted to publish "The AI That Knows You Before You Even Speak" to jareddsanborn.com.

Discovered post was already published as post ID 1273 with correct slug, categories, and featured image.

- Existing Post ID: 1273
- URL: https://jareddsanborn.com/2026/03/17/the-ai-that-knows-you-before-you-even-speak/
- Status: publish
- Featured media: 1272
- Categories: [32, 22, 33]
- HTTP check: 200 OK

New banner uploaded as media ID 1276 (unused — 1273 uses 1272).
Duplicate post 1277 was created then immediately deleted with `?force=true`.

## Key Learning: Check Before Publishing

Before publishing, always check if the post already exists:
```
GET /wp-json/wp/v2/posts?slug={slug}&status=any
```

If a post already exists with that slug, do NOT republish — just return the existing URL.

## Category IDs on jareddsanborn.com (confirmed)

From post 1273:
- Categories: [32, 22, 33] — unknown names, but set by prior publish
- Previously mapped: AI Insights=9, AI Partnership=22, AI Strategy=13

Note: categories [32, 33] may be "AI Memory" and "Business Strategy" added since last mapping.

## Tools Used

- `tools/wordpress_publisher.py upload-media` — uploaded banner
- `tools/wordpress_publisher.py publish` — created (then deleted) duplicate
- `curl -X DELETE .../posts/{id}?force=true` — permanent delete of post
