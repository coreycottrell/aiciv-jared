# XSS Fix: company and role inputs sanitized in chatbox v4

**Date**: 2026-02-26
**Type**: teaching
**Topic**: XSS vulnerability patched in pay-test-script-chat-flow-v4.js

## What Was Fixed

File: `exports/pay-test-script-chat-flow-v4.js`

The `company` and `role` user inputs (Q3 and Q4 of the onboarding questionnaire) were being
interpolated directly into `aiSay()` template literals without sanitization. Since `aiSay()`
uses `bubble.innerHTML`, this was a stored XSS vector.

## The Pattern Applied

```javascript
// BEFORE (vulnerable):
const company = await promptText(...);
// company used directly in template literal → innerHTML

// AFTER (safe):
const rawCompany = await promptText(...);
const company = rawCompany ? sanitizeText(rawCompany) : null;
// company is now HTML-escaped before interpolation
```

Same pattern applied identically for `role`.

## Why This Pattern

- `sanitizeText()` already existed in the file (CRIT-004, added for aiName in v4.2)
- It uses `div.textContent = str; return div.innerHTML` — browser-native escaping
- It also enforces 60-char max to prevent UI overflow
- Null-safety: raw value is checked for truthiness before sanitizing

## What Was NOT Touched

- No other logic modified
- No deployment — fix is local only (per Jared: do not deploy tonight)
- File stays at `exports/pay-test-script-chat-flow-v4.js`
- Deploy tomorrow when Witness work resumes

## Lines Changed

- Line 1174-1175: company collection (rawCompany → sanitizeText)
- Line 1194-1195: role collection (rawRole → sanitizeText)

## Verification

Read lines 1172-1206 post-edit. Both variables use the raw/sanitized split pattern.
`sanitizeText()` confirmed present at line 1905.
