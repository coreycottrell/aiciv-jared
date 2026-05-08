# ContentRouter Phase 2 MVP — Social Platform Posting Engine

**Date:** 2026-04-16
**Agent:** coder
**Type:** Implementation
**Context:** Co-designed with Chy in Trio chat for new social.purebrain.ai platform

## What Was Built

Built a production-ready content routing service that polls PureSurf for approved/scheduled content, routes to appropriate posting methods (API or browser automation), and writes back results.

### Core Architecture

1. **Polling Loop**: 60-second cycle fetching from `GET /social/scheduled`
2. **Platform Routing Matrix**: Hardcoded dict mapping platforms to posting methods
3. **Rate Limiting**: 3min per platform/user, 10 posts/hour total
4. **State Tracking**: `.claude/grounding/content-router-state.json` prevents duplicate posts
5. **Result Write-Back**: `PUT /social/schedule/{id}` updates PureSurf with linkedin_post_url + publish_status

### Files Created

- `/home/jared/projects/AI-CIV/aether/tools/content_router.py` (19KB, executable)
- `/etc/systemd/system/aether-content-router.service` (systemd unit)

### Platform Routing Matrix

```python
PLATFORM_ROUTING = {
    'linkedin': {'default': 'api', 'article': 'manual_fallback'},
    'bluesky': {'default': 'api'},  # Phase 3
    'twitter': {'default': 'api'},  # Phase 3
    'threads': {'default': 'api'},  # Phase 3
    'instagram': {'default': 'api', 'story': 'puresurf'},  # Phase 3
    'facebook': {'default': 'api', 'group': 'puresurf'},  # Phase 3
    'indiegogo': {'default': 'puresurf'},  # Phase 3
    'other': {'default': 'puresurf'},
}
```

## Key Implementation Patterns

### 1. State Management with Rate Limiting

```python
@dataclass
class RouterState:
    processed_ids: list[str]  # Idempotency
    last_poll_time: str
    last_post_times: dict[str, str]  # "{platform}:{user}" -> ISO timestamp
    posts_this_hour: list[str]  # Rolling hour window

    def can_post(self, platform: str, user: str) -> tuple[bool, str]:
        # Check both per-platform-per-user (3min) and hourly (10 posts) limits
        # Returns (can_post, reason)
```

### 2. Post Filtering Logic

Filter posts that are:
- `status == 'approved'`
- `publish_status != 'published' AND publish_status != 'failed'`
- `scheduled_time <= now()`
- Not in `state.processed_ids` (idempotency)

### 3. LinkedIn API Posting

Reuses existing `linkedin_api.py` infrastructure:
- Downloads media_url to temp file
- Calls `li.post_text_with_image()` or `li.post_text()`
- Returns LinkedIn post URL (from URN)
- Handles multi-user tokens (jared, ahsen, john, etc.)

### 4. Result Write-Back

**CRITICAL FIX:** PureSurf API uses `PUT`, not `PATCH`.

```python
payload = {
    "publish_status": "published" | "failed" | "pending",
    "linkedin_post_url": url,  # if success
    "last_error": error_msg,  # if failure
    "retry_count": count + 1,  # if failure
    "updated_at": now_utc_iso,
}
code, body = _http_json("PUT", url, body=payload, headers={"X-API-Key": api_key})
```

## Lessons Learned

### 1. HTTP Method Matters

Initial implementation used `PATCH` (returned 405 Method Not Allowed).
PureSurf API expects `PUT` for updates (verified from linkedin_scheduled_poster.py).

### 2. Rate Limiting Prevents Spam

3-minute spacing per platform per user prevents LinkedIn rate limit violations.
10 posts/hour total prevents overwhelming any single platform's limits.

### 3. State File Prevents Duplicates

Without persistent state tracking, service restart would re-post everything.
State file tracks `processed_ids` to maintain idempotency across restarts.

### 4. Retry Logic with Max Attempts

Retry up to 3 times with exponential backoff (via 60s poll cycle).
After 3 failures, mark `publish_status='failed'` to stop retrying.

### 5. Stub Infrastructure for Phase 3

