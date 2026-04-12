# Portal File Preview Cards - Visual Verification

**Date**: 2026-03-08
**Agent**: browser-vision-tester
**Type**: technique

## Context

Verified that PureBrain portal (http://localhost:8097) shows file preview cards with CONTENT PREVIEWS inside the card — markdown/code text shown below filename, with a gradient fade and "Show more" toggle.

## Login Pattern

- URL: http://localhost:8097
- Input placeholder: "Bearer Token"
- Button class: `.pb-signin-btn` (text: "ACCESS YOUR AI'S BRAIN STREAM")
- Wait 4-5 seconds after login for chat history to load

## File Card Structure

Classes confirmed:
- `.ai-file-card` — outer container
- `.ai-file-card__name` — filename
- `.ai-file-card__size` — file size
- `.ai-file-card__preview` — content preview area (shows markdown/code text)
- `.ai-file-card__preview-fade` — gradient fade overlay at bottom
- `.ai-file-card__toggle` — "Show more / Show less" toggle button
- `.ai-file-card__icon` — file icon
- `.ai-file-card__cp` — copy button
- `.ai-file-card__dl` — download button

## What I Saw (Verified Working)

`portal-preview-proof.md` card showed:
```
# File Preview Feature — PROOF TEST

## What You Should See
1. This file card with a **content preview** below the filename
2. First 8 lines visible, with a gradient fade
3. "Show more" button to expand full content
4. Download button still works
5. Copy button still works
...
```
Toggle button shows: "▼ Show more"

## "Loading preview..." Pattern

Cards showing "Loading preview..." = files with 0 B size. This means the file content couldn't be retrieved from server. The preview container and toggle still render, but content is loading/unavailable.

## Screenshot Evidence

- `/tmp/portal-preview-proof-screenshot.png` — full chat view (1400x900)
- `/tmp/portal-file-card-zoomed.png` — cropped zoom of single working card
- `/tmp/portal-both-cards.png` — both cards + message context

## Playwright Selector Tips

- 186 total `.ai-file-card` elements exist (most in history, out of viewport)
- Filter to visible ones using `getBoundingClientRect()` in JS
- Scroll: `Array.from(document.querySelectorAll('*')).forEach(el => { if(el.scrollHeight > el.clientHeight + 10) el.scrollTop = el.scrollHeight; })`
- Use arrow function syntax in `page.evaluate()` — bare return statements throw SyntaxError

## When to Apply

Any time verifying portal file card feature, previews, or chat UI state on localhost:8097.
