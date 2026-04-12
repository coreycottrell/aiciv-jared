# dept-systems-technology: Portal MVP v1.1.0 — Git Push and Flux Package Delivery

**Date**: 2026-03-20
**Type**: operational
**Topic**: Full portal packaging — git push to GitHub + Flux deployment package via AgentMail

---

## What Was Done

### Git Push to coreycottrell/purebrain-portal

Pushed Portal MVP v1.1.0 commit `be512c4` to `git@github-interciv:coreycottrell/purebrain-portal.git`.

Files staged and committed:
- `.gitignore` — expanded with new exclusion patterns
- `admin-referrals.html` — updated referral admin
- `aether-infrastructure/api-server/purebrain_log_server.py` — API server updates
- `portal-pb-styled.html` — full light mode + all v1.1.0 features
- `portal_owner.example.json` — updated template
- `portal_server.py` — security fixes, multi-tenant, upload dedup
- `light-mode-bg-prototype.html` — new file (prototype reference)
- `migrate_agents_departments.py` — new file (migration utility)
- `paypal_sync_subscriptions.py` — new file (sync utility)

### .gitignore Expansion

Added exclusions for:
- `portal_owner.json` (personal data)
- `investor_config.json` (sensitive prompts/contacts)
- `bookmarks.json` (runtime data)
- `*.bak.*`, `*.bak_*` (backup variations not covered by old pattern)
- `*.task*-backup-*`, `*.mvp-backup-*` (additional backup patterns)
- `release_notes.json.local`, `run_portal_patch.sh`

Previous .gitignore had `*.bak` and `*.bak-*` but missed `.bak.`, `.bak_`, `.task5-backup-`, `.mvp-backup-` patterns.

### Flux Package

Created clean deployment tarball using `git ls-files` to copy only tracked files.
Added deployment-specific empty runtime files and .env.example + FLUX-DEPLOY-README.md.
Tarball: `/tmp/purebrain-portal-mvp-v1.1.0.tar.gz` (1.2MB, 62 files)

### AgentMail Delivery

FROM: aethergottaeat@agentmail.to
TO: flux.civ@agentmail.to
CC: jared@puretechnology.nyc
Message ID: 0100019d0ccf4520-b4f3ab5e-79eb-490f-be51-50f061db48aa-000000@email.amazonses.com

---

## Key Patterns

### Use git ls-files for clean packages

```bash
git ls-files | while IFS= read -r f; do
    dir=$(dirname "/tmp/dest/$f")
    mkdir -p "$dir"
    cp "$f" "/tmp/dest/$f"
done
```

### .gitignore backup patterns are tricky

Portal generates backups with many patterns. Need all of:
- `*.bak`, `*.bak-*`, `*.bak.*`, `*.bak_*`, `*.task*-backup-*`, `*.mvp-backup-*`

### SSH remote format

Always use `git@github-interciv:coreycottrell/{repo}.git` for Corey's repos.
