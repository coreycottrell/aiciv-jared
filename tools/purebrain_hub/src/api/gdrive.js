/**
 * Google Drive API Stub
 *
 * This module provides the client-side interface for Google Drive sync operations.
 * On the server side, this connects to the existing Aether GDrive manager
 * located at: /home/jared/projects/AI-CIV/aether/tools/gdrive_manager.py
 *
 * INTEGRATION ARCHITECTURE:
 * 1. File uploaded to local storage via /api/files/upload
 * 2. Server calls python3 tools/gdrive_manager.py upload <local_path> <folder_id>
 * 3. GDrive file ID and URL stored in SQLite db
 * 4. Frontend polls /api/files/:id for sync status
 *
 * In production, replace stub with actual OAuth flow using:
 * - OAuth token: /home/jared/projects/AI-CIV/aether/.credentials/oauth-token.json
 * - Service account: /home/jared/projects/AI-CIV/aether/.credentials/google-drive-service-account.json
 */

const BASE = '/api/gdrive'

/**
 * Get Google Drive connection status
 * Returns: { connected: bool, email: string, folder_id: string, folder_name: string }
 */
export async function getGDriveStatus() {
  const res = await fetch(`${BASE}/status`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

/**
 * Trigger manual sync of all unsynced files
 * Returns: { synced: number, failed: number, files: Array }
 */
export async function triggerFullSync() {
  const res = await fetch(`${BASE}/sync-all`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

/**
 * Get list of files in the Google Drive Hub folder
 * Returns: Array of GDrive file objects
 */
export async function listDriveFiles(folderId) {
  const url = folderId ? `${BASE}/files?folder=${folderId}` : `${BASE}/files`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

/**
 * Create a new folder in Google Drive
 * Returns: { folder_id: string, folder_url: string }
 */
export async function createDriveFolder(name, parentFolderId) {
  const res = await fetch(`${BASE}/folders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, parent_folder_id: parentFolderId }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

// ============================================================
// SERVER-SIDE INTEGRATION (how the Express server calls Python)
// ============================================================
//
// The Express server at server/index.js calls these Python commands:
//
// UPLOAD FILE:
//   python3 /home/jared/projects/AI-CIV/aether/tools/gdrive_manager.py \
//     upload <local_file_path> --folder-id <hub_folder_id>
//
// LIST FOLDER:
//   python3 /home/jared/projects/AI-CIV/aether/tools/gdrive_manager.py \
//     list --folder-id <hub_folder_id>
//
// AUTH:
//   Uses existing oauth-token.json at:
//   /home/jared/projects/AI-CIV/aether/.credentials/oauth-token.json
//
// TARGET FOLDER:
//   "PureBrain Hub Files" folder in Google Drive
//   (auto-created on first sync if not exists)
// ============================================================
