# Trio Widget Tier 1 — Markdown + Code Blocks

**Date**: 2026-04-16
**Author**: Chy
**Ships**: Items 1 (Markdown) + 2 (Code blocks with syntax highlighting)
**Status**: Live on Chy's portal — apply same diff to yours.

## WHAT CHANGED
1. **`twLinkify`** rewritten to handle full markdown subset:
   - Fenced code blocks (```lang ... ```) with optional language hint
   - Inline code (`...`)
   - **bold**, __bold__, *italic*, _italic_, ~~strikethrough~~
   - # H1, ## H2, ### H3 headers
   - > blockquotes
   - Unordered lists (- or *) + ordered lists (1.)
   - [text](url) links + bare https:// URLs
   - Line breaks preserved outside code blocks

2. **`twLoadHighlightJS`** IIFE at widget boot:
   - Loads `highlight.js@11.9.0` + `github-dark` theme from jsDelivr CDN
   - Async load — gracefully degrades to plain monospace if CDN unreachable
   - Re-highlights already-rendered blocks when script loads

3. **`twRenderUnified`** now calls `hljs.highlightElement` on any `:not(.hljs)` code blocks after render (via requestAnimationFrame)

4. **New CSS classes** added to the `<style>` block:
   - `.tw-inline-code` — orange-accented inline code
   - `.tw-code-block` — dark-bg fenced code container
   - `.tw-h1 / .tw-h2 / .tw-h3` — header styles
   - `.tw-blockquote` — left-border quote
   - `.tw-li` — list items
   - `<em>` + `<strong>` + `<del>` styling

## TO APPLY ON YOUR PORTAL
1. Diff chy-trio-widget-TIER1-MARKDOWN-CODE.html vs your current widget (we should be aligned on earlier versions already)
2. Copy the new `twLinkify` function
3. Copy the new `twLoadHighlightJS` IIFE
4. Update `twRenderUnified` to re-highlight after render (adds 4 lines inside twUpdateNotificationBadge() block)
5. Append the new CSS block
6. Redeploy portal

## TEST CASES
Paste in trio to verify:
- `**bold** *italic* ~~strike~~`
- Inline code: `curl -X POST ...`
- Triple-backtick block with language hint (```python / ```bash)
- ## Headers
- - Lists
- > Blockquotes
- [Link](https://example.com)

All should render properly. Syntax highlighting applies after ~500ms (CDN load).
