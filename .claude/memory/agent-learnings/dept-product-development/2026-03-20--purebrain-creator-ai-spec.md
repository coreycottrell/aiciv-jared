# Memory: PureBrain Creator AI — Product Spec Complete

**Date**: 2026-03-20
**Agent**: dept-product-development
**Type**: teaching + synthesis
**Topic**: Full product spec for PureBrain Creator AI — Stanley-killer product for creator economy

---

## What Was Produced

Full PRD at: `/home/jared/projects/AI-CIV/aether/exports/departments/product-development/specs/2026-03-20--purebrain-creator-ai-spec.md`

24 user stories with acceptance criteria, 4-night sprint plan, data model, pricing strategy, competitive positioning, and key architecture decisions.

---

## Key Decisions Made

- **Domain**: `creator.purebrain.ai` (subdomain, not path)
- **Build approach**: Extend existing Witness containers / portal codebase — NOT a new app
- **Container model**: 1 Witness container per creator (matches existing isolation architecture)
- **Pricing**: Starter $97/mo | Growth $197/mo | Pro $297/mo — undercutting Stanley ($149) at entry

---

## Architecture Rationale (Most Important Lesson)

The fastest path to ship is reusing what is already proven:
- Birth pipeline live since 2026-03-14
- Multi-user data isolation shipped 2026-03-17
- Payment infrastructure (PayPal) already working
- Portal/FastAPI codebase battle-tested

Do NOT rebuild from scratch. The moat is speed + memory, not novelty of infrastructure.

---

## Competitive Positioning That Stuck

"Stanley knows what you posted. PureBrain knows who you ARE."

The memory moat is the whole game. Every competitor forgets. We compound.

---

## Pricing Logic

- $97 (Starter): Beat Stanley at entry point
- $197 (Growth): Where we make money — includes voice clone
- $297 (Pro): White-label is the key unlock

---

## Sprint Structure

- Night 1: Scaffold + creator onboarding + knowledge base upload
- Night 2: Content generation engine + Interview Me mode
- Night 3: Fan-facing public chat + lead capture
- Night 4: Analytics + QA + deploy

15-minute time-to-value target for creator onboarding is the key metric to hit.

---

## Risk to Watch

Creator content history import. Text paste should be primary recommended method.

---

## Files

- Spec: `/home/jared/projects/AI-CIV/aether/exports/departments/product-development/specs/2026-03-20--purebrain-creator-ai-spec.md`
- Google Drive: https://drive.google.com/drive/folders/1DM_JOptsxIkRVIfvGVWSIDqcybq4KfsU
