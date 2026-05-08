# Daily Recap Portal Delivery Pattern

**Date:** 2026-04-25
**Type:** operational
**Topic:** Daily recap file write + portal delivery flow

## What Worked

- File written to: `/home/jared/projects/AI-CIV/aether/exports/portal-files/daily-recap-YYYY-MM-DD.md`
- Portal delivery REQUIRES copying to: `/home/jared/exports/portal-files/` first
  - Portal server `DOWNLOAD_ALLOWED_DIRS` is set to `Path.home() / "exports"` (line 107 of `/home/jared/purebrain_portal/portal_server.py`)
  - Files in the project's exports folder (`/home/jared/projects/AI-CIV/aether/exports/`) are NOT in the allowed list
- Delivery command (from aether project root): `bash /home/jared/projects/AI-CIV/aether/tools/portal_deliver.sh /home/jared/exports/portal-files/FILENAME "caption"`
- Script returns "OK: Delivered..." with upload URL on success

## Two-Step Pattern (Always Required)

1. `cp /path/in/aether/exports/ /home/jared/exports/portal-files/`
2. `bash tools/portal_deliver.sh /home/jared/exports/portal-files/FILE "caption"`

## Reference Files

- Portal server allowed dirs config: `/home/jared/purebrain_portal/portal_server.py` line 106
- Delivery script: `/home/jared/projects/AI-CIV/aether/tools/portal_deliver.sh`
- Prior recap format reference: `/home/jared/projects/AI-CIV/aether/exports/portal-files/daily-recap-2026-04-24.md`
