# V8 Dashboard Integration - pure-brain-v7 + dashboard-preview

**Date**: 2026-02-21
**Type**: technique
**Topic**: Integrating a standalone HTML section into a full SPA as an accessible panel

## What Was Built

Combined `/home/jared/projects/AI-CIV/aether/docs/from-telegram/pure-brain-v7.html` (746KB, 11356 lines) with `/home/jared/projects/AI-CIV/aether/docs/from-telegram/purebrain-dashboard-preview.html` (59KB, 1830 lines) into a single self-contained file at `/home/jared/projects/AI-CIV/aether/exports/pure-brain-v8-with-dashboard.html`.

## Integration Architecture

### Panel Overlay Pattern
The dashboard is embedded as a `position: absolute; inset: 0; z-index: 90` panel inside `.content-split` (which already had `position: relative` in v7's CSS for the project-overlay pattern). This is the same pattern v7 uses for project overlays, goal overlays, etc.

```css
.dashboard-panel {
    position: absolute;
    inset: 0;
    background: #080d14;
    z-index: 90;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
}
.dashboard-panel.visible {
    opacity: 1;
    pointer-events: auto;
}
```

### Navigation
Added "Command Center" nav item in Workspace section of sidebar (after History). Uses same pattern as other nav items with onclick handler.

```html
<a href="#" class="nav-item" id="dashboardNavItem" onclick="showDashboard(); return false;">
    <!-- dashboard icon SVG -->
    Command Center
</a>
```

### JS Functions Added
- `showDashboard()`: Sets nav active state, shows panel with `.visible` class, calls `initDashboard()`
- `initDashboard()`: One-time initialization - runs the dashboard IIFE animations on first show
- Updated `showChat()`: Hides dashboard panel when switching back to chat

### Lazy Initialization
The dashboard animations (IntersectionObserver for bars/counters, task timer interval) are deferred via `dashboardInited` flag. Only runs when the user first navigates to Command Center. This prevents wasted CPU on page load.

## CSS Namespacing
The dashboard uses `.dp-` prefix on all classes - zero conflicts with v7's classes. The only added CSS is:
1. The `.dashboard-panel` and `.dashboard-panel.visible` overlay classes
2. The full dashboard CSS block (already namespaced)

## Injection Points
1. **CSS**: Injected before the last `</style>` in `<head>`
2. **Nav item**: Injected after the History nav item in sidebar Workspace section
3. **Panel HTML**: Injected before the last `</div>` that closes `.content-split` (before `</main>`)
4. **JS functions**: Appended to the NAVIGATION section at bottom of script block

## Gotchas

1. **Don't use regex on `<html>` count**: v7 has multiple `<html>` strings inside JS template literals (artifact preview feature). Not a bug.

2. **content-split already had position: relative**: v7 uses project-overlay with `position: absolute` in the same container. No extra CSS needed.

3. **Dashboard script is an IIFE**: The original dashboard JS was wrapped in `(function() { 'use strict'; ... }())`. When embedding, we wrap the inner content in `initDashboard()` and call it lazily.

4. **Python string replace for JS**: When injecting JS that contains `'use strict'` as a string literal inside Python `replace()`, escape single quotes with `\'`.

## Files
- Output: `/home/jared/projects/AI-CIV/aether/exports/pure-brain-v8-with-dashboard.html`
- Size: ~797 KB
- Lines: ~13,223
- Single file, zero external JS dependencies, one Google Fonts URL
