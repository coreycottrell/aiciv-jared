# CF Worker Rollback — purebrain-portal-proxy (Phase 0 reversal)

**Date**: 2026-05-07
**Type**: operational
**Topic**: How to safely roll back a CF Worker without touching git main when the bad deploy was an uncommitted working-tree mod.

## Situation

Phase 0 security deploy (`a3f1da4a`) replaced hardcoded `purebrain-admin-2026` token with `env.ADMIN_TOKEN` and removed what looked like a duplicate routing block. Customer onboarding flow regressed afterwards. CEO greenlit rollback.

## Key insight

`wrangler deployments list` showed the deploy lineage, and the prior version was `d12a1a12` (2026-05-05). However, the safest rollback wasn't `wrangler rollback` to that version ID — it was restoring the working tree from `git show HEAD:...` since the deployed code was an **uncommitted modification on top of HEAD**. Working tree was dirty; HEAD already had the pre-Phase-0 source.

**Procedure that worked:**

```bash
# 1. Backup current (broken) source
cp workers/purebrain-portal-proxy/src/worker.js .backups/portal-proxy-rollback-2026-05-07/worker.js.current-a3f1da4a

# 2. Restore from HEAD (no git checkout — keeps index untouched)
git show HEAD:workers/purebrain-portal-proxy/src/worker.js > workers/purebrain-portal-proxy/src/worker.js

# 3. Deploy via wrangler (constitutional — never local-deploy, never wrangler pages for Workers)
export CLOUDFLARE_API_TOKEN=$(grep "^CF_API_TOKEN=" .env | cut -d'=' -f2)
cd workers/purebrain-portal-proxy && npx wrangler deploy
```

Resulting active version: `7e562dba-8220-4a6e-b77e-25f293ce45ac`.

## Forensic finding (more important than rollback itself)

**Pre- and post-rollback curl status codes were IDENTICAL** for all 6 onboarding-adjacent endpoints (`/api/log-conversation`, `/api/magic-link/...`, `/api/verify-payment`, `/api/send-seed`, `/partnered/`, `portal.purebrain.ai/admin/clients`). The proxy itself was not breaking onboarding. Phase 0 changes only affected `/api/admin/*` outbound headers; customer onboarding paths flow through different code branches that were untouched.

**Lesson**: Before assuming a deploy caused a regression, run the same curl matrix against the previous version. If statuses match, the breakage is upstream/downstream of what you changed. Don't roll back blind on hypothesis — measure the diff.

## What to remember next time

- `git show HEAD:path` is a clean way to restore a single file without `git checkout` polluting the index
- `wrangler deployments list --name <worker>` paginates oldest-first; tail it to see latest
- `wrangler rollback` exists but isn't always the right tool — sometimes the previous source isn't even what you want (e.g. uncommitted state)
- **Always capture the same baseline curl matrix BEFORE rollback** so you can compare. Saved me from declaring "rollback fixed it!" when in reality proxy was never the problem.
- A "Secret Change" deployment event (e.g. `eadae6eb` at 16:25) shows up as a separate deploy in the list — it's a metadata event, not a code change. The actual code-change deploys are the ones with `Source: Unknown (deployment)`.

## File paths
- Worker source: `workers/purebrain-portal-proxy/src/worker.js`
- wrangler.toml: `workers/purebrain-portal-proxy/wrangler.toml` (no `[[routes]]` block — route is registered at zone level)
- Backup of broken Phase 0 deploy: `.backups/portal-proxy-rollback-2026-05-07/worker.js.current-a3f1da4a`
- Receipt: `exports/portal-files/portal-proxy-rollback-receipt-2026-05-07.md`
