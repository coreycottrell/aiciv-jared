# Twitter PureSurf Integration for ContentRouter

**Date**: 2026-04-15
**Agent**: coder
**Type**: pattern
**Topic**: Browser automation for Twitter posting via PureSurf BaaS

## Context

Added PureSurf browser automation handler to ContentRouter for Twitter posting. This bypasses Twitter's $100/mo API paywall by posting through browser automation instead of API calls.

## Implementation Pattern

### Core Architecture

**PureSurf Session Management:**
```python
# Session creation with profile-based persistence
sid = _puresurf_ensure_session(profile_name, api_key, log)

# Profile names isolate cookies/storage per user
profile_name = f"{user}-twitter"  # e.g., "jared-twitter"
```

**Navigation:**
```python
# Navigate to URL
_puresurf_navigate(sid, url, api_key, log)

# Execute JavaScript
result = _puresurf_evaluate(sid, script, api_key, log)
```

### Twitter Posting Flow

1. **Session Management**: Create/reuse session for `{user}-twitter` profile
2. **Login Verification**: Check if Twitter session is authenticated
3. **Navigation**: Go to `https://x.com/compose/post` or home page
4. **Type Content**: Use JavaScript to type into compose box
5. **Click Post**: Use JavaScript to click Post button
6. **Capture URL**: Extract tweet URL from redirect or DOM

### JavaScript Patterns

**Typing with multiple selector fallbacks:**
```javascript
const selectors = [
    '[data-testid="tweetTextarea_0"]',
    '[role="textbox"][aria-label*="Tweet"]',
    '.public-DraftStyleDefault-block'
];

for (const sel of selectors) {
    const elem = document.querySelector(sel);
    if (elem) {
        elem.focus();
        elem.textContent = content;
        elem.dispatchEvent(new Event('input', { bubbles: true }));
        return { success: true, selector: sel };
    }
}
```

**Clicking with fallbacks:**
```javascript
const selectors = [
    '[data-testid="tweetButton"]',
    '[data-testid="tweetButtonInline"]',
    'button[aria-label*="Post"]'
];

for (const sel of selectors) {
    const btn = document.querySelector(sel);
    if (btn && !btn.disabled) {
        btn.click();
        return { success: true, selector: sel };
    }
}
```

## Rate Limiting

**PureSurf vs API rate limits:**
- API posting: 3 minutes between posts
- PureSurf posting: 5 minutes between posts (browser automation is slower)

Implementation:
```python
def can_post(self, platform: str, user: str, route_method: str = "api"):
    if route_method == "puresurf":
        min_wait = MIN_SECONDS_BETWEEN_PURESURF_POSTS  # 300 sec
    else:
        min_wait = MIN_SECONDS_BETWEEN_POSTS_PER_PLATFORM_PER_USER  # 180 sec
```

## Login Requirement

**Critical**: User must log into Twitter at `surf.purebrain.ai` with the profile name ONCE before automation works.

Error message when not logged in:
```
Twitter session not authenticated - user needs to log in at surf.purebrain.ai with profile '{profile_name}'
```

## Session Caching

Sessions are cached in memory to avoid creating new browser sessions for every post:

```python
_PURESURF_SESSION_CACHE: dict = {}  # profile_name -> session_id

# Reuse if session still alive
if cached_sid:
    resp = _puresurf_request("GET", f"/sessions/{cached_sid}", api_key, ...)
    if resp and not resp.get("detail"):
        return cached_sid
```

## Generic PureSurf Routing

Created dispatcher pattern for future platforms:

```python
def post_via_puresurf(post: dict, platform: str, user: str, log: logging.Logger):
    if platform == "twitter":
        return post_twitter_puresurf(post, user, log)
    # Future: elif platform == "indiegogo": ...
```

## API Fallback

Kept original Twitter API handler as `post_twitter_api()` for users who upgrade to paid tier:

```python
def post_twitter_api(post: dict, user: str, log: logging.Logger):
    """Post to Twitter/X via v2 API (requires $100/mo tier). Returns (success, post_url, error).
    
    This is a fallback for users who upgrade to Twitter API paid tier.
    Default routing uses post_twitter_puresurf() instead.
    """
```

## Limitations & TODOs

1. **Media Upload**: Not yet implemented - requires file upload API from PureSurf
2. **URL Capture**: May not always get exact tweet URL (fallback to /home)
3. **Browser Automation Flakiness**: JS selectors may break if Twitter changes UI

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/content_router.py` (+300 lines)

## Testing Checklist

- [ ] Twitter session logged in at surf.purebrain.ai with profile 'jared-twitter'
- [ ] Test text-only tweet
- [ ] Verify tweet appears on Twitter
- [ ] Verify tweet URL captured correctly
- [ ] Test rate limiting (5 min cooldown)
- [ ] Test error handling when not logged in

## Lessons Learned

1. **PureSurf API uses JavaScript evaluation** for interaction (no dedicated click/type endpoints)
2. **Multiple selector fallbacks** are essential for UI stability
3. **Session persistence via profile names** enables reuse across runs
4. **Login verification before posting** prevents cryptic failures
5. **Route-specific rate limiting** allows different timing for browser vs API

## Reusable for Future Platforms

This pattern can be applied to any platform without an API:
- Indiegogo campaigns
- Facebook groups
- Instagram stories
- Any site where login cookies persist via profile names

## Memory Search Keywords

twitter, puresurf, browser automation, content router, social posting, baas, session management, javascript evaluation
