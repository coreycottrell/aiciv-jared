# 777-API Write API Key — CONFIDENTIAL

**Date**: 2026-05-02
**Owner**: Jared (do not redistribute outside trusted internal callers)
**Worker**: `777-sheets-api` on Cloudflare
**Affected endpoints**: `POST /api/sheets/update`, `POST /api/sheets/append`

---

## The Key

```
SHEETS_WRITE_API_KEY=RkcVixJuuOVMzf_0sL7Yh2kAgaX76sldClRaqBq7CtPTlYIHHmtsgQM0nmdhB2UY
```

**Properties**: 64 characters, URL-safe Base64 (~384 bits of entropy), generated via Python `secrets.token_urlsafe(48)`.

**Do NOT**:
- Post this to the handshake queue
- Commit this to any git repo
- Send via email, Slack, or Telegram
- Embed in any client-side asset that goes to a non-trusted user

**OK to**:
- Embed in `exports/cf-pages-deploy/777-command-center/index.html` as `WRITE_API_KEY` constant (the dashboard is trusted-internal at `777.purebrain.ai`). NOTE: this is a known limitation — view-source attackers visiting the dashboard URL can extract it. See "Residual risk" below.
- Use in private CLI scripts you (or trusted internal AIs) keep on local/server filesystems
- Set as `SHEETS_WRITE_API_KEY` secret on the worker via `wrangler secret put`

---

## Internal callers that need this key

Currently, only ONE caller writes to the worker today:

1. **777 Command Center dashboard** (`777.purebrain.ai`) — uses `WORKER_API_KEY` constant in `index.html` for both reads and writes today. Needs to be split into:
   - `WORKER_API_KEY` (existing) for reads — stays as-is
   - `WRITE_API_KEY` (new) for writes — this new value

No Python scripts, shell scripts, or other workers currently call `/api/sheets/update` or `/api/sheets/append` (verified via repo grep on 2026-05-02). If you wire up new internal callers later (Aether scripts, Chy scripts), give them this key.

---

## Rollout sequence (zero-downtime)

Run these in order. Each step is reversible until step 4.

### Step 1 — Set the worker secret

```bash
cd /home/jared/projects/AI-CIV/aether/workers/777-sheets-api
wrangler secret put SHEETS_WRITE_API_KEY
# When prompted, paste:
# RkcVixJuuOVMzf_0sL7Yh2kAgaX76sldClRaqBq7CtPTlYIHHmtsgQM0nmdhB2UY
wrangler secret list   # verify SHEETS_WRITE_API_KEY appears
```

This is safe to do BEFORE deploying the new worker code — the existing worker code ignores the secret.

### Step 2 — Patch the dashboard with the new key

Edit `exports/cf-pages-deploy/777-command-center/index.html`:

Replace line ~4343:
```js
const WORKER_API_KEY = 'j5kLX8NkYrHIxBOHUlVHXGs40nOf8jn7MP9wkPPQV_Q';
```

With:
```js
const WORKER_API_KEY = 'j5kLX8NkYrHIxBOHUlVHXGs40nOf8jn7MP9wkPPQV_Q';
const WRITE_API_KEY  = 'RkcVixJuuOVMzf_0sL7Yh2kAgaX76sldClRaqBq7CtPTlYIHHmtsgQM0nmdhB2UY';
```

Then in the three write call sites (lines ~4729, ~4751, ~4773), change:
```js
'X-API-Key': WORKER_API_KEY
```
to:
```js
'X-API-Key': WRITE_API_KEY
```

(Reads at line ~4710 keep `WORKER_API_KEY`.)

### Step 3 — Deploy dashboard

```bash
cd /home/jared/projects/AI-CIV/aether
# 777-command-center is a Pages project — use cf-deploy.py per constitutional rule
CF_PAGES_PROJECT=777-command-center python3 tools/cf-deploy.py 777-command-center/index.html
```

