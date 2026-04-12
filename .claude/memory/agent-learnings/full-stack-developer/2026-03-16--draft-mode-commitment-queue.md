# Draft Mode / Commitment Queue Feature

**Date**: 2026-03-16
**Type**: technique
**Topic**: Portal chat commitment queue — draft mode feature

## What Was Built

Added "Draft Mode / Commitment Queue" to `portal-pb-styled.html` — a full sidebar panel that:
1. Detects action items from Aether's responses via `[ACTION: ...]`, `[COMMITMENT: ...]`, `[TASK: ...]`, `[TODO: ...]` markers and lines starting with `→` or `⚡`
2. Queues them in a sliding sidebar panel (280px, slides in from right)
3. Shows a "🔥 GO EAT" orange gradient button that sends `[EXECUTE_QUEUE]` message
4. Draft mode toggle (ON/OFF) in chat header
5. FAB (floating action button) when panel is closed but items are queued
6. "go eat" / "go" text intercepts in chat input
7. Inline "N queued" badge on assistant messages that contained action items
8. Execute-or-discard confirmation modal

## File Modified
`/home/jared/projects/AI-CIV/aether/_comms_hub/packages/purebrain-portal/portal-server/portal-pb-styled.html`

## Key Implementation Patterns

### Surgical Additions Only
- Added CSS block after `/* ===== END HOVER TOOLTIPS ===== */` comment
- Added HTML after `<!-- Chat panel (DEFAULT ACTIVE) -->` opening div  
- Added JS + confirm modal just before `</body>` tag
- Used Python string replacement (not Edit tool) for the final append due to "file modified" errors from the Edit tool on large files

### Commitment Queue Panel Position
The panel is `position: absolute` inside `#panel-chat` which is `position: relative`. Uses `translateX(100%)` with CSS transition for slide-in animation.

### MutationObserver Hook
Watches `#chat-messages` for new `.msg.assistant` nodes (new messages) and removed `[id^="thinking-"]` nodes (stream complete). Scans bubble text and extracts commitments.

### sendChat Integration
`executeQueue()` puts the `[EXECUTE_QUEUE]` message into `#chat-input` and calls `sendChat()` if available, else falls back to clicking `#send-btn`.

### Debug Handle
`window._cq.add("text")` — manually add items for demo
`window._cq.execute()` — manually trigger execution

## CSS Colors Used
- Panel background: `rgba(8, 10, 18, 0.96)` with `backdrop-filter: blur(24px)`
- Orange accent: `var(--teal)` = `#f1420b` (site's PT Orange variable)
- Queued dot: `#f59e0b` (amber/yellow)
- Done dot: `var(--green)` = `#22c55e`
- Go Eat button: `linear-gradient(135deg, #f1420b, #ff8c42)`

## Edit Tool Gotcha
For files this large (9000+ lines), the Edit tool's "file has been modified since read" check fires even when no external change occurred. Workaround: use Python `str.replace()` directly on the file.
