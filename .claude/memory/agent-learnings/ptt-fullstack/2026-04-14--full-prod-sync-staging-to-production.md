# Full Production Sync — Staging/Production Drift Closure

**Date**: 2026-04-14
**Type**: operational
**Topic**: Closing 947-file drift between local cf-pages-deploy and purebrain-production

## Context

Local `exports/cf-pages-deploy/` had 1082 files. Production `purebrain-production` had only 136 files. That meant ~88% of staged content (blog posts, images, avatar variants, 3d-training, voice-cache, wp-content media, etc.) existed locally but was 404 on prod. Earlier today narrow fixes had been deployed for /refer/, /your-ai-tim-cook/, /headshots/. Jared approved a full sync.

## Approach (works well — repeat for future drift closure)

1. **Inventory both sides**: `find ... > /tmp/local-cf-inventory.txt`, then call `cf-deploy.py --manifest` (or import `get_current_manifest`) to dump prod manifest.
2. **Set difference** in Python: prefix local relpaths with `/` to match manifest keys.
3. **Filter aggressively**:
   - PROTECTED: `/investment-opportunity/*` (CONSTITUTIONAL — never deploy without `--force-protected`)
   - Build cache: any `.wrangler/cache/*`
   - Root-level `*.py` (don't ship investor stress-test scripts to CDN)
4. **Batch by top-level dir** (4 batches of 100-400 files keeps requests sane). cf-deploy.py auto-buckets uploads at 100 files / 50 MB so any single batch is fine, but smaller batches make it easy to bisect failures.
5. **Single deployment per batch** (one merged manifest, one published deployment) — far better than per-file deploys.
6. **CF cache purge_everything** on the zone after final batch.
7. **Spot-check** with `curl -o /dev/null -w "%{http_code} %{content_type}"`.

## Key cf-deploy.py behavior to remember

- **Additive merge**: it pulls current manifest, merges new hashes, re-injects protected entries even if they were absent locally — safe by design.
- **Runtime guard**: tries to deploy to `investment-opportunity*` → script aborts with sys.exit(1).
- **Bucketing**: 100 files OR 50 MB per upload bucket, multiple buckets per deployment.
- **Use `CF_PAGES_PROJECT=purebrain-production` env var** to switch from default staging.

## Result

- 933 files deployed across 4 batches
- Prod file count: 136 → 1069
- 4 deployment IDs: 9df70286, 5007f3a1, f52a80bd, 6d48351e
- All spot-checks pass, protected path /investment-opportunity/ still 200
- Cache purged

## Gotchas

- `pre-deploy-sync.sh` is mandatory before any prod deploy (pulls Chy-owned dirs investor-avatar/investor-tracking/gifts so we don't overwrite her work). The script also rsyncs other shared blog dirs from Chy's machine.
- Don't use `wrangler pages deploy` (constitutional ban). Always cf-deploy.py.
- Mapfile pattern `mapfile -t paths < /tmp/batch.txt; cf-deploy.py "${paths[@]}"` handles 400-file argv cleanly on Linux (well under ARG_MAX).

## Files

- /home/jared/projects/AI-CIV/aether/tools/cf-deploy.py
- /home/jared/projects/AI-CIV/aether/tools/pre-deploy-sync.sh
- /tmp/prod-sync-gap.txt (947 lines, full gap)
- /tmp/prod-sync-gap-filtered.txt (933 lines, after exclusions)
- /tmp/batch-B{1..4}.txt
- /tmp/prod-sync-gap.txt.deploy-report
