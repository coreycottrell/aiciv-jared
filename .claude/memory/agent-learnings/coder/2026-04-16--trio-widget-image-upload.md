# Trio Widget Image Upload Implementation

**Date**: 2026-04-16
**Agent**: coder
**Task**: Add image drag-drop, paste, and inline rendering to Trio widget

---

## What Was Implemented

Added 3 image features to the Trio widget on both portal and 777:

### 1. Drag-and-Drop
- `.tw-feed` area becomes drop zone on dragover
- Visual overlay with blue dashed border + "📷 Drop image here" text
- Accepts image files, uploads to `social.purebrain.ai/api/uploads`
- Shows pending preview after upload

### 2. Paste-to-Chat (Ctrl+V / Cmd+V)
- Paste event listener on `#tw-input` textarea
- Detects clipboard image items
- Uploads image, shows preview below input
- Normal text paste behavior preserved

### 3. Inline Image Rendering
- Messages with `media_refs` array render inline images
- Images: `<img class="tw-msg-img">` (max 300px height, rounded, click opens full-size)
- Files: `<a class="tw-file-link">📎 filename</a>`
- Integrates with existing message rendering

---

## Technical Details

### Upload Endpoint
```
POST https://social.purebrain.ai/api/uploads
- Content-Type: multipart/form-data
- Field: 'file'
- Auth: Bearer token (portal_token for portal, baas_session_token for 777)
- Max: 10MB
- Returns: { key, url, mime, size, original_name, uploaded_at }
```

### Integration with Message Sending
- Pending media stored in `TRIO_WIDGET.pendingMedia`
- On send: include `media_refs: [pendingMedia]` in POST body
- Clear pending after successful send
- Preview shows thumbnail (60px) with filename and size, removable with X

### Files Modified

**Portal**: `/home/jared/purebrain_portal/portal-pb-styled.html`
**777**: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html`

**Markers used**:
- `<!-- BEGIN: trio-image-upload -->` / `<!-- END: trio-image-upload -->` (3 sections: JS, CSS, HTML)

---

## Key Code Patterns

### Upload Function
```javascript
async function twUploadFile(file){
  if (file.size > 10 * 1024 * 1024) throw new Error('File too large (max 10MB)');
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch('https://social.purebrain.ai/api/uploads', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + twToken() },
    body: formData
  });
  // ...
}
```

### Render Media
```javascript
function twRenderMedia(message){
  if (!message.media_refs || !Array.isArray(message.media_refs)) return '';
  return message.media_refs.map(media => {
    if (media.mime.startsWith('image/')) {
      return `<img src="${media.url}" class="tw-msg-img" onclick="window.open(this.src,'_blank')" />`;
    } else {
      return `<a href="${media.url}" class="tw-file-link">📎 ${media.original_name}</a>`;
    }
  }).join('');
}
```

### Drag-Drop Setup
```javascript
feed.addEventListener('drop', async (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (!file.type.startsWith('image/')) { alert('Only images'); return; }
  const media = await twUploadFile(file);
  twShowPendingMedia(media);
});
```

---

## CSS Highlights

### Drop Zone Overlay
```css
.tw-feed.tw-drop-zone-active::before{
  content:'📷 Drop image here';
  position:absolute; inset:0;
  background:rgba(42,147,193,0.12);
  border:3px dashed #2a93c1;
  /* centered text */
}
```

### Pending Preview
```css
.tw-pending-preview{
  display:none; /* shown when media pending */
  gap:8px; padding:8px 12px;
  background:rgba(42,147,193,0.08);
  /* thumbnail + info + remove button */
}
```

### Inline Images
```css
.tw-msg-img{
  max-width:100%; max-height:300px;
  border-radius:8px; margin-top:8px;
  cursor:pointer; /* click to open full-size */
}
```

---

## Deployment

**Portal**: `sudo systemctl restart aether-portal.service` ✅
**777**: `CF_PAGES_PROJECT=777-command-center python3 tools/cf-deploy.py --base-dir exports/cf-pages-deploy/777-command-center/ index.html` ✅

---

## Testing Checklist

- [ ] Drag image onto feed → uploads and shows preview
- [ ] Paste image into textarea → uploads and shows preview
- [ ] Send message with pending image → includes in message
- [ ] Received messages with images → render inline
- [ ] Click inline image → opens full-size in new tab
- [ ] File (non-image) → shows download link
- [ ] Remove pending preview (X button) → clears
- [ ] 10MB limit enforced → shows error

---

## CORS Status

**IMPORTANT**: Upload endpoint is on `social.purebrain.ai` (different origin from `portal.purebrain.ai` and `777.purebrain.ai`).

**Expected**: CORS should allow these origins (Chy's Worker should have CORS headers).

**If blocked**: Add portal and 777 domains to Worker's CORS allowlist, OR proxy through portal/777 endpoints.

**Not tested yet** - will need real test to confirm CORS works.

---

## Future Enhancements

1. **Multiple images** - currently only supports 1 pending image at a time
2. **Image compression** - client-side resize before upload for large images
3. **Progress indicator** - show upload progress bar for large files
4. **Preview gallery** - show all images in message as gallery/carousel
5. **Voice messages** - extend pattern to audio files

---

## Gotchas

1. **Different auth tokens**: Portal uses `portal_token`, 777 uses `baas_session_token`
2. **Different send endpoints**: Portal proxies to `/trio/message`, 777 uses `SHEETS_API/trio/message`
3. **Must initialize on widget open**: `twSetupDragDrop()` and `twSetupPaste()` called in `openTrioWidget()` with 200ms delay
4. **Media must be in message body**: Added `mediaHtml` to message rendering, not separate container

---

## Memory-First Protocol Applied

- Searched: `.claude/memory/agent-learnings/coder/` for "image upload portal trio widget"
- Found: No prior work on this exact feature
- Applied: Fresh implementation based on specs
- Documented: This memory for future reference

---

**Type**: Implementation pattern
**Topic**: Trio widget image upload/paste/render
**Files**: portal-pb-styled.html, 777/index.html
**Complexity**: Medium (upload, preview, render, 3 UX patterns)
