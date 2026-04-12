import { useState } from 'react'
import { useApp } from '../../context/AppContext.jsx'

export default function LoginOverlay() {
  const { state, dispatch } = useApp()
  const [aicivName, setAicivName] = useState('')
  const [secret, setSecret] = useState('')
  const [gatewayUrl, setGatewayUrl] = useState(state.gatewayUrl || '')
  const [showGatewayField, setShowGatewayField] = useState(!state.gatewayUrl)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async () => {
    if (!aicivName.trim() || !secret.trim()) { setError('Please enter AiCIV name and secret'); return }
    const url = gatewayUrl.trim() || state.gatewayUrl
    if (!url) { setError('Please configure your gateway URL'); setShowGatewayField(true); return }

    setLoading(true)
    setError('')
    try {
      const loginUrl = `${url.replace(/\/$/, '')}/api/login`
      const r = await fetch(loginUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: aicivName.trim(), secret: secret.trim() }),
      })
      if (!r.ok) {
        const err = await r.json().catch(() => ({}))
        throw new Error(err.detail || err.error || `Login failed (${r.status})`)
      }
      const data = await r.json()
      const token = data.token || data.access_token || data.auth_token || ''
      const aiName = data.aiciv_name || data.name || aicivName
      dispatch({
        type: 'SET_AUTH',
        gatewayUrl: url.replace(/\/$/, ''),
        authToken: token,
        aiName,
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => { if (e.key === 'Enter') handleLogin() }

  const configureGateway = () => {
    // Just configure URL without login (for manual token setup)
    const url = gatewayUrl.trim()
    if (!url) { setError('Please enter a gateway URL'); return }
    dispatch({ type: 'SET_AUTH', gatewayUrl: url.replace(/\/$/, ''), authToken: '***manual***', aiName: 'AiCIV' })
  }

  return (
    <div className="login-overlay">
      <div className="login-card">
        <div className="login-logo">
          <svg width="40" height="40" viewBox="0 0 100 100">
            <defs>
              <linearGradient id="loginGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f1420b"/>
                <stop offset="100%" stopColor="#2a93c1"/>
              </linearGradient>
            </defs>
            <circle cx="50" cy="50" r="45" fill="url(#loginGrad)"/>
            <text x="50" y="62" textAnchor="middle" fill="white" fontSize="32" fontWeight="bold" fontFamily="sans-serif">A</text>
          </svg>
        </div>
        <div className="login-title">Sign in to <span className="text-blue">Ai</span><span className="text-orange">CIV</span></div>
        <div className="login-subtitle">Connect to your AI civilization</div>

        {showGatewayField && (
          <div className="login-field">
            <label>Gateway URL</label>
            <input
              type="url"
              placeholder="http://your-gateway:8098"
              value={gatewayUrl}
              onChange={e => setGatewayUrl(e.target.value)}
              onKeyDown={handleKeyDown}
            />
          </div>
        )}

        <div className="login-field">
          <label>AiCIV Name</label>
          <input
            type="text"
            placeholder="e.g. aether, ember"
            value={aicivName}
            onChange={e => setAicivName(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus={!showGatewayField}
          />
        </div>

        <div className="login-field">
          <label>Secret</label>
          <input
            type="password"
            placeholder="Enter your secret"
            value={secret}
            onChange={e => setSecret(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>

        {error && <div className="login-error">{error}</div>}

        <button className="login-btn" onClick={handleLogin} disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'}
        </button>

        <div className="login-separator">or</div>
        <div className="login-settings-link">
          {!showGatewayField ? (
            <a onClick={() => setShowGatewayField(true)}>Configure gateway URL</a>
          ) : (
            <a onClick={configureGateway}>Skip login — configure manually</a>
          )}
        </div>
      </div>
    </div>
  )
}
