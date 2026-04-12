# Memory: Migration Portal Quiz Integration Audit

**Date**: 2026-02-24
**Type**: synthesis
**Agent**: full-stack-developer
**Topic**: Migration portal audit — quiz integration strategy, live page gap analysis, 3-layer funnel approach

---

## What Was Built / What Was Found

### Live Portal State (https://purebrain.ai/migrate/)
- Portal UI (Steps 1-4) is deployed and functionally complete
- Client-side JSZip parsing is embedded in migration-portal.html
- Step 3 animation, Step 4 task cards are built
- Backend API routes (hub server migration.js) NOT verified as active
- Portal is unauthenticated/public — no auth gate
- No Brevo connection verified on the live page
- Quiz is NOT present at /migrate/ — portal wizard shows directly

### Quiz State (migration-exodus-quiz.html)
- Standalone 5-question component — fully built
- Captures: competitor, usage duration, use cases, frustration, business goal
- Has Brevo integration code in migration-brevo-integration.js
- Output schema matches the `exodus_data` the portal architecture needs for Step 4 personalization
- NOT deployed anywhere currently

---

## Key Architecture Decision

**3-Layer Funnel Approach:**

1. **Pre-purchase**: Quiz at /migrate/ captures email + competitor data → Brevo drip → convert to customer
2. **Post-purchase (no quiz data)**: Dashboard quiz nudge for customers who skipped exodus pages
3. **Inside portal**: Portal reads quiz exodus_data to personalize Step 1 (competitor upload card) and Step 4 (task cards)

---

## Critical Technical Gotcha

**Brevo API key must NOT be in client-side quiz HTML.**
Security review (S-09) flags this as P0. Need server-side proxy endpoint:
`POST /api/capture-migration-intent` on hub server → calls Brevo internally → returns success to client.

This is the same pattern as all other Brevo calls in the codebase.

---

## Data Flow (Quiz → Portal)

Quiz answer `competitor = chatgpt` → Brevo attribute `COMPETITOR = chatgpt`
→ On portal entry, fetch profile → pre-select ChatGPT upload card in Step 1
→ Quiz `main_frustration` → personalize portal banner copy
→ Quiz `primary_use_cases` → personalize Step 4 suggested task cards

The quiz captures EXACTLY the `exodus_data` schema defined in migration-portal-architecture.md Section F (Integration Plan).

---

## Priority Order

1. Deploy quiz at /migrate/ as entry gate (30 min)
2. Build server-side proxy for Brevo intent capture (2-3 hrs)
3. Wire quiz submit → proxy (1 hr)
4. Verify hub server migration API routes are active
5. Connect quiz data to portal Step 1 pre-selection
6. Dashboard quiz nudge for post-purchase customers
