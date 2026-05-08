# LinkedIn ICP Discovery — PureSurf Backend Shipped

**Date**: 2026-04-15
**Type**: teaching + operational
**Dept**: systems-technology (ST#)
**Trigger**: Jared correction — "I don't need to populate the profiles. You need to find the profiles. Use PureSurf to do that."

## What Shipped

Added `backend_puresurf_search()` + helpers to `tools/linkedin_icp_commenter.py`.
Reordered `pick_backend()` priority so PureSurf is first (we own it, free, anchored).

Key design:
- `profile_name` on `/sessions` POST is the persistence anchor — same name
  reuses cookies/logged-in state indefinitely. Default `aether-linkedin`.
- One session per `run_discovery` call (module-level cache), DELETE in finally.
- Login check runs once per run (not per persona) to conserve LinkedIn's
  60 navs/hour budget.
- 10-15s randomized inter-persona spacing.
- DOM scrape via `document.querySelectorAll('a[href*="/in/"]')` + walk up to
  the single-anchor container for name/headline/subline extraction.

## What Worked

- surf.purebrain.ai is publicly reachable from container (HTTP 200)
- `BAAS_API_KEY` already present in `.env`
- Existing prior art (full-stack-developer 2026-04-14) had scaffolded
  `pick_backend()` entry for puresurf — just needed the wrong env var
  contract replaced (`PURESURF_BROWSER_URL + _LI_COOKIE` → `BAAS_API_KEY`)
- Test scripts at `exports/departments/systems-technology/puresurf-test2.sh`
  documented the exact API contract (profile_name, /evaluate with script param)

## What Didn't (By Design)

Live dry-run correctly fail-closed because `aether-linkedin` profile isn't
logged into LinkedIn yet. Tool returned empty candidates, logged the one-time
login step needed, cleaned up session. This is the CORRECT behavior —
fail-closed > fake data.

## Key Gotchas

1. **Endpoint is `surf.purebrain.ai`, NOT `localhost:8901`** — the localhost
   URL from old test scripts is internal to a different container.
2. **`profile_name` not `session_id`** on session create — session_id is
   returned; profile_name is the persistence key (test-script v2 got this
   right, v1 was wrong).
3. **`evaluate` uses `script` param, not `expression`** (v1 had it wrong).
4. **Login check costs a nav** — don't do it per persona, cache the result.
5. **`quote_plus` on search query** is already imported at top of file.

## One-Time Human Setup Required

Log into LinkedIn ONCE via surf.purebrain.ai UI under `profile_name=aether-linkedin`.
After that, fully autonomous. Documented in `configs/linkedin_icp_discovery.md`.

## Files

- `tools/linkedin_icp_commenter.py` — +~240 lines (backend + helpers + cleanup wiring)
- `configs/linkedin_icp_discovery.md` — NEW operator doc
- Syntax check: passed
- Dry-run: executed against real surf.purebrain.ai, session lifecycle confirmed

## For Future Agents

When Jared ships a scraper-backed feature, default to PureSurf. Don't
reach for Proxycurl/Apollo paid APIs — we have our own browser infra.
The pattern (profile_name persistence + /evaluate DOM scrape + finally-cleanup)
generalizes to any logged-in-site scraping task.

## Delegation Chain Note (Constitutional)

This task was dispatched ST# to dept-systems-technology. Because sub-agents
cannot spawn sub-agents (runtime limit per 2026-04-14 finding), dept manager
executed the build directly rather than fanning out to full-stack-developer
→ security-engineer-tech → qa-engineer. Honest pragmatism > delegation theater.
Scope was bounded (one file, one backend, clear contract), so single-agent
execution was appropriate. For larger builds, Primary must fan out directly.
