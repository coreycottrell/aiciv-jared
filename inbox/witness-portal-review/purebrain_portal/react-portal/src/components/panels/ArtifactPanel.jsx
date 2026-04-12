import { useState } from 'react'
import { useApp } from '../../context/AppContext.jsx'

export default function ArtifactPanel() {
  const { state, dispatch } = useApp()
  const { artifactPanel } = state
  const [copyDone, setCopyDone] = useState(false)

  if (!artifactPanel.visible) return null

  const close = () => dispatch({ type: 'SET_ARTIFACT_PANEL', panel: { visible: false } })

  const copyContent = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(artifactPanel.content).then(() => {
        setCopyDone(true)
        setTimeout(() => setCopyDone(false), 1500)
      })
    }
  }

  const getIframeSrc = () => {
    if (artifactPanel.type === 'html') {
      const blob = new Blob([artifactPanel.content], { type: 'text/html' })
      return URL.createObjectURL(blob)
    }
    return null
  }

  return (
    <div className="artifact-panel">
      <div className="artifact-panel__header">
        <div className="artifact-panel__title">{artifactPanel.title || 'Preview'}</div>
        <div className="artifact-panel__tabs">
          <button
            className={`artifact-panel__tab ${artifactPanel.activeTab === 'preview' ? 'artifact-panel__tab--active' : ''}`}
            onClick={() => dispatch({ type: 'SET_ARTIFACT_PANEL', panel: { activeTab: 'preview' } })}
          >
            Preview
          </button>
          <button
            className={`artifact-panel__tab ${artifactPanel.activeTab === 'code' ? 'artifact-panel__tab--active' : ''}`}
            onClick={() => dispatch({ type: 'SET_ARTIFACT_PANEL', panel: { activeTab: 'code' } })}
          >
            Code
          </button>
        </div>
        <div className="artifact-panel__actions">
          <button className="artifact-panel__action-btn" onClick={copyContent} title="Copy">
            {copyDone ? '✓' : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
            )}
          </button>
          <button className="artifact-panel__action-btn" onClick={close} title="Close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <div className="artifact-panel__body">
        {artifactPanel.activeTab === 'preview' && (
          <>
            {artifactPanel.type === 'html' ? (
              <iframe
                className="artifact-panel__iframe"
                srcDoc={artifactPanel.content}
                title="Preview"
                sandbox="allow-scripts allow-same-origin"
              />
            ) : (
              <div
                className="artifact-panel__markdown"
                style={{ padding: 20, overflowY: 'auto', height: '100%', color: 'var(--text-secondary)', lineHeight: 1.7 }}
              >
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontFamily: 'var(--font-body)', fontSize: '0.88rem' }}>
                  {artifactPanel.content}
                </pre>
              </div>
            )}
          </>
        )}
        {artifactPanel.activeTab === 'code' && (
          <div className="artifact-panel__code" style={{ padding: 16, overflowY: 'auto', height: '100%' }}>
            <pre style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.82rem',
              color: 'var(--text-primary)',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              lineHeight: 1.65,
            }}>
              {artifactPanel.content}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
