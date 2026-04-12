import React, { useState, useEffect, createContext, useContext } from 'react'
import Login from './components/Login.jsx'
import Dashboard from './components/Dashboard.jsx'
import WinsBoard from './components/WinsBoard.jsx'
import FileUpload from './components/FileUpload.jsx'
import CreatePost from './components/CreatePost.jsx'

// Auth Context
export const AuthContext = createContext(null)
export const ToastContext = createContext(null)

export function useAuth() { return useContext(AuthContext) }
export function useToast() { return useContext(ToastContext) }

// Toast Component
function Toast({ toasts }) {
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          {t.message}
        </div>
      ))}
    </div>
  )
}

// Sidebar
function Sidebar({ view, setView, user, onLogout }) {
  const navItems = [
    { key: 'dashboard', icon: '🏠', label: 'Dashboard' },
    { key: 'wins', icon: '🏆', label: 'Wins Board' },
    { key: 'upload', icon: '📁', label: 'Files & Uploads' },
  ]

  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">PB</div>
        <div className="logo-text">
          <span className="blue">PUREBR</span><span className="orange">AI</span><span className="blue">N</span>
          <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 400 }}>Hub</div>
        </div>
      </div>

      <div className="sidebar-nav">
        <div className="nav-section">
          <div className="nav-label">Navigation</div>
          {navItems.map(item => (
            <button
              key={item.key}
              className={`nav-item ${view === item.key ? 'active' : ''}`}
              onClick={() => setView(item.key)}
            >
              <span className="icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>

        <div className="nav-section">
          <div className="nav-label">Quick Actions</div>
          <button className="nav-item" onClick={() => setView('create')}>
            <span className="icon">✏️</span>
            <span>New Post</span>
          </button>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="user-card" onClick={onLogout} title="Logout">
          <div className="avatar">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="user-info">
            <div className="user-name">{user?.name || 'Team Member'}</div>
            <div className="user-role">{user?.role || 'Member'} · Logout</div>
          </div>
        </div>
      </div>
    </nav>
  )
}

// Main App
export default function App() {
  const [user, setUser] = useState(null)
  const [view, setView] = useState('dashboard')
  const [toasts, setToasts] = useState([])
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Restore session
  useEffect(() => {
    const saved = localStorage.getItem('pb_hub_user')
    if (saved) {
      try { setUser(JSON.parse(saved)) } catch {}
    }
  }, [])

  const addToast = (message, type = 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3500)
  }

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('pb_hub_user', JSON.stringify(userData))
    addToast(`Welcome back, ${userData.name}!`, 'success')
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('pb_hub_user')
  }

  if (!user) {
    return (
      <ToastContext.Provider value={addToast}>
        <Login onLogin={handleLogin} />
        <Toast toasts={toasts} />
      </ToastContext.Provider>
    )
  }

  const renderView = () => {
    switch (view) {
      case 'dashboard':
        return <Dashboard onCreatePost={() => setView('create')} />
      case 'wins':
        return <WinsBoard />
      case 'upload':
        return <FileUpload />
      case 'create':
        return <CreatePost onDone={() => setView('dashboard')} onCancel={() => setView('dashboard')} />
      default:
        return <Dashboard onCreatePost={() => setView('create')} />
    }
  }

  const viewTitles = {
    dashboard: '🏠 Team Dashboard',
    wins: '🏆 Wins Board',
    upload: '📁 Files & Uploads',
    create: '✏️ Create Post',
  }

  return (
    <AuthContext.Provider value={{ user }}>
      <ToastContext.Provider value={addToast}>
        <div className="app-layout">
          <Sidebar
            view={view}
            setView={setView}
            user={user}
            onLogout={handleLogout}
          />
          <div className="main-content">
            <div className="topbar">
              <div className="topbar-title">{viewTitles[view] || 'Hub'}</div>
              <div className="topbar-actions">
                <div className="gdrive-badge">
                  <span>☁️</span>
                  <span>Drive Connected</span>
                </div>
                {view !== 'create' && (
                  <button className="btn btn-orange btn-sm" onClick={() => setView('create')}>
                    + New Post
                  </button>
                )}
              </div>
            </div>
            <div className="page-content">
              {renderView()}
            </div>
          </div>
        </div>
        <Toast toasts={toasts} />
      </ToastContext.Provider>
    </AuthContext.Provider>
  )
}
