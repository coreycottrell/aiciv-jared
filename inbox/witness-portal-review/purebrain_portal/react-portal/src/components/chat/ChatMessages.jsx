import { useEffect, useRef } from 'react'
import { useApp } from '../../context/AppContext.jsx'
import Message from './Message.jsx'
import ThinkingIndicator from './ThinkingIndicator.jsx'
import WelcomeHero from './WelcomeHero.jsx'

export default function ChatMessages({ onSuggestion }) {
  const { state } = useApp()
  const { messages } = state
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, state.isThinking])

  if (messages.length === 0 && !state.isThinking) {
    return <WelcomeHero onSuggestion={onSuggestion} />
  }

  return (
    <div className="chat-messages">
      <div className="chat-messages__inner">
        {messages.map(msg => (
          <Message key={msg.id} message={msg} />
        ))}
        <ThinkingIndicator />
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
