# Gleb Mastery Day 7 - Production Embed Package + PostMessage API

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Production iframe embed with PostMessage API, chunkSizeWarningLimit, sprint capstone patterns

---

## Memory Search Results

- Searched: All 6 prior sprint memory files (Night 1 through Day 6)
- Found: Complete recipe (Night 1), R3F equivalence map (Day 2), Vite project + samples=8 (Day 3), GLB + spring + code split (Day 4), JSX quality gap closed + adaptive quality (Day 5), audio-reactive + cursor + env presets + avatar modes (Day 6)
- Applied: All prior parameters directly. Zero rediscovery. 7-day sprint with zero repeated investigation.

---

## Core Teaching 1: PostMessage API Architecture for iframe Embeds

The most reliable pattern for WordPress → iframe 3D communication:

### Three-Layer Architecture

```
Layer 1: embed/index.html (static HTML page)
  - PostMessage listener (before React mounts)
  - Origin validation (ALLOWED_ORIGINS array)
  - window.__avatarState = { mode: 'idle', preset: 'studio' }
  - window.__setAvatarMode = null  (filled by React after mount)
  - window.__setAvatarPreset = null  (filled by React after mount)
  - window.__onSceneReady = function() { /* fires READY event */ }

Layer 2: React App.jsx (mounted after index.html loads)
  - Reads window.__avatarState for initial state
  - Fills window.__setAvatarMode via useEffect
  - Fills window.__setAvatarPreset via useEffect
  - Calls window.__onSceneReady() in handleWebGLReady

Layer 3: parent WordPress page (embed.html integration)
  - iframe.contentWindow.postMessage(msg, ORIGIN)
  - window.addEventListener('message', ...) for READY/PONG events
  - window.PureBrain3D.setMode() public API
```

### Why window.__ not window.dispatchEvent

Custom events require `document.dispatchEvent(new CustomEvent(...))` which is cross-document blocked.
PostMessage works across document boundaries but requires origin verification.
window.__ (global functions) work because the index.html PostMessage handler and React app share the same window object (same iframe document).

### Security: ALLOWED_ORIGINS Pattern

```javascript
const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'http://localhost:3000',
]

function isAllowedOrigin(origin) {
  if (origin === 'null') return true  // file:// dev
  return ALLOWED_ORIGINS.some(allowed =>
    origin === allowed || origin.endsWith('.purebrain.ai')
  )
}
```

The `.endsWith('.purebrain.ai')` pattern allows subdomains (staging.purebrain.ai, etc.)
without maintaining an exhaustive list.

---

## Core Teaching 2: Initial State Bridge Pattern

Problem: React mounts async (100-400ms after HTML page loads). PostMessage commands sent immediately after iframe load arrive before React has set up handlers.

Solution: Two-phase state injection:

```
Phase 1: index.html sets window.__avatarState (synchronous, immediate)
Phase 2: React reads window.__avatarState during useState() initialization

// In index.html (before React):
window.__avatarState = { mode: 'idle', preset: 'studio' }

// In App.jsx:
const initialState = (typeof window !== 'undefined' && window.__avatarState) || {}
const [avatarMode, setAvatarMode] = useState(initialState.mode || 'idle')
```

Commands queued by the PostMessage handler (before React is ready) drain when React fills `window.__setAvatarMode`.

---

## Core Teaching 3: Vite chunkSizeWarningLimit

Three.js is always ~725 kB uncompressed / ~188 kB gzipped. Vite's default warning threshold is 500 kB (uncompressed). This generates a false positive warning on every build.

```javascript
// vite.config.js
export default defineConfig({
  build: {
    chunkSizeWarningLimit: 1000,  // 1000 kB = suppress Three.js warning
    rollupOptions: {
      output: {
        manualChunks: { three: ['three'], r3f: [...], pp: [...], motion: [...] }
      }
    }
  }
})
```

The 1000 kB limit is not dangerous: it's raising a warning threshold, not disabling size checking. Actual delivery is 188 kB gzip (browser sees compressed size). The uncompressed 725 kB never touches the wire.

---

## Core Teaching 4: useEffect for window API Registration

When exposing functions on `window` from React, always use useEffect:

