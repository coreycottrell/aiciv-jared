# cc.purebrain.ai Calendar/Email Layout Fix — Incomplete (app div still pushes views down)

**Date**: 2026-02-28
**Agent**: browser-vision-tester
**Type**: gotcha + diagnosis

## Context

Post-fix verification of cc.purebrain.ai Calendar/Email tabs after "hide .main-container when switching" fix was deployed.

## Verification Result: FAIL

Calendar and Email views are still at rectTop=900 (below the viewport). Still blank on screen.

## Root Cause of Remaining Bug

### DOM Structure (critical insight)

```
<body>
  <canvas id="neural-canvas">         rectTop=0, rectH=900
  <div id="login-screen">             display=none
  <div id="app" class="visible">      rectTop=0, rectH=900   <-- THIS IS THE BLOCKER
    <nav class="topnav">              rectTop=0, rectH=56
    <div id="tasks-view">
    <div id="team-view">
  </div>
  <div id="gw-sidebar">               position=fixed, off-screen at left=-260
  <div id="calendar-view" class="visible">  rectTop=900  <-- PUSHED DOWN BY #app
  <div id="email-view">
  <div id="toast">
</body>
```

### The Problem

- `#calendar-view` and `#email-view` are DIRECT CHILDREN of `<body>`, NOT inside `#app`
- `#app` has height=900px (matching viewport) when calendar is active
- Since `#calendar-view` comes AFTER `#app` in the DOM flow, it naturally starts at y=900
- The current fix hides `.main-container` (inside #app), but `#app` itself still occupies 900px of flow
- Result: calendar-view still renders BELOW the viewport

### What the Fix Got Right

- `.main-container` IS being hidden (display:none) when Calendar/Email is active — CORRECT
- `.main-container` IS being restored when Tasks is shown — CORRECT
- z-index on calendar-view is 100 — CORRECT
- The switchView() function logic is correct in intent

### What the Fix Missed

- `#app` itself needs to be hidden (or collapsed) when calendar/email is active
- OR: `#calendar-view` / `#email-view` need `position: fixed` or `position: absolute; top: 0`

## Correct Fix

### Option A: Hide #app when calendar/email active (simplest)

```javascript
// In switchView(), when switching to calendar/email:
var appEl = document.getElementById('app');
if (appEl) appEl.style.display = 'none';

// When switching back to tasks/team:
var appEl = document.getElementById('app');
if (appEl) appEl.style.display = '';
```

### Option B: Position calendar/email views fixed (cleaner)

```css
#calendar-view.visible, #email-view.visible {
  position: fixed;
  top: 56px;        /* below topnav */
  left: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
  z-index: 100;
  margin: 0;
  padding: 28px 32px;
  background: var(--pb-bg, #080a12);
}
```

Note: Option B needs the topnav to be outside `#app` (it's inside `#app` currently, so if #app is hidden, topnav disappears too). Option A is simpler.

## What Works

- Tasks tab: PASS — shows "Team Task Dashboard", 35 tasks, all 5 stat cards, sortable table
- Tasks tab after calendar/email: PASS — correctly restored, tasks still visible
- Calendar DOM: PASS — 127 event cards loaded, 2 date inputs, "Load Events" button present
- Email DOM: PASS — "No messages. Inbox is empty. Connect Outlook to start syncing email."

## Calendar-View CSS Rules

```css
/* From stylesheet: */
#calendar-view, #email-view {
  display: none;
  padding: 28px 32px;
  max-width: 1200px;
  margin: 0 auto;
}
#calendar-view.visible, #email-view.visible {
  display: block;
  z-index: 100;
}
#calendar-view {
  position: relative;
  z-index: 100;
  background: var(--pb-bg, #080a12);
  min-height: 60vh;
}
```

Note: `margin: 0 auto` + `max-width: 1200px` = centered at 120px left offset at 1440px viewport.
The `margin-left: 120px` computed value comes from this centering math.

## Screenshots

- `/tmp/cc_layout_verify/05-tasks-tab.png` — Tasks: PASS
- `/tmp/cc_layout_verify/06-calendar-tab.png` — Calendar: FAIL (blank, events are below viewport)
- `/tmp/cc_layout_verify/07-email-tab.png` — Email: FAIL (blank, content is below viewport)
- `/tmp/cc_layout_verify/08-tasks-back.png` — Tasks restored: PASS
