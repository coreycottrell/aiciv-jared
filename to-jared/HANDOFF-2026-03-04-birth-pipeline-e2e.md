# HANDOFF — 2026-03-04 Birth Pipeline E2E Wiring Session

## FIRST THING
1. **Fix portal URL allowlist** — `ai-civ.com` is NOT in the browser's allowed domains. Witness magic links (`*.ai-civ.com`) will be REJECTED by the portal button validator. Add `ai-civ.com` to the `allowedDomains` array in page 1232's `runPortalButtonWatcher` function.
2. **Fix container naming** — Match Witness format: `keen-jared-sanborn` (hyphens between parts). Current derivation strips all non-alpha. Change to: `aiName + '-' + fullName.split(' ').join('-')`.
3. **Check Witness comms** — They have a test findings doc + 4 bugs. Bug #1 (auto-trigger) is the main blocker.
4. **Verify server running** — `ss -tlnp | grep 8443` should show python3 listening.

## What Was Accomplished This Session

### Birth Pipeline — WIRED END-TO-END
1. **pay-test-sandbox-3 blank screen FIXED** — `sanitizeText()` missing + `launchPostPaymentFlow` trapped in IIFE scope
2. **Button text changed** — "a button will appear here" → "the button below will light up" on pages 1232, 688, 689
3. **Greyed-out button injected INTO chat overlay** — was hidden behind z-index 999999, now inside `msgList`
4. **Button animation system** — `ptc-portal-btn--disabled` (grey) → `ptc-portal-btn--active` (blinking blue #2a93c1 / orange #f1420b)
5. **Welcome to Family card updated** — removed old placeholder text

### Webhook Endpoint
6. **`/api/birth/webhook` built** — receives birth_complete from Witness, validates, logs, emails customer, notifies Jared
7. **Brevo template 30 created** — "Your AI partner is ready" email with magic link button
8. **5/5 tests passing** — fresh birth, dedup, bad auth, missing fields, wrong event
9. **Witness confirmed e2e test** — their POST got `{"ok":true,"duplicate":true}`

### Portal Status
10. **`/api/birth/portal-status/{container}` FIXED** — was broken (old proxy intercepting). Now checks local `birth_completions.jsonl` first, falls back to Witness proxy.
11. **REAL Witness birth received** — container `keen-jared-sanborn`, magic link with real token

### Seed Sender
12. **Page 1232 now sends seed** to `/api/birth/start` after chat completes
13. **Container name derived client-side** as fallback, server response is authoritative

## Key Files Changed
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` — webhook endpoint, portal-status fix, Brevo template ID
- WP Page 1232 — sanitizeText fix, IIFE fix, button text, greyed-out button, seed sender, portal polling
- WP Pages 688, 689 — button text change only
- `/home/jared/projects/AI-CIV/aether/docs/e2e-aether-side-findings-20260304.md` — full findings doc
- `_comms_hub/partnerships/2026-03-04--aether-e2e-test-findings.md` — same doc in hub

## Known Gaps (Priority Order)
1. **🔴 `ai-civ.com` not in portal URL allowlist** — button will reject Witness magic links
2. **🟡 Container naming mismatch** — Aether: `keenjared`, Witness: `keen-jared-sanborn`
3. **🟡 Witness auto-trigger broken** — seeds land but SCP fails, orchestrator never fires (Witness fixing)
4. **🟢 Pages 688/689 don't have new button UX** — only 1232 has greyed-out → light-up
5. **🟢 Brevo template 30 untested with real delivery**

## Server State
- PID: check with `pgrep -f purebrain_log_server`
- Port: 8443 (SSL)
- Public: `https://api.purebrain.ai`
- Birth log: `logs/birth_completions.jsonl` (9 entries, 1 real Witness birth)
