# CTO Memory: PureBrain Post-Payment Chatbox Revamp

**Date**: 2026-02-22
**Type**: operational
**Topic**: Architecture spec for chatbox revamp — Phase 1 completion

## Key Decisions Made

### Claude Auth Relocation
- Moved from Phase 4 (after Telegram setup) to Phase 1 (after Role question, before Primary Goal)
- Reason: Logically the user knows who they are after Role — AI linking to Claude is a natural next step
- All data fields preserved for logging compatibility (claudeMaxStatus, claudeSessionInfo, etc.)

### Thank-You Page Elimination
- `/thank-you/?name=&ai=` redirect is gone
- Content rendered as in-chat message via new `runThankYouMessage()` function
- Welcome button click triggers the function instead of `window.location.href`

### Portal Button Architecture
- Polling mechanism: `setInterval` every 30 seconds, max 60 polls (30 minutes)
- Endpoint needed (not yet built): `POST https://api.purebrain.ai/api/portal-status`
- Placeholder div `#ptc-portal-placeholder` replaced with live button when ready
- Must start BEFORE learn-more loop (concurrent, not sequential)

### Learn More Loop
- 5 questions about working style, biggest friction, 6-month vision, hidden context, personal success
- Skip option on every question (not shameful — visible "Skip →" button)
- All logged immediately per question with event `learn-more:{fieldName}`

### Behind-the-Curtain Visual Enhancement
- Emoji icons (zero dependencies, instant render, dark-bg friendly)
- `showSlide()` gets new `iconHtml` optional parameter — backward compatible
- `buildCurtainSlides()` returns `{content, icon}` objects instead of strings

## Code Files Involved
- Primary target: `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow.js`
- Integration glue (no changes): `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-integration-glue.js`
- Architecture spec: `/home/jared/projects/AI-CIV/aether/exports/chatbox-revamp-architecture-spec.md`

## WordPress Page IDs
- Sandbox: Page ID 688 (pay-test-sandbox-2) — deploy first
- Live: Page ID 689 (pay-test-2) — deploy after sandbox QA passes

## Risks to Watch
1. Portal API endpoint doesn't exist yet — developer needs to stub it
2. `runPortalButtonWatcher` must be called BEFORE `await runLearnMoreLoop` (concurrency)
3. JSON escaping on Elementor widget replace (newlines must be \\n, not literal)
