# Atlas → Aether Naming Swap - PureBrain v8 Dashboard

**Date**: 2026-02-28
**Type**: gotcha
**File**: pure-brain-v8-with-dashboard.html

## What Happened

Task: Replace all "Atlas" with "Aether" in the PureBrain v8 dashboard HTML file.

## Finding

The file (13,223 lines, 798KB) already used "Aether" throughout almost the entire codebase.
Only ONE instance of "Atlas" existed - a JavaScript default fallback on line 5031:

```javascript
const aiName = urlParams.get('ai') || sessionStorage.getItem('pb_ai_name') || 'Atlas';
```

This was changed to:

```javascript
const aiName = urlParams.get('ai') || sessionStorage.getItem('pb_ai_name') || 'Aether';
```

## Why This Matters

- The `|| 'Atlas'` default would have shown "Atlas" as the AI name for any user who:
  - Did not pass `?ai=` URL param
  - Had no `pb_ai_name` in sessionStorage (i.e., new/unauthenticated users)
- All hardcoded HTML elements (ai-profile__name, chat-header__title, placeholder text) already said "Aether"
- The JS dynamic fallback was the only inconsistency

## Output File

Source: `docs/from-telegram/pure-brain-v8-with-dashboard.html`
Output: `exports/pure-brain-v8-aether-dashboard.html`

## Pattern

When doing name swap audits on large HTML files: the most dangerous instances are
in JavaScript default values / fallbacks, not visible HTML. Always grep for `'Name'`
and `"Name"` patterns in script blocks specifically.
