# Memory: PureBrain Portal Login Page Build

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Self-contained premium login page for app.purebrain.ai — replaces AiCIV-branded overlay

---

## What Was Built

File: `/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-login.html`
Lines: 1,064

A fully self-contained, production-quality login page replacing the generic AiCIV-branded overlay in `purebrain-frontend.html`. Customer-facing — first thing paying customers see after $79-$999 purchase.

---

## Design System Applied

```css
--bright-orange: #f1420b;
--orange: #ed6626;
--light-blue: #2a93c1;
--dark-blue: #3a60ab;
--black: #0a0a0a;
--font-heading: 'Oswald', sans-serif;
--font-body: 'Plus Jakarta Sans', sans-serif;
```

---

## Visual Architecture

### Background (3 layers)
1. **Mesh gradient** (`.pb-bg` via `::before`/`::after`) — slow animated radial gradients in orange + blue tones, `meshDrift` animation 18-24s
2. **Particle canvas** (`#pb-particles`) — 55 floating particles, orange/blue tinted, pulsing alpha, wrap edges
3. **Glass orb** (`.pb-orb-wrap`) — 420px sphere, radial gradient, glass highlight via `::before`, neural grid lines via `::after`, `orbFloat` animation

### Card (`pb-login-card`)
- Glass morphism: `backdrop-filter: blur(28px) saturate(1.4)`
- Multi-layer box-shadow for depth + ambient glow
- `::before` = orange-to-blue gradient top edge line
- `::after` = bottom ambient glow
- `cardMaterialize` animation: slides in + scale from 0.97 on page load (delay 0.2s)

### Logo
- Mini orb mark (52px circle, glass treatment)
- Wordmark: `<span class="pure">PURE</span><span class="brain">BRAIN</span><span class="ai">.ai</span>`
- Colors: PURE=dark-blue, BRAIN=orange, .ai=white

### Form Fields (floating label pattern)
- `position: absolute` label on top of input
- Floats to small uppercase when `input:focus` or `input:not(:placeholder-shown)`
- Placeholder = transparent (label does the work)
- Bottom accent bar (orange→blue gradient) scales from 0 on focus
- Orange glow box-shadow on focus

### Sign-In Button
- Orange (#f1420b) → light-blue (#2a93c1) gradient (105deg)
- Shimmer sweep `::after` on hover (translateX left→right)
- `loading` class swaps text for spinner
- `.btn-text` / `.btn-loading` toggle via CSS class

---

## Interface Compatibility (CRITICAL)

Preserved ALL original IDs and function names for drop-in replacement:

| Original | Preserved |
|---------|-----------|
| `id="loginOverlay"` | YES |
| `id="loginAicivName"` | YES |
| `id="loginSecret"` | YES |
| `id="loginError"` | YES |
| `id="loginButton"` | YES |
| `handleLogin()` function | YES (stub with loading state) |
| `loginOverlay.classList.add('hidden')` | YES |
| "Configure gateway manually" escape hatch | YES |
| `openSettingsModal()` + `switchSettingsTab('gateway')` calls | YES |

---

## Integration Instructions

To replace the overlay in `purebrain-frontend.html`:

1. Replace lines 2718-2746 (the `#loginOverlay` div block) with the `#loginOverlay` section from this file
2. Copy the CSS from `<style>` that starts `/* PUREBRAIN PORTAL */` — add it to the existing `<style>` block
3. Copy the JS section for `handleLogin()`, particles, etc. — replace existing stub
4. Replace the existing login CSS (lines 1891-1986) with the new `.pb-*` CSS
5. Remove the particle canvas and orb elements from the body if embedding just the overlay — those are standalone demo background

**Or**: Use this file as a standalone preview/demo at `app.purebrain.ai/login` directly.

---

## Animations Inventory

| Name | Element | Duration | Effect |
|------|---------|----------|--------|
| `meshDrift` | `.pb-bg::before/after` | 18-24s | Background gradient drift |
| `orbFloat` | `.pb-orb-wrap` | 8s | Gentle vertical float |
| `orbPulse` | `.pb-orb-inner` | 6s | Glow intensity pulse |
| `neuralShift` | `.pb-orb-inner::after` | 12s linear | Neural grid rotation |
| `orbMarkSpin` | `.pb-logo-mark` | 20s | Mini orb glow pulse |
| `cardMaterialize` | `.pb-login-card` | 0.8s | Entrance from below + scale |
| `logoReveal` | `.pb-logo-wrap` | 0.6s | Fade+slide from above |
| `contentReveal` | Various | 0.5s | Staggered content fade-in |
| `dotPulse` | Trust dots | 2s | Pulsing status dots |
| `orbMarkSpin` | Logo mark | 20s | Glow alternation |
| `spinnerRotate` | `.pb-spinner` | 0.7s | Loading spinner |
| `errorShake` | `.pb-error` | 0.35s | Error shake (dynamically injected) |

All animations respect `prefers-reduced-motion`.

---

## Key Patterns

### Floating Label CSS
```css
.pb-field label {
  position: absolute;
  top: 14px; left: 14px;
  /* normal state — looks like placeholder */
}
.pb-field input:not(:placeholder-shown) ~ label,
.pb-field input:focus ~ label {
  top: 6px; font-size: 10px; text-transform: uppercase; color: var(--light-blue);
}
.pb-field input::placeholder { color: transparent; }
```
Use `height: 52px` + `padding: 20px 14px 6px` to give room for floating label.

### Button Loading State
```css
.pb-signin-btn .btn-text    { display: inline; }
.pb-signin-btn .btn-loading { display: none; }
.pb-signin-btn.loading .btn-text    { display: none; }
.pb-signin-btn.loading .btn-loading { display: inline; }
```
JS: `button.classList.add('loading'); button.disabled = true;`

### Glass Card Pattern
```css
backdrop-filter: blur(28px) saturate(1.4);
border: 1px solid rgba(255,255,255,0.08);
box-shadow: 0 0 0 1px rgba(241,66,11,0.08), 0 8px 32px rgba(0,0,0,0.6), ...;
```

---

## File Size
1,064 lines — all self-contained CSS+JS+HTML.
