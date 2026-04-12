# Wave 1a: BUILD - Worker Extension

**Agent**: full-stack-developer
**Wave**: 1 of 4 (BUILD -> SECURITY -> QA -> SHIP)
**Priority**: P1 CRITICAL - SHIP TODAY
**From**: dept-systems-technology
**Date**: 2026-04-08

## Objective

Extend the Cloudflare Worker at apex.purebrain.ai to support LinkedIn personal-profile posts with image uploads. DO NOT rebuild the existing text-only endpoint.

## File to Modify

`/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/apex-migration/pureapex-worker/src/linkedin.js` (246 lines — text-only `POST /api/linkedin/post` already works)

## New Endpoint

`POST /api/linkedin/post-with-image`

### Request

```json
{
  "text": "post body",
  "image_url": "https://purebrain.ai/blog/.../banner.png"
}
```

### Required Headers

- `X-Internal-Auth: <INTERNAL_AUTH_TOKEN secret>`
- `Content-Type: application/json`

### Success Response

```json
{
  "success": true,
  "post_urn": "urn:li:share:...",
  "post_url": "https://www.linkedin.com/feed/update/<urn>/",
  "posted_at": "<ISO8601>"
}
```

### Error Response

```json
{ "success": false, "error": "<message>", "stage": "register|upload|publish" }
```

## LinkedIn 3-Step Upload Flow

### Step 1: Register Upload

```
POST https://api.linkedin.com/v2/assets?action=registerUpload
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "registerUploadRequest": {
    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
    "owner": "urn:li:person:<linkedin_id from D1>",
    "serviceRelationships": [{
      "relationshipType": "OWNER",
      "identifier": "urn:li:userGeneratedContent"
    }]
  }
}
```

Returns: `value.uploadMechanism['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'].uploadUrl` and `value.asset` (the asset URN).

### Step 2: Fetch + Upload Image Bytes

1. Fetch `image_url` through SSRF guard (allowlist below)
2. `PUT <uploadUrl>` with `Authorization: Bearer <access_token>` and raw image bytes

### Step 3: Publish ugcPost

```
POST https://api.linkedin.com/v2/ugcPosts
Authorization: Bearer <access_token>
X-Restli-Protocol-Version: 2.0.0
Content-Type: application/json

{
  "author": "urn:li:person:<linkedin_id>",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": { "text": "<text>" },
      "shareMediaCategory": "IMAGE",
      "media": [{
        "status": "READY",
        "description": { "text": "" },
        "media": "<asset URN from step 1>",
        "title": { "text": "" }
      }]
    }
  },
  "visibility": { "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC" }
}
```

The response `id` is the post URN. Build `post_url` as `https://www.linkedin.com/feed/update/<urn>/`.

## Token Management

Before any LinkedIn call:

```sql
SELECT access_token, expires_at, linkedin_id, refresh_token
FROM linkedin_tokens LIMIT 1
```

If `expires_at < now() + 5 min` AND `refresh_token` present:

```
POST https://www.linkedin.com/oauth/v2/accessToken
grant_type=refresh_token&client_id=86qlcrlwbfggp0&client_secret=<env>&refresh_token=<refresh>
```

Update D1 with new `access_token` and `expires_at`. **Never** log tokens in responses or `console.log`.

## Internal Auth Shim

- Read `env.INTERNAL_AUTH_TOKEN` (Cloudflare Worker secret)
- Constant-time compare against `X-Internal-Auth` header
- Return `401 { "error": "unauthorized" }` on mismatch
- Do NOT leak which part failed

## SSRF Protection (CRITICAL)

```js
function isImageUrlSafe(url) {
  let u;
  try { u = new URL(url); } catch { return false; }
  if (u.protocol !== "https:") return false;
  const allowedHosts = new Set([
    "purebrain.ai", "www.purebrain.ai", "cdn.purebrain.ai",
    "jareddsanborn.com", "www.jareddsanborn.com"
  ]);
  return allowedHosts.has(u.hostname);
}
```

Reject `http://`, `file://`, `data:`, `localhost`, private IP ranges, and any host not in the allowlist.

## Rate Limiting

Max 5 posts/hour per worker. Use D1 counter keyed by `YYYY-MM-DD-HH`. Create table if missing:

```sql
CREATE TABLE IF NOT EXISTS linkedin_rate_limit (
  hour_key TEXT PRIMARY KEY,
  count INTEGER NOT NULL DEFAULT 0
);
```

On each successful publish, `INSERT OR REPLACE` the incremented count. Reject with 429 if count >= 5.

## Router Wiring

Add route handler for `POST /api/linkedin/post-with-image` in whatever dispatch mechanism `linkedin.js` currently uses for `POST /api/linkedin/post`.

## Deliverables

1. Modified `linkedin.js` with new handler + router wiring
2. Migration SQL for `linkedin_rate_limit` table (if needed) — run via `npx wrangler d1 execute`
3. Any `wrangler.toml` additions listed in report (do NOT apply; devops-engineer will)
4. Deploy command: `npx wrangler deploy` from `pureapex-worker/` directory
5. Secret setup command for Jared: `npx wrangler secret put INTERNAL_AUTH_TOKEN`
6. Sample curl for QA team to test the endpoint

## Constraints

- DO NOT rebuild `POST /api/linkedin/post` (text-only, already working)
- DO NOT touch `tools/linkedin_post_with_image.py` except to add a deprecation comment at the top
- DO NOT add org page posting (Phase 2, explicitly skipped)
- Use existing OAuth token in D1, no re-auth
- Idiomatic Workers JS only (fetch API, no Node builtins)

## Verification Required

Before claiming done, show:
- Diff of `linkedin.js`
- `npx wrangler deploy` output with "Uploaded" success
- Curl command for QA
- Memory written to `.claude/memory/agent-learnings/full-stack-developer/2026-04-08--linkedin-image-upload-worker.md`
