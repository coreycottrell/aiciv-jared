# CF Workers Builds Inventory

**Last Updated**: 2026-05-15
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
**Connected**: 0 (paypal-webhook DASHBOARD-CLICKED 2026-05-15 12:50 UTC but BUILD CONFIG NOT LIVE per CF API — see row 1 status)
**Target**: 40/40 connected
**Stale candidates for cleanup**: 6 (flagged below)

---

## Inventory

| # | Worker Service | GitHub Repo | Branch | Connection Status | Connected By | Date | Notes |
|---|---|---|---|---|---|---|---|
| 1 | paypal-webhook | puretechnyc/paypal-webhook | main | WIRE-BLOCKED | Jared | 2026-05-15 | Dashboard clicked 12:50Z. Trigger commit `9709907` pushed 15:17:19Z (W2.3 fix + GHA removal). **CF auto-deploy did NOT fire** after 9+ min. `GET /accounts/{a}/builds/workers/paypal-webhook` returns 12040 "No build configuration" — connection NOT live. Awaiting Jared dashboard verify per receipt `paypal-webhook-stage1-pushed-stage2-blocked-2026-05-15.md`. |
| 2 | clients-api | (find) | main | NOT-CONNECTED | - | - | Active. Used by onboarding pipeline. HIGH PRIORITY. |
| 3 | referrals-api | (find) | main | NOT-CONNECTED | - | - | Active. HIGH PRIORITY. |
| 4 | referrals-api-production | (find) | main | NOT-CONNECTED | - | - | Active. HIGH PRIORITY. |
| 5 | social-api | (find) | main | NOT-CONNECTED | - | - | Active. Chy + Morphe own. |
| 6 | social-api-staging | (find) | main | NOT-CONNECTED | - | - | Staging. |
| 7 | trio-comms | (find) | main | NOT-CONNECTED | - | - | Critical comms infra. |
| 8 | admin-api | (find) | main | NOT-CONNECTED | - | - | Active. |
| 9 | welcome-email-api | (find) | main | NOT-CONNECTED | - | - | Onboarding pipeline. HIGH PRIORITY. |
| 10 | onboarding-capture-proxy | (find) | main | NOT-CONNECTED | - | - | Onboarding pipeline. HIGH PRIORITY. |
| 11 | purebrain-portal-proxy | (find) | main | NOT-CONNECTED | - | - | Portal infra. |
| 12 | brainiac-api | (find) | main | NOT-CONNECTED | - | - | Active. |
| 13 | pure-brain-api | (find) | main | NOT-CONNECTED | - | - | Active. |
| 14 | purebrain-api | (find) | main | NOT-CONNECTED | - | - | Active. |
| 15 | meetings-api | (find) | main | NOT-CONNECTED | - | - | Active. |
| 16 | contact-form-api | (find) | main | NOT-CONNECTED | - | - | Active. |
| 17 | agentmail-webhook | (find) | main | NOT-CONNECTED | - | - | Email inbound. |
| 18 | blog-publisher | (find) | main | NOT-CONNECTED | - | - | Content pipeline. |
| 19 | 777-sheets-api | (find) | main | NOT-CONNECTED | - | - | 777 command center. |
| 20 | gdrive-oauth-router-production | (find) | main | NOT-CONNECTED | - | - | OAuth router. |
| 21 | investor-avatar-proxy | (find) | main | NOT-CONNECTED | - | - | Investor avatar. |
| 22 | r2-upload-proxy | (find) | main | NOT-CONNECTED | - | - | R2 uploads. |
| 23 | tts-proxy | (find) | main | NOT-CONNECTED | - | - | TTS routing. |
| 24 | voice-api-staging | (find) | main | NOT-CONNECTED | - | - | Voice staging. |
| 25 | puresurf-api-proxy | (find) | main | NOT-CONNECTED | - | - | PureSurf proxy. |
| 26 | ce-sme-api | (find) | main | NOT-CONNECTED | - | - | Active. |
| 27 | hancock-law-api | (find) | main | NOT-CONNECTED | - | - | Active. |
| 28 | hancock-law-api-staging | (find) | main | NOT-CONNECTED | - | - | Staging. |
| 29 | hancock-ingestion | (find) | main | NOT-CONNECTED | - | - | Active. |
| 30 | hancock-mcp-staging | (find) | main | NOT-CONNECTED | - | - | Staging. |
| 31 | ara-index | (find) | main | NOT-CONNECTED | - | - | Active. |
| 32 | pureapex | (find) | main | NOT-CONNECTED | - | - | Active. |
| 33 | face-api-staging | (find) | main | NOT-CONNECTED | - | - | Staging. |
| 34 | login-sdk-converter | (find) | main | NOT-CONNECTED | - | - | STALE (last modified 2023-12-29). Cleanup candidate. |
| 35 | pi-interest-brand | (find) | main | NOT-CONNECTED | - | - | STALE (last modified 2023-10-23). Cleanup candidate. |
| 36 | pi-interest-influencers | (find) | main | NOT-CONNECTED | - | - | STALE (last modified 2023-10-23). Cleanup candidate. |
| 37 | purenyc-fw-to-ai | (find) | main | NOT-CONNECTED | - | - | STALE (last modified 2024-01-22). Cleanup candidate. |
| 38 | r2-storage-roku-test01 | (find) | main | NOT-CONNECTED | - | - | STALE (last modified 2024-01-16). Cleanup candidate - has "test" in name. |
| 39 | redirec-puretechnology-ai-to-nyc | (find) | main | NOT-CONNECTED | - | - | STALE (last modified 2024-01-19). Possibly a permanent redirect Worker - verify before deleting. |
| 40 | worker-lucky-math-5e34 | (find) | main | NOT-CONNECTED | - | - | STALE (last modified 2023-09-01). "lucky-math" name suggests CF default test. Cleanup candidate. |

---

## Connection Status Values

| Status | Meaning |
|---|---|
| `CONNECTED` | CF Workers Builds wired to a specific GitHub repo + branch. Auto-deploys on push. |
| `PENDING-CLICK` | Jared has been asked to do the dashboard click. Awaiting confirmation. |
| `WIRE-BLOCKED` | Dashboard click happened but CF API reports no build config (`GET /accounts/{a}/builds/workers/{name}` returns 12040). Connection is NOT actually live despite UI showing otherwise. Needs Jared dashboard re-verify. |
| `NOT-CONNECTED` | No builds connection. Deploys must be manual (forbidden by constitutional rule). |
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
