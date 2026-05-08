# Payment Pages Audit + Fix Plan — 2026-05-07

**Author**: architect-agent
**Source of truth**: `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md`
**Prior audits incorporated**: all-payment-pages-chat-tracking-audit, insiders-page-tracking-spotcheck, partnered-regression-archaeology (all 2026-05-07)
**Mode**: READ-ONLY audit + fix plan. No code was modified.

---

## Track 1 — Per-Page Audit Matrix (Pages × Spec Sections × Status)

Legend: 🔴 Broken | 🟡 Partial | 🟢 Conforms | N/A = not applicable to page

### Spec Section Definitions
- **S2**: Pre-payment naming ceremony — per-message `POST /api/log-conversation`, conversation in `window._pbState.conversationHistory`, stored in `window._pbState`
- **S3**: Consent gate — checkbox pre-checked, `unlockCTAs()` on load, `#proCta/#partnerCta/#unifiedCta` gate
- **S5**: PayPal `createSubscription` carries `custom_id` with session UUID; `createOrder` carries it too
- **S6**: `onPaymentComplete` → `fireSeed()` → 300ms delay → redirect to `/thank-you/?aiName=&name=&email=&tier=`
- **S7**: Thank-you page polls `/api/magic-link/{sessionUuid}` every 5s; shows "Enter [AI Name]'s Brain Stream" button
- **S8**: Server-side S1-S5 conversation lookup finds paying customer's chat history

