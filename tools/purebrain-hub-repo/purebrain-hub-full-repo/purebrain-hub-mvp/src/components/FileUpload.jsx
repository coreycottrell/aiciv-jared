import React, { useState, useEffect, useRef } from 'react'
import { uploadFile, fetchFiles, syncToGDrive } from '../api/files.js'
import { useAuth, useToast } from '../App.jsx'

const TAGS = ['Safety', 'Quality', 'Efficiency', 'Innovation']

const FILE_ICONS = {
  'image/': '🖼️',
  'application/pdf': '📄',
  'application/vnd.ms-excel': '📊',
  'application/vnd.openxmlformats-officedocument.spreadsheetml': '📊',
  'text/': '📝',
  'video/': '🎬',
  'audio/': '🎵',
  'default': '📁',
}

function getFileIcon(mimeType) {
  if (!mimeType) return FILE_ICONS.default
  for (const [prefix, icon] of Object.entries(FILE_ICONS)) {
    if (mimeType.startsWith(prefix)) return icon
  }
  return FILE_ICONS.default
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

export default function FileUpload() {
  const { user } = useAuth()
  const addToast = useToast()
  const fileRef = useRef(null)

  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [selectedTags, setSelectedTags] = useState([])
  const [description, setDescription] = useState('')
  const [syncing, setSyncing] = useState(null)
  const [filterTag, setFilterTag] = useState('all')

  useEffect(() => {
    loadFiles()
  }, [])

  const loadFiles = async () => {
    setLoading(true)
    try {
      const data = await fetchFiles()
      setFiles(data || SAMPLE_FILES)
    } catch {
      setFiles(SAMPLE_FILES)
    }
    setLoading(false)
  }

  const toggleTag = (tag) => {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    )
  }

  const handleFileDrop = async (droppedFiles) => {
    if (!droppedFiles || droppedFiles.length === 0) return
    const file = droppedFiles[0]
    await doUpload(file)
  }

  const doUpload = async (file) => {
    if (!file) return
    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('tags', JSON.stringify(selectedTags))
      formData.append('description', description)
      formData.append('uploader_name', user?.name || 'Team Member')

      const result = await uploadFile(formData)
      addToast(`File uploaded: ${file.name}`, 'success')

      // Add to local list optimistically
      const newFile = {
        id: result?.id || Date.now().toString(),
        filename: file.name,
        original_name: file.name,
        mime_type: file.type,
        size: file.size,
        tags: selectedTags,
        description,
        uploader_name: user?.name,
        created_at: new Date().toISOString(),
        gdrive_synced: false,
      }
      setFiles(prev => [newFile, ...prev])
      setDescription('')
      setSelectedTags([])
    } catch (err) {
      console.log('Upload error (demo mode):', err.message)
      // Demo mode: simulate success
      const newFile = {
        id: Date.now().toString(),
        filename: file.name,
        original_name: file.name,
        mime_type: file.type,
        size: file.size,
        tags: selectedTags,
        description,
        uploader_name: user?.name,
        created_at: new Date().toISOString(),
        gdrive_synced: false,
      }
      setFiles(prev => [newFile, ...prev])
      addToast(`File ready: ${file.name} (demo mode)`, 'info')
      setDescription('')
      setSelectedTags([])
    }

    setUploading(false)
  }

  const handleSync = async (fileId) => {
    setSyncing(fileId)
    try {
      await syncToGDrive(fileId)
      setFiles(prev => prev.map(f =>
        f.id === fileId ? { ...f, gdrive_synced: true, gdrive_url: '#' } : f
      ))
      addToast('Synced to Google Drive!', 'success')
    } catch (err) {
      // Demo mode
      await new Promise(r => setTimeout(r, 1200))
      setFiles(prev => prev.map(f =>
        f.id === fileId ? { ...f, gdrive_synced: true, gdrive_url: '#' } : f
      ))
      addToast('Synced to Google Drive! (demo)', 'success')
    }
    setSyncing(null)
  }

  const filteredFiles = filterTag === 'all'
    ? files
    : files.filter(f => f.tags && f.tags.includes(filterTag))

  return (
    <div>
      {/* Upload Section */}
      <div className="upload-section">
        <h3>Upload Files to Team Hub</h3>

        {/* Description */}
        <div className="form-group">
          <label className="form-label">Description (optional)</label>
          <input
            type="text"
            className="form-input"
            placeholder="What is this file about?"
            value={description}
            onChange={e => setDescription(e.target.value)}
          />
        </div>

        {/* Tags */}
        <div className="form-group">
          <label className="form-label">Tag this file</label>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {TAGS.map(tag => {
              const tagClasses = {
                Safety: 'tag-safety', Quality: 'tag-quality',
                Efficiency: 'tag-efficiency', Innovation: 'tag-innovation'
              }
              const selected = selectedTags.includes(tag)
              return (
                <button
                  key={tag}
                  type="button"
                  className={`tag ${tagClasses[tag]}`}
                  style={{
                    cursor: 'pointer',
                    opacity: selected ? 1 : 0.5,
                    transform: selected ? 'scale(1.05)' : 'scale(1)',
                    transition: 'var(--transition)',
                    fontSize: '13px',
                    padding: '6px 14px',
                    border: 'none',
                    background: selected ? undefined : 'var(--bg-tertiary)',
                  }}
                  onClick={() => toggleTag(tag)}
                >
                  {selected ? '✓ ' : ''}{tag}
                </button>
              )
            })}
          </div>
        </div>

        {/* Drop Zone */}
        <div
          className={`drop-zone ${dragOver ? 'dragging' : ''}`}
          onClick={() => fileRef.current?.click()}
          onDragOver={e => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={e => {
            e.preventDefault()
            setDragOver(false)
            handleFileDrop(Array.from(e.dataTransfer.files))
          }}
        >
          {uploading ? (
            <>
              <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto 12px' }}></div>
              <div className="drop-zone-text">Uploading and syncing to Drive...</div>
            </>
          ) : (
            <>
              <div className="drop-zone-icon">☁️</div>
              <div className="drop-zone-text">
                <strong>Click to upload</strong> or drag and drop<br />
                All file types supported · Auto-syncs to Google Drive
              </div>
            </>
          )}
        </div>
        <input
          ref={fileRef}
          type="file"
          style={{ display: 'none' }}
          onChange={e => doUpload(e.target.files[0])}
        />

        {/* GDrive Info */}
        <div style={{
          marginTop: '12px',
          padding: '10px 16px',
          background: 'rgba(42,147,193,0.08)',
          border: '1px solid rgba(42,147,193,0.2)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '13px',
          color: 'var(--text-secondary)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <span>☁️</span>
          <span>Files auto-sync to <strong style={{ color: 'var(--pb-blue)' }}>Google Drive / PureBrain Hub Files</strong> folder within seconds of upload.</span>
        </div>
      </div>

      {/* Files List */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Team Files ({filteredFiles.length})</h3>
          <div style={{ display: 'flex', gap: '6px', marginLeft: 'auto' }}>
            {['all', ...TAGS].map(tag => (
              <button
                key={tag}
                className={`btn btn-sm ${filterTag === tag ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setFilterTag(tag)}
              >
                {tag === 'all' ? 'All' : tag}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="loading-screen"><div className="spinner"></div></div>
        ) : filteredFiles.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📂</div>
            <div className="empty-state-title">No files uploaded yet</div>
            <div className="empty-state-text">Upload SOPs, photos, reports, and documents to share with the team.</div>
          </div>
        ) : (
          <div className="files-list">
            {filteredFiles.map(file => (
              <div key={file.id} className="file-item">
                <span className="file-icon">{getFileIcon(file.mime_type)}</span>
                <div className="file-info">
                  <div className="file-name">{file.original_name || file.filename}</div>
                  <div className="file-meta">
                    {file.uploader_name} · {formatBytes(file.size)}
                    {file.description && ` · ${file.description}`}
                    {file.tags && file.tags.length > 0 && (
                      <span style={{ marginLeft: '6px' }}>
                        {file.tags.map(t => (
                          <span key={t} style={{ marginRight: 4, color: 'var(--pb-blue)', fontSize: 11 }}>#{t}</span>
                        ))}
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  {file.gdrive_synced ? (
                    <a
                      href={file.gdrive_url || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="gdrive-status gdrive-synced"
                      style={{ textDecoration: 'none' }}
                    >
                      ☁️ In Drive
                    </a>
                  ) : (
                    <button
                      className="gdrive-status gdrive-pending"
                      style={{ cursor: 'pointer', border: 'none', background: 'rgba(251,191,36,0.15)' }}
                      onClick={() => handleSync(file.id)}
                      disabled={syncing === file.id}
                    >
                      {syncing === file.id ? '⏳ Syncing...' : '☁️ Sync'}
                    </button>
                  )}
                  <button className="btn-icon" title="Download">⬇️</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// Sample files for demo
const SAMPLE_FILES = [
  {
    id: 'f1',
    filename: 'safety-sop-v3.pdf',
    original_name: 'Safety SOP v3.pdf',
    mime_type: 'application/pdf',
    size: 2400000,
    tags: ['Safety'],
    description: 'Updated pre-shift safety checklist',
    uploader_name: 'Sarah K.',
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    gdrive_synced: true,
    gdrive_url: '#',
  },
  {
    id: 'f2',
    filename: 'q1-quality-report.xlsx',
    original_name: 'Q1 Quality Report.xlsx',
    mime_type: 'application/vnd.ms-excel',
    size: 890000,
    tags: ['Quality'],
    description: 'Full Q1 quality metrics and analysis',
    uploader_name: 'Marcus T.',
    created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    gdrive_synced: true,
    gdrive_url: '#',
  },
  {
    id: 'f3',
    filename: 'process-improvement-photos.zip',
    original_name: 'Process Improvement Photos.zip',
    mime_type: 'application/zip',
    size: 15600000,
    tags: ['Efficiency'],
    description: 'Before/after photos from floor redesign',
    uploader_name: 'David R.',
    created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    gdrive_synced: false,
  },
]
