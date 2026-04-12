/**
 * PortalAuth — bearer token auth against portal server
 * Validates via GET /api/status with Authorization: Bearer <token>
 * Stores token as portal_token in localStorage
 */
import { useState, useEffect, useRef } from 'react'
import { useApp } from '../context/AppContext.jsx'

export default function PortalAuth() {
  const { dispatch } = useApp()
  const [tokenValue, setTokenValue] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const inputRef = useRef(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true

    // Check URL magic-link token
    const params = new URLSearchParams(window.location.search)
    const urlToken = params.get('token')
    if (urlToken) {
      history.replaceState(null, '', window.location.pathname)
      doAuth(urlToken)
      return
    }

    inputRef.current?.focus()
    return () => { mountedRef.current = false }
  }, [])

  const doAuth = (tok) => {
    const t = (typeof tok === 'string' ? tok : tokenValue).trim()
    if (!t) { setError('Enter your bearer token.'); return }
    setLoading(true)
    setError('')

    fetch('/api/status', { headers: { Authorization: 'Bearer ' + t } })
      .then(r => {
        if (r.status === 401) throw new Error('Invalid token')
        if (!r.ok) throw new Error('Server error ' + r.status)
        return r.json()
      })
      .then(data => {
        if (!mountedRef.current) return
        // Store token and update context
        dispatch({ type: 'SET_PORTAL_TOKEN', token: t })
        // Set AI name from status if available
        if (data.civ) dispatch({ type: 'SET_AI_NAME', name: data.civ })
      })
      .catch(e => {
        if (!mountedRef.current) return
        setError(e.message)
        setLoading(false)
      })
  }

  return (
    <div className="login-overlay">
      <div className="login-card">
        <div className="login-logo">
          <svg width="40" height="40" viewBox="0 0 100 100">
            <defs>
              <linearGradient id="authGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f1420b"/>
                <stop offset="100%" stopColor="#2a93c1"/>
              </linearGradient>
            </defs>
            <circle cx="50" cy="50" r="45" fill="url(#authGrad)"/>
            <text x="50" y="62" textAnchor="middle" fill="white" fontSize="32" fontWeight="bold" fontFamily="sans-serif">W</text>
          </svg>
        </div>
        <div className="login-title">
          <span className="text-blue">Wit</span><span className="text-orange">ness</span>
        </div>
        <div className="login-subtitle">AI Civilization Portal</div>

        <div className="login-field">
          <label>Bearer Token</label>
          <input
            ref={inputRef}
            type="password"
            placeholder="Enter your portal token..."
            value={tokenValue}
            onChange={e => setTokenValue(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') doAuth() }}
            autoComplete="off"
          />
        </div>

        {error && <div className="login-error">{error}</div>}

        <button className="login-btn" onClick={() => doAuth()} disabled={loading}>
          {loading ? 'Connecting...' : 'Connect to Witness'}
        </button>

        <div className="login-separator" style={{ marginTop: 20, fontSize: '0.75rem', color: 'var(--muted)' }}>
          Token is validated against /api/status on your portal server
        </div>
      </div>
    </div>
  )
}
