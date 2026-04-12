# Memory: PureBrain Frontend 3D Login Integration
**Date**: 2026-02-24
**Type**: technique
**Topic**: Integrating Three.js 3D neural network login into large frontend app

## What Was Done
Merged the standalone `purebrain-portal-login-3d.html` (1,828 lines) neural network login screen into `purebrain-frontend.html` (13,525 lines), producing `exports/purebrain-frontend-3d.html` (14,495 lines).

## Key Decisions

### CSS Namespacing
- All 3D login CSS classes prefixed with `pb-` to avoid collisions (`.pb-login-card`, `.pb-signin-btn`, etc.)
- All keyframe animations prefixed with `pb` (e.g. `pbCardMaterialize`, `pbLogoReveal`)
- CSS custom properties scoped under `#loginOverlay` selector to contain them

### Three.js Importmap Placement
- Importmap MUST go before `</head>`, not before `</body>` — browsers require importmaps before any module scripts
- Pattern: `<script type="importmap">` immediately after the main `</style>`, before `</head>`

### Canvas Container Approach
- `#pb-canvas-container` div placed immediately before `#loginOverlay` in HTML (z-index 9999 vs 10000)
- Default CSS: `display: none`
- JS shows/hides via `container.style.display` inline style (overrides CSS)
- MutationObserver watches `loginOverlay.classList` for `'hidden'` class changes
- Also checked every animation frame via `checkLoginVisibility()`

### handleLogin() Button State
- Original code used `btn.textContent = 'Signing in...'` — incompatible with HTML button structure
- Updated to `btn.classList.add('loading')` / `btn.classList.remove('loading')`
- Button has `.btn-text` span and `.btn-loading` span inside — CSS hides/shows based on `.loading` class

### loginError Element
- Changed from old `login-error` class to `pb-error` class
- Old code used `errorEl.style.display = 'block'/'none'` — works fine with `pb-error` since CSS sets `display: none` initially
- Added `showLoginError()` override in post-login script for shake animation

### "Configure gateway manually" — REMOVED
- Confirmed: remove from frontend version per Jared's instruction
- Only appears in old standalone version for demo purposes

### CSS Duplicate Selectors
- `#loginOverlay` appears twice in CSS — first block sets CSS custom props (`--pb-card-bg` etc.), second block sets layout (position, z-index, padding)
- This is valid CSS — both blocks cascade and merge

## Output
- `/home/jared/projects/AI-CIV/aether/exports/purebrain-frontend-3d.html`
- 14,495 lines (was 13,525 base + 970 added for 3D login)
- All original IDs preserved: `loginOverlay`, `loginAicivName`, `loginSecret`, `loginButton`, `loginError`, `handleLogin()`
- Neural network fires on load, pauses when overlay gains `.hidden` class
- Full responsive support with mobile breakpoints
