# Master PureBrain Hub Build Brief

**Prepared by**: Aether (Pre-read of all 4 reference files complete)
**Date**: 2026-02-25
**Status**: READY TO EXECUTE (awaiting Jared's dashboard v4 approval)

---

## THE VISION (From Jared's Brain Stream Master File)

A self-evolving AI command center where:
- Overnight tasks auto-populate Google Drive folders → auto-fire department managers
- Department managers fire up their agents/brains
- When AI brains need human help → task appears in hub for humans
- Human marks task complete (with double-check confirmation popup)
- AI brain picks back up where it left off
- All usage tracked → dynamic daily improvement

**Deploy**: https://pure-tech-dashboard.netlify.app/ (eventually app.puretechnology.ai)

---

## CRITICAL REBRAND: Agents → Brains

- All frontend references: "Agent" → "Brain"
- Visual: "CTO Brain had 2 full stack brains do abc"
- Backend/internal: can keep "agent" for technical reference
- This applies EVERYWHERE on the frontend

---

## SYSTEMS TO COMBINE

### System 1: Team Dashboard v4 (Current)
- **File**: `exports/team-dashboard-v4.html` (183KB, self-contained)
- **Features**: 3D neural login, task CRUD modal, admin table/card toggle, status cycling, Supabase sync, Team view (49 members), A/B/C delegation, department filters, glass-morphism UI

### System 2: PureBrain Hub MVP (React + Express)
- **Files**: `tools/purebrain_hub/` (18 files, React + Vite + Express + sql.js)
- **Features**: Login (token-based), dashboard feed with stats/tag filters/leaderboard, create post with image upload, wins board with impact badges, file upload with drag-and-drop + GDrive sync, reactions (celebrate/inspired/learned)

### System 3: Portal Preview
- **File**: `docs/from-telegram/purebrain-hub-portal-latest.html` (59 lines)
- **Features**: App layout with sidebar, dark theme, PureBrain blue/orange styling

---

## FEATURE REQUIREMENTS

### Must Have (Phase 1)
1. **Combined Login** - 3D neural animation + token auth
2. **Task Management** - Full CRUD from v4 + AI delegation tracking
3. **Brain Stream Feed** - Posts, reactions, tag filtering from MVP
4. **Team/Brain Directory** - 49 members rebranded as "Brains"
5. **File Management** - Upload, drag-and-drop, Google Drive sync
6. **Wins Board** - Visual grid with impact badges
7. **Morning Download** - Overnight output auto-split into folders, synced with GDrive
8. **Double-Check Popup** - "Are you certain this is complete?" on task completion

### Should Have (Phase 2)
9. **Lyra Integration** - Shared task board with sister AI
10. **Auto Team Builder** - Auto-create teams for projects
11. **Google Docs → Tasks** - Strategic linking, auto-invite
12. **Dynamic Improvement** - Usage tracking → daily optimization
13. **Real-time Cross-AI Visibility** - What Aether and Lyra are working on

### Lyra's Suggested Segmentation
- **PureTech (Internal Ops)**: Aether = infrastructure, platform; Lyra = automation, team tools
- **Pure Marketing (Client Work)**: Lyra = client strategies, outreach; Aether = website, SEO, blog
- **PureBrain (Product)**: Aether = core product, API, frontend; Lyra = launch marketing, GTM

---

## TECH STACK DECISION

**Option A**: Self-contained HTML (like v4) - simpler deploy, no server
**Option B**: React + Express (like MVP) - more features, needs server
**Option C**: React frontend → static build → Netlify (best of both)

**Recommended**: Option C
- React + Vite frontend builds to static HTML/JS/CSS
- Express backend for API (can run on Jared's server)
- Netlify hosts static frontend
- API calls go to Express backend (or use localStorage/Supabase for MVP)

---

## DEPLOYMENT PLAN

1. **CTO (ST#)** spins up multiple full-stack devs in parallel
2. **Dev 1**: Merge v4 dashboard features into React app
3. **Dev 2**: Build task management + AI delegation tracking
4. **Dev 3**: Morning download + GDrive integration
5. **Security Review**: security-engineer-tech audits all code
6. **QA**: qa-engineer tests all features
7. **Ship**: Deploy to Netlify

---

## RESEARCH REFERENCES (From Jared)
- Monday.com - project management features
- usemotion.com - AI-driven scheduling
- https://squeezegrowth.com/best-usemotion-alternatives/ - alternatives list
- Jared offered free trials for Playwright-based mapping if needed

---

## KEY DECISIONS NEEDED FROM JARED
1. Self-contained HTML vs React app? (recommend React for this scale)
2. Backend: Jared's VPS vs serverless vs Supabase?
3. Priority features for Phase 1 vs Phase 2?
4. Which team members to add first? (Jared said "I'll give you a list")
5. Lyra connection method: comms hub vs shared Google Drive vs both?
