#!/usr/bin/env python3
"""
Google Drive Tester Feedback Monitor

Monitors the Human Testing folder on Google Drive for new files from human testers.
Downloads new files, saves them locally, and sends Telegram notifications.

Usage:
    python3 tools/gdrive_tester_monitor.py check     # One-time check
    python3 tools/gdrive_tester_monitor.py daemon    # Run as daemon (every 5 min)
    python3 tools/gdrive_tester_monitor.py list      # List all known files

Folder: https://drive.google.com/drive/folders/1IjG2LY9jytxcueuytj2Tz7dDUwLWMieV
Folder Name: Human Testing
Owner: purebrain@puremarketing.ai

Author: Aether (full-stack-developer agent)
Created: 2026-02-23
"""

import json
import os
import sys
import time
import argparse
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional

# Google Drive API
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
    HAS_GDRIVE = True
except ImportError:
    HAS_GDRIVE = False
    print("ERROR: google-api-python-client not installed. Run: pip3 install google-api-python-client")
    sys.exit(1)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SERVICE_ACCOUNT_FILE = PROJECT_ROOT / ".credentials" / "google-drive-service-account.json"
TELEGRAM_CONFIG = PROJECT_ROOT / "config" / "telegram_config.json"
STATE_FILE = PROJECT_ROOT / "inbox" / "tester-feedback" / ".seen_files.json"
DOWNLOAD_DIR = PROJECT_ROOT / "inbox" / "tester-feedback"
LOG_FILE = PROJECT_ROOT / "logs" / "gdrive_tester_monitor.log"

# Google Drive folder
FOLDER_ID = "1IjG2LY9jytxcueuytj2Tz7dDUwLWMieV"
FOLDER_NAME = "Human Testing"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# MIME type to extension mapping for Google Docs exports
GOOGLE_DOC_EXPORTS = {
    "application/vnd.google-apps.document": ("application/pdf", ".pdf"),
    "application/vnd.google-apps.spreadsheet": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
    "application/vnd.google-apps.presentation": ("application/pdf", ".pdf"),
    "application/vnd.google-apps.drawing": ("image/png", ".png"),
    "application/vnd.google-apps.form": ("application/pdf", ".pdf"),
}

# File types we want to process (skip folders and shortcuts)
SKIP_MIME_TYPES = {
    "application/vnd.google-apps.folder",
    "application/vnd.google-apps.shortcut",
}


def log(message: str, level: str = "INFO"):
    """Log message to file and stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")


def load_state() -> dict:
    """Load seen files state from disk."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception as e:
            log(f"Could not load state: {e}", "WARNING")
    return {
        "seen_file_ids": {},  # file_id -> {name, downloaded_at, local_path}
        "last_check": None,
        "total_files_downloaded": 0
    }


