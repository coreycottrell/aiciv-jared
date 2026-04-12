import React, { useState, useEffect } from 'react'
import PostCard from './PostCard.jsx'
import { fetchPosts, reactToPost } from '../api/posts.js'
import { useAuth } from '../App.jsx'

const SAMPLE_POSTS = [
  {
    id: '1',
    title: 'Zero Incident Month - March 2025',
    content: 'Proud to share that our team completed March with ZERO safety incidents! This is our third consecutive month. Key improvements: new pre-shift checklist, buddy system on the floor, and updated PPE protocols. Huge thanks to everyone for staying vigilant.',
    author_name: 'Sarah K.',
    department: 'Safety',
    tags: ['Safety', 'Win'],
    is_win: true,
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    reactions: { celebrate: 12, inspired: 8, learned: 3 },
    userReactions: [],
  },
  {
    id: '2',
    title: 'Process Efficiency Breakthrough',
    content: 'We redesigned the intake workflow and cut processing time from 47 minutes down to 28 minutes per unit. That\'s a 40% efficiency gain! The key was eliminating the double-entry step and automating the routing logic. Detailed SOP attached to the drive.',
    author_name: 'Marcus T.',
    department: 'Operations',
    tags: ['Efficiency', 'Innovation'],
    is_win: false,
    created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    reactions: { celebrate: 7, inspired: 15, learned: 11 },
    userReactions: [],
    gdrive_url: '#',
  },
  {
    id: '3',
    title: 'Customer Quality Score Hit 98.4%',
    content: 'Q1 quality scores are in and we hit 98.4% - up from 94.1% last quarter! The root cause analysis workshops we ran in January really paid off. Team identified 3 systemic issues and we\'ve since patched all three. This is what continuous improvement looks like.',
    author_name: 'Jared Sanborn',
    department: 'Leadership',
    tags: ['Quality', 'Win'],
    is_win: true,
    created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    reactions: { celebrate: 23, inspired: 18, learned: 6 },
    userReactions: [],
  },
]

export default function Dashboard({ onCreatePost }) {
  const { user } = useAuth()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    loadPosts()
  }, [])

  const loadPosts = async () => {
    setLoading(true)
    try {
      const data = await fetchPosts()
      // Merge API posts with sample posts (sample as fallback/seed data)
      const apiPosts = data || []
      setPosts(apiPosts.length > 0 ? apiPosts : SAMPLE_POSTS)
    } catch (err) {
      console.log('Using sample data:', err.message)
      setPosts(SAMPLE_POSTS)
    }
    setLoading(false)
  }

  const handleReact = async (postId, type, adding) => {
    try {
      await reactToPost(postId, type, adding, user?.name)
    } catch (err) {
      console.log('Reaction error:', err.message)
    }
  }

  const filteredPosts = filter === 'wins'
    ? posts.filter(p => p.is_win)
    : filter === 'all'
    ? posts
    : posts.filter(p => p.tags && p.tags.includes(filter))

  const stats = {
    total: posts.length,
    wins: posts.filter(p => p.is_win).length,
    reactions: posts.reduce((sum, p) => sum + Object.values(p.reactions || {}).reduce((a, b) => a + b, 0), 0),
  }

  return (
    <div>
      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Stories</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.wins}</div>
          <div className="stat-label">Team Wins</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.reactions}</div>
          <div className="stat-label">Reactions</div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Feed */}
        <div className="feed-column">
          {/* Filter Bar */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
            {[
              { key: 'all', label: 'All Posts' },
              { key: 'wins', label: '🏆 Wins' },
              { key: 'Safety', label: '🦺 Safety' },
              { key: 'Quality', label: '✅ Quality' },
              { key: 'Efficiency', label: '⚡ Efficiency' },
              { key: 'Innovation', label: '💡 Innovation' },
            ].map(f => (
              <button
                key={f.key}
                className={`btn btn-sm ${filter === f.key ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setFilter(f.key)}
              >
                {f.label}
              </button>
            ))}
          </div>

          {loading ? (
            <div className="loading-screen"><div className="spinner"></div></div>
          ) : filteredPosts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📭</div>
              <div className="empty-state-title">No posts yet</div>
              <div className="empty-state-text">Be the first to share a win or story with your team!</div>
              <button className="btn btn-orange" onClick={onCreatePost}>Share Your Story</button>
            </div>
          ) : (
            filteredPosts.map(post => (
              <PostCard key={post.id} post={post} onReact={handleReact} />
            ))
          )}
        </div>

        {/* Right Sidebar */}
        <div className="sidebar-column">
          <div className="widget">
            <div className="widget-title">Top Contributors</div>
            {[
              { name: 'Marcus T.', dept: 'Operations', score: 47 },
              { name: 'Sarah K.', dept: 'Safety', score: 38 },
              { name: 'Jared Sanborn', dept: 'Leadership', score: 31 },
              { name: 'Lisa M.', dept: 'Quality', score: 24 },
              { name: 'David R.', dept: 'Operations', score: 19 },
            ].map((member, i) => (
              <div key={member.name} className="leaderboard-item">
                <div className={`rank rank-${i + 1}`}>#{i + 1}</div>
                <div className="avatar" style={{ width: 28, height: 28, fontSize: 11 }}>
                  {member.name[0]}
                </div>
                <div className="leaderboard-name">
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{member.name}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{member.dept}</div>
                </div>
                <div className="leaderboard-score">{member.score}pts</div>
              </div>
            ))}
          </div>

          <div className="widget">
            <div className="widget-title">Tag Distribution</div>
            {[
              { tag: 'Safety', count: 8, color: 'var(--pb-blue)', cls: 'tag-safety' },
              { tag: 'Quality', count: 12, color: '#a78bfa', cls: 'tag-quality' },
              { tag: 'Efficiency', count: 9, color: '#4ade80', cls: 'tag-efficiency' },
              { tag: 'Innovation', count: 6, color: 'var(--pb-orange)', cls: 'tag-innovation' },
            ].map(item => (
              <div key={item.tag} style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span className={`tag ${item.cls}`}>{item.tag}</span>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{item.count} posts</span>
                </div>
                <div style={{ height: '4px', background: 'var(--bg-tertiary)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${(item.count / 35) * 100}%`,
                    background: item.color,
                    borderRadius: '2px'
                  }} />
                </div>
              </div>
            ))}
          </div>

          <div className="widget">
            <div className="widget-title">Drive Sync Status</div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>
              <span style={{ color: '#4ade80' }}>●</span> Connected to Google Drive
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Last sync: just now<br />
              Files synced: 24<br />
              Folder: PureBrain Hub Files
            </div>
            <div className="gdrive-badge" style={{ marginTop: 12 }}>
              ☁️ Auto-sync enabled
            </div>
          </div>

          <button className="btn btn-orange" style={{ width: '100%', justifyContent: 'center' }} onClick={onCreatePost}>
            ✨ Share a Win
          </button>
        </div>
      </div>
    </div>
  )
}