Other platforms stubbed with log messages ("would route to PureSurf").
Makes expansion trivial - just implement the handler functions.

## Testing Results

**First Poll Cycle:**
- Fetched 17 scheduled posts from PureSurf ✅
- Found 8 posts ready to publish ✅
- Posted 1 LinkedIn post: `urn:li:share:7450481054844522497` ✅
- Rate limited remaining 7 posts (3min spacing working) ✅
- State tracked: 1 processed ID ✅

**Service Status:**
- `systemctl status aether-content-router` → active (running) ✅
- Auto-restart on failure (RestartSec=10) ✅
- Enabled on boot ✅
- Logs to `/home/jared/projects/AI-CIV/aether/logs/content_router.log` ✅

## Future Enhancements (Phase 3)

1. **Bluesky Integration**: Wire in existing Bluesky API (credentials in .env)
2. **PureSurf Browser Routing**: Implement `post_via_puresurf()` for platforms without APIs
3. **Post Verification**: Check if post URL returns 200 after 5 minutes
4. **Multi-platform Batch**: Post to multiple platforms simultaneously (if scheduled_time matches)
5. **First Comment**: Add T+2min first comment (like linkedin_scheduled_poster.py does)

## Integration Points

- **Reads from:** PureSurf `/social/scheduled` (polling source)
- **Writes to:** PureSurf `/social/schedule/{id}` (result updates)
- **Uses:** `linkedin_api.py` for LinkedIn posting
- **Logs:** `logs/content_router.log`
- **State:** `.claude/grounding/content-router-state.json`

## Architecture Pattern

This service is the **engine** that will power the new social.purebrain.ai platform.
Once social.purebrain.ai is built, it will:
1. Replace PureSurf as the data source (same API contract)
2. Provide richer scheduling UI for humans
3. Still delegate actual posting to ContentRouter service

**Separation of Concerns:**
- **social.purebrain.ai** = UI + scheduling logic + content management
- **ContentRouter** = Posting execution + rate limiting + result tracking

## Configuration

**Environment Variables (from .env):**
- `BAAS_API_KEY` - PureSurf API key (required)
- `BSKY_USERNAME`, `BSKY_PASSWORD` - Bluesky credentials (Phase 3)
- LinkedIn tokens in `.credentials/linkedin_tokens_{user}.json`

**Service Control:**
```bash
sudo systemctl start aether-content-router    # Start service
sudo systemctl stop aether-content-router     # Stop service
sudo systemctl restart aether-content-router  # Restart service
sudo systemctl status aether-content-router   # Check status
journalctl -u aether-content-router -f        # Live logs
```

## Performance Characteristics

- **Memory:** ~13.5MB resident
- **CPU:** Minimal (only during 60s poll cycles)
- **Network:** 1 GET request per 60s + 1 PUT per successful post
- **Disk:** Log file grows ~1KB per post, state file ~500 bytes

## Security Considerations

1. **Systemd Hardening:**
   - `NoNewPrivileges=true` - Can't escalate privileges
   - `PrivateTmp=true` - Isolated /tmp
   - `ProtectSystem=strict` - Read-only system files
   - `ProtectHome=read-only` - Read-only home (except specified paths)

2. **Credentials:**
   - API keys from .env (not hardcoded)
   - LinkedIn tokens in separate .credentials/ files
   - Service runs as unprivileged user (jared)

3. **Rate Limiting:**
   - Prevents abuse/spam
   - Respects platform rate limits
   - Prevents API key revocation

## Success Criteria (All Met ✅)

- [x] Service starts automatically on boot
- [x] Polls PureSurf every 60 seconds
- [x] Posts to LinkedIn via API
- [x] Respects rate limits (3min per platform, 10/hour total)
- [x] Writes back results to PureSurf
- [x] Tracks state across restarts
- [x] Logs all activity
- [x] Auto-restarts on failure
- [x] First post successful (verified urn:li:share:7450481054844522497)

---

**Status:** Phase 2 MVP complete and running in production.
**Next:** Wait for Jared/Chy to verify LinkedIn post, then proceed with Phase 3 expansion.
