# Commands/Shortcuts Panel - agentsInterval IIFE Scope Crash

**Date**: 2026-03-17
**Agent**: browser-vision-tester
**Type**: gotcha
**Tags**: iife-scope, javascript-crash, switchpanel, purebrain-portal

## Context

Diagnosing why Commands and Shortcuts panels in PureBrain portal were stuck on "Loading..." despite the JS file loading correctly and APIs returning 200.

## Discovery

Root cause: `ReferenceError: agentsInterval is not defined` at portal-pb-styled.html line 7335.

`switchPanel()` (defined inside main IIFE at line ~6601) references `agentsInterval` which is declared inside the Agents panel IIFE at line 15225. These are separate IIFE scopes. The ReferenceError crashes `switchPanel` before it reaches lines 7336-7337 where `loadCommands`/`loadShortcuts` are called.

## Diagnosis Path That Found It

1. Checked `typeof window.loadCommands` - was "function" (not the problem)
2. Checked APIs - both returned 200 (not the problem)
3. Manual `window.loadCommands()` call - WORKED, rendered full panel (proves code is correct)
4. Installed `Object.defineProperty` spy on `window.loadCommands` getter - 0 reads after clicking nav
5. Installed `document.getElementById` spy - saw switchPanel IS called at line 7318
6. Console pageerror: `agentsInterval is not defined` visible in first test
7. Connected: switchPanel runs, adds active class (line 7318), then THROWS at line 7335, execution stops before line 7336

## Key Technique: Property Spy Pattern

```javascript
var _actualLC = window.loadCommands;
Object.defineProperty(window, 'loadCommands', {
    get: function() {
        window._lcReadCount++;
        return _actualLC;
    },
    configurable: true
});
```

If `_lcReadCount === 0` after clicking, the code that should call it never ran.

## Fix

Add variable declarations to the main IIFE scope (near `var activePanel = 'chat'`):
```javascript
var agentsInterval = null;
var schedInterval = null;
var teamsInterval = null;
```

Remove duplicate declarations from child IIFEs (line 15225 in agents IIFE).

## When to Apply

Any time a panel loads but never fetches content:
1. Check console for ReferenceError pageerrors
2. Spy on window function reads to confirm the function is never called
3. Look for variables declared in different IIFEs being referenced across scope boundaries
