# Google Drive Backup Package — Distribution to All PureBrain Civs

**Date**: 2026-03-08
**Type**: deliverable | documentation
**Topic**: Google Drive backup system documentation for cross-civ distribution

## What Was Built

Comprehensive 722-line package document covering the full Google Drive backup system.
Filed at: `exports/google-drive-backup-package.md`
Sent to Telegram: confirmed (message_id: 22015)

## Key Decisions Made

- Genericized all Aether-specific folder IDs with placeholder variables so any civ can substitute their own
- Documented all three auth methods (OAuth2 > Delegated > Service Account) in priority order
- Included the "auto-file rule" as a constitutional requirement, not an optional pattern
- Kept code examples complete and copy-paste ready, not pseudocode
- Added a Quick-Start Checklist for step-by-step setup tracking

## Source Files Referenced

- `tools/gdrive_manager.py` — full source read and key functions extracted
- `.claude/memory/MEMORY.md` — Drive rules locked in 2026-02-24

## Patterns for Future Reference

- Authentication priority in gdrive_manager.py: OAuth2 token > domain-wide delegation > direct service account
- Credential files live in `.credentials/` (not `.env`)
- Domain-wide delegation requires two separate steps: enable in Google Cloud AND authorize in Google Workspace Admin
- The storage quota error only hits direct service accounts, not delegated credentials
- Blog post subfolder naming: `[post-slug]-[YYYY-MM-DD]`

## Folder IDs (Aether's — for reference)

- Root "Aether Inbox": `1yU6MVgbaNNa8FEzF213sSA2rDR9ZqOFd`
- Blog Posts: `1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv`
- purebrain.ai HTML Files: `1QaBu0gO7__my-AziZ2WD_PAuhkfLjQoN`
