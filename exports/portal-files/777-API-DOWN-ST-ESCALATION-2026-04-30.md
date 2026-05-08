# 777-API DOWN — Handshake Queue + Morning Pulse blocked

**Date**: 2026-04-30 19:18 UTC
**Severity**: HIGH (blocks Triangle OS conductor cycle)
**Routed to**: ST# (dept-systems-technology)
**Escalated by**: Aether (conductor-of-conductors BOOP)

---

## What's broken

`https://777-api.purebrain.ai/api/sheet?range=...` returns `{"error":"Not found"}` (HTTP 404) for both:
- `Handshake%20Queue!A:H`
- `Morning%20Pulse!A:H`

Tested with documented `Origin: https://777.purebrain.ai` header. Worker is reachable but the `/api/sheet` route handler is failing on every range query.

## Why it matters

1. **Conductor-of-conductors BOOP is half-blind** — cannot read CHY → AETHER handshakes programmatically.
2. **Anticipation Engine is degraded** — can't auto-generate sales talking points from shipped features without Pulse rows.
3. **Triangle Operating System (LIVE) is hobbled** — falls back to `msg-chy.sh` direct + portal-only coordination.

## Confirmed status

- **2nd consecutive conductor BOOP** has hit the 404 (first finding logged in `inbox/conductor-boop-2026-04-30-findings.md`).
- Dashboard frontend (`https://777.purebrain.ai/`) serves 200 — UI loads, API doesn't.
- Local `exports/777-command-center/data.json` snapshot is fresh for `daily_pulse` but **does not contain Handshake Queue rows**.

## Asks for ST# (dept-systems-technology)

Per `feedback_routed_items_need_verification_boop.md`, this routing receipt requires a paired verification. Suggested ST# diagnostic order:

1. **Worker → project binding**: confirm `777-api.purebrain.ai` Worker is still bound to project `777-command-center`. CF Pages/Workers dashboard.
2. **Recent deploys**: did the `/api/sheet` route handler get removed/renamed in a recent commit?
3. **Service-account creds**: did the Sheets service-account creds rotate or expire?
4. **Spreadsheet ID**: verify worker reads `1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs` (the correct TOS sheet).
5. **Worker logs**: tail `wrangler tail` or CF logs to capture the actual failure mode (auth? wrong sheet ID? scope?).

## Workaround active

- Coordination with Chy via `msg-chy.sh` direct + portal messages.
- Anticipation Engine paused for the duration.

## Verification BOOP

Per `feedback_verifier_independence_audit_separation.md`, OP# (operations-analyst) should verify ST# fix in next 24h cycle. Don't self-attest.

---

**File**: `exports/portal-files/777-API-DOWN-ST-ESCALATION-2026-04-30.md`

---

## UPDATE 19:30 UTC — ST# diagnosis complete (TWO bugs found)

**Bug 1 — Wrong route name (the visible 404):**
- Worker exposes `/api/sheets/read` (plural). Conductor BOOP + memory doc call `/api/sheet` (singular). Worker correctly 404s.
- Source: `workers/777-sheets-api/src/worker.js:243`.

**Bug 2 — Worker bound to wrong default spreadsheet (the hidden 500):**
- `wrangler.toml` has `SPREADSHEET_ID = "1BaMup71ObVneuEBn-VWwGgU2vPpg9IZX9lFui_qTO8c"` (Life Planner — 70 tabs, none named "Morning Pulse" or "Handshake Queue").
- Correct TOS sheet is `1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs`.
- Live proof: `/api/sheets/read?range=Morning%20Pulse!A:H&spreadsheetId=1bMshOr-Hf4...` → **HTTP 200 + 14 rows of Pulse data**.

**Two-line fix (NOT executed — needs Jared greenlight):**
1. `workers/777-sheets-api/wrangler.toml` → set `SPREADSHEET_ID = "1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs"`
2. `cd workers/777-sheets-api && wrangler deploy` (Workers — wrangler-deploy ban applies to Pages, not Workers)
3. Update memory doc `reference_777_sheets_api_format.md` to use `/api/sheets/read` (plural)

**ST# memory written**: `.claude/memory/departments/systems-technology/2026-04-30--777-api-down-diagnosis.md`

**Asking Jared**: Greenlight ptt-fullstack to execute the 2-line fix + redeploy + ptt-qa verification curl? Reply **GO** or **fix it** to authorize.

**Workaround active until fix**: conductor BOOP can use `/api/sheets/read?...&spreadsheetId=1bMshOr-Hf4...` override.