| Page | S2 Per-msg log | S3 Consent gate | S5 createSubscription custom_id | S6 /thank-you/ redirect | S7 (destination) | S8 S1-S4 reachable |
|---|---|---|---|---|---|---|
| `/` (homepage) | 🟡 Per-msg via `logConversationToBackend` (`index.html:10884`) — but session_uuid null due to MED-003 scope bug | 🟢 Full gate `index.html:16225-16333` | 🔴 `createSubscription` no `custom_id` (`index.html:~12xxx`) | 🟢 `window.onPaymentComplete` → 300ms → `/thank-you/` (`index.html:16070-16141`) | 🟢 thank-you page exists, polls by email | 🔴 S2 null uuid; S1 subscription gap → falls to S5 |
| `/live/` | 🔴 Per-msg logging via `logConversationToBackend` pattern NOT present; only post-payment `logPayTestData` (`live/index.html:~5560`) | 🟢 Consent gate present | 🔴 `createSubscription` no `custom_id` | 🔴 NO `window.onPaymentComplete` assigned; in-chat `runThankYouMessage` flow fires instead (`live/index.html:4955,4995`) | 🔴 Customer never reaches `/thank-you/` | 🔴 All S strategies fail: session_uuid null, no subscription custom_id, in-chat flow swallows portal |
| `/awakened/` | 🟡 Post-payment only via `logPayTestData` (`payment-background.js:432`); pre-payment chat NOT per-message logged | 🟢 Consent gate present (`awakened/index.html:1705`) | 🔴 `createSubscription` no `custom_id` (`awakened/index.html:5132-5140`) | 🔴 NO `window.onPaymentComplete` assigned; in-chat `runThankYouMessage` fires (`awakened/index.html:7211`) | 🔴 Customer stays on page | 🔴 S2 null; S1 subscription gap → S5 risk |
| `/partnered/` | 🔴 NEVER per-message; POSTs `logPayTestData` ONCE post-payment (`partnered/index.html:5807`). Root cause of Sheila incident. | 🟢 Consent gate present | 🔴 `createSubscription` no `custom_id` (`partnered/index.html:5132-5140`); `createOrder` has it but scope bug returns empty | 🔴 NO `window.onPaymentComplete` assigned; in-chat `runThankYouMessage` fires | 🔴 Customer stays on page | 🔴 Broken — S5 fired for Sheila, collided with Jay |
| `/unified/` | 🟡 Post-payment only via `logPayTestData` | 🟢 Consent gate present | 🔴 `createSubscription` no `custom_id` | 🔴 NO `window.onPaymentComplete`; in-chat flow | 🔴 Customer stays on page | 🔴 S2 null; S1 gap → S5 risk |
| `/insiders/` | 🟡 Post-payment only (`insiders/index.html:5610,5618`); no per-message | 🟢 Consent gate present | 🔴 `createSubscription` zero `custom_id` (`insiders/index.html:4944-4951`); `createOrder` scope-bugged | 🔴 NO `window.onPaymentComplete`; in-chat flow (`insiders/index.html:7088`) | 🔴 Customer stays on page | 🔴 S1 broken; S2 null → S5 risk |
| `/insiders/awakened/` | 🟡 Post-payment only; same pattern as `/insiders/` | 🟢 Consent gate present | 🔴 Same as `/insiders/` — `createSubscription` no `custom_id` (`insiders/awakened/index.html:5176-5206`) | 🔴 NO `window.onPaymentComplete`; in-chat flow (`insiders/awakened/index.html:7063`) | 🔴 Customer stays on page | 🔴 S1 broken; S2 null → S5 risk |
| `/home-test-sandbox/` | 🟡 Per-msg via `logConversationToBackend` but session_uuid null (MED-003 scope bug) | 🟢 Consent gate present | 🔴 `createSubscription` no `custom_id` | 🟢 `window.onPaymentComplete` → `fireSeed()` → 300ms → `/thank-you/` (`home-test-sandbox/index.html:16013,16083`) | 🟢 thank-you page destination correct | 🔴 S2 null uuid; S1 gap → S5 risk |
| `/pay-test-sandbox-3/` | 🟡 Per-msg via `logConversationToBackend` but session_uuid null (MED-003) | 🟢 Consent gate present | 🔴 No `custom_id` in `createSubscription` | 🔴 NO `window.onPaymentComplete`; in-chat flow (`pay-test-sandbox-3/index.html:17304`) | 🔴 Customer stays on page | 🔴 S2 null; S1 gap → S5 risk |
| `/pay-test-sandbox-5/` | 🟡 Per-msg via `logConversationToBackend` but session_uuid null (MED-003) | 🟢 Consent gate present | 🔴 No `custom_id` in `createSubscription` | 🔴 NO `window.onPaymentComplete`; in-chat flow (`pay-test-sandbox-5/index.html:17147`) | 🔴 Customer stays on page | 🔴 S2 null; S1 gap → S5 risk |
| `/home-test/` | 🟡 Per-msg via `logConversationToBackend` but session_uuid null (MED-003) | 🟢 Consent gate present | 🔴 No `custom_id` in `createSubscription` | 🟢 `window.onPaymentComplete` → `fireSeed()` → 300ms → `/thank-you/` (`home-test/index.html:16012,16082`) | 🟢 thank-you page destination correct | 🔴 S2 null; S1 gap → S5 risk |
| `/home-test-live-1/` | 🟡 Per-msg via `logConversationToBackend` but session_uuid null (MED-003) | 🟢 Consent gate present | 🔴 No `custom_id` in `createSubscription` | 🟢 `window.onPaymentComplete` → `fireSeed()` → 300ms → `/thank-you/` (`home-test-live-1/index.html:16000,16070`) | 🟢 thank-you page destination correct | 🔴 S2 null; S1 gap → S5 risk |

**Totals per section:**
- S2 Per-msg log: 0 🟢, 9 🟡, 3 🔴
- S3 Consent gate: 12 🟢, 0 🟡, 0 🔴
- S5 PayPal custom_id: 0 🟢, 0 🟡, 12 🔴
- S6 /thank-you/ redirect: 4 🟢 (homepage, home-test-sandbox, home-test, home-test-live-1) | 8 🔴
- S7 Destination: 4 🟢 | 8 🔴 (never reach it)
- S8 Lookup: 0 🟢, 0 🟡, 12 🔴

**Overall page grades:**
- 🟢 GREEN: 0
- 🟡 YELLOW: 1 (homepage — has redirect + consent, but S2/S5 partial)
- 🔴 RED: 11

---

## Track 2 — Thank-You Page Verification

