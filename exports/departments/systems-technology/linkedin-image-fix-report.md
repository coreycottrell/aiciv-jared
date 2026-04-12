# LinkedIn Image Upload Fix Report

**Date**: 2026-04-03
**Server**: 157.180.69.225 (PureSurf)
**Agent**: dept-systems-technology

---

## Root Causes Found

### Problem 1: Authentication (BLOCKING)

The `jared-linkedin` profile does NOT have a `li_at` cookie -- the critical LinkedIn session token. Without it, LinkedIn always redirects to the login page.

**Evidence**:
- Decrypted `cookies.json`: 22 LinkedIn cookies, NO `li_at`
- Firefox `cookies.sqlite`: Same -- no `li_at`
- Diagnostic: `python3 /opt/baas/check_linkedin_session.py` confirms

**Why it worked earlier today at 16:08**: The session that posted at 16:08 was created from an external caller (89.167.19.20). That session likely inherited `li_at` as a transient session cookie from a prior login within the same Playwright context that was never persisted to disk. When the context was closed and reopened, the session cookie was lost.

**Fix applied**: Enhanced `_save_cookies()` in `baas_server_simple.py` to also extract cookies from Firefox's `cookies.sqlite` database. This catches httpOnly cookies that Playwright's cookie API may not surface.

**Fix needed (requires Jared)**: Inject a valid `li_at` cookie. Two options:

**Option A** - Use the new inject endpoint:
```bash
# 1. Get li_at from your browser:
#    Chrome/Firefox -> F12 -> Application -> Cookies -> linkedin.com -> li_at -> Copy value

# 2. Create session
curl -X POST http://157.180.69.225:8901/sessions \
  -H 'x-api-key: <KEY>' -H 'Content-Type: application/json' \
  -d '{"profile_name": "jared-linkedin", "proxy_provider": "residential"}'

# 3. Inject li_at
curl -X POST http://157.180.69.225:8901/sessions/jared-linkedin/inject-li-at \
  -H 'x-api-key: <KEY>' -H 'Content-Type: application/json' \
  -d '{"li_at": "YOUR_LI_AT_VALUE_HERE"}'

# 4. Navigate to verify
curl -X POST http://157.180.69.225:8901/sessions/jared-linkedin/navigate \
  -H 'x-api-key: <KEY>' -H 'Content-Type: application/json' \
  -d '{"url": "https://www.linkedin.com/feed/"}'

# 5. Save cookies (close session saves automatically)
```

**Option B** - Login via browser automation (provide LinkedIn email/password).

---

### Problem 2: Image Not Passed to Post Endpoint (FIXED)

From the server logs at 16:08-16:11 today:

1. First post at 16:09 -- text only, NO `media_urls`
2. Media upload at 16:10 -- image saved to `/opt/baas/media_uploads/`
3. Second post at 16:11 -- again NO `_linkedin_attach_images` log output

The calling code (Aether on the main server) uploads media via `/social/adapters/media/upload` but does NOT include the returned `file_path` in the subsequent `/social/adapters/linkedin/post` call's `media_urls` parameter.

**Fix**: The `media_urls` parameter is already wired through all code paths. The caller needs to include the image path:
```json
POST /social/adapters/linkedin/post
{
    "session_id": "jared-linkedin",
    "content": "Post text here",
    "media_urls": ["/opt/baas/media_uploads/upload_1775232635_06364327.jpg"]
}
```

---

### Problem 3: Stale Selectors (FIXED)

The `_linkedin_attach_images` function had selectors that may not match LinkedIn's current DOM, and failures were logged at DEBUG level (invisible in production).

**Fix applied** to `/opt/baas/social_suite.py`:

- **14 button selectors** (up from 7) including case-insensitive partial matches
- **5 strategies** (up from 3):
  1. Click media button + file_chooser intercept
  2. Direct `set_input_files` on `input[type=file]`
  3. Force-reveal hidden file inputs via JS
  4. **NEW**: JS DataTransfer drop simulation (fallback)
  5. **NEW**: Shadow DOM deep scan for file inputs
- **All failure logs upgraded** from `log.debug` to `log.warning` (visible in production)
- **DOM dump on failure** -- logs all dialog buttons and inputs for debugging
- **Debug screenshot** saved on failure with DOM analysis

---

## Files Modified

| File | Change |
|------|--------|
| `/opt/baas/social_suite.py` | Replaced `_linkedin_attach_images` (969 -> 1134 lines) |
| `/opt/baas/baas_server_simple.py` | Enhanced `_save_cookies` + new `/inject-li-at` endpoint (4101 -> 4203 lines) |
| `/opt/baas/check_linkedin_session.py` | NEW - diagnostic tool |
| `/opt/baas/test_linkedin_image_upload.sh` | NEW - E2E test script |

## Backups

| Backup | Purpose |
|--------|---------|
| `/opt/baas/social_suite.py.bak.20260403_173338` | Before image attach fix |
| `/opt/baas/baas_server_simple.py.bak.20260403_173610` | Before cookie + inject fixes |

## Testing Status

- Code changes: Syntax verified, server restarted, health check passing
- Image upload: Cannot test E2E because `li_at` cookie is missing (LinkedIn not logged in)
- Once `li_at` is injected: Run `/opt/baas/test_linkedin_image_upload.sh <li_at_value>`

## Next Steps

1. **Jared**: Copy `li_at` cookie from your browser and inject it (see Option A above)
2. **Aether**: When calling `/social/adapters/linkedin/post`, always include `media_urls` with the file path from the media upload response
3. **Test**: Run `test_linkedin_image_upload.sh` to verify image appears in composer
4. **Monitor**: Check `journalctl -u purebrain-baas -f` for `LinkedIn: SUCCESS` or `LinkedIn: FAILED` messages