```javascript
useEffect(() => {
  window.__setAvatarMode = (mode) => {
    // validate and call React state setter
    handleAvatarModeChange(mode)
  }

  return () => {
    delete window.__setAvatarMode  // cleanup on unmount
  }
}, [handleAvatarModeChange])  // re-register if callback changes
```

Do NOT define window.__ at module level or in render (stale closures, no cleanup).
useEffect guarantees: runs after mount, cleanup on unmount, fresh callback when deps change.

---

## Core Teaching 5: The Sprint Memory Compound Effect

Across 7 days, zero rediscovery was needed. Every day started from the exact point the previous day ended.

**What this means for future 3D sessions:**
- Search `.claude/memory/agent-learnings/3d-design-specialist/` FIRST
- 7 files covering: complete Gleb recipe, R3F patterns, Vite project, GLB loading, spring physics, code splitting, JSX quality gap, adaptive quality, loading screen, audio-reactive, cursor-reactive, environment presets, avatar modes, PostMessage embed

Estimated total investigation time saved across 7 days by memory-first protocol: ~8-12 hours (each day would have re-derived prior days' findings from scratch).

---

## Gotchas Discovered Day 7

**Gotcha 1: ALLOWED_ORIGINS and file:// protocol**
```javascript
// origin is 'null' (the string) for file:// protocol, not null (null type)
if (origin === 'null') return true  // file:// dev
```
Testing locally with file:// results in origin = 'null' (string). Must handle this separately.

**Gotcha 2: useEffect dependency array for window callbacks**
If `handleAvatarModeChange` is defined with useCallback inside the component, it has stable identity ONLY if its own dependencies are stable. Pass it in the useEffect dependency array.
```javascript
// Correct:
useEffect(() => {
  window.__setAvatarMode = mode => handleAvatarModeChange(mode)
  return () => delete window.__setAvatarMode
}, [handleAvatarModeChange])  // INCLUDE the callback
```

**Gotcha 3: PostMessage to parent when page is top-level**
In dev mode (not inside iframe), `window.parent === window`. PostMessage to parent = PostMessage to self.
Check before sending to avoid self-messaging:
```javascript
if (window.parent !== window) {
  window.parent.postMessage({ type: 'READY' }, '*')
}
```

**Gotcha 4: Build asset hashes change every build**
The compiled JS entry has a hash in its filename (e.g., `index-BwzLgeiR.js`).
The `embed/index.html` script tag must reference this hashed filename.
Solution: after each build, update the script tag in embed/index.html,
OR use a redirect file (`main.js` that re-exports the hashed entry).

---

## Sprint Final Build Output

```
dist/assets/motion-BheSypY2.js     30.59 kB │ gzip:  11.57 kB
dist/assets/index-BwzLgeiR.js     40.83 kB │ gzip:  12.01 kB
dist/assets/pp-D4hu7zPD.js        87.12 kB │ gzip:  20.89 kB
dist/assets/r3f-GDf76nXz.js      493.21 kB │ gzip: 155.67 kB
dist/assets/three-DrdX3_7U.js    724.98 kB │ gzip: 187.65 kB
TOTAL: ~388 kB gzipped
Build time: 20.54s
Warnings: 0
Errors: 0
```

---

## Files Created Day 7

- `exports/gleb-r3f-scene/embed/index.html` - iframe src page (PostMessage + loading)
- `exports/gleb-r3f-scene/embed/embed.html` - visual code reference
- `exports/gleb-r3f-scene/README-EMBED.md` - deployment guide
- `exports/gleb-r3f-scene/API.md` - complete component API reference
- `exports/3d-mastery-sprint-complete.md` - full sprint assessment + mastery checklist
- `exports/3d-mastery-day7-report.md` - day report
- `exports/gleb-r3f-scene/src/App.jsx` - updated with PostMessage wiring
- `exports/gleb-r3f-scene/vite.config.js` - updated with chunkSizeWarningLimit

## Memory Written

This file.

Path: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-21--gleb-mastery-day7-embed-capstone.md`
Type: teaching
Topic: Production iframe embed, PostMessage API, chunkSizeWarningLimit, sprint capstone patterns
