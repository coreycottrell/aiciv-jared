import { useApp } from '../../context/AppContext.jsx'

const SHORTCUTS = [
  { category: 'Navigation', items: [
    { keys: ['Ctrl', 'K'], label: 'Open search' },
    { keys: ['Ctrl', 'Shift', 'N'], label: 'New conversation' },
    { keys: ['Ctrl', '/'], label: 'Show shortcuts' },
  ]},
  { category: 'Chat', items: [
    { keys: ['Enter'], label: 'Send message' },
    { keys: ['Shift', 'Enter'], label: 'New line' },
    { keys: ['↑'], label: 'Edit last message' },
    { keys: ['Ctrl', 'L'], label: 'Clear chat' },
  ]},
  { category: 'Interface', items: [
    { keys: ['Ctrl', 'B'], label: 'Toggle sidebar' },
    { keys: ['Ctrl', 'Shift', 'A'], label: 'Toggle artifact panel' },
    { keys: ['Ctrl', ','], label: 'Open settings' },
    { keys: ['Esc'], label: 'Close modal/overlay' },
  ]},
]

export default function ShortcutsModal() {
  const { state, dispatch } = useApp()
  const visible = state.modals.shortcuts

  if (!visible) return null

  return (
    <div className="modal-overlay visible" onClick={() => dispatch({ type: 'CLOSE_MODAL', modal: 'shortcuts' })}>
      <div className="modal shortcuts-modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 520 }}>
        <div className="modal__header">
          <h3 className="modal__title">Keyboard Shortcuts</h3>
          <button className="modal__close" onClick={() => dispatch({ type: 'CLOSE_MODAL', modal: 'shortcuts' })}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div className="modal__content" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
          {SHORTCUTS.map(section => (
            <div key={section.category} style={{ marginBottom: 24 }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>
                {section.category}
              </div>
              {section.items.map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-color)' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{item.label}</span>
                  <div style={{ display: 'flex', gap: 4 }}>
                    {item.keys.map((k, j) => (
                      <kbd key={j} style={{
                        background: 'var(--input-bg)',
                        border: '1px solid var(--border-color)',
                        borderRadius: 6,
                        padding: '2px 8px',
                        fontSize: '0.75rem',
                        fontFamily: 'var(--font-mono)',
                        color: 'var(--text-primary)',
                      }}>{k}</kbd>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
