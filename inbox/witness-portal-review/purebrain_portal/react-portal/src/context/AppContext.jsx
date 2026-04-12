import { createContext, useContext, useReducer, useCallback } from 'react'

const AppContext = createContext(null)

const getLS = (key, def) => {
  try { const v = localStorage.getItem(key); return v !== null ? JSON.parse(v) : def }
  catch { return def }
}
const setLS = (key, val) => { try { localStorage.setItem(key, JSON.stringify(val)) } catch {} }
const getStr = (key, def = '') => localStorage.getItem(key) || def

const initialState = {
  // Auth — portal bearer token (primary, always required)
  portalToken: getStr('portal_token'),

  // Auth / Gateway (optional AiCIV gateway, TODO: wire up separately)
  gatewayUrl: getStr('aiciv_gateway_url'),
  authToken: getStr('aiciv_auth_token'),
  aiName: getStr('aiciv_name', 'Witness'),
  userId: (() => {
    let id = localStorage.getItem('pb_user_id')
    if (!id) { id = 'user-' + Math.random().toString(36).slice(2, 10); localStorage.setItem('pb_user_id', id) }
    return id
  })(),

  // Active view: 'chat' | 'terminal' | 'status'
  activeView: 'chat',

  // UI
  sidebarCollapsed: localStorage.getItem('pb_sidebar_collapsed') === 'true',
  theme: getStr('pb_theme', 'system'),
  mobileSidebarOpen: false,

  // Chat
  sessionId: null,
  messages: [],
  isThinking: false,
  thinkingLabel: 'Thinking',
  thinkingElapsed: 0,
  attachments: [],
  activeConvId: null,
  isDragOver: false,

  // Conversations
  conversations: (() => {
    const uid = localStorage.getItem('pb_user_id') || ''
    return getLS(`pb_conv_${uid}`, [])
  })(),

  // Brains
  brains: (() => {
    const uid = localStorage.getItem('pb_user_id') || ''
    return getLS(`pb_brains_${uid}`, [])
  })(),
  activeBrainId: null,

  // Tasks
  tasks: (() => {
    const uid = localStorage.getItem('pb_user_id') || ''
    return getLS(`pb_tasks_${uid}`, [])
  })(),

  // Skills
  skills: [],

  // Gateway status
  gatewayStatus: 'disconnected', // 'connected' | 'disconnected' | 'gateway' | 'checking'

  // Panels
  artifactPanel: {
    visible: false,
    title: 'Artifact Preview',
    content: '',
    type: 'html',
    activeTab: 'preview',
  },
  canvasPanel: {
    visible: false,
    title: 'Document',
    content: '',
    mode: 'doc', // 'doc' | 'code'
  },
  resizeDividerVisible: false,

  // Modals
  modals: {
    settings: false,
    settingsTab: 'appearance',
    search: false,
    share: false,
    shortcuts: false,
    createProject: false,
    createGoal: false,
    createBrain: false,
    editBrainId: null,
    createTask: false,
    comingSoon: { visible: false, title: '', text: '', icon: '🚧' },
    skills: false,
  },

  // Overlays
  overlays: {
    project: { visible: false, projectId: null },
    brain: { visible: false, brainId: null },
    brainStore: { visible: false },
    goal: { visible: false, goalId: null },
    task: { visible: false, taskId: null },
  },

  // Search
  chatSearch: { visible: false, query: '', results: [], currentIdx: 0 },

  // Personalization
  personalization: getLS('pb_personalization', {
    baseTone: 'default',
    warm: 'default',
    enthusiastic: 'default',
    headers: 'default',
    emoji: 'default',
    customInstructions: '',
    nickname: '',
    occupation: '',
  }),

  // Model
  defaultModel: getStr('pb_default_model', 'claude-sonnet-4-20250514'),

  // Memory
  memories: [],
  memoryEnabled: localStorage.getItem('pb_memory_enabled') !== 'false',
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_PORTAL_TOKEN':
      localStorage.setItem('portal_token', action.token || '')
      return { ...state, portalToken: action.token }

    case 'PORTAL_LOGOUT':
      localStorage.removeItem('portal_token')
      return { ...state, portalToken: '', activeView: 'chat' }

    case 'SET_ACTIVE_VIEW':
      return { ...state, activeView: action.view }

    case 'SET_AUTH':
      localStorage.setItem('aiciv_gateway_url', action.gatewayUrl || '')
      localStorage.setItem('aiciv_auth_token', action.authToken || '')
      if (action.aiName) localStorage.setItem('aiciv_name', action.aiName)
      return { ...state, gatewayUrl: action.gatewayUrl, authToken: action.authToken, aiName: action.aiName || state.aiName }

    case 'LOGOUT':
      localStorage.removeItem('aiciv_auth_token')
      localStorage.removeItem('aiciv_name')
      return { ...state, authToken: '', aiName: 'Witness', sessionId: null, messages: [], conversations: [], gatewayStatus: 'disconnected' }

    case 'SET_SESSION':
      return { ...state, sessionId: action.sessionId }

    case 'SET_GATEWAY_STATUS':
      return { ...state, gatewayStatus: action.status }

    case 'SET_AI_NAME':
      localStorage.setItem('aiciv_name', action.name)
      return { ...state, aiName: action.name }

    case 'TOGGLE_SIDEBAR':
      const collapsed = !state.sidebarCollapsed
      localStorage.setItem('pb_sidebar_collapsed', collapsed)
      return { ...state, sidebarCollapsed: collapsed }

    case 'SET_MOBILE_SIDEBAR':
      return { ...state, mobileSidebarOpen: action.open }

    case 'SET_THEME':
      localStorage.setItem('pb_theme', action.theme)
      if (action.theme === 'dark') document.documentElement.removeAttribute('data-theme')
      else if (action.theme === 'light') document.documentElement.setAttribute('data-theme', 'light')
      else {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        if (isDark) document.documentElement.removeAttribute('data-theme')
        else document.documentElement.setAttribute('data-theme', 'light')
      }
      return { ...state, theme: action.theme }

    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.message] }

    case 'CLEAR_MESSAGES':
      return { ...state, messages: [], sessionId: null }

    case 'SET_THINKING':
      return { ...state, isThinking: action.thinking, thinkingLabel: action.label || 'Thinking', thinkingElapsed: 0 }

    case 'SET_THINKING_ELAPSED':
      return { ...state, thinkingElapsed: action.elapsed }

    case 'ADD_ATTACHMENT':
      return { ...state, attachments: [...state.attachments, action.attachment] }

    case 'REMOVE_ATTACHMENT':
      return { ...state, attachments: state.attachments.filter((_, i) => i !== action.index) }

    case 'CLEAR_ATTACHMENTS':
      return { ...state, attachments: [] }

    case 'SET_DRAG_OVER':
      return { ...state, isDragOver: action.over }

    case 'SET_CONVERSATIONS': {
      setLS(`pb_conv_${state.userId}`, action.conversations)
      return { ...state, conversations: action.conversations }
    }

    case 'SET_ACTIVE_CONV':
      return { ...state, activeConvId: action.convId }

    case 'SET_BRAINS': {
      setLS(`pb_brains_${state.userId}`, action.brains)
      return { ...state, brains: action.brains }
    }

    case 'SET_ACTIVE_BRAIN':
      localStorage.setItem(`pb_active_brain_${state.userId}`, action.brainId || '')
      return { ...state, activeBrainId: action.brainId }

    case 'SET_TASKS': {
      setLS(`pb_tasks_${state.userId}`, action.tasks)
      return { ...state, tasks: action.tasks }
    }

    case 'SET_SKILLS':
      return { ...state, skills: action.skills }

    case 'SET_ARTIFACT_PANEL':
      return { ...state, artifactPanel: { ...state.artifactPanel, ...action.panel } }

    case 'TOGGLE_ARTIFACT_PANEL':
      return { ...state, artifactPanel: { ...state.artifactPanel, visible: !state.artifactPanel.visible }, resizeDividerVisible: !state.artifactPanel.visible }

    case 'SET_CANVAS_PANEL':
      return { ...state, canvasPanel: { ...state.canvasPanel, ...action.panel } }

    case 'TOGGLE_CANVAS_PANEL':
      return { ...state, canvasPanel: { ...state.canvasPanel, visible: !state.canvasPanel.visible }, resizeDividerVisible: !state.canvasPanel.visible }

    case 'OPEN_MODAL':
      return { ...state, modals: { ...state.modals, [action.modal]: true } }

    case 'CLOSE_MODAL':
      return { ...state, modals: { ...state.modals, [action.modal]: false } }

    case 'SET_SETTINGS_TAB':
      return { ...state, modals: { ...state.modals, settingsTab: action.tab } }

    case 'OPEN_SETTINGS':
      return { ...state, modals: { ...state.modals, settings: true, settingsTab: action.tab || state.modals.settingsTab } }

    case 'SHOW_COMING_SOON':
      return { ...state, modals: { ...state.modals, comingSoon: { visible: true, title: action.title, text: action.text, icon: action.icon || '🚧' } } }

    case 'HIDE_COMING_SOON':
      return { ...state, modals: { ...state.modals, comingSoon: { ...state.modals.comingSoon, visible: false } } }

    case 'SET_EDIT_BRAIN':
      return { ...state, modals: { ...state.modals, editBrainId: action.brainId } }

    case 'OPEN_OVERLAY':
      return { ...state, overlays: { ...state.overlays, [action.overlay]: { visible: true, ...action.data } } }

    case 'CLOSE_OVERLAY':
      return { ...state, overlays: { ...state.overlays, [action.overlay]: { ...state.overlays[action.overlay], visible: false } } }

    case 'SET_PERSONALIZATION': {
      const p = { ...state.personalization, ...action.data }
      setLS('pb_personalization', p)
      return { ...state, personalization: p }
    }

    case 'SET_DEFAULT_MODEL':
      localStorage.setItem('pb_default_model', action.model)
      return { ...state, defaultModel: action.model }

    case 'SET_MEMORY_ENABLED':
      localStorage.setItem('pb_memory_enabled', action.enabled ? 'true' : 'false')
      return { ...state, memoryEnabled: action.enabled }

    case 'SET_MEMORIES':
      return { ...state, memories: action.memories }

    case 'OPEN_CHAT_SEARCH':
      return { ...state, chatSearch: { ...state.chatSearch, visible: true } }

    case 'CLOSE_CHAT_SEARCH':
      return { ...state, chatSearch: { visible: false, query: '', results: [], currentIdx: 0 } }

    default:
      return state
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState)

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be inside AppProvider')
  return ctx
}
