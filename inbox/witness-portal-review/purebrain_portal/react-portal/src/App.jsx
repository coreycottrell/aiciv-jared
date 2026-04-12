import { useState, useEffect, useCallback } from 'react'
import { useApp } from './context/AppContext.jsx'

// Auth
import PortalAuth from './components/PortalAuth.jsx'

// Layout
import Sidebar from './components/layout/Sidebar.jsx'
import MobileBottomNav from './components/layout/MobileBottomNav.jsx'

// Views
import ChatPanel from './components/chat/ChatPanel.jsx'
import TerminalPanel from './components/panels/TerminalPanel.jsx'
import StatusPanel from './components/panels/StatusPanel.jsx'

// Side panels
import ArtifactPanel from './components/panels/ArtifactPanel.jsx'
import CanvasPanel from './components/panels/CanvasPanel.jsx'

// Modals
import SettingsModal from './components/modals/SettingsModal.jsx'
import CreateBrainModal from './components/modals/CreateBrainModal.jsx'
import SearchModal from './components/modals/SearchModal.jsx'
import ComingSoonModal from './components/modals/ComingSoonModal.jsx'
import ShortcutsModal from './components/modals/ShortcutsModal.jsx'

function AppInner() {
  const { state, dispatch } = useApp()

  // Apply theme on mount / change
  useEffect(() => {
    const theme = state.theme || 'system'
    if (theme === 'dark') {
      document.documentElement.removeAttribute('data-theme')
    } else if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light')
    } else {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (isDark) document.documentElement.removeAttribute('data-theme')
      else document.documentElement.setAttribute('data-theme', 'light')
    }
  }, [state.theme])

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') {
        dispatch({ type: 'CLOSE_MODAL', modal: 'settings' })
        dispatch({ type: 'CLOSE_MODAL', modal: 'search' })
        dispatch({ type: 'CLOSE_MODAL', modal: 'shortcuts' })
        dispatch({ type: 'CLOSE_MODAL', modal: 'createBrain' })
        dispatch({ type: 'HIDE_COMING_SOON' })
        dispatch({ type: 'SET_MOBILE_SIDEBAR', open: false })
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        dispatch({ type: 'OPEN_MODAL', modal: 'search' })
      }
      if ((e.ctrlKey || e.metaKey) && e.key === ',') {
        e.preventDefault()
        dispatch({ type: 'OPEN_SETTINGS', tab: 'appearance' })
      }
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault()
        dispatch({ type: 'OPEN_MODAL', modal: 'shortcuts' })
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault()
        dispatch({ type: 'TOGGLE_SIDEBAR' })
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [dispatch])

  // File drag-and-drop for attachments
  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    dispatch({ type: 'SET_DRAG_OVER', over: true })
  }, [dispatch])

  const handleDragLeave = useCallback((e) => {
    if (!e.currentTarget.contains(e.relatedTarget)) {
      dispatch({ type: 'SET_DRAG_OVER', over: false })
    }
  }, [dispatch])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    dispatch({ type: 'SET_DRAG_OVER', over: false })
    const files = Array.from(e.dataTransfer.files)
    files.forEach(file => {
      const reader = new FileReader()
      reader.onload = (ev) => {
        dispatch({
          type: 'ADD_ATTACHMENT',
          attachment: { name: file.name, size: file.size, type: file.type, data: ev.target.result },
        })
      }
      reader.readAsDataURL(file)
    })
  }, [dispatch])

  // Auth gate — require portal bearer token
  if (!state.portalToken) {
    return <PortalAuth />
  }

  const hasSidePanel = state.artifactPanel.visible || state.canvasPanel.visible

  return (
    <div
      className={[
        'app-layout',
        state.sidebarCollapsed ? 'app-layout--sidebar-collapsed' : '',
        hasSidePanel ? 'app-layout--panel-open' : '',
      ].join(' ')}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Sidebar */}
      <Sidebar />

      {/* Main view — switches between chat / terminal / status */}
      <main className="app-main">
        {state.activeView === 'chat' && <ChatPanel />}
        {state.activeView === 'terminal' && <TerminalPanel />}
        {state.activeView === 'status' && <StatusPanel />}
      </main>

      {/* Right-side artifact / canvas panels */}
      {state.artifactPanel.visible && (
        <div className="app-side-panel">
          <ArtifactPanel />
        </div>
      )}
      {state.canvasPanel.visible && (
        <div className="app-side-panel">
          <CanvasPanel />
        </div>
      )}

      {/* Mobile bottom nav */}
      <MobileBottomNav />

      {/* Modals */}
      <SettingsModal />
      <CreateBrainModal />
      <SearchModal />
      <ComingSoonModal />
      <ShortcutsModal />

      {/* Mobile sidebar overlay */}
      {state.mobileSidebarOpen && (
        <div
          className="mobile-overlay"
          onClick={() => dispatch({ type: 'SET_MOBILE_SIDEBAR', open: false })}
        />
      )}
    </div>
  )
}

export default function App() {
  return <AppInner />
}
