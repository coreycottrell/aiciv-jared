# D1 Referral Migration — Phase 1 Blocker

**Date**: 2026-04-14
**Type**: operational
**Task**: Stand up `purebrain-referrals` D1 DB + schema + `trio_messages` table
**Status**: BLOCKED on CF token permissions

## What Worked
- `npx wrangler@latest` (v4.82.2) — no global install needed; user-scoped via npx cache works fine.
- `CF_API_TOKEN` from `.env` authenticates (`wrangler whoami` succeeds).
- Account resolved: **`d526a3e9498dd167509003004df03290`** (In0v8.admins@puretechnology.nyc's Account). NOTE: `.env` `CF_ACCOUNT_ID=19bb52a20bc7fc1b34036fea91f6860c` is DIFFERENT and appears stale/wrong — wrangler ignores it and uses the token's native account.

## What Failed
- `wrangler d1 list` → `code 10000 Authentication error` on `/accounts/{id}/d1/database`.
- Direct REST: `curl .../d1/database` also 10000. Token verify: active, but D1 scope missing.
- Tried `CF_API_TOKEN` ✓ auths but no D1 perm. `CF_PAGES_TOKEN` same error. `CF_MANAGEMENT_TOKEN` → 9109 invalid. `CF_API_KEY` is deprecated Global API Key form.

## Also Discovered
- `CF_API_KEY` env var triggers deprecation warning in wrangler even when overridden; harmless but noisy. Workaround: `env -i HOME=$HOME PATH=$PATH CLOUDFLARE_API_TOKEN=... npx wrangler ...`
- Two different CF accounts reachable from this box — `.env` mixes them. Worth auditing.

## Action Needed from Jared
Create a new CF API token (or edit existing `CF_API_TOKEN`) with these scopes on account `d526a3e9498dd167509003004df03290`:
- **Account → D1 → Edit**
- **Account → Workers Scripts → Edit** (for wrangler.toml binding later)
- **User → User Details → Read** (nice-to-have for clean whoami)

Then update `.env` → `CF_API_TOKEN=...` OR add `CF_D1_TOKEN=...`. Fix `CF_ACCOUNT_ID` to `d526a3e9498dd167509003004df03290` while at it.

## Files Referenced
- Migration SQL ready: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/d1-migrations/0001-referral-schema.sql`
- Pages Functions already code-complete against `env.REFERRAL_DB`: `exports/cf-pages-deploy/functions/api/referral/*.js`
- Setup doc: `exports/cf-pages-deploy/functions/api/referral/SETUP.md`
- `wrangler.toml` NOT yet created at `exports/cf-pages-deploy/wrangler.toml` (waiting on database_id)

## Prior Memory Cross-Refs
- `ptt-fullstack/2026-04-14--referral-d1-deprecated.md` — ptt also hit "no wrangler auth" on their box.
- `full-stack-developer/2026-03-12--sqlite-referral-system-portal-server.md` — confirms wrangler reads `CLOUDFLARE_API_TOKEN` not `CF_PAGES_TOKEN`.

## Next Session Resume
Once token has D1 Edit scope:
```bash
cd /home/jared/projects/AI-CIV/aether
export CLOUDFLARE_API_TOKEN=$(grep '^CF_API_TOKEN=' .env | cut -d= -f2 | tr -d '"')
export CLOUDFLARE_ACCOUNT_ID=d526a3e9498dd167509003004df03290
unset CF_API_KEY
npx wrangler d1 create purebrain-referrals   # capture database_id
npx wrangler d1 execute purebrain-referrals --file=exports/cf-pages-deploy/d1-migrations/0001-referral-schema.sql --remote
# Then create wrangler.toml + trio_messages table.
```
