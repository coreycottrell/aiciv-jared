import { useState, useRef, useCallback } from 'react'
import { useApp } from '../../context/AppContext.jsx'

export default function ChatInput({ onSend, disabled }) {
  const { state, dispatch } = useApp()
  const [text, setText] = useState('')
  const textareaRef = useRef(null)
  const fileInputRef = useRef(null)

  const handleSend = useCallback(() => {
    const msg = text.trim()
    if (!msg || disabled) return
    onSend(msg)
    setText('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }, [text, disabled, onSend])

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])

  const handleInput = useCallback((e) => {
    setText(e.target.value)
    // Auto-resize
    const ta = e.target
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px'
  }, [])

  const handleFileSelect = useCallback((e) => {
    const files = Array.from(e.target.files || [])
    files.forEach(file => {
      const reader = new FileReader()
      reader.onload = (ev) => {
        dispatch({
          type: 'ADD_ATTACHMENT',
          attachment: {
            name: file.name,
            size: file.size,
            type: file.type,
            data: ev.target.result,
          }
        })
      }
      reader.readAsDataURL(file)
    })
    e.target.value = ''
  }, [dispatch])

  const removeAttachment = useCallback((idx) => {
    dispatch({ type: 'REMOVE_ATTACHMENT', index: idx })
  }, [dispatch])

  return (
    <div className="chat-input-area">
      {state.attachments.length > 0 && (
        <div className="chat-attachments">
          {state.attachments.map((att, i) => (
            <div key={i} className="attachment-chip">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
              </svg>
              <span className="attachment-chip__name">{att.name}</span>
              <button className="attachment-chip__remove" onClick={() => removeAttachment(i)}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="12" height="12">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      <div className={`chat-input ${state.isDragOver ? 'chat-input--drag-over' : ''}`}>
        <button
          className="chat-input__attach-btn"
          onClick={() => fileInputRef.current?.click()}
          title="Attach file"
          type="button"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
          </svg>
        </button>
        <textarea
          ref={textareaRef}
          className="chat-input__textarea"
          placeholder="Message AiCIV…"
          value={text}
          onInput={handleInput}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={disabled}
        />
        <button
          className={`chat-input__send-btn ${text.trim() ? 'chat-input__send-btn--active' : ''}`}
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          title="Send"
          type="button"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        multiple
        style={{ display: 'none' }}
        onChange={handleFileSelect}
      />

      <div className="chat-input__footer">
        <span className="chat-input__hint">Enter to send · Shift+Enter for new line</span>
        <div className="chat-input__quick-actions">
          <button
            className="quick-action"
            onClick={() => dispatch({ type: 'OPEN_MODAL', modal: 'skills' })}
            title="Skills"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
            </svg>
            Skills
          </button>
        </div>
      </div>
    </div>
  )
}