Verify the dashboard works (reads are unchanged; writes still hit the OLD worker code which doesn't yet enforce the new key — so writes succeed via origin alone).

### Step 4 — Deploy the patched worker

```bash
cd /home/jared/projects/AI-CIV/aether/workers/777-sheets-api
wrangler deploy
```

`wrangler deploy` for a Worker is NOT the banned `wrangler pages deploy` — Workers are single JS files with no file-deletion semantics. This is the only supported tool for Worker deploys (cf-deploy.py is Pages-only).

After deploy, the new worker enforces `X-API-Key=SHEETS_WRITE_API_KEY` on writes. Dashboard already has the new key from step 3, so it keeps working. Curl-from-anywhere with spoofed Origin no longer can write.

### Step 5 — Run QA matrix (see `QA-CURL-MATRIX` below)

### Step 6 — (Optional, later) Rotate the key

If the dashboard key ever leaks (or to rotate quarterly):
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"   # generate new key
wrangler secret put SHEETS_WRITE_API_KEY   # paste new value
# Update dashboard WRITE_API_KEY constant, redeploy
```

---

## QA Curl Matrix (run AFTER step 4)

```bash
KEY="RkcVixJuuOVMzf_0sL7Yh2kAgaX76sldClRaqBq7CtPTlYIHHmtsgQM0nmdhB2UY"
URL="https://777-api.purebrain.ai"

# 1. Read still works origin-only — expect 200
curl -s -o /dev/null -w "READ origin-only: %{http_code}\n" \
  -H "Origin: https://777.purebrain.ai" \
  "$URL/api/sheet?range=Morning%20Pulse!A1:B2"
# EXPECT: 200

# 2. Write WITHOUT key — expect 401
curl -s -o /tmp/r2.json -w "WRITE no-key: %{http_code}\n" \
  -X POST -H "Content-Type: application/json" \
  -H "Origin: https://777.purebrain.ai" \
  -d '{"range":"EOD Report!Z99","values":[["test"]]}' \
  "$URL/api/sheets/update"
cat /tmp/r2.json
# EXPECT: 401, body: {"error":"Unauthorized","reason":"missing_or_invalid_write_key"}

# 3. Write WITH WRONG key — expect 401
curl -s -o /tmp/r3.json -w "WRITE wrong-key: %{http_code}\n" \
  -X POST -H "Content-Type: application/json" \
  -H "Origin: https://777.purebrain.ai" \
  -H "X-API-Key: not-the-real-key" \
  -d '{"range":"EOD Report!Z99","values":[["test"]]}' \
  "$URL/api/sheets/update"
cat /tmp/r3.json
# EXPECT: 401

# 4. Write WITH CORRECT key — expect 200
curl -s -o /tmp/r4.json -w "WRITE correct-key: %{http_code}\n" \
  -X POST -H "Content-Type: application/json" \
  -H "Origin: https://777.purebrain.ai" \
  -H "X-API-Key: $KEY" \
  -d '{"range":"EOD Report!Z99","values":[["security-test-2026-05-02"]]}' \
  "$URL/api/sheets/update"
cat /tmp/r4.json
# EXPECT: 200, body has updatedRange/updatedRows

# 5. Append WITHOUT key — expect 401
curl -s -o /tmp/r5.json -w "APPEND no-key: %{http_code}\n" \
  -X POST -H "Content-Type: application/json" \
  -H "Origin: https://777.purebrain.ai" \
  -d '{"range":"EOD Report!A:Z","values":[["test"]]}' \
  "$URL/api/sheets/append"
cat /tmp/r5.json
# EXPECT: 401

# 6. Read with no Origin — expect 401 (existing behavior, unchanged)
curl -s -o /dev/null -w "READ no-origin: %{http_code}\n" \
  "$URL/api/sheet?range=Morning%20Pulse!A1:B2"
# EXPECT: 401
```

All six checks must pass. After confirming, clean up the test row written in step 4 (range `EOD Report!Z99`) if you don't want lingering test data.

---

## Residual risks (for follow-up, not blocking ship)

1. **Dashboard view-source extraction**: The `WRITE_API_KEY` value is embedded in the dashboard HTML at `777.purebrain.ai`. Anyone who loads that page can view-source and extract the key. This means the lockdown blocks naive curl-from-anywhere attackers but NOT anyone who scrapes the dashboard. Proper fix would be a server-side proxy: a CF Pages Function that holds the key as an HttpOnly secret and the dashboard talks to it instead. ~half-day rebuild. Track as a follow-up ST# task.

2. **Length oracle in constant-time compare**: The `constantTimeEquals` helper reveals whether the input length matches the secret length. With a 64-char random secret, this leaks essentially nothing useful (an attacker still has to guess 384 bits of entropy). Acceptable.

3. **No app-level rate limiting**: CF edge naturally rate-limits, but no per-key brute-force lockout. Given the entropy of the key, brute-forcing is infeasible. Acceptable.

---

**Field this back to ST#** if any of the QA matrix steps fail. The conductor will queue OP# pair-verification per `feedback_verifier_independence_audit_separation.md` to confirm the lockdown actually works in production.