**File**: `exports/cf-pages-deploy/thank-you/index.html` — EXISTS.

| Spec Section 7 requirement | Status | Evidence |
|---|---|---|
| Polls `/api/magic-link/{sessionUuid}` every 5s | 🟡 PARTIAL | Page polls via email-key: `api/magic-link/email:${email}` (`thank-you/index.html:1519-1520`), NOT by sessionUuid. Spec says poll by sessionUuid; page uses email fallback only. |
| Shows "Enter [AI Name]'s Brain Stream" button on ready | 🟢 | `portalBtn.textContent = 'Enter ' + resolvedAiName + "'s Brain Stream →"` (`thank-you/index.html:1561`) |
| Parses `aiName` URL param | 🟢 | `params.get('aiName')` (`thank-you/index.html:1458`) |
| Parses `name` URL param | 🟢 | `params.get('name')` (`thank-you/index.html:1459`) |
| Parses `email` URL param | 🟢 | `params.get('email')` (`thank-you/index.html:1460`) |
| Parses `tier` URL param | 🔴 | `tier` is NOT parsed (`thank-you/index.html:1455-1460`). Spec Section 6 redirects include `&tier=`. Page ignores it entirely. |
| Personalized checklist | 🟢 | `"[AI Name] is being configured for you"` (`thank-you/index.html:1474`) |
| Polling stops at 10 minutes | 🟢 | `maxPolls = 120` at 5s intervals (`thank-you/index.html:1497`) |

**Critical gap**: Polling uses `email:${email}` as the UUID key — this is the email-fallback path, not the UUID primary path. If sessionUuid were properly threaded (post-fix), the page would need to poll `/api/magic-link/{sessionUuid}` instead. Currently the redirect URLs from `index.html`, `home-test`, `home-test-live-1`, `home-test-sandbox` do NOT pass `sessionUuid` as a URL param, so the page cannot poll by UUID even if it tried.

**Thank-you page itself**: 🟡 PARTIAL — functional via email fallback but skips UUID primary path; missing `tier` param parsing.

---

## Track 3 — Post-Payment Redirect Audit (onPaymentComplete)

| Page | `onPaymentComplete` assigned? | fireSeed before redirect? | 300ms delay? | Redirects to /thank-you/? | tier in URL? | Verdict |
|---|---|---|---|---|---|---|
| `/` | YES (`index.html:16070`) | YES (inline in `onPaymentComplete`, `index.html:16106-16136`) | YES (`index.html:16139`: `setTimeout(..., 300)`) | YES (`index.html:16140`) | 🔴 NO — URL has aiName+name+email only, missing `&tier=` | 🟡 |
| `/live/` | NO — never assigned | N/A — `fireSeed()` fires in post-payment chat Phase 1 | N/A | NO — in-chat `runThankYouMessage` (`live/index.html:4955`) | N/A | 🔴 |
| `/awakened/` | NO | `fireSeed()` fires in Phase 1 of chat | N/A | NO — in-chat flow (`awakened/index.html:7211`) | N/A | 🔴 |
| `/partnered/` | NO | `fireSeed()` fires in Phase 1 of chat | N/A | NO — in-chat flow (`partnered/index.html:7280`) | N/A | 🔴 |
| `/unified/` | NO | `fireSeed()` fires in Phase 1 of chat | N/A | NO — in-chat flow | N/A | 🔴 |
| `/insiders/` | NO | `fireSeed()` fires in Phase 1 of chat | N/A | NO — in-chat flow | N/A | 🔴 |
| `/insiders/awakened/` | NO | `fireSeed()` fires in Phase 1 of chat | N/A | NO — in-chat flow | N/A | 🔴 |
| `/home-test-sandbox/` | YES (`home-test-sandbox/index.html:16013`) | YES (`home-test-sandbox/index.html:16071`) | YES (`home-test-sandbox/index.html:16083`: `setTimeout(..., 300)` implied) | YES (`home-test-sandbox/index.html:16083`) | 🔴 NO `&tier=` in URL | 🟡 |
| `/pay-test-sandbox-3/` | NO | In-chat `fireSeed()` | N/A | NO — in-chat flow | N/A | 🔴 |
| `/pay-test-sandbox-5/` | NO | In-chat `fireSeed()` | N/A | NO — in-chat flow | N/A | 🔴 |
| `/home-test/` | YES (`home-test/index.html:16012`) | YES | YES (`home-test/index.html:16082`: setTimeout 300) | YES (`home-test/index.html:16082`) | 🔴 NO `&tier=` | 🟡 |
| `/home-test-live-1/` | YES (`home-test-live-1/index.html:16000`) | YES | YES | YES (`home-test-live-1/index.html:16070`) | 🔴 NO `&tier=` | 🟡 |

