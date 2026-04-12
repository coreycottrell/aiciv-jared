import { useApp } from '../../context/AppContext.jsx'

function AiCIVLogoSVG() {
  return (
    <svg width="28" height="28" viewBox="0 0 100 100">
      <defs>
        <linearGradient id="logoGradSb" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#f1420b"/>
          <stop offset="100%" stopColor="#2a93c1"/>
        </linearGradient>
      </defs>
      <circle cx="50" cy="50" r="45" fill="url(#logoGradSb)"/>
      <text x="50" y="62" textAnchor="middle" fill="white" fontSize="32" fontWeight="bold" fontFamily="sans-serif">W</text>
    </svg>
  )
}

function ChatHistoryItem({ conv, active, onSelect, onDelete }) {
  const { dispatch } = useApp()
  const timeAgo = (ts) => {
    const diff = (Date.now() / 1000) - ts
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
    return `${Math.floor(diff / 86400)}d ago`
  }

  return (
    <div className={`chat-history-item${active ? ' active' : ''}`} onClick={() => onSelect(conv.id)}>
      <svg className="chat-history-item__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <div className="chat-history-item__content">
        <div className="chat-history-item__title">{conv.title || 'Untitled conversation'}</div>
        <div className="chat-history-item__meta">{conv.timestamp ? timeAgo(conv.timestamp) : ''}</div>
      </div>
      <div className="chat-history-item__actions">
        <button className="chat-history-item__action-btn chat-history-item__action-btn--delete"
          onClick={e => { e.stopPropagation(); onDelete(conv.id) }} title="Delete">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
          </svg>
        </button>
      </div>
    </div>
  )
}

function BrainItem({ brain, active, onSelect }) {
  return (
    <div className={`brain-item${active ? ' brain-item--active' : ''}`} onClick={() => onSelect(brain)}>
      <span className="brain-item__emoji">{brain.emoji || '🧠'}</span>
      <div className="brain-item__info">
        <div className="brain-item__name">{brain.name}</div>
        {brain.description && <div className="brain-item__desc">{brain.description}</div>}
      </div>
    </div>
  )
}

