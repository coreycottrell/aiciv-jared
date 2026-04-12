# Portal Task 2: AI File Send-Back — Architecture & Patch Decision
**Date**: 2026-03-05
**Type**: operational + teaching
**Agent**: cto

## Summary

Task 2 of the portal upgrade series: "When the AI sends files back in chat, they should appear as downloadable items."

## Architecture Decision: 100% Client-Side, No Server Changes

The server already handles everything needed for this feature. All logic lives in the HTML/JS single file.

### Why No Server Changes

- The AI response text is already the delivery mechanism
- Code blocks in markdown are already transmitted as plaintext
- A Blob URL approach requires zero round-trips to the server
- `URL.createObjectURL()` + `URL.revokeObjectURL()` handles memory cleanly

## Design: Two Detection Modes

### Mode 1: Fenced Code Block Auto-Extract
Any assistant message with a language-tagged code block (` ```python\ncode\n``` `) is parsed. The code is offered as a downloadable file (`code_1.py`). The inline `<pre><code>` rendering is preserved — the card is additive, not a replacement.

**Tradeoff considered**: Could strip code from display and only show card. Decided against — users still want to read code inline, the download is a convenience.

### Mode 2: Explicit [ATTACH:] Marker
For binary files (images, PDFs) where the AI embeds base64 data, a marker format:
```
[ATTACH: report.csv | base64data]
```
This strips cleanly from display text and renders as card only.

**Note for future**: The server-side AI would need to be prompted to use this syntax. The client parser is ready; the AI prompt engineering is a separate task.

## File Card UI Spec

- Container: `#141820` bg, `1px solid #2a93c1` border, `6px` radius
- Icon: SVG file icon, color-coded by type (blue=code, green=data, orange=image, red=pdf)
- Info: monospace filename + size in KB/MB
- Download button: `#2a93c1` background, hover darkens + scale(1.08), triggers Blob download
- Animation: `aiCardFadeIn` — 0.2s ease-out translateY(4px) -> 0

## Patch Script Pattern

5 patches total:
1. CSS block inserted before closing `</style>` tag (unique anchor with THREE.JS comment)
2-4. JS helpers block inserted before `renderMarkdown` function definition (unique comment anchor)
5. Hook in `addMessage()` — 4-line sequence anchor, unique in file

All anchors verified present and unique before writing patch.

## Key Lesson: Anchor Selection

The `</style>` anchor required surrounding context (the THREE.JS importmap comment) to be unique — the file has multiple `</style>` tags. Always include at least 2-3 lines of context when anchoring near common HTML.

## Files

- Patch script: `/home/jared/purebrain_portal/apply_task2_file_sendback.py`
- Target file: `/home/jared/purebrain_portal/portal-pb-styled.html`
- No server changes: `/home/jared/purebrain_portal/portal_server.py` unchanged
