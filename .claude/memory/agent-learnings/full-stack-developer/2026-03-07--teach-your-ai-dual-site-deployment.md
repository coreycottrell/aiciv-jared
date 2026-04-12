# Dual Site Blog Deployment - teach-your-ai-something-no-one-else-could

**Date**: 2026-03-07
**Type**: operational
**Topic**: Deploying blog post to purebrain.ai AND jareddsanborn.com simultaneously

## What Worked

### purebrain.ai (direct REST API)
- User: Aether | App Password in deployment instructions
- Banner uploaded via multipart: POST /wp-json/wp/v2/media → ID 1420
- Post deployed: ID 1423, template="" (empty string), category [5] = AI Strategy
- Final URL: https://purebrain.ai/teach-your-ai-something-no-one-else-could/

### jareddsanborn.com (wordpress_publisher.py tool)
- Credentials in .env: WORDPRESS_USER=jared, WORDPRESS_APP_PASSWORD=plhi NeE4 Cb1c 4d9i BbjZ Knq3
- Tool: python3 tools/wordpress_publisher.py upload-media + publish
- Banner uploaded → ID 1229
- Post deployed: ID 1230
- Final URL: https://jareddsanborn.com/2026/03/07/teach-your-ai-something-no-one-else-could/

## HTML Format Differences

| Site | Wrapper | Template | Source |
|------|---------|----------|--------|
| purebrain.ai | `<!-- wp:html --><article class="pb-blog-post">...</article><!-- /wp:html -->` | "" | pb-blog-post is mandatory |
| jareddsanborn.com | `<!-- wp:html -->...<!-- /wp:html -->` (NO article wrapper) | "" | plain HTML only |

## Gotchas

### Duplicate Slug / "-2" URL Issue
- A second post (ID 1422) was auto-created with the same slug (possibly overnight pipeline)
- My post got slug `teach-your-ai-something-no-one-else-could-2`
- Fix: DELETE /wp/v2/posts/1422 (trash it), then PATCH /wp/v2/posts/1423 with correct slug
- Slug collision = always check for existing posts before deploying

### jareddsanborn.com Auth Pattern
- "Aether" username does NOT work on jareddsanborn.com
- Must use username "jared" with app password from .env
- GET requests work unauthenticated, POST requires auth - don't confuse them
- Use wordpress_publisher.py tool, not direct curl, for jareddsanborn.com

## Google Drive
- Blog subfolder: teach-your-ai-something-no-one-else-could-2026-03-07 (ID: 1W2OW1zYTFhGSmkAq_Ole3u1T1EXt2o98)
- 4 files uploaded: blog-post.md, banner.png, linkedin-newsletter.md, linkedin-post.md
- gdm.upload_file(filepath, folder_id) - no mime_type kwarg
