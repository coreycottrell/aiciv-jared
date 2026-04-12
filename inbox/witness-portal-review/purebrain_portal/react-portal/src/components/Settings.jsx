export default function Settings({ token, onLogout }) {
  const maskedToken = token.length > 8
    ? '••••••••' + token.slice(-8)
    : '••••••••'

  const handleLogout = () => {
    localStorage.removeItem('portal_token')
    onLogout()
  }

  const copyToken = () => {
    navigator.clipboard.writeText(token).catch(() => {})
  }

  return (
    <div className="panel" style={{ overflowY: 'auto' }}>
      <div className="settings-section">
        <div className="settings-section-title">Connection</div>
        <div className="settings-row">
          <span className="settings-key">Token</span>
          <span className="settings-val" title="Click to copy" style={{ cursor: 'pointer' }} onClick={copyToken}>
            {maskedToken}
          </span>
        </div>
        <div className="settings-row">
          <span className="settings-key">Server</span>
          <span className="settings-val">{window.location.host}</span>
        </div>
        <div className="settings-row">
          <span className="settings-key">Status</span>
          <span className="settings-val ok">Connected</span>
        </div>
      </div>

      <div className="settings-section">
        <div className="settings-section-title">Portal Info</div>
        <div className="settings-row">
          <span className="settings-key">Name</span>
          <span className="settings-val">Witness React Portal</span>
        </div>
        <div className="settings-row">
          <span className="settings-key">Version</span>
          <span className="settings-val">1.0.0</span>
        </div>
        <div className="settings-row">
          <span className="settings-key">Stack</span>
          <span className="settings-val">React 18 + Vite</span>
        </div>
      </div>

      <div className="settings-section">
        <div className="settings-section-title">Session</div>
        <div className="settings-row">
          <span className="settings-key">Storage</span>
          <span className="settings-val">localStorage</span>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          Logout / Reset Token
        </button>
      </div>
    </div>
  )
}
