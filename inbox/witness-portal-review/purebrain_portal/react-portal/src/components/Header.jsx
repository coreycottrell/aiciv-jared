export default function Header({ isConnected }) {
  return (
    <header>
      <div className="header-brand">
        <div className="header-logo-icon">W</div>
        <span className="header-name grad-text">Witness</span>
        <span className="header-tag">AI Civilization</span>
      </div>
      <div className="header-status">
        <div className={`status-dot ${isConnected ? 'online' : ''}`} />
        <span className="conn-label">{isConnected ? 'Online' : 'Offline'}</span>
      </div>
    </header>
  )
}