def save_state(state: dict):
    """Save seen files state to disk."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def get_drive_service():
    """Build Google Drive API service using service account."""
    if not SERVICE_ACCOUNT_FILE.exists():
        log(f"Service account file not found: {SERVICE_ACCOUNT_FILE}", "ERROR")
        raise FileNotFoundError(f"Missing: {SERVICE_ACCOUNT_FILE}")

    creds = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE), scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def list_folder_files(service, folder_id: str, recursive: bool = True) -> list:
    """
    List all files in a folder (and subfolders if recursive=True).
    Returns list of file metadata dicts.
    """
    all_files = []

    def _list_in(parent_id: str, path_prefix: str = ""):
        query = f"'{parent_id}' in parents and trashed=false"
        page_token = None

        while True:
            response = service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink)",
                pageSize=100,
                pageToken=page_token
            ).execute()

            items = response.get("files", [])
            for item in items:
                item["drive_path"] = f"{path_prefix}/{item['name']}" if path_prefix else item["name"]

                if item["mimeType"] == "application/vnd.google-apps.folder":
                    if recursive:
                        _list_in(item["id"], item["drive_path"])
                else:
                    all_files.append(item)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

    _list_in(folder_id)
    return all_files


def download_file(service, file_info: dict, dest_dir: Path) -> Optional[Path]:
    """
    Download a file from Google Drive.
    Handles both regular files and Google Docs (exports to appropriate format).
    Returns local path on success, None on failure.
    """
    file_id = file_info["id"]
    file_name = file_info["name"]
    mime_type = file_info["mimeType"]

    # Skip non-downloadable types
    if mime_type in SKIP_MIME_TYPES:
        return None

    # Sanitize filename for local filesystem
    safe_name = "".join(c if c.isalnum() or c in "._- ()" else "_" for c in file_name)
    timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Handle Google Workspace documents (need export)
    if mime_type in GOOGLE_DOC_EXPORTS:
        export_mime, ext = GOOGLE_DOC_EXPORTS[mime_type]
        if not safe_name.endswith(ext):
            safe_name = safe_name + ext
        local_path = dest_dir / f"{timestamp_prefix}_{safe_name}"

        try:
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        except Exception as e:
            log(f"Could not export {file_name}: {e}", "ERROR")
            return None
    else:
        # Regular file download
        # Add extension if missing
        if "." not in safe_name:
            ext = mimetypes.guess_extension(mime_type) or ""
            safe_name = safe_name + ext
        local_path = dest_dir / f"{timestamp_prefix}_{safe_name}"

        try:
            request = service.files().get_media(fileId=file_id)
        except Exception as e:
            log(f"Could not get media for {file_name}: {e}", "ERROR")
            return None

    # Perform download
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Write to disk
        with open(local_path, "wb") as f:
            f.write(fh.getvalue())

        log(f"Downloaded: {file_name} -> {local_path}")
        return local_path

    except Exception as e:
        log(f"Download failed for {file_name}: {e}", "ERROR")
        return None


def send_telegram_notification(files_info: list) -> bool:
    """
    Send Telegram notification about new tester feedback files.
    Returns True if sent successfully.
    """
    if not TELEGRAM_CONFIG.exists():
        log("Telegram config not found, skipping notification", "WARNING")
        return False

    try:
        with open(TELEGRAM_CONFIG) as f:
            tg_config = json.load(f)

        bot_token = tg_config.get("bot_token")
        chat_id = tg_config.get("default_chat_id", "548906264")

        if not bot_token:
            log("No bot_token in Telegram config", "WARNING")
            return False

        # Build message
        count = len(files_info)
        file_lines = []
        for fi in files_info[:10]:  # Show max 10 files in notification
            name = fi.get("name", "Unknown")
            drive_path = fi.get("drive_path", "")
            local_path = fi.get("local_path", "")
            size = fi.get("size", "")
            size_str = f" ({int(size)/1024:.1f}KB)" if size and str(size).isdigit() else ""
            file_lines.append(f"  - {name}{size_str}")

        if len(files_info) > 10:
            file_lines.append(f"  ... and {len(files_info) - 10} more")

        message = (
            f"New tester feedback in Google Drive!\n\n"
            f"Folder: {FOLDER_NAME}\n"
            f"New files: {count}\n\n"
            f"Files:\n" + "\n".join(file_lines) + "\n\n"
            f"Downloaded to: inbox/tester-feedback/\n"
            f"Check: ls /home/jared/projects/AI-CIV/aether/inbox/tester-feedback/"
        )

        import urllib.request
        import urllib.parse

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": message
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read())

        if result.get("ok"):
            log(f"Telegram notification sent for {count} new files")
            return True
        else:
            log(f"Telegram API error: {result}", "WARNING")
            return False

    except Exception as e:
        log(f"Telegram notification failed: {e}", "ERROR")
        return False


def check_for_new_files(force: bool = False) -> dict:
    """
    Check Google Drive folder for new files.
    Downloads new files and sends notifications.
    Returns summary dict.
    """
    log(f"Checking Google Drive folder: {FOLDER_NAME} ({FOLDER_ID})")

    state = load_state()
    state["last_check"] = datetime.now().isoformat()

    try:
        service = get_drive_service()
    except Exception as e:
        log(f"Failed to connect to Google Drive: {e}", "ERROR")
        return {"error": str(e), "new_files": []}

    # List all files in folder
    try:
        all_files = list_folder_files(service, FOLDER_ID, recursive=True)
    except Exception as e:
        log(f"Failed to list files: {e}", "ERROR")
        save_state(state)
        return {"error": str(e), "new_files": []}

    log(f"Found {len(all_files)} total files in folder")

    # Find new files (not in seen_file_ids)
    new_files = []
    for file_info in all_files:
        file_id = file_info["id"]
        if file_id not in state["seen_file_ids"] or force:
            new_files.append(file_info)

    log(f"New files to process: {len(new_files)}")

    if not new_files:
        save_state(state)
        return {"new_files": [], "total_in_folder": len(all_files)}

    # Download new files
    downloaded = []
    for file_info in new_files:
        file_id = file_info["id"]
        file_name = file_info["name"]

        log(f"Processing: {file_name} (type: {file_info['mimeType']})")

        local_path = download_file(service, file_info, DOWNLOAD_DIR)

        record = {
            "name": file_name,
            "drive_path": file_info.get("drive_path", file_name),
            "size": file_info.get("size", ""),
            "modified_time": file_info.get("modifiedTime", ""),
            "web_view_link": file_info.get("webViewLink", ""),
            "local_path": str(local_path) if local_path else None,
            "downloaded": local_path is not None,
            "downloaded_at": datetime.now().isoformat()
        }

        # Mark as seen regardless of download success
        state["seen_file_ids"][file_id] = record

        if local_path:
            state["total_files_downloaded"] += 1
            downloaded.append(record)
            log(f"Successfully downloaded: {file_name}")
        else:
            log(f"Could not download: {file_name}", "WARNING")

    # Send notification if any files downloaded
    if downloaded:
        send_telegram_notification(downloaded)

    save_state(state)

    return {
        "new_files": downloaded,
        "total_in_folder": len(all_files),
        "total_seen": len(state["seen_file_ids"]),
        "total_downloaded": state["total_files_downloaded"]
    }


def list_known_files():
    """Print all known/seen files from state."""
    state = load_state()
    seen = state.get("seen_file_ids", {})

    if not seen:
        print("No files seen yet. Run 'check' first.")
        return

    print(f"\nKnown files ({len(seen)} total):")
    print("-" * 60)
    for file_id, info in seen.items():
        name = info.get("name", "Unknown")
        downloaded_at = info.get("downloaded_at", "")
        local_path = info.get("local_path", "Not downloaded")
        downloaded = info.get("downloaded", False)
        status = "OK" if downloaded else "FAILED"
        print(f"[{status}] {name}")
        print(f"       Downloaded: {downloaded_at[:19] if downloaded_at else 'N/A'}")
        print(f"       Local: {local_path}")
        print()

    print(f"\nLast check: {state.get('last_check', 'Never')}")
    print(f"Total downloaded: {state.get('total_files_downloaded', 0)}")


def run_daemon(interval_seconds: int = 300):
    """Run as a daemon, checking every interval_seconds."""
    log(f"Starting daemon mode (check every {interval_seconds}s = {interval_seconds//60}min)")

    # Send startup notification
    try:
        with open(TELEGRAM_CONFIG) as f:
            tg_config = json.load(f)
        import urllib.request, urllib.parse
        bot_token = tg_config.get("bot_token", "")
        chat_id = tg_config.get("default_chat_id", "548906264")
        if bot_token:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = urllib.parse.urlencode({
                "chat_id": chat_id,
                "text": f"GDrive tester monitor started. Watching: {FOLDER_NAME}\nChecking every {interval_seconds//60} minutes."
            }).encode("utf-8")
            urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10)
    except Exception:
        pass

    while True:
        try:
            result = check_for_new_files()
            new_count = len(result.get("new_files", []))
            total = result.get("total_in_folder", 0)
            log(f"Check complete. New: {new_count}, Total in folder: {total}")
        except Exception as e:
            log(f"Daemon check error: {e}", "ERROR")

        log(f"Sleeping {interval_seconds}s until next check...")
        time.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser(description="Google Drive Tester Feedback Monitor")
    parser.add_argument(
        "command",
        choices=["check", "daemon", "list"],
        nargs="?",
        default="check",
        help="Command to run (default: check)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download of all files"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Daemon check interval in seconds (default: 300 = 5 minutes)"
    )

    args = parser.parse_args()

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if args.command == "check":
        result = check_for_new_files(force=args.force)
        if "error" in result:
            print(f"\nERROR: {result['error']}")
            sys.exit(1)
        new_count = len(result.get("new_files", []))
        total = result.get("total_in_folder", 0)
        print(f"\nCheck complete:")
        print(f"  New files downloaded: {new_count}")
        print(f"  Total files in folder: {total}")
        print(f"  Total seen so far: {result.get('total_seen', 0)}")
        print(f"  Downloaded to: {DOWNLOAD_DIR}")
        if new_count > 0:
            print("\nNew files:")
            for f in result["new_files"]:
                status = "Downloaded" if f["downloaded"] else "Failed"
                print(f"  [{status}] {f['name']} -> {f['local_path']}")

    elif args.command == "daemon":
        run_daemon(interval_seconds=args.interval)

    elif args.command == "list":
        list_known_files()


if __name__ == "__main__":
    main()
