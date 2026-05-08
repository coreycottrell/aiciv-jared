# Phase 0 Portal-Proxy Admin Token Rotation — 2026-05-07

**Type**: operational + teaching
**Topic**: How to rotate a leaked CF Worker admin token without downtime when downstream HTML still uses the old value

---

## What was wrong

`workers/purebrain-portal-proxy/src/worker.js` had `proxyHeaders.set('X-Admin-Token', 'purebrain-admin-2026')` hardcoded on lines 183 AND 196. Lines 192-205 were a **duplicate dead block** — same `if` condition as 179-191. Code drift from a copy-paste that was never cleaned up. Token committed to git → permanently leaked.

## How rotation works when downstream HTML still ships the old token

The KEY insight: `referrals-api` validates against `env.ADMIN_TOKENS` (plural, **CSV**). This means rotation can be staged:

1. Add NEW token to `ADMIN_TOKENS` CSV (alongside old) — both work
2. Bind NEW token as `ADMIN_TOKEN` (singular) on the proxy
3. Deploy proxy with `env.ADMIN_TOKEN` read
4. (later, after admin HTML migration) Remove old token from `ADMIN_TOKENS`

Without the CSV grace period, ANY admin HTML that hardcodes the old value would 401-break the moment the proxy stops sending old. CSV = zero-downtime rotation.

**Generalization**: any time you find a hardcoded shared secret used by BOTH a server-side proxy AND client-side pages, the rotation path is:
- Step 1: make validator accept BOTH old and new
- Step 2: cut over server-side caller to new
- Step 3: separately migrate clients off old (different ticket)
- Step 4: remove old from validator

## Workflow gotchas hit this session

1. **Wrangler not on PATH** — solved with `npx wrangler` (auto-installs to npx cache).
2. **`CLOUDFLARE_API_TOKEN` env var required** for non-interactive wrangler — read from `.env` (`CF_API_TOKEN`).
3. **Working tree blocked checkout main from referral-v1** because referral-v1 had untracked files that `main` would overwrite. Solution: `git worktree add /tmp/aether-main-security main` — creates a separate working dir at the target ref without disturbing current cwd. Cleanup with `git worktree remove`.
4. **Stash with untracked files** — stash refuses pathspecs for untracked files. `git add` first, then stash by path.
5. **Linter modified file mid-edit** causing line numbers to shift — Edit tool errors with "file modified since read". Solution: re-read, then re-Edit with current content.

## Verification commands that proved the fix

```bash
# Pre-fix
grep -n "purebrain-admin-2026" workers/purebrain-portal-proxy/src/worker.js
# 183:        proxyHeaders.set('X-Admin-Token', 'purebrain-admin-2026');
# 196:        proxyHeaders.set('X-Admin-Token', 'purebrain-admin-2026');

# Post-fix
grep -n "purebrain-admin-2026" workers/purebrain-portal-proxy/src/worker.js
# 189:      // env.ADMIN_TOKEN secret. Previously hardcoded literal `purebrain-admin-2026`
# (only in audit-trail comment, not code)

# Live proof (GET, per cf-pages-health-check-get-not-head)
curl -s -o /dev/null -w "%{http_code}" https://portal.purebrain.ai/api/admin/stats  # 200
curl -s -o /dev/null -w "%{http_code}" -H "X-Admin-Token: bogus" https://referrals-api.in0v8.workers.dev/admin/stats  # 401
```

## Files

- Receipt: `exports/portal-files/phase0-portal-proxy-security-fix-2026-05-07.md`
- Commit: `1fe0a3e` on `main` (NOT pushed — awaiting Jared)
- Token doc: `tools/.secrets/portal-proxy-admin-token-2026-05-07.txt` (gitignored, mode 600)
- Worker source: `workers/purebrain-portal-proxy/src/worker.js`
- Worker config (newly committed to main): `workers/purebrain-portal-proxy/wrangler.toml`
- Deploy version: `a3f1da4a-f747-43a9-af01-114aeb32d24a`

## Open downstream work (not in this fix)

Three admin HTML pages and one rebranded portal HTML still hardcode the old token — they continue to work because of the CSV grace period. ST# already has these in queue per `2026-05-07-security-posture-boop.md`.

Once those are migrated, the OLD token can be removed from `ADMIN_TOKENS` to complete the mitigation.
