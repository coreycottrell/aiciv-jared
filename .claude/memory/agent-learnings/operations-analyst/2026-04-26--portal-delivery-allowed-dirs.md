# Portal Delivery: Allowed Directories

**Date**: 2026-04-26
**Type**: operational
**Topic**: portal_deliver.sh path restrictions

## What Was Learned

portal_deliver.sh (and the /api/deliverable endpoint) enforces a strict path allowlist defined in portal_server.py at line 106:

```
DOWNLOAD_ALLOWED_DIRS = [
    ~/exports
    ~/to-human
    ~/purebrain_portal
    ~/from-acg
    ~/portal_uploads
]
```

The aether project exports path `/home/jared/projects/AI-CIV/aether/exports/portal-files/` is NOT in the allowlist.

## Correct Procedure for Daily Recap Delivery

1. Write file to `/home/jared/projects/AI-CIV/aether/exports/portal-files/` (for git tracking)
2. Copy to `/home/jared/exports/portal-files/` (portal-allowed path)
3. Run `bash tools/portal_deliver.sh /home/jared/exports/portal-files/{filename} "caption"`

## Dead End Avoided

Do NOT try to deliver directly from the aether project path — it will fail with "path not in allowed directories" every time.
