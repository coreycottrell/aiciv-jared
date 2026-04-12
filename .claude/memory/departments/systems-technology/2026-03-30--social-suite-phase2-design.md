# Social Suite Phase 2 — Instagram + Facebook Adapters Design

**Date**: 2026-03-30
**Agent**: dept-systems-technology
**Type**: operational
**Topic**: Phase 2 social suite adapters for PureSurf BaaS

---

## What Was Designed & Built

### Architecture Decision: Extension Pattern
- Phase 2 uses `extend_social_router()` which mutates the existing Phase 1 router
- No new router creation -- all endpoints stay under `/social/` prefix
- Same auth pattern (x_api_key header), same sessions_ref, same screenshot pattern

### Instagram Adapter (6 endpoints)
- `POST /social/adapters/instagram/post` -- image + caption draft
- `POST /social/adapters/instagram/confirm-post` -- click Share
- `POST /social/adapters/instagram/story` -- story with image + text overlay
- `POST /social/adapters/instagram/confirm-story` -- publish story
- `POST /social/adapters/instagram/feed-scan` -- scrape feed posts
- `POST /social/adapters/instagram/engage` -- like or comment on posts

### Facebook Adapter (5 endpoints)
- `POST /social/adapters/facebook/page-post` -- page post (text/image/link)
- `POST /social/adapters/facebook/confirm-post` -- click Post
- `POST /social/adapters/facebook/feed-scan` -- scrape feed
- `POST /social/adapters/facebook/comment` -- like/comment management
- `POST /social/adapters/facebook/group-post` -- group posting

### Media Upload (1 endpoint)
- `POST /social/adapters/media/upload` -- base64 image/video to temp file

### Analytics (1 endpoint)
- `POST /social/analytics/engagement` -- cross-platform metrics scraping

### Status (1 endpoint)
- `GET /social/status/v2` -- full Phase 2 status with endpoint list

## Key Design Decisions
1. **File chooser for Instagram uploads** -- Playwright's `expect_file_chooser()` with fallback to `input[type=file]`
2. **Multi-selector strategy** -- every interaction has 3-6 CSS selectors with JS evaluate fallback (Instagram/Facebook UIs change frequently)
3. **Same draft-then-confirm flow** -- matches Phase 1 LinkedIn/Twitter pattern exactly
4. **Facebook comment deletion** -- deferred to Phase 3 (requires 3-dot menu interaction)
5. **Instagram web limitations** -- documented that web doesn't support video posts or carousels natively

## Files Created
- `exports/departments/systems-technology/social_suite_phase2.py` (main module, ~900 lines)
- `exports/departments/systems-technology/patch_social_suite_phase2.py` (server patch)

## Deployment Steps (NOT done yet)
1. `scp social_suite_phase2.py root@157.180.69.225:/opt/baas/`
2. `scp patch_social_suite_phase2.py root@157.180.69.225:/opt/baas/`
3. SSH in and run: `python3 /opt/baas/patch_social_suite_phase2.py`
4. Restart server: `systemctl restart puresurf` (or equivalent)
5. Test via: `curl -H "X-API-Key: ..." http://157.180.69.225:8901/social/status/v2`

## Integration with Phase 1 Scheduler
- The Phase 1 scheduler's `publish_post_now` already checks platform names
- To activate Instagram/Facebook in scheduler, add platform routing in the publish loop:
  ```python
  elif platform == 'instagram':
      result = await _instagram_post(sessions_ref, profile_name, post['content'], auto_confirm=auto)
  elif platform == 'facebook':
      result = await _facebook_page_post(sessions_ref, profile_name, page_url, post['content'], auto_confirm=auto)
  ```
- This integration patch is NOT included yet -- needs Phase 1 scheduler update
