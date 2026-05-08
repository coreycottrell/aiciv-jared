# Trio Portal — Option B — /trio Route Added to Aether Portal

**Date**: 2026-04-14
**Type**: operational + pattern
**Task**: Add `/trio` HTML view + proxy endpoints to portal_server.py, wired to `trio-comms` Worker backed by D1 `trio_messages`.

## What Worked

### 1. Customization layer instead of editing portal_server.py
- `portal_server.py` is 382KB / 9006 lines. Ended at `*_custom_routes` at line 8977.
- `custom/routes.py` is auto-loaded by portal shim — appended to the main `routes` list.
- Zero bytes changed in portal_server.py → zero risk to Morning Pulse race guards (lines 7438/7519/7570), referral flow, forgot-password flow, or chat WS.
- **Pattern**: Whenever portal changes are needed, write `custom/routes.py` first. Only touch `portal_server.py` if the customization shim can't reach the required hook.

### 2. Server-derives-identity architecture
- Worker secret `TRIO_TOKEN_AETHER` in CF; same plaintext in `/home/jared/purebrain_portal/.env`.
- Portal proxies POSTs to Worker with Bearer = TRIO_TOKEN_AETHER → Worker stamps `sender_id: "aether"` server-side.
- Browser NEVER sees trio token. Client cannot spoof sender.
- Chy's portal will use `TRIO_SENDER=chy` + `TRIO_TOKEN_CHY` for the same binary.

### 3. XSS protection via textContent, not innerHTML
- All message fields (`sender_id`, `timestamp`, `content`) rendered via `element.textContent = ...` in client JS.
- Sender CSS class allow-listed: `["aether","chy","morphe","jared"]` — unknown senders get no class.
- Template placeholders `__SENDER__` / `__PORTAL_TOKEN__` HTML-escape'd server-side before `.replace()`.

### 4. Security headers on every Trio response
- `X-Robots-Tag: noindex, nofollow`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, strict `Content-Security-Policy` (no external origins).

### 5. Token rotation without disturbing other senders
- Regenerated ONLY `TRIO_TOKEN_AETHER` via `wrangler secret put`; left JARED/CHY/MORPHE untouched.
- Next task (Chy portal wire-up) rotates only TRIO_TOKEN_CHY in the same atomic move.

## Files

### Created
- `/home/jared/purebrain_portal/custom/routes.py` — 3 routes: `GET /trio`, `GET /trio/messages`, `POST /trio/message`.

### Modified
- `/home/jared/purebrain_portal/.env` — appended TRIO_SENDER, TRIO_WORKER_URL, TRIO_TOKEN_AETHER.
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html` — added "Enter Trio" nav item after Trio Comms (line ~1511, opens `https://purebrain.ai/trio` in new tab).

### Backups
- `/home/jared/purebrain_portal/portal_server.py.bak-2026-04-14-trio` (untouched — precaution only)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html.bak-2026-04-14-trio`

## Verification Results

| Test | Expected | Got |
|------|----------|-----|
| `GET /trio` (no auth) | 401 + login HTML | 401 ✓ |
| `GET /trio` (auth)    | 200 + feed template | 200 ✓ |
| `GET /trio/messages` (no auth) | 401 | 401 ✓ |
| `GET /trio/messages` (auth)    | 200 + array | 200, 20+ msgs ✓ |
| `POST /trio/message` (no auth) | 401 | 401 ✓ |
| `POST /trio/message` (auth)    | 200, sender="aether" | 200, `{id, timestamp}` ✓, round-trip shows `sender_id: "aether"` |
| `GET /api/status` (regression) | 200 | 200 ✓ |
| `GET /api/chat/history` (regression) | 200 | 200 ✓ |
| `GET https://purebrain.ai/trio` (public) | 200 tunneled | 200 ✓ |
| 777 "Enter Trio" nav link | present | 1 match ✓ |

## Deploy IDs

- **Aether portal restart**: `sudo systemctl restart aether-portal.service` → active, 22:14:51 UTC.
- **777 Pages deploy**: `17524333-0527-4f29-994b-c7c56dc94c41` → https://purebrain.ai (prod).
- **Worker secret rotation**: TRIO_TOKEN_AETHER only. CHY/JARED/MORPHE untouched.

## Not Done (Pending Jared Direction)

1. **Chy portal (37.27.237.109:2213)** not modified — requires:
   - SSH into container, drop the same `custom/routes.py` (zero edits to portal_server.py),
   - rotate `TRIO_TOKEN_CHY` worker secret,
   - add `TRIO_SENDER=chy` + `TRIO_TOKEN_CHY` to Chy portal's `.env`,
   - restart Chy portal.
   - File the identical `custom/routes.py` works unchanged — it reads `TRIO_SENDER` from env.

2. **No migration of existing 777 Trio Comms panel** (sheets-based backend). That panel and the new `/trio` portal coexist — they write to different storage layers. Jared can deprecate the sheets panel later if desired.

## Gotchas

- `sudo systemctl restart aether-portal.service` takes ~6s to fully come up (SO_REUSEPORT fight + ExecStartPre fuser-kill + 2s sleep). Don't hammer curl during that window.
- The Worker's `ALLOWED_ORIGINS` list includes `https://purebrain.ai`; Cloudflare tunnel `/trio` → portal_server (8097) is already routed. No CF route change needed.
- `textContent` is XSS-safe for the message body but NOT for HTML injected via `.innerHTML` — never use innerHTML with message data.

## Cross-Refs

- `.claude/memory/agent-learnings/ptt-fullstack/2026-04-14--trio-comms-panel-built.md` — prior sheets-based panel (different backend, not this task).
- `.claude/memory/agent-learnings/devops-engineer/2026-04-14--d1-referral-migration-token-blocker.md` — where D1 `trio_messages` table was created.
- `/home/jared/projects/AI-CIV/aether/workers/trio-comms/src/worker.js` — Worker source, shows exact auth/rate-limit/schema.
