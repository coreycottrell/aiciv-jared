# Portal Login 3D Neural Network Integration

**Date**: 2026-03-03
**Agent**: dept-systems-technology
**Type**: Integration pattern

## What Was Done

Replaced the simple `#auth-overlay` login on the PureBrain portal with the full 3D Neural Network login from v7 HTML file, with one key change: consolidated 2 fields ("AI Name" + "Secret") into 1 field (Bearer Token).

## Source File
`/home/jared/projects/AI-CIV/aether/docs/from-telegram/purebrain-frontend-3d wlogin v7.html`

## Target File
`/home/jared/purebrain_portal/portal-pb-styled.html`

## Key Technical Patterns

### Portal uses different CSS vars than v7
- v7 uses `var(--font-heading)` and `var(--font-body)`
- Portal uses `var(--font-ui)` and `var(--font-mono)`
- FIX: Add `--font-heading` and `--font-body` to portal `:root` vars pointing to Oswald

### Auth element ID mapping (old -> new)
- `#auth-overlay` -> `#loginOverlay`
- `#token-input` -> `#loginToken`
- `#auth-btn` -> `#loginButton`
- `#auth-error` -> `#loginError`

### Login visibility pattern
- Old portal: `overlay.style.display = 'none'` on success
- New v7 pattern: `overlay.classList.add('hidden')` (CSS `display:none`)
- Also must: `document.body.classList.remove('login-active')` to stop 3D rendering

### 3D canvas show/hide
- CSS: `.login-active #pb-canvas-container { display: block; }`
- Body gets `login-active` class on page load (in JS)
- Body loses `login-active` class on successful auth
- 3D JS also watches `loginOverlay` classList via MutationObserver

### Loading state
- Old: `authBtn.textContent = 'Authenticating...'`
- New: `authBtn.classList.add('loading')` (CSS shows spinner via `.pb-signin-btn.loading`)

### Form submit wiring
- v7 form uses `onsubmit="handlePBLogin(); return false;"`
- Expose as `window.handlePBLogin = function() { doAuth(); };` in portal JS

### Error display
- New error div is `display:none` by default (CSS `.pb-error`)
- Must set `.style.display = 'block'` when showing errors
- Clear `authBtn.classList.remove('loading')` on error too

## Three.js importmap
Must go in `<head>` BEFORE `</head>`. The portal originally had no importmap. The `<script type="module">` 3D script depends on it.

## Files Modified
- `/home/jared/purebrain_portal/portal-pb-styled.html` (main change)
- Backup: `/home/jared/purebrain_portal/portal-pb-styled.html.bak`

## Verification
- 30/30 checks passed
- Portal served HTTP 200
- Live response contained 21 matches for new login elements
- File delivered to Jared via Telegram
