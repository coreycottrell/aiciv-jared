# LinkedIn ICP Discovery — PureSurf-Backed Flow

**Status**: LIVE (2026-04-15)
**Owner**: dept-systems-technology
**Tool**: `tools/linkedin_icp_commenter.py --discover`

---

## What This Does

Finds real LinkedIn profiles that match each ICP persona's description by
driving a real logged-in browser session on `surf.purebrain.ai` (PureSurf).
Candidates are scored against persona keywords and written to
`configs/linkedin_icp_candidates.json` for human review.

**Jared never populates `configs/linkedin_icps.json`.profiles[] manually.**
Discovery finds them — a human approves them — only approved entries get
copied into the commenter's target list.

---

## Architecture

```
tools/linkedin_icp_commenter.py
  ├─ pick_backend()              # priority: puresurf > proxycurl > stub
  ├─ backend_puresurf_search()   # the new thing
  │    ├─ _puresurf_ensure_session()   # persistent profile_name=aether-linkedin
  │    ├─ _puresurf_check_logged_in()  # one-time per run, /feed/ redirect check
  │    ├─ _puresurf_navigate()          # POST /sessions/{sid}/navigate
  │    ├─ _puresurf_evaluate(PURESURF_SEARCH_JS)  # DOM scrape
  │    └─ _puresurf_cleanup()           # DELETE session at end
  └─ discover_icp_profiles()     # score, dedupe, write candidates file
```

---

## Environment Variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `BAAS_API_KEY` | YES | — | PureSurf BaaS auth (in `.env`) |
| `PURESURF_BASE_URL` | no | `https://surf.purebrain.ai` | BaaS endpoint |
| `PURESURF_LI_PROFILE` | no | `aether-linkedin` | `profile_name` for session persistence |
| `PURESURF_PROXY` | no | `floppydata-jared` | Residential proxy provider |
| `PURESURF_DEVICE` | no | `macbook` | Device profile fingerprint |

---

## One-Time Setup (REQUIRED before first discovery run)

The `aether-linkedin` profile must be logged into LinkedIn ONCE via the
surf.purebrain.ai UI. After that, cookies persist across sessions forever
(until LinkedIn forces re-auth).

**Steps**:
1. Go to https://surf.purebrain.ai
2. Create/open a session with `profile_name = aether-linkedin` and
   `proxy_provider = floppydata-jared` and `device_profile = macbook`
3. Navigate to https://www.linkedin.com/login
4. Log in using the anchored Aether LinkedIn account
5. Complete any 2FA / verification
6. Close the session — cookies are now persisted under that profile name

**Re-run discovery**:
```bash
python3 tools/linkedin_icp_commenter.py --discover --persona smb-founder --count 10 --dry-run
```

If login cookies expire, the tool fail-closes with a clear error pointing
back to this doc.

---

## Usage

### One persona, 10 candidates (dry-run)
```bash
python3 tools/linkedin_icp_commenter.py --discover --persona smb-founder --count 10 --dry-run
```

### All 6 personas, 10 each
```bash
python3 tools/linkedin_icp_commenter.py --discover --all --count 10 --dry-run
```

### After candidate review — promote to active commenting list
```bash
# Open candidates file
$EDITOR configs/linkedin_icp_candidates.json

# Flip approved:true for winners, copy approved entries into
# configs/linkedin_icps.json > profiles[]
```

---

## Rate Limits (CONSTITUTIONAL)

LinkedIn allows **~60 navigations/hour** per browser session, enforced
proactively by PureSurf.

| Cost | Count |
|---|---|
| Login check (once per run) | 1 nav |
| Each persona search | 1 nav |
| Scroll (evaluate, not a nav) | 0 |
| **All 6 personas in one run** | **7 navs** |

Inter-persona spacing: **10–15s randomized** (set in `run_discovery`).
Session reuse: one session across all personas in a run (module-level cache).
Session cleanup: DELETE in `finally` block — always.

---

## What Gets Scraped

Per search result card:
- `handle` — LinkedIn vanity URL slug (e.g., `janesmith`)
- `url` — `https://www.linkedin.com/in/{handle}/`
- `name` — display name
- `headline` — LinkedIn "headline" field (used for persona scoring)
- `subline` — company/location (also scored)

Top 25 visible per search (more requires pagination — not implemented).

---

## What's NEVER Done

- NEVER auto-populates `configs/linkedin_icps.json` profiles[] — human gate always
- NEVER comments during discovery — discovery is read-only
- NEVER scrapes posts, messages, or private profile data
- NEVER bypasses LinkedIn's login — requires real logged-in session
- NEVER uses Wrangler, ElevenLabs, local-only files, or any banned infra

---

## Fallback Order

If `BAAS_API_KEY` is missing from `.env`:
1. → `PROXYCURL_API_KEY` (paid, external)
2. → `APOLLO_API_KEY` (scaffolded, not implemented)
3. → `PHANTOMBUSTER_API_KEY` (scaffolded, not implemented)
4. → `none` (stub — logs what's needed, returns empty)

`BAAS_API_KEY` is always present in `.env` — PureSurf is the canonical path.

---

## Files Changed

- `tools/linkedin_icp_commenter.py` — added PureSurf backend (+~240 lines)
- `configs/linkedin_icp_discovery.md` — this doc (NEW)

## Files Referenced (Unchanged)

- `configs/linkedin_icps.json` — target profiles (empty until human approves candidates)
- `configs/icp_personas/*.md` — 6 persona descriptions (from Drive `1dI3uyCeVgmkLctIt2yIv6AG2vgJKjZM3`)
- `configs/linkedin_icp_candidates.json` — human-review queue
- `configs/linkedin_icp_discovery_log.jsonl` — audit trail

---

## Verified

- [x] Syntax check: `python3 -c "import ast; ast.parse(open('tools/linkedin_icp_commenter.py').read())"` → OK
- [x] Live dry-run against surf.purebrain.ai: backend=puresurf selected, session created, `/feed/` nav executed, login-redirect detected, fail-closed with clear error, session cleanly deleted
- [ ] Post-login end-to-end: pending one-time manual login under `profile_name=aether-linkedin`
