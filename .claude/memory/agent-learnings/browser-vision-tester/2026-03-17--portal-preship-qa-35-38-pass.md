# Portal Pre-Ship QA — 35/38 Pass, Ship-Ready

**Date**: 2026-03-17
**Agent**: browser-vision-tester
**Type**: operational + technique
**Tags**: portal, pre-ship, commands, shortcuts, agents, mobile, dark-theme

## Context

Full pre-ship QA of https://app.purebrain.ai covering all 18 test areas from Jared's spec. Run after the agentsInterval IIFE scope fix was deployed.

## Summary

35/38 PASS. 1 FAIL (Shortcuts cold-click timing — not a blocker). 2 WARN (minor).

## Critical Fix Verified: Commands Panel

The agentsInterval scope fix IS deployed and working. Commands panel loads real data immediately on click:
- Server IP 89.167.19.20, SSH Port 22, SSH User jared
- SSH Access commands with copy buttons
- Status Checks section
- Log Files section
- Zero console errors (the ReferenceError is gone)

## Shortcuts Panel Timing Issue

The Shortcuts panel DOES work but needs the page to be fully initialized before click. Cold-click (immediately after page load) → brief "Loading shortcuts..." state. After 4-5s wait or on second click → full data loads instantly.

Root cause: loadShortcuts() is called from switchPanel(), but if shortcuts API response hasn't been pre-loaded, it shows the loading state. The data IS available (3,342 bytes from API). Fix: pre-load shortcuts on page init or add small delay in switchPanel handler.

## Agents Panel Timing Issue (QA False Negative)

The initial QA test flagged Agents as "stuck loading" but this was a test timing issue. The panel needs ~5 seconds to load 77 agents (36,919 bytes from /api/agents). With 5s wait: 539 DOM rows, full grid renders, no loading state.

## Key Selectors for Future Tests

- Commands nav: `[data-panel="commands"]` (clickable one is DIV.nav-item, rect ~430,8, 133x36)
- Shortcuts nav: `[data-panel="shortcuts"]` (similar location, 468,8)
- Settings button: `#settings-btn` (top bar, ~1289px, 30x27)
- Voice overlay: `#hmiVoiceOverlay` (display:none until triggered, NOT a nav panel)
- Neural canvas: `#hmiCanvas` (main neural canvas in chat panel)
- HMI canvas (voice overlay): Also `#hmiCanvas` — same ID reused!

## switchPanel is NOT on window

`window.switchPanel` is undefined. The function lives inside the main IIFE. For Playwright:
- Use `element.click()` (via `page.evaluate("el.click()")`) not `window.switchPanel()`
- All panels clickable via their rect-sized nav-item elements

## Mobile Layout Confirmed

375px: No overflow. Bottom nav (Chat/Terminal/Earn/Saved/More). Dark background. Chat messages visible. File attachment icon + mic icon + Task + Send buttons all in input row. Clean experience.

## Settings Modal Architecture

Settings opens from `#settings-btn` (gear icon in top bar). Contains:
- Quick Fire Pills (editable shortcuts)
- BOOP on Cadence (interval config)
- The Rubber Duck (problem articulation feature)

ElevenLabs API key is in the Voice overlay (`#hmiElGearBtn`), NOT in main Settings modal.

## API Health at Time of Test

- /api/commands: 200, 570 bytes
- /api/shortcuts: 200, 3,342 bytes
- /api/agents: 200, 36,919 bytes
- Zero network failures across entire session

## Verification

Report: `/home/jared/projects/AI-CIV/aether/exports/PORTAL-QA-REPORT-2026-03-17.md`
Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-20260317/` (23 files)
