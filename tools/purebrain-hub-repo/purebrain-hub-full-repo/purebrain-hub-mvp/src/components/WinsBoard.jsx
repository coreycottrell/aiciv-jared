import React, { useState, useEffect } from 'react'
import { fetchPosts } from '../api/posts.js'
import { formatDistanceToNow } from 'date-fns'

const SAMPLE_WINS = [
  {
    id: 'w1',
    title: 'Zero Incident Month',
    content: 'Third consecutive month with zero safety incidents on the production floor.',
    author_name: 'Sarah K.',
    department: 'Safety',
    tags: ['Safety'],
    is_win: true,
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    reactions: { celebrate: 12, inspired: 8, learned: 3 },
    emoji: '🛡️',
    impact: 'Critical',
  },
  {
    id: 'w2',
    title: '40% Faster Processing',
    content: 'Redesigned intake workflow cut processing time from 47 to 28 minutes per unit.',
    author_name: 'Marcus T.',
    department: 'Operations',
    tags: ['Efficiency'],
    is_win: true,
    created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    reactions: { celebrate: 7, inspired: 15, learned: 11 },
    emoji: '⚡',
    impact: 'High',
  },
  {
    id: 'w3',
    title: 'Quality Score 98.4%',
    content: 'Q1 customer quality score hit 98.4%, up from 94.1% last quarter.',
    author_name: 'Jared Sanborn',
    department: 'Leadership',
    tags: ['Quality'],
    is_win: true,
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    reactions: { celebrate: 23, inspired: 18, learned: 6 },
    emoji: '✅',
    impact: 'Critical',
  },
  {
    id: 'w4',
    title: 'New Safety Protocol Adopted',
    content: 'Fleet-wide adoption of the enhanced PPE checklist across all 3 shifts.',
    author_name: 'Lisa M.',
    department: 'Safety',
    tags: ['Safety', 'Innovation'],
    is_win: true,
    created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    reactions: { celebrate: 9, inspired: 12, learned: 8 },
    emoji: '🦺',
    impact: 'High',
  },
  {
    id: 'w5',
    title: '$120K Cost Savings Q1',
    content: 'Waste reduction initiative eliminated $120K in material costs this quarter.',
    author_name: 'David R.',
    department: 'Operations',
    tags: ['Efficiency'],
    is_win: true,
    created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    reactions: { celebrate: 18, inspired: 9, learned: 5 },
    emoji: '💰',
    impact: 'Critical',
  },
  {
    id: 'w6',
    title: 'AI Root Cause Tool Launch',
    content: 'Deployed new AI-assisted root cause analysis tool - first in our region.',
    author_name: 'Tech Team',
    department: 'Innovation',
    tags: ['Innovation'],
    is_win: true,
    created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
    reactions: { celebrate: 14, inspired: 22, learned: 16 },
    emoji: '🤖',
    impact: 'Medium',
  },
]

const IMPACT_COLORS = {
  Critical: 'var(--pb-orange)',
  High: 'var(--pb-blue)',
  Medium: '#a78bfa',
  Low: '#4ade80',
}

const TAG_EMOJIS = {
  Safety: '🛡️',
  Quality: '✅',
  Efficiency: '⚡',
  Innovation: '💡',
}

