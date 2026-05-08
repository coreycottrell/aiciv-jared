# 777-API Down — Diagnosis (dept-systems-technology)

**Date**: 2026-04-30
**Severity**: HIGH (Triangle OS conductor cycle blocked)
**Type**: operational
**Topic**: 777-sheets-api worker — wrong spreadsheet bound + caller path mismatch

## Root Causes (TWO distinct bugs, both real)

### Bug 1: Caller using wrong route (the visible 404)
- Conductor BOOP / TOS clients hitting `/api/sheet?range=...` (singular)
- Worker exposes `/api/sheets/read?range=...` (plural)
- Worker correctly returns 404 — caller path is wrong
- Evidence: `curl /api/sheet?range=Handshake%20Queue!A:H` → 404 `Not found`
- Evidence: `curl /api/sheets/read?range=Handshake%20Queue!A:H` → 500 (different error, see Bug 2)
- Source: `workers/777-sheets-api/src/worker.js:243` only routes `/api/sheets/read`

### Bug 2: Worker bound to wrong default spreadsheet
- `wrangler.toml` SPREADSHEET_ID = `1BaMup71ObVneuEBn-VWwGgU2vPpg9IZX9lFui_qTO8c` (Life Planner sheet)
- Correct TOS spreadsheet ID = `1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs`
- The bound sheet has 70 tabs but NONE are "Morning Pulse" or "Handshake Queue"
- Evidence: `/api/sheets/meta` returned tabs from "0. Jared's Learning to Live Life Planner..."
- Evidence: passing `?spreadsheetId=1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs` returns 200 with full Morning Pulse data
- Override param `spreadsheetId` works because `getSpreadsheetId(env, override)` honors caller value

## Live Verification (2026-04-30 ~19:30 UTC)

```
# 404 (wrong path)
curl -H "Origin: https://777.purebrain.ai" "https://777-api.purebrain.ai/api/sheet?range=Morning%20Pulse!A:H"
→ HTTP 404 {"error":"Not found"}

# 500 (right path, wrong default sheet)
curl -H "Origin: https://777.purebrain.ai" "https://777-api.purebrain.ai/api/sheets/read?range=Morning%20Pulse!A:H"
→ HTTP 500 "Unable to parse range: Morning Pulse!A:H" (because that tab doesn't exist in bound sheet)

# 200 (right path + override = correct sheet)
curl -H "Origin: https://777.purebrain.ai" "https://777-api.purebrain.ai/api/sheets/read?range=Morning%20Pulse!A:H&spreadsheetId=1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs"
→ HTTP 200 with 14 rows of data
```

## Recommended Fix (delegated to ptt-fullstack)

Two-line fix, but must follow git → staging → production:

1. Update `workers/777-sheets-api/wrangler.toml` SPREADSHEET_ID to `1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs`
2. Commit, push, redeploy worker via `wrangler deploy` (Workers, NOT Pages — wrangler-pages ban does NOT apply to Workers)
3. Update conductor BOOP scripts to call `/api/sheets/read` (not `/api/sheet`) — search codebase for `/api/sheet?` callers

## Why Bug 1 alone wouldn't explain it

If only Bug 1 were the issue, fixing the caller path would land on `/api/sheets/read` and STILL fail (500, wrong sheet). Both bugs must be fixed for full restoration.

## Verification BOOP target (per OP# audit separation)

After ptt-fullstack deploys:
- `curl /api/sheets/read?range=Handshake%20Queue!A:H` → expect 200
- `curl /api/sheets/read?range=Morning%20Pulse!A:H` → expect 200
- No `spreadsheetId` override needed once wrangler.toml fixed

OP# (operations-analyst) verifies independently in next 24h.
