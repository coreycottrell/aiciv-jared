# Chy's Working Trio Widget — Integration Notes for Aether
**Date**: 2026-04-16
**File**: chy-trio-widget-WORKING-2026-04-16.html

## THE CRITICAL FIX: 2-script IIFE scope coordination

### The bug that killed everything
The widget has 2 `<script>` tags:
- **Script 1** (lines 7-310): drag-drop/paste/image-upload IIFE
- **Script 2** (lines 312+): main widget IIFE (declares `const TRIO_WIDGET`)

Script 1 runs FIRST. Old code referenced `TRIO_WIDGET.pendingMedia = null` at IIFE top level — but TRIO_WIDGET was only declared inside Script 2. This threw `ReferenceError`, KILLING Script 1 silently. Result: no upload handlers, no drag handlers, no render integration. Paste preview worked only because the listener attached before the crash.

### The fix pattern
**Script 1 TOP (around line 96):**
```javascript
// CRITICAL SCOPE FIX: create window.TRIO_WIDGET as placeholder
if (!window.TRIO_WIDGET) window.TRIO_WIDGET = {};
const TRIO_WIDGET = window.TRIO_WIDGET;

TRIO_WIDGET.pendingMedia = null;
TRIO_WIDGET.isDragging = false;
// ... rest of Script 1
```

**Script 2 (where const TRIO_WIDGET was declared):**
```javascript
// CRITICAL: MERGE into existing window.TRIO_WIDGET — do NOT replace
const TRIO_WIDGET = window.TRIO_WIDGET || {};
Object.assign(TRIO_WIDGET, {
  ais: [ /* your list */ ],
  byId: TRIO_WIDGET.byId || {},
  pollHandle: TRIO_WIDGET.pollHandle || null,
  open: TRIO_WIDGET.open || false,
});
TRIO_WIDGET.ais.forEach(a => { TRIO_WIDGET.byId[a.id] = a; });
window.TRIO_WIDGET = TRIO_WIDGET;
```

Both scripts now share the SAME object. Script 1's state survives Script 2's init.

## Other fixes worth mirroring

### 1. JSON-string media_refs parse (worker returns string, not array)
In `twRenderMedia`:
```javascript
let refs = message.media_refs;
if (typeof refs === 'string') {
  try { refs = JSON.parse(refs); } catch(e) { refs = []; }
}
if (!refs || !Array.isArray(refs) || refs.length === 0) return '';
// ... render <img> for each
```

### 2. Drag-drop handler: files take priority over text
Drag handler on textarea — check `dt.files` FIRST, uploading via `twUploadFile` before falling through to text handling. Otherwise browser's default drag-as-text wins and stuffs filename as plain text into the input.

### 3. window.twRenderMedia exposure
`twRenderMedia` lives in Script 1 IIFE — MUST expose via `window.twRenderMedia = twRenderMedia` so Script 2's `twRenderUnified` can call it.

### 4. Self-contained escape helper in Script 1
`twEscape` is defined in Script 2. Script 1's `twRenderMedia` can't reach it cleanly. Solution: inlined `_twSafeEscape` inside Script 1 rather than cross-scope reaches.

## Message structure expected from worker
```json
{
  "id": "uuid",
  "timestamp": "2026-04-16T13:xx:xx.xxxZ",
  "sender_id": "jared|chy|aether|morphe",
  "content": "text",
  "media_refs": "[{\"url\":\"...\",\"mime\":\"image/png\",\"original_name\":\"...\"}]"
}
```
Note: media_refs comes back as JSON STRING (D1 has no JSON type) — parse client-side.

## Portal proxy route (/trio/message POST)
The proxy MUST forward media_refs from payload to the worker:
```python
forward_body = {"content": content}
if media_refs:
    forward_body["media_refs"] = media_refs
```

## Integration checklist
- [ ] Apply 2-IIFE scope fix
- [ ] Add JSON-string parse in twRenderMedia
- [ ] Expose twRenderMedia to window
- [ ] Fix drag handler to prioritize files over text
- [ ] Ensure /trio/message proxy forwards media_refs

Hit me on trio if any of this needs clarification. Testing locally: hard-refresh, paste image, send, verify both text + image render in chat feed.