export default function WinsBoard() {
  const [wins, setWins] = useState([])
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState('recent')
  const [filterTag, setFilterTag] = useState('all')

  useEffect(() => {
    loadWins()
  }, [])

  const loadWins = async () => {
    setLoading(true)
    try {
      const posts = await fetchPosts()
      const winPosts = (posts || []).filter(p => p.is_win)
      setWins(winPosts.length > 0 ? winPosts : SAMPLE_WINS)
    } catch {
      setWins(SAMPLE_WINS)
    }
    setLoading(false)
  }

  const sortedWins = [...wins].sort((a, b) => {
    if (sortBy === 'reactions') {
      const ra = Object.values(a.reactions || {}).reduce((x, y) => x + y, 0)
      const rb = Object.values(b.reactions || {}).reduce((x, y) => x + y, 0)
      return rb - ra
    }
    return new Date(b.created_at) - new Date(a.created_at)
  }).filter(w => filterTag === 'all' || (w.tags && w.tags.includes(filterTag)))

  const totalReactions = wins.reduce((sum, w) =>
    sum + Object.values(w.reactions || {}).reduce((a, b) => a + b, 0), 0
  )

  return (
    <div>
      {/* Header Stats */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(42,147,193,0.15), rgba(241,66,11,0.1))',
        border: '1px solid rgba(42,147,193,0.3)',
        borderRadius: 'var(--radius-xl)',
        padding: '28px 32px',
        marginBottom: '28px',
        display: 'flex',
        alignItems: 'center',
        gap: '32px',
      }}>
        <div>
          <div style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', marginBottom: '4px' }}>
            Team Wins Board
          </div>
          <div style={{ fontFamily: 'Oswald, sans-serif', fontSize: '36px', fontWeight: 700, color: 'var(--text-primary)' }}>
            {wins.length} <span style={{ color: 'var(--pb-blue)' }}>Wins</span> Celebrated
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            {totalReactions} total reactions from the team
          </div>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '16px' }}>
          {Object.entries(TAG_EMOJIS).map(([tag, emoji]) => {
            const count = wins.filter(w => w.tags?.includes(tag)).length
            return (
              <div key={tag} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px' }}>{emoji}</div>
                <div style={{ fontFamily: 'Oswald', fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)' }}>{count}</div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{tag}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          {[
            { key: 'all', label: 'All' },
            { key: 'Safety', label: '🛡️ Safety' },
            { key: 'Quality', label: '✅ Quality' },
            { key: 'Efficiency', label: '⚡ Efficiency' },
            { key: 'Innovation', label: '💡 Innovation' },
          ].map(f => (
            <button
              key={f.key}
              className={`btn btn-sm ${filterTag === f.key ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setFilterTag(f.key)}
            >
              {f.label}
            </button>
          ))}
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
          <button
            className={`btn btn-sm ${sortBy === 'recent' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setSortBy('recent')}
          >
            Most Recent
          </button>
          <button
            className={`btn btn-sm ${sortBy === 'reactions' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setSortBy('reactions')}
          >
            Most Celebrated
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-screen"><div className="spinner"></div></div>
      ) : sortedWins.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🏆</div>
          <div className="empty-state-title">No wins yet for this filter</div>
          <div className="empty-state-text">Start celebrating team achievements by posting a win!</div>
        </div>
      ) : (
        <div className="wins-grid">
          {sortedWins.map((win) => {
            const totalR = Object.values(win.reactions || {}).reduce((a, b) => a + b, 0)
            const timestamp = win.created_at
              ? formatDistanceToNow(new Date(win.created_at), { addSuffix: true })
              : 'recently'
            const impact = win.impact || (totalR > 15 ? 'Critical' : totalR > 8 ? 'High' : 'Medium')

            return (
              <div key={win.id} className="win-card">
                <div className="win-card-header">
                  <div className="win-emoji">{win.emoji || TAG_EMOJIS[win.tags?.[0]] || '🏆'}</div>
                  <div className="win-title">{win.title}</div>
                  <div className="win-impact" style={{ background: IMPACT_COLORS[impact] }}>
                    {impact}
                  </div>
                </div>
                <div className="win-card-body">
                  <p className="win-description">{win.content}</p>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
                    {(win.tags || []).map(t => {
                      const tagClasses = {
                        Safety: 'tag-safety', Quality: 'tag-quality',
                        Efficiency: 'tag-efficiency', Innovation: 'tag-innovation'
                      }
                      return <span key={t} className={`tag ${tagClasses[t] || 'tag-win'}`}>{t}</span>
                    })}
                  </div>
                  <div className="win-stats">
                    <div className="win-stat">
                      <span>👤</span>
                      <span>{win.author_name}</span>
                    </div>
                    <div className="win-stat">
                      <span>🎉</span>
                      <span>{totalR} reactions</span>
                    </div>
                    <div className="win-stat" style={{ marginLeft: 'auto' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{timestamp}</span>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
