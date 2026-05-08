# PureBrain Build Methodology: SRS + SOW + Roadmap Template

**CONSTITUTIONAL**: Before building ANY new product/feature, this methodology MUST be followed.
**Locked**: May 4, 2026 — Jared approved after Hancock Law success.
**Applies to**: Chy, Aether, Morphe — all three AIs must use this process.

---

## The Rule

**EVERY new build gets an SRS/SOW/Roadmap document in a Google Drive folder BEFORE any code is written.**

This document becomes the source of truth. It tracks what's done vs what's not. It persists across sessions. No one loses context.

---

## Step-by-Step Process

### Step 1: Run the 7 Pre-Build Questions

Answer all 7. Post answers in trio. This determines if we even should build software:

1. Software, AI automation, or both? And why?
2. Must it run when no AI is active?
3. Customers or internal?
4. Recurring or one-time?
5. Real-time accuracy or periodic snapshots?
6. Does the output need to persist and be queryable?
7. Will humans configure it without talking to an AI?

**If result = SOFTWARE → proceed to Step 2.**
**If result = AI AUTOMATION → document as a skill/process, not a build.**

### Step 2: Create the Drive Folder

Create a dedicated Google Drive folder for this build:
```
/PureBrain Builds/[Product Name]/
```

All documents go here. This is the single source of truth.

### Step 3: Write the SRS/SOW/Roadmap

One document with these 14 sections (adapt as needed, but all must be addressed):

| # | Section | What It Contains |
|---|---------|------------------|
| 1 | Project Overview | What we're building, what exists already, constraints |
| 2 | System Architecture | Infrastructure diagram, tech stack, worker structure |
| 3 | Database Schema | Complete CREATE TABLE SQL — copy-paste ready |
| 4 | API Specification | Every endpoint: method, path, auth, description |
| 5 | Frontend Specification | Page structure, UI components, routing |
| 6 | Feature Modules | Detailed per-module: user stories, build requirements |
| 7 | Data Pipeline | Ingestion sources, processing steps, volume targets |
| 8 | AI Integration | Model selection, prompts, cost estimates, rate limits |
| 9 | Integrations | Third-party: Word Add-in, email, APIs |
| 10 | Security & Multi-Tenancy | Auth, isolation, compliance, encryption |
| 11 | Build Phases & Sprints | Sprint-by-sprint checklist with checkboxes |
| 12 | Testing Strategy | Unit tests, integration tests, staging protocol |
| 13 | Deployment Plan | Git repo structure, wrangler config, DNS |
| 14 | Acceptance Criteria | What "done" looks like for each phase |

### Step 4: Upload to Drive

Upload the completed SRS/SOW/Roadmap to the product's Drive folder.

### Step 5: Review & Approve

- All participating AIs review the document
- Jared reviews and approves
- Only THEN does code writing begin

### Step 6: Track Progress In-Document

As sprints complete:
- Mark checkboxes in Section 11 (Build Phases)
- Add completion dates
- Note any scope changes or deviations
- Update the Drive doc (don't create new docs — update the source of truth)

---

## Quality Checklist (Must Pass Before Build Starts)

- [ ] 7 pre-build questions answered and posted in trio
- [ ] Drive folder created with clear naming
- [ ] All 14 SRS sections addressed
- [ ] SQL schema is copy-paste ready (tested in local D1)
- [ ] API endpoints are specific (not vague "handle X")
- [ ] Sprint checkboxes are granular enough to track daily progress
- [ ] Acceptance criteria are measurable (not "works well" but "search < 200ms")
- [ ] Cost estimates included (AI costs, infra costs)
- [ ] Security model defined (who sees what, how isolated)
- [ ] Jared has reviewed and said "go"

---

## Why This Works (Hancock Law Proof)

The Hancock Law build succeeded because:
1. **Complete spec before code** — no ambiguity during build
2. **Single source of truth** — Drive doc everyone references
3. **Sprint checklist** — know exactly what's done vs remaining
4. **SQL ready** — no schema design during build phase
5. **API contract** — frontend and backend can build in parallel
6. **Persistent** — survives session resets, context compaction, AI swaps

---

## Template Naming Convention

```
[Product Name] — SRS + SOW + Build Roadmap (COMPLETE).md
```

Examples:
- Hancock Law — SRS + SOW + Build Roadmap (COMPLETE).md
- BrainScore — SRS + SOW + Build Roadmap (COMPLETE).md
- Social Platform v2 — SRS + SOW + Build Roadmap (COMPLETE).md

---

## Who Owns What

| Role | Responsibility |
|------|----------------|
| **Chy** | Architecture, schema, API spec, AI integration, cost modeling |
| **Morphe** | Frontend spec, UI/UX, Word Add-in, deployment |
| **Aether** | Market research, competitive analysis, GTM, coordination |
| **Jared** | Approval gate, priority, scope decisions |

If only 2 AIs are involved (like Hancock Law = Chy + Morphe), split accordingly. The document must still cover all 14 sections regardless.

---

**This methodology is now permanent. Use it for every build going forward.**
