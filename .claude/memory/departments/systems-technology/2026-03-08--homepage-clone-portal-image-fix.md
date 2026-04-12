# 2026-03-08: Homepage Clone + Portal Image Preview Fix

## Task 1: Homepage Clone to Pay-Test Pages

### Architecture Discovery
- Homepage (ID:11), pay-test-2 (ID:689), pay-test-sandbox-3 (ID:1232) all use `elementor_canvas` template
- Pages store content in `meta._elementor_data` (NOT `post_content`)
- elementor_data = JSON array of 4 containers; container[0].elements[0].settings.html = the full page HTML
- All pages have identical HTML structure with 26 scripts

### Key Differences Between Pages
- **Script 23** (PayPal SDK): Contains `PAYPAL_CLIENT_ID`
  - Homepage + Sandbox-3: AYTFob... (LIVE PayPal)
  - Pay-test-2: AWgWNlBQ... (SANDBOX PayPal)
- **Script 25** (Integration Glue): 
  - Homepage: Form-based waitlist (openWaitlistModal + form rating buttons)
  - Pay-test-2 + Sandbox-3: Post-payment chat flow (checkForPaymentReturn)
- CTA buttons: Homepage uses `openWaitlistModal(...)`, pay-test pages use `openPayPalModal(...)` (aliased to same function)

### Deployment Approach
1. Fetch homepage elementor_data JSON (497KB)
2. Extract HTML from `data[0].elements[0].settings.html`
3. Replace script 23 with test page's version (preserves PayPal client ID)
4. Replace script 25 with test page's version (enables post-payment chat flow)
5. Build new elementor_data with merged HTML
6. POST to WP REST API: `PATCH /wp-json/wp/v2/pages/{id}` with `meta._elementor_data` + `template: elementor_canvas`
7. DELETE `/wp-json/elementor/v1/cache` to clear Elementor cache

### Credentials
- WP REST API: `PUREBRAIN_WP_USER` + `PUREBRAIN_WP_APP_PASSWORD` from `.env`

## Task 2: Portal Image Preview Fix

### Bug Discovery
Portal `renderAiFileCards()` correctly renders inline image `<img>` tags when:
- `ext` is an image extension (png/jpg/gif/etc)
- `serverPath` is set
- `isPortalUpload: true`

But `[PORTAL_FILE:storedName:originalName]` format was only handled in `addMessage()`, NOT in:
1. `startStreamingMessage()` → `renderChunk()` final render (line ~5966)
2. In-place update path in `chatWs.onmessage` (line ~6352)

Messages from `portal_send_file.sh` come through as role=`assistant`, which triggers `startStreamingMessage`, bypassing the PORTAL_FILE handler in `addMessage`.

### Fix Applied
Added PORTAL_FILE handler in two locations in `/home/jared/purebrain_portal/portal-pb-styled.html`:
1. After streaming complete in `renderChunk()` - uses IIFE to avoid var conflicts
2. After in-place update in `chatWs.onmessage`

Both handlers call `renderAiFileCards([pfFile], div)` where `pfFile.isPortalUpload = true` and `pfFile.serverPath = '/api/chat/uploads/' + encodeURIComponent(storedName)`.

### Pipeline Verification
- `tg_send.sh --photo` and `--file` both call `portal_send_file.sh` (dual delivery)
- `portal_send_file.sh` writes `[PORTAL_FILE:storedName:originalName]` to JSONL
- Portal server broadcasts via WebSocket → portal HTML handles via PORTAL_FILE pattern
- Upload files served at `/api/chat/uploads/{filename}` via `api_chat_serve_upload()`
- `FileResponse` handles correct MIME types for images automatically

### parseAiFiles Mode 3 Bug (Do Not Fix - Low Priority)
`parseAiFiles` Mode 3 pattern `[(?:FILE|PORTAL_FILE):\s*([^\]]+\.ext)\s*]` would partially match
`[PORTAL_FILE:storedName:originalName]` but capture `storedName:originalName` as the path (wrong).
The dedicated PORTAL_FILE handler is the correct code path and supersedes Mode 3 for this format.
