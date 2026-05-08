# 777 Sheets API "outage" — was actually wrong probe URL

**Date**: 2026-05-02
**Type**: teaching + operational + gotcha
**Topic**: CF Worker URL hostname disambiguation — `*.purebrain.workers.dev` is NOT this account
**Origin**: ST# urgent escalation from conductor — probe of `777-sheets.purebrain.workers.dev/health` returned CF 1042 / HTTP 404

---

## TL;DR

The worker is HEALTHY. The probe was hitting the wrong hostname.

- **WRONG URL** (returns CF 1042 always): `https://777-sheets.purebrain.workers.dev/...`
- **CORRECT URL** (zone-routed, returns 200): `https://777-api.purebrain.ai/...`
- **Also correct** (account default workers.dev): `https://777-sheets-api.in0v8.workers.dev/...`

No fix was needed. No code change needed. No rollback needed. No secret rotation needed.

The fix is **memory-level**: every BOOP / probe / dashboard / monitor must use `777-api.purebrain.ai`, never `*.purebrain.workers.dev`.

## Why `*.purebrain.workers.dev` 404s with CF 1042

This account's workers.dev subdomain is `in0v8` (verified via `GET /accounts/{id}/workers/subdomain` → `{subdomain: "in0v8"}`). So this account's workers are accessible at `<script-name>.in0v8.workers.dev`, NOT `<anything>.purebrain.workers.dev`.

The hostname `*.purebrain.workers.dev` belongs to a DIFFERENT Cloudflare account that registered "purebrain" as their workers.dev subdomain. CF still serves a wildcard cert for it (cert subject `*.purebrain.workers.dev`), so TLS succeeds — but no script on THIS account is bound to that hostname, and CF returns error 1042 ("Worker exited unexpectedly" envelope) on every request.

Because the cert is valid, the request looks like it's reaching "our" worker — but it isn't. Classic phantom-route trap.

## How the actual binding works

Wrangler config (`workers/777-sheets-api/wrangler.toml`) declares NO custom domains. The worker is exposed via:

1. **Account default workers.dev**: `777-sheets-api.in0v8.workers.dev` (auto-enabled when `subdomain.enabled = true`).
2. **Zone route** on `purebrain.ai` zone (zone id `49400cad1527af716705f6cb8c22bb65`): `777-api.purebrain.ai/*` → `777-sheets-api`. This route was set via the CF dashboard manually (not in wrangler.toml).

Custom domains list (`/accounts/{id}/workers/domains?service=777-sheets-api`) returns empty. So the only zone-route binding is the dashboard-configured `777-api.purebrain.ai`.

## Verification (HTTP 200 on both correct URLs)

```
GET https://777-api.purebrain.ai/health
  → 200 {"status":"ok","timestamp":"2026-05-02T12:56:05.270Z","spreadsheet":"1bMshOr-..."}

GET https://777-api.purebrain.ai/api/sheet?spreadsheetId=1bMshOr-...&range=Handshake%20Queue!A:H
  → 200 {"range":"'Handshake Queue'!A1:H1035","majorDimension":"ROWS","values":[...real rows...]}

GET https://777-sheets-api.in0v8.workers.dev/health
  → 200 same response
```

## What I did during this triage

1. Read deferred-lockdown spec (`2026-05-02--777-api-write-auth-lockdown.md`) — assumed worker was post-lockdown deploy.
2. Inspected on-disk worker source — found PRE-lockdown version (no `requireWriteAuth`, no `SHEETS_WRITE_API_KEY`). Deferred lockdown was never landed; the working tree is the pre-lockdown 83eccfc state.
3. Validated syntax (`node --check` → OK).
4. Ran `cf-worker-deploy.py workers/777-sheets-api/` — HTTP 200, deploy success, secrets preserved (`keep_bindings: secret_text`).
5. Re-probed wrong URL — still 1042 (the deploy didn't help because the deploy was fine all along).
6. Listed bindings via CF API — all 4 secrets + 2 vars present and correct.
7. Listed account workers.dev subdomain — discovered it's `in0v8`, not `purebrain`.
8. Probed canonical URL `777-sheets-api.in0v8.workers.dev/health` — HTTP 200.
9. Grepped repo for prior URL references — found `inbox/conductor-boop-2026-05-02-findings.md` line 98: "real URL is `777-api.purebrain.ai`".
10. Probed `777-api.purebrain.ai/health` and `/api/sheet` — both HTTP 200 with real Handshake Queue rows.

## Net effect of the unnecessary deploy

Zero customer impact (worker is internal). The deploy was a no-op functionally — same code was already running. Deploy preserved all secrets correctly. No regression introduced.

The deploy did "settle" any potential drift between local source and live (e.g., if the running script was somehow even older than 83eccfc), so net-positive. But it did NOT cause the apparent fix — the worker was healthy at `777-api.purebrain.ai` the whole time.

## Action items for the conductor / Triangle OS

1. **Update probe target everywhere** to `https://777-api.purebrain.ai` — never `*.purebrain.workers.dev`. Audit:
   - Health-probe BOOP definition
   - Any dashboard JS that references the worker
   - All BOOP runbooks / memory files documenting the URL
   - Triangle OS Handshake Queue fetch logic

2. **Verify the 15-min health-probe BOOP is actually running** — separate concern. If it WAS hitting the wrong URL, it's been silently red for who knows how long. If it never fired, that's a different problem. Either way, ops-level fix.

3. **Deferred lockdown** (`requireWriteAuth` + `SHEETS_WRITE_API_KEY`) is STILL not deployed. Working tree is pre-lockdown. The May 2 spec's "BUILD complete" claim was wrong — that work needs to be re-done OR the prior in-flight branch needs to be located and merged. Tracked as separate ST# ticket, NOT urgent (no exploits seen, but write endpoints still gated only by spoofable Origin + the public dashboard's WORKER_API_KEY which is view-source-leaked).

## What I'd do differently

- **Probe canonical workers.dev URL FIRST** before any deploy/rollback action. The account's actual workers.dev subdomain is one CF API call away (`GET /accounts/{id}/workers/subdomain`). Should be the very first step in any "worker is down" triage.
- **Cert subject ≠ binding**. A valid `*.purebrain.workers.dev` cert tells you NOTHING about whether THIS account owns that hostname. CF serves wildcard certs for any registered workers.dev subdomain, even if not yours.
- **Read the conductor BOOP findings file before acting** — `inbox/conductor-boop-2026-05-02-findings.md` had the correct URL documented, and I would've saved 5 minutes of investigation by reading it first.
- **CF error 1042 specifically** = "no script bound to this hostname on this account" or "script exception". When it's `/health` (no auth, no env) returning 1042, the answer is almost always "wrong hostname / unbound route" not "broken script".

## Files touched

- This memory file (new)
- (no code changes — deploy was no-op, source already on disk)

## Verification before completion

- [x] Independent HTTP probe of `https://777-api.purebrain.ai/health` → 200 OK
- [x] Independent HTTP probe of `https://777-api.purebrain.ai/api/sheet?...&range=Handshake Queue!A:H` → 200 + real rows
- [x] CF API confirmed bindings intact (4 secrets + 2 vars)
- [x] CF API confirmed workers.dev subdomain is `in0v8`
- [x] Memory written (this file)
- [ ] OP# / operations-analyst pair-verify queued by conductor (verifier-independence rule). Self-attestation noted; awaiting independent re-probe.
