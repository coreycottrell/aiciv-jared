# PureSurf Cookie Sync Page - Deployed

**Date**: 2026-04-04
**Type**: operational
**Agent**: dept-systems-technology

## What Was Built

Mobile-friendly cookie sync page at `surf.purebrain.ai/sync` that allows users to sync browser cookies to PureSurf profiles from ANY device (including mobile phones) without needing a Chrome extension.

## Architecture

- **Module**: `/opt/baas/cookie_sync_page.py` - Standalone module imported by main server
- **Pattern**: Same as social_suite.py - `extend_sync_routes()` mounts routes on app
- **Server**: `baas_server_simple.py` imports and mounts at startup

## How It Works (Proxy Login Flow)

1. User visits `surf.purebrain.ai/sync` on phone
2. Enters PureSurf API key -> loads their profiles
3. Selects profile + platform (LinkedIn, Twitter, Facebook, Instagram, Google)
4. PureSurf creates a server-side Playwright browser session
5. Navigates to platform login page, takes screenshot
6. User types credentials via the sync page form
7. PureSurf types them into the real browser (server-side)
8. If 2FA needed: shows screenshot, user enters code
9. On success: all cookies (including httpOnly like `li_at`) are captured server-side
10. Cookies saved to profile's encrypted storage

## API Endpoints Added

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/sync` | GET | Serve the HTML page |
| `/sync/start` | POST | Create session, navigate to login page |
| `/sync/credentials` | POST | Type username + password |
| `/sync/password` | POST | Separate password step (Twitter/Google) |
| `/sync/2fa` | POST | Submit 2FA code |
| `/sync/screenshot` | GET | Get fresh browser screenshot |
| `/sync/cancel` | POST | Cancel and close session |

## Platform Support

- LinkedIn (li_at, JSESSIONID, li_mc)
- Twitter/X (auth_token, ct0, twid)
- Facebook (c_user, xs, datr)
- Instagram (sessionid, csrftoken, ds_user_id)
- Google (SID, __Secure-3PSID, SSID)

## Key Design Decisions

- **Proxy login approach chosen**: Server-side browser captures httpOnly cookies that `document.cookie` cannot access
- **Screenshot polling**: Every 3 seconds to show live browser state
- **Multi-step login**: Handles Twitter/Google style (username -> next -> password) flows
- **Session auto-cleanup**: Browser closed after successful sync
- **Auth required**: All endpoints require PureSurf API key via x-api-key header
- **No credential storage**: Creds typed directly into browser, never saved

## Files

- `/opt/baas/cookie_sync_page.py` (the module)
- `exports/departments/systems-technology/cookie_sync_page.py` (local copy)
- `exports/departments/systems-technology/deploy_cookie_sync.sh` (deploy script)

## UI Features

- Dark theme (#080a12, PureBrain branded)
- Mobile-first (max-width 480px, touch-friendly buttons)
- Font Awesome icons for platforms
- Live screenshot display (16:10 aspect ratio)
- Loading spinners, status indicators
- Secure password fields
- Profile selector with "Create New" option
