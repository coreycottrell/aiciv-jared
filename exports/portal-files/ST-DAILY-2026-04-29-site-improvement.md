# ST# Daily Site Improvement — 2026-04-29

**Agent**: dept-systems-technology  
**Trigger**: ST# (daily department production task)  
**Date**: 2026-04-29  
**Result**: SHIPPED — perf improvement live on purebrain.ai

---

## 1. Item picked + why

**Picked**: Add `decoding="async"` to all `<img>` tags on `/home-experiment/`.

**Why this candidate**:
- Triaged inbox/tester-feedback/, ST# memories, recent CTO memories, and recent handoffs. No fresh tester bugs in the inbox; chronic open issues (LinkedIn cookies, GTM form tracking, PayPal sandbox) all need Jared/external action and don't fit the daily-ship-one-thing scope.
- Pivoted to "pick highest-impact safe perf win" per the BOOP fallback path.
- Audited every page in `exports/cf-pages-deploy/` for image-perf-attribute coverage and repo-vs-live sync. **Most pages were drifted** between repo and live — see Risk section. `/home-experiment/` was the cleanest candidate: in sync (live md5 == repo md5 once edge-injected footer is stripped), 35 images, only 14/35 (40%) had `decoding="async"`. Non-payment, non-onboarding-spec page (A/B test surface created Apr 15 per ptt-fullstack memory).
- `decoding="async"` is universally safe — it hints to the browser to decode images off the main thread, freeing the main thread for layout and interaction. Universal browser support, zero negative cases.

**Why not pick something bigger**: Three other candidates were rejected:
- `/insiders/`, `/insiders/awakened/`, `/insiders/pay-test-awakened/` — payment / onboarding-spec pages. `/insiders/` had un-pulled live edits to `og:image` dimensions (live 1200x630 vs repo 480x270), so deploying repo-as-is would regress.
- `live-3d`, `governance`, `pitch`, `strategic-roadmap` — drifted repo-vs-live in ways that on first inspection looked content-significant; turned out to be Built-by-Aether edge-injected footers, but I didn't unwind that safely-enough to ship today. Logged for tomorrow.
- Homepage WP-served HTML — outside our git→cf-deploy.py surface (WordPress-themed).

---

## 2. Diff summary

**Files changed**: 1 (`exports/cf-pages-deploy/home-experiment/index.html`)

**Lines**: +21 / -21 (only `decoding="async"` added to 21 img tags that lacked it; the diff stat shows 21 insertions and 21 deletions because each affected line was rewritten in-place).

**Bytes**: +357 uncompressed, ~20-50 after gzip/br.

**Commits**:
| SHA | Subject |
|---|---|
| `de6fd4a` | baseline: track existing /home-experiment/ page in git |
| `40e183f` | perf: add decoding="async" to 21 images on /home-experiment/ |

The baseline commit was needed because `/home-experiment/` had been deployed to production but its source HTML had **never been committed to git** (constitutional violation per `feedback_never_local_deploy_always_git.md`). Tracked it as today's first commit at the existing live state, then layered the perf change on top.

**Audit before**: 35 imgs, 14 with `decoding="async"` (40%), 27 with `loading="lazy"` (77%).  
**Audit after**: 35 imgs, 35 with `decoding="async"` (100%), 27 with `loading="lazy"` (77%).

No content/text/script/style changes — only the one attribute on existing img tags.

---

## 3. Security review verdict

**GREEN.**

- `decoding="async"` is a pure browser perf hint. No behavior change.
- Zero new content, no new scripts, no new URLs, no auth/cookie/session impact.
- No CSP impact (no new resources).
- No XSS surface (no user input, no innerHTML/eval).
- Payment guard (`tools/verify-payment-pages.sh`): **113/113 checks passed** post-deploy, all 9 payment pages clean.

---

## 4. QA evidence

**Staging deploy**: `https://27440854.purebrain-staging.pages.dev/home-experiment/`

Verifications run:
- HTTP 200, 650998 bytes, 0.29s response time
- All 35 images have `decoding="async"`, all 27 lazy-loaded images preserved
- Staging md5 == repo md5 (`50f71c765bb61e8315cbbb8548a57bd6`)
- Mobile UA fetch (`iPhone iOS 17 Safari`) returns identical bytes to desktop (zero diff)
- No broken markup, no missing tags, file size matches exactly

**Visual regression**: not run (single mechanical attribute change with no rendered impact — would have been overkill).

**Adjacent pages**: payment guard sweep ran across all 9 payment pages post-deploy → all 113 checks pass.

---

## 5. Production deploy

