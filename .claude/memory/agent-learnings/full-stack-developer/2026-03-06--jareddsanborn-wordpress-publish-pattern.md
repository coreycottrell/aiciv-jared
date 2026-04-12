# jareddsanborn.com WordPress Publish Pattern

**Date**: 2026-03-06
**Type**: operational
**Topic**: Publishing blog posts to jareddsanborn.com via REST API

## What Worked

### Credentials
- Located in `/home/jared/projects/AI-CIV/aether/.env`
- `WORDPRESS_URL=https://jareddsanborn.com`
- `WORDPRESS_USER=jared`
- `WORDPRESS_APP_PASSWORD=plhi NeE4 Cb1c 4d9i BbjZ Knq3`

### Tool
- `tools/wordpress_publisher.py` handles upload-media, publish, test commands
- Skill file: `.claude/skills/wordpress-publishing/SKILL.md`

### Format
- jareddsanborn.com uses PLAIN WordPress HTML - no theme-specific wrappers
- NO `<article class="pb-blog-post">` (that is purebrain.ai only)
- Template: default empty string (same as purebrain.ai blog posts)
- Existing post example: post ID 1226 - plain `<h2>`, `<p>`, `<hr>`, `<strong>`, `<em>`, `<a>` tags
- Category ID 1 = default/uncategorized; "AI" category available

### Publish Flow
1. `python3 tools/wordpress_publisher.py upload-media --file /path/to/banner.jpg --alt "..."` → returns media_id
2. Convert markdown to clean HTML (strip pb-blog-post wrapper, convert headings/bold/italic/links/hr)
3. `python3 tools/wordpress_publisher.py publish --title "..." --content-file /tmp/content.html --status publish --featured-image {media_id} --categories "AI" --slug "..."`
4. Verify with REST API: `GET /wp-json/wp/v2/posts/{id}` - check status=publish, featured_media set, link live

### Published Post (Reference)
- Post ID: 1228
- Media ID: 1227 (banner)
- URL: https://jareddsanborn.com/2026/03/06/52-billion-ai-agents-market-not-the-story/
- Title: The $52.6 Billion AI Agents Market Is Not the Story

## Gotchas
- Blog post markdown from Jared had `<article class="pb-blog-post">` wrapper - MUST strip this for jareddsanborn.com
- H1 title in markdown = post title param, not content
- Slug with dollar sign: use `\$` in bash or just omit the dollar from slug (used "52-billion" format)
