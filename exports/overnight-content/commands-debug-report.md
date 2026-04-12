# Commands/Shortcuts Panel - Deep Browser Diagnosis Report

**Date**: 2026-03-17
**Agent**: browser-vision-tester
**Severity**: CRITICAL BUG - Root Cause Confirmed
**Status**: Fix Ready

---

## Executive Summary

The Commands and Shortcuts panels are stuck on "Loading..." because a **ReferenceError exception crashes `switchPanel()` before it can call `window.loadCommands` or `window.loadShortcuts`**.

The exception is: `ReferenceError: agentsInterval is not defined`

Everything else (the JS file, the APIs, the DOM structure) is working correctly.

---

## Diagnosis Findings

### Step 1: External JS Loads - PASS
- `typeof window.loadCommands` = `"function"` (confirmed in browser)
- `typeof window.loadShortcuts` = `"function"` (confirmed in browser)
- `typeof window._copyCmd` = `"function"` (confirmed in browser)
- `commands-shortcuts.js` network request: **HTTP 200** (loads successfully)
- Script tag present in DOM: `https://app.purebrain.ai/static/commands-shortcuts.js`

### Step 2: APIs Work - PASS
- `GET /api/commands` returns HTTP 200 with valid JSON (`server`, `paths`, `tmux`, `civ`, `owner`)
- `GET /api/shortcuts` returns HTTP 200 with 10 slash commands, keyboard shortcuts, features
- Auth headers sent correctly from `localStorage.getItem('portal_token')`

### Step 3: DOM Structure - PASS
- `#panel-commands` exists in DOM
- `#commands-content` exists inside it, initially contains "Loading command reference..."
- `#panel-shortcuts` exists in DOM
- `#shortcuts-content` exists inside it

### Step 4: Manual Call Works - CONFIRMED WORKING
Running `window.loadCommands()` manually in browser renders the full Commands panel correctly (screenshot attached). The panel shows Server Info, SSH Access, Status Checks, Log Files, Restarts, tmux Reference, Quick Reference Table, Troubleshooting - all populated with live server data.

### Step 5: Console Errors - THE SMOKING GUN

```
[PAGEERROR] agentsInterval is not defined
```

This error fires every time a nav item is clicked.

### Step 6: Root Cause - CONFIRMED

**The switchPanel function (line 7309) contains this code:**

```javascript
// Line 7334 - inside switchPanel IIFE (defined at ~line 6601)
if (panel === 'agents') { if (window.loadAgents) window.loadAgents(); if (!agentsInterval) agentsInterval = ... }
// Line 7335 - THIS LINE THROWS ReferenceError
if (panel !== 'agents' && agentsInterval) { clearInterval(agentsInterval); agentsInterval = null; }
// Line 7336 - NEVER EXECUTES due to exception above
if (panel === 'commands') { if (window.loadCommands) window.loadCommands(); }
// Line 7337 - NEVER EXECUTES due to exception above
if (panel === 'shortcuts') { if (window.loadShortcuts) window.loadShortcuts(); }
```

**`agentsInterval` is declared at line 15225 inside the Agents panel IIFE:**

```javascript
// Line 15225 - inside DIFFERENT IIFE
var agentsInterval = null;
```

These are **two separate IIFEs**. The `agentsInterval` variable in the agents IIFE is **invisible** to `switchPanel`'s IIFE. When `switchPanel` reaches line 7335 (`if (panel !== 'agents' && agentsInterval)`), JavaScript throws `ReferenceError: agentsInterval is not defined`.

This exception terminates `switchPanel` execution. Lines 7336-7337 (the `loadCommands`/`loadShortcuts` calls) are never reached.

### Step 7: Verification Chain

| Test | Result | Meaning |
|------|--------|---------|
| `typeof window.loadCommands` | `"function"` | JS file loaded fine |
| window.loadCommands spy read count after click | **0** | switchPanel never reads it |
| `getElementById('panel-commands')` trace | Called at line 7318 | switchPanel does run... |
| ...but then throws at line 7335 | `agentsInterval` not defined | ...and dies before 7336 |
| Manual execution of lines 7336-7337 logic | Works, content loads | Code is correct, just never reached |

---

## The Fix

**File**: `/home/jared/purebrain_portal/portal-pb-styled.html`

**Problem**: Lines 7334-7335 reference `agentsInterval` which is declared in a different IIFE scope.

**Fix Option A (Recommended): Make agentsInterval a window-level variable**

