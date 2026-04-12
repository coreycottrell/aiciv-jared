import { useApp } from '../../context/AppContext.jsx'

const SUGGESTIONS = [
  { icon: '💡', text: 'Explain a complex concept in simple terms' },
  { icon: '📝', text: 'Help me write or improve my content' },
  { icon: '🔧', text: 'Debug or review my code' },
  { icon: '🔍', text: 'Research a topic in depth' },
]

export default function WelcomeHero({ onSuggestion }) {
  const { state } = useApp()
  const name = state.aiName || 'AiCIV'

  return (
    <div className="welcome-hero">
      <div className="welcome-hero__logo">
        <svg width="60" height="60" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f1420b"/>
              <stop offset="100%" stopColor="#2a93c1"/>
            </linearGradient>
          </defs>
          <circle cx="50" cy="50" r="45" fill="url(#heroGrad)"/>
          <text x="50" y="62" textAnchor="middle" fill="white" fontSize="32" fontWeight="bold" fontFamily="sans-serif">A</text>
        </svg>
      </div>
      <h1 className="welcome-hero__title">Hi, I'm <span className="text-gradient">{name}</span></h1>
      <p className="welcome-hero__subtitle">Your AI civilization. How can I help you today?</p>
      <div className="welcome-hero__suggestions">
        {SUGGESTIONS.map((s, i) => (
          <button
            key={i}
            className="welcome-hero__suggestion"
            onClick={() => onSuggestion && onSuggestion(s.text)}
          >
            <span className="welcome-hero__suggestion-icon">{s.icon}</span>
            <span className="welcome-hero__suggestion-text">{s.text}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
