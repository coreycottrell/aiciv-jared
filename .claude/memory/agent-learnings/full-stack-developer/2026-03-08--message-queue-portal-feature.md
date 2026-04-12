# Memory: Message Queue Feature — PureBrain Portal

**Date**: 2026-03-08
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Message queue UI implementation in single-file portal HTML app

---

## What Was Built

Added a message queue system to `/home/jared/purebrain_portal/portal-pb-styled.html` — a 9,000+ line single-file portal app with all CSS and JS inline.

## Key Implementation Details

### HTML Changes
- Added `<div class="queue-bar" id="queue-bar">` between `attach-preview-bar` and `chat-input-bar`
- Wrapped Send button in `<div class="chat-btn-stack">` alongside new `<button class="chat-queue-btn" id="queue-btn">`
- Queue bar contains: header (count badge + clear btn + expand toggle) + collapsible items list

### CSS (added before `</style>` at end of style block)
- `.chat-btn-stack` — flex column wrapper for Queue + Send buttons
- `.chat-queue-btn` — blue-outlined, transparent background (secondary action)
- `.queue-bar` — hidden by default, shown with `.active` class
- `.queue-item` — card per queued message with truncated preview + up/down/delete controls

### JS (added inside outer IIFE before `})();` + `</script>`)
- `msgQueue` array stores `{ text: string }` objects
- `renderQueue()` rebuilds DOM list and badge count
- `isAIThinking()` — checks for `[id^="thinking-"]` elements in DOM
- **MutationObserver** on `#chat-messages` watches for thinking indicator removal
- When thinking indicator removed AND queue has items: `startQueueWatcher()` → waits 1.5s → shifts first item → puts in textarea → calls `sendChat()`
- Queue watcher uses `setInterval` polling at 400ms as fallback
- Keyboard shortcut: `Ctrl+Enter` queues message

### Critical: Enter key guard
The existing keydown handler was: `if (e.key === 'Enter' && !e.shiftKey)`
Updated to: `if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.metaKey)`
Without this, `Ctrl+Enter` would both queue AND send the message.

## File Locations
- Source: `/home/jared/purebrain_portal/portal-pb-styled.html`
- Copied to: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/packages/purebrain-portal/portal-server/portal-pb-styled.html`
- Copied to: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/for-witness/portal-pb-styled.html`
- Service: `sudo systemctl restart aether-portal`

## Pattern: Large Single-File HTML Apps
- Add CSS immediately before `</style>` (end of style block)
- Add JS inside outer IIFE, before `})();` closing, before `</script>`
- The main JS block closes at a specific `</script>` — there are multiple script tags (Three.js, tooltip engine, etc.) — identify the right one by context
- `sendChat()` is declared inside the IIFE so it IS accessible from within the same IIFE scope
