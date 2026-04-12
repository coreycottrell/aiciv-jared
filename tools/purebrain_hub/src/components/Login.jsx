import React, { useState, useEffect, useRef } from 'react'
import { useToast } from '../App.jsx'

// Demo users - in production these come from the server
const DEMO_USERS = [
  { token: 'team2025', name: 'Jared Sanborn', role: 'Admin', department: 'Leadership' },
  { token: 'safety2025', name: 'Sarah K.', role: 'Safety Lead', department: 'Operations' },
  { token: 'quality2025', name: 'Marcus T.', role: 'Quality Manager', department: 'Quality' },
  { token: 'demo', name: 'Demo User', role: 'Member', department: 'General' },
]

// Brand colors
const COLORS = {
  orange: '#f1420b',
  lightOrange: '#ed6626',
  blue: '#2a93c1',
  darkBlue: '#3a60ab',
}

function NeuralCanvas() {
  const canvasRef = useRef(null)
  const animRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const dpr = window.devicePixelRatio || 1

    function resize() {
      const w = window.innerWidth
      const h = window.innerHeight
      canvas.style.width = w + 'px'
      canvas.style.height = h + 'px'
      canvas.width = w * dpr
      canvas.height = h * dpr
    }
    resize()
    window.addEventListener('resize', resize)

    let time = 0

    // We draw multiple orbs across the screen background,
    // plus a primary large orb centered behind the login card.
    function getCtxDims() {
      return {
        w: canvas.width / dpr,
        h: canvas.height / dpr,
      }
    }

    // Rings config (relative to scale factor S)
    const rings = [
      { radius: 180, segments: 60, speed: 0.002, width: 1, gap: 4 },
      { radius: 160, segments: 40, speed: -0.003, width: 2, gap: 6 },
      { radius: 140, segments: 24, speed: 0.004, width: 1.5, gap: 8 },
      { radius: 100, segments: 12, speed: -0.005, width: 3, gap: 15 },
    ]

    // Particle class factory — bound to a center point
    function createParticles(cx, cy, S, count) {
      return Array.from({ length: count }, () => {
        const p = {
          angle: Math.random() * Math.PI * 2,
          radius: (80 + Math.random() * 100) * S,
          speed: (0.001 + Math.random() * 0.002) * (Math.random() > 0.5 ? 1 : -1),
          size: (1 + Math.random() * 2) * S,
          alpha: 0.2 + Math.random() * 0.4,
          color: Math.random() > 0.5 ? COLORS.orange : COLORS.blue,
          trail: [],
          maxTrail: 3 + Math.floor(Math.random() * 6),
        }
        return p
      })
    }

    // Update and draw all particles for one orb center
    function updateParticles(particles, cx, cy, S) {
      particles.forEach(p => {
        const x = cx + Math.cos(p.angle) * p.radius
        const y = cy + Math.sin(p.angle) * p.radius
        p.trail.unshift({ x, y, alpha: p.alpha })
        if (p.trail.length > p.maxTrail) p.trail.pop()
        p.angle += p.speed
        p.radius += Math.sin(time * 0.02 + p.angle) * 0.3 * S
      })
    }

    function drawParticles(particles) {
      particles.forEach(p => {
        p.trail.forEach((point, i) => {
          const trailAlpha = point.alpha * (1 - i / p.trail.length) * 0.5
          ctx.beginPath()
          ctx.arc(point.x, point.y, p.size * (1 - i / p.trail.length * 0.5), 0, Math.PI * 2)
          ctx.fillStyle = p.color
          ctx.globalAlpha = trailAlpha
          ctx.fill()
        })
        const x = cx_last(p)
        const y = cy_last(p)
        ctx.beginPath()
        ctx.arc(x, y, p.size, 0, Math.PI * 2)
        ctx.fillStyle = p.color
        ctx.globalAlpha = p.alpha
        ctx.shadowColor = p.color
        ctx.shadowBlur = 10 * p.size
        ctx.fill()
        ctx.shadowBlur = 0
        ctx.globalAlpha = 1
      })
    }

    function cx_last(p) {
      return p.trail.length > 0 ? p.trail[0].x : 0
    }
    function cy_last(p) {
      return p.trail.length > 0 ? p.trail[0].y : 0
    }

    function drawRings(cx, cy, S) {
      rings.forEach((ring, ringIndex) => {
        const baseRotation = time * ring.speed
        for (let i = 0; i < ring.segments; i++) {
          const segmentAngle = (Math.PI * 2) / ring.segments
          const startAngle = baseRotation + i * segmentAngle
          const endAngle = startAngle + segmentAngle - (ring.gap * Math.PI / 180)
          const t = i / ring.segments
          let r, g, b
          if (t < 0.5) {
            r = 241; g = 66 + t * 72; b = 11 + t * 30
          } else {
            const t2 = (t - 0.5) * 2
            r = 237 - t2 * 195; g = 102 + t2 * 45; b = 38 + t2 * 155
          }
          const alpha = 0.3 + Math.sin(time * 0.02 + i * 0.5) * 0.2
          ctx.beginPath()
          ctx.arc(cx, cy, ring.radius * S, startAngle, endAngle)
          ctx.strokeStyle = `rgba(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)}, ${alpha})`
          ctx.lineWidth = ring.width * S
          ctx.lineCap = 'round'
          ctx.stroke()
        }
        // Tick marks on outer ring
        if (ringIndex === 0) {
          for (let i = 0; i < 60; i++) {
            const angle = baseRotation + (i * Math.PI * 2) / 60
            const innerR = ring.radius * S - 5 * S
            const outerR = ring.radius * S + (i % 5 === 0 ? 8 : 3) * S
            ctx.beginPath()
            ctx.moveTo(cx + Math.cos(angle) * innerR, cy + Math.sin(angle) * innerR)
            ctx.lineTo(cx + Math.cos(angle) * outerR, cy + Math.sin(angle) * outerR)
            ctx.strokeStyle = i % 5 === 0 ? 'rgba(42, 147, 193, 0.6)' : 'rgba(42, 147, 193, 0.2)'
            ctx.lineWidth = (i % 5 === 0 ? 2 : 1) * S
            ctx.stroke()
          }
        }
      })
    }

    function drawScanBeam(cx, cy, S) {
      const scanAngle = time * 0.015
      const scanWidth = Math.PI / 8
      ctx.beginPath()
      ctx.moveTo(cx, cy)
      ctx.arc(cx, cy, 200 * S, scanAngle, scanAngle + scanWidth)
      ctx.closePath()
      if (ctx.createConicGradient) {
        const gradient = ctx.createConicGradient(scanAngle, cx, cy)
        gradient.addColorStop(0, 'rgba(241, 66, 11, 0)')
        gradient.addColorStop(0.02, 'rgba(241, 66, 11, 0.3)')
        gradient.addColorStop(0.05, 'rgba(42, 147, 193, 0.09)')
        gradient.addColorStop(0.1, 'rgba(42, 147, 193, 0)')
        gradient.addColorStop(1, 'rgba(241, 66, 11, 0)')
        ctx.fillStyle = gradient
      } else {
        const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, 200 * S)
        gradient.addColorStop(0, 'rgba(241, 66, 11, 0.25)')
        gradient.addColorStop(0.5, 'rgba(42, 147, 193, 0.08)')
        gradient.addColorStop(1, 'rgba(42, 147, 193, 0)')
        ctx.fillStyle = gradient
      }
      ctx.fill()
    }

    function drawDataArcs(cx, cy, S) {
      const arcs = [
        { radius: 210, start: -0.5, length: 1.2, color: COLORS.orange },
        { radius: 215, start: 2, length: 0.8, color: COLORS.blue },
        { radius: 220, start: 4, length: 1.5, color: COLORS.lightOrange },
      ]
      arcs.forEach(arc => {
        const animatedStart = arc.start + time * 0.005
        const pulseLength = arc.length + Math.sin(time * 0.03) * 0.2
        ctx.beginPath()
        ctx.arc(cx, cy, arc.radius * S, animatedStart, animatedStart + pulseLength)
        ctx.strokeStyle = arc.color
        ctx.lineWidth = 3 * S
        ctx.lineCap = 'round'
        ctx.globalAlpha = 0.6
        ctx.stroke()
        ctx.globalAlpha = 1
      })
    }

    function drawCenterGlow(cx, cy, S) {
      const baseSize = 80 * S
      const pulseSize = baseSize + Math.sin(time * 0.04) * 10 * S
      const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, pulseSize)
      gradient.addColorStop(0, 'rgba(241, 66, 11, 0.15)')
      gradient.addColorStop(0.5, 'rgba(237, 102, 38, 0.075)')
      gradient.addColorStop(0.8, 'rgba(42, 147, 193, 0.045)')
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)')
      ctx.beginPath()
      ctx.arc(cx, cy, pulseSize, 0, Math.PI * 2)
      ctx.fillStyle = gradient
      ctx.fill()
    }

    // Background floating neural dots (scattered across screen)
    const bgNodes = Array.from({ length: 50 }, () => ({
      x: Math.random(),
      y: Math.random(),
      vx: (Math.random() - 0.5) * 0.0003,
      vy: (Math.random() - 0.5) * 0.0003,
      r: 1 + Math.random() * 2,
      alpha: 0.1 + Math.random() * 0.3,
      color: Math.random() > 0.5 ? COLORS.blue : COLORS.orange,
    }))

    function drawBgNodes(w, h) {
      bgNodes.forEach(n => {
        n.x = (n.x + n.vx + 1) % 1
        n.y = (n.y + n.vy + 1) % 1
        ctx.beginPath()
        ctx.arc(n.x * w, n.y * h, n.r, 0, Math.PI * 2)
        ctx.fillStyle = n.color
        ctx.globalAlpha = n.alpha
        ctx.fill()
        ctx.globalAlpha = 1
      })

      // Connection lines between nearby nodes
      ctx.lineWidth = 0.5
      for (let i = 0; i < bgNodes.length; i++) {
        for (let j = i + 1; j < bgNodes.length; j++) {
          const dx = (bgNodes[i].x - bgNodes[j].x) * w
          const dy = (bgNodes[i].y - bgNodes[j].y) * h
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 120) {
            const alpha = (1 - dist / 120) * 0.12
            ctx.beginPath()
            ctx.moveTo(bgNodes[i].x * w, bgNodes[i].y * h)
            ctx.lineTo(bgNodes[j].x * w, bgNodes[j].y * h)
            ctx.strokeStyle = COLORS.blue
            ctx.globalAlpha = alpha
            ctx.stroke()
            ctx.globalAlpha = 1
          }
        }
      }
    }

    // Create particles for the main center orb
    const { w, h } = getCtxDims()
    const mainCx = w / 2
    const mainCy = h / 2
    const mainS = Math.min(w, h) / 500

    let mainParticles = createParticles(mainCx, mainCy, mainS, 60)

    // Secondary smaller orbs at corners for depth
    let secondaryOrbs = [
      { fx: 0.1, fy: 0.2, sScale: 0.45, particles: null },
      { fx: 0.9, fy: 0.8, sScale: 0.35, particles: null },
    ]
    secondaryOrbs.forEach(orb => {
      const { w, h } = getCtxDims()
      const cx = orb.fx * w
      const cy = orb.fy * h
      const S = Math.min(w, h) / 500 * orb.sScale
      orb.particles = createParticles(cx, cy, S, 20)
    })

    function animate() {
      const { w, h } = getCtxDims()

      // Reset transform for DPR scaling
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

      // Clear
      ctx.clearRect(0, 0, w, h)

      // Dark background with subtle gradient
      const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, Math.max(w, h) * 0.8)
      bgGrad.addColorStop(0, 'rgba(15,10,20,1)')
      bgGrad.addColorStop(0.5, 'rgba(10,10,15,1)')
      bgGrad.addColorStop(1, 'rgba(5,5,10,1)')
      ctx.fillStyle = bgGrad
      ctx.fillRect(0, 0, w, h)

      // Floating bg neural network
      drawBgNodes(w, h)

      // Recalc center in case window resized
      const cx = w / 2
      const cy = h / 2
      const S = Math.min(w, h) / 500

      // Secondary orbs (dimmer, background)
      ctx.globalAlpha = 0.35
      secondaryOrbs.forEach(orb => {
        const ox = orb.fx * w
        const oy = orb.fy * h
        const oS = S * orb.sScale
        updateParticles(orb.particles, ox, oy, oS)
        drawCenterGlow(ox, oy, oS)
        drawRings(ox, oy, oS)
        drawParticles(orb.particles)
      })
      ctx.globalAlpha = 1

      // Main center orb
      drawScanBeam(cx, cy, S)
      drawCenterGlow(cx, cy, S)
      drawDataArcs(cx, cy, S)
      drawRings(cx, cy, S)
      updateParticles(mainParticles, cx, cy, S)
      drawParticles(mainParticles)

      time++
      animRef.current = requestAnimationFrame(animate)
    }

    animRef.current = requestAnimationFrame(animate)

    return () => {
      cancelAnimationFrame(animRef.current)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="neural-canvas"
    />
  )
}

