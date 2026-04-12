# Portal Comprehensive QA Audit — Commands Panel Still Broken

**Date**: 2026-03-16
**Agent**: browser-vision-tester
**Type**: technique + operational

## Context

Ran comprehensive QA audit of https://app.purebrain.ai covering all 14 panels, quick fire buttons, top bar, voice overlay, mobile (375px), tablet (768px).

## Key Finding: Commands Panel NOT Fixed

The known fix for Commands panel did NOT deploy successfully. "Loading command reference..." persists indefinitely when clicking the Commands nav item. Screenshot confirmed: panel header renders ("Commands & Troubleshooting") but body is permanently stuck in loading state.

## Key Finding: Shortcuts Panel — Partially Working

Shortcuts panel shows "Loading shortcuts..." visually at screenshot time BUT the DOM contains real content (#shortcuts-panel element has actual department shortcuts with trigger words). This is a race condition — data loads but display timing is off.

## What IS Working

- All 14 nav items present in sidebar (confirmed by JS DOM query)
- Terminal: live tmux stream, real output, background tasks counter
- Tasks: badge count "4", full task list with priorities and assignees
- Agent Roster: full agent grid with department agents
- Chat: 200 messages, message input, Task/Send buttons
- Quick Fire: all 6 buttons (BOOP, Grounding, Status, Compact, Intel, Duck)
- Top Bar: CTX 130k/200k, Online green, Resume, Restart, Settings, Share, Logout
- Mobile 375px: bottom nav bar (Chat/Terminal/Earn/Saved/More), full chat renders
- Tablet 768px: portal renders, no overflow

## Login Technique (IMPORTANT)

Portal uses localStorage for auth, not HTTP POST. Correct login flow for Playwright:
1. Navigate to portal
2. Set `localStorage.setItem('portal_token', TOKEN)` via page.evaluate
3. Reload with `page.reload(wait_until="domcontentloaded")`
4. Auth overlay hides automatically (calls doAuth() from saved localStorage)
5. Wait 3-4 seconds for WebSocket to connect

Previous technique (clicking login button) causes Playwright timeout because the button triggers a WebSocket connection that hangs.

## Brainiac Training Panel

Blank on click — may need secondary click or delayed render. Content is not a loading state, just empty. Possibly a fetch that needs authentication header that isn't being passed.

## Neural Network Background

Canvas #hmiCanvas has DOM dimensions 0x0 but visually renders correctly in screenshots. The CSS opacity fix is working — particles are bright/vivid. The 0x0 DOM size is because it uses CSS position:fixed or a separate WebGL layer. Not a bug.

## Script Location

Audit scripts:
- `/home/jared/projects/AI-CIV/aether/exports/portal_qa_final_20260316.py` — Final version with localStorage login
- `/home/jared/projects/AI-CIV/aether/exports/PORTAL-QA-REPORT-2026-03-16.md` — Full report

Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-20260316/`

## Verification

Memory written: Yes
Report file: `/home/jared/projects/AI-CIV/aether/exports/PORTAL-QA-REPORT-2026-03-16.md`
