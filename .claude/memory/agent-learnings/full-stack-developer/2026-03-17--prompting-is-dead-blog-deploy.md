# Blog Deploy: Prompting Is Dead

**Date**: 2026-03-17
**Type**: operational
**Agent**: full-stack-developer

## Task Completed

Published "Prompting Is Dead" blog post to:
1. CF Pages: https://purebrain.ai/blog/prompting-is-dead/ (HTTP 200 verified)
2. WordPress: https://jareddsanborn.com/2026/03/17/prompting-is-dead/ (HTTP 200 verified, Post ID: 1281)

## Files Created/Used

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/prompting-is-dead/index.html` — CF Pages HTML
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/prompting-is-dead/banner.png` — Banner image (copied from portal upload)
- Source markdown: `/home/jared/portal_uploads/from-portal/portal_20260317_145220_prompting-is-dead-blog-post.md`
- Template: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/your-ai-has-no-idea-who-you-are/index.html`

## Key Patterns

- CF Pages deploy command: `CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true`
- WordPress media upload returns ID (1280 for banner.png)
- WP publisher tool doesn't support `--featured-media` CLI arg — use Python API directly with `"featured_media": ID` in post_data dict
- CF Pages token does NOT have zone list perms (scoped to Pages only) — cache flush requires separate zone token or manual flush
- WP post date format: `"date": "2026-03-17T09:00:00"` (ISO 8601, no timezone suffix for local)

## WordPress Direct Publish Pattern

```python
post_data = {
    "title": "...",
    "slug": "...",
    "content": html_content,
    "status": "publish",
    "featured_media": media_id,
    "excerpt": "...",
    "date": "YYYY-MM-DDTHH:MM:SS"
}
headers = {"Authorization": f"Basic {base64_creds}", "Content-Type": "application/json"}
resp = httpx.Client().post(f"{wp_url}/wp-json/wp/v2/posts", json=post_data, headers=headers)
```
