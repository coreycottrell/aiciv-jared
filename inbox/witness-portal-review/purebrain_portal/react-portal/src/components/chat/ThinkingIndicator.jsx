import { useApp } from '../../context/AppContext.jsx'

export default function ThinkingIndicator() {
  const { state } = useApp()
  const { isThinking, thinkingLabel, thinkingElapsed, aiName } = state

  if (!isThinking) return null

  return (
    <div className="thinking-indicator">
      <div className="thinking-indicator__avatar">
        <svg width="28" height="28" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="thinkGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f1420b"/>
              <stop offset="100%" stopColor="#2a93c1"/>
            </linearGradient>
          </defs>
          <circle cx="50" cy="50" r="45" fill="url(#thinkGrad)"/>
          <text x="50" y="62" textAnchor="middle" fill="white" fontSize="32" fontWeight="bold" fontFamily="sans-serif">A</text>
        </svg>
      </div>
      <div className="thinking-indicator__content">
        <div className="thinking-indicator__label">
          {thinkingLabel || 'Thinking'}
          <span className="thinking-indicator__dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        {thinkingElapsed > 0 && (
          <div className="thinking-indicator__elapsed">{thinkingElapsed.toFixed(1)}s</div>
        )}
      </div>
      <div className="thinking-indicator__pulse">
        <div className="thinking-indicator__pulse-ring"></div>
        <div className="thinking-indicator__pulse-ring thinking-indicator__pulse-ring--delay"></div>
      </div>
    </div>
  )
}
