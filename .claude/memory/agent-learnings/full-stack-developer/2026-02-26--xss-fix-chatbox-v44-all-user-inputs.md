# XSS Fix: All user inputs sanitized in purebrain-chatbox-v44.html

**Date**: 2026-02-26
**Type**: teaching
**Topic**: HIGH severity XSS — 4 unsanitized user inputs patched in chatbox v44

## What Was Fixed

File: `exports/purebrain-chatbox-v44.html`

The `aiSay()` function renders its text argument via `bubble.innerHTML = text.replace(/\n/g, '<br>')`.
Four user-supplied values were being interpolated raw into `aiSay()` template literals, creating
a reflected/stored XSS vector in the post-payment chatbox questionnaire.

## The 4 Vulnerabilities Patched

| Line | Variable | Where |
|------|----------|--------|
| 9419 | `firstName` (from name input) | "Nice to meet you, ${firstName}" |
| 9444 | `company` | "Got it — ${company}. ..." |
| 9465 | `role` | "${role} — that context is going to..." |
| 9497-9498 | `goal` + `firstName` again | Quote echo + confirmation message |

## Pattern Applied (Inline Sanitization)

Instead of sanitizing at collection time (which would truncate stored raw values),
`sanitizeText()` is applied inline at the point of HTML interpolation only:

```javascript
// BEFORE (vulnerable):
await aiSay(msgList, `Got it \u2014 ${company}. ${aiName} will keep that context in mind.`);

// AFTER (safe):
await aiSay(msgList, `Got it \u2014 ${sanitizeText(company)}. ${aiName} will keep that context in mind.`);
```

This preserves the raw value in `payTestData` (for API calls, logging, Google Forms submission)
while escaping only the HTML rendering path.

## Why userSay() Was NOT Changed

`userSay()` correctly uses `bubble.textContent = text` (not innerHTML), so it was
already safe. No changes needed there.

## sanitizeText() Definition (line 10167)

```javascript
function sanitizeText(str) {
  const d = document.createElement('div');
  d.textContent = typeof str === 'string' ? str.slice(0, 60) : '';
  return d.innerHTML; // returns HTML-escaped string safe for innerHTML
}
```

Browser-native HTML escaping + 60-char overflow protection.

## Lines Changed

- Line 9419: `firstName` → `sanitizeText(firstName)`
- Line 9444: `${company}` → `${sanitizeText(company)}`
- Line 9465: `${role}` → `${sanitizeText(role)}`
- Line 9497: `"${goal...}"` → `&ldquo;${sanitizeText(goal...)}...&rdquo;`
- Line 9498: `${firstName}` → `${sanitizeText(firstName)}`

## What Was NOT Changed

- No deployment (Jared instructed: local fix only)
- payTestData.company and payTestData.role store raw unsanitized values (correct — used for API/logging)
- waitlist form company/role (lines 6751-6752) — uses formData.append(), not innerHTML, safe
- userSay() calls — already uses textContent, safe

## Verification

`grep -n "sanitizeText" exports/purebrain-chatbox-v44.html` confirms 6 call sites:
lines 9419, 9444, 9465, 9497, 9498 (new) + 10177, 10178, 10394, 10512 (pre-existing).
