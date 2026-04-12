/**
 * TerminalPanel — real connection via portal server
 * API: WS /ws/terminal
 * Input is sent via /api/chat/send (portal relays to tmux)
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import { useApp } from '../../context/AppContext.jsx'

export default function TerminalPanel() {
  const { state, dispatch } = useApp()
  const token = state.portalToken

  const [content, setContent] = useState('Connecting to terminal...\n')
  const [wsStatus, setWsStatus] = useState('disconnected')
  const [inputValue, setInputValue] = useState('')

  const wsRef = useRef(null)
  const reconnectRef = useRef(null)
  const mountedRef = useRef(true)
  const outputRef = useRef(null)

  useEffect(() => {
    mountedRef.current = true
    connect()
    return () => {
      mountedRef.current = false
      if (reconnectRef.current) clearTimeout(reconnectRef.current)
      if (wsRef.current) { wsRef.current.close(); wsRef.current = null }
    }
  }, [token])

  const connect = () => {
    if (wsRef.current) { wsRef.current.close(); wsRef.current = null }
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${proto}//${location.host}/ws/terminal?token=${encodeURIComponent(token)}`)
    wsRef.current = ws

    ws.onopen = () => {
      if (!mountedRef.current) return
      setWsStatus('live')
      if (reconnectRef.current) { clearTimeout(reconnectRef.current); reconnectRef.current = null }
    }

    ws.onmessage = (e) => {
      if (!mountedRef.current) return
      const lines = e.data.replace(/\s+$/, '').split('\n')
      while (lines.length > 0 && lines[lines.length - 1].trim() === '') lines.pop()
      setContent(lines.join('\n'))
      if (outputRef.current) {
        outputRef.current.scrollTop = outputRef.current.scrollHeight
      }
    }

    ws.onclose = () => {
      if (!mountedRef.current) return
      setWsStatus('disconnected')
      wsRef.current = null
      reconnectRef.current = setTimeout(() => {
        if (mountedRef.current) connect()
      }, 3000)
    }

    ws.onerror = () => { setWsStatus('disconnected') }
  }

  const sendCommand = useCallback(() => {
    const msg = inputValue.trim()
    if (!msg) return
    setInputValue('')
    fetch('/api/chat/send', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg }),
    }).catch(() => {})
  }, [token, inputValue])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendCommand()
    }
  }

  return (
    <div className="chat-panel" style={{ background: '#0a0a0a' }}>
      {/* Header */}
      <div className="chat-panel__header">
        <button
          className="chat-panel__menu-btn"
          onClick={() => dispatch({ type: 'TOGGLE_SIDEBAR' })}
          title="Toggle sidebar"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>

        {/* Terminal chrome */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
          <div style={{ display: 'flex', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#ff5f57', display: 'block' }}/>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#ffbd2e', display: 'block' }}/>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#28ca41', display: 'block' }}/>
          </div>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--muted)' }}>
            witness-primary
          </span>
        </div>

        <div className="chat-panel__header-actions">
          <div className={`gateway-status gateway-status--${wsStatus === 'live' ? 'connected' : 'disconnected'}`}>
            <span className="gateway-status__dot"/>
            <span className="gateway-status__label">{wsStatus}</span>
          </div>
        </div>
      </div>

      {/* Terminal output */}
      <div
        ref={outputRef}
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '16px 20px',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.8rem',
          lineHeight: 1.5,
          color: '#d4d4d4',
          whiteSpace: 'pre-wrap',
          background: '#0a0a0a',
        }}
      >
        {content}
      </div>

      {/* Terminal input */}
      <div style={{ borderTop: '1px solid var(--border-color)', padding: '10px 16px', display: 'flex', gap: 10, background: '#111' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: '#22c55e', flexShrink: 0 }}>$</span>
        <input
          type="text"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send command to Witness..."
          autoComplete="off"
          style={{
            flex: 1,
            background: 'none',
            border: 'none',
            outline: 'none',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.82rem',
            color: '#d4d4d4',
          }}
        />
        <button
          onClick={sendCommand}
          style={{ padding: '4px 12px', borderRadius: 6, border: '1px solid var(--border-color)', background: 'none', color: 'var(--muted)', fontFamily: 'var(--font-mono)', fontSize: '0.78rem', cursor: 'pointer' }}
        >
          Send
        </button>
      </div>
    </div>
  )
}
