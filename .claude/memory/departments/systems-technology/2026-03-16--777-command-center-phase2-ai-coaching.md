# 777 Command Center Phase 2 — AI Coaching Layer

**Date**: 2026-03-16
**Type**: build
**Status**: DEPLOYED — READY (pending ANTHROPIC_API_KEY env var)

## What Was Built

Full AI coaching layer for the 777 Command Center at https://777-command-center.vercel.app

### Files Created / Modified
- `exports/777-command-center/api/chat.js` — NEW: Vercel serverless function proxying to Claude API
- `exports/777-command-center/vercel.json` — UPDATED: Added functions config and /api/chat route
- `exports/777-command-center/exercises.html` — UPDATED: Full AI chat UI, replaced 6 placeholder panels

### Architecture Decision
Vercel serverless function (`api/chat.js`) chosen over direct client-side calls.
Rationale: API key must never be in client code. The project is already on Vercel, making this zero-friction.

### Security Measures in api/chat.js
1. API key stored as Vercel env var — never in code
2. Per-IP rate limiting: 20 requests/minute (in-memory Map, resets per cold start — sufficient for personal tool)
3. Origin check: only *.vercel.app origins allowed
4. Request body validation: module whitelist, messages array required
5. Message sanitization: max 10 turns depth, max 2000 chars per message
6. First message must be from user (Claude API requirement)
7. System prompt context limited to 3000 chars
8. Max tokens: 600 per response (keeps costs low for coaching interactions)
9. Model: claude-haiku-4-5 (fast, cost-effective for coaching)

### AI System Prompts — One Per Module
- **reflection**: Daily check-in pattern analysis, Tim Ferriss meets Naval style
- **fear**: Stoic Fear Setting challenge, Socratic questioning
- **goals**: Strategic goal advisor, progress vs time analysis
- **ceo**: Weekly CEO Brief generator, 7 F's trend analysis
- **ritual**: Morning ritual optimizer, completion rate analysis
- **gratitude**: Gratitude depth coach, theme detection

### Context Passing
`gatherAIContext(module)` collects localStorage data specific to each module:
- Reflection: today's scores + 7-day history
- Fear: current fear inputs from DOM
- Goals: vision + yearly goals with progress percentages
- CEO: current week scores/wins/lessons + 8-week trend history
- Ritual: completion rates over 7 days per item
- Gratitude: today's entries + 14-day history

### UX
- "Ask AI" buttons now call `openAIPanel()` instead of `toggleAskAI()`
- Starter pills (3 per module) for zero-friction first messages
- Pills hidden after first use
- Auto-greeting on first open (no blank state)
- Typing indicator (3-dot bounce animation)
- Enter to send, Shift+Enter for new line
- Auto-resize textarea
- Scrollable message history (max 340px)
- Error messages shown in red bubble (not mixed into conversation)
- Close button on each panel

## One Manual Step Required
Jared must set ANTHROPIC_API_KEY in Vercel dashboard:
1. Go to https://vercel.com/pure-marketing-groups-projects/777-command-center/settings/environment-variables
2. Add: Name = ANTHROPIC_API_KEY, Value = sk-ant-... (get from Anthropic console)
3. Check "Production" environment
4. Redeploy (or it auto-applies on next deploy)

Without this env var, the serverless function returns 500 "AI service not configured."

## Deployment Info
- Deployment ID: dpl_GAsYrSysiqoepicTo3wAqyBZDAvf
- State: READY
- Preview URL: 777-command-center-dudmvtw1e-pure-marketing-groups-projects.vercel.app
- Production URL: 777-command-center.vercel.app
- Team: pure-marketing-groups-projects (team_UY8ko0aXMklAF933yVSHsBfU)
- Project ID: prj_N18auQqHO0GgpwJv4rWoEeb8o1QC

## Gotchas
- Vercel v13 deployment API does NOT accept `projectId` in the body — use v12 endpoint
- The ANTHROPIC_API_KEY was NOT found in .env or anywhere in the repo — it lives only in Cloudflare Worker secrets
- vercel.json `cleanUrls` was already set; kept it; added `functions` and `routes` blocks
