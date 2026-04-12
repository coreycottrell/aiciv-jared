# Memory: Task Dashboard v3 — 3D Neural Login Merge

**Date**: 2026-02-25
**Type**: build | deployment | pattern
**Agent**: dept-systems-technology

---

## What Was Built

Merged the 3D neural network login design from the PureBrain Hub React app
into the self-contained Pure Technology team task assignment dashboard HTML.

**Output file**: `exports/team-dashboard-v3.html` (83KB, 2,515 lines)
**Deployed to**: https://pure-tech-dashboard.netlify.app
**Deploy ID**: 699edb7843c362090f5f3626

---

## Source Files Used

1. `exports/team-dashboard.html` — v1 dashboard (62KB, 1,863 lines)
   - Airtable integration, 49-member team roster, admin CRUD, task cards, A/B/C delegation system
   - Used: All functionality preserved 100%

2. `tools/purebrain_hub/src/components/Login.jsx` — React 3D login component
   - Extracted: NeuralCanvas animation logic (IIFE-converted from React hooks)
   - Extracted: AetherOrb CSS animations
   - Extracted: Glass-morphism login card design
   - Extracted: All CSS keyframes (aetherPulse, aetherRingRotate, statusPulse, etc.)

3. `tools/purebrain_hub/src/styles/main.css` — Hub CSS
   - Extracted: .neural-canvas, .login-card, .login-page, .aether-orb*, .login-btn-primary
   - Extracted: All login-specific CSS (input focus glow, spinner, footer divider)

4. `docs/from-telegram/purebrain-frontend-3d.html` — 3D reference (lines 5415-5620)
   - Cross-referenced canvas code patterns

---

## Key Technical Decisions

### React-to-Vanilla Conversion
The NeuralCanvas was a React functional component using `useRef` and `useEffect`.
Converted to a vanilla JS IIFE (`initNeuralCanvas()`) called immediately on script load.
- `canvasRef.current` → `document.getElementById('neural-canvas')`
- `useEffect cleanup` → stored in `animRunning` flag
- Particle factory functions preserved exactly

### Canvas Persistence After Login
Instead of destroying the canvas on login, implemented smooth opacity dimming:
- `window.setCanvasAlpha(0.18)` dims canvas to 18% after successful login
- Canvas continues animating as subtle background behind dashboard
- On logout: `setCanvasAlpha(1)` restores full opacity
- Smooth interpolation: `canvasAlpha += (targetAlpha - canvasAlpha) * 0.05` per frame

### Login Form Mapping
Original dashboard had: select name + email input (matched against TEAM_ROSTER)
New design preserves the same auth logic with premium UI:
- Glass select dropdown for name (same options, same validation)
- Glass email input (same format)
- Loading spinner state (600ms artificial delay for UX feel)
- Orange border glow on focus (from hub CSS)

### Auth Preserved
Authentication is unchanged — still checks name + email against TEAM_ROSTER array.
49 members, isAdmin flag on Jared Sanborn only.

### Font Addition
Added Google Fonts: Oswald + Inter (used in login title + button labels)
These are CDN-loaded; the file remains self-contained in function but requires network for fonts.
Inter is already system fallback so fonts degrade gracefully offline.

---

## Deployment Pattern

```bash
NETLIFY_AUTH_TOKEN=$(grep NETLIFY_AUTH_TOKEN .env | cut -d= -f2)
mkdir -p /tmp/dashboard-deploy
cp exports/team-dashboard-v3.html /tmp/dashboard-deploy/index.html
cd /tmp/dashboard-deploy && npx netlify deploy --prod --dir=. --auth=$NETLIFY_AUTH_TOKEN --site=pure-tech-dashboard
```

Site ID alias: `pure-tech-dashboard` (Netlify resolves to site ID automatically)

---

## What Was Preserved From v1

- All 49 team members with emails, initials, roles
- Admin-only panel (Jared Sanborn, jaredsanborn@gmail.com)
- Airtable CRUD: create/read/update/delete tasks
- Demo tasks fallback when Airtable is unavailable
- Status cycling: Pending → In Progress → Complete → Pending
- A/B/C delegation system with color-coded badges
- Priority badges (High/Medium/Low)
- Deadline tracking with overdue/soon indicators
- File attachment chips (Google Drive links)
- Search and filter bar
- Stats row (5 metrics)
- Session storage for login persistence
- Toast notifications
- Loading overlay with spinner

---

## Verification Evidence

All 20 component checks passed before deployment:
- 3D Neural Canvas, Aether Orb CSS, Glass login card, Login card animation
- Team roster (49), Airtable config, Admin panel, Task grid
- Status cycle, Delete task, Demo fallback, Session storage
- Canvas alpha dimming, Delegation A/B/C, Neural rings, Scan beam
- BG nodes, Secondary orbs, Login btn loading, Oswald font

Deploy confirmed live: https://pure-tech-dashboard.netlify.app
