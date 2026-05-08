# ICP Discovery Layer for LinkedIn Commenter

**Date**: 2026-04-14
**Type**: teaching
**Topic**: Extending `tools/linkedin_icp_commenter.py` with a discovery layer that finds real LinkedIn profiles matching persona descriptions.

## Context
Drive folder `1dI3uyCeVgmkLctIt2yIv6AG2vgJKjZM3` holds 6 persona .md descriptions (not people). Commenter expected a pre-populated `profiles[]` array. Empty list = nothing to comment on.

## What Worked
- Built `discover_icp_profiles(segment, count, dry_run, log, cfg)` that:
  1. Loads persona `.md` from `configs/icp_personas/` (with `--sync-personas` to pull from Drive via `gdrive_manager.GDriveManager`)
  2. Parses title, company type, location, team size, keyword hints (regex on `**Field**:` lines + industry keyword whitelist)
  3. Picks backend in priority order by env var: Proxycurl → Apollo → PhantomBuster → PureSurf scrape → `none` (stub)
  4. Scores candidates (`score_candidate`) against persona.keywords_top5, requires `FIT_THRESHOLD >= 3`
  5. Writes to `configs/linkedin_icp_candidates.json` (NOT `linkedin_icps.json` — human review gate)
  6. Logs every run to `configs/linkedin_icp_discovery_log.jsonl`
- Enforced 14-day rotation in `select_profiles` via `ROTATION_DAYS` cutoff against `state.last_commented_at`.
- Flags: `--discover --persona <key> --count N --dry-run` and `--discover --all --count N --dry-run`.

## What's Blocked
No API keys present in `.env` for people-search:
- No `PROXYCURL_API_KEY`
- No `APOLLO_API_KEY`
- No `PHANTOMBUSTER_API_KEY`
- No `PURESURF_BROWSER_URL` / `PURESURF_LI_COOKIE` (PureSurf is a CF Worker not a local scraper)

Stub backend logs exactly what's needed; never fakes data. Discovery log + candidates file still get written cleanly.

## Files Touched
- `tools/linkedin_icp_commenter.py` (added ~230 lines)
- `configs/icp_personas/*.md` (6 personas cached from Drive)
- `configs/linkedin_icp_candidates.json` (created, empty `candidates[]`)
- `configs/linkedin_icp_discovery_log.jsonl` (7 entries from test runs)

## Key Gotcha
`gdrive_manager.download_file(file_id, dest)` creates a *directory* at `dest` and nests the file inside. Handler flattens with `.replace()` after download.

## For Future Agents
When Jared provisions a key, only `backend_proxycurl_search` is implemented. Apollo/PhantomBuster/PureSurf paths need concrete backend functions — scaffolding is in place in `pick_backend()`.
