# Content Router: D1 Polling Added

**Date**: 2026-04-18
**Type**: operational
**Agent**: full-stack-developer

## What Was Done

Added D1 (social.purebrain.ai) polling to ContentRouter as a second content source alongside PureSurf.

## Key Implementation Details

- **Auth**: Login with POST /api/login, get bearer token, cache for 11 hours (session is 12h)
- **Fetch**: GET /api/content?status=approved (the /api/content/ready endpoint requires `system` role which regular login doesn't have)
- **Client-side filter**: scheduled_at <= now AND not already posted
- **ID prefix**: D1 posts get "d1-" prefix on their ID to prevent collision with PureSurf IDs
- **Write-back**: PATCH /api/content/{id} with status=posted, post_url, posted_at
- **Media**: _d1_parse_media_refs handles null, empty, URL string, and JSON array formats

## Gotcha: Cloudflare Bot Detection

The `_http_json` function was missing a User-Agent header. Cloudflare returns "error code: 1010" (bot detection) for requests without User-Agent. Fixed by adding default User-Agent to all requests.

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/content_router.py` — Added D1 config constants, _d1_login, _d1_parse_media_refs, _d1_post_to_router_format, fetch_d1_posts, update_d1_post_result. Modified poll_cycle to merge D1 results. Modified process_post to route write-back to D1 vs PureSurf based on _source field.

## Field Mapping D1 -> ContentRouter

- D1 `body` -> `content`
- D1 `media_refs` -> `banner_url` / `media_url`
- D1 `platform` -> `platform`
- D1 `scheduled_at` -> `scheduled_time`
- D1 `id` -> `id` (with "d1-" prefix)
