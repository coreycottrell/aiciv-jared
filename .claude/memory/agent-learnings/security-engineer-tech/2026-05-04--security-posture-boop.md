# Security Posture BOOP — 2026-05-04

**Scope**: Code/deployments since last security check. Reviewer: security-engineer-tech.

## Recent Security-Relevant Commits

| SHA | Date | Subject | Skipped Security Review? |
|-----|------|---------|---|
| 95499ee | 2026-04-30 | fix(security): rotate dead PureSurf BaaS key in 3 client-side dashboards | No (security-tagged commit, follow-up TODO acknowledged) |
| 1601cf1 | 2026-04-30 | feat: agentmail-webhook Worker + PayPal double-count fix + welcome email fix | **YES — shipped without security review** |
| 607413e | earlier | fix: restore /insiders/awakened/ tier @ $74.50 | Constitutional onboarding-spec touched; payment-flow-qa would normally gate |

## 🔴 HIGH — agentmail-webhook unauthenticated; live at onboarding-api.purebrain.ai

**Verified by passive probe (BOOP, 2026-05-04)**: `curl -X POST https://onboarding-api.purebrain.ai/webhook` with arbitrary JSON returns `200 {"ok":true,"action":"notified"}` and forwards the body to Jared's Telegram. No authentication required.

### Findings

1. **Webhook secret bypass — `workers/agentmail-webhook/src/worker.js:309-312`**
   - "learning mode" comment explicitly logs mismatch and proceeds. Any caller can hit `/webhook` with a magic-link-shaped payload and:
     - Insert attacker-controlled rows into D1 `magic_links`
     - Trigger `welcome-email-api` to send Brevo emails to arbitrary recipients
     - Have `handleMagicLinkPoll` later return the attacker-controlled URL to a legitimate user polling `/api/magic-link/:uuid`
   - **Phishing primitive**: subject contains `MAGIC LINK`, sender contains `witness`, body has `Magic Link: https://attacker.tld/...`. Domain rewrite only fires on `.ai-civ.com`, so any other host passes through verbatim.

2. **Bearer-token comparison uses `.includes()` — `:304`**
   - `val.includes(env.AGENTMAIL_WEBHOOK_SECRET)` is substring-match instead of constant-time equality. Even if enforcement is restored, this is timing-leaky and oracle-friendly.

3. **Sensitive headers logged — `:283-290`**
   - First 50 chars of `authorization`, `x-webhook-signature`, etc. are written to `console.log`. CF Workers Logs / Logpush will capture these. Should redact entirely (e.g., `[REDACTED:len=N]`), not truncate.

4. **Permissive CORS on webhook — `:114-118, :664-668`**
   - `Access-Control-Allow-Origin: *` on a state-mutating endpoint. Combined with #1, any browser tab can trigger the pipeline.

5. **Telegram notification body is attacker-controlled — `:351-356`**
   - HTML parse_mode + arbitrary attacker text → Telegram HTML injection (limited blast — recipient is Jared only).

6. **Admin endpoint mutates `env` mid-request — `:615-619`**
   - `env.AGENTMAIL_WEBHOOK_SECRET = null; await handleWebhook(...); env = orig;` works in CF Workers per-request env, but is a footgun the next refactor will trip over. Prefer passing an explicit `{ skipAuthCheck: true }` flag.

### Recommended fix path (sequence matters)

1. **Immediate**: enforce `AGENTMAIL_WEBHOOK_SECRET` — flip lines 310-312 from log-and-continue to `return jsonResponse({ok:false,error:'unauthorized'}, 401)`. Set the secret via `wrangler secret put AGENTMAIL_WEBHOOK_SECRET` and configure AgentMail to send it. Verify with the same probe → expect 401.
2. **Same deploy**: replace `.includes()` with constant-time compare; redact (not truncate) auth headers in logs; restrict CORS to `https://app.purebrain.ai` and `https://purebrain.ai`.
3. **Follow-up**: validate parsed `magic_link` host against an allowlist (`*.app.purebrain.ai`, `*.ai-civ.com`) before D1 insert and welcome-email send. Reject any other host.
4. **Follow-up**: refactor admin endpoint to use an explicit bypass parameter instead of mutating `env`.

## 🟡 MEDIUM — paypal-webhook constitutional integrity

`workers/paypal-webhook/src/worker.js:25-40` (resolveTier) and the upsertClient fix in 1601cf1 look correct and now match constitutional pricing tiers ($74.50 Insiders / $149 Awakened / $499 Partnered / $999 Unified). Recommend follow-up unit test in `tests/` to lock the tier table — drift here directly hits revenue per the PayPal double-count incident.

I did NOT verify the PayPal signature-validation path in this BOOP — flagged for next security review.

## 🟢 LOW / GOOD — PureSurf BaaS key rotation (95499ee)

Commit verifies 0 occurrences of dead key remain. Right call as stop-gap. Constitutional follow-up already filed: migrate the 777 calendar widget behind a CF Worker proxy so no BaaS key ships in client JS. Track in ST# next rotation.

## CVE Watch (last 7 days)

No new high-severity CVEs in our stack signals (Cloudflare Workers runtime, D1, Brevo SDK, AgentMail). No npm dependencies in `workers/agentmail-webhook` (pure Worker JS) — minimal supply-chain surface.

## Decision

**Routing**: This needs ST# (workers/agentmail-webhook) + LC# (constitutional onboarding-spec compliance check). Single-line fix to enforce the secret unblocks; the rest is hardening.

**Day-3 default if Jared decision stalls**: ST# ships the immediate enforcement (item 1 above) under "security stop-gap" authority; that does NOT touch the locked onboarding flow logic, only the auth gate.
