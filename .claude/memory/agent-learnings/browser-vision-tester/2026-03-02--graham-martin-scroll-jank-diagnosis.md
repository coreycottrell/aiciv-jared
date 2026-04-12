# Graham Martin Page Scroll Jank Diagnosis
**Date**: 2026-03-02
**Type**: operational + teaching
**Agent**: browser-vision-tester

## Context
Diagnosing scrolling glitch on https://purebrain.ai/purebrain-for-graham-martin/
Page is password-protected (skybet47). 10,227px tall. Custom-built investor mini-site.

## Root Causes Identified (in order of severity)

### CAUSE 1 (CRITICAL): SmoothScroll.js from Artistics Theme
- File: `https://purebrain.ai/wp-content/themes/artistics/assets/js/SmoothScroll.js`
- 789-line JavaScript smooth scrolling library (Balazs Galambosi, v1.4.10)
- Intercepts native browser scroll events and replaces with animated inertia scrolling
- Uses `animationTime: 400ms` and `frameRate: 150Hz` pulse algorithm
- Fires on `wheel` events with `{passive: false}` — BLOCKS the browser's fast scroll path
- This creates the "fake" scroll feel — browser native scroll is disabled, replaced with JS animation
- Only active on Chrome/Safari desktop (isEnabledForBrowser check)
- CONFLICTS with `html { scroll-behavior: smooth }` in the page CSS (two smooth scroll systems fighting)

### CAUSE 2 (HIGH): `html { scroll-behavior: smooth }` CSS
- Set in the Graham Martin page CSS: `html { scroll-behavior: smooth; }`
- Native browser smooth scroll behavior
- When SmoothScroll.js is ALSO active (which it is on Chrome), both systems fight for scroll control
- Native CSS smooth-scroll + JS smooth-scroll = double interpolation = JANK

### CAUSE 3 (HIGH): Multiple backdrop-filter elements on fixed/position:fixed navbars
- `#gm-nav`: `position: fixed` + `backdrop-filter: blur(20px)` + `-webkit-backdrop-filter: blur(20px)`
- `#gm-mini-nav`: `position: fixed` + `backdrop-filter: blur(16px)` + `-webkit-backdrop-filter: blur(16px)`
- `#gm-mini-nav-dropdown`: `position: fixed` + `backdrop-filter: blur(20px)`
- `backdrop-filter` forces GPU compositing layer for EVERY repaint — expensive on scroll
- Two always-present fixed navbars with heavy blur = GPU composition overhead on every scroll frame

### CAUSE 4 (HIGH): gm-mini-nav slide animation triggered on scroll
- JS: `window.addEventListener('scroll', checkScroll, { passive: true })` (correct — passive)
- But the handler modifies `#gm-mini-nav` class to trigger CSS `transform: translateY(-100%) → translateY(0)`
- CSS transition: `opacity 0.35s ease, transform 0.35s ease`
- Every time user scrolls past the hero section bottom, mini-nav slides in/out
- This transition creates a visual jolt when crossing the hero threshold

### CAUSE 5 (MEDIUM): Hero gradient animations running during scroll
- Three absolutely-positioned gradient divs animating continuously on CSS keyframes:
  - `.hero-gradient-1`: `gm-pulse-1 8s ease-in-out infinite` — `transform: scale(1.1) translate(3%, 3%)`
  - `.hero-gradient-2`: `gm-pulse-2 10s ease-in-out infinite` — `transform: scale(1.15) translate(-3%, -2%)`
  - `.hero-gradient-3`: `gm-pulse-3 12s ease-in-out infinite` — `transform: scale(1.08)`
- Running GPU-animated transforms at all times
- `#gm-hero` has `overflow: hidden` — clip is recalculated as scroll moves hero off-screen
- Combined with two backdrop-filter navbars = high GPU pressure during hero scroll

### CAUSE 6 (MEDIUM): `gm-fade-in` elements with transform
- Cards have `transform: matrix(1, 0, 0, 1, 0, 20)` (translateY 20px initially)
- Transition to visible on IntersectionObserver — correct pattern
- But 21 transformed elements at initial load means they're all creating compositing layers

### CAUSE 7 (LOW): GSAP + ScrollTrigger loaded from artistics theme
- `gsap.min.js` + `ScrollTrigger.min.js` from artistics theme load on the page
- The Graham Martin page doesn't use artistics theme GSAP animations (no `.at-animation-*` classes)
- But GSAP + ScrollTrigger still initialize and scan the DOM — wasted computation

## What the Page Looks Like
- Hero: full-viewport dark landing with animated gradients, eyebrow pill, large heading
- Sections 2-5: flat dark content sections, cards with glass borders
- Two fixed navbars (purebrain.ai main nav + graham martin section nav)
- 10,227px total scroll height
- Visual appearance: professional, clean, no glaring layout issues

## Fix Recommendations

### Fix 1: Remove scroll-behavior: smooth from html (EASIEST, IMMEDIATE)
In the graham martin CSS block, remove or change:
```css
html {
  scroll-behavior: smooth;  /* REMOVE THIS — conflicts with SmoothScroll.js */
  background: var(--pb-dark);
}
```

### Fix 2: Disable artistics SmoothScroll.js on this page (BEST FIX)
Add this to the page's inline JS BEFORE the SmoothScroll.js runs:
```javascript
window.SmoothScrollOptions = { animationTime: 0 };  // disable smoothing
// OR: Override after load
window.addEventListener('load', function() {
  if (window.SmoothScroll) SmoothScroll.destroy();
});
```
OR: Use WordPress to dequeue the script on this specific page template.

### Fix 3: Add will-change to animated gradient elements
```css
#gm-hero .hero-gradient-1,
#gm-hero .hero-gradient-2,
#gm-hero .hero-gradient-3 {
  will-change: transform;  /* promote to own GPU layer */
}
```

### Fix 4: Reduce backdrop-filter cost (optional)
Consider using solid `rgba()` backgrounds on the nav bars instead of blur:
```css
#gm-nav { background: rgba(8,10,18,0.96); /* no backdrop-filter */ }
```

## Patterns to Remember
- Artistics theme ALWAYS loads SmoothScroll.js — will affect ALL purebrain.ai pages on Chrome
- CSS `scroll-behavior: smooth` + SmoothScroll.js = double smooth scrolling = jank
- `backdrop-filter: blur()` on fixed elements is expensive — use sparingly
- The page's custom scroll JS uses `{passive: true}` correctly — that's NOT the issue
- GSAP/ScrollTrigger load but have no active instances on this page (only fires for .at-animation-* elements)
