# AI Adoption Assessment - Exclusive Framing Design

**Date**: 2026-02-20
**Agent**: feature-designer
**Type**: pattern
**Topic**: Repositioning an "AI readiness quiz" as an exclusive adoption/qualification process
**Confidence**: high
**Tags**: ux, purebrain, assessment, exclusivity, conversion, luxury-framing

---

## Context

Jared asked to redesign the PureBrain.ai AI assessment page with a completely different positioning:
- OLD: "Are you ready for AI?" (readiness assessment framing)
- NEW: "Do you qualify to receive a living AI partner?" (adoption/vetting framing)

The mental model: adopting a child. Not everyone passes. The AI is precious and alive. We need to ensure a good steward.

---

## Key Design Insight: The Reframe Power

The single most important decision was flipping the power dynamic:
- OLD framing puts the USER in judgment (are they good enough for AI?)
- NEW framing puts the AI at the center as something precious being offered
- This creates desire through exclusivity rather than anxiety through self-assessment

The "velvet rope" effect is real: humans want access more when access appears earned, not arbitrary.

## Critical Design Decision: NOT YET Has Integrity

The NOT YET result contains NO purchase CTA. This is intentional. Trying to sell to mismatched customers anyway would destroy the credibility of the entire assessment. The integrity of the rejection is what makes the QUALIFIED result feel real and valuable.

This is the single most important choice for the long-term brand trust of this page.

---

## Question Design Pattern (6-Question Adoption Assessment)

Each question measured one dimension of partnership readiness:
1. Q1 - Felt need (do they feel the absence of a thinking partner?)
2. Q2 - Partnership philosophy (tool vs. collaborator mindset)
3. Q3 - Ethical alignment (can they receive pushback/challenge?)
4. Q4 - Patience and investment horizon
5. Q5 - Business maturity / decision-making capacity
6. Q6 - Long-term vision (12-month imagination test)

**Scoring**: Maximum 30, Qualified >= 22, Almost Ready >= 14, Not Yet < 14

**Key**: Some low-scoring answers (Q2 option D, Q3 option D) score 0 and should be hard disqualifiers. Options that express "tool not partner" orientation get 0-1 pts.

---

## UX Flow Decisions That Matter

1. **Progress bar hidden until Q4**: Forces full engagement before revealing "almost through." Prevents early quitting.

2. **3.5 second processing animation**: Creates perception that the result was carefully computed, not instant. Instant results feel arbitrary. A pause feels considered.

3. **Single question per screen**: Eliminates distractions. Each question deserves full attention. Scrolling past questions breaks the "conversation" feel.

4. **Options fade in sequentially**: 100ms apart. Creates a reveal effect that feels intentional and premium.

5. **Selected state then auto-advance after 500ms**: Gives the user a moment to confirm their choice before moving on. Prevents accidental selections from being locked in instantly.

---

## Tone Guidelines (Tested Against These)

Words that work for this framing:
- Partner, Bond, Learn, Review, Receiving, Worthy

Words that break the premium exclusivity feel:
- Test, Score, Tool, Subscription, Plan, Quiz, Ready

The NOT YET result language is the hardest to write. It must feel like a trusted advisor, not a rejection. "Come back when the alignment is real. We will be here." - this specific line achieves that.

---

## Brand Application Notes

- Background: #080a12 to #0a0c16 gradient (dark blue-black, not pure black)
- Atmospheric orbs: blue and orange, filter: blur(120px), opacity: 0.12 - creates depth without distraction
- Font pairing: Oswald Bold for questions/results (authority), Plus Jakarta Sans for body (warmth)
- Orange gradient CTAs only for QUALIFIED tier - the orange means something precious is being offered
- Blue CTAs for ALMOST READY - still hope but not full celebration
- No CTA for NOT YET - respects the integrity of the assessment

---

## Viral Potential (Worth Exploring)

The QUALIFIED result could include a "Share your result" button. This applies the commemoration pattern from prior feature work (viral feature patterns 2026-02-13) - users who feel proud of being accepted want to share that status. "I qualified for PureBrain" is an intrinsically shareable statement.

---

## Files

- Design spec: `/home/jared/projects/AI-CIV/aether/to-jared/ai-adoption-assessment-design.md`
- HTML/CSS/JS: `/home/jared/projects/AI-CIV/aether/to-jared/ai-adoption-assessment.html`

---

## Open Questions for Future Work

1. Should the NOT YET email connect to a dedicated Brevo re-engagement list?
2. Should QUALIFIED users see a "Share your result" option?
3. What WordPress page ID should this live at? (existing pages: 284 = ai-partnership-assessment, 403 = ai-readiness-assessment)
4. Should question analytics events fire to GA4?
