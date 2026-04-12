/**
 * StatusPanel — real connection via portal server
 * API: GET /api/status (auto-refreshes every 30s)
 */
import { useState, useEffect, useRef } from 'react'
import { useApp } from '../../context/AppContext.jsx'

function StatCard({ label, value, status }) {
  const colors = { ok: '#22c55e', bad: '#ef4444', warn: '#f59e0b', accent: 'var(--light-blue)', dim: 'var(--muted)' }
  const color = colors[status] || 'var(--text-primary)'
  return (
    <div style={{
      background: 'var(--hover-bg)',
      border: '1px solid var(--border-color)',
      borderRadius: 12,
      padding: '16px 20px',
    }}>
      <div style={{ fontSize: '0.72rem', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
        {label}
      </div>
      <div style={{ fontSize: '1.1rem', fontFamily: 'var(--font-heading)', fontWeight: 700, color }}>
        {value}
      </div>
    </div>
  )
}

function fmtUptime(s) {
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  return `${m}m ${s % 60}s`
}

export default function StatusPanel() {
  const { state, dispatch } = useApp()
  const token = state.portalToken

  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(null)

  const mountedRef = useRef(true)
  const intervalRef = useRef(null)

  useEffect(() => {
    mountedRef.current = true
    loadStatus()
    intervalRef.current = setInterval(loadStatus, 30000)
    return () => {
      mountedRef.current = false
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [token])

  const loadStatus = () => {
    fetch('/api/status', { headers: { Authorization: 'Bearer ' + token } })
      .then(r => r.json())
      .then(d => {
        if (!mountedRef.current) return
        setData(d)
        setError(null)
        setLoading(false)
        setLastRefresh(new Date())
      })
      .catch(e => {
        if (!mountedRef.current) return
        setError(e.message)
        setLoading(false)
      })
  }

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-panel__header">
        <button
          className="chat-panel__menu-btn"
          onClick={() => dispatch({ type: 'TOGGLE_SIDEBAR' })}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        <div className="chat-panel__title">System Status</div>
        <div className="chat-panel__header-actions">
          <button className="chat-panel__icon-btn" onClick={loadStatus} title="Refresh">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
              <polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
          </button>
          <button
            className="chat-panel__icon-btn"
            onClick={() => dispatch({ type: 'OPEN_SETTINGS', tab: 'gateway' })}
            title="Settings"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 24px 40px' }}>
        {loading && (
          <div style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>Loading status...</div>
        )}
        {error && (
          <div style={{ padding: '16px', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 10, color: '#ef4444', fontSize: '0.85rem' }}>
            Error: {error}
          </div>
        )}
        {data && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 24 }}>
              <StatCard label="CIV Name" value={data.civ || '—'} status="accent" />
              <StatCard label="Uptime" value={fmtUptime(data.uptime || 0)} />
              <StatCard label="tmux" value={data.tmux_alive ? 'Active' : 'Dead'} status={data.tmux_alive ? 'ok' : 'bad'} />
              <StatCard label="Claude" value={data.claude_running ? 'Running' : 'Stopped'} status={data.claude_running ? 'ok' : 'bad'} />
              <StatCard label="TG Bot" value={data.tg_bot_running ? 'Running' : 'Stopped'} status={data.tg_bot_running ? 'ok' : 'bad'} />
              <StatCard label="Session" value={data.tmux_session || '—'} status="dim" />
            </div>

            {/* TODO: Add more status sections (memory, fleet health, etc.) when gateway connected */}
            <div style={{ padding: '12px 16px', background: 'var(--hover-bg)', borderRadius: 10, borderLeft: '3px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>TODO</div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                Fleet health, agent status, and memory metrics will show here once gateway is connected.
              </div>
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div style={{ borderTop: '1px solid var(--border-color)', padding: '10px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
        <span style={{ fontSize: '0.72rem', color: 'var(--muted)' }}>
          {lastRefresh ? `Last refresh: ${lastRefresh.toLocaleTimeString()}` : 'Auto-refreshes every 30s'}
        </span>
        <button
          onClick={loadStatus}
          style={{ padding: '4px 12px', borderRadius: 6, border: '1px solid var(--border-color)', background: 'none', color: 'var(--text-secondary)', fontSize: '0.78rem', fontFamily: 'var(--font-body)', cursor: 'pointer' }}
        >
          Refresh Now
        </button>
      </div>
    </div>
  )
}
