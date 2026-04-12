# video.purebrain.ai R2 Credentials Missing — Root Cause & Fix

**Date**: 2026-03-10
**Type**: gotcha + incident-record
**Topic**: R2 credentials not persisted to .env — service lost them on restart

---

## Incident Summary

`https://video.purebrain.ai` threw:
> "Failed to load library - R2 listing failed: 503: R2 credentials missing. Set CF_ACCOUNT_ID, R2_ACCESS_KEY, R2_SECRET_KEY in .env"

Service (`purebrain-video-gui.service`) had been running for 3 days since last restart (2026-03-06). Library endpoint returned 503 on every `/api/library` call.

---

## Root Cause

`CF_ACCOUNT_ID`, `R2_ACCESS_KEY`, and `R2_SECRET_KEY` were **never written to `.env`**.

They were set only as shell environment variables in a prior session. Shell env vars die with the session. The systemd service does NOT have `EnvironmentFile=` set — it relies entirely on the `.env` file being read by `server.py`'s `load_dotenv()` at startup.

When the service restarted (2026-03-06), it got empty strings for all three variables. The `r2_client()` function at line 126 of `server.py` checks `if not all([CF_ACCOUNT_ID, R2_ACCESS_KEY, R2_SECRET_KEY])` and raises 503.

This was even documented in our own memory:
> "Always Persist Credentials to .env — Never Rely on Shell Env Vars"

---

## What Was Done (2026-03-10)

Added to `/home/jared/projects/AI-CIV/aether/.env`:
```
CF_ACCOUNT_ID=699c81c818f8d32e1da73e79
R2_ACCESS_KEY=NEEDS_TO_BE_SET
R2_SECRET_KEY=NEEDS_TO_BE_SET
R2_PUBLIC_URL_BASE=https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev
```

`CF_ACCOUNT_ID` confirmed from memory. `R2_PUBLIC_URL_BASE` confirmed from prior job records.

**Blocker**: `R2_ACCESS_KEY` and `R2_SECRET_KEY` are not stored anywhere in the codebase. Jared must retrieve them from the Cloudflare dashboard.

---

## Action Required from Jared

1. Go to: https://dash.cloudflare.com/699c81c818f8d32e1da73e79/r2/api-tokens
2. Find existing R2 API token OR create new one:
   - Token type: R2 API Token
   - Permissions: Object Read & Write on bucket `purebrain-video`
3. Copy the **Access Key ID** → set as `R2_ACCESS_KEY` in `.env`
4. Copy the **Secret Access Key** → set as `R2_SECRET_KEY` in `.env`
5. Run: `sudo systemctl restart purebrain-video-gui`
6. Verify: `curl -u purebrain:PASSWORD https://video.purebrain.ai/api/library` should return 200 with video list

---

## Prevention Going Forward

If R2 credentials are ever regenerated or newly created:
- Write them to `.env` IMMEDIATELY — do not rely on shell `export` commands
- Verify the systemd service file has no `EnvironmentFile=` (it doesn't — `.env` is the only source)
- After any new credential addition to `.env`, restart the service

---

## Known Credentials (recovered)

| Variable | Value | Source |
|----------|-------|--------|
| `CF_ACCOUNT_ID` | `699c81c818f8d32e1da73e79` | Memory file (2026-02-28 analytics audit) |
| `R2_PUBLIC_URL_BASE` | `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev` | Job records, multiple memory files |
| `R2_BUCKET` | `purebrain-video` | Multiple memory files |
| `R2_ACCESS_KEY` | MISSING — needs Cloudflare dashboard | — |
| `R2_SECRET_KEY` | MISSING — needs Cloudflare dashboard | — |
