import { useState, useRef } from 'react'
import { useApp } from '../../context/AppContext.jsx'

export default function CanvasPanel() {
  const { state, dispatch } = useApp()
  const { canvasPanel } = state
  const [content, setContent] = useState(canvasPanel.content || '')
  const editorRef = useRef(null)

  if (!canvasPanel.visible) return null

  const close = () => dispatch({ type: 'SET_CANVAS_PANEL', panel: { visible: false } })

  const download = () => {
    const blob = new Blob([content], { type: 'text/plain' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${canvasPanel.title || 'document'}.txt`
    a.click()
  }

  const copy = () => {
    if (navigator.clipboard) navigator.clipboard.writeText(content)
  }

  return (
    <div className="canvas-panel">
      <div className="canvas-panel__header">
        <div className="canvas-panel__title">{canvasPanel.title || 'Document'}</div>
        <div className="canvas-panel__toolbar">
          <button className="canvas-panel__tool-btn" onClick={copy} title="Copy">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
              <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
          </button>
          <button className="canvas-panel__tool-btn" onClick={download} title="Download">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </button>
          <button className="canvas-panel__tool-btn" onClick={close} title="Close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>
      <div className="canvas-panel__body">
        <textarea
          ref={editorRef}
          className="canvas-panel__editor"
          value={content}
          onChange={e => {
            setContent(e.target.value)
            dispatch({ type: 'SET_CANVAS_PANEL', panel: { content: e.target.value } })
          }}
          placeholder="Start writing..."
          spellCheck
        />
      </div>
    </div>
  )
}
