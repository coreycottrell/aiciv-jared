# Portal Task 5: Multi-Terminal Tab System

**Date**: 2026-03-05
**Type**: teaching
**Topic**: portal.purebrain.ai multi-terminal WebSocket tab architecture

---

## What Was Built

Added a full multi-terminal tab system to `/home/jared/purebrain_portal/portal-pb-styled.html` via patch script at `/home/jared/purebrain_portal/apply_task5_multi_terminal.py`.

## Architecture Decisions

### Session Registry Pattern
Instead of a single `termWs` variable, introduced `termSessions` object:
```js
termSessions: { [tid]: { ws, reconnectTimer, paneEl } }
```
Each tab (tid) has its own independent WebSocket connection, reconnect timer, and DOM pane element.

### Backward Compatibility via `Object.defineProperty`
The existing codebase used `termWs` in several places (boot, switchPanel). Rather than hunting every reference, used `Object.defineProperty` to make `termWs` a computed property that mirrors the active tab's ws. Zero breaking changes.

### Pane Architecture (hide/show not destroy)
Terminal content persists when switching tabs. Each pane is a `.term-pane` div:
- Created lazily by `getOrCreatePane(tid)` on first connect
- Hidden/shown via CSS class toggle (`.term-pane.active { display: flex }`)
- First pane (`#term-pane-1`) is static HTML; subsequent panes created by JS

### Tab Bar HTML Structure
```
.term-tab-bar > .term-tab[data-tid=N] > .term-tab-label + .term-tab-close
.term-tab-bar > .term-tab-add (+ button)
```
- Single-tab mode: `.term-tab-bar.single-tab` hides close buttons via CSS
- Max 4 tabs: `MAX_TERM_TABS = 4`; "+" button gets `.hidden` class at limit

### CSS Placement
Multi-terminal CSS injected immediately after `@keyframes blink-cur` block — after existing terminal output pseudo-element styles, before `.term-input-bar`. Keeps the terminal section visually grouped.

## Patch Script Pattern (apply_task5_multi_terminal.py)

5 targeted `str.replace()` patches:

| Patch | What | Anchor |
|-------|------|--------|
| 1 | CSS styles | After `@keyframes blink-cur` closing brace |
| 2 | Panel HTML | `<!-- Terminal panel -->` block |
| 3 | Terminal JS | `// ===== TERMINAL WEBSOCKET =====` block |
| 4 | switchPanel check | `if (panel === 'terminal' && !termWs)` line |
| 5 | boot() init | `connectTerminalWS(); connectChatWS();` pair |

10 post-patch sanity checks before writing. Auto-backup with timestamp before any write.

## Key Gotcha: Python String Escaping vs HTML Content

The portal file contains literal JS unicode escapes like `\u25CF` (stored as backslash-u-2-5-C-F in the file). In Python `OLD_TERMINAL_JS` strings, these must be `'\\u25CF'` (double backslash) so Python produces the literal two characters `\u` rather than the Unicode character ●.

Similarly, JS regex `/\s+$/` in the HTML file requires `\\s+$` in Python strings.

## Feature Spec Delivered

- Tab bar: `#0e1015` bg, tabs `#141820`, blue (`var(--gold)`) bottom border when active
- "+" button: circular, gold border, hidden at max 4 tabs
- Double-click tab label to rename (contenteditable)
- "x" close button (hidden on single tab)
- Each tab: independent WebSocket to `/ws/terminal?token=TOKEN`
- Active tab reflects connection status in existing `#ws-status` badge
- Chrome title updates to active tab name

## Files

- Patch script: `/home/jared/purebrain_portal/apply_task5_multi_terminal.py`
- Portal: `/home/jared/purebrain_portal/portal-pb-styled.html` (run script to apply)
