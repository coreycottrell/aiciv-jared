import { useState, useCallback } from 'react'
import { useApp } from '../../context/AppContext.jsx'

const EMOJI_OPTIONS = ['🤖', '🧠', '💡', '🔬', '📝', '🎨', '💻', '📊', '🌐', '🔧', '⚡', '🚀', '📚', '🎯', '🏆', '🔮', '🦾', '🌟']

export default function CreateBrainModal() {
  const { state, dispatch } = useApp()
  const visible = state.modals.createBrain

  const [emoji, setEmoji] = useState('🤖')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [instructions, setInstructions] = useState('')
  const [starters, setStarters] = useState([''])

  const close = () => {
    dispatch({ type: 'CLOSE_MODAL', modal: 'createBrain' })
    setName(''); setDescription(''); setInstructions(''); setEmoji('🤖'); setStarters([''])
  }

  const addStarter = () => setStarters(s => [...s, ''])
  const updateStarter = (i, v) => setStarters(s => s.map((x, j) => j === i ? v : x))
  const removeStarter = (i) => setStarters(s => s.filter((_, j) => j !== i))

  const submit = useCallback(() => {
    if (!name.trim()) return
    const brain = {
      id: 'brain-' + Date.now(),
      emoji,
      name: name.trim(),
      description: description.trim(),
      instructions: instructions.trim(),
      starters: starters.filter(s => s.trim()),
      createdAt: Date.now(),
    }
    dispatch({ type: 'SET_BRAINS', brains: [...state.brains, brain] })
    close()
  }, [emoji, name, description, instructions, starters, state.brains, dispatch])

  if (!visible) return null

  return (
    <div className="modal-overlay visible" onClick={close}>
      <div className="modal brain-modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 560 }}>
        <div className="modal__header">
          <h3 className="modal__title">Create Brain</h3>
          <button className="modal__close" onClick={close}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div className="modal__content" style={{ maxHeight: '70vh', overflowY: 'auto' }}>
          {/* Emoji Picker */}
          <div className="brain-modal__field">
            <label>Avatar</label>
            <div className="brain-modal__emoji-picker">
              {EMOJI_OPTIONS.map(e => (
                <button
                  key={e}
                  className={`brain-modal__emoji-option ${emoji === e ? 'brain-modal__emoji-option--active' : ''}`}
                  onClick={() => setEmoji(e)}
                >
                  {e}
                </button>
              ))}
            </div>
          </div>

          <div className="brain-modal__field">
            <label>Name *</label>
            <input
              type="text"
              placeholder="e.g. Marketing Writer"
              value={name}
              onChange={e => setName(e.target.value)}
              maxLength={40}
            />
          </div>

          <div className="brain-modal__field">
            <label>Description</label>
            <input
              type="text"
              placeholder="Short description of what this brain does"
              value={description}
              onChange={e => setDescription(e.target.value)}
              maxLength={120}
            />
          </div>

          <div className="brain-modal__field">
            <label>Instructions</label>
            <textarea
              placeholder="You are a helpful AI that specializes in..."
              value={instructions}
              onChange={e => setInstructions(e.target.value)}
              rows={5}
              maxLength={8000}
              style={{ width: '100%', resize: 'vertical', background: 'var(--input-bg)', border: '1px solid var(--border-color)', borderRadius: 10, padding: '10px 12px', color: 'var(--white)', fontFamily: 'var(--font-body)', fontSize: '0.85rem', outline: 'none' }}
            />
            <div style={{ textAlign: 'right', fontSize: '0.72rem', color: 'var(--muted)', marginTop: 4 }}>
              {instructions.length} / 8000
            </div>
          </div>

          <div className="brain-modal__field">
            <label>Conversation Starters</label>
            {starters.map((s, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                <input
                  type="text"
                  placeholder={`Starter ${i + 1}`}
                  value={s}
                  onChange={e => updateStarter(i, e.target.value)}
                  style={{ flex: 1, background: 'var(--input-bg)', border: '1px solid var(--border-color)', borderRadius: 8, padding: '8px 12px', color: 'var(--white)', fontFamily: 'var(--font-body)', fontSize: '0.85rem', outline: 'none' }}
                />
                {starters.length > 1 && (
                  <button
                    onClick={() => removeStarter(i)}
                    style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', padding: '0 8px' }}
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </button>
                )}
              </div>
            ))}
            {starters.length < 4 && (
              <button
                className="brain-modal__add-starter"
                onClick={addStarter}
              >
                + Add starter
              </button>
            )}
          </div>

          <button
            className="brain-modal__submit"
            onClick={submit}
            disabled={!name.trim()}
          >
            Create Brain
          </button>
        </div>
      </div>
    </div>
  )
}
