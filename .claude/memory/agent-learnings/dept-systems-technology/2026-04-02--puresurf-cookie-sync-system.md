# PureSurf Universal Cookie Sync System

**Date**: 2026-04-02
**Type**: operational
**Agent**: dept-systems-technology

## What Was Built

Universal cookie sync system for PureSurf (surf.purebrain.ai) enabling any team member to push browser cookies to profiles from the dashboard.

### API Endpoints Added (Feature 21)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/profiles/{name}/cookies` | PUT | Sync cookies to profile storage (no session needed) |
| `/api/v1/profiles/{name}/cookies` | GET | Retrieve stored cookies (admin only) |
| `/api/v1/profiles` | GET | List all profiles with cookie sync status |
| `/sessions/{sid}/inject-cookie` | POST | Generalized cookie injection (any cookie, any platform) |
| `/api/v1/profiles/{name}/sync-status` | GET | Cookie sync metadata (no values exposed) |

### Dashboard Panel

"Cookie Sync" panel added to sidebar with:
- Manual cookie paste (platform presets: LinkedIn/Google/Facebook/X/Custom)
- Bulk JSON import
- Profile cookie status table (freshness indicators)
- Bookmarklet generator (for non-httpOnly cookies)
- Chrome extension config generator

### Key Implementation Details

- Cookies merge by (name, domain) key - new values override existing
- Encryption at rest via Fernet (same as existing cookie storage)
- `cookie_sync_meta.json` tracks last sync time, count, domains per profile
- If profile has active session, cookies also injected into live browser
- Existing `/profiles/{name}/cookies/import` endpoint still works (backward compatible)
- The PUT endpoint uses `/api/v1/` prefix for clean REST-style API versioning

### Files Modified

- `/opt/baas/baas_server_simple.py` - 275 lines added (Feature 21 section before `__main__`)
- `/var/www/puresurf/index.html` - Nav item, panel HTML, JavaScript added
- Backups created with timestamp suffix before modifications

### How PureSurf Restarts

No systemd service. Process runs directly:
```bash
kill $(pgrep -f baas_server_simple.py)
cd /opt/baas && nohup /opt/baas/venv/bin/python3 /opt/baas/baas_server_simple.py > /tmp/baas_startup.log 2>&1 &
```

### Gotcha: Cookie Encryption

Profile cookies may be Fernet-encrypted or plain JSON. The `_decrypt_cookies()` function handles both. When writing new code that reads cookies, always try decrypt first, then fall back to json.load().
