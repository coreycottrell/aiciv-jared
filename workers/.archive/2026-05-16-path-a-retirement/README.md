# Path A Retirement — 2026-05-16

**Retired**: 2026-05-16
**Branch**: `retire/aether-workers-path-a-2026-05-16`
**Rollback tag**: `pre-workers-retirement-2026-05-16`

## Why

These 12 Worker source trees were aether-local mirrors of the canonical `puretechnyc/<worker-name>` repositories. They drifted significantly from the live deployed versions (the most extreme was `referrals-api` at -1185 commits behind canonical), violating the constitutional rule:

> **Git is the only source of truth.** Any production state not derivable from `git HEAD` of the canonical repo is a future-incident waiting to fire. (locked 2026-05-11)

Maintaining two source trees per worker created a chronic drift class — every `wrangler deploy` from the aether-local copy risked rolling back live production by hundreds of commits. Per the 2026-05-13 canonical deploy flow lock, Workers ship via `git commit → wrangler deploy` from their canonical `puretechnyc/<worker>` repositories only. The aether-local copies are no longer the source of truth.

## What was retired

12 worker directories, each formerly at `aether/workers/<name>/`:

1. `admin-api`
2. `paypal-webhook`
3. `purebrain-portal-proxy`
4. `referrals-api`
5. `trio-comms`
6. `777-sheets-api`
7. `agentmail-webhook`
8. `ara-index`
9. `blog-publisher`
10. `blog-publish-hook`
11. `meetings-api`
12. `welcome-email-api`

## What was NOT retired (held)

- `aether/workers/social-api/` — Chy's domain; pending her TRIO reply before retirement
- `aether/workers/ce-sme-api/` — no canonical `puretechnyc` twin yet; pending Chy confirmation
- `aether/workers/_shared-migrations/` — shared infra (not a mirror); retained

## Recovery path

Source code is preserved here (never deleted), but the canonical recovery path is:

```bash
# To recover a worker's source, clone from its canonical repo:
git clone git@github-interciv:coreycottrell/<worker-name>.git
# e.g., git clone git@github-interciv:coreycottrell/admin-api.git
```

## Rollback (this retirement only)

If this retirement itself needs reversing:

```bash
cd /home/jared/projects/AI-CIV/aether
git checkout main
git reset --hard pre-workers-retirement-2026-05-16
```

## Constitutional references

- 2026-05-11: "Git is the only source of truth" lock
- 2026-05-13: Canonical deploy flow lock — workers via `git commit → wrangler deploy` from canonical repos only
- Recon source: `/home/jared/exports/portal-files/aether-workers-retirement-inventory-2026-05-16.md`