Change line 7335 from:
```javascript
if (panel !== 'agents' && agentsInterval) { clearInterval(agentsInterval); agentsInterval = null; }
```

To use `window.agentsInterval`:
```javascript
if (panel !== 'agents' && window.agentsInterval) { clearInterval(window.agentsInterval); window.agentsInterval = null; }
```

And update line 7334:
```javascript
if (panel === 'agents') { if (window.loadAgents) window.loadAgents(); if (!window.agentsInterval) window.agentsInterval = setInterval(function() { if (window.loadAgents) window.loadAgents(); }, 5000); }
```

And update line 15225 (in the agents IIFE):
```javascript
window.agentsInterval = window.agentsInterval || null;
// Remove: var agentsInterval = null;
```

**Fix Option B (Simpler): Add window.agentsInterval declaration at top of switchPanel's IIFE**

Add near line 6601 where `activePanel` is declared:
```javascript
var activePanel = 'chat';
var agentsInterval = null;  // ADD THIS LINE
var schedInterval = null;
var teamsInterval = null;
```

And remove the `var agentsInterval = null;` from the agents IIFE (line 15225), or keep it but make the agents IIFE use the outer variable (which is the point of Option B).

**Fastest Fix: Add a safety guard at line 7335**

Change line 7335 to:
```javascript
if (panel !== 'agents' && (typeof agentsInterval !== 'undefined') && agentsInterval) { clearInterval(agentsInterval); agentsInterval = null; }
```

This prevents the ReferenceError crash without restructuring scope.

---

## Secondary Issue: agentsInterval Scope

Even after fixing the crash, the `agentsInterval` management in `switchPanel` (lines 7334-7335) references a variable that can never be properly accessed. The Agents panel interval will:
1. Never be properly started via line 7334 (throws before this line is never reached... wait, line 7334 runs BEFORE 7335, so agents DO start. But since `agentsInterval` is not declared in this scope, the assignment `agentsInterval = setInterval(...)` will create a GLOBAL variable, not update the local one in the agents IIFE)
2. Never be properly cleared when switching away from Agents panel

This is a scope mismatch that should be cleaned up as part of the fix.

---

## Screenshots

| Screenshot | What It Shows |
|-----------|--------------|
| `/tmp/debug-03-commands-panel.png` | Commands panel stuck on "Loading command reference..." |
| `/tmp/debug-04-after-loadcommands.png` | Commands panel FULLY LOADED after manual `window.loadCommands()` call - proves the JS and API work |
| `/tmp/debug-05-shortcuts-panel.png` | Shortcuts panel stuck on "Loading shortcuts..." |

---

## What Works (Not the Problem)

- Static file serving at `/static/commands-shortcuts.js` - HTTP 200
- `window.loadCommands` function definition - correct
- `window.loadShortcuts` function definition - correct
- `/api/commands` endpoint - HTTP 200, returns full server config data
- `/api/shortcuts` endpoint - HTTP 200, returns all shortcuts data
- Token authentication for API calls - working
- Panel HTML structure (`#commands-content`, `#shortcuts-content`) - correct
- `switchPanel` detecting panel change (panel IS becoming active) - working

---

## What Is The Problem

`switchPanel` at line 7335 references `agentsInterval` which is **declared in a different IIFE** (line 15225). JavaScript throws `ReferenceError: agentsInterval is not defined`. This crashes `switchPanel` before it reaches lines 7336-7337 where `loadCommands`/`loadShortcuts` are called.

---

## Recommended Fix (Apply to portal-pb-styled.html)

**Three-line fix in the main IIFE scope (around line 6601):**

Find:
```javascript
  var activePanel = 'chat';
```

Change to:
```javascript
  var activePanel = 'chat';
  var agentsInterval = null;
  var schedInterval = null;
  var teamsInterval = null;
```

Then verify lines 7330-7335 use these local variables (they should reference `teamsInterval`, `schedInterval`, `agentsInterval` by name - which is fine once they're declared in the same scope).

Then remove (or comment out) the duplicate declarations in their respective IIFEs:
- Line 15225: `var agentsInterval = null;` (in agents IIFE)
- Any `var schedInterval` or `var teamsInterval` declarations in other IIFEs

---

## Memory Written
Path: `.claude/memory/agent-learnings/browser-vision-tester/2026-03-17--commands-shortcuts-agentsinterval-scope-crash.md`
Type: technique / gotcha
Topic: IIFE scope cross-contamination causing switchPanel crash before loadCommands