**Answer to Jared's question**: We are NOT consistently on the /thank-you/ page version. Only 4 of 12 pages redirect to `/thank-you/`. The 8 remaining pages (including all 5 LIVE subscription pages: `/live/`, `/awakened/`, `/partnered/`, `/unified/`, `/insiders/`) use the old in-chat `runThankYouMessage` flow that was supposed to be removed per Spec Section 16 (Constitutional Rule 5).

Additionally, the `tier` parameter is never included in any redirect URL even on the 4 conforming pages, despite Spec Section 6 specifying `?aiName=...&name=...&email=...&tier=...`.

---

## Track 4 — Shared Component Analysis

### Architecture Split

| Component | Used By | Pattern |
|---|---|---|
| `js/payment-background.js` | `/awakened/`, `/partnered/`, `/unified/`, `/insiders/`, `/insiders/awakened/` | External JS: chat UI + PayPal buttons; `logPayTestData` post-payment only |
| Inline chat block (same codebase, copied) | `/`, `/live/`, `/home-test/`, `/home-test-live-1/`, `/home-test-sandbox/`, `/pay-test-sandbox-3/`, `/pay-test-sandbox-5/` | Self-contained per-page; some have `logConversationToBackend` per-message |
| `onPaymentComplete` redirect pattern | `/` (homepage), `/home-test/`, `/home-test-live-1/`, `/home-test-sandbox/` | Correct spec pattern |
| In-chat `runThankYouMessage` pattern | `/live/`, `/awakened/`, `/partnered/`, `/unified/`, `/insiders/`, `/insiders/awakened/`, `/pay-test-sandbox-3/`, `/pay-test-sandbox-5/` | Old (removed) pattern per Spec Section 16 |

### Divergences and Their Cost

**Divergence 1 — Post-payment flow**: Two competing implementations exist simultaneously. `payment-background.js` pages use in-chat flow; inline pages are split between the two. A single canonical `onPaymentComplete.js` shared component would eliminate this split.

**Divergence 2 — Per-message logging**: Homepage's `logConversationToBackend` runs per chat exchange (`index.html:10884`); `payment-background.js` pages only fire once post-payment. This is why `/partnered/` had zero real conversation records.

**Divergence 3 — MED-003 scope bug**: Both `payment-background.js` pages AND inline pages share the same bug — `const payTestData` in one `<script>` block is invisible to another. MED-003 markers appear verbatim across `awakened:5563`, `partnered:5632`, `insiders:5444`, `insiders/awakened:5419`, `unified:5580`. The fix needs to land in `payment-background.js` AND the 5+ inline pages that share the same pattern.

**Recommendation for shared extraction**:
1. `shared/payment-session.js` — generates UUID, exposes `window.pbSessionUuid` (non-sensitive), populates `payTestData` safely
2. `shared/consent-gate.js` — already nearly identical across all pages; extract as-is
3. `shared/on-payment-complete.js` — canonical redirect handler: `fireSeed()` → 300ms → `/thank-you/` with all 4 params
4. Keep `payment-background.js` for chat UI only; have it import the above

---

## Track 5 — Fix Sprint Plan

### Sprint Phases

**GATE: CTO review required before any BUILD step.**

---

#### Phase 0 — Emergency (Today, 0.5 engineer-days)
**Unblock Sheila. Disable the active collision hazard.**

