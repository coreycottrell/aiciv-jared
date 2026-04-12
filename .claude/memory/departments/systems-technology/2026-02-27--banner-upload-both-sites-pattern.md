# Banner Upload: Both WordPress Sites + Google Drive Pattern

**Date**: 2026-02-27
**Type**: pattern
**Topic**: Uploading a Jared-approved banner to both blog sites and Drive in one operation

---

## What Was Done

Banner file from Telegram (`docs/from-telegram/photo_20260227_112736.jpg`) uploaded to:

1. **purebrain.ai** — Media ID 995, set as featured_media on post 994 (stop-treating-your-ai-like-an-intern)
2. **jareddsanborn.com** — Media ID 1213, set as featured_media on post 1212
3. **Google Drive** — subfolder `stop-treating-your-ai-like-an-intern-2026-02-27` (ID: 1XcOCTlnYOazJ6yrveGWMUdhZ6JmSpFSh), file ID: 1LQQJGahtWVXQdj7OK4eSg_U2Tzyq-l4k

---

## Verified Steps Pattern

### Step 1: Upload to WP media (POST /wp-json/wp/v2/media)
- Auth: HTTPBasicAuth(user, app_password)
- Headers: Content-Disposition (filename) + Content-Type: image/jpeg
- Returns media ID + source_url

### Step 2: Set featured_media on post (POST /wp-json/wp/v2/posts/{id})
- Body: {"featured_media": media_id}
- Verify: GET same post, confirm featured_media field matches

### Step 3: Google Drive upload
- Class: `GDriveManager` (NOT GoogleDriveManager)
- Path: `tools/gdrive_manager.py`
- Blog posts folder: `1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv`
- Subfolder naming: `{post-slug}-{YYYY-MM-DD}`
- Check if subfolder exists first; create if not
- Check if file exists first; update vs create accordingly

---

## Credentials

| Site | User | Env Var |
|------|------|---------|
| purebrain.ai | Aether | PUREBRAIN_WP_APP_PASSWORD |
| jareddsanborn.com | AetherPureBrain.ai (from WORDPRESS_USER) | WORDPRESS_APP_PASSWORD |

---

## Key Gotcha

`GDriveManager` is the correct class name — not `GoogleDriveManager`. ImportError will tell you the right name if unsure.

---

## Verification Evidence

- purebrain.ai GET /posts/994 → featured_media: 995 (matches)
- jareddsanborn.com GET /posts/1212 → featured_media: 1213 (matches)
- Drive file created: ID 1LQQJGahtWVXQdj7OK4eSg_U2Tzyq-l4k
