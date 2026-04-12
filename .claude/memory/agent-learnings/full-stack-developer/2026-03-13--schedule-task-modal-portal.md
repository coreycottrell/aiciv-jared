# Memory: Schedule Task Modal — PureBrain Portal

**Date**: 2026-03-13
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: Replacing Queue button with Schedule Task modal in single-file portal HTML app

---

## What Was Built

Redesigned the Queue button (`id="queue-btn"`) in `/home/jared/purebrain_portal/portal-pb-styled.html` to open a full "Schedule Task" modal instead of directly queueing messages.

## Key Changes Made

### Button label
- Changed button text from "Queue" to "Task"
- Updated tooltip to "Schedule a task — opens task scheduler"

### HTML Added (before `<!-- HMI Voice Overlay -->`)
- Full modal at `id="schedModalOverlay"` with class `sched-modal-overlay`
- Fields: Task Name, Task Prompt/Instructions, Assign to Brain (text input), Schedule (select), Priority (select), Advanced Options (collapsible)
- Schedule select drives conditional date/time pickers: once-row, daily-row, weekly-row
- Day-of-week chips for Weekly schedule
- Advanced panel: Retries, Timeout, Include Memories checkbox
- Footer: Cancel + Create Task buttons

### CSS Added (before `</style>`, after END MESSAGE QUEUE block)
- `.sched-modal-overlay` — fixed positioned dark overlay with backdrop-filter blur
- `.sched-modal` — centered card, max-width 540px, dark theme
- All field styles: `.sched-input`, `.sched-textarea`, `.sched-select`
- `.sched-day-chip` — pill buttons for weekday selection
- `.sched-advanced-panel` — collapsible via `.open` class
- Mobile: bottom sheet style on screens < 560px

### JS Added (new IIFE after END MESSAGE QUEUE, before outer `})()`)
- `window.openScheduleTaskModal = openModal` — exposes function globally
- Schedule select change → shows/hides date/time picker rows
- Day chip click → toggles `.active` class
- Advanced toggle → toggles `.open` on panel + rotates arrow
- Create Task: builds structured message format, injects into `#chat-input`, calls `sendChat()` after 80ms delay
- Close handlers: X button, Cancel button, click outside overlay, Escape key
- Form resets after each Create Task

### Message format sent to chat
```
[SCHEDULED TASK] {task_name}
Assign: {brain}
Priority: {priority}
Schedule: {schedule_label}
Retries: {retries}  (only if non-zero)
Timeout: {timeout}min
Include Memories: Yes  (only if checked)

{instructions}
```

### Queue JS changes
- Replaced `queueBtn.addEventListener` handler to call `openScheduleTaskModal()` instead of `queueMessage()`
- Replaced `Ctrl+Enter` handler same way
- Existing queue bar (`id="queue-bar"`) and queue functionality preserved — just not triggered from the button anymore

## Files Modified
- Source: `/home/jared/purebrain_portal/portal-pb-styled.html`
- Mirror 1: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/packages/purebrain-portal/portal-server/portal-pb-styled.html`
- Mirror 2: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/for-witness/portal-pb-styled.html`
- Service restarted: `sudo systemctl restart aether-portal`

## Pattern: Conditional UI in Single-File Portal
- Use `.visible` class toggling (not inline style) for show/hide — consistent with existing patterns (`.ctx-popup-overlay.visible`, `.hmi-voice-overlay.visible`)
- Expose functions globally via `window.funcName = fn` when cross-IIFE communication needed
- Add `setTimeout(fn, 80)` delay before `sendChat()` to let modal close animation complete
- Form reset logic belongs inside Create Task handler (after close), not in closeModal()

## Gotcha: sendChat is inside the outer IIFE scope
- `sendChat` is declared inside the main outer IIFE — accessible from inner IIFEs that are also inside it
- The schedule task modal IIFE is ALSO inside the outer IIFE, so `sendChat` is accessible directly