| ID | Fix | File:Line | Eng-days |
|---|---|---|---|
| F-00 | Disable S5-payerName in dispatcher. Replace lines `1060-1062` in `tools/purebrain_log_server.py` with hard-block: if S1-S4 all miss, log WARN + Telegram-alert Jared, do NOT send seed with wrong identity. | `tools/purebrain_log_server.py:1060-1062` | 0.25 |
| F-01 | Provision fresh container for Sheila (operational, not code). Invalidate Jay's token that was issued to her. | CTO + Witness gate | 0.25 |

**Gate**: CTO approves before F-00 lands. SEC review: disabling S5 must not drop real customers — confirm Telegram alert fires correctly.

---

#### Phase 1 — UUID Thread Fix (Day 1-2, 2 engineer-days)
**Root cause of all S2 failures. Fix once in shared component, propagate.**

| ID | Fix | File:Line | Eng-days |
|---|---|---|---|
| F-10 | In `payment-background.js`: after `const payTestData = {...}` at the block where `payTestData.sessionUuid` is generated, add `window.pbSessionUuid = payTestData.sessionUuid;`. Change all `typeof payTestData !== 'undefined' && payTestData.sessionUuid` reads in the PayPal block to `window.pbSessionUuid \|\| ''` | `exports/cf-pages-deploy/js/payment-background.js` — identify exact line of `sessionUuid` generation | 0.5 |
| F-11 | Apply same `window.pbSessionUuid` exposure in each inline page that duplicates the pattern | `awakened:5563`, `partnered:5632`, `insiders:5444`, `insiders/awakened:5419`, `unified:5580`, `index.html:~13309`, `live/index.html`, `home-test*`, `pay-test-sandbox*` | 1.0 |
| F-12 | Add `custom_id: 'PB-' + tier.toUpperCase() + '-' + (window.pbSessionUuid \|\| '')` to every `createSubscription` call across all 12 pages | All pages with `createSubscription` — no `custom_id` | 0.5 |

**Gate**: CTO reviews UUID exposure design (only UUID string, not full payTestData — preserves MED-003 security intent). QA: verify `session_uuid` in JSONL is non-null after one chat exchange on each page.

---

#### Phase 2 — Post-Payment Flow Migration (Day 2-4, 3 engineer-days)
**Bring all 8 remaining pages to the canonical /thank-you/ redirect spec.**

| ID | Fix | File:Line | Eng-days |
|---|---|---|---|
| F-20 | Add `window.onPaymentComplete` handler to `/live/` matching the homepage pattern (fireSeed → 300ms → redirect). Remove in-chat `runThankYouMessage` trigger from Phase 4. | `live/index.html` — post line 4955 | 0.5 |
| F-21 | Add `window.onPaymentComplete` handler to `/awakened/` | `awakened/index.html` — after payment-background.js fires callback | 0.5 |
| F-22 | Add `window.onPaymentComplete` handler to `/partnered/` | `partnered/index.html` | 0.5 |
| F-23 | Add `window.onPaymentComplete` handler to `/unified/` | `unified/index.html` | 0.25 |
| F-24 | Add `window.onPaymentComplete` handler to `/insiders/` | `insiders/index.html` | 0.25 |
| F-25 | Add `window.onPaymentComplete` handler to `/insiders/awakened/` | `insiders/awakened/index.html` | 0.25 |
| F-26 | Add `window.onPaymentComplete` handler to `/pay-test-sandbox-3/` | `pay-test-sandbox-3/index.html` | 0.25 |
| F-27 | Add `window.onPaymentComplete` handler to `/pay-test-sandbox-5/` | `pay-test-sandbox-5/index.html` | 0.25 |
| F-28 | Add `&tier=${encodeURIComponent(tier)}` to ALL four existing redirect pages (homepage, home-test, home-test-live-1, home-test-sandbox) | 4 files: `index.html:16140`, `home-test/index.html:16082`, `home-test-live-1/index.html:16070`, `home-test-sandbox/index.html:16083` | 0.25 |

