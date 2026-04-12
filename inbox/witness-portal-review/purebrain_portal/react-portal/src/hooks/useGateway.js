import { useCallback, useRef } from 'react'
import { useApp } from '../context/AppContext.jsx'

export function useGateway() {
  const { state, dispatch } = useApp()
  const pollRef = useRef(null)
  const thinkingTimerRef = useRef(null)

  const headers = useCallback(() => ({
    'Content-Type': 'application/json',
    Authorization: state.authToken ? `Bearer ${state.authToken}` : '',
  }), [state.authToken])

  const apiUrl = (path) => `${state.gatewayUrl}${path}`

  const checkHealth = useCallback(async () => {
    if (!state.gatewayUrl) return false
    try {
      dispatch({ type: 'SET_GATEWAY_STATUS', status: 'checking' })
      const r = await fetch(apiUrl('/api/health'), { headers: headers(), signal: AbortSignal.timeout(5000) })
      if (r.ok) {
        dispatch({ type: 'SET_GATEWAY_STATUS', status: 'connected' })
        return true
      }
      dispatch({ type: 'SET_GATEWAY_STATUS', status: 'disconnected' })
      return false
    } catch {
      dispatch({ type: 'SET_GATEWAY_STATUS', status: 'disconnected' })
      return false
    }
  }, [state.gatewayUrl, headers])

  const startSession = useCallback(async () => {
    if (!state.gatewayUrl) return null
    try {
      const r = await fetch(apiUrl('/api/start'), {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ user_id: state.userId }),
      })
      if (!r.ok) return null
      const data = await r.json()
      const sid = data.session_id || data.sessionId
      dispatch({ type: 'SET_SESSION', sessionId: sid })
      return sid
    } catch { return null }
  }, [state.gatewayUrl, state.userId, headers])

  const sendMessage = useCallback(async (text, sessionId, onDone) => {
    if (!state.gatewayUrl || !sessionId) return
    dispatch({ type: 'SET_THINKING', thinking: true, label: 'Thinking' })

    // Thinking elapsed timer
    let elapsed = 0
    thinkingTimerRef.current = setInterval(() => {
      elapsed += 0.1
      dispatch({ type: 'SET_THINKING_ELAPSED', elapsed })
    }, 100)

    try {
      const r = await fetch(apiUrl(`/api/message/${sessionId}`), {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ message: text }),
      })
      if (!r.ok) throw new Error('Send failed')

      // Poll for response
      let attempts = 0
      const poll = async () => {
        if (attempts > 120) {
          clearInterval(thinkingTimerRef.current)
          dispatch({ type: 'SET_THINKING', thinking: false })
          return
        }
        attempts++
        try {
          const pollR = await fetch(apiUrl(`/api/response/${sessionId}`), { headers: headers() })
          if (!pollR.ok) {
            pollRef.current = setTimeout(poll, 1000)
            return
          }
          const data = await pollR.json()
          if (data.status === 'pending' || data.status === 'processing') {
            if (data.events && data.events.length > 0) {
              const lastEvent = data.events[data.events.length - 1]
              dispatch({ type: 'SET_THINKING', thinking: true, label: lastEvent.type || 'Thinking' })
            }
            pollRef.current = setTimeout(poll, 1000)
          } else if (data.status === 'complete' || data.response) {
            clearInterval(thinkingTimerRef.current)
            dispatch({ type: 'SET_THINKING', thinking: false })
            if (onDone) onDone(data.response || data.text || '')
          } else {
            pollRef.current = setTimeout(poll, 1000)
          }
        } catch {
          pollRef.current = setTimeout(poll, 2000)
        }
      }
      pollRef.current = setTimeout(poll, 500)
    } catch (err) {
      clearInterval(thinkingTimerRef.current)
      dispatch({ type: 'SET_THINKING', thinking: false })
      if (onDone) onDone('Error: ' + err.message, true)
    }
  }, [state.gatewayUrl, headers])

  const loadConversations = useCallback(async () => {
    if (!state.gatewayUrl) return []
    try {
      const r = await fetch(apiUrl('/api/conversations'), { headers: headers() })
      if (!r.ok) return []
      const data = await r.json()
      return data.conversations || data || []
    } catch { return [] }
  }, [state.gatewayUrl, headers])

  const loadSkills = useCallback(async () => {
    if (!state.gatewayUrl) return []
    try {
      const r = await fetch(apiUrl('/api/skills'), { headers: headers() })
      if (!r.ok) return []
      const data = await r.json()
      return data.skills || data || []
    } catch { return [] }
  }, [state.gatewayUrl, headers])

  const loadAgents = useCallback(async () => {
    if (!state.gatewayUrl) return []
    try {
      const r = await fetch(apiUrl('/api/agents'), { headers: headers() })
      if (!r.ok) return []
      const data = await r.json()
      return data.agents || data || []
    } catch { return [] }
  }, [state.gatewayUrl, headers])

  const loadBoopStatus = useCallback(async () => {
    if (!state.gatewayUrl) return null
    try {
      const r = await fetch(apiUrl('/api/boop/status'), { headers: headers() })
      if (!r.ok) return null
      return await r.json()
    } catch { return null }
  }, [state.gatewayUrl, headers])

  const login = useCallback(async (aicivName, secret) => {
    if (!state.gatewayUrl) throw new Error('No gateway URL configured')
    const r = await fetch(apiUrl('/api/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: aicivName, secret }),
    })
    if (!r.ok) {
      const err = await r.json().catch(() => ({}))
      throw new Error(err.detail || err.error || 'Login failed')
    }
    const data = await r.json()
    return data
  }, [state.gatewayUrl])

  const stopPolling = useCallback(() => {
    if (pollRef.current) { clearTimeout(pollRef.current); pollRef.current = null }
    if (thinkingTimerRef.current) { clearInterval(thinkingTimerRef.current); thinkingTimerRef.current = null }
  }, [])

  return { checkHealth, startSession, sendMessage, loadConversations, loadSkills, loadAgents, loadBoopStatus, login, stopPolling }
}
