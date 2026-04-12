# LinkedIn Image Attachment Bug Fix

**Date**: 2026-04-04
**Agent**: dept-systems-technology
**Type**: teaching
**Topic**: Fixed LinkedIn image posting via PureSurf - media_base64 silently dropped

---

## Root Cause

The `LinkedInPostReq` Pydantic model only had `media_urls: List[str]`. When callers sent `media_base64` (a raw base64 string), Pydantic SILENTLY DROPPED the unknown field. The API returned 200 OK with "draft_ready"/"posted" status, but no image was ever passed to the `_linkedin_post` function.

This is a classic Pydantic gotcha: unknown fields are silently ignored by default (no warning, no error). The API appeared to succeed while doing nothing with the image data.

## Fix Applied

### 1. Model Update (social_suite.py)
Added `media_base64: Optional[str]` and `media_type: Optional[str]` to `LinkedInPostReq`.

### 2. Endpoint Conversion Logic
In `linkedin_post_endpoint`, before calling `_linkedin_post`:
- If `media_base64` is present, decode it to a temp file in `/opt/baas/media_uploads/`
- Append the file path to `media_urls_final`
- Pass `media_urls_final` to `_linkedin_post` (which already has 5-strategy image attachment)

### 3. Image Attachment Strategies (already existed in social_suite.py)
The `_linkedin_attach_images` function has 5 strategies:
1. Click media button -> Playwright file_chooser intercept
2. Direct `set_input_files` on `input[type="file"]`
3. Force-reveal hidden file inputs via JS
4. JS DataTransfer drop simulation
5. Deep scan shadow DOM for file inputs

These strategies were NEVER being invoked because `media_urls` was always empty.

## Files Changed
- `/opt/baas/social_suite.py` on 157.180.69.225 (patched via `patch_linkedin_media_base64.py`)
- `tools/patch_linkedin_media_base64.py` (local, can be re-run safely)
- `tools/linkedin_post_with_image.py` (new standalone posting tool)

## How to Post with Image

### Via API (most reliable):
```python
POST /social/adapters/linkedin/post
{
    "session_id": "jared-linkedin-fresh",
    "content": "Post text here",
    "media_base64": "BASE64_ENCODED_IMAGE",
    "media_type": "image/png"
}
```

### Via script:
```bash
python3 tools/linkedin_post_with_image.py --image /path/to/image.png --text "Post content" --dry-run
```

## Testing Notes
- Cannot fully test without logged-in LinkedIn session
- Session `jared-linkedin-fresh` has saved profile/cookies but they expire
- Password login required after server restart when cookies are stale
- Rate limiter can block navigation: reset via `PUT /rate-limits/linkedin.com` with `{"reset_tightening": true}`
- For hard reset of rate limits: edit `/opt/baas/proactive_rate_limits.json` and restart

## Key Lesson
**ALWAYS check Pydantic model fields match what callers send.** Pydantic's silent field dropping is dangerous for APIs where the caller thinks they're sending data that's being processed.

Consider adding `model_config = ConfigDict(extra='forbid')` to catch unknown fields as errors.
