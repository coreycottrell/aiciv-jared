# Security Audit: Witness Portal Project (External Code)

**Date**: 2026-03-02
**Source**: Partner collective (Witness/Corey) via tarball
**Verdict**: WARN — Safe to deploy with 3 remediations required

## Key Findings

### CRITICAL (0)
None.

### HIGH (1)
- `Message.jsx:90-92` — `dangerouslySetInnerHTML` on user-controlled content
  - User messages rendered via `dangerouslySetInnerHTML` with only `/\n/` → `<br>` transform, NO HTML escaping
  - If Claude's response or session log contains `<script>` tags, they execute
  - Mitigation: encode HTML before `renderMarkdown()`, or use textContent for user messages

### MEDIUM (2)
- `ArtifactPanel.jsx:72` — iframe with `sandbox="allow-scripts allow-same-origin"`
  - allow-same-origin + allow-scripts together negates the sandbox: iframe content can access the parent's origin, read localStorage (which contains the portal bearer token), and exfiltrate it
  - Mitigation: Remove `allow-same-origin` OR set `srcdoc` to a data: URL

- `portal-pb-styled.html:964-970` + `portal.html:669-676` — status panel injects server-controlled values into `innerHTML` via `statCard()` string concatenation
  - `d.civ`, `d.tmux_session` values from the API response are injected directly into innerHTML without escaping
  - An attacker who can write to the server response (MITM or server compromise) could inject HTML
  - Mitigation: escape values before inserting, or use textContent for each StatCard field

### LOW (3)
- `portal_server.py:364` — Bearer token accepted in query string (`?token=`)
  - WebSocket auth uses `?token=` which appears in server logs and browser history
  - HTTP path also supports `?token=` as fallback
  - Mitigation: WebSocket auth via first-message handshake or Sec-WebSocket-Protocol header

- `AppContext.jsx:17` — Portal bearer token stored in `localStorage`
  - localStorage survives browser crashes, syncs across tabs, accessible to any same-origin JS
  - Combined with the allow-same-origin iframe finding = real extraction vector
  - Mitigation: Use sessionStorage OR memory-only state

- `portal_server.py:439` — `int(request.query_params.get("last", "100"))` without try/except
  - ValueError if non-numeric string passed. Starlette will 500. Not exploitable, but a nuisance DoS
  - Mitigation: Wrap in try/except with fallback

## Architecture Security Assessment
- All subprocess calls use list form (NOT shell=True) — no command injection possible
- Token generation uses `secrets.token_urlsafe(32)` — cryptographically secure
- Auth check function `check_auth()` is applied consistently to all protected endpoints
- No hardcoded credentials found anywhere
- No eval/exec/pickle/yaml.load anywhere
- All external network calls are relative-path only (same host) — no data exfiltration vectors
- No obfuscated code — Vite minification only, source maps would verify
- React app has no external CDN script loads

## Deployment Decision
SAFE TO DEPLOY after addressing HIGH finding (dangerouslySetInnerHTML).
MEDIUM findings are important but not blocking for initial internal-only deployment.

## Patterns for Future Partner Code Reviews
1. Always grep for `dangerouslySetInnerHTML` in React code — XSS through chat messages is a real attack
2. iframe `allow-scripts allow-same-origin` combination is a known sandbox escape
3. Token-in-querystring is a common low-severity leak pattern
4. Check statCard/template literals that inject server values into innerHTML without escaping
5. subprocess list-form calls with hardcoded command names (tmux, pgrep) are safe — no user input reaches shell
