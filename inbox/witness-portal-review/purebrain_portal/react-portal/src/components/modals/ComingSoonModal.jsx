import { useApp } from '../../context/AppContext.jsx'

export default function ComingSoonModal() {
  const { state, dispatch } = useApp()
  const { visible, title, text, icon } = state.modals.comingSoon

  if (!visible) return null

  return (
    <div className="modal-overlay visible" onClick={() => dispatch({ type: 'HIDE_COMING_SOON' })}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 380 }}>
        <div className="modal__header">
          <h3 className="modal__title">{icon} {title || 'Coming Soon'}</h3>
          <button className="modal__close" onClick={() => dispatch({ type: 'HIDE_COMING_SOON' })}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div className="modal__content" style={{ textAlign: 'center', paddingTop: 32, paddingBottom: 32 }}>
          <div style={{ fontSize: '3rem', marginBottom: 16 }}>{icon || '🚧'}</div>
          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{text || 'This feature is coming soon. Stay tuned!'}</p>
          <button
            className="login-btn"
            style={{ marginTop: 24, width: 'auto', padding: '10px 32px' }}
            onClick={() => dispatch({ type: 'HIDE_COMING_SOON' })}
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  )
}
