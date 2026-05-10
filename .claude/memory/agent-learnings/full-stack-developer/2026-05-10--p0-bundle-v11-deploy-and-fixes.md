# P0 Bundle: V-11 Deploy + display_name + Owner Role Gate + Sheila Cosmetic

**Date**: 2026-05-10
**Agent**: PTT (full-stack-developer)
**Type**: teaching
**Trigger**: CTO APPROVE-FOR-BUILD on 5-fix P0 bundle

## What I Did
- Diagnosed V-11 (anonymous /api/admin/invites returning full invitee list).
- Fixed display_name selector on admin-api worker.js:213 (u.name AS display_name).
- Fixed sess.role !== "leader" at 6 sites in admin-api + 1 site in portal-proxy.
- Reduced waitlist form from 5 required to 2 required (name + email only).
- Cleared cosmetic Sheila/Jay residue at magic_links id=9.

## Key Learnings

### V-11 root cause was MISSED DEPLOY, not branch divergence per se
- The CTO brief hypothesized "deploy didn't propagate vs path-match wrong vs middleware ordering."
- Reality: commit `65ef0f0` (V-11 gate) lives on `referral-v1`. Last live portal-proxy deploy was 2026-05-09 10:08 UTC — the gate commit at 10:25 UTC was **never deployed**.
- Diagnostic: `wrangler deployments list --name purebrain-portal-proxy` shows the live version's timestamp. Compare to the gate commit timestamp on the source branch. If commit > last deploy = deploy never happened.
- Fix path: stay on `referral-v1`, add fixes there, `wrangler deploy`. Branch reconciliation with `main` is a separate chore.

### Branch divergence audit before assuming "deploy didn't propagate"
- `git log --oneline main ^referral-v1 -- workers/purebrain-portal-proxy/` showed 2 commits on `main` not on `referral-v1` (admin token rotation + literal removal).
- `git log --oneline referral-v1 ^main -- workers/purebrain-portal-proxy/` showed the V-11 gate commit.
- **Always do this two-way diff before deploying** — otherwise you can lose security work that's only on the other branch.

### display_name was masked by X-Admin-Token shortcut
- admin-api worker.js getSession() has 3 paths: X-Admin-Token shortcut → bridge call → D1 fallback.
- The buggy SELECT lives ONLY on the D1 fallback path. With bridge healthy + X-Admin-Token in use, line 213 is never executed in prod.
- Why this matters: a security-critical bug can be invisible for weeks if a faster path bypasses it. Schema audits should run against ALL paths, not just the one currently executing.

### Owner exclusion was in TWO files
- `sess.role !== "leader"` (admin-api, 6 sites) is the obvious one.
- `j.role !== "leader"` (portal-proxy worker.js:182, in `validateLeaderSession`) is the SAME bug at the gate layer.
- **CTO pre-build review caught this; my initial dispatch only listed admin-api.** Fix MUST go in same commit, otherwise V-11 gate exposes 500s for every owner the second auth fixes flip live.

### NO-FUZZY rule for human_name selection (constitutional)
- S5-payerName fuzzy fallback is BANNED (May 8 rule). That extends to "guess Sheila's last name from the data."
- Found authoritative answer in PTT memory: `2026-05-10--whitehurst-household-audit.md` confirmed `sheila@couplify.com (id=94): Sheila Whitehurst`. Used this, not a guess.
- Belt-and-suspenders WHERE clause: `WHERE id=9 AND LOWER(human_email)='sheila@couplify.com' AND ai_name='Kindred'` — three matchers so if any drifts, UPDATE fails closed.

### Browser verification on form-field changes
- Yesterday's lesson (no curl-only) applied: ran Playwright headless against live URL to verify `required` attribute state.
- The form is gated behind a tier-selection step, so element fill via Playwright .fill() failed (element not visible).
- Workaround: evaluate `getElementById(...).hasAttribute('required')` directly — DOM evaluation works on hidden elements. Confirmed: name+email required, all others not required.

### Pre-deploy credential scan = MANDATORY before each deploy
- Ran `bash .claude/skills/pre-deploy-credential-scan/scan.sh` on both workers BEFORE and AFTER edits (0 CRITICAL, 0 HIGH).
- `cf-deploy.py` ran its own credential scan on the materialized waitlist file (clean).

## Files Touched
- `workers/admin-api/src/worker.js` (commit 83d767a)
- `workers/purebrain-portal-proxy/src/worker.js` (commit 83d767a)
- `exports/cf-pages-deploy/waitlist/index.html` (commit 04c7e93)
- D1 `purebrain-social.magic_links` row id=9 (UPDATE)

## Deploy IDs
- portal-proxy version: `e768da8b-c514-4b60-bc27-f67ccb2085ca`
- admin-api version: `586bc3ed-0857-4fed-9b5c-97675aea8236`
- Pages deploy: `6cd6f846-4051-479d-ae38-0b51a9461acf`

## What Didn't Work
- `git status` showed pending uncommitted changes on admin-api (cache helpers, bridge code) that rolled into my commit. Did a sanity check via `git show --stat` — they were consistent with the wrangler.toml CLIENTS_API binding and the CTO brief's bridge architecture, so I accepted them. **Future**: should `git stash` first, then apply only my edits, to isolate diffs cleanly.
- Initial `cf-deploy.py exports/cf-pages-deploy/waitlist/index.html` failed with double-prefix path. Tool wants relative path: `cf-deploy.py waitlist/index.html`.

## Status
P0-BUNDLE-COMPLETE-AWAITING-SEC-QA. Receipt: `exports/portal-files/build-receipt-p0-bundle-2026-05-10.md`.
