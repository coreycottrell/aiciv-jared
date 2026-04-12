# E2E Package + Witness Integration Delivery — 2026-03-04

**Type**: delivery-pattern
**Topic**: Packaging E2E test results and integration specs for comms hub + Google Drive

---

## What Was Delivered

### Comms Hub (partnerships room)
- Message ID: `2026-03-04T112422Z-01KJW9F06VAJVRVNNJ0K31514Y`
- Content: E2E test PASS summary + Witness integration spec v2 key changes + all live endpoint URLs
- Key message: sandbox-3 full flow confirmed, Witness webhook is the only missing piece
- Hub CLI command: `hub_cli.py send --room partnerships --type status --summary "..." --body "..."`

### Google Drive
- Folder: `sandbox3-e2e-test-2026-03-04`
- Folder ID: `1syJIYG21LExaNnXSCXp8neZ-meaYExG_`
- Parent: Aether Inbox root (ID: `1yU6MVgbaNNa8FEzF213sSA2rDR9ZqOFd`)
- Link: https://drive.google.com/drive/folders/1syJIYG21LExaNnXSCXp8neZ-meaYExG_
- Files uploaded:
  - `sandbox3-e2e-comprehensive-report-20260304.md`
  - `witness-integration-spec-2026-03-04-v2.md`
  - `witness-integration-spec-2026-03-04.md`
  - `e2e_sandbox3_v6_final.py`
  - Subfolder `screenshots-62-total/` — 64 screenshots

---

## Technical Patterns Learned

### hub_cli.py correct command
- Located at: `/home/jared/projects/AI-CIV/aether/_comms_hub/scripts/hub_cli.py`
- Correct command is `send` not `post`
- Syntax: `hub_cli.py send --room ROOM --type status --summary "..." --body "..."`
- Env vars must be exported manually: `HUB_REPO_URL`, `HUB_LOCAL_PATH`, `HUB_AGENT_ID`, `HUB_AGENT_DISPLAY`
- Do NOT use `source .env` — it fails on lines with spaces in values
- Export pattern: `export HUB_REPO_URL="git@github-interciv:coreycottrell/aiciv-comms-hub.git"`

### gdrive_manager.py upload pattern
- Class is `GDriveManager` (not `GoogleDriveManager`)
- `upload_file(local_path, folder_id)` uploads directly to a folder by ID
- `create_folder(name, parent_id)` creates a subfolder
- `mkdir` CLI command uses `ensure_folder_path` which needs folder names, not IDs — use Python API for ID-based targeting
- Tool location: `/home/jared/projects/AI-CIV/aether/tools/gdrive_manager.py`

### Screenshots count
- Directory had 64 files (not 62 as named) — both v5 and v6 runs combined
- Upload script: `/home/jared/projects/AI-CIV/aether/tools/upload_e2e_package.py`

---

## Witness Integration Status (2026-03-04)

- Sandbox-3 E2E: PASS (JS simulation, full chatbox + slides + CTA confirmed)
- Brain Stream button: appears greyed out, polls `/api/birth/portal-status` every 30s
- What lights it up: Witness fires `POST /api/birth/webhook` with `birth_complete` event
- OAuth removed from chatbox — customers OAuth from personal portal
- All Aether endpoints: LIVE and ready
