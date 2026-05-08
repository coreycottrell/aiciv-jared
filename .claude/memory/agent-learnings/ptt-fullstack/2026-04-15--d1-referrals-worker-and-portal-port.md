# D1 Referrals Worker + portal_server.py Port (2026-04-15)

**Type**: operational + teaching
**Topic**: Replace SQLite referral reads with D1 HTTPS facade behind env flag
**Companion task**: Trio nav link in portal-pb-styled.html sidebar

## What shipped

### Task 1: Trio nav link
- Added `<a href="/trio" target="_blank">` to `/home/jared/purebrain_portal/portal-pb-styled.html` between "777 Command Center" and "Brainiac Training" nav rows (matched the external-link pattern).
- Backup: `portal-pb-styled.html.bak-2026-04-15-trio-nav` (802 KB)
- Verified: rendered HTML contains 1 `href="/trio"` instance, live portal serves it 200.

### Task 2: Referrals API Worker + portal D1 client
- **Worker**: `/home/jared/projects/AI-CIV/aether/workers/referrals-api/` (wrangler.toml + src/worker.js)
- **Deploy URL**: https://referrals-api.in0v8.workers.dev
- **Version ID**: `e3e5fd84-50f7-4717-a356-bee58a3223ce`
- **D1 binding**: `purebrain-referrals` (`cdd9a522-f947-42a6-b9a3-c30534e02c3f`)
- **Endpoints**: `/health`, `/referrers`, `/referrals`, `/commission_payments`, `/dashboard`, `/admin/affiliates`
- **Auth**: admin endpoints need `X-Admin-Token` matching `ADMIN_TOKENS` secret (comma-separated allowlist)
- **Python client**: `/home/jared/purebrain_portal/referrals_d1_client.py` — async httpx wrapper, 30s TTL cache
- **Portal wiring**: `api_referral_dashboard` (line 4086) and `api_admin_affiliates` (line 5134) get a flag-gated D1 short-circuit with SQLite fallback on `D1ClientError`.
- **Flag**: `USE_D1_REFERRALS=false` in `/home/jared/purebrain_portal/.env` (default OFF).

## Patterns to reuse

### 1. `wrangler secret put` trailing-newline gotcha
`echo "$TOK" | wrangler secret put X` appends `\n`. Use `printf "%s" "$TOK" | wrangler secret put X` — otherwise allowlist string comparison fails because the stored secret has a trailing newline not in the caller's header.

### 2. CF token permission scope
Of the four CF tokens in `/home/jared/projects/AI-CIV/aether/.env`:
- `CF_PAGES_TOKEN` — Pages deploys only (Workers deploy → 10000 auth error)
- `CF_MANAGEMENT_TOKEN` — invalid / wrong scope (9109)
- `CF_API_TOKEN` — **THE ONE** for Workers deploy + secret put (works)
Always try CF_API_TOKEN first for Worker operations.

### 3. First-call 1104 race
New Worker deploys return CF error 1104 ("not deployed to this colo yet") for ~1-2s after `Deployed` message. Retry loop with 2s backoff, 5 attempts max.

### 4. D1 prepared statement binding
`env.DB.prepare(SQL).bind(val).all()` for SELECT → `{ results: [...] }` shape. `.first()` for single row → direct object. `COUNT(*)` returns column named literal `c` when aliased `AS c`; in the JSON this maps to `row.c`.

### 5. In-process parity harness (safer than second instance)
Rather than spawn a second portal_server.py on :8099 (which would collide on JSONL writes, session tokens, Morning Pulse race guards), import the module, force `USE_D1_REFERRALS=true` in `os.environ`, build a `FakeRequest` with valid Bearer, and `await api_referral_dashboard(req)`. Diff the JSON against a live `curl` of the SQLite path. Saved at `/tmp/d1_parity_test.py` for re-use.

## Parity Results (JAREDSB0)

| Field            | SQLite (live :8097) | D1 (worker)    | Match |
|------------------|---------------------|----------------|-------|
| referral_code    | JAREDSB0            | JAREDSB0       | ✓     |
| name             | MJ S                | MJ S           | ✓     |
| email            | jared@puretech...   | jared@puretech | ✓     |
| paypal_email     | support@purem...    | support@purem  | ✓     |
| total_referrals  | 10                  | 10             | ✓     |
| completed        | 10                  | 10             | ✓     |
| pending          | 0                   | 0              | ✓     |
| history rows     | 10                  | 10             | ✓     |
| earnings         | $70.78              | **$48.38**     | ✗     |
| total_clicks     | 43                  | **55**         | ✗     |

## The divergences are NOT port bugs

- **clicks**: D1 got the 303-row merged union (local 216 + chy 87, deduped). Expected per migration memo.
- **earnings**: local SQLite rewards table = $70.78. D1 rewards table (chy-preferred merge) = $48.38. Jared's spec said target = $61.51 (today's corrections). Neither store matches $61.51.
- **This is a data-reconciliation problem, not a code problem.** The worker returns exactly what D1 contains. SQLite fallback returns exactly what local contains.

## Flag state (ready for Primary)

```bash
# /home/jared/purebrain_portal/.env
USE_D1_REFERRALS=false           # ← flip to true for cutover
D1_API_URL=https://referrals-api.in0v8.workers.dev
D1_API_ADMIN_TOKEN=<43-char urlsafe token, matches worker secret>
```

To cutover: set `USE_D1_REFERRALS=true` in `.env`, `sudo systemctl restart aether-portal.service`. Response will include `"_source":"d1"` to confirm. To roll back: set back to `false`, restart. On transient D1 error, the code auto-falls back to SQLite and logs `[d1-port] ... fell back to SQLite`.

**Blocker for Primary before flip**: reconcile $48.38 (D1) vs $61.51 (expected). Otherwise users see $48.38 after cutover and it looks like missing revenue.

## Files

### Created
- `/home/jared/projects/AI-CIV/aether/workers/referrals-api/wrangler.toml`
- `/home/jared/projects/AI-CIV/aether/workers/referrals-api/src/worker.js`
- `/home/jared/purebrain_portal/referrals_d1_client.py`
- `/tmp/d1_parity_test.py` (kept for future parity runs)

### Modified
- `/home/jared/purebrain_portal/portal-pb-styled.html` (Trio nav anchor, 3 lines added)
- `/home/jared/purebrain_portal/portal_server.py` (import + 2 flag-gated short-circuits, ~50 lines)
- `/home/jared/purebrain_portal/.env` (3 new D1 vars at tail)

### Backups
- `/home/jared/purebrain_portal/portal-pb-styled.html.bak-2026-04-15-trio-nav`
- `/home/jared/purebrain_portal/portal_server.py.bak-2026-04-15-d1-port`

## Gotchas for next session

1. `wrangler secret put` reads stdin verbatim — always `printf "%s"` not `echo`.
2. `referrals_d1_client.py` must be importable from portal's CWD; it lives next to `portal_server.py` which is already the working dir per systemd unit.
3. Worker is currently PUBLIC on the open internet. Before true cutover, add a CF WAF rule restricting origin IP to the VPS, OR switch to `Authorization: Bearer` on ALL endpoints (not just /admin). Currently adequate for staging.
4. The 30s cache in `referrals_d1_client.py` is process-local dict. After a production cutover, admins expect refresh latency <30s on corrections — either reduce TTL or expose `invalidate_cache()` via an admin route.
