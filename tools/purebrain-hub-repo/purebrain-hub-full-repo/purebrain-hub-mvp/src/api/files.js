/**
 * Files API - Upload, list, and manage team files
 * Backend: Express + local filesystem storage
 */

const BASE = '/api'

export async function fetchFiles(params = {}) {
  const query = new URLSearchParams(params).toString()
  const res = await fetch(`${BASE}/files${query ? '?' + query : ''}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function uploadFile(formData) {
  const res = await fetch(`${BASE}/files/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: 'Upload failed' }))
    throw new Error(err.error || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function syncToGDrive(fileId) {
  const res = await fetch(`${BASE}/files/${fileId}/sync-gdrive`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: 'Sync failed' }))
    throw new Error(err.error || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function deleteFile(id) {
  const res = await fetch(`${BASE}/files/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function getFileDownloadUrl(id) {
  return `${BASE}/files/${id}/download`
}
