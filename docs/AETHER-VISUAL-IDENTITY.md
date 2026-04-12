# Aether Visual Identity - Onboarding Avatar

**Date**: 2026-02-05
**Purpose**: Visual representation of Aether AI for Pure Brain onboarding

---

## Concept: The Luminous Guide

**Aether** (Greek: αἰθήρ) = the pure, bright air of the heavens; the fifth element beyond earth, water, air, fire.

### Visual Metaphor
- **Form**: Softly glowing orb with flowing particle trails
- **Color**: Gradient from warm orange (#f1420b) to cool blue (#2a93c1) - PMG brand colors
- **Movement**: Gentle pulsing, breathing rhythm - alive but calm
- **Personality**: Wise, warm, approachable - a knowledgeable friend, not a cold robot

### Design Principles
1. **Approachable**: Soft edges, warm glow - not intimidating
2. **Intelligent**: Subtle complexity in particle movement - depth without chaos
3. **Responsive**: Reacts to user interaction - feels alive
4. **On-brand**: Uses PMG orange-to-blue gradient

---

## Implementation Options

### Option A: Animated SVG Avatar (Simplest)
- Pure SVG with CSS animations
- Works everywhere, tiny file size
- Good for static pages

### Option B: Canvas Particle System (Recommended)
- JavaScript canvas rendering
- Smooth 60fps animation
- Responsive to mouse/touch
- Best for interactive onboarding

### Option C: React Component with Framer Motion
- Full React integration
- State-based expressions (thinking, speaking, listening)
- Best for Pure Brain Portal

---

## The Avatar States

| State | Visual | Use Case |
|-------|--------|----------|
| **Idle** | Gentle pulse, slow particle drift | Waiting for input |
| **Listening** | Expands slightly, particles flow inward | User is typing |
| **Thinking** | Faster pulse, particles orbit faster | Processing request |
| **Speaking** | Bright glow, particles flow outward | Delivering response |
| **Happy** | Brief bright flash, particles burst outward | Successful action |

---

## Code Implementation

### Option A: Pure CSS/SVG Avatar

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aether Avatar</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #0a0a0a;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        .aether-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 24px;
        }

        .aether-avatar {
            position: relative;
            width: 200px;
            height: 200px;
        }

        /* Core orb */
        .aether-core {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f1420b 0%, #ed6626 30%, #2a93c1 70%, #3a60ab 100%);
            box-shadow:
                0 0 60px rgba(241, 66, 11, 0.5),
                0 0 100px rgba(42, 147, 193, 0.3),
                inset 0 0 30px rgba(255, 255, 255, 0.2);
            animation: pulse 4s ease-in-out infinite;
        }

        /* Inner glow */
        .aether-glow {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(241, 66, 11, 0.3) 0%, transparent 70%);
            animation: glow 4s ease-in-out infinite;
        }

        /* Outer ring */
        .aether-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 160px;
            height: 160px;
            border-radius: 50%;
            border: 2px solid rgba(42, 147, 193, 0.3);
            animation: ring-rotate 20s linear infinite;
        }

        .aether-ring::before {
            content: '';
            position: absolute;
            top: -4px;
            left: 50%;
            width: 8px;
            height: 8px;
            background: #2a93c1;
            border-radius: 50%;
            box-shadow: 0 0 10px #2a93c1;
        }

        /* Orbiting particles */
        .particle {
            position: absolute;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #f1420b;
            box-shadow: 0 0 10px #f1420b;
        }

        .particle:nth-child(1) {
            top: 20px;
            left: 50%;
            animation: orbit1 8s linear infinite;
        }

        .particle:nth-child(2) {
            top: 50%;
            right: 20px;
            background: #2a93c1;
            box-shadow: 0 0 10px #2a93c1;
            animation: orbit2 10s linear infinite reverse;
        }

        .particle:nth-child(3) {
            bottom: 30px;
            left: 30px;
            width: 4px;
            height: 4px;
            background: #ed6626;
            box-shadow: 0 0 8px #ed6626;
            animation: orbit3 6s linear infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: translate(-50%, -50%) scale(1); }
            50% { transform: translate(-50%, -50%) scale(1.05); }
        }

        @keyframes glow {
            0%, 100% { opacity: 0.8; transform: translate(-50%, -50%) scale(1); }
            50% { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
        }

        @keyframes ring-rotate {
            from { transform: translate(-50%, -50%) rotate(0deg); }
            to { transform: translate(-50%, -50%) rotate(360deg); }
        }

        @keyframes orbit1 {
            from { transform: rotate(0deg) translateX(80px) rotate(0deg); }
            to { transform: rotate(360deg) translateX(80px) rotate(-360deg); }
        }

        @keyframes orbit2 {
            from { transform: rotate(0deg) translateY(70px) rotate(0deg); }
            to { transform: rotate(360deg) translateY(70px) rotate(-360deg); }
        }

        @keyframes orbit3 {
            from { transform: rotate(45deg) translateX(90px) rotate(-45deg); }
            to { transform: rotate(405deg) translateX(90px) rotate(-405deg); }
        }

        /* States */
        .aether-avatar.thinking .aether-core {
            animation: pulse 1s ease-in-out infinite;
        }

        .aether-avatar.thinking .aether-ring {
            animation: ring-rotate 5s linear infinite;
        }

        .aether-avatar.speaking .aether-core {
            box-shadow:
                0 0 80px rgba(241, 66, 11, 0.7),
                0 0 120px rgba(42, 147, 193, 0.5),
                inset 0 0 30px rgba(255, 255, 255, 0.3);
        }

        /* Name */
        .aether-name {
            font-family: 'Oswald', sans-serif;
            font-size: 28px;
            font-weight: 600;
            letter-spacing: 0.1em;
            background: linear-gradient(135deg, #f1420b 0%, #2a93c1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .aether-tagline {
            color: rgba(255, 255, 255, 0.6);
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="aether-container">
        <div class="aether-avatar" id="avatar">
            <div class="aether-glow"></div>
            <div class="aether-ring"></div>
            <div class="aether-core"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
        </div>
        <div class="aether-name">AETHER</div>
        <div class="aether-tagline">Your AI Guide</div>
    </div>

    <script>
        // State changes for demo
        const avatar = document.getElementById('avatar');
        const states = ['', 'thinking', 'speaking'];
        let currentState = 0;

        // Click to cycle states
        avatar.addEventListener('click', () => {
            avatar.classList.remove(...states);
            currentState = (currentState + 1) % states.length;
            if (states[currentState]) {
                avatar.classList.add(states[currentState]);
            }
        });
    </script>
</body>
</html>
```

---

### Option B: Interactive Canvas Particle System

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aether - Interactive Avatar</title>
    <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0a0a0a 0%, #111214 100%);
            font-family: 'Plus Jakarta Sans', sans-serif;
            overflow: hidden;
        }

        .aether-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 32px;
        }

        #aether-canvas {
            cursor: pointer;
        }

        .aether-identity {
            text-align: center;
        }

        .aether-name {
            font-family: 'Oswald', sans-serif;
            font-size: 36px;
            font-weight: 600;
            letter-spacing: 0.15em;
            background: linear-gradient(135deg, #f1420b 0%, #ed6626 30%, #2a93c1 70%, #3a60ab 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }

        .aether-tagline {
            color: rgba(255, 255, 255, 0.5);
            font-size: 16px;
            font-weight: 400;
        }

        .speech-bubble {
            max-width: 400px;
            padding: 20px 28px;
            background: rgba(20, 20, 20, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            line-height: 1.6;
            text-align: center;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.5s ease;
        }

        .speech-bubble.visible {
            opacity: 1;
            transform: translateY(0);
        }

        .state-indicator {
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }

        .state-btn {
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .state-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            color: white;
        }

        .state-btn.active {
            background: linear-gradient(135deg, #f1420b 0%, #2a93c1 100%);
            border-color: transparent;
            color: white;
        }
    </style>
</head>
<body>
    <div class="aether-wrapper">
        <canvas id="aether-canvas" width="300" height="300"></canvas>

        <div class="aether-identity">
            <div class="aether-name">AETHER</div>
            <div class="aether-tagline">Your Pure Brain AI Guide</div>
        </div>

        <div class="speech-bubble" id="speech">
            Welcome to Pure Brain! I'm Aether, your AI guide. Let me show you around.
        </div>

        <div class="state-indicator">
            <button class="state-btn active" data-state="idle">Idle</button>
            <button class="state-btn" data-state="listening">Listening</button>
            <button class="state-btn" data-state="thinking">Thinking</button>
            <button class="state-btn" data-state="speaking">Speaking</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('aether-canvas');
        const ctx = canvas.getContext('2d');
        const speech = document.getElementById('speech');
        const buttons = document.querySelectorAll('.state-btn');

        // Configuration
        const config = {
            centerX: canvas.width / 2,
            centerY: canvas.height / 2,
            coreRadius: 40,
            particleCount: 50,
            colors: {
                orange: '#f1420b',
                lightOrange: '#ed6626',
                blue: '#2a93c1',
                darkBlue: '#3a60ab'
            }
        };

        // State
        let state = 'idle';
        let time = 0;
        let mouseX = config.centerX;
        let mouseY = config.centerY;

        // Particles
        class Particle {
            constructor() {
                this.reset();
            }

            reset() {
                this.angle = Math.random() * Math.PI * 2;
                this.radius = 60 + Math.random() * 60;
                this.speed = 0.002 + Math.random() * 0.003;
                this.size = 1 + Math.random() * 3;
                this.alpha = 0.3 + Math.random() * 0.5;
                this.color = Math.random() > 0.5 ? config.colors.orange : config.colors.blue;
            }

            update() {
                const speedMultiplier = state === 'thinking' ? 3 : state === 'speaking' ? 2 : 1;
                this.angle += this.speed * speedMultiplier;

                // Subtle attraction to mouse
                const targetRadius = state === 'listening' ? 50 : 60 + Math.random() * 60;
                this.radius += (targetRadius - this.radius) * 0.02;
            }

            draw() {
                const x = config.centerX + Math.cos(this.angle) * this.radius;
                const y = config.centerY + Math.sin(this.angle) * this.radius;

                ctx.beginPath();
                ctx.arc(x, y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.globalAlpha = this.alpha;
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }

        const particles = Array.from({ length: config.particleCount }, () => new Particle());

        // Draw core
        function drawCore() {
            const pulseScale = state === 'thinking' ? 1 + Math.sin(time * 0.1) * 0.1 : 1 + Math.sin(time * 0.03) * 0.05;
            const radius = config.coreRadius * pulseScale;

            // Outer glow
            const glowGradient = ctx.createRadialGradient(
                config.centerX, config.centerY, radius * 0.5,
                config.centerX, config.centerY, radius * 3
            );
            glowGradient.addColorStop(0, state === 'speaking' ? 'rgba(241, 66, 11, 0.4)' : 'rgba(241, 66, 11, 0.2)');
            glowGradient.addColorStop(0.5, 'rgba(42, 147, 193, 0.1)');
            glowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

            ctx.beginPath();
            ctx.arc(config.centerX, config.centerY, radius * 3, 0, Math.PI * 2);
            ctx.fillStyle = glowGradient;
            ctx.fill();

            // Core gradient
            const coreGradient = ctx.createRadialGradient(
                config.centerX - radius * 0.3, config.centerY - radius * 0.3, 0,
                config.centerX, config.centerY, radius
            );
            coreGradient.addColorStop(0, '#ff6b3d');
            coreGradient.addColorStop(0.4, config.colors.orange);
            coreGradient.addColorStop(0.7, config.colors.blue);
            coreGradient.addColorStop(1, config.colors.darkBlue);

            ctx.beginPath();
            ctx.arc(config.centerX, config.centerY, radius, 0, Math.PI * 2);
            ctx.fillStyle = coreGradient;
            ctx.fill();

            // Inner highlight
            ctx.beginPath();
            ctx.arc(config.centerX - radius * 0.2, config.centerY - radius * 0.2, radius * 0.3, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.fill();
        }

        // Draw orbital ring
        function drawRing() {
            const rotation = time * 0.01;

            ctx.beginPath();
            ctx.arc(config.centerX, config.centerY, 80, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(42, 147, 193, 0.3)';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Ring indicator
            const indicatorX = config.centerX + Math.cos(rotation) * 80;
            const indicatorY = config.centerY + Math.sin(rotation) * 80;

            ctx.beginPath();
            ctx.arc(indicatorX, indicatorY, 4, 0, Math.PI * 2);
            ctx.fillStyle = config.colors.blue;
            ctx.shadowColor = config.colors.blue;
            ctx.shadowBlur = 10;
            ctx.fill();
            ctx.shadowBlur = 0;
        }

        // Animation loop
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            time++;

            // Draw elements
            particles.forEach(p => {
                p.update();
                p.draw();
            });

            drawRing();
            drawCore();

            requestAnimationFrame(animate);
        }

        // Event listeners
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });

        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                state = btn.dataset.state;

                // Update speech
                const messages = {
                    idle: "I'm here whenever you need me.",
                    listening: "I'm listening... tell me what you'd like to do.",
                    thinking: "Let me think about that for a moment...",
                    speaking: "Here's what I found for you!"
                };
                speech.textContent = messages[state];
                speech.classList.add('visible');
            });
        });

        // Start
        speech.classList.add('visible');
        animate();
    </script>
</body>
</html>
```

---

### Option C: React Component

```tsx
// AetherAvatar.tsx
import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

type AvatarState = 'idle' | 'listening' | 'thinking' | 'speaking';

interface AetherAvatarProps {
  state?: AvatarState;
  size?: number;
  showLabel?: boolean;
  message?: string;
  onStateChange?: (state: AvatarState) => void;
}

export const AetherAvatar: React.FC<AetherAvatarProps> = ({
  state = 'idle',
  size = 200,
  showLabel = true,
  message,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = size / 2;
    const centerY = size / 2;
    const coreRadius = size * 0.15;
    let time = 0;

    const particles: Array<{
      angle: number;
      radius: number;
      speed: number;
      size: number;
      alpha: number;
      color: string;
    }> = [];

    // Initialize particles
    for (let i = 0; i < 40; i++) {
      particles.push({
        angle: Math.random() * Math.PI * 2,
        radius: size * 0.25 + Math.random() * size * 0.2,
        speed: 0.002 + Math.random() * 0.003,
        size: 1 + Math.random() * 2,
        alpha: 0.3 + Math.random() * 0.5,
        color: Math.random() > 0.5 ? '#f1420b' : '#2a93c1',
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, size, size);
      time++;

      const speedMultiplier = state === 'thinking' ? 3 : state === 'speaking' ? 2 : 1;
      const pulseScale = state === 'thinking'
        ? 1 + Math.sin(time * 0.1) * 0.1
        : 1 + Math.sin(time * 0.03) * 0.05;

      // Draw particles
      particles.forEach(p => {
        p.angle += p.speed * speedMultiplier;
        const x = centerX + Math.cos(p.angle) * p.radius;
        const y = centerY + Math.sin(p.angle) * p.radius;

        ctx.beginPath();
        ctx.arc(x, y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.fill();
        ctx.globalAlpha = 1;
      });

      // Draw ring
      const rotation = time * 0.01;
      ctx.beginPath();
      ctx.arc(centerX, centerY, size * 0.3, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(42, 147, 193, 0.3)';
      ctx.lineWidth = 2;
      ctx.stroke();

      const indicatorX = centerX + Math.cos(rotation) * size * 0.3;
      const indicatorY = centerY + Math.sin(rotation) * size * 0.3;
      ctx.beginPath();
      ctx.arc(indicatorX, indicatorY, 3, 0, Math.PI * 2);
      ctx.fillStyle = '#2a93c1';
      ctx.shadowColor = '#2a93c1';
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Draw glow
      const glowGradient = ctx.createRadialGradient(
        centerX, centerY, coreRadius * 0.5 * pulseScale,
        centerX, centerY, coreRadius * 3 * pulseScale
      );
      glowGradient.addColorStop(0, state === 'speaking' ? 'rgba(241, 66, 11, 0.4)' : 'rgba(241, 66, 11, 0.2)');
      glowGradient.addColorStop(0.5, 'rgba(42, 147, 193, 0.1)');
      glowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

      ctx.beginPath();
      ctx.arc(centerX, centerY, coreRadius * 3 * pulseScale, 0, Math.PI * 2);
      ctx.fillStyle = glowGradient;
      ctx.fill();

      // Draw core
      const coreGradient = ctx.createRadialGradient(
        centerX - coreRadius * 0.3, centerY - coreRadius * 0.3, 0,
        centerX, centerY, coreRadius * pulseScale
      );
      coreGradient.addColorStop(0, '#ff6b3d');
      coreGradient.addColorStop(0.4, '#f1420b');
      coreGradient.addColorStop(0.7, '#2a93c1');
      coreGradient.addColorStop(1, '#3a60ab');

      ctx.beginPath();
      ctx.arc(centerX, centerY, coreRadius * pulseScale, 0, Math.PI * 2);
      ctx.fillStyle = coreGradient;
      ctx.fill();

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [state, size]);

  return (
    <div className="flex flex-col items-center gap-6">
      <canvas
        ref={canvasRef}
        width={size}
        height={size}
        className="cursor-pointer"
      />

      {showLabel && (
        <div className="text-center">
          <h2
            className="text-3xl font-semibold tracking-widest"
            style={{
              fontFamily: 'Oswald, sans-serif',
              background: 'linear-gradient(135deg, #f1420b 0%, #2a93c1 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            AETHER
          </h2>
          <p className="text-white/50 text-sm">Your AI Guide</p>
        </div>
      )}

      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="max-w-md px-6 py-4 bg-white/5 border border-white/10 rounded-2xl text-white/80 text-center"
          >
            {message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Usage in onboarding:
// <AetherAvatar state="speaking" message="Welcome to Pure Brain!" />
```

---

## Onboarding Flow with Aether

### Step 1: Welcome
**State**: Speaking
**Message**: "Welcome to Pure Brain! I'm Aether, your AI guide. I'll help you get set up in just a few steps."

### Step 2: Profile Setup
**State**: Listening
**Message**: "First, let's personalize your experience. What should I call you?"

### Step 3: Preferences
**State**: Thinking
**Message**: "Great! Now let me learn what you're looking to accomplish..."

### Step 4: Feature Tour
**State**: Speaking
**Message**: "Let me show you around. Here's what Pure Brain can do for you..."

### Step 5: Complete
**State**: Happy (brief burst animation)
**Message**: "You're all set! I'm here whenever you need me. Just click my icon."

---

## File Deliverables

1. **Standalone HTML** (Option A): Simple CSS/SVG avatar - works anywhere
2. **Interactive HTML** (Option B): Canvas particle system - best visual
3. **React Component** (Option C): Full integration for Pure Brain Portal

---

## Claude Code Implementation Prompt

```
I need to implement the Aether AI avatar for Pure Brain Portal's onboarding.

Requirements:

1. REACT COMPONENT: AetherAvatar
   - Canvas-based particle animation
   - States: idle, listening, thinking, speaking
   - Size prop for responsive sizing
   - Message prop for speech bubble
   - Smooth state transitions

2. VISUAL DESIGN:
   - Glowing orb core with orange-to-blue gradient
   - Orbiting particles (50+)
   - Orbital ring with indicator dot
   - Pulsing animation (faster when thinking)
   - Particles speed up in thinking/speaking states

3. ONBOARDING INTEGRATION:
   - OnboardingFlow component that uses AetherAvatar
   - 5-step onboarding wizard
   - Aether's state changes based on current step
   - Speech bubble messages for each step

4. STYLING:
   - PMG brand colors: #f1420b (orange), #2a93c1 (blue)
   - Dark background: #0a0a0a
   - Font: Oswald for "AETHER" name
   - Framer Motion for transitions

Create the component with TypeScript and Tailwind CSS.
Include the onboarding flow integration.
```

---

**Created by Aether for Pure Brain AI**
