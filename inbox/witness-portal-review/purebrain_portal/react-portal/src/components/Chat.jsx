import { useState, useEffect, useRef } from 'react'

function formatTime(ts) {
  const d = new Date(ts * 1000)
  let h = d.getHours(), m = d.getMinutes()
  const ampm = h >= 12 ? 'pm' : 'am'
  h = h % 12 || 12
  return `${h}:${m < 10 ? '0' : ''}${m}${ampm}`
}

function MessageItem({ msg }) {
  const isUser = msg.role === 'user'
  const displayText = msg.text.length > 4000 ? msg.text.substring(0, 4000) + '\n\n... [truncated]' : msg.text
  const timeStr = formatTime(msg.timestamp)

  return (
    <div className={`msg ${msg.role}`}>
      <div className="msg-row">
        <div className="msg-avatar">
          {isUser ? 'C' : (
            <div className="msg-avatar-inner">W</div>
          )}
        </div>
        <div className="msg-bubble">{displayText}</div>
      </div>
      <div className="msg-meta">
        {isUser ? 'Corey' : 'Witness'} · {timeStr}
      </div>
    </div>
  )
}

export default function Chat({ token }) {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const wsRef = useRef(null)
  const reconnectRef = useRef(null)
  const mountedRef = useRef(true)
  const messagesEndRef = useRef(null)
  const knownIdsRef = useRef(new Set())
  const inputRef = useRef(null)

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

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessages = (newMsgs) => {
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
  }

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
          setMessages(data.messages)
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
      if (reconnectRef.current) { clearTimeout(reconnectRef.current); reconnectRef.current = null }
    }

    ws.onmessage = (e) => {
      if (!mountedRef.current) return
      try {
        const msg = JSON.parse(e.data)
        addMessages([msg])
      } catch {}
    }

    ws.onclose = () => {
      if (!mountedRef.current) return
      wsRef.current = null
      reconnectRef.current = setTimeout(() => {
        if (mountedRef.current) connectWS()
      }, 3000)
    }

    ws.onerror = () => {}
  }

  const sendChat = () => {
    const msg = inputValue.trim()
    if (!msg || sending) return
    setInputValue('')
    setSending(true)
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
    }

    const localId = 'local-' + Date.now()
    addMessages([{
      id: localId,
      role: 'user',
      text: msg,
      timestamp: Math.floor(Date.now() / 1000),
    }])

    fetch('/api/chat/send', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg }),
    })
      .then(r => r.json())
      .then(data => {
        if (data.error) {
          addMessages([{
            id: 'err-' + Date.now(),
            role: 'assistant',
            text: 'Error: ' + data.error,
            timestamp: Math.floor(Date.now() / 1000),
          }])
        }
      })
      .catch(e => {
        addMessages([{
          id: 'err-' + Date.now(),
          role: 'assistant',
          text: 'Network error: ' + e.message,
          timestamp: Math.floor(Date.now() / 1000),
        }])
      })
      .finally(() => {
        if (mountedRef.current) {
          setSending(false)
          inputRef.current?.focus()
        }
      })
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendChat()
    }
  }

  const autoResize = (e) => {
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
  }

  const isEmpty = !loading && messages.length === 0

  return (
    <div className="panel">
      <div className="chat-messages">
        {loading && (
          <div className="chat-loading">Loading history...</div>
        )}
        {isEmpty && (
          <div className="chat-empty">
            <div className="chat-empty-orb">
              <div className="chat-empty-orb-inner">W</div>
            </div>
            <div className="chat-empty-name grad-text">Witness</div>
            <div className="chat-empty-tagline">AI Civilization — ready to help</div>
          </div>
        )}
        {messages.map(msg => (
          <MessageItem key={msg.id} msg={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-area">
        <div className="chat-input-container">
          <textarea
            ref={inputRef}
            className="chat-input-field"
            rows="1"
            placeholder="Message Witness..."
            value={inputValue}
            onChange={e => { setInputValue(e.target.value); autoResize(e) }}
            onKeyDown={handleKeyDown}
          />
          <button
            className="chat-submit"
            onClick={sendChat}
            disabled={sending || !inputValue.trim()}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