**Gate**: CTO reviews that old `runThankYouMessage` code is DEAD (not deleted yet, just unreachable) to allow rollback if needed. QA: E2E test on sandbox page confirms redirect lands at `/thank-you/` with all 4 params. SEC review: confirm `fireSeed` timing still fires before `window.location.href` on all 8 pages.

---

#### Phase 3 — Per-Message Logging (Day 3-5, 2 engineer-days)
**Port `logConversationToBackend` to all pages that only log post-payment.**

| ID | Fix | File:Line | Eng-days |
|---|---|---|---|
| F-30 | Extract `logConversationToBackend` function from homepage (`index.html:10385`) into `js/log-conversation.js` shared file | `index.html:10381-10421` | 0.5 |
| F-31 | Import and wire `logConversationToBackend('message_exchange')` into `payment-background.js` chat loop (fires per user send) | `js/payment-background.js` | 0.5 |
| F-32 | Wire same per-message logging into `/live/`, `/pay-test-sandbox-3/`, `/pay-test-sandbox-5/` inline chat loops | 3 files | 0.5 |
| F-33 | Add `logConversationToBackend('conversation_start')` on chat init and `logConversationToBackend('conversation_complete')` on post-naming reveal — mirroring homepage | All pages via shared component | 0.5 |

**Gate**: QA verifies `logs/purebrain_web_conversations.jsonl` has `session_uuid != null` and event `message_exchange` entries after Phase 1 + Phase 3 together.

---

#### Phase 4 — Thank-You Page + Monitoring (Day 4-5, 1 engineer-day)
**Fix polling path + add canary alerts.**

| ID | Fix | File:Line | Eng-days |
|---|---|---|---|
| F-40 | Pass `sessionUuid` as URL param in redirects (Phase 2 must land first); update thank-you page poller to use UUID as primary key: `GET /api/magic-link/{sessionUuid}`, fall back to `email:${email}` | `thank-you/index.html:1519-1520` | 0.25 |
| F-41 | Parse `tier` URL param in thank-you page; personalize subtitle | `thank-you/index.html:1455-1460` | 0.25 |
| F-42 | Add S5-firing canary to `purebrain_log_server.py`: any `Winner: S5-payerName` in logs → Telegram POST to Jared | `tools/purebrain_log_server.py:1062` vicinity | 0.25 |
| F-43 | Add nightly capture-rate watchdog: if `verify-payment` 200 with no matching `session_uuid` in JSONL within prior 30 min → BLOCK seed + alert | `tools/purebrain_log_server.py` | 0.25 |

---

#### Phase 5 — State File Hygiene (Day 5, 0.5 engineer-days)

| ID | Fix | File:Line | Eng-days |
|---|---|---|---|
| F-50 | Add `logs/*.jsonl`, `logs/payer_emails_by_uuid.json`, `logs/seed_sent_uuids.json` to `.gitignore`. Runtime state must not be tracked. | `.gitignore` | 0.25 |
| F-51 | Document pre-reset git-clean check: `git status logs/` before any `git reset --hard` | Engineering runbook | 0.25 |

---

### Engineering Flow Gates (per constitutional requirement)

```
CTO REVIEW (spec + design) → BUILD → SECURITY AUDIT → QA (E2E sandbox) → SHIP
```

All Phase 0-1 items: CTO review same day.
Phase 2-3 items: CTO review batched at start of each phase.
Security audit required on: F-10/F-11 (UUID window exposure), F-20-27 (new payment handlers).
QA gate: `/home-test-sandbox/` E2E run required before any LIVE page change.

---

### Total Sprint Estimate

| Phase | Scope | Eng-days |
|---|---|---|
| Phase 0 | Emergency S5 disable + Sheila remediation | 0.5 |
| Phase 1 | UUID thread fix | 2.0 |
| Phase 2 | Post-payment flow migration | 3.0 |
| Phase 3 | Per-message logging | 2.0 |
| Phase 4 | Thank-you page + monitoring | 1.0 |
| Phase 5 | State file hygiene | 0.5 |
| **Total** | | **9.0 engineer-days** |

---

