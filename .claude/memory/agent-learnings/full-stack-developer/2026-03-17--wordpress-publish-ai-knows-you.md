# WordPress Publish: The AI That Knows You Before You Even Speak

**Date**: 2026-03-17
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Publishing markdown blog post to jaredsanborn.com via WordPress REST API

---

## What Was Done

Published blog post "The AI That Knows You Before You Even Speak" to jaredsanborn.com.

- Source markdown: `/home/jared/portal_uploads/from-portal/portal_20260315_162207_the-ai-that-knows-you-before-you-speak-blog-post.md`
- Banner image: `/home/jared/portal_uploads/from-portal/portal_20260315_162207_the-ai-that-knows-you-before-you-speak-blog-post-Newslettersize.jpg`
- Published URL: https://jareddsanborn.com/2026/03/17/the-ai-that-knows-you-before-you-even-speak-2/
- Post ID: 1279, Media ID: 1278

## Tool Used

`/home/jared/projects/AI-CIV/aether/tools/wordpress_publisher.py` — existing tool, programmatic usage via `WordPressPublisher` class.

## Pattern: Markdown → HTML Conversion

Custom inline converter (no external deps) handles:
- `##` → `<h2>`, `###` → `<h3>`
- `---` → `<hr>`
- `**text**` → `<strong>`, `*text*` → `<em>`
- `[text](url)` → `<a href="url">text</a>`
- Numbered lists `1. item` → `<ol><li>`
- Skip H1 (post title), skip front-matter lines (`**By Aether`, `**Category**`, etc.)
- Skip `*[Internal note:` lines

## Credentials (jaredsanborn.com)

`.env` keys: `WORDPRESS_URL`, `WORDPRESS_USER`, `WORDPRESS_APP_PASSWORD`
Auth user ID on site: 2 (jared). Admin user name: jared.

## Workflow

1. `wp.upload_media(image_path, alt_text, caption)` → returns `media_id`
2. `wp.publish_post(title, content_html, status="publish", slug=..., featured_image_id=media_id, categories=[...], tags=[...])` → returns URL

## Gotcha: Slug Collision

The slug `the-ai-that-knows-you-before-you-even-speak` was already taken (a prior draft existed), so WordPress appended `-2`. Result URL had `-2` suffix. Check for duplicates before publishing if exact slug matters.
