# Migration Portal Quiz - WordPress && HTML Entity Encoding Bug

**Date**: 2026-02-25
**Type**: gotcha + teaching
**Page**: https://purebrain.ai/migrate/ (WP page ID 800)

## Root Cause: WordPress Converts && to &#038;&#038; in Rendered Script Output

WordPress's `the_content` filter pipeline (specifically `convert_chars()`) converts `&` to `&#038;` when rendering `<!-- wp:html -->` blocks. This means:

- **Stored in WP raw content**: `e.target.files && e.target.files[0]` (correct)
- **Rendered in browser**: `e.target.files &#038;&#038; e.target.files[0]` (BROKEN)
- **Result**: SyntaxError at first `&&` occurrence → entire IIFE fails → NO event listeners registered

The `&#038;` HTML entity is valid HTML but NOT valid JavaScript. When the browser encounters it inside a `<script>` tag, it causes a SyntaxError because `<script>` content is NOT processed for HTML entities.

## Symptom

Everything on the quiz appeared visually correct:
- Pills rendered
- CSS applied
- HTML structure intact
- Continue button visible

But **NOTHING was clickable** because the IIFE threw a SyntaxError before any `addEventListener()` calls ran.

## The Fix

Replace ALL `&&` operators in JavaScript with ternary operator equivalents that don't use the `&` character:

```javascript
// BEFORE (broken by WordPress):
var f = e.target.files && e.target.files[0];
if (a && b) { ... }

// AFTER (WordPress-safe):
var f = e.target.files ? e.target.files[0] : null;
if (a ? b : false) { ... }
```

For complex multi-level `&&`:
```javascript
// BEFORE:
if (userObj && userObj.chat_settings && userObj.chat_settings.custom_instructions)

// AFTER:
if (userObj ? (userObj.chat_settings ? userObj.chat_settings.custom_instructions : false) : false)
```

## Files Modified

- `/home/jared/projects/AI-CIV/aether/exports/migration-portal-v2-updated.html`
- Backup: `/home/jared/projects/AI-CIV/aether/exports/migration-portal-v2-updated.html.bak`
- Fixed version also saved as: `/home/jared/projects/AI-CIV/aether/exports/migration-portal-v2-fixed.html`

## Scope of Changes

23 occurrences of `&&` in the migration portal IIFE were replaced with ternary equivalents.
All in the **portal wizard section** (file upload, data parsing, step building) - NOT in the quiz section.
The quiz section had no `&&` operators which is why the quiz CSS/HTML rendered but the issue was the IIFE dying before reaching the quiz event listeners.

## Diagnosis Pattern

When a WordPress-embedded script COMPLETELY fails (nothing works) but the page renders fine:
1. Check rendered source for `&#038;` inside `<script>` tags
2. Extract the script and run `node --check script.js`
3. WordPress encodes `&` in HTML block content via `the_content` filter

## Prevention Rule

**NEVER use `&&` operators in JavaScript that will be deployed to WordPress via `<!-- wp:html -->` blocks.**

Always use ternary operators instead:
- `a && b` → `a ? b : a`
- `a && b && c` → `a ? (b ? c : false) : false`
- `if (a && b)` → `if (a ? b : false)`
- Null guards: `x && x.prop` → `x ? x.prop : null`

## Deployment Pattern

- Deploy via Python `requests.post` to `https://purebrain.ai/wp-json/wp/v2/pages/800`
- Verify: `curl https://purebrain.ai/migrate/` + check script has 0 occurrences of `&#038;` and `&&` in IIFE
- Also run `node --check` on extracted script to validate syntax before deploying

## Previous Related Bug

`2026-02-24--migration-portal-quiz-continue-fix.md`: `pointer-events: all` → `pointer-events: auto`
This was a different bug (invalid CSS value) but also caused silent failure of the Continue button.
