# Tier 3 Extraction Sprint — Dispatch Plan
**Agent**: dept-systems-technology (ST#)
**Date**: 2026-05-08
**For**: Aether (spawns specialists DIRECTLY — sub-agent constraint)
**SPEC reference**: `exports/portal-files/TIER3-EXTRACTION-SPEC-2026-05-08.md`
**CTO review**: `exports/portal-files/cto-prebuild-review-clients-extraction-2026-05-08.md` (GO-WITH-EDITS — already incorporated into SPEC)

---

## 1. Phase-by-Phase Specialist Assignments

| Phase | Scope | Specialist | Rationale |
|---|---|---|---|
| **0** | Schema dumps (`clients`, `users`, `sessions`, `team_invites`, `paypal_events`) → `shared/*.sql` git commit | **coder** | Precision dump+commit. Gate-zero. |
| **1** | Stand up `clients-api` repo + Worker + D1 `purebrain-clients` + skeleton routes | **wtt-fullstack** | Hancock-Law repo pattern matches Witness birth-pipeline shape. |
| **2** | Stand up `payments-api` repo + Worker + D1 `purebrain-payments` + skeleton webhook | **coder** | Hancock-Law clone scaffolding. Parallel with P1. |
| **3** | Migrate clients/users/sessions code from social-api + fold `admin-api` in + add `/api/forgot-password` + `/api/reset-password` | **wtt-fullstack** | Same engineer as P1. PBKDF2 hash-parity critical. |
| **4** | Migrate `paypal-webhook` code into payments-api + bridge calls to clients-api & hancock-law-api | **coder** | Same engineer as P2. Mechanical port. |
| **5** | Bridge APIs (`/validate-token`, `/internal/clients`) + portal-proxy header gate + rebind agentmail-webhook + meetings-api + blog-publisher to bridges | **ptt-fullstack** | PT owns portal-proxy + Service Bindings. |
| **6** | Data migration via SQL dump+import; row-count verify | **coder** | Per CTO §2 SQL-dump path. |
| **7** | Header-gated routing flip canary → 100% | **ptt-fullstack** | Continuation of P5. |
| **8** | 24h verify — login%, page load, error rate, bridge success | **operations-analyst** | **Constitutional**: independent verifier. NOT the cutover engineer. |
| **9** | Cleanup — DROP tables, remove admin-api + paypal-webhook Workers | **coder** | Destructive SQL. Aether holds gate. |
| **10** | Bulk resend — 64 admin users, batches of 10 @ 30s | **human-liaison** | Owns AgentMail + rate-limit patterns. |

**SECURITY gate** (`security-auditor`): between P5 close and P7 traffic flip. Hard gate.
**QA gate** (`wtt-qa` / `qa-engineer` / `ptt-qa`): end of P3, P4, P5, and integration pre-P7.

---

## 2. Parallelization Graph

```
                Phase 0 (coder) — SCHEMAS TO GIT — gate-zero
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         Phase 1        Phase 2       (Phase 5 prep:
         (wtt-FS)       (coder)        ptt-FS reads
       clients-api     payments-api    contracts)
              │             │
              ▼             ▼
         Phase 3        Phase 4       Phase 5 (ptt-FS)
         (wtt-FS)       (coder)       bridge APIs
       code migrate    paypal port    + portal-proxy
              │             │             │
              └─────────────┴──────┬──────┘
                                   ▼
                          QA gate (qa-engineer
                          + wtt-qa + ptt-qa)
                                   │
                                   ▼
                          SECURITY gate
                          (security-auditor)
                                   │
                                   ▼
                          Phase 6 (coder)
                          DATA MIGRATION
                                   │
                                   ▼
                          Phase 7 (ptt-FS)
                          HEADER FLIP — canary → 100%
                                   │
                                   ▼
                          Phase 8 (operations-analyst)
                          24h VERIFY
                                   │
                          ┌────────┴────────┐
                          ▼ GREEN           ▼ RED
                    Phase 9 (coder)    Rollback (header off)
                    CLEANUP            social-api still owns data
                          │
                          ▼
                    Phase 10 (human-liaison)
                    BULK RESEND
```

**Concurrent windows:**
- **Window A (Day 1)**: Phase 0 alone — gate-zero, no parallel.
- **Window B (Days 2–3)**: Phase 1 + Phase 2 in parallel (wtt-fullstack + coder).
- **Window C (Days 3–5)**: Phase 3 + Phase 4 + Phase 5 in parallel (wtt-fullstack + coder + ptt-fullstack — 3-engineer max parallelism).
- **Window D (Day 6)**: QA + SECURITY gates — sequential (QA first, then SEC).
- **Window E (Day 7)**: Phase 6 + Phase 7 — Phase 6 must finish before Phase 7 traffic flip.
- **Window F (Days 8–9)**: Phase 8 — 24h burn, ops-analyst monitors only.
- **Window G (Day 10)**: Phase 9 + Phase 10 — parallel (different specialists, independent work).

---

## 3. SECURITY / QA Gate Placement

**Per BUILD → SECURITY → QA → SHIP rule (no exceptions):**

| Gate | When | Owner | What gets reviewed |
|---|---|---|---|
| QA — clients-api unit | End of Phase 3 | `wtt-qa` | Login flow, session token compat, hash parity |
| QA — payments-api unit | End of Phase 4 | `qa-engineer` | Webhook signature verify, idempotency |
| QA — bridges + proxy | End of Phase 5 | `ptt-qa` | Header gating works; legacy path unchanged |
| QA — integration | Pre-Phase 7 | `qa-engineer` | E2E: login → admin → paypal webhook → bridge → clients-api |
| **SECURITY — full** | After QA, **before** Phase 7 traffic flip | `security-auditor` | New auth surface (forgot-password, reset-password), bridge shared-secret, Service Binding scopes, no token leaks, credential scan on every Worker pre-deploy |
| OPS verify | 24h post-cutover (Phase 8) | `operations-analyst` | Independent monitoring — different agent than cutover engineer |

**Hard gate**: Phase 7 (header flip to canary) cannot start without security-auditor sign-off receipt in portal.

---

## 4. Critical-Path Sequencing

**The critical path is Phase 0 → Phase 1 → Phase 3 → QA → SEC → Phase 7 → Phase 8 → Phase 9.**

Phase 2 + Phase 4 (payments-api) run alongside but are NOT on the critical path until Phase 5 needs the payments bridge contracts defined. Worst case: payments-api ships behind clients-api by 1 day without slipping cutover.

**Slippage risk concentrated in:**
1. **Phase 0** — if schema dump reveals undocumented columns or FKs, sprint stalls. Mitigation: Phase 0 takes 0.5 ed, fail-fast.
2. **Phase 5** — bridge contracts must be agreed BEFORE Phase 3+4 can stub their outbound calls. Mitigation: ptt-fullstack publishes contract markdown by end of Window B (Day 2).
3. **Phase 8** — 24h is non-compressible. Cleanup (Phase 9) gated on it.

---

## 5. Risk Callouts

| Risk | Sev | Mitigation |
|---|---|---|
| `admin-api` not folded → dual-writer drift returns | HIGH | CTO §1 mandate. wtt-FS confirms fold-in in Phase 3 receipt. |
| Hash divergence (PBKDF2 params) | HIGH | Phase 3 deliverable: `requireAuth()` byte-identical diff. wtt-qa verifies. |
| Bridge shared-secret leaks in git | CRIT | `pre-deploy-credential-scan` MANDATORY every Phase. Service Bindings preferred over shared-secret. |
| Data migration row-count mismatch | HIGH | Phase 6 deliverable: row counts before/after for all 5 tables. |
| Sessions forced re-login | MED | Tokens opaque, copy preserves. wtt-qa runs "existing session still valid" test. |
| Cutover-day emails sent prematurely | HIGH | Phase 10 strictly after Phase 8 GREEN. Aether holds the gate. |
| Local deploys / wrangler-pages misuse | HIGH | All deploys via `cf-deploy.py` (Pages) or `wrangler deploy` (Workers). Constitutional. |
| Worker secrets missing pre-deploy | MED | `wrangler secret put` BEFORE `wrangler deploy`. |
| 24h window cut short | MED | Aether holds the gate. ops-analyst reports hourly. |

---

## 6. Day-by-Day Calendar (3-Engineer Parallelism)

| Day | Active | Phase |
|---|---|---|
| **Day 1 (May 9)** | coder | P0 schema dumps — gate-zero closes EOD |
| **Day 2 (May 10)** | wtt-FS, coder | P1 + P2 parallel (repos + D1s) |
| **Day 3–5 (May 11–13)** | wtt-FS, coder, ptt-FS | P3 + P4 + P5 parallel (3-engineer max) |
| **Day 6 (May 14)** | wtt-qa, qa-eng, ptt-qa, security-auditor | QA → SEC sequential; sign-off EOD |
| **Day 7 (May 15)** | coder, ptt-FS | P6 data migration AM + P7 canary PM |
| **Day 8–9 (May 16–17)** | operations-analyst | P7 100% + P8 24h verify burn |
| **Day 10 (May 18)** | coder, human-liaison | P9 cleanup + P10 bulk resend (parallel) |

**Total: 10 calendar days**. Matches CTO 10.5 ed compressed via parallelism. One buffer day if Day 6 SEC surfaces blockers.

---

## 7. Status Reporting Cadence

- **After each phase**: receipt to portal — file at `exports/portal-files/tier3-phase{N}-receipt-YYYY-MM-DD.md` with: scope, files touched, deploy URLs, test evidence, gate status.
- **Daily 17:00 ET**: dept-systems-technology synthesis to Aether — one-line per phase, RAG status, blockers list.
- **Phase 8 (24h verify window)**: hourly status from operations-analyst. Format: `{timestamp} | login_success% | error_rate | bridge_success% | RAG`.
- **Cutover day (Phase 7)**: real-time portal updates. Aether on-deck. Jared notified at canary start, 50%, and 100%.
- **Customer-facing**: ZERO notifications until Phase 10 bulk resend. Constitutional.

---

## 8. Aether's Dispatch Order Recommendation

**Spawn 1 (Day 1, blocking):** `coder` — P0 schema dump. Gate-zero.

**Spawn 2–3 (Day 2, parallel cohort A — after P0 receipt):**
- `wtt-fullstack` — P1 clients-api stand-up
- `coder` (fresh) — P2 payments-api stand-up

**Spawn 4–6 (Day 3, parallel cohort B — after P1+P2 staging URLs live):**
- `wtt-fullstack` (continue) — P3 clients code migration + admin-api fold-in
- `coder` (continue) — P4 paypal-webhook port
- `ptt-fullstack` — P5 bridge APIs + portal-proxy header gate + agentmail/meetings/blog rebind

**Spawn 7–10 (Day 6, sequential gates after P3+P4+P5 receipts):**
- `wtt-qa` → `qa-engineer` → `ptt-qa` (parallel) → `security-auditor` (after all QA green)

**Spawn 11–12 (Day 7, after SEC sign-off):**
- `coder` (fresh) — P6 data migration
- `ptt-fullstack` (continue) — P7 canary → 100%

**Spawn 13 (Day 8, cutover):** `operations-analyst` — P8 24h verify. **Independent of P7 cutover engineer** (constitutional rule).

**Spawn 14–15 (Day 10, after P8 GREEN):**
- `coder` (fresh) — P9 cleanup (DROP tables, remove redundant Workers)
- `human-liaison` — P10 bulk credentials resend (batch 10 / 30s spacing)

**Aether personally holds the P8 → P9 gate** — DROP TABLE is irreversible without R2 restore.

---

## 9. DONE Summary

**Phase-by-phase specialists**:
P0=coder, P1=wtt-fullstack, P2=coder, P3=wtt-fullstack, P4=coder, P5=ptt-fullstack, P6=coder, P7=ptt-fullstack, P8=operations-analyst, P9=coder, P10=human-liaison.
QA=wtt-qa+qa-engineer+ptt-qa. SEC=security-auditor.

**Aether's dispatch order**: spawn coder for P0 first (gate-zero, blocking) → after receipt spawn wtt-fullstack (P1) + coder (P2) in parallel → after staging URLs spawn the 3-way Window C (wtt-FS P3 + coder P4 + ptt-FS P5) → QA fan-out → SEC → P6+P7 → ops-analyst P8 (24h hold) → P9 + P10 final pair.

**END dispatch plan.**
