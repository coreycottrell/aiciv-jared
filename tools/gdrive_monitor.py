#!/usr/bin/env python3
"""
Google Drive Monitor for Aether

Monitors the "Aether Inbox" folder in Jared's Google Drive
- Recursively scans subfolders (departments, projects, etc.)
- Exports Google Docs/Sheets/Slides to readable formats
- Downloads binary files directly
- Maintains folder structure locally
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Will be available once libraries are installed
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
except ImportError:
    print("Google Drive libraries not installed yet")
    print("Waiting for: pip install google-auth google-auth-oauthlib google-api-python-client")
    exit(1)

# Google Docs export MIME types
EXPORT_FORMATS = {
    'application/vnd.google-apps.document': ('application/pdf', '.pdf'),
    'application/vnd.google-apps.spreadsheet': ('text/csv', '.csv'),
    'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),
    'application/vnd.google-apps.drawing': ('image/png', '.png'),
}

class GDriveMonitor:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.creds_path = self.base_path / ".credentials" / "google-drive-service-account.json"
        self.inbox_path = self.base_path / "docs" / "gdrive"  # Changed to docs/gdrive for organization
        self.state_file = self.base_path / ".gdrive_state.json"

        # Create inbox if doesn't exist
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        # Initialize service
        self.service = self._authenticate()
        self.inbox_folder_id = None

    def _authenticate(self):
        """Authenticate with Google Drive using service account"""
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

        credentials = service_account.Credentials.from_service_account_file(
            str(self.creds_path), scopes=SCOPES)

        return build('drive', 'v3', credentials=credentials)

    def _find_inbox_folder(self):
        """Find the 'Aether Inbox' folder shared with service account"""
        query = "name='Aether Inbox' and mimeType='application/vnd.google-apps.folder' and trashed=false"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        folders = results.get('files', [])

        if not folders:
            raise Exception("'Aether Inbox' folder not found. Make sure it's shared with the service account.")

        return folders[0]['id']

    def _load_state(self):
        """Load processed files state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {"processed_files": []}

    def _save_state(self, state):
        """Save processed files state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def list_all_files_recursive(self, folder_id=None, path_prefix=""):
        """Recursively list all files in folder and subfolders"""
        if folder_id is None:
            if not self.inbox_folder_id:
                self.inbox_folder_id = self._find_inbox_folder()
            folder_id = self.inbox_folder_id

        query = f"'{folder_id}' in parents and trashed=false"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, createdTime, modifiedTime, size)',
            orderBy='createdTime desc'
        ).execute()

        items = results.get('files', [])
        all_files = []

        for item in items:
            item['path_prefix'] = path_prefix

            if item['mimeType'] == 'application/vnd.google-apps.folder':
                # It's a folder - recurse into it
                subfolder_path = f"{path_prefix}/{item['name']}" if path_prefix else item['name']
                print(f"[{datetime.now()}] Scanning folder: {subfolder_path}")
                subfiles = self.list_all_files_recursive(item['id'], subfolder_path)
                all_files.extend(subfiles)
            else:
                # It's a file
                all_files.append(item)

        return all_files

    def list_new_files(self):
        """List files that haven't been processed (recursive)"""
        all_files = self.list_all_files_recursive()

        # Filter out already processed files
        state = self._load_state()
        processed = state.get('processed_files', {})

        new_files = []
        for f in all_files:
            file_id = f['id']
            modified_time = f.get('modifiedTime', '')

            # Check if file is new or modified since last process
            if file_id not in processed or processed[file_id] != modified_time:
                new_files.append(f)

        return new_files

    def download_file(self, file_info, local_folder):
        """Download or export a file from Google Drive"""
        file_id = file_info['id']
        file_name = file_info['name']
        mime_type = file_info['mimeType']

        # Ensure local folder exists
        local_folder.mkdir(parents=True, exist_ok=True)

        # Check if it's a Google Docs type that needs export
        if mime_type in EXPORT_FORMATS:
            export_mime, extension = EXPORT_FORMATS[mime_type]

            # Export the file
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType=export_mime
            )

            file_path = local_folder / f"{file_name}{extension}"
            print(f"[{datetime.now()}] Exporting {file_name} as {extension}...")

        else:
            # Regular file - download directly
            request = self.service.files().get_media(fileId=file_id)
            file_path = local_folder / file_name
            print(f"[{datetime.now()}] Downloading {file_name}...")

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                print(f"  Progress: {int(status.progress() * 100)}%")

        # Save file
        with open(file_path, 'wb') as f:
            f.write(fh.getvalue())

        return file_path

    def mark_processed(self, file_id, modified_time):
        """Mark a file as processed with its modification time"""
        state = self._load_state()
        if 'processed_files' not in state or isinstance(state['processed_files'], list):
            # Migrate from old format (list) to new format (dict with mod times)
            state['processed_files'] = {}
        state['processed_files'][file_id] = modified_time
        self._save_state(state)

    def check_and_download_new(self):
        """Check for new files and download them (recursive)"""
        new_files = self.list_new_files()

        downloaded = []

        for file in new_files:
            path_prefix = file.get('path_prefix', '')
            full_path = f"{path_prefix}/{file['name']}" if path_prefix else file['name']
            print(f"[{datetime.now()}] New/updated file: {full_path}")

            try:
                # Determine local folder based on path prefix
                if path_prefix:
                    local_folder = self.inbox_path / path_prefix
                else:
                    local_folder = self.inbox_path

                # Download/export file
                local_path = self.download_file(file, local_folder)
                print(f"[{datetime.now()}] Saved to: {local_path}")

                # Mark as processed with modification time
                self.mark_processed(file['id'], file.get('modifiedTime', ''))

                downloaded.append({
                    'name': file['name'],
                    'path': str(local_path),
                    'gdrive_path': full_path,
                    'size': file.get('size', 'unknown'),
                    'type': file.get('mimeType', 'unknown')
                })

            except Exception as e:
                print(f"[{datetime.now()}] Error downloading {file['name']}: {e}")
                import traceback
                traceback.print_exc()

        return downloaded


def main():
    """Main function - check for new files and download"""
    monitor = GDriveMonitor()

    print(f"[{datetime.now()}] Google Drive Monitor for Aether")
    print(f"[{datetime.now()}] Local storage: {monitor.inbox_path}")
    print(f"[{datetime.now()}] Checking Aether Inbox (recursive)...")

    try:
        downloaded = monitor.check_and_download_new()

        if downloaded:
            print(f"\n{'='*60}")
            print(f"[{datetime.now()}] Downloaded {len(downloaded)} file(s):")
            print(f"{'='*60}")
            for file in downloaded:
                print(f"\n  📄 {file['gdrive_path']}")
                print(f"     Type: {file['type']}")
                print(f"     Local: {file['path']}")
        else:
            print(f"[{datetime.now()}] No new or updated files")

    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


def list_all():
    """List all files in the monitored folder"""
    monitor = GDriveMonitor()
    print(f"[{datetime.now()}] Listing all files in Aether Inbox...")

    files = monitor.list_all_files_recursive()
    print(f"\nFound {len(files)} file(s):")
    for f in files:
        path = f"{f.get('path_prefix', '')}/{f['name']}" if f.get('path_prefix') else f['name']
        print(f"  - {path} ({f['mimeType']})")

    return files


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_all()
    else:
        main()
