#!/usr/bin/env python3
"""
Google Drive Manager for Aether

Full read/write access to Google Drive folders.
- Upload files to any shared folder
- Create folders and nested structures
- Download/export files
- Monitor for new files

This replaces the read-only gdrive_monitor.py with full capabilities.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
    import io
except ImportError:
    print("Google Drive libraries not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-api-python-client")
    exit(1)

# Google Docs export MIME types
EXPORT_FORMATS = {
    'application/vnd.google-apps.document': ('application/pdf', '.pdf'),
    'application/vnd.google-apps.spreadsheet': ('text/csv', '.csv'),
    'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),
    'application/vnd.google-apps.drawing': ('image/png', '.png'),
}

# Common file MIME types for upload
MIME_TYPES = {
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.html': 'text/html',
    '.htm': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.py': 'text/x-python',
    '.ts': 'text/typescript',
    '.tsx': 'text/typescript',
    '.pdf': 'application/pdf',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.csv': 'text/csv',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}


class GDriveManager:
    """Full-featured Google Drive manager with read/write capabilities."""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.creds_path = self.base_path / ".credentials" / "google-drive-service-account.json"
        self.local_path = self.base_path / "docs" / "gdrive"
        self.state_file = self.base_path / ".gdrive_state.json"
        self.folder_cache = {}  # Cache folder IDs

        # Create local storage if doesn't exist
        self.local_path.mkdir(parents=True, exist_ok=True)

        # Initialize service with FULL access
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive - FULL ACCESS (read + write)"""
        SCOPES = [
            'https://www.googleapis.com/auth/drive',  # Full access
        ]

        credentials = service_account.Credentials.from_service_account_file(
            str(self.creds_path), scopes=SCOPES)

        return build('drive', 'v3', credentials=credentials)

    # ==================== FOLDER OPERATIONS ====================

    def find_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Find a folder by name, optionally within a parent folder.

        Returns folder ID or None if not found.
        """
        cache_key = f"{parent_id or 'root'}:{folder_name}"
        if cache_key in self.folder_cache:
            return self.folder_cache[cache_key]

        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        folders = results.get('files', [])

        if folders:
            folder_id = folders[0]['id']
            self.folder_cache[cache_key] = folder_id
            return folder_id

        return None

    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Create a folder in Google Drive.

        Returns the new folder's ID.
        """
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_id:
            file_metadata['parents'] = [parent_id]

        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()

        folder_id = folder.get('id')

        # Cache it
        cache_key = f"{parent_id or 'root'}:{folder_name}"
        self.folder_cache[cache_key] = folder_id

        print(f"[{datetime.now()}] Created folder: {folder_name} (ID: {folder_id})")
        return folder_id

    def ensure_folder_path(self, path: str, root_folder_id: Optional[str] = None) -> str:
        """Ensure a folder path exists, creating folders as needed.

        path: "CTO/Pure Brain/Platform"
        Returns: ID of the deepest folder
        """
        parts = [p.strip() for p in path.split('/') if p.strip()]

        current_parent = root_folder_id

        for folder_name in parts:
            existing = self.find_folder(folder_name, current_parent)

            if existing:
                current_parent = existing
            else:
                current_parent = self.create_folder(folder_name, current_parent)

        return current_parent

    def list_shared_folders(self) -> List[Dict]:
        """List all folders shared with the service account."""
        query = "mimeType='application/vnd.google-apps.folder' and trashed=false and sharedWithMe=true"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, owners)'
        ).execute()

        return results.get('files', [])

    # ==================== FILE OPERATIONS ====================

    def upload_file(self, local_path: str, folder_id: str,
                    new_name: Optional[str] = None) -> str:
        """Upload a file to a Google Drive folder.

        Returns the uploaded file's ID.
        """
        local_path = Path(local_path)

        if not local_path.exists():
            raise FileNotFoundError(f"File not found: {local_path}")

        file_name = new_name or local_path.name
        extension = local_path.suffix.lower()
        mime_type = MIME_TYPES.get(extension, 'application/octet-stream')

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        media = MediaFileUpload(
            str(local_path),
            mimetype=mime_type,
            resumable=True
        )

        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()

        print(f"[{datetime.now()}] Uploaded: {file_name}")
        print(f"  → ID: {file.get('id')}")
        if file.get('webViewLink'):
            print(f"  → Link: {file.get('webViewLink')}")

        return file.get('id')

    def upload_content(self, content: str, filename: str, folder_id: str,
                       mime_type: str = 'text/plain') -> str:
        """Upload content directly as a file (without saving locally first).

        Returns the uploaded file's ID.
        """
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }

        # Create in-memory file
        fh = io.BytesIO(content.encode('utf-8'))

        media = MediaFileUpload(
            fh,
            mimetype=mime_type,
            resumable=True
        )

        # MediaFileUpload doesn't accept BytesIO directly, need temp file approach
        # Using alternative method
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix=Path(filename).suffix,
                                          delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            file_id = self.upload_file(tmp_path, folder_id, filename)
        finally:
            os.unlink(tmp_path)

        return file_id

    def download_file(self, file_id: str, local_folder: Path) -> Path:
        """Download a file from Google Drive."""
        # Get file metadata
        file_meta = self.service.files().get(
            fileId=file_id,
            fields='name, mimeType'
        ).execute()

        file_name = file_meta['name']
        mime_type = file_meta['mimeType']

        local_folder = Path(local_folder)
        local_folder.mkdir(parents=True, exist_ok=True)

        # Check if it's a Google Docs type that needs export
        if mime_type in EXPORT_FORMATS:
            export_mime, extension = EXPORT_FORMATS[mime_type]
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType=export_mime
            )
            file_path = local_folder / f"{file_name}{extension}"
        else:
            request = self.service.files().get_media(fileId=file_id)
            file_path = local_folder / file_name

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        with open(file_path, 'wb') as f:
            f.write(fh.getvalue())

        print(f"[{datetime.now()}] Downloaded: {file_path}")
        return file_path

    def list_files(self, folder_id: str) -> List[Dict]:
        """List all files in a folder."""
        query = f"'{folder_id}' in parents and trashed=false"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, modifiedTime, size)',
            orderBy='name'
        ).execute()

        return results.get('files', [])

    # ==================== CONVENIENCE METHODS ====================

    def upload_to_path(self, local_file: str, drive_path: str,
                       root_folder_name: str = "CTO") -> str:
        """Upload a file to a path like "CTO/Pure Brain/Landing Page".

        Creates folders as needed.
        Returns the uploaded file's ID.
        """
        # Find the root folder (must be shared with service account)
        root_id = self.find_folder(root_folder_name)

        if not root_id:
            raise Exception(f"Root folder '{root_folder_name}' not found. "
                          f"Make sure it's shared with the service account.")

        # Ensure the full path exists
        if drive_path:
            folder_id = self.ensure_folder_path(drive_path, root_id)
        else:
            folder_id = root_id

        # Upload the file
        return self.upload_file(local_file, folder_id)

    def upload_content_to_path(self, content: str, filename: str,
                                drive_path: str, root_folder_name: str = "CTO") -> str:
        """Upload content directly to a path.

        Example: upload_content_to_path("# README", "README.md", "Pure Brain/Platform")
        """
        root_id = self.find_folder(root_folder_name)

        if not root_id:
            raise Exception(f"Root folder '{root_folder_name}' not found.")

        if drive_path:
            folder_id = self.ensure_folder_path(drive_path, root_id)
        else:
            folder_id = root_id

        return self.upload_content(content, filename, folder_id)


