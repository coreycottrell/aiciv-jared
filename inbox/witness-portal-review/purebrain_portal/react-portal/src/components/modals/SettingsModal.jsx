import { useState } from 'react'
import { useApp } from '../../context/AppContext.jsx'

const MODELS = [
  { id: 'claude-opus-4-6', label: 'Claude Opus 4.6', desc: 'Most capable' },
  { id: 'claude-sonnet-4-6', label: 'Claude Sonnet 4.6', desc: 'Balanced' },
  { id: 'claude-haiku-4-5-20251001', label: 'Claude Haiku 4.5', desc: 'Fast & efficient' },
]

function AppearanceTab() {
  const { state, dispatch } = useApp()
  const themes = [
    { value: 'light', label: 'Light', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/></svg> },
    { value: 'dark', label: 'Dark', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg> },
    { value: 'system', label: 'System', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg> },
  ]
  return (
    <div>
      <h4 className="settings-modal__section-title">Appearance</h4>
      <p className="settings-modal__section-desc">Choose how your AI looks to you.</p>
      <div className="settings-theme-picker">
        {themes.map(t => (
          <button
            key={t.value}
            className={`settings-theme-picker__option ${state.theme === t.value ? 'settings-theme-picker__option--active' : ''}`}
            onClick={() => dispatch({ type: 'SET_THEME', theme: t.value })}
          >
            <div className="settings-theme-picker__icon">{t.icon}</div>
            <span className="settings-theme-picker__label">{t.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

function PersonalizationTab() {
  const { state, dispatch } = useApp()
  const p = state.personalization
  const update = (key, val) => dispatch({ type: 'SET_PERSONALIZATION', data: { [key]: val } })

  const row = (label, key, options) => (
    <div className="personalization__row" key={key}>
      <div className="personalization__row-label">{label}</div>
      <select className="personalization__select" value={p[key] || 'default'} onChange={e => update(key, e.target.value)}>
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  )

  return (
    <div>
      <h4 className="settings-modal__section-title">Personalization</h4>
      <p className="settings-modal__section-desc">Customize how your AI responds to you.</p>

      <div className="personalization__section">
        <div className="personalization__section-header">Base style &amp; tone</div>
        {row('Response tone', 'baseTone', [
          { value: 'default', label: 'Default' },
          { value: 'professional', label: 'Professional' },
          { value: 'friendly', label: 'Friendly' },
          { value: 'candid', label: 'Candid' },
          { value: 'efficient', label: 'Efficient' },
          { value: 'nerdy', label: 'Nerdy' },
        ])}
      </div>

      <hr className="personalization__divider"/>

      <div className="personalization__section">
        <div className="personalization__section-header">Characteristics</div>
        {row('Warm', 'warm', [{ value: 'less', label: 'Less' }, { value: 'default', label: 'Default' }, { value: 'more', label: 'More' }])}
        {row('Enthusiastic', 'enthusiastic', [{ value: 'less', label: 'Less' }, { value: 'default', label: 'Default' }, { value: 'more', label: 'More' }])}
        {row('Headers & Lists', 'headers', [{ value: 'less', label: 'Less' }, { value: 'default', label: 'Default' }, { value: 'more', label: 'More' }])}
        {row('Emoji', 'emoji', [{ value: 'less', label: 'Less' }, { value: 'default', label: 'Default' }, { value: 'more', label: 'More' }])}
      </div>

      <hr className="personalization__divider"/>

      <div className="personalization__section">
        <div className="personalization__section-header">Custom instructions</div>
        <textarea
          className="personalization__textarea"
          maxLength={1500}
          placeholder="e.g., Be concise, use bullet points, avoid jargon..."
          value={p.customInstructions || ''}
          onChange={e => update('customInstructions', e.target.value)}
          rows={4}
          style={{ width: '100%', resize: 'vertical', background: 'var(--input-bg)', border: '1px solid var(--border-color)', borderRadius: 10, padding: '10px 12px', color: 'var(--white)', fontFamily: 'var(--font-body)', fontSize: '0.85rem', outline: 'none' }}
        />
        <div style={{ textAlign: 'right', fontSize: '0.72rem', color: 'var(--muted)' }}>
          {(p.customInstructions || '').length}/1500
        </div>
      </div>

      <hr className="personalization__divider"/>

      <div className="personalization__section">
        <div className="personalization__section-header">About you</div>
        <div className="personalization__field">
          <label className="personalization__field-label">Nickname</label>
          <input className="personalization__input" type="text" maxLength={50} placeholder="What should your AI call you?" value={p.nickname || ''} onChange={e => update('nickname', e.target.value)} />
        </div>
        <div className="personalization__field" style={{ marginTop: 12 }}>
          <label className="personalization__field-label">Occupation</label>
          <input className="personalization__input" type="text" maxLength={100} placeholder="e.g., Software Engineer, Marketing Director..." value={p.occupation || ''} onChange={e => update('occupation', e.target.value)} />
        </div>
      </div>
    </div>
  )
}

function ModelTab() {
  const { state, dispatch } = useApp()
  return (
    <div>
      <h4 className="settings-modal__section-title">Model</h4>
      <p className="settings-modal__section-desc">Choose the AI model for your conversations.</p>
      {MODELS.map(m => (
        <div
          key={m.id}
          onClick={() => dispatch({ type: 'SET_DEFAULT_MODEL', model: m.id })}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '14px 16px',
            marginBottom: 8,
            borderRadius: 12,
            border: `2px solid ${state.defaultModel === m.id ? 'var(--light-blue)' : 'var(--border-color)'}`,
            background: state.defaultModel === m.id ? 'rgba(42,147,193,0.08)' : 'var(--input-bg)',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
        >
          <div style={{
            width: 20, height: 20, borderRadius: '50%',
            border: `2px solid ${state.defaultModel === m.id ? 'var(--light-blue)' : 'var(--border-color)'}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          }}>
            {state.defaultModel === m.id && <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--light-blue)' }}/>}
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>{m.label}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>{m.desc}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

function GatewayTab() {
  const { state, dispatch } = useApp()
  const [url, setUrl] = useState(state.gatewayUrl || '')
  const [saved, setSaved] = useState(false)

  const save = () => {
    dispatch({ type: 'SET_AUTH', gatewayUrl: url.trim().replace(/\/$/, ''), authToken: state.authToken, aiName: state.aiName })
    setSaved(true)
    setTimeout(() => setSaved(false), 1500)
  }

  const logout = () => {
    dispatch({ type: 'LOGOUT' })
  }

  return (
    <div>
      <h4 className="settings-modal__section-title">AiCIV Gateway</h4>
      <p className="settings-modal__section-desc">Configure your gateway connection.</p>
      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 8, color: 'var(--text-primary)' }}>Gateway URL</label>
        <input
          type="url"
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder="http://your-gateway:8098"
          style={{ width: '100%', background: 'var(--input-bg)', border: '1px solid var(--border-color)', borderRadius: 10, padding: '10px 14px', color: 'var(--white)', fontFamily: 'var(--font-body)', fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box' }}
        />
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={save}
          style={{ flex: 1, padding: '10px', borderRadius: 10, border: 'none', background: 'linear-gradient(135deg, var(--dark-blue), var(--light-blue))', color: '#fff', fontFamily: 'var(--font-heading)', fontWeight: 600, cursor: 'pointer' }}
        >
          {saved ? 'Saved!' : 'Save'}
        </button>
        <button
          onClick={logout}
          style={{ padding: '10px 20px', borderRadius: 10, border: '1px solid var(--danger)', background: 'none', color: 'var(--danger)', fontFamily: 'var(--font-body)', cursor: 'pointer' }}
        >
          Sign Out
        </button>
      </div>
      <div style={{ marginTop: 20, padding: '12px 16px', background: 'var(--hover-bg)', borderRadius: 10 }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--muted)', marginBottom: 4 }}>Connected as</div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 600 }}>{state.aiName}</div>
        <div style={{ fontSize: '0.78rem', color: 'var(--muted)', marginTop: 4 }}>
          Status: <span style={{ color: state.gatewayStatus === 'connected' ? 'var(--success)' : 'var(--danger)' }}>{state.gatewayStatus}</span>
        </div>
      </div>
    </div>
  )
}

function DataTab() {
  const { dispatch } = useApp()
  return (
    <div>
      <h4 className="settings-modal__section-title">Data Controls</h4>
      <p className="settings-modal__section-desc">Manage your data and privacy settings.</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <button
          onClick={() => { if (window.confirm('Clear all conversation history?')) dispatch({ type: 'SET_CONVERSATIONS', conversations: [] }) }}
          style={{ padding: '12px 20px', borderRadius: 10, border: '1px solid var(--border-color)', background: 'var(--input-bg)', color: 'var(--text-primary)', fontFamily: 'var(--font-body)', cursor: 'pointer', textAlign: 'left' }}
        >
          <div style={{ fontWeight: 600, marginBottom: 2 }}>Clear conversation history</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--muted)' }}>Delete all stored conversations</div>
        </button>
        <button
          onClick={() => { if (window.confirm('Clear all brains?')) dispatch({ type: 'SET_BRAINS', brains: [] }) }}
          style={{ padding: '12px 20px', borderRadius: 10, border: '1px solid var(--border-color)', background: 'var(--input-bg)', color: 'var(--text-primary)', fontFamily: 'var(--font-body)', cursor: 'pointer', textAlign: 'left' }}
        >
          <div style={{ fontWeight: 600, marginBottom: 2 }}>Clear all brains</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--muted)' }}>Delete all custom brain configurations</div>
        </button>
      </div>
    </div>
  )
}

const TABS = [
  { id: 'appearance', label: 'Appearance', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/></svg> },
  { id: 'personalization', label: 'Personalization', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> },
  { id: 'model', label: 'Model', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg> },
  { id: 'data', label: 'Data Controls', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> },
  { id: 'gateway', label: 'AICIV Gateway', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg> },
]

export default function SettingsModal() {
  const { state, dispatch } = useApp()
  const activeTab = state.modals.settingsTab || 'appearance'
  const visible = state.modals.settings

  if (!visible) return null

  const close = () => dispatch({ type: 'CLOSE_MODAL', modal: 'settings' })

  const tabContent = {
    appearance: <AppearanceTab />,
    personalization: <PersonalizationTab />,
    model: <ModelTab />,
    data: <DataTab />,
    gateway: <GatewayTab />,
  }

  return (
    <div className="modal-overlay visible" onClick={close}>
      <div className="modal settings-modal" onClick={e => e.stopPropagation()}>
        <div className="modal__header">
          <h3 className="modal__title">Settings</h3>
          <button className="modal__close" onClick={close}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div className="settings-modal__body">
          <aside className="settings-modal__sidebar">
            <nav>
              {TABS.map(t => (
                <button
                  key={t.id}
                  className={`settings-modal__nav-item ${activeTab === t.id ? 'settings-modal__nav-item--active' : ''}`}
                  onClick={() => dispatch({ type: 'SET_SETTINGS_TAB', tab: t.id })}
                >
                  <span className="settings-modal__nav-item-icon">{t.icon}</span>
                  <span className="settings-modal__nav-item-label">{t.label}</span>
                </button>
              ))}
            </nav>
          </aside>
          <div className="settings-modal__content">
            <div className="settings-modal__section settings-modal__section--active">
              {tabContent[activeTab] || tabContent.appearance}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
