import { useState, useEffect, useRef } from 'react'

function fmtUptime(s) {
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  return `${m}m ${s % 60}s`
}

function StatCard({ label, value, cls }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className={`stat-value ${cls || ''}`}>{value}</div>
    </div>
  )
}

export default function Status({ token }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
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
      })
      .catch(e => {
        if (!mountedRef.current) return
        setError(e.message)
        setLoading(false)
      })
  }

  return (
    <div className="panel">
      <div className="status-grid">
        {loading && (
          <StatCard label="Loading" value="—" cls="dim" />
        )}
        {error && (
          <StatCard label="Error" value={error} cls="bad" />
        )}
        {data && (
          <>
            <StatCard label="CIV Name" value={data.civ || '—'} cls="accent" />
            <StatCard label="Uptime" value={fmtUptime(data.uptime || 0)} />
            <StatCard label="tmux" value={data.tmux_alive ? 'Active' : 'Dead'} cls={data.tmux_alive ? 'ok' : 'bad'} />
            <StatCard label="Claude" value={data.claude_running ? 'Running' : 'Stopped'} cls={data.claude_running ? 'ok' : 'bad'} />
            <StatCard label="TG Bot" value={data.tg_bot_running ? 'Running' : 'Stopped'} cls={data.tg_bot_running ? 'ok' : 'bad'} />
            <StatCard label="Session" value={data.tmux_session || '—'} cls="dim" />
          </>
        )}
      </div>
      <div className="status-footer">
        Auto-refresh every 30s
        <button className="refresh-btn" onClick={loadStatus}>Refresh Now</button>
      </div>
    </div>
  )
}
