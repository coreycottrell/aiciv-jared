# Bluesky Blog Thread Post: 2026-02-20

**Type**: operational + teaching

## Task

Posted 5-post approved thread promoting:
"The Difference Between Using AI and Having an AI Partner"
Blog URL: https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/

## Thread Posted

First post URL: https://bsky.app/profile/purebrain.ai/post/3mfbzvvvvvr2w

All 5 posts successful, 0 failed.

Post URIs (in thread order):
1. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mfbzvvvvvr2w (hook + image)
2. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mfbzvxy5h72n (transactional AI)
3. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mfbzvzluvi2n (4 differences)
4. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mfbzw37lv325 (3 diagnostic questions)
5. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mfbzw4tesq2e (close + link)

## Image Handling GOTCHA

Original image: 3.48MB PNG - EXCEEDS Bluesky's 976KB limit (BlobTooLarge error).
Fix: Convert to JPEG, compress with Pillow at quality=85.
Result: 257.5KB JPEG - well within limits.

**Rule**: Always compress images before upload. Use Pillow to convert PNG -> JPEG at quality=85.
Max Bluesky image size: 976KB (~1MB).

```python
from PIL import Image
img = Image.open(src).convert('RGB')
img.save('/tmp/bsky_compressed.jpg', 'JPEG', quality=85, optimize=True)
```

## Script Location

/home/jared/projects/AI-CIV/aether/tools/post_blog_thread.py

## What Worked

- atproto session string restore: works fine (session was fresh, no expiry)
- Image compression via Pillow: essential for PNG images from Telegram
- Thread reply chain: root_ref + parent_ref pattern works correctly
- 1.5 second delay between posts: sufficient for human-like pacing, no rate limit issues
- models.AppBskyEmbedImages.Main for image embed: works correctly

## Safety Notes

- Thread post count: 5 (within 10/day limit)
- No follows done this session
- Rate limit remaining: 2996/3000 (plenty of headroom)
