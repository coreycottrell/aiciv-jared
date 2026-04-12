# Portal Security Audit Fixes - 2026-03-20

**Type**: operational + teaching
**Topic**: 7 security fixes applied to portal-pb-styled.html and portal_server.py

## What Was Fixed

### H1: XSS via unescaped error messages (HIGH)
- 4 locations where e.message was inserted into innerHTML without escaping
- Lines 9695, 11341, 11390, 16798 in portal-pb-styled.html
- Fix: wrapped all with escHtml() (function already existed in the file)

### H2: Bearer token in WebSocket URL (HIGH)
- Both /ws/terminal and /ws/chat were passing ?token= in the URL query string
- Fix client: remove token from URL, send as first WS message on onopen
- Fix server: accept() first, then await first message with 5s timeout, check token, close 4401 on fail
- Updated check_auth() to remove /ws from query-param exception list

### M1: Unescaped directory names in file browser (MEDIUM)
- Line 11190: dd.name and dd.path inserted raw into innerHTML
- Fix: escHtml(dd.name) and escHtml(dd.path)

### M2: Content-Security-Policy headers (MEDIUM)
- Added to index() and index_pb() handlers in portal_server.py
- CSP allows: self, unsafe-inline, PayPal, ElevenLabs, fonts, wss:

### M3: ElevenLabs API key not cleared on logout (MEDIUM)
- Added localStorage.removeItem('elevenlabs_api_key') and 'elevenlabs_voice_id' to logout handler

### M4: Missing rel="noopener noreferrer" (MEDIUM)
- Added to download anchor at line 11210

## Files Changed
- /home/jared/purebrain_portal/portal-pb-styled.html
- /home/jared/purebrain_portal/portal_server.py

## Backups
- portal-pb-styled.html.bak-security-fixes-20260320
- portal_server.py.bak-security-fixes-20260320

## Verification
- Portal HTTP 200 after restart: confirmed
- CSP header present in HTTP response: confirmed

## Teaching: WebSocket Auth Pattern
Accept() first, then await first message { type: "auth", token: "..." } with timeout.
Close 4401 if auth fails. Keeps tokens out of URLs/logs/browser history.
