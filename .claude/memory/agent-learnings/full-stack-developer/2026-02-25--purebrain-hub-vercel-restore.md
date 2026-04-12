# PureBrain Hub Vercel Restore — Merge Netlify + V1

**Date**: 2026-02-25
**Type**: operational
**Agent**: full-stack-developer

## Summary

Restored features from the original Netlify repo version into the live Vercel hub (purebrain-hub.vercel.app). The Netlify version had a much richer login UI; the Vercel V1 had more complete app features.

## Key Differences Found

### Netlify repo had (but V1 was missing):
1. **NeuralCanvas** — Full-screen animated canvas with rotating rings, scan beams, particles, background neural network
2. **AetherOrb CSS animation** — 3-ring orbiting orb above login form with pulsing core
3. **Token-based login** — Demo tokens (team2025, safety2025, demo) vs simple email/password
4. **Richer login card** — Glass-morphism, gradient button, status dot, guest toggle
5. **Animated orb float** on login wrapper

### V1 had (Netlify was missing or more basic):
1. **All app views** — Dashboard, Brain Stream, Tasks, Wins Board, Team Directory
2. **32 agent BRAINS data** — full team roster
3. **Task board** with filter chips
4. **Win logging modal**
5. **Keyboard shortcuts** (1-5 to switch views, / for search)

## What Was Built

Merged file at:
- `/home/jared/projects/AI-CIV/aether/exports/purebrain-hub-v1.html` (86KB)
- `/home/jared/projects/AI-CIV/aether/tools/purebrain-hub-static/index.html` (copied)

### New features added on top of V1:
- Full NeuralCanvas implementation (pure JS, no React dependency)
- AetherOrb CSS animation on login
- Token-based auth with demo users + guest fallback
- Team Profile Section header with stats (AI count, human count, total) and dept filter chips
- User-aware sidebar (name/initials update on login)
- Dynamic dept filter for team directory

## Deployment

```
cd /home/jared/projects/AI-CIV/aether/tools/purebrain-hub-static
npx vercel --prod --yes
# → https://purebrain-hub.vercel.app (200 OK)
```

## Token Auth
- `team2025` → Jared Sanborn (Admin)
- `safety2025` → Sarah K. (Safety Lead)
- `quality2025` → Marcus T. (Quality Manager)
- `demo` → Demo User

## Pattern: Netlify→Vercel static migration
When converting React components to self-contained HTML:
1. Inline all CSS from main.css
2. Convert React JSX to vanilla JS DOM rendering
3. Replace useState/useEffect with module-level STATE object
4. Canvas animations work identically in vanilla JS
5. No bundler needed — single HTML file deploys directly
