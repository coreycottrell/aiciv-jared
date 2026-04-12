/**
 * ChatPanel — real connection via portal server
 * APIs: GET /api/chat/history, POST /api/chat/send, WS /ws/chat
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import { useApp } from '../../context/AppContext.jsx'
import ChatInput from './ChatInput.jsx'
import Message from './Message.jsx'
import ThinkingIndicator from './ThinkingIndicator.jsx'
import WelcomeHero from './WelcomeHero.jsx'

export default function ChatPanel() {
  const { state, dispatch } = useApp()
  const token = state.portalToken

  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [wsStatus, setWsStatus] = useState('disconnected')
  const [sending, setSending] = useState(false)

  const wsRef = useRef(null)
  const reconnectRef = useRef(null)
  const mountedRef = useRef(true)
  const knownIdsRef = useRef(new Set())
  const bottomRef = useRef(null)

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, sending])

  // Load history + connect WebSocket on mount
  useEffect(() => {
    mountedRef.current = true
    loadHistory()
    connectWS()
    return () => {
      mountedRef.current = false
      if (reconnectRef.current) clearTimeout(reconnectRef.current)
      if (wsRef.current) { wsRef.current.close(); wsRef.current = null }
    }
  }, [token])

  const addMessages = useCallback((newMsgs) => {
    setMessages(prev => {
      const updated = [...prev]
      for (const msg of newMsgs) {
        if (!knownIdsRef.current.has(msg.id)) {
          knownIdsRef.current.add(msg.id)
          updated.push(msg)
        }
      }
      return updated
    })
  }, [])

  const loadHistory = () => {
    setLoading(true)
    fetch('/api/chat/history?last=100', {
      headers: { Authorization: 'Bearer ' + token },
    })
      .then(r => r.json())
      .then(data => {
        if (!mountedRef.current) return
        setLoading(false)
        if (data.messages && data.messages.length > 0) {
          for (const m of data.messages) knownIdsRef.current.add(m.id)
          // Normalize field names: portal uses {role, text} vs our {role, content}
          setMessages(data.messages.map(m => ({ ...m, content: m.content || m.text || '' })))
        }
      })
      .catch(() => { if (mountedRef.current) setLoading(false) })
  }

  const connectWS = () => {
    if (wsRef.current) { wsRef.current.close(); wsRef.current = null }
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${proto}//${location.host}/ws/chat?token=${encodeURIComponent(token)}`)
    wsRef.current = ws

    ws.onopen = () => {
      if (!mountedRef.current) return
      setWsStatus('connected')
      if (reconnectRef.current) { clearTimeout(reconnectRef.current); reconnectRef.current = null }
    }

    ws.onmessage = (e) => {
      if (!mountedRef.current) return
      try {
        const msg = JSON.parse(e.data)
        setSending(false)
        dispatch({ type: 'SET_THINKING', thinking: false })
        // Normalize: portal sends {role, text, id, timestamp}
        addMessages([{ ...msg, content: msg.content || msg.text || '' }])
      } catch {}
    }

    ws.onclose = () => {
      if (!mountedRef.current) return
      setWsStatus('disconnected')
      wsRef.current = null
      reconnectRef.current = setTimeout(() => {
        if (mountedRef.current) connectWS()
      }, 3000)
    }

    ws.onerror = () => { setWsStatus('disconnected') }
  }

  const handleSend = useCallback((text) => {
    if (!text.trim() || sending) return
    setSending(true)

    // Optimistic user message
    const localId = 'local-' + Date.now()
    const userMsg = {
      id: localId,
      role: 'user',
      content: text,
      timestamp: Math.floor(Date.now() / 1000),
    }
    knownIdsRef.current.add(localId)
    setMessages(prev => [...prev, userMsg])
    dispatch({ type: 'SET_THINKING', thinking: true, label: 'Thinking' })

    fetch('/api/chat/send', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: text }),
    })
      .then(r => r.json())
      .then(data => {
        if (!mountedRef.current) return
        if (data.error) {
          setSending(false)
          dispatch({ type: 'SET_THINKING', thinking: false })
          addMessages([{
            id: 'err-' + Date.now(),
            role: 'assistant',
            content: 'Error: ' + data.error,
            timestamp: Math.floor(Date.now() / 1000),
          }])
        }
        // Success: WS will deliver the response
      })
      .catch(e => {
        if (!mountedRef.current) return
        setSending(false)
        dispatch({ type: 'SET_THINKING', thinking: false })
        addMessages([{
          id: 'err-' + Date.now(),
          role: 'assistant',
          content: 'Network error: ' + e.message,
          timestamp: Math.floor(Date.now() / 1000),
        }])
      })
  }, [token, sending, addMessages, dispatch])

  const handleSuggestion = useCallback((text) => handleSend(text), [handleSend])

  const showEmpty = !loading && messages.length === 0

  return (
    <div className="chat-panel">
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

        <div className="chat-panel__title">{state.aiName || 'Witness'}</div>

        <div className="chat-panel__header-actions">
          {/* WS connection badge */}
          <div className={`gateway-status gateway-status--${wsStatus === 'connected' ? 'connected' : 'disconnected'}`}>
            <span className="gateway-status__dot"/>
            <span className="gateway-status__label">
              {wsStatus === 'connected' ? 'Live' : 'Offline'}
            </span>
          </div>

          <button
            className="chat-panel__icon-btn"
            onClick={() => { setMessages([]); knownIdsRef.current.clear() }}
            title="Clear view"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>

          <button
            className="chat-panel__icon-btn"
            onClick={() => dispatch({ type: 'TOGGLE_ARTIFACT_PANEL' })}
            title="Toggle panel"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/>
            </svg>
          </button>

          <button
            className="chat-panel__icon-btn"
            onClick={() => dispatch({ type: 'OPEN_SETTINGS', tab: 'appearance' })}
            title="Settings"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-panel__body">
        {loading ? (
          <div className="chat-messages" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)', fontSize: '0.85rem' }}>
            Loading history...
          </div>
        ) : showEmpty ? (
          <WelcomeHero onSuggestion={handleSuggestion} />
        ) : (
          <div className="chat-messages">
            <div className="chat-messages__inner">
              {messages.map(msg => (
                <Message key={msg.id} message={msg} />
              ))}
              {sending && (
                <ThinkingIndicator />
              )}
              <div ref={bottomRef} />
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="chat-panel__footer">
        <ChatInput onSend={handleSend} disabled={sending} />
      </div>
    </div>
  )
}
