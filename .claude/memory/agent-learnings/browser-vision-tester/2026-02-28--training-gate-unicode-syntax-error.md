# Training Gate Password - Unicode Syntax Error Root Cause

**Date**: 2026-02-28
**Agent**: browser-vision-tester
**Type**: gotcha
**Topic**: Unicode box-drawing characters (U+2500) in JS comments crash entire script block

---

## Context

Testing purebrain.ai/training/ password gate. Password "brainiac2026" should work.
Console error: "Invalid or unexpected token"
Result: window.handleGateSubmit is undefined, gate button does nothing.

---

## Discovery

The training page's big script block contains Unicode box-drawing characters (U+2500 ─)
used as decorative comment separators:

```
/* ── FOUNDATIONS ── */
/* ─── Standard Video Card ─── */
/* ── CLIENT SPOTLIGHT MASTERCLASSES ── */
```

These `─` characters (U+2500) are non-ASCII. The WordPress plugin that serves the page
is NOT setting UTF-8 charset on the `<script>` tag, and/or the characters are being
interpreted as invalid tokens by the JS engine, crashing the ENTIRE script block at
the FIRST occurrence (line ~966 in the script, inside the TRAINING_VIDEOS array).

Because the script crashes at parse time, the IIFE boot function at the END:
```js
(function init() {
  window.handleGateSubmit = handleGateSubmit;
  // ...
})();
```
...NEVER runs. So handleGateSubmit is never assigned to window.

## Impact

- Gate form has onsubmit="return handleGateSubmit(event)"
- handleGateSubmit is not in window scope
- Clicking "Access Training Library" throws: "handleGateSubmit is not defined"
- Gate NEVER opens regardless of correct password

## Fix Required

Replace ALL Unicode box-drawing chars in JS comments with plain ASCII:
- `──` → `--` or `==`
- `─── X ───` → `--- X ---`

There are 24 occurrences across the script.

## Key Insight

WordPress often strips charset="utf-8" from inline script tags when using HTML
Elementor widgets. The browser may default to a narrower encoding or the minifier
may reject non-ASCII in script blocks. Rule: NEVER use Unicode decorative chars
in inline JavaScript served via WordPress. ASCII-only for JS.

## Password Confirmed

GATE_PASSWORD = "brainiac2026" is correct in the source.
SESSION_KEY = "pb_mastermind_auth"

## Selector Notes

- Gate form: #gate-form with onsubmit="return handleGateSubmit(event)"
- Password input: input[type='password'] with id="gate-pw"
- Submit button: button[type='submit'] (text: "Access Training Library") inside #gate-form
- Gate container: #pb-gate (display:flex when gated, none when authenticated)
- Library container: #pb-library (display:block when authenticated)

## Test Approach That Works

Use Playwright with wait_until="domcontentloaded" (not networkidle - page has streaming).
