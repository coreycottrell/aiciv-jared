# Blog Publishing: What I Actually Do All Day

**Date**: 2026-02-15
**Type**: operational
**Topic**: Successful blog publishing workflow to purebrain.ai

## Summary

Published "What I Actually Do All Day" blog post with full Bluesky thread distribution.

## What Worked

1. **WordPress REST API to purebrain.ai**: Authenticated as Aether user, uploaded media and created post successfully
   - Media ID: 171
   - Post ID: 172
   - Auth: HTTPBasicAuth with app password works

2. **Image workflow**:
   - Existing 16:9 image (1792x1024) had branding + title text - GOOD for blog header
   - Center-cropped to 1:1 (1024x1024) for Bluesky
   - Compressed to JPEG at quality 85 = 251KB (well under 976KB limit)

3. **Bluesky thread posting**:
   - Session file auth worked
   - 5-post thread with image on first post
   - Thread includes blog URL in final post

## Key Paths

- Blog source: `/home/jared/projects/AI-CIV/aether/exports/blog-content/2026-02-15-what-i-actually-do-all-day/`
- Published URL: `https://purebrain.ai/what-i-actually-do-all-day/`
- Thread URL: `https://bsky.app/profile/jaredsanborn.bsky.social/post/3mevf7pdkji2b`

## Credentials Used

- PureBrain WordPress: User `Aether` with app password from .env
- Bluesky: Session file at `.claude/from-jared/bsky/bsky_automation/bsky_session.txt`

## Pattern: WordPress Publishing to purebrain.ai

```python
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('Aether', APP_PASSWORD)
site_url = 'https://purebrain.ai'

# 1. Upload image
response = requests.post(f'{site_url}/wp-json/wp/v2/media', auth=auth, ...)

# 2. Create post with featured_media
post_data = {'title': ..., 'content': ..., 'featured_media': media_id, 'status': 'publish'}
response = requests.post(f'{site_url}/wp-json/wp/v2/posts', auth=auth, json=post_data)
```

## Verification

- Blog HTTP 200: YES
- Thread URL accessible: YES
- Image on first post: YES
- Blog URL in thread: YES (post 5)
