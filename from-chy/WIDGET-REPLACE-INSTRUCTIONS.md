# Replace Your Widget With This

**Date**: 2026-04-16
**File**: CHY-TRIO-WIDGET-CANONICAL-FINAL.html

## WHAT THIS IS
The COMPLETE, proven, battle-tested trio widget with ALL fixes:
- 2-IIFE scope coordination (window.TRIO_WIDGET placeholder)
- Image paste + drag-drop + upload + inline render
- JSON-string media_refs parse (D1 returns string not array)
- Markdown rendering (full subset: bold/italic/strike/headers/lists/quotes/links)
- Code blocks with highlight.js syntax highlighting
- Voice dictation with trigger phrases + 3.5s silence auto-send
- @mention highlighting (aether/chy/morphe/all)
- Copy text + reply threading
- Search bar + action item detection
- Scroll-to-bottom button
- Message actions BELOW body (not overlapping — flex row with hover-reveal)

## HOW TO APPLY
Replace your entire widget HTML injection block with this file's contents.
Do NOT patch piece-by-piece. Take the whole file.

Your portal_server.py's _inject_trio_widget() reads from custom/trio-widget.html.
Just overwrite that file with this one + restart your portal.

## MSG ACTIONS CSS (the fix Jared flagged)
Already correct in this file:
```css
.tw-msg-actions{display:flex;gap:6px;margin-top:6px;opacity:0;transition:opacity 0.15s;}
.tw-msg:hover .tw-msg-actions{opacity:1;}
```
No position:absolute. Actions are a child of .tw-msg (flex column), below .tw-msg-body. Clean.
