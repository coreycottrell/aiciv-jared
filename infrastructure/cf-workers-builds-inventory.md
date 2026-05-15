# CF Workers Builds Inventory

**Last Updated**: 2026-05-15 16:20 UTC (Stream A fleet wire — 13/40 connected)
**Source of Truth**: This file (git HEAD)
**Drift Detection**: `tools/cf-workers-builds-drift-check.sh` runs hourly
**Account ID**: `d526a3e9498dd167509003004df03290`

---

## Constitutional Rule

> **Every CF Worker MUST be deployed via CF Workers Builds connected to its source GitHub repo.**
>
> Filed: `.claude/memory/feedback_workers_deploy_via_cf_workers_builds.md` (2026-05-15)
> Reason: CF-native deploy is faster than GHA, doesn't require external billing, runs inside CF's edge, and aligns with "git is the only source of truth" constitutional.
>
> **Banned**:
> - Local `wrangler deploy` (constitutional, 2026-05-13)
> - GHA `wrangler deploy` (decided 2026-05-15 after Jared challenge "we're a CF-native shop")
> - Direct CF API script uploads (constitutional, 2026-05-13)
>
> **Allowed**: Git push to repo `main` -> CF Workers Builds auto-deploys.

---

## Current State (Baseline)

**Total Workers**: 40
**Connected**: 13 (paypal-webhook + 12 wired via Builds API by devops-engineer 2026-05-15 16:17 UTC)
**Target**: 40/40 connected
**Blocked**: 27 (likely sourced in `coreycottrell/aiciv-jared` monorepo — CF GitHub App NOT installed on coreycottrell org; needs Jared dashboard action to install App on that org OR finish source migration to puretechnyc/*)
**Stale candidates for cleanup**: 6 (flagged below)

### Stream A Fleet Wire Discovery (2026-05-15)

The CF Workers Builds API works end-to-end **without** any dashboard click, given:
1. CF GitHub App installed on the target org (confirmed: puretechnyc, NOT confirmed: coreycottrell)
2. User-scoped CF token with `Workers Builds Configuration:Edit` (in `.env` as `CF_API_TOKEN_BUILDS`)
3. `build_token_uuid` from `GET /accounts/{a}/builds/tokens` (current: `5f445549-fbc4-416b-9fcf-0a16b23178d5`)

**Per-Worker API calls** (2 calls, ~1 sec):
- `PUT /accounts/{a}/builds/repos/connections` body `{provider_type, provider_account_id, provider_account_name, repo_id, repo_name}` → returns `repo_connection_uuid`
- `POST /accounts/{a}/builds/triggers` body with `external_script_id` (= script_tag), `repo_connection_uuid`, `branch_includes`, `deploy_command`, `build_token_uuid`, etc.

**Brief was wrong about paypal-webhook 12040**: the GET probe used script NAME instead of script TAG. paypal-webhook was wired correctly by Jared's dashboard click at 15:38:26Z.

---

## Inventory

| # | Worker Service | GitHub Repo | Branch | Connection Status | Connected By | Date | Notes |
|---|---|---|---|---|---|---|---|
| 1 | paypal-webhook | puretechnyc/paypal-webhook | main | CONNECTED | Jared (dashboard) | 2026-05-15 | Dashboard wire at 15:38:26Z created conn `f18493ce` + 2 triggers (Deploy default branch `9090b508`, non-prod branches `bc50fb72`). API GET probe needs script_tag NOT script name. |
| 2 | clients-api | puretechnyc/clients-api | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `5a5373a0`, trig `3a18f217`. Tier 1 #1. |
| 3 | referrals-api | puretechnyc/referrals-api | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `0ebf02c1`, trig `561af962`. Tier 3 #16. |
| 4 | referrals-api-production | (find) | main | BLOCKED-NO-REPO | - | - | No standalone puretechnyc/* repo. Likely lives in coreycottrell/aiciv-jared (App NOT installed). Tier 1 HIGH PRIORITY. |
| 5 | social-api | puretechnyc/social-api | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `4290d458`, trig `423bd97d`. Tier 2. Chy + Morphe own. |
| 6 | social-api-staging | (find) | main | BLOCKED-NO-REPO | - | - | No standalone puretechnyc/* repo. Likely monorepo. |
| 7 | trio-comms | puretechnyc/trio-comms | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `f3c01ebe`, trig `34dc3243`. Tier 2 critical comms infra. |
| 8 | admin-api | puretechnyc/admin-api | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `d78238e5`, trig `7c18a545`. Tier 2. |
| 9 | welcome-email-api | puretechnyc/welcome-email-api | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `68e05528`, trig `2a0bb8b1`. Tier 1 HIGH PRIORITY (onboarding pipeline). |
| 10 | onboarding-capture-proxy | (find) | main | BLOCKED-NO-REPO | - | - | No standalone puretechnyc/* repo. Aether tree `workers/onboarding-capture-proxy/` exists; canonical source likely coreycottrell/aiciv-jared monorepo (BLOCKED — App not installed). HIGH PRIORITY. |
| 11 | purebrain-portal-proxy | puretechnyc/purebrain-portal-proxy | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `c37fae69`, trig `2f853c56`. Tier 2 portal infra. |
| 12 | brainiac-api | (find — puretechnyc/brainiac-purebrain?) | main | BLOCKED-NEEDS-MAPPING | - | - | Candidate: `puretechnyc/brainiac-purebrain` (multi-Worker repo, needs root_directory). 3 names (brainiac-api/pure-brain-api/purebrain-api) may all collapse into one repo. |
| 13 | pure-brain-api | (find — puretechnyc/brainiac-purebrain?) | main | BLOCKED-NEEDS-MAPPING | - | - | See brainiac-api note. |
| 14 | purebrain-api | (find — puretechnyc/brainiac-purebrain?) | main | BLOCKED-NEEDS-MAPPING | - | - | See brainiac-api note. |
| 15 | meetings-api | puretechnyc/meetings-api | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `9a37c97a`, trig `82ed0f79`. Tier 3 #11. |
| 16 | contact-form-api | (find) | main | BLOCKED-NO-REPO | - | - | No standalone puretechnyc/* repo. Aether tree has `workers/contact-form-api/`; likely coreycottrell monorepo (BLOCKED). |
| 17 | agentmail-webhook | puretechnyc/agentmail-webhook | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `31f37112`, trig `421bd6a2`. Tier 3 email inbound. |
| 18 | blog-publisher | puretechnyc/blog-publisher | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `873a3293`, trig `a56a4dc1`. Tier 3 content pipeline. |
| 19 | 777-sheets-api | puretechnyc/777-sheets-api | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `27e86352`, trig `46668b28`. Tier 3 #14. |
| 20 | gdrive-oauth-router-production | (find) | main | BLOCKED-NO-REPO | - | - | No standalone puretechnyc/* repo. Likely coreycottrell monorepo or different name. |
| 21 | investor-avatar-proxy | (find — puretechnyc/investor-portal?) | main | BLOCKED-NEEDS-MAPPING | - | - | Candidate: `puretechnyc/investor-portal` (multi-Worker repo, needs root_directory). |
| 22 | r2-upload-proxy | (find) | main | BLOCKED-NO-REPO | - | - | No standalone puretechnyc/* repo. |
| 23 | tts-proxy | (find — puretechnyc/voice-platform?) | main | BLOCKED-NEEDS-MAPPING | - | - | Candidate: `puretechnyc/voice-platform` (multi-Worker repo, needs root_directory). |
| 24 | voice-api-staging | (find — puretechnyc/voice-platform?) | main | BLOCKED-NEEDS-MAPPING | - | - | Same candidate as tts-proxy. |
| 25 | puresurf-api-proxy | (find — puretechnyc/puresurf?) | main | BLOCKED-NEEDS-MAPPING | - | - | Candidate: `puretechnyc/puresurf`. |
| 26 | ce-sme-api | (find — puretechnyc/ce-sme?) | main | BLOCKED-NEEDS-MAPPING | - | - | Candidate: `puretechnyc/ce-sme` (id 1235908062, multi-component repo). Also lives in aiciv-jared monorepo. |
| 27 | hancock-law-api | (find — puretechnyc/hancock-law?) | main | BLOCKED-NEEDS-MAPPING | - | - | Candidate: `puretechnyc/hancock-law` (id 1231947578, multi-Worker repo with 4 hancock-* workers). |
| 28 | hancock-law-api-staging | (find — puretechnyc/hancock-law?) | main | BLOCKED-NEEDS-MAPPING | - | - | Same candidate as hancock-law-api. |
| 29 | hancock-ingestion | (find — puretechnyc/hancock-law?) | main | BLOCKED-NEEDS-MAPPING | - | - | Same candidate as hancock-law-api. |
| 30 | hancock-mcp-staging | (find — puretechnyc/hancock-law?) | main | BLOCKED-NEEDS-MAPPING | - | - | Same candidate as hancock-law-api. |
| 31 | ara-index | puretechnyc/ara-index | main | CONNECTED | devops-engineer (API) | 2026-05-15 | conn `a5fae905`, trig `e5783e9d`. Tier 3 #21. |
| 32 | pureapex | (find — puretechnyc/PureApex-portal?) | main | BLOCKED-NEEDS-MAPPING | - | - | Candidate: `puretechnyc/PureApex-portal`. |
| 33 | face-api-staging | (find — puretechnyc/face-platform?) | main | BLOCKED-NEEDS-MAPPING | - | - | Candidate: `puretechnyc/face-platform`. |
| 34 | login-sdk-converter | (find) | main | BLOCKED-STALE | - | - | STALE (last modified 2023-12-29). Cleanup candidate — recommend DELETE not connect. |
| 35 | pi-interest-brand | (find) | main | BLOCKED-STALE | - | - | STALE (last modified 2023-10-23). Cleanup candidate — recommend DELETE. |
| 36 | pi-interest-influencers | (find) | main | BLOCKED-STALE | - | - | STALE (last modified 2023-10-23). Cleanup candidate — recommend DELETE. |
| 37 | purenyc-fw-to-ai | (find) | main | BLOCKED-STALE | - | - | STALE (last modified 2024-01-22). Cleanup candidate — recommend DELETE. |
| 38 | r2-storage-roku-test01 | (find) | main | BLOCKED-STALE | - | - | STALE (last modified 2024-01-16). Cleanup candidate — recommend DELETE. |
| 39 | redirec-puretechnology-ai-to-nyc | (find) | main | BLOCKED-STALE | - | - | STALE (last modified 2024-01-19). Verify if still serving redirects via probe before deciding. |
| 40 | worker-lucky-math-5e34 | (find) | main | BLOCKED-STALE | - | - | STALE (last modified 2023-09-01). "lucky-math" suggests CF default test. Recommend DELETE. |

---

## Connection Status Values

| Status | Meaning |
|---|---|
| `CONNECTED` | CF Workers Builds wired to a specific GitHub repo + branch. Auto-deploys on push. |
| `PENDING-CLICK` | Jared has been asked to do the dashboard click. Awaiting confirmation. |
| `WIRE-BLOCKED` | Dashboard click happened but CF API reports no build config (`GET /accounts/{a}/builds/workers/{name}` returns 12040). Connection is NOT actually live despite UI showing otherwise. Needs Jared dashboard re-verify. |
| `NOT-CONNECTED` | No builds connection. Deploys must be manual (forbidden by constitutional rule). |
| `BLOCKED-NO-REPO` | No standalone puretechnyc/* repo found. Source is likely in `coreycottrell/aiciv-jared` monorepo where CF GitHub App is NOT installed. Needs source migration to puretechnyc OR App install on coreycottrell. |
| `BLOCKED-NEEDS-MAPPING` | A candidate puretechnyc/* repo exists but it's multi-Worker. Need code-archaeologist to identify exact `root_directory` for this Worker's source. |
| `BLOCKED-STALE` | Worker hasn't been touched in 6+ months. Recommend DELETE not wire — audit before action. |
| `STALE` | Worker hasn't been touched in 6+ months. Mark for cleanup audit before wiring builds. |
| `DRIFT` | Connection exists but differs from this inventory file (wrong repo, wrong branch, or removed). |

---

## Repo Discovery TODO

The `GitHub Repo` column is `(find)` for most rows because:
- Some Workers were originally deployed via local `wrangler deploy` (no repo tracked in CF)
- Some have source in `aether/` tree, some in `puretechnyc/` org repos, some in `coreycottrell/` org
- ST# needs a separate sweep to map each Worker -> source repo

**Action**: After Phase 1 ships (paypal-webhook live), spawn `code-archaeologist` to grep the aether tree + `gh repo list` for matching source files per Worker name. Update this column.

---

## Connection Priority Queue (for Jared dashboard clicks)

After paypal-webhook lands, Jared works through these in order:

**Tier 1 - Customer-facing onboarding (CRITICAL)**:
1. clients-api
2. welcome-email-api
3. onboarding-capture-proxy
4. referrals-api-production

**Tier 2 - Live infrastructure**:
5. social-api
6. trio-comms
7. admin-api
8. purebrain-portal-proxy
9. brainiac-api / pure-brain-api / purebrain-api (consolidate or wire all 3)

**Tier 3 - Active feature Workers**:
10. blog-publisher
11. meetings-api
12. contact-form-api
13. agentmail-webhook
14. 777-sheets-api
15. gdrive-oauth-router-production
16. referrals-api (note: vs referrals-api-production - clarify diff)
17. r2-upload-proxy
18. tts-proxy
19. puresurf-api-proxy
20. ce-sme-api
21. ara-index
22. pureapex
23. investor-avatar-proxy

**Tier 4 - Staging environments**:
24. social-api-staging
25. voice-api-staging
26. hancock-law-api-staging
27. hancock-mcp-staging
28. face-api-staging

**Tier 5 - Hancock vertical**:
29. hancock-law-api
30. hancock-ingestion

**Tier 6 - STALE / Cleanup audit FIRST**:
31. login-sdk-converter (verify dead, then delete)
32. pi-interest-brand (verify dead, then delete)
33. pi-interest-influencers (verify dead, then delete)
34. purenyc-fw-to-ai (verify dead, then delete)
35. r2-storage-roku-test01 (verify dead, then delete - test-named)
36. redirec-puretechnology-ai-to-nyc (verify if still serving redirects, then decide)
37. worker-lucky-math-5e34 (verify dead, then delete - looks like CF default test name)

---

## How to Update This File

**When a connection is made**:
1. Update the row: `NOT-CONNECTED` -> `CONNECTED`, fill `GitHub Repo`, `Connected By`, `Date`
2. Commit to aether repo with message: `infra: connect <worker-name> CF Workers Builds to <repo>`
3. The drift detector will pick up the change on next hourly run

**When a connection is removed** (NOT recommended - violates constitutional):
1. Update row to `NOT-CONNECTED`
2. Document reason in Notes column
3. File constitutional exception in `.claude/memory/`

**When a new Worker is created** (anywhere in the account):
1. Drift detector will alert: "Worker X exists in CF but not in inventory"
2. ST# must add a row within 24h
3. Per constitutional: new Workers MUST be created with CF Workers Builds connection BEFORE first push

---

## Source-of-Truth Pattern

- **CF Dashboard** = current state (mutable, can be wrong)
- **This file** = desired state (git-immutable, the truth)
- **Drift detector** = compares them hourly, alerts on mismatch

If drift detector says CF != inventory, the inventory wins. Investigate the drift before changing this file.

---

## References

- Constitutional memo: `.claude/memory/feedback_workers_deploy_via_cf_workers_builds.md`
- Canonical deploy flow: `.claude/memory/feedback_canonical_deploy_flow_2026_05_13.md`
- Git source of truth: `.claude/memory/feedback_wrangler_deploy_must_be_preceded_by_git_commit.md`
- SOP for clicks: `infrastructure/cf-workers-builds-connection-SOP.md`
- Drift detector: `tools/cf-workers-builds-drift-check.sh`
- CF API endpoint base: `https://api.cloudflare.com/client/v4/accounts/d526a3e9498dd167509003004df03290/workers/`
