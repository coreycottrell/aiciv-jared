# Content Router Critical Fixes

**Date**: 2026-04-16
**Agent**: coder
**Type**: bug-fix
**File**: `/home/jared/projects/AI-CIV/aether/tools/content_router.py`

## Problem Context

ContentRouter service fired 5 old posts (from Apr 14-15) in rapid succession this morning, causing rapid-fire posting. Service was stopped to prevent recurrence.

## Root Causes Identified

### Problem 1: No Max-Age Guard
- Router treated ANY approved post with `scheduled_time <= now()` as ready
- Old posts (48+ hours past due) would become "ready" and fire
- No mechanism to skip posts that were too old

### Problem 2: Rate Limiting State Persistence
- Rate limiting logic was correct but state only saved at END of poll cycle
- If service restarted mid-cycle or crashed, rate limit state could be lost
- Multiple old posts becoming ready simultaneously would all enter the queue

## Fixes Implemented

### Fix 1: 24-Hour Max-Age Guard (Lines 884, 916-920)

Added constant and check in `filter_ready_posts()`:

```python
MAX_AGE_HOURS = 24

# Inside the scheduled_time validation:
time_since_scheduled = now - sched_dt
if time_since_scheduled > timedelta(hours=MAX_AGE_HOURS):
    log.info(f"Skipping {post_id} — scheduled {sched_time}, more than {MAX_AGE_HOURS}hrs ago")
    continue
```

**Effect**: Posts older than 24 hours are skipped with a log message. Prevents backlog fires.

### Fix 2: Immediate State Persistence (Lines 987, 996)

Modified `process_post()` to save state immediately after EACH post:

```python
if success:
    state.record_post(platform, user)
    state.mark_processed(post_id)
    save_state(state)  # ← NEW: Save immediately
    update_post_result(post_id, post_url, "published", None, api_key, log)
```

Also added for failed posts (after 3 retries):
```python
if retry_count >= 3:
    log.error(f"Post {post_id} failed after 3 retries: {error}")
    update_post_result(post_id, None, "failed", error, api_key, log)
    state.mark_processed(post_id)
    save_state(state)  # ← NEW: Save immediately
```

**Effect**: Rate limit state persists after EACH post, not just at end of cycle. Survives mid-cycle restarts.

## Testing Results

### Max-Age Guard Test
```
✅ PASS - Old posts (48hrs) correctly skipped
✅ PASS - Recent posts (5min) correctly accepted
✅ PASS - Future posts correctly rejected
```

### Rate Limiting Tests
```
✅ PASS - 3-minute spacing enforced for API posts
✅ PASS - 5-minute spacing enforced for PureSurf posts
✅ PASS - 10 posts/hour limit enforced
✅ PASS - State persists correctly across save/load
```

### Import Verification
```
✅ PASS - No import errors
```

## How the Incident Happened

1. Multiple posts from Apr 14-15 remained in "approved" status with past `scheduled_time`
2. All became "ready" simultaneously when router polled
3. No max-age guard, so all 5 entered the ready queue
4. Rate limiting DID work (3-minute spacing visible in logs: 09:51, 09:55, 09:58, 10:01, 10:04)
5. But 5 posts in 13 minutes = rapid-fire user experience

## Prevention

- **Max-age guard** prevents old posts from firing
- **Immediate state persistence** ensures rate limits survive restarts
- **Existing rate limiting** already worked but needed persistence fix

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/content_router.py` (lines 884, 916-920, 987, 996)

## Next Steps

1. Service can be safely restarted (fixes are in place)
2. Monitor logs for "Skipping {id} — scheduled..." messages
3. Old posts will be automatically skipped
4. Rate limits will persist correctly

## Key Learnings

- **Guard rails on time-based triggers**: Always add max-age checks for scheduled tasks
- **Persist state immediately**: Don't wait until end of cycle for critical state
- **Rate limiting worked**: The issue was backlog accumulation, not rate limit failure