// Animated Aether Orb (CSS-based, sits above the login form)
function AetherOrb() {
  return (
    <div className="login-orb-wrapper">
      <div className="aether-orb">
        <div className="aether-orb__glow" />
        <div className="aether-orb__ring" />
        <div className="aether-orb__ring--inner" />
        <div className="aether-orb__core" />
        <div className="aether-orb__particle aether-orb__particle--1" />
        <div className="aether-orb__particle aether-orb__particle--2" />
        <div className="aether-orb__particle aether-orb__particle--3" />
      </div>
    </div>
  )
}

export default function Login({ onLogin }) {
  const [token, setToken] = useState('')
  const [name, setName] = useState('')
  const [useToken, setUseToken] = useState(true)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [mounted, setMounted] = useState(false)
  const addToast = useToast()

  useEffect(() => {
    // Trigger fade-in animation after mount
    const t = setTimeout(() => setMounted(true), 50)
    return () => clearTimeout(t)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    await new Promise(r => setTimeout(r, 600)) // Simulate auth check

    if (useToken) {
      const user = DEMO_USERS.find(u => u.token === token.trim().toLowerCase())
      if (user) {
        onLogin(user)
      } else {
        setError('Invalid access token. Try: team2025 | safety2025 | demo')
      }
    } else {
      if (name.trim().length < 2) {
        setError('Please enter your name (2+ characters)')
        setLoading(false)
        return
      }
      onLogin({
        name: name.trim(),
        role: 'Member',
        department: 'General',
        token: 'guest'
      })
    }
    setLoading(false)
  }

  return (
    <div className="login-page">
      {/* Full-screen animated neural network canvas */}
      <NeuralCanvas />

      {/* Login card — floats over canvas */}
      <div className={`login-card${mounted ? ' login-card--visible' : ''}`}>

        {/* Animated orb above form */}
        <AetherOrb />

        {/* Logo / branding */}
        <div className="login-logo">
          <h1 className="login-title">
            <span className="login-title__blue">PUREBR</span>
            <span className="login-title__orange">AI</span>
            <span className="login-title__blue">N</span>
          </h1>
          <p className="login-subtitle">Team Engagement Hub</p>
          <div className="login-status-dot">
            <span className="status-pulse" />
            COMMAND CENTER ONLINE
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="login-error">
            <span className="login-error__icon">!</span>
            {error}
          </div>
        )}

        {/* Auth form */}
        <form onSubmit={handleSubmit} className="login-form">
          {useToken ? (
            <div className="form-group">
              <label className="login-label">
                <span className="login-label__icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                </span>
                Access Token
              </label>
              <input
                type="text"
                className="login-input"
                placeholder="Enter your team access token"
                value={token}
                onChange={e => setToken(e.target.value)}
                autoFocus
                autoComplete="off"
              />
              <div className="login-hint">
                Demo: <code>team2025</code> · <code>safety2025</code> · <code>demo</code>
              </div>
            </div>
          ) : (
            <div className="form-group">
              <label className="login-label">
                <span className="login-label__icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </span>
                Your Name
              </label>
              <input
                type="text"
                className="login-input"
                placeholder="Enter your full name"
                value={name}
                onChange={e => setName(e.target.value)}
                autoFocus
              />
            </div>
          )}

          <button
            type="submit"
            className="login-btn-primary"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="login-spinner" />
                <span>Verifying...</span>
              </>
            ) : (
              <>
                <span>Access Hub</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </>
            )}
          </button>

          <button
            type="button"
            className="login-btn-ghost"
            onClick={() => { setUseToken(!useToken); setError('') }}
          >
            {useToken ? 'Join as Guest (no token)' : 'Use access token instead'}
          </button>
        </form>

        {/* Footer */}
        <div className="login-footer">
          <div className="login-footer__divider" />
          <p className="login-footer__text">
            Share wins. Celebrate achievements. Drive improvement.
          </p>
          <p className="login-footer__version">
            PureBrain Team Hub · v0.1 MVP
          </p>
        </div>
      </div>
    </div>
  )
}