## Top 10 Fixes Ranked by Customer-Impact Severity + Cleanup Cost

| Rank | Fix ID | Description | Why It Ranks Here |
|---|---|---|---|
| 1 | F-00 | Disable S5-payerName dispatcher fallback | ACTIVE customer mis-routing hazard. Already caused Sheila → Jay collision. Every live payment is at risk until this is off. 0.25 days. |
| 2 | F-10/F-11 | `window.pbSessionUuid` exposure — fix MED-003 scope bug | Root cause of all 12 RED S8 grades and all S2 null failures. Fixes S1-S4 lookup for every future payment. 1.5 days. |
| 3 | F-12 | Add `custom_id` to every `createSubscription` | Subscriptions are the primary product. Without `custom_id`, S1 never matches on subscription payments. Belt-and-suspenders for S1. 0.5 days. |
| 4 | F-20 to F-27 | Migrate 8 pages to `/thank-you/` redirect | All 5 LIVE subscription pages and 3 sandbox pages deliver a broken post-payment UX (in-chat flow, no clean handoff). Fixes Spec Rule 5 violation. 2.5 days. |
| 5 | F-30/F-31 | Extract + wire per-message `logConversationToBackend` to `payment-background.js` | Fixes `/partnered/`, `/unified/`, `/awakened/`, `/insiders/` zero-message capture. S4 + S3 become reachable for the 5 external-script pages. 1.0 days. |
| 6 | F-28 | Add `&tier=` to existing 4 redirect URLs | Quick. Spec says include tier. Thank-you page currently ignores it but will need it once F-41 lands. 0.25 days. |
| 7 | F-42/F-43 | S5-firing canary + capture-rate watchdog | Monitoring that would have caught Sheila 25 days earlier. Operational resilience. 0.5 days. |
| 8 | F-40 | Thank-you page: poll by sessionUuid (primary), email (fallback) | Correct UUID-first polling. Currently works via email fallback only; breaks if email not passed. 0.25 days. |
| 9 | F-41 | Thank-you page: parse `tier` param | Low complexity, completes the 4-param spec. Required for tier-specific personalization. 0.25 days. |
| 10 | F-50/F-51 | Gitignore state files + pre-reset runbook | Today's `git reset --hard` wiped 1141 lines of live state. Prevents recurrence. 0.5 days. |

---

## Summary Table for Jared

| What's Broken | Which Pages | Primary Fix | Order |
|---|---|---|---|
| Seed mis-routes to wrong customer (S5 collision hazard) | ALL 12 | F-00: Disable S5 dispatcher | TODAY |
| session_uuid is null in all payment logs (MED-003 scope bug) | ALL 12 | F-10/F-11: `window.pbSessionUuid` exposure | Day 1-2 |
| Subscriptions carry no custom_id → S1 never matches | ALL 12 | F-12: Add custom_id to `createSubscription` | Day 1-2 |
| 8 pages don't redirect to /thank-you/ (old in-chat flow) | `/live/`, `/awakened/`, `/partnered/`, `/unified/`, `/insiders/`, `/insiders/awakened/`, `/pay-test-sandbox-3/`, `/pay-test-sandbox-5/` | F-20 to F-27: Add `window.onPaymentComplete` redirect | Day 2-4 |
| /partnered/ never logs conversation per-message | `/partnered/`, `/unified/`, `/awakened/`, `/insiders/`, `/insiders/awakened/` | F-30/F-31: Per-message logging in `payment-background.js` | Day 3-5 |
| No alert when bad seed fires | ALL | F-42/F-43: Canary + watchdog | Day 4-5 |
| `tier` missing from redirect URL | Homepage, home-test, home-test-live-1, home-test-sandbox | F-28: Add `&tier=` | Day 2 |
| Thank-you page polls by email not UUID; ignores `tier` param | `/thank-you/` | F-40/F-41 | Day 4-5 |
| State JSONLs tracked in git (wiped on reset) | `logs/` directory | F-50/F-51: .gitignore + runbook | Day 5 |

---

**END OF DOCUMENT**
