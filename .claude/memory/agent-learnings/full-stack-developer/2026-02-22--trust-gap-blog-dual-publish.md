# WordPress Dual Publish: "The AI Trust Gap" Blog

**Date**: 2026-02-22
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Dual blog post publication - drafts to publish with new featured image

---

## Task

Published existing draft posts to both WordPress sites simultaneously, replacing previously-generated banner with Jared's approved banner from Telegram.

## Published URLs

- **purebrain.ai**: https://purebrain.ai/the-ai-trust-gap/ (Post ID: 631)
- **jareddsanborn.com**: https://jareddsanborn.com/2026/02/22/the-ai-trust-gap/ (Post ID: 1122)

## Media IDs

- purebrain.ai: Media ID 639 (Jared's banner uploaded from docs/from-telegram/photo_20260222_135503.jpg)
- jareddsanborn.com: Media ID 1124

## Banner Source

`/home/jared/projects/AI-CIV/aether/docs/from-telegram/photo_20260222_135503.jpg`
- Visual: Automation (Tasks) vs Strategy (Decisions), 50% vs 28% Trust
- Text: "The Gap: Capability vs. Relationship / Awaken Your AI Partner at PUREBRAIN.ai"
- PureBrain branding: blue + orange, hexagon logo

## Workflow That Worked

1. Load .env manually (not bash source - special chars break bash)
2. Auth: `base64.b64encode(f'User:{pass}'.encode()).decode()` for Basic auth header
3. Upload image via POST to `/wp-json/wp/v2/media` with `Content-Disposition` + `Content-Type: image/jpeg` headers, `data=f.read()` (NOT multipart files)
4. PATCH post: `POST /wp-json/wp/v2/posts/{id}` with `{"status": "publish", "featured_media": media_id}`
5. Verify via GET on post IDs (check status + featured_media fields)
6. Public URL check (HTTP 200 without auth = actually live)

## Key Credential Notes

- PureBrain: user=`Aether`, pass from `PUREBRAIN_WP_APP_PASSWORD` (no quotes needed after strip)
- JDS: user=`AetherPureBrain.ai`, pass from `WORDPRESS_APP_PASSWORD` (has spaces - strip quotes)

## Image Upload Method

Using `data=f.read()` (raw bytes) with `Content-Type: image/jpeg` header works reliably.
The `files=` parameter (multipart) also works but raw data is cleaner.

## Verification Checklist (All Passed)

- [x] Both posts status = "publish" (API confirmed)
- [x] Featured media = Jared's banner on both sites (639, 1124)
- [x] Public HTTP 200 on both URLs
- [x] Banner URLs HTTP 200 accessible
- [x] Telegram notification sent with both links

---

**End of Memory**
