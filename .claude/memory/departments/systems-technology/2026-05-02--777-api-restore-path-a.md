# 777-API Restore Path A — 2026-05-02 09:59 UTC

**Type**: operational + teaching
**Status**: RESTORED — READY-FOR-VERIFICATION (OP# to confirm before RESOLVED)

## Outcome
- All 4 endpoints returning HTTP 200 with real data
- Triangle OS dashboard restored
- Anti-regression health probe BOOP installed (15min cadence)
- Reusable CF Worker deploy tool built (`tools/cf-worker-deploy.py`)

## What was done (in order)
1. Backed up broken worker.js to `/tmp/worker.js.broken-backup-{timestamp}`
2. `git checkout HEAD -- workers/777-sheets-api/src/worker.js` — reverted to commit 83eccfc state
3. Verified `git status workers/777-sheets-api/src/worker.js` clean
4. Built `tools/cf-worker-deploy.py` — multipart/form-data upload to CF API, NO wrangler dependency
5. Dry-run validated config parsing (vars: SPREADSHEET_ID, ALLOWED_ORIGIN; preserves secret_text bindings)
6. Live deploy → HTTP 200, `"success":true`, deployment_id `a913af9b230a4580a902c9bd3944ac3e`
7. Curl-verified all 4 endpoints with proper Origin header
8. Added `777-api-health-probe-boop` to `.claude/scheduled-tasks-state.json` (15min, owner devops-engineer)

## CRITICAL CORRECTION to prior diagnosis memo
**The URL in the prior memo was WRONG.** The diagnosis used `https://777-api.purebrain.workers.dev/` which doesn't exist (account workers.dev subdomain is `in0v8`, not `purebrain`). The real URL is `https://777-api.purebrain.ai/*` — bound via the `*.purebrain.ai` zone routes (route pattern `777-api.purebrain.ai/*` → script `777-sheets-api`).

This means yesterday's "1042 on every route" symptom was real but the URL the agents were testing was structurally wrong AND the worker really was broken. After deploy, the in0v8.workers.dev URL came back first; the purebrain.ai zone route propagated within ~30 seconds.

## Live verification evidence (curl outputs)

```
GET https://777-api.purebrain.ai/health
HTTP 200
{"status":"ok","timestamp":"2026-05-02T09:59:21.558Z","spreadsheet":"1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs"}

GET https://777-api.purebrain.ai/api/sheet?range=Handshake+Queue!A:H  (Origin: https://777.purebrain.ai)
HTTP 200
{"range":"'Handshake Queue'!A1:H1034","majorDimension":"ROWS","values":[["DATE","FROM","TO","ITEM",...

GET https://777-api.purebrain.ai/api/sheet?range=Morning+Pulse!A:H   (Origin: https://777.purebrain.ai)
HTTP 200
{"range":"'Morning Pulse'!A1:H1010","majorDimension":"ROWS","values":[["DATE","JARED PRIORITIES",...

GET https://777-api.purebrain.ai/api/sheet?range=Trio+Comms!A:H      (Origin: https://777.purebrain.ai)
HTTP 200
{"range":"'Trio Comms'!A1:H1013","majorDimension":"ROWS","values":[["id","timestamp","from","to",...
```

## New tooling (reusable)

`tools/cf-worker-deploy.py` — direct CF API worker deployer
- Replaces wrangler entirely for our use cases (wrangler is constitutionally BANNED)
- Parses `wrangler.toml` for name + main + [vars] section
- Multipart/form-data upload with `keep_bindings: ["secret_text"]` so existing service account secrets survive redeploys
- Supports `--dry-run`, `--name`, `--script` overrides
- Uses CF_API_TOKEN (Bearer, preferred) or CF_API_KEY+CF_AUTH_EMAIL fallback

Usage going forward:
```
python3 tools/cf-worker-deploy.py workers/777-sheets-api/
python3 tools/cf-worker-deploy.py workers/777-sheets-api/ --dry-run
```

## Anti-regression installed

`tasks/777-api-health-probe-boop` in `.claude/scheduled-tasks-state.json`:
- Frequency: 15 minutes
- Owner: devops-engineer
- Probes: `/health` + `/api/sheet?range=Handshake+Queue!A:H` (with Origin header)
- Alerts: portal + Telegram
- Trigger: HTTP != 200 OR body contains `"error code"` OR `"success":false`
- Recovery instructions in description (revert worker.js to HEAD, redeploy via cf-worker-deploy.py)

## Teaching for future agents

1. **Trust but verify URLs.** Prior diagnosis named `777-api.purebrain.workers.dev` but the real URL is `777-api.purebrain.ai`. Always confirm worker URLs against `/zones/{id}/workers/routes` before basing recovery on them.

2. **CF account workers.dev subdomain ≠ custom subdomain you might guess.** This account's subdomain is `in0v8`. So workers default to `<script-name>.in0v8.workers.dev`. Custom hostnames like `777-api.purebrain.ai` are zone routes, NOT account-subdomain magic.

3. **CF API multipart deploys preserve secrets via `keep_bindings: ["secret_text"]` in metadata.** Without this flag, secrets get dropped on upload and the worker fail-closes. This is the #1 footgun when migrating off wrangler.

4. **The `bindings` array in metadata REPLACES all plain_text vars on each deploy.** Always include the full list every time — partial deploys mean partial config.

5. **CF_API_TOKEN auth gives 10000 ("Authentication error") on the legacy `/workers/scripts/{name}/routes` endpoint.** That endpoint requires Global API Key (X-Auth-Email + X-Auth-Key) instead. The newer `/zones/{id}/workers/routes` endpoint accepts Bearer tokens. When in doubt, fall back to Global Key.

6. **A failed worker deploy can leave the script returning 1042 universally** — including unauth'd `/health`. The fix is always: revert to last known-good source, deploy clean, verify before adding new features.

7. **15-min health probes are non-negotiable for any worker the dashboard calls.** Prior incident held 22 hours undetected. With this BOOP we'd know within 15 min.

## Files touched
- `/home/jared/projects/AI-CIV/aether/workers/777-sheets-api/src/worker.js` (reverted to HEAD)
- `/home/jared/projects/AI-CIV/aether/tools/cf-worker-deploy.py` (NEW — 195 lines)
- `/home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json` (added 777-api-health-probe-boop)

## Deferred (next session, separate PR)
**X-API-Key write-auth hardening.** The uncommitted code at `/tmp/worker.js.broken-backup-*` is well-written — the bug was sequencing.
Required sequence:
1. `PUT /accounts/{acct}/workers/scripts/777-sheets-api/secrets` with `{name: "SHEETS_WRITE_API_KEY", text: "<value>", type: "secret_text"}` FIRST
2. Deploy hardened worker.js via cf-worker-deploy.py
3. Verify reads still work without key (no Origin/no key)
4. Verify writes now require key (POST /api/sheets/update without key → 401)
5. Update any internal callers to pass X-API-Key header
6. Then commit.

## Self-attestation boundary
Marking RESTORED + READY-FOR-VERIFICATION only. OP# (operations-analyst) must independently re-verify the 4 endpoints + confirm the BOOP entry exists + confirm git is clean before conductor marks RESOLVED.