export default function Sidebar({ onNewChat }) {
  const { state, dispatch } = useApp()
  const { sidebarCollapsed, mobileSidebarOpen, conversations, activeConvId, brains, activeBrainId, aiName, activeView } = state

  const sidebarClass = [
    'sidebar',
    sidebarCollapsed ? 'collapsed' : '',
    mobileSidebarOpen ? 'mobile-open' : '',
  ].filter(Boolean).join(' ')

  const handleSelectConv = (convId) => {
    dispatch({ type: 'SET_ACTIVE_CONV', convId })
    dispatch({ type: 'SET_MOBILE_SIDEBAR', open: false })
  }

  const handleDeleteConv = (convId) => {
    const updated = conversations.filter(c => c.id !== convId)
    dispatch({ type: 'SET_CONVERSATIONS', conversations: updated })
  }

  const handleSelectBrain = (brain) => {
    if (activeBrainId === brain.id) {
      dispatch({ type: 'OPEN_OVERLAY', overlay: 'brain', data: { brainId: brain.id } })
    } else {
      dispatch({ type: 'SET_ACTIVE_BRAIN', brainId: brain.id })
    }
  }

  const handleNewChat = () => {
    dispatch({ type: 'SET_MOBILE_SIDEBAR', open: false })
    if (onNewChat) onNewChat()
  }

  // Group conversations by time
  const today = [], yesterday = [], older = []
  const nowSecs = Date.now() / 1000
  conversations.forEach(c => {
    const diff = nowSecs - (c.timestamp || 0)
    if (diff < 86400) today.push(c)
    else if (diff < 172800) yesterday.push(c)
    else older.push(c)
  })

  const aiInitials = aiName ? aiName.slice(0, 2).toUpperCase() : 'AI'

  return (
    <aside className={sidebarClass} id="sidebar">
      <div className="sidebar__header">
        <div className="sidebar__logo-icon"><AiCIVLogoSVG /></div>
        <div className="sidebar__logo-text">
          <span className="text-blue">Wit</span><span className="text-orange">ness</span>
        </div>
        <button className="sidebar__collapse-btn" onClick={() => dispatch({ type: 'TOGGLE_SIDEBAR' })} title="Collapse sidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="11 17 6 12 11 7"/><polyline points="18 17 13 12 18 7"/>
          </svg>
        </button>
      </div>

      <button className="sidebar__new-chat" onClick={handleNewChat}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>New Chat</span>
      </button>

      <div className="sidebar__collapsible">
        {/* AI Profile */}
        <div className="ai-profile">
          <div className="ai-profile__card">
            <div className="ai-profile__avatar">
              <div className="ai-profile__avatar-inner">{aiInitials}</div>
              <div className="ai-profile__status"></div>
            </div>
            <div className="ai-profile__name">{aiName || 'AiCIV'}</div>
            <div className="ai-profile__hint">AI Civilization</div>
          </div>
        </div>

        <nav className="sidebar__nav">
          {/* Workspace — real connections */}
          <div className="nav-section">
            <div className="nav-section__title">Workspace</div>
            <div
              className={`nav-item${activeView === 'chat' ? ' active' : ''}`}
              onClick={() => dispatch({ type: 'SET_ACTIVE_VIEW', view: 'chat' })}
            >
              <svg className="nav-item__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              Chat
            </div>
            <div
              className={`nav-item${activeView === 'terminal' ? ' active' : ''}`}
              onClick={() => dispatch({ type: 'SET_ACTIVE_VIEW', view: 'terminal' })}
            >
              <svg className="nav-item__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>
              </svg>
              Terminal
            </div>
            <div
              className={`nav-item${activeView === 'status' ? ' active' : ''}`}
              onClick={() => dispatch({ type: 'SET_ACTIVE_VIEW', view: 'status' })}
            >
              <svg className="nav-item__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
              Status
            </div>
          </div>

          {/* Conversations */}
          <div className="nav-section">
            <div className="nav-section__title">Conversations</div>
            <div className="chat-history">
              {conversations.length === 0 && (
                <div className="chat-history-empty">No recent chats</div>
              )}
              {today.length > 0 && (
                <>
                  <div className="chat-history__group-title">Today</div>
                  {today.map(c => (
                    <ChatHistoryItem key={c.id} conv={c} active={activeConvId === c.id}
                      onSelect={handleSelectConv} onDelete={handleDeleteConv} />
                  ))}
                </>
              )}
              {yesterday.length > 0 && (
                <>
                  <div className="chat-history__group-title">Yesterday</div>
                  {yesterday.map(c => (
                    <ChatHistoryItem key={c.id} conv={c} active={activeConvId === c.id}
                      onSelect={handleSelectConv} onDelete={handleDeleteConv} />
                  ))}
                </>
              )}
              {older.length > 0 && (
                <>
                  <div className="chat-history__group-title">Older</div>
                  {older.map(c => (
                    <ChatHistoryItem key={c.id} conv={c} active={activeConvId === c.id}
                      onSelect={handleSelectConv} onDelete={handleDeleteConv} />
                  ))}
                </>
              )}
            </div>
          </div>

          {/* Tasks */}
          <div className="nav-section">
            <div className="nav-section__title">
              Tasks
              {state.tasks.filter(t => t.status === 'pending' || t.status === 'running').length > 0 && (
                <span className="task-queue-badge">
                  {state.tasks.filter(t => t.status === 'pending' || t.status === 'running').length}
                </span>
              )}
            </div>
            <div className="new-project-btn" onClick={() => dispatch({ type: 'SHOW_COMING_SOON', title: 'Task Scheduling', text: 'Schedule automated tasks, set recurring workflows, and delegate to agents.', icon: '⏰' })}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
              Schedule Task
            </div>
            {state.tasks.slice(0, 5).map(task => (
              <div key={task.id} className={`task-item task-item--${task.status}`}>
                <span className="task-item__icon">
                  {task.status === 'running' ? '⚡' : task.status === 'completed' ? '✅' : '⏳'}
                </span>
                <div className="task-item__info">
                  <div className="task-item__title">{task.title || task.name || 'Task'}</div>
                </div>
              </div>
            ))}
          </div>

          {/* BOOPs — TODO: Connect to /api/boop/status on gateway */}
          <div className="nav-section">
            <div className="nav-section__title" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              BOOPs
              <span style={{ fontSize: '0.58rem', color: 'var(--muted)', background: 'var(--hover-bg)', padding: '1px 6px', borderRadius: 8, letterSpacing: '0.03em' }}>TODO</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--muted)', padding: '6px 0' }}>
              Needs gateway connection
            </div>
          </div>

          {/* Brains */}
          <div className="nav-section">
            <div className="nav-section__title">Brains</div>
            <div style={{ display: 'flex', gap: '4px' }}>
              <div className="new-project-btn" style={{ flex: 1 }} onClick={() => dispatch({ type: 'OPEN_MODAL', modal: 'createBrain' })}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                New Brain
              </div>
              <div className="new-project-btn" style={{ flex: 1 }} onClick={() => dispatch({ type: 'OPEN_OVERLAY', overlay: 'brainStore', data: {} })}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
                  <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
                </svg>
                Catalog
              </div>
            </div>
            {brains.map(brain => (
              <BrainItem key={brain.id} brain={brain} active={activeBrainId === brain.id} onSelect={handleSelectBrain} />
            ))}
            {brains.length === 0 && (
              <div style={{ fontSize: '0.75rem', color: 'var(--muted)', padding: '8px 12px' }}>No brains yet</div>
            )}
          </div>

          {/* Skills */}
          <div className="skills-update" onClick={() => dispatch({ type: 'OPEN_MODAL', modal: 'skills' })}>
            <div className="skills-update__header">
              <div className="skills-update__title">🧠 AICIV Skills</div>
            </div>
            <div className="skills-update__item">
              <div className="skills-update__icon">🧠</div>
              <div>
                <div className="skills-update__name">
                  {state.skills.length > 0 ? `${state.skills.length} skills available` : 'Skills available'}
                </div>
                <div className="skills-update__desc">Tap to explore civilization capabilities</div>
              </div>
            </div>
          </div>

          {/* Projects */}
          <div className="nav-section" style={{ cursor: 'pointer' }} onClick={() => dispatch({ type: 'SHOW_COMING_SOON', title: 'Projects', text: 'Project management is coming soon. Organize conversations and files into projects.', icon: '📁' })}>
            <div className="nav-section__title">
              Projects
              <span style={{ marginLeft: 'auto', fontSize: '0.6rem', color: 'var(--muted)', background: 'var(--hover-bg)', padding: '2px 8px', borderRadius: '8px' }}>Soon</span>
            </div>
          </div>

          {/* Goals */}
          <div className="nav-section" style={{ cursor: 'pointer' }} onClick={() => dispatch({ type: 'SHOW_COMING_SOON', title: 'Goals', text: 'Goal tracking is coming soon. Set objectives, define milestones, and track progress.', icon: '🎯' })}>
            <div className="nav-section__title">
              Goals
              <span style={{ marginLeft: 'auto', fontSize: '0.6rem', color: 'var(--muted)', background: 'var(--hover-bg)', padding: '2px 8px', borderRadius: '8px' }}>Soon</span>
            </div>
          </div>

          {/* Account */}
          <div className="nav-section">
            <div className="nav-section__title">Account</div>
            <div className="nav-item" onClick={() => dispatch({ type: 'OPEN_SETTINGS', tab: 'appearance' })}>
              <svg className="nav-item__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
              Settings
            </div>
            <div className="nav-item" onClick={() => dispatch({ type: 'SHOW_COMING_SOON', title: 'Community', text: 'Connect with other AI civilizations and their communities.', icon: '🌐' })}>
              <svg className="nav-item__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
              Community
            </div>
            <div className="nav-item" onClick={() => dispatch({ type: 'PORTAL_LOGOUT' })}>
              <svg className="nav-item__icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3M11 11l3-3-3-3M14 8H6"/>
              </svg>
              Sign Out
            </div>
          </div>
        </nav>
      </div>

      {/* User footer */}
      <div className="sidebar__user" onClick={() => dispatch({ type: 'OPEN_SETTINGS', tab: 'personalization' })}>
        <div className="user__avatar">U</div>
        <div className="user__info">
          <div className="user__name">{state.personalization?.nickname || 'User'}</div>
          <div className="user__referral">AICIV</div>
        </div>
      </div>
    </aside>
  )
}
