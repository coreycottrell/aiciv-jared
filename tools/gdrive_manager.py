#!/usr/bin/env python3
"""
Google Drive Manager for Aether

Full read/write access to Google Drive folders.
- Upload files to any shared folder
- Create folders and nested structures
- Download/export files
- Monitor for new files

AUTHENTICATION PRIORITY:
1. OAuth2 token (oauth-token.json) - Full access as account owner, no quotas
2. Service Account (google-drive-service-account.json) - Fallback, has quotas

Run tools/gdrive_oauth_setup.py to set up OAuth2 authentication.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

try:
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials as OAuthCredentials
    from google.auth.transport.requests import Request
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

# Scopes for full Drive access
SCOPES = [
    'https://www.googleapis.com/auth/drive',           # Full Drive access
    'https://www.googleapis.com/auth/spreadsheets',    # Full Sheets access
]


class GDriveManager:
    """Full-featured Google Drive manager with read/write capabilities."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.base_path = Path(__file__).parent.parent
        self.creds_dir = self.base_path / ".credentials"
        self.oauth_token_path = self.creds_dir / "oauth-token.json"
        self.service_account_path = self.creds_dir / "google-drive-service-account.json"
        self.local_path = self.base_path / "docs" / "gdrive"
        self.state_file = self.base_path / ".gdrive_state.json"
        self.folder_cache = {}  # Cache folder IDs
        self.auth_type = None  # Track which auth method is being used

        # Create local storage if doesn't exist
        self.local_path.mkdir(parents=True, exist_ok=True)

        # Initialize service with best available credentials
        self.service = self._authenticate()

    def _log(self, message: str):
        """Print message if verbose mode is on."""
        if self.verbose:
            print(message)

    def _get_oauth_credentials(self) -> Optional[OAuthCredentials]:
        """Try to load OAuth2 credentials from token file."""
        if not self.oauth_token_path.exists():
            return None

        try:
            creds = OAuthCredentials.from_authorized_user_file(
                str(self.oauth_token_path), SCOPES
            )

            # Check if token is valid
            if creds.valid:
                return creds

            # Try to refresh expired token
            if creds.expired and creds.refresh_token:
                self._log("[AUTH] OAuth token expired, refreshing...")
                creds.refresh(Request())

                # Save refreshed token
                self._save_oauth_token(creds)
                self._log("[AUTH] OAuth token refreshed successfully")
                return creds

            return None

        except Exception as e:
            self._log(f"[AUTH] OAuth token error: {e}")
            return None

    def _save_oauth_token(self, creds: OAuthCredentials):
        """Save refreshed OAuth credentials."""
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': list(creds.scopes) if creds.scopes else SCOPES,
        }

        with open(self.oauth_token_path, 'w') as f:
            json.dump(token_data, f, indent=2)

        os.chmod(self.oauth_token_path, 0o600)

    def _get_service_account_credentials(self):
        """Load service account credentials."""
        if not self.service_account_path.exists():
            return None

        try:
            return service_account.Credentials.from_service_account_file(
                str(self.service_account_path), scopes=SCOPES
            )
        except Exception as e:
            self._log(f"[AUTH] Service account error: {e}")
            return None

    def _authenticate(self):
        """
        Authenticate with Google Drive using best available credentials.

        Priority:
        1. OAuth2 token (owner access, no quotas)
        2. Service Account (has quotas, requires sharing)
        """
        # Try OAuth2 first (preferred)
        oauth_creds = self._get_oauth_credentials()
        if oauth_creds:
            self.auth_type = "oauth2"
            self._log("[AUTH] Using OAuth2 credentials (owner access)")
            return build('drive', 'v3', credentials=oauth_creds)

        # Fall back to service account
        sa_creds = self._get_service_account_credentials()
        if sa_creds:
            self.auth_type = "service_account"
            self._log("[AUTH] Using Service Account credentials (may have quota limits)")
            self._log("[AUTH] TIP: Run 'python tools/gdrive_oauth_setup.py' for owner access")
            return build('drive', 'v3', credentials=sa_creds)

        raise Exception(
            "No valid credentials found!\n"
            f"  OAuth token: {self.oauth_token_path} (not found)\n"
            f"  Service account: {self.service_account_path} (not found)\n"
            "\nRun: python tools/gdrive_oauth_setup.py to set up OAuth authentication"
        )

    def get_auth_info(self) -> Dict:
        """Return information about current authentication."""
        return {
            'auth_type': self.auth_type,
            'oauth_token_exists': self.oauth_token_path.exists(),
            'service_account_exists': self.service_account_path.exists(),
            'recommendation': (
                'Using OAuth2 (optimal)' if self.auth_type == 'oauth2'
                else 'Run gdrive_oauth_setup.py for better access'
            )
        }

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

        self._log(f"[{datetime.now()}] Created folder: {folder_name} (ID: {folder_id})")
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
        """List all folders shared with the current account.

        Note: With OAuth2, this returns folders shared with the user.
              With Service Account, this returns folders shared with the SA.
        """
        query = "mimeType='application/vnd.google-apps.folder' and trashed=false"

        # Only add sharedWithMe for service account (OAuth user owns their files)
        if self.auth_type == "service_account":
            query += " and sharedWithMe=true"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, owners)',
            pageSize=100
        ).execute()

        return results.get('files', [])

    def list_my_drive_root(self) -> List[Dict]:
        """List files and folders in the root of My Drive.

        Only works with OAuth2 authentication.
        """
        if self.auth_type != "oauth2":
            self._log("[WARN] list_my_drive_root works best with OAuth2 auth")

        query = "'root' in parents and trashed=false"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, modifiedTime)',
            orderBy='name',
            pageSize=100
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

        self._log(f"[{datetime.now()}] Uploaded: {file_name}")
        self._log(f"  -> ID: {file.get('id')}")
        if file.get('webViewLink'):
            self._log(f"  -> Link: {file.get('webViewLink')}")

        return file.get('id')

    def upload_content(self, content: str, filename: str, folder_id: str,
                       mime_type: str = 'text/plain') -> str:
        """Upload content directly as a file (without saving locally first).

        Returns the uploaded file's ID.
        """
        # MediaFileUpload doesn't accept BytesIO directly, need temp file approach
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

        self._log(f"[{datetime.now()}] Downloaded: {file_path}")
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

    if len(sys.argv) < 2:
        print("Google Drive Manager for Aether")
        print("\nUsage:")
        print("  python gdrive_manager.py auth-info         # Show authentication status")
        print("  python gdrive_manager.py list-shared       # List shared folders")
        print("  python gdrive_manager.py list-root         # List My Drive root (OAuth only)")
        print("  python gdrive_manager.py list <folder>     # List files in folder")
        print("  python gdrive_manager.py upload <file> <path>  # Upload file")
        print("  python gdrive_manager.py mkdir <path>      # Create folder path")
        return

    command = sys.argv[1]

    manager = GDriveManager()

    if command == 'auth-info':
        info = manager.get_auth_info()
        print("Authentication Info:")
        print(f"  Auth type: {info['auth_type']}")
        print(f"  OAuth token exists: {info['oauth_token_exists']}")
        print(f"  Service account exists: {info['service_account_exists']}")
        print(f"  Status: {info['recommendation']}")

    elif command == 'list-shared':
        print("Folders accessible to current account:")
        folders = manager.list_shared_folders()
        for f in folders:
            print(f"  - {f['name']} (ID: {f['id']})")
        if not folders:
            print("  (no folders found)")

    elif command == 'list-root':
        print("Files in My Drive root:")
        files = manager.list_my_drive_root()
        for f in files:
            file_type = 'folder' if f['mimeType'] == 'application/vnd.google-apps.folder' else 'file'
            print(f"  - [{file_type}] {f['name']}")
        if not files:
            print("  (empty)")

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
