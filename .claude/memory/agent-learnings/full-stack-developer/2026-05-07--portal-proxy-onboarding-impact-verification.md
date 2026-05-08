# Portal-Proxy Phase-0 Deploy → Onboarding Impact Verification (2026-05-07)

**Type**: operational + teaching
**Topic**: How to verify whether a CF Worker deploy broke unrelated routing paths — without rolling back

---

## Memory Search Results
- Searched: `.claude/memory/agent-learnings/full-stack-developer/` for `portal-proxy`, `purebrain-admin-2026`, `admin-2026`
- Found: `2026-05-07--portal-proxy-admin-token-rotation.md` (the deploy under investigation), `2026-05-07--cf-530-portal-proxy-greedy-wildcard.md` (greedy wildcard precedent), `2026-05-07--clients-d1-location-verification.md` (admin/clients routing), `2026-03-18--magic-link-domain-swap-research.md` (magic link path)
- Applied: route-pattern map (`*.purebrain.ai/*` greedy match + `SYSTEM_SUBDOMAINS` set), exact commit `1fe0a3e`, deploy version `a3f1da4a-...`. Avoided re-investigating from scratch.

---

## What was claimed vs what's true

**Claim:** Phase-0 commit `1fe0a3e` may have broken onboarding (`/api/log-conversation`, `/api/verify-payment`, `/api/send-seed`, `/api/magic-link/{uuid}`), because Jared reports onboarding broken AFTER the 16:27 UTC deploy.

**Truth:** No. The diff is scoped exclusively to `portal.purebrain.ai/api/admin/*`. The Worker passes `api.purebrain.ai` traffic through untouched (`'api'` is in `SYSTEM_SUBDOMAINS`). All four onboarding endpoints live-tested healthy: `200` on valid payloads, proper `400` validation on bad payloads.

---

## Verification technique that worked (4-step)

1. **Diff the exact commit**: `git show 1fe0a3e -- workers/purebrain-portal-proxy/src/worker.js` — confirmed scope.
2. **Verify "dead block" claim**: `git show 1fe0a3e^:workers/.../worker.js | sed -n '170,215p'` — read the PRE-deploy version. Two `if` blocks with **identical conditions**, first ending in `return` → second was structurally unreachable. No header/method/subdomain difference between them.
3. **Map route logic**: read `worker.js` lines 36-58 (`SYSTEM_SUBDOMAINS`) and lines 130-150 (entry point + dispatch). `'api'` is in the set → falls through to default fetch, never enters portal-routing branch.
4. **Live curl with two payloads each**: empty payload to confirm handler reachable (returns 400 with validation message), then proper payload to confirm full success (200). This distinguishes "endpoint reachable but rejecting test data" from "endpoint truly broken."

---

## CF deployment history via CF API (when wrangler is broken)

```bash
CF_TOKEN=$(grep "^CF_API_TOKEN=" .env | cut -d= -f2)
CF_ACCT=$(grep "^CF_ACCOUNT_ID=" .env | cut -d= -f2)
curl -sS "https://api.cloudflare.com/client/v4/accounts/${CF_ACCT}/workers/scripts/{name}/deployments?per_page=5" \
  -H "Authorization: Bearer ${CF_TOKEN}" | python3 -m json.tool
```

The response uses `result.deployments[]` (not `result[]`). Each entry has `id`, `created_on`, `versions[].version_id`, `annotations.workers/triggered_by`. Found prior version `d12a1a12-17f2-47fd-a158-ab4bf3854cad` (2026-05-05) for rollback prep.

---

## Gotchas hit

1. **`npx wrangler` broken mid-investigation** — `ENOTEMPTY` rename error in `~/.npm/_npx/.../node_modules/.miniflare-*` (parallel install conflict). Fall back to direct CF API. Don't fight npm.
2. **`-5` flag position with git log + path filter**: `git log --oneline path -5` errors with "option must come before non-option arguments". Use `git log -5 --oneline -- path` instead.
3. **Word-count discipline**: deliverable spec said "under 600 words." First draft was 759. Tighten by collapsing tables, dropping recap of what was said in the prompt, merging the diff/route sections.
4. **Empty test payload != broken endpoint**: a `400` response with `error: "Missing required field: X"` is PROOF the handler is reachable and validating. Always test with a valid payload AND an empty one — together they prove "alive AND validating correctly."

---

## Generalization: timing correlation ≠ causation

When two events happen close in time and one breaks (here: 15:33 git reset → 16:27 deploy → onboarding reported broken), the natural narrative is "the deploy caused the break." But the only honest test is: **does the diff touch the broken path?** If no, the timing is coincidental.

Sequence to follow before accepting "deploy broke X":
1. Show the exact diff
2. Show the path X takes through the code
3. Demonstrate the diff is in or out of that path
4. Live-test the path

If the path is healthy live, the deploy is exonerated regardless of how strong the timing correlation looks.

---

## Files

- Deliverable: `exports/portal-files/portal-proxy-deploy-impact-2026-05-07.md` (590 words)
- Worker source verified: `workers/purebrain-portal-proxy/src/worker.js`
- Commit: `1fe0a3e` (Phase 0 V-11 fix)
- Deploy under investigation: version `a3f1da4a-f747-43a9-af01-114aeb32d24a` @ 2026-05-07 16:27:03 UTC
- Prior version (rollback target if ever needed): `d12a1a12-17f2-47fd-a158-ab4bf3854cad` @ 2026-05-05 11:18:23 UTC

## Likely next investigation

Since the proxy deploy is exonerated, the actual onboarding break (if Jared's report stands) is likely:
- The 15:33 UTC `git reset --hard` (wiped runtime logs — possibly wiped local state owned by `portal_server.py` on the Witness/api box)
- An unrelated change to `api.purebrain.ai` upstream (Argo tunnel, D1 schema, or `portal_server.py`)
- Or a frontend regression on the payment/onboarding pages calling api.purebrain.ai

Recommend ST# investigate `api.purebrain.ai` upstream, NOT the proxy.
