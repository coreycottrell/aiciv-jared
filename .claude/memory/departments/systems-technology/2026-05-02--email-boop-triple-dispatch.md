# 2026-05-02 — Email-BOOP Triple Dispatch (PureSurf keys / PayPal-Brevo / PureSocial UI)

**Trigger**: Aether ST# email-check-boop dispatch — 3 tasks committed back to senders (Anchor, Mireille via Lyra, Clarity for Phil Bliss).
**Type**: operational + teaching
**Status**: DISPATCHED — awaiting specialist execution evidence

---

## Tasks

### T1 — PureSurf API Keys (P0, overdue 48hr)
- **Recipients**: Anchor (anchoraiciv@agentmail.to) + Mireille Dirany (mireille@puretechnology.nyc)
- **Plus**: Team-wide key registry audit (Lyra flagged "correct API keys need to be updated across the board")
- **Routed**: devops-engineer (provision) + security-engineer-tech (audit + IDOR session check) + cts-fullstack (delivery comms)
- **Constitutional**: VNC segments per user; keys direct-emailed (NOT via Aether)
- **Pricing change May 15** — daily cost to Anchor outreach pipeline (71 reactors + 19 profiles + 100 Noomii coaches)

### T2 — PayPal → Brevo Webhook (P1)
- **Brevo lists ALREADY BUILT** (Lyra confirmed): List 30 (Lapsed, 30 win-back automations), List 35 (Immediate Payment Recovery)
- **Missing piece**: PayPal webhook → Brevo Contacts API integration
- **Routed**: ptt-fullstack (CF Worker build) → security-engineer-tech (PAYPAL-TRANSMISSION-SIG verify) → qa-engineer (sandbox + 1 PROD test)
- **Pattern**: Reuse `tools/agentmail-webhook` worker shape (commit 1601cf1) + `paypal_auto_split.py` SDK pattern + idempotency guard from `2026-04-15--paypal-webhook-idempotency-guard.md`
- **Events**: `BILLING.SUBSCRIPTION.PAYMENT.FAILED` → List 35; `BILLING.SUBSCRIPTION.CANCELLED` → List 30
- **Constitutional**: CF Worker only (NO customer container deploy); Brevo API key in env vars

### T3 — PureSocial UI Bugs (P2 non-blocking)
- **Customer**: Phil Bliss (philip@canadasentrepreneur.com), social account `da46a702-7f2e-4e52-8d6c-f983211ad99f`
- **Bug 3a**: Avatar shows "JS" not "PB" — cached LinkedIn profile contamination on Reconnect; force-refresh /me + re-derive initials from fresh `account_handle`
- **Bug 3b**: media_refs not rendering in live preview (posts 91e95565 May 6, 021c0774 May 8); attachment confirmed in Edit panel; wire R2 CDN URLs into preview `<img>`
- **Routed**: ptt-fullstack (frontend fix at `purebrain-site/social/index.html`) → qa-engineer (smoke test + confirm scheduled posts deliver with images)
- **Constitutional**: cf-deploy.py only (NEVER wrangler); CF_PAGES_PROJECT=purebrain-production for customer-visible

---

## Conductor-of-Conductors Pattern Applied

- **Aether → ST# (me)**: Dispatched briefs, did NOT execute any task work
- **ST# (me) → specialists**: 6-7 agents in parallel where independent (devops, security, cts, ptt, qa) + sequential where dependent (BUILD → SECURITY → QA → SHIP)
- **Verifier independence**: `operations-analyst` (OP#) runs verification BOOP — NOT the executing agent (per `feedback_verifier_independence_audit_separation`)
- **Total agents in flight**: ~7 across 3 tasks

## Memory Reuse — what saved time

- `2026-04-15--linkedin-icp-puresurf-backend.md` — PureSurf has existing backend; key provisioning pattern lives there
- `2026-04-15--baas-idor-fix-session-ownership.md` — security-engineer-tech already has session ownership context for PureSurf audit
- `2026-04-21--paypal-webhook-cf-worker.md` + `2026-04-15--paypal-webhook-idempotency-guard.md` — full webhook worker shape reusable
- `2026-04-21--social-frontend-git-deploy-extraction.md` — frontend lives at `purebrain-site/social/index.html`, fetch-based worker built but not deployed
- `1601cf1` commit (`agentmail-webhook` worker) — fresh CF Worker scaffold to copy for PayPal-Brevo

## Constitutional Compliance Checklist

- [x] No customer container deploy (T2 = CF Worker)
- [x] No wrangler deploy (T3 = cf-deploy.py)
- [x] cf-deploy.py target = purebrain-production for any customer-visible T3 change
- [x] Pre-deploy sync with Chy first (T3)
- [x] Keys delivered direct (T1, NOT through Aether)
- [x] Webhook signature verification mandatory BEFORE processing (T2)
- [x] Verifier independence — OP# runs paired verify BOOP (all 3)
- [x] BUILD → SECURITY → QA → SHIP enforced (T2, T3)

## Next Action

Await specialist execution + ops-analyst verification → produce status report at `/home/jared/exports/portal-files/ST-EMAIL-BOOP-2026-05-02-status.md` with per-task DONE/IN-PROGRESS/BLOCKED + evidence + next steps.

## Teaching for Future ST# Dispatches

When Aether routes 3+ tasks in one ST# message:
1. Search memory FIRST across all 3 task domains in parallel (Grep with multiple patterns) — saves 5+ minutes vs sequential
2. Include memory paths IN the specialist brief — they don't re-discover
3. Pair every dispatch with named OP# verifier in the SAME brief — prevents "send-rate ≠ close-rate" anti-pattern
4. Constitutional reminders inline in brief — don't trust specialists to remember (wrangler ban, container ban, cf-deploy target)