- **Project**: `purebrain-production`
- **Deployment ID**: `3271a54e-209c-4832-a542-4427f0377fa2`
- **Direct URL**: `https://3271a54e.purebrain-production-23b.pages.dev`
- **Live URL**: `https://purebrain.ai/home-experiment/`
- **Files in deployment**: 1304 (1 changed, 0 new, 0 deleted, 1303 preserved). 1 protected file preserved per cf-deploy.py constitutional protection.

**CF cache purge**:
```json
POST https://api.cloudflare.com/client/v4/zones/{zone}/purge_cache
files: ["https://purebrain.ai/home-experiment/", "https://purebrain.ai/home-experiment"]
result: {"success": true, "errors": [], "id": "49400cad1527af716705f6cb8c22bb65"}
```

**Live verification** (3 sec post-purge):
```
status: 200
size:   650998 bytes
imgs total:    35
decoding=async: 35    <-- proof: all images now have the attribute
loading=lazy:  27
md5(live, footer-stripped) = 50f71c765bb61e8315cbbb8548a57bd6
md5(repo)                  = 50f71c765bb61e8315cbbb8548a57bd6
```

Live md5 matches repo md5 exactly. Production is serving the new content.

**Pre-deploy sync with Chy**: ran `tools/pre-deploy-sync.sh` first. Pulled investor-avatar/, investor-tracking/, gifts/ + general shared changes. No conflicts with `/home-experiment/`.

---

## 6. Risk + rollback

**Risk**: minimal. `decoding="async"` is a perf hint with no behavior change. Page is non-payment, non-onboarding-spec.

**Rollback** (if ever needed):
```bash
git revert 40e183f
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py home-experiment/index.html
# then purge https://purebrain.ai/home-experiment/
```

The baseline commit `de6fd4a` should NOT be reverted — it documents the pre-existing live state and brings `/home-experiment/` under git management for the first time. That's net-positive regardless of the perf delta.

---

## 7. Followups (queued for tomorrow / future BOOPs)

These came up during triage and deserve their own tickets:

1. **`/insiders/index.html` has un-pulled live edits**: live serves `og:image:width=1200, og:image:height=630` while repo has `480x270`. Someone updated OG meta on the deployed file (probably via dashboard / direct asset edit) and it never came back to git. Deploying repo-as-is regresses live. Need to either pull live-back into repo OR re-derive the correct values intentionally. **Owner**: ST# (full-stack-developer to investigate, then commit corrected version).

2. **`/home-experiment/` was never in git** before today. Are there OTHER pages on purebrain.ai that exist live but never landed in git? Worth a one-shot audit. **Owner**: ST# (devops-engineer, scriptable: walk Pages manifest vs `git ls-files exports/cf-pages-deploy/`).

3. **CF cache rules are bypassing Pages `_headers`**: every page returns `cf-cache-status: DYNAMIC` despite our `_headers` declaring `max-age=300`. Likely a zone-level Cache Rule or cookie-based bypass. Edge-cache opt-in is broken for HTML across the zone. **Owner**: OP# + security-engineer-tech (zone Cache Rule audit).

4. **Same `decoding="async"` pass on other in-sync non-payment pages** (`oldchatbox`, candidates with edge-footer drift only). Quick win to ship in a future daily ST# BOOP — same recipe, different page.

5. **Built-by-Aether edge-injected footer** — what worker injects this, where does it live, is it documented? Showed up as drift on most pages. **Owner**: ST# (devops-engineer to locate worker / Pages function).

---

## Appendix: triage timeline

| Step | Result |
|---|---|
| Search inbox/tester-feedback/ | No new files since 2026-04-03 |
| Search ST# dept memory | Most recent = 2026-04-23 calculator-v2-email-gate; relevant = 2026-03-20 site-speed-optimization (WP bloat removal) |
| Search CTO memory | Most recent = 2026-04-20 container-cf-migration-plan |
| Read scratch-pad RECENT ERRORS | Last update 2026-04-11; chronic issues all need Jared / external action |
| Audit 30+ static pages for image perf gap | 30 pages had `decoding="async"` <70% coverage |
| Cross-reference sync state (repo md5 vs live md5) | Most "drift" was edge-injected footer; truly-in-sync candidates: home-experiment, oldchatbox, home-test variants, investor-avatar-max, invest |
| Filter for non-payment, non-Chy-owned | home-experiment (Aether-owned A/B test) wins |
| Verify spec position | Not on ONBOARDING-SPEC payment page list; safe to modify |
| Build → Security → QA → Ship | All green |
| Memory written | `.claude/memory/departments/systems-technology/2026-04-29--daily-st-decoding-async-home-experiment.md` |