# ==================== CLI INTERFACE ====================

def main():
    """CLI for Google Drive Manager."""
    import sys

    manager = GDriveManager()

    if len(sys.argv) < 2:
        print("Google Drive Manager for Aether")
        print("\nUsage:")
        print("  python gdrive_manager.py list-shared     # List shared folders")
        print("  python gdrive_manager.py list <folder>   # List files in folder")
        print("  python gdrive_manager.py upload <file> <path>  # Upload file")
        print("  python gdrive_manager.py mkdir <path>    # Create folder path")
        return

    command = sys.argv[1]

    if command == 'list-shared':
        print("Folders shared with service account:")
        folders = manager.list_shared_folders()
        for f in folders:
            print(f"  - {f['name']} (ID: {f['id']})")

    elif command == 'list' and len(sys.argv) >= 3:
        folder_name = sys.argv[2]
        folder_id = manager.find_folder(folder_name)
        if folder_id:
            files = manager.list_files(folder_id)
            print(f"Files in {folder_name}:")
            for f in files:
                print(f"  - {f['name']} ({f['mimeType']})")
        else:
            print(f"Folder not found: {folder_name}")

    elif command == 'upload' and len(sys.argv) >= 4:
        local_file = sys.argv[2]
        drive_path = sys.argv[3]

        file_id = manager.upload_to_path(local_file, drive_path)
        print(f"Uploaded! File ID: {file_id}")

    elif command == 'mkdir' and len(sys.argv) >= 3:
        path = sys.argv[2]
        folder_id = manager.ensure_folder_path(path)
        print(f"Folder path created. Final folder ID: {folder_id}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
