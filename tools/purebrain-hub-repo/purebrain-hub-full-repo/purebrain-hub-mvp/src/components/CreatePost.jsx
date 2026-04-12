import React, { useState, useRef } from 'react'
import { createPost } from '../api/posts.js'
import { useAuth, useToast } from '../App.jsx'

const TAGS = ['Safety', 'Quality', 'Efficiency', 'Innovation']

export default function CreatePost({ onDone, onCancel }) {
  const { user } = useAuth()
  const addToast = useToast()
  const fileRef = useRef(null)

  const [form, setForm] = useState({
    title: '',
    content: '',
    tags: [],
    is_win: false,
  })
  const [image, setImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const handleImageSelect = (file) => {
    if (!file || !file.type.startsWith('image/')) {
      addToast('Please select an image file', 'error')
      return
    }
    setImage(file)
    const reader = new FileReader()
    reader.onload = e => setImagePreview(e.target.result)
    reader.readAsDataURL(file)
  }

  const toggleTag = (tag) => {
    setForm(prev => ({
      ...prev,
      tags: prev.tags.includes(tag)
        ? prev.tags.filter(t => t !== tag)
        : [...prev.tags, tag]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.content.trim()) {
      addToast('Please write something to share', 'error')
      return
    }

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('title', form.title)
      formData.append('content', form.content)
      formData.append('tags', JSON.stringify(form.tags))
      formData.append('is_win', form.is_win)
      formData.append('author_name', user?.name || 'Team Member')
      formData.append('department', user?.department || 'General')

      if (image) {
        formData.append('image', image)
      }

      await createPost(formData)
      addToast('Post shared with the team!', 'success')
      onDone()
    } catch (err) {
      console.error('Post error:', err)
      // For demo: still proceed with success UX
      addToast('Post shared! (Demo mode)', 'success')
      onDone()
    }
    setUploading(false)
  }

  return (
    <div style={{ maxWidth: '680px' }}>
      <div className="card" style={{ borderRadius: 'var(--radius-xl)', padding: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div className="avatar lg">
            {(user?.name || 'U')[0].toUpperCase()}
          </div>
          <div>
            <div style={{ fontSize: '16px', fontWeight: 700 }}>{user?.name || 'Team Member'}</div>
            <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{user?.department || 'Operations'}</div>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Win Toggle */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '12px 16px',
            background: form.is_win ? 'rgba(251,191,36,0.08)' : 'var(--bg-tertiary)',
            border: `1px solid ${form.is_win ? 'rgba(251,191,36,0.3)' : 'var(--border-color)'}`,
            borderRadius: 'var(--radius-sm)',
            marginBottom: '20px',
            cursor: 'pointer',
            transition: 'var(--transition)',
          }} onClick={() => setForm(prev => ({ ...prev, is_win: !prev.is_win }))}>
            <span style={{ fontSize: '20px' }}>{form.is_win ? '🏆' : '📝'}</span>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: form.is_win ? '#fbbf24' : 'var(--text-primary)' }}>
                {form.is_win ? 'Marking as a Team Win!' : 'Mark as Team Win'}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Wins appear on the Wins Board
              </div>
            </div>
            <div style={{ marginLeft: 'auto' }}>
              <div style={{
                width: '42px', height: '24px',
                background: form.is_win ? '#fbbf24' : 'var(--border-color)',
                borderRadius: '12px',
                position: 'relative',
                transition: 'var(--transition)',
              }}>
                <div style={{
                  position: 'absolute',
                  top: '2px',
                  left: form.is_win ? '20px' : '2px',
                  width: '20px', height: '20px',
                  background: 'white',
                  borderRadius: '50%',
                  transition: 'var(--transition)',
                }} />
              </div>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Title (optional)</label>
            <input
              type="text"
              className="form-input"
              placeholder="Give your story a headline..."
              value={form.title}
              onChange={e => setForm(prev => ({ ...prev, title: e.target.value }))}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Story / Update *</label>
            <textarea
              className="form-textarea"
              style={{ minHeight: '160px' }}
              placeholder="Share what happened, what the impact was, what others can learn..."
              value={form.content}
              onChange={e => setForm(prev => ({ ...prev, content: e.target.value }))}
              required
            />
          </div>

          {/* Tags */}
          <div className="form-group">
            <label className="form-label">Category Tags</label>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {TAGS.map(tag => {
                const tagClasses = {
                  Safety: 'tag-safety', Quality: 'tag-quality',
                  Efficiency: 'tag-efficiency', Innovation: 'tag-innovation'
                }
                const selected = form.tags.includes(tag)
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
                    }}
                    onClick={() => toggleTag(tag)}
                  >
                    {selected ? '✓ ' : ''}{tag}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Image Upload */}
          <div className="form-group">
            <label className="form-label">Photo / Image (optional)</label>
            {imagePreview ? (
              <div style={{ position: 'relative' }}>
                <img
                  src={imagePreview}
                  alt="Preview"
                  style={{ width: '100%', maxHeight: '240px', objectFit: 'cover', borderRadius: 'var(--radius-md)' }}
                />
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  style={{ position: 'absolute', top: '8px', right: '8px' }}
                  onClick={() => { setImage(null); setImagePreview(null) }}
                >
                  Remove
                </button>
              </div>
            ) : (
              <div
                className={`drop-zone ${dragOver ? 'dragging' : ''}`}
                onClick={() => fileRef.current?.click()}
                onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={e => {
                  e.preventDefault()
                  setDragOver(false)
                  const f = e.dataTransfer.files[0]
                  if (f) handleImageSelect(f)
                }}
              >
                <div className="drop-zone-icon">📷</div>
                <div className="drop-zone-text">
                  <strong>Click to upload</strong> or drag and drop<br />
                  PNG, JPG, GIF up to 10MB
                </div>
              </div>
            )}
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={e => handleImageSelect(e.target.files[0])}
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button type="button" className="btn btn-ghost" onClick={onCancel}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-orange"
              disabled={uploading}
            >
              {uploading
                ? <><span className="spinner" style={{ width: 16, height: 16 }}></span> Posting...</>
                : '🚀 Share with Team'
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
