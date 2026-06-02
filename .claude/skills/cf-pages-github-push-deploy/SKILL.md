---
name: cf-pages-github-push-deploy
version: 1.0.0
author: aether
description: Canonical CF Pages deploy via git push to puretechnyc/purebrain-site
tags: [deploy, cloudflare, pages, git, production]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# CF Pages GitHub Push Deploy

The ONLY canonical deployment method for purebrain.ai CF Pages sites.

## The Rule (Constitutional)

ALL CF Pages deploys = git push to `puretechnyc/purebrain-site` main branch.

**BANNED FOREVER:**
- `cf-deploy.py`
- `wrangler pages deploy`
- Direct CF API uploads
- `CF_DEPLOY_FORCE_PROTECTED=1`

## Deploy Flow

```bash
cd /home/jared/projects/purebrain-site
git add <specific-files>
git commit -m "feat(section): description"
git push origin main
```

## Propagation

- CF Pages github:push takes **90-150s** to propagate
- Verification before 60s may show stale content
- Wait ≥120s OR poll CF API for commit hash match

## Verification

```bash
# Poll until new content is live
until curl -s "https://purebrain.ai/path/" | grep -q "expected-content"; do sleep 5; done
```

## Deploy Targets

| Target | Live URL |
|--------|----------|
| `purebrain-production` | purebrain.ai |
| `purebrain-staging` | staging preview |
| `purebrain-staging-new` | staging.purebrain.ai |
| `777-command-center` | 777.purebrain.ai |

## Anti-Patterns

### Anti-Pattern 1: Deploy Locally
- **BAD**: Running cf-deploy.py or wrangler pages deploy
- **GOOD**: Git push only

### Anti-Pattern 2: Trust PROTECTED_PATHS
- **BAD**: Assuming PROTECTED_PATHS prevents omissions
- **GOOD**: GET-probe every protected path after deploy to catch 404s

### Anti-Pattern 3: Using _redirects
- **BAD**: Creating `_redirects` files for CF Pages
- **GOOD**: Use meta-refresh HTML instead (CF Pages ignores _redirects)

### Anti-Pattern 4: Verify Too Soon
- **BAD**: Check after 30s, see stale content, think deploy failed
- **GOOD**: Wait ≥120s for propagation window

## Workers vs Pages

**Workers**: Use `wrangler deploy` (after git commit)
**Pages**: Use `git push` ONLY

## Dual-Source Warning

Files shared between:
- `aether/exports/cf-pages-deploy/`
- `puretechnyc/purebrain-site/`

**MUST** stay byte-identical. Check diffs before pushing.

## Protected Path Probe Pattern

```bash
# After deploy, verify every protected path
for path in /index.html /our-team/ /investment-opportunity/ /insiders/portal/ /gift/seed/ /gift/awakened/ /gift/partnered/; do
  echo "Checking $path..."
  curl -s "https://purebrain.ai$path" | head -50
done
```

## Constitutional Reference

Locked 2026-05-13 per `feedback_canonical_deploy_flow_2026_05_13.md`

---

**When in doubt: git push to puretechnyc/purebrain-site main. Nothing else.**
