# 2026-05-07 — admin/referrals deploy/source mismatch

## Type
operational + teaching

## Context
Jared tested commit b98235f's referral admin fixes on portal.purebrain.ai/admin/. Reported: autocomplete works but missing names; Save Splits button "does nothing".

## Findings (verified by curl)

1. **17 commits unpushed on main** including b98235f.
2. **Live portal HTML** (md5 `3b74f111…`, 1323 lines) has zero references to splits/btnSaveSplits/renderSplitRows. The split UI does not exist on live site.
3. **Live staging HTML** (md5 `3a7d8eed…`, 1286 lines) — same: no splits.
4. **Local CF Pages copy** (md5 `c91a4d7b…`, 2159 lines) is the b98235f file with full split logic. Never deployed.
5. **Symptom mapping**:
   - "Save Splits does nothing" = button selector returns null on live = matches the fact that `btnSaveSplits` is absent from live HTML.
   - "Names missing in autocomplete" = could be CORS fallback gating + wrong dataset (affiliates vs clients).

## Worker-side bugs found (referrals-api/src/worker.js)

- `/admin/affiliates` (line 1775-1784) does not return `split_config` field. Frontend reads `af.split_config` to render existing splits — always empty even if D1 has data. Confirmed via /admin/partners which does include split_config.
- D1 stores `split_config` as JSON string (e.g., `"[{\"role\":\"invalid_role\",...}]"`). Frontend handles string→parse on save response (line 1865) but not on initial load — relevant once Worker fix lands.

## Frontend-side bugs (exports/cf-pages-deploy/admin/referrals/index.html)

- Line 1006: `renderSplitRows(af.split_config || [])` — needs JSON.parse if string.
- Line 1336: fallback gated to `hostname !== 'portal.purebrain.ai'` — defeats fallback purpose on production.
- Line 1336 fallback uses `affiliates` as proxy for `clients` — wrong dataset (subset).

## CORS verified

- referrals-api: `*` origin, all methods. Works.
- admin-api: returns origin-specific allow header. Works for `https://portal.purebrain.ai`. **Does NOT** include `https://staging.purebrain.ai` (returns `https://purebrain.ai` instead — mismatch).

## Lesson

**Always verify what the live host actually serves before debugging frontend.** I almost diagnosed Save Splits as a route mismatch when the real cause was "the button is not on the live page." `curl + md5sum + diff against repo file` is a 30-second sanity check that prevents hours of dead-end work.

## Files referenced
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/admin/referrals/index.html` (b98235f, undeployed)
- `/home/jared/projects/AI-CIV/aether/workers/referrals-api/src/worker.js` (lines 380-426, 1775-1784)

## Next session
- Wait for Jared confirmation of exact URL tested.
- Do not push the 17-commit backlog without explicit auth — mixed unrelated changes.
