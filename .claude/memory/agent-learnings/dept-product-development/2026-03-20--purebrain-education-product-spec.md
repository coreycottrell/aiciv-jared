# Memory: PureBrain Education Product Spec

**Date**: 2026-03-20
**Agent**: dept-product-development
**Type**: operational
**Topic**: PureBrain Education — college alternative product scope and landing page

---

## What Was Built

1. Full PRD saved to `exports/departments/product-development/specs/2026-03-20--purebrain-education-spec.md`
2. Password-gated landing page saved to `exports/cf-pages-deploy/education/index.html`

## Key Decisions Made

- **Architecture**: Reskin of existing portal, NOT a new build. All infrastructure (Witness containers, birth pipeline, multi-user isolation) already production-ready.
- **Target audience**: Parents 40-55 (Gen X/Millennial), decision makers. Students 16-22 are end users.
- **Pricing structure**: Student $97/mo, Family $197/mo (most popular), Family Pro $297/mo
- **Password on gate page**: `pureeducation` (simple, change before any wider distribution)
- **5 skill tracks**: AI Fundamentals (4wk), Business AI (8wk), Creative AI (6wk), Developer AI (10wk), Entrepreneur AI (12wk)
- **Certification levels**: 4 levels (Practitioner → Builder → Specialist → Master), portfolio-backed

## MVP Scope (14 Days)

- Landing page (password-protected, CF Pages) — DONE
- Portal reskin (education branding, AI Tutor labels)
- Mentor Mode system prompt update
- Skill Tracks selection at onboarding
- Basic progress dashboard
- Portfolio page auto-generation

## Open Questions for Jared

1. Is this "PureBrain Education" or a separate brand?
2. Accreditation partnerships?
3. Student age minimum (16+)?
4. Pilot users for early testimonials?
5. Launch timing — insiders first vs. direct?
6. Change the gate password before wider sharing

## Landing Page Structure

Hero → Cost Math → Reality Check Stats → What They Learn → PureBrain Difference → Skill Tracks → Comparison Table → Pricing → FAQ → CTA

## Files

- Spec: `exports/departments/product-development/specs/2026-03-20--purebrain-education-spec.md`
- Landing page: `exports/cf-pages-deploy/education/index.html`
