import { useState, useCallback } from 'react'
import { useApp } from '../../context/AppContext.jsx'

// Simple markdown renderer (no external deps)
function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    // Escape HTML
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    // Code blocks
    .replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) =>
      `<div class="code-block"><div class="code-block__header"><span class="code-block__lang">${lang || 'text'}</span><button class="code-block__copy" onclick="(function(b){navigator.clipboard&&navigator.clipboard.writeText(b.closest('.code-block').querySelector('code').innerText).then(()=>{b.textContent='Copied!';setTimeout(()=>b.textContent='Copy',1500)})})(this)">Copy</button></div><div class="code-block__content"><code>${code}</code></div></div>`
    )
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Bold
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Horizontal rule
    .replace(/^---$/gm, '<hr>')
    // Blockquote
    .replace(/^> (.+)$/gm, '<blockquote><p>$1</p></blockquote>')
    // Unordered lists
    .replace(/^[*-] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    // Ordered lists
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    // Line breaks → paragraphs
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')

  return `<p>${html}</p>`
}

export default function Message({ message }) {
  const { dispatch } = useApp()
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'

  const copyText = useCallback(() => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(message.content).then(() => {
        setCopied(true)
        setTimeout(() => setCopied(false), 1500)
      })
    }
  }, [message.content])

  const openArtifact = useCallback(() => {
    dispatch({
      type: 'SET_ARTIFACT_PANEL',
      panel: {
        visible: true,
        title: 'Response',
        content: message.content,
        type: 'markdown',
        activeTab: 'preview',
      }
    })
    dispatch({ type: 'TOGGLE_ARTIFACT_PANEL' })
    dispatch({ type: 'TOGGLE_ARTIFACT_PANEL' }) // ensure visible
  }, [message.content, dispatch])

  return (
    <div className={`message ${isUser ? 'message--user' : 'message--ai'}`}>
      {!isUser && (
        <div className="message__avatar">
          <svg width="28" height="28" viewBox="0 0 100 100">
            <defs>
              <linearGradient id={`msgGrad-${message.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f1420b"/>
                <stop offset="100%" stopColor="#2a93c1"/>
              </linearGradient>
            </defs>
            <circle cx="50" cy="50" r="45" fill={`url(#msgGrad-${message.id})`}/>
            <text x="50" y="62" textAnchor="middle" fill="white" fontSize="32" fontWeight="bold" fontFamily="sans-serif">A</text>
          </svg>
        </div>
      )}
      <div className="message__body">
        <div
          className="message__bubble"
          dangerouslySetInnerHTML={isUser
            ? { __html: `<p>${message.content.replace(/\n/g, '<br>')}</p>` }
            : { __html: renderMarkdown(message.content) }
          }
        />
        <div className="message__actions">
          <button className="message__action-btn" onClick={copyText} title="Copy">
            {copied ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            )}
          </button>
          {!isUser && (
            <button className="message__action-btn" onClick={openArtifact} title="Open in panel">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
            </button>
          )}
        </div>
      </div>
      {isUser && (
        <div className="message__avatar message__avatar--user">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
      )}
    </div>
  )
}
