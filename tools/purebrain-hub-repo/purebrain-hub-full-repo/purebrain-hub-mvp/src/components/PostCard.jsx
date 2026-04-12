import React, { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { useAuth } from '../App.jsx'

const REACTION_TYPES = [
  { key: 'celebrate', emoji: '🎉', label: 'Celebrate' },
  { key: 'inspired', emoji: '💡', label: 'Inspired' },
  { key: 'learned', emoji: '📚', label: 'Learned' },
]

const TAG_CLASSES = {
  Safety: 'tag-safety',
  Quality: 'tag-quality',
  Efficiency: 'tag-efficiency',
  Innovation: 'tag-innovation',
  Win: 'tag-win',
}

export default function PostCard({ post, onReact }) {
  const { user } = useAuth()
  const [reactions, setReactions] = useState(post.reactions || {})
  const [userReactions, setUserReactions] = useState(post.userReactions || [])

  const handleReaction = async (type) => {
    const hasReacted = userReactions.includes(type)

    // Optimistic update
    const newReactions = { ...reactions }
    const newUserReactions = hasReacted
      ? userReactions.filter(r => r !== type)
      : [...userReactions, type]

    if (hasReacted) {
      newReactions[type] = Math.max(0, (newReactions[type] || 0) - 1)
    } else {
      newReactions[type] = (newReactions[type] || 0) + 1
    }

    setReactions(newReactions)
    setUserReactions(newUserReactions)

    // Call API
    if (onReact) {
      onReact(post.id, type, !hasReacted)
    }
  }

  const timestamp = post.created_at
    ? formatDistanceToNow(new Date(post.created_at), { addSuffix: true })
    : 'just now'

  return (
    <div className="post-card">
      <div className="post-header">
        <div className="avatar">
          {(post.author_name || 'U')[0].toUpperCase()}
        </div>
        <div className="post-author-info">
          <div className="post-author-name">{post.author_name || 'Team Member'}</div>
          <div className="post-meta">
            <span>{post.department || 'Operations'}</span>
            <span>·</span>
            <span>{timestamp}</span>
          </div>
        </div>
        {post.is_win && (
          <div className="tag tag-win" style={{ marginLeft: 'auto' }}>🏆 Win</div>
        )}
      </div>

      {post.image_url && (
        <img
          src={post.image_url}
          alt="Post image"
          className="post-image"
          onError={e => { e.target.style.display = 'none' }}
        />
      )}

      <div className="post-body">
        {post.title && (
          <h3 style={{ fontSize: '17px', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
            {post.title}
          </h3>
        )}
        <p className="post-text">{post.content}</p>

        {post.tags && post.tags.length > 0 && (
          <div className="tag-list">
            {post.tags.map(tag => (
              <span key={tag} className={`tag ${TAG_CLASSES[tag] || 'tag-safety'}`}>
                {tag}
              </span>
            ))}
          </div>
        )}

        {post.gdrive_url && (
          <div style={{ marginTop: '8px' }}>
            <a
              href={post.gdrive_url}
              target="_blank"
              rel="noopener noreferrer"
              className="gdrive-badge"
              style={{ textDecoration: 'none' }}
            >
              ☁️ View in Google Drive
            </a>
          </div>
        )}
      </div>

      <div className="reactions-bar">
        {REACTION_TYPES.map(r => (
          <button
            key={r.key}
            className={`reaction-btn ${userReactions.includes(r.key) ? 'active' : ''}`}
            onClick={() => handleReaction(r.key)}
            title={r.label}
          >
            <span>{r.emoji}</span>
            <span className="reaction-count">{reactions[r.key] || 0}</span>
          </button>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-muted)' }}>
          {Object.values(reactions).reduce((a, b) => a + b, 0)} reactions
        </span>
      </div>
    </div>
  )
}
