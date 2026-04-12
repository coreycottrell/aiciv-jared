# Blog Publish: The Meeting Your AI Should Already Know About

**Date**: 2026-03-14
**Type**: operational
**Topic**: WordPress blog post publishing to jaredsanborn.com

## What Was Done

Published blog post "The Meeting Your AI Should Already Know About" to jaredsanborn.com.

- Post ID: 1260
- URL: https://jareddsanborn.com/2026/03/14/the-meeting-your-ai-should-already-know-about/
- Status: published
- Featured media ID: 1259
- Categories: AI Insights (9), AI Partnership (22)

## Patterns Used

- Used `tools/wordpress_publisher.py` CLI for all operations
- Upload media first → get media_id → use in publish command
- Credentials in `.env`: `WORDPRESS_URL`, `WORDPRESS_USER`, `WORDPRESS_APP_PASSWORD`
- Note: WORDPRESS_URL is `jareddsanborn.com` (double-d) — this is correct
- `markdown` Python module not available; wrote pure Python inline conversion instead
- The H1 title should be stripped from HTML content — WordPress uses the `--title` flag separately

## Markdown Conversion Approach

Since `markdown` module and `pandoc` were unavailable, used a pure Python line-by-line parser:
- Strip H1 (title handled by WP)
- Convert `## ` headers to `<h2>`
- Convert `---` to `<hr />`
- Convert `*text*` italics (standalone lines) to `<p><em>text</em></p>`
- Convert `**text**` bold inline
- Group non-special lines into `<p>` blocks

## Category IDs on jaredsanborn.com

- AI Insights: 9
- AI Partnership: 22
- AI Strategy: 13
- Leadership: 12
- Marketing: 10
- Origin Story: 23
- Technology: 11
- Uncategorized: 1
