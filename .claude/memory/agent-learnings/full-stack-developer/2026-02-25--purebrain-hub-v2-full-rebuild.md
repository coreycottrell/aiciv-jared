# PureBrain Hub V2 Full Rebuild

**Date**: 2026-02-25
**Type**: operational + teaching
**Agent**: full-stack-developer

## Summary

Rebuilt the PureBrain Hub from the React source repo into a complete single-file HTML app (V2). Jared reported V1 was "missing a lot of things" and the login was "all messed up."

## What Was Done

1. Read all 7 React components from `/home/jared/projects/AI-CIV/aether/tools/purebrain_hub/src/`
2. Read the complete `main.css` (1312 lines)
3. Converted ALL React JSX to vanilla JS + HTML
4. Built complete 84KB single-file HTML at `/home/jared/projects/AI-CIV/aether/exports/purebrain-hub-v2.html`
5. Copied to `/home/jared/projects/AI-CIV/aether/tools/purebrain-hub-static/index.html`
6. Deployed to https://purebrain-hub.vercel.app

## Key Features Restored / Added

### Login (The Primary Ask)
- Full `NeuralCanvas` animated background: rotating rings, scan beam, particles, neural network dots + connection lines
- `AetherOrb` CSS animation: 3 orbital particles + pulsing core + rotating inner/outer rings
- Token auth: `team2025`, `safety2025`, `quality2025`, `demo`
- Guest mode with name entry
- Glass-morphism login card with gradient CTA button (orange-to-blue)
- Fade-in animation on card mount
- "COMMAND CENTER ONLINE" pulsing status dot

### Dashboard
- Stats grid: Total Stories, Team Wins, Total Reactions
- Filter bar: All Posts, Wins, Safety, Quality, Efficiency, Innovation
- Post feed with post cards (reactions, tags, timestamps)
- Right sidebar: Leaderboard, Tag Distribution, Drive Sync Status, Share Win CTA

### Wins Board
- Header stats: total wins, total reactions, per-category counts
- Filter by tag + sort by Most Recent / Most Celebrated
- Win cards with colored headers, impact badges, emoji, stats

### Files & Uploads
- Drag-and-drop upload zone
- File description + tag selection before upload
- Files list with filter bar
- GDrive sync status + Sync button
- File icons by MIME type
- Format file size helper

### Create Post Modal
- Author display with avatar
- Win/regular toggle (animated switch)
- Title + content fields
- Tag selection (Safety, Quality, Efficiency, Innovation)
- Image upload with preview + remove
- Drag & drop on image zone

### General
- Full sidebar navigation
- Top bar with current view title + New Post button
- Toast notifications (success/error/info, 3.5s auto-dismiss)
- Session persistence via localStorage
- Logout functionality
- Fully responsive (900px and 600px breakpoints)

## Technical Patterns

### React-to-Vanilla Conversion
- `useState` → plain JS variables + re-render functions
- `useEffect` → `initAuth()` at boot
- `createContext/useContext` → module-level `currentUser` variable
- Event handlers inline in HTML strings or as global functions
- `formatDistanceToNow` from date-fns → custom `timeAgo()` helper

### NeuralCanvas Faithfulness
The canvas animation was ported exactly from Login.jsx:
- Same ring config (4 rings with different radii/speeds/segments)
- Same particle system with trail rendering
- Same scan beam (conic gradient with fallback to radial)
- Same data arcs
- Same center glow
- Same secondary orbs at 10%/20% and 90%/80% of screen

### Build Strategy (Large File)
Used bash heredoc chunks (3-5KB each) to build the file incrementally:
```bash
cat > file.html << 'EOF'
[first chunk]
EOF
cat >> file.html << 'EOF'
[next chunk]
EOF
```
This avoids the Write tool failing on large files.

### Deployment
- Static site at `/home/jared/projects/AI-CIV/aether/tools/purebrain-hub-static/`
- Deploy command: `cd tools/purebrain-hub-static && npx vercel --prod --yes`
- Live URL: https://purebrain-hub.vercel.app
- Build time: ~13 seconds

## Files

- Source: `/home/jared/projects/AI-CIV/aether/exports/purebrain-hub-v2.html` (84KB, 1828 lines)
- Deployed: `/home/jared/projects/AI-CIV/aether/tools/purebrain-hub-static/index.html`
- React source: `/home/jared/projects/AI-CIV/aether/tools/purebrain_hub/src/`

## Lessons

1. Always read ALL source components before building - V1 was missing features because the original React components weren't fully ported
2. The NeuralCanvas is the heart of the login experience - Jared cares deeply about it
3. Bash heredoc chunks are reliable for large files; always verify with wc -c after each chunk
4. Run a Python verification script checking for all key features before deploying
5. The `cx_last/cy_last` functions in the React source should be inlined when converting to vanilla JS
