import { useState, useCallback, useRef } from 'react'
import { useApp } from '../../context/AppContext.jsx'

export default function SearchModal() {
  const { state, dispatch } = useApp()
  const [query, setQuery] = useState('')
  const inputRef = useRef(null)
  const visible = state.modals.search

  const close = () => {
    setQuery('')
    dispatch({ type: 'CLOSE_MODAL', modal: 'search' })
  }

  const results = query.trim().length > 1
    ? state.conversations.filter(c =>
        (c.title || '').toLowerCase().includes(query.toLowerCase()) ||
        (c.preview || '').toLowerCase().includes(query.toLowerCase())
      )
    : []

  const handleSelect = useCallback((conv) => {
    dispatch({ type: 'SET_ACTIVE_CONV', convId: conv.id })
    close()
  }, [dispatch])

  if (!visible) return null

  return (
    <div className="modal-overlay visible" onClick={close}>
      <div
        className="modal search-modal"
        onClick={e => e.stopPropagation()}
        style={{ maxWidth: 560, padding: 0 }}
      >
        <div className="search-modal__input-wrap" style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: 10 }}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="18" height="18" style={{ color: 'var(--muted)', flexShrink: 0 }}>
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            ref={inputRef}
            autoFocus
            type="text"
            placeholder="Search conversations..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => { if (e.key === 'Escape') close() }}
            style={{
              flex: 1,
              background: 'none',
              border: 'none',
              outline: 'none',
              fontSize: '1rem',
              color: 'var(--text-primary)',
              fontFamily: 'var(--font-body)',
            }}
          />
          <button onClick={close} style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer' }}>
            <kbd style={{ padding: '2px 6px', border: '1px solid var(--border-color)', borderRadius: 4, fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>Esc</kbd>
          </button>
        </div>

        <div style={{ maxHeight: 400, overflowY: 'auto', padding: results.length > 0 ? '8px 0' : '40px 20px', textAlign: results.length > 0 ? 'left' : 'center' }}>
          {query.trim().length < 2 && (
            <div style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>
              Type to search your conversation history...
            </div>
          )}
          {query.trim().length >= 2 && results.length === 0 && (
            <div style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>
              No conversations found for "{query}"
            </div>
          )}
          {results.map(conv => (
            <button
              key={conv.id}
              onClick={() => handleSelect(conv)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                width: '100%',
                padding: '12px 20px',
                background: 'none',
                border: 'none',
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'background 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--hover-bg)'}
              onMouseLeave={e => e.currentTarget.style.background = 'none'}
            >
              <span style={{ fontSize: '0.88rem', color: 'var(--text-primary)', fontWeight: 500, marginBottom: 2 }}>
                {conv.title || 'Untitled'}
              </span>
              {conv.preview && (
                <span style={{ fontSize: '0.78rem', color: 'var(--muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {conv.preview}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
