# Trio Widget Injection into Customer Portal (2026-04-15)

**Type**: teaching
**Topic**: Porting 777 Command Center widgets into portal-pb-styled.html

## Task
Inject 3-panel Trio chat widget from `exports/cf-pages-deploy/777-command-center/index.html` (lines 8800-9180) into `/home/jared/purebrain_portal/portal-pb-styled.html` as a pop-out overlay (not a separate page).

## Key Patterns

### 1. Proxy-route adaptation (BaaS → portal proxy)
777 widgets call `${SHEETS_API}/trio/messages` with `X-API-Key: WORKER_API_KEY` header.
Portal version must call same-origin `/trio/messages` with `Authorization: Bearer ${localStorage.portal_token}`.

- Portal routes defined at `/home/jared/purebrain_portal/custom/routes.py:121` (GET) and `:155` (POST)
- Auth check at `portal_server.py:1014` — requires `Authorization: Bearer` header, cookies alone NOT sufficient
- Portal token lives in `localStorage.portal_token` (set at line 8420 after login)

### 2. Portal proxy strips metadata
`/trio/message` POST only forwards `{content}` — sender derived server-side from `TRIO_TOKEN_*` env.
Browser cannot spoof `from` or `to`. Widget filter must treat empty `to` field as broadcast.

### 3. CSS scoping for huge files (19K+ lines)
portal-pb-styled.html is 805KB / 19K lines. To prevent class collisions, scope ALL selectors:
- Bad: `.tw-shell { ... }`
- Good: `#trio-widget-modal .tw-shell { ... }`

Everything goes inside `#trio-widget-modal` descendant selectors. Also `z-index:99999` to beat portal's agent hub and toast overlays.

### 4. Nav link conversion (external page → modal trigger)
```
FROM: <a href="/trio" target="_blank" ...>
TO:   <a href="javascript:void(0)" onclick="openTrioWidget()" ...>
```
No need for FAB button — nav link is cleaner.

### 5. IIFE wrapping + window.* exports
Wrap widget in IIFE to avoid polluting globals, but explicitly attach what HTML `onclick` handlers need:
`window.openTrioWidget`, `window.closeTrioWidget`, `window.trioSend`, `window.trioRefresh`, `window.TRIO_WIDGET`

## Process
1. `cp portal-pb-styled.html portal-pb-styled.html.bak-trio-widget-20260415`
2. Edit nav link (1 occurrence at line 6750)
3. Inject widget block before `</body>` (was at line 19157)
4. `sudo systemctl restart aether-portal.service`
5. Verify: `curl https://portal.purebrain.ai/` and grep for widget markers
6. Verify proxy: `curl /trio/messages?limit=1` → 401 (expected without auth)

## Gotchas
- Portal CSP allows inline `<script>` (line 110 in routes.py sets CSP) — no external file needed
- Hard refresh required — portal sends `Cache-Control` that can serve stale HTML
- `check_auth` does NOT accept cookies for `/trio/*` paths — must include Bearer header explicitly

## Files
- Edited: `/home/jared/purebrain_portal/portal-pb-styled.html` (+240 lines)
- Backup: `/home/jared/purebrain_portal/portal-pb-styled.html.bak-trio-widget-20260415`
- Source: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html` lines 8945-9180
- Proxy routes: `/home/jared/purebrain_portal/custom/routes.py:121, :155`
- Auth: `/home/jared/purebrain_portal/portal_server.py:1014`
