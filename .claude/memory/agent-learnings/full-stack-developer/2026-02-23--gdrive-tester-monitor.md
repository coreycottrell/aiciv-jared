# Google Drive Tester Feedback Monitor

**Date**: 2026-02-23
**Type**: operational
**Topic**: Google Drive service account access + tester feedback monitoring

## What Was Built

`tools/gdrive_tester_monitor.py` - monitors the "Human Testing" Google Drive folder for new files from human testers.

## Access Method That Works

- **Service account at**: `.credentials/google-drive-service-account.json`
- **Email**: `aether-drive-access@aether-integration.iam.gserviceaccount.com`
- **Project**: `aether-integration`
- **Permissions**: Has WRITER access to the Human Testing folder
- **Python packages**: `google-api-python-client`, `google-auth`, `google-auth-oauthlib` all installed

## Folder Details

- **Folder name**: "Human Testing"
- **Folder ID**: `1IjG2LY9jytxcueuytj2Tz7dDUwLWMieV`
- **Owner**: `purebrain@puremarketing.ai`
- **Other users with access**: ashley@puremarketing.ai (writer), natasha@puremarketing.ai (writer), nathan@puremarketing.ai (writer), acgee.ai@gmail.com (reader)
- **Status at build time**: 0 files (folder is empty, waiting for testers)

## Key Patterns Learned

1. **Service account for Drive**: Use `service_account.Credentials.from_service_account_file()` with `drive.readonly` scope. The service account needs to be shared on the folder by the folder owner.

2. **Google Docs export**: Google Workspace docs (Docs, Sheets, Slides) cannot be downloaded directly - use `files().export_media()` with target MIME type. Regular files use `files().get_media()`.

3. **Recursive listing**: Must manually recurse into subfolders by querying `'{parent_id}' in parents and trashed=false` for each folder found.

4. **No API key needed**: Service accounts use JWT auth, not API keys. The `GOOGLE_APP_PASSWORD` in .env is IMAP/SMTP for Gmail, NOT for Drive API.

## Files Created

- `tools/gdrive_tester_monitor.py` - main monitor script
- `config/gdrive-tester-monitor.service` - systemd service
- `config/gdrive-tester-monitor.timer` - systemd timer (every 15 min)
- `inbox/tester-feedback/` - download destination directory
- `inbox/tester-feedback/.seen_files.json` - state tracking (auto-created)

## Systemd Timer Setup

```bash
sudo cp config/gdrive-tester-monitor.service /etc/systemd/system/
sudo cp config/gdrive-tester-monitor.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gdrive-tester-monitor.timer
sudo systemctl start gdrive-tester-monitor.timer
```

## Usage

```bash
# One-time check
python3 tools/gdrive_tester_monitor.py check

# Force re-download all files
python3 tools/gdrive_tester_monitor.py check --force

# Run as daemon (every 5 min)
python3 tools/gdrive_tester_monitor.py daemon

# List all known/seen files
python3 tools/gdrive_tester_monitor.py list
```

## When New Files Arrive

The script will:
1. Download them to `inbox/tester-feedback/` with timestamp prefix
2. Send Telegram notification to Jared (chat_id: 548906264)
3. Log to `logs/gdrive_tester_monitor.log`
4. Track in `.seen_files.json` to avoid re-processing

## Dead End: API Key Approach

A plain Google API key (`https://www.googleapis.com/drive/v3/files?q=...&key=API_KEY`) does NOT work for private Drive folders - returns 403. Need OAuth or service account.
