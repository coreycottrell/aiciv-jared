# Deprecated Tooling — 2026-05-16

## Why these scripts are here

These scripts directly edited / deployed `workers/social-api/` in the aether
repo. As of 2026-05-16, **social-api is solely Chy's domain in
`puretechnyc/social-api`** (constitutional ownership per Chy TRIO approval
2026-05-16). The aether mirror at `workers/social-api/` was archived in the
same commit set to
`workers/.archive/2026-05-16-path-a-retirement/social-api/`.

Running any of these scripts against the aether tree now would either:
- target a path that no longer exists (`workers/social-api/`), or
- attempt a `wrangler deploy` that would race with Chy's canonical deploys
  from `puretechnyc/social-api`, violating the "git is the only source of
  truth" constitutional rule.

## Scripts archived here

| Script | Original purpose |
|--------|------------------|
| `fix_social.sh` | Edited `workers/social-api/src/worker.js` |
| `fix_social_complete.py` | Edited + `cd workers/social-api` operations |
| `apply_r2_proxy_patches.py` | R2 proxy migration patches for social-api |
| `migrate_r2_to_proxy.py` | R2-to-proxy migration helper |
| `deploy-social-frontend.sh` | Embedded `cd workers/social-api && wrangler deploy` |

## Inventory note

The 2026-05-16 retirement BOOP referenced "6 scripts" but the canonical
inventory at
`/home/jared/exports/portal-files/aether-workers-retirement-inventory-2026-05-16.md`
lists only the 5 above as having direct social-api impact. A sixth file,
`tools/cf-worker-deploy.py`, is mentioned in the inventory only because its
docstring uses 777-sheets-api as an example — it does NOT edit or deploy
social-api and remains active in `tools/`. No sixth script was archived.

## If you need to revive one

These were archived via `git mv`, not deleted — full history is preserved.
To revive, first reroute the script to a `puretechnyc/social-api` clone path
and confirm with Chy on TRIO. Do NOT point it back at `workers/social-api/`
in the aether tree.

## References

- Branch: `retire/aether-workers-path-a-2026-05-16`
- Inventory: `/home/jared/exports/portal-files/aether-workers-retirement-inventory-2026-05-16.md`
- Constitutional rule: `feedback_purebrain_social_never_touches_referral_or_clients.md`
- Constitutional rule: `feedback_canonical_deploy_flow_2026_05_13.md`
