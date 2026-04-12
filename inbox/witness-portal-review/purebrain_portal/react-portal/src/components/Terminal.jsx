import { useState, useEffect, useRef } from 'react'

export default function Terminal({ token, onConnectionChange }) {
  const [content, setContent] = useState('Connecting to terminal stream...')
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
      onConnectionChange?.(true)
      if (reconnectRef.current) { clearTimeout(reconnectRef.current); reconnectRef.current = null }
    }

    ws.onmessage = (e) => {
      if (!mountedRef.current) return
      // Replace full terminal content (tmux capture-pane gives full pane state)
      const lines = e.data.replace(/\s+$/, '').split('\n')
      while (lines.length > 0 && lines[lines.length - 1].trim() === '') lines.pop()
      setContent(lines.join('\n'))
      // Auto-scroll to bottom
      if (outputRef.current) {
        outputRef.current.scrollTop = outputRef.current.scrollHeight
      }
    }

    ws.onclose = () => {
      if (!mountedRef.current) return
      setWsStatus('disconnected')
      onConnectionChange?.(false)
      wsRef.current = null
      reconnectRef.current = setTimeout(() => {
        if (mountedRef.current) connect()
      }, 3000)
    }

    ws.onerror = () => {
      setWsStatus('disconnected')
      onConnectionChange?.(false)
    }
  }

  const sendCommand = () => {
    const msg = inputValue.trim()
    if (!msg) return
    setInputValue('')
    fetch('/api/chat/send', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg }),
    }).catch(() => {})
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendCommand()
    }
  }

  return (
    <div className="panel">
      <div className="terminal-chrome">
        <span className="chrome-dot chrome-dot-r" />
        <span className="chrome-dot chrome-dot-y" />
        <span className="chrome-dot chrome-dot-g" />
        <span className="terminal-title">witness-primary</span>
        <span className={`ws-badge ${wsStatus === 'live' ? 'live' : ''}`}>
          {wsStatus}
        </span>
      </div>
      <div className="terminal-output" ref={outputRef}>
        {content}
      </div>
      <div className="terminal-input-bar">
        <input
          type="text"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send command..."
          autoComplete="off"
        />
        <button onClick={sendCommand}>Send</button>
      </div>
    </div>
  )
}
