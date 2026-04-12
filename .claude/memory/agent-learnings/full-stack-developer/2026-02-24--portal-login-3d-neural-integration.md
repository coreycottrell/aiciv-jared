# Memory: Portal Login + 3D Neural Network Background Integration

**Date**: 2026-02-24
**Type**: technique
**Agent**: full-stack-developer
**Topic**: Layering Three.js 3D neural network behind portal login form — all 3 tasks

---

## Task Summary

Three simultaneous tasks on purebrain-portal-login-3d.html:
1. Tone down orange redness in 3D scene
2. Make fully responsive (desktop/tablet/mobile/touch)
3. Integrate portal login form on top of 3D background

Output: `/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-login-3d.html`

---

## Task 1: Orange Toning

**Problem**: Original #f1420b = very red. Jared: "almost looks more red than blue with the sparks"

**Changes made**:

| Parameter | Before | After |
|-----------|--------|-------|
| `C_ORANGE` color | `0xf1420b` | `0xe86020` — warmer, less aggressive red |
| Ambient particle ratio | 70% blue / 30% orange | 85% blue / 15% orange |
| Orange ambient intensity | `0.3 + 0.3 * random` red channel | `0.2 + 0.2 * random` — dimmer |
| Orange spark count | `5 + depth * 2` always | Multiplied by 0.6 when color is orange |
| Ambient fire initial | 50/50 blue/orange | 75% blue, 25% orange |
| Odd-depth propagation | Always orange | 60% orange, 40% blue |
| After-orange next color | Always blue | Always blue (unchanged — cascade ends quickly) |
| Env rim light intensity | 2.0 | 1.2 (reduced orange rim environment) |
| Click/tap burst | Orange | Blue (reinforces blue dominance) |
| Mouse proximity trigger | Orange | 70% blue, 30% orange |

**Result**: Scene reads as "blue neural brain with occasional warm amber sparks" vs previous red-and-blue parity.

---

## Task 2: Mobile Responsive

### Device Detection
```javascript
const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
  || window.innerWidth < 768;
const isLowPower = isMobile;
```

### Scaled Parameters (mobile vs desktop)
- `NODE_COUNT`: 160 vs 280
- `AMBIENT_COUNT`: 800 vs 1800
- `MAX_PULSES`: 60 vs 120
- `MAX_SPARKS`: 300 vs 600
- `PIXEL_RATIO_MAX`: 1 vs 2
- `antialias`: false vs true
- `powerPreference`: 'low-power' vs 'high-performance'
- Ambient fire delay: 300-600ms vs 200-400ms
- Bloom strength: 1.0 vs 1.4

### Touch Events
```javascript
// Unified pointer handler
function getClientXY(e) {
  if (e.touches && e.touches.length > 0) {
    return { x: e.touches[0].clientX, y: e.touches[0].clientY };
  }
  return { x: e.clientX, y: e.clientY };
}
window.addEventListener('touchmove', onPointerMove, { passive: true });
window.addEventListener('touchstart', onPointerMove, { passive: true });
window.addEventListener('touchend', (e) => { ... onTap(...) }, { passive: true });
```

### Camera FOV for Portrait vs Landscape
```javascript
function getInitialFOV() {
  return (W / H) < 0.8 ? 70 : 55;  // portrait gets wider FOV
}
// Also recalculated on resize + orientationchange
window.addEventListener('orientationchange', () => setTimeout(onResize, 200));
```

### Tab Visibility Pause
```javascript
document.addEventListener('visibilitychange', () => {
  isVisible = document.visibilityState === 'visible';
});
// In animate(): if (!isVisible) return;
```

### Tap vs Click on Login Card
```javascript
// Don't fire neurons when user taps the login card itself
const card = document.querySelector('.pb-login-card');
const rect = card.getBoundingClientRect();
if (clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom) {
  return;  // tap was on card — don't activate neurons
}
```

### Safe Area Insets (mobile notch/home-bar)
```css
padding-top: max(20px, env(safe-area-inset-top));
padding-bottom: max(20px, env(safe-area-inset-bottom));
```

### Landscape Mobile (very short viewport)
```css
@media (max-height: 600px) {
  #loginOverlay { align-items: flex-start; overflow-y: auto; }
  .pb-login-card { max-height: none; }
  /* Reduced logo/heading sizes */
}
```

---

## Task 3: Z-Index Integration

### Architecture
```
z-index: 0  — #canvas-container (Three.js renderer, position:fixed)
z-index: 10 — #loginOverlay (form + card, position:fixed)
```

### Card Glass Effect
```css
.pb-login-card {
  background: rgba(10, 10, 10, 0.82);   /* slightly less opaque than original 0.85 */
  backdrop-filter: blur(32px) saturate(1.6);  /* increased from blur(28px) */
}
```
This lets the 3D neural scene show through while keeping the form readable.

### Elements Removed (from portal-login.html)
- `.pb-bg` div — CSS mesh gradient background
- `#pb-particles` canvas — 2D particle system
- `.pb-orb-wrap` div — glowing orb

### Replaced With
- `<div id="canvas-container">` — Three.js renderer appends canvas here

### Elements Preserved (zero changes)
- `id="loginOverlay"` — outer overlay wrapper
- `id="loginAicivName"` — AI name input
- `id="loginSecret"` — password input
- `id="loginButton"` — submit button
- `id="loginError"` — error display div
- `function handleLogin()` — complete login logic
- `function showLoginError(msg)` — error display
- All visible text strings (headlines, labels, footer tagline)
- PUREBR(blue)AI(orange)N(blue).ai(white) color split classes
- PureBrain icon img tag + src URL
- Trust badges, footer, all card styling

---

## Integration Pattern (Reusable)

For any Three.js background + content overlay:
1. Three.js `renderer.domElement` in `position:fixed; inset:0; z-index:0` container
2. Content wrapper `position:fixed; z-index:10+`
3. Card/panel uses `backdrop-filter: blur(32px)` for glassmorphism
4. `background: rgba(r,g,b,0.82)` — 82% opacity lets scene show, 100% keeps text readable
5. Touch events with `{ passive: true }` — required for mobile scroll performance
6. Tap handler avoids firing on UI elements (check `getBoundingClientRect`)

---

## File

`/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-login-3d.html`
