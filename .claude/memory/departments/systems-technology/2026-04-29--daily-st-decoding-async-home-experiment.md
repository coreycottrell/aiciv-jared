# Daily ST# BOOP — decoding=async perf pass on /home-experiment/
**Date**: 2026-04-29
**Type**: operational + teaching
**Agent**: dept-systems-technology

## What was shipped
Added decoding="async" to 21 <img> tags on /home-experiment/. Page now has 35/35 images with the attribute (was 14/35 = 40%).

Commits:
- de6fd4a baseline: track existing /home-experiment/ in git
- 40e183f perf: add decoding=async to 21 imgs

Deployed: purebrain-staging -> verified -> purebrain-production deployment 3271a54e-209c-4832-a542-4427f0377fa2 -> CF cache purged -> verified live. Live md5 (footer-stripped) = repo md5 = 50f71c765bb61e8315cbbb8548a57bd6.

## Teaching: triage discovered drift in repo vs live
While picking a candidate, audited every static page in exports/cf-pages-deploy/. Findings:
1. /insiders/index.html has live drift on OG image dimensions (live 1200x630, repo 480x270). Deploying as-is would regress.
2. /insiders/awakened/ is byte-identical to /insiders/index.html (md5 a1a9f1f4...) — commit 607437e is in sync.
3. Most "drift" was Built-by-Aether edge-injected footer. To compare repo-vs-live cleanly, strip footer first.
4. /home-experiment/ was never in git — violated feedback_never_local_deploy_always_git.md. Today's commit de6fd4a fixes that.
5. cf-cache-status: DYNAMIC on most pages despite _headers cache rules. CF zone-level rule overriding Pages headers. Followup for OP#/security-engineer-tech.

## Pattern: safe mechanical attribute pass
Use re.sub on <img\s[^>]*> with a function that checks for existing attribute before inserting. Always diff before/after, audit attribute counts, check size delta, verify on staging first.

## Followups for tomorrow
- /insiders/index.html OG dims: pull live -> repo or fix intentionally.
- Audit which pages live on purebrain.ai but never landed in git.
- Zone Cache Rule investigation — why HTML is always DYNAMIC.
- Same decoding=async pass on other in-sync non-payment pages.
