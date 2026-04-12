import { useState, useEffect, useRef } from 'react'

export default function Auth({ onAuth }) {
  const [tokenValue, setTokenValue] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const inputRef = useRef(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true

    // Check URL token magic link
    const params = new URLSearchParams(window.location.search)
    const urlToken = params.get('token')
    if (urlToken) {
      history.replaceState(null, '', window.location.pathname)
      setTokenValue(urlToken)
      doAuth(urlToken)
      return
    }

    // Auto-login from localStorage
    const saved = localStorage.getItem('portal_token')
    if (saved) {
      setTokenValue(saved)
      doAuth(saved)
    } else {
      inputRef.current?.focus()
    }

    return () => { mountedRef.current = false }
  }, [])

  const doAuth = (tok) => {
    const t = typeof tok === 'string' ? tok : tokenValue.trim()
    if (!t) { setError('Enter your bearer token.'); return }
    setLoading(true)
    setError('')

    fetch('/api/status', { headers: { Authorization: 'Bearer ' + t } })
      .then(r => {
        if (r.status === 401) throw new Error('Invalid token')
        if (!r.ok) throw new Error('Server error ' + r.status)
        return r.json()
      })
      .then(() => {
        if (!mountedRef.current) return
        localStorage.setItem('portal_token', t)
        onAuth(t)
      })
      .catch(e => {
        if (!mountedRef.current) return
        setError(e.message)
        setLoading(false)
      })
  }

  return (
    <div className="auth-overlay">
      <div className="auth-card">
        <div className="auth-logo">W</div>
        <div className="auth-title grad-text">Witness</div>
        <div className="auth-subtitle">AI Civilization Portal</div>
        <div className="auth-field">
          <label htmlFor="token-input">Bearer Token</label>
          <input
            ref={inputRef}
            type="password"
            id="token-input"
            placeholder="Enter your token..."
            autoComplete="off"
            value={tokenValue}
            onChange={e => setTokenValue(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') doAuth() }}
          />
        </div>
        <button
          className="auth-btn"
          onClick={() => doAuth()}
          disabled={loading}
        >
          {loading ? 'Connecting...' : 'Connect to Witness'}
        </button>
        {error && <div className="auth-error">{error}</div>}
      </div>
    </div>
  )
}
