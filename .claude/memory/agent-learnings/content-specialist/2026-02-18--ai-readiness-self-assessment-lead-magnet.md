# AI Readiness Self-Assessment - Lead Magnet (Full Version)

**Date**: 2026-02-18
**Type**: operational
**Agent**: content-specialist
**Topic**: Comprehensive 10-question scored AI readiness assessment for PureBrain.ai

---

## Task Summary

Created a production-ready HTML lead magnet for PureBrain.ai: a 10-question scored AI readiness self-assessment that fills the funnel gap between "blog reader" and "$79/mo subscriber."

## Output File

`/home/jared/projects/AI-CIV/aether/exports/lead-magnet/ai-readiness-assessment.html`

Note: This is a NEW file in a new directory (`lead-magnet/` vs the older `lead-magnets/`). The older version is at `exports/lead-magnets/ai-partnership-assessment-page.html` (5 questions, letter-choice format).

---

## Content Architecture

### Assessment Questions (10 scored, 1-5 scale)

| # | Dimension | What it measures |
|---|-----------|-----------------|
| 1 | AI Tool Usage | Regular vs occasional use |
| 2 | Data Readiness | CRM hygiene, structured records |
| 3 | Team AI Literacy | Who can use AI effectively |
| 4 | Process Documentation | SOPs, tribal knowledge risk |
| 5 | Leadership Commitment | Budget, time, willingness to change |
| 6 | Budget Allocation | Protected AI budget vs ad hoc |
| 7 | Integration Readiness | API-ready stack vs spreadsheets |
| 8 | Change Management | Track record of tools that actually stick |
| 9 | Success Metrics | Measurable KPIs defined |
| 10 | Partnership Mindset | Tool mindset vs partner mindset |

### Score Tiers

| Score | Tier | Persona |
|-------|------|---------|
| 10-20 | AI Tourist | Dabbling, not deploying |
| 21-30 | AI Experimenter | Started but lacks structure |
| 31-40 | AI Ready | Foundation in place |
| 41-50 | AI Partner Material | Ready for named partnership |

### CTA Strategy (Funnel Logic)

- **10-20 (Tourist)**: No primary CTA. Directs to newsletter (build literacy first). Honest framing: "Do the foundation work, then PureBrain will be ready for you."
- **21-30 (Experimenter)**: Soft primary CTA. "You're closer than you think." Offers PureBrain as a peek at what's possible.
- **31-40 (Ready)**: Strong primary CTA. "You're ready. The partnership starts here." Recommends Awakened ($79/mo).
- **41-50 (Partner Material)**: High-urgency primary CTA. Direct to start. Recommends starting with Awakened, then upgrading.

---

## Technical Architecture

### Key Interactive Features

1. **Live score counter** - Updates as each question is answered
2. **Sticky score widget** - Appears after 3 answers, shows running total, scroll-to-results button
3. **Progress bar** - Fills as questions answered (count-based, not score-based)
4. **Button enable gate** - Calculate button disabled until all 10 answered
5. **Animated score reveal** - Cubic ease-out animation counting up to score
6. **Score breakdown bars** - Animated bars per dimension, color-coded (gray/blue/orange)
7. **Tier card highlight** - The relevant tier card elevates with orange border
8. **Dynamic next steps** - Tier-specific 4-step action plans generated from TIER_DATA
9. **Email capture form** - Secondary CTA with success state (no page reload)
10. **Print/PDF styles** - @media print rule for PDF download use case

### Design Tokens (PureBrain 4.0 Standard)

```css
--blue:    #2a93c1
--orange:  #f1420b
--bg-dark: #0a0a1a
Fonts: Oswald (headings), Plus Jakarta Sans (body)
```

### Brand Patterns Applied

- Animated background orbs (orange top-left, blue bottom-right)
- Sticky nav with PureBrain logo + "Start My AI Partnership" CTA
- Orange numbered question badges
- Card-based questions with hover states
- Orange CTA button with glow effect

---

## Content Philosophy Applied

### Honest Positioning

The Tourist tier deliberately withholds the hard pitch. This is intentional - recommending PureBrain to someone who scores 15 would create buyer regret and churn. Instead, we direct them to the newsletter ("The Neural Feed") and give them real foundation work to do. This builds trust more than it loses sales.

### Voice Notes

- Direct, no fluff ("Be honest - a lower score isn't failure, it's a roadmap")
- CEO-level but accessible (no jargon, explains why each dimension matters)
- Slight edge/challenge tone ("10 Questions That Don't Lie")
- Each tier description is honest about the gap, not condescending

---

## Funnel Position

```
Blog reader
     |
     v
[Takes assessment]
     |
     v
Tourist (10-20) --> Newsletter signup --> Long nurture
Experimenter (21-30) --> Soft PureBrain intro --> Medium nurture
AI Ready (31-40) --> Strong PureBrain CTA --> Short nurture
Partner Material (41-50) --> Direct purchase CTA --> Immediate conversion
```

---

## Differences from Previous Lead Magnet (Feb 16 version)

The older version (`exports/lead-magnets/ai-partnership-assessment-page.html`) was:
- 5 questions (not 10)
- Letter-choice format (A/B/C/D, not 1-5 scale)
- Simpler scoring (no per-dimension breakdown)
- No tier-specific next steps
- No email capture block
- No sticky score widget

This new version is significantly more comprehensive and designed for the worksheet/guide use case as well as interactive use.

---

## Future Improvements

1. Connect email capture to actual Mailchimp/Klaviyo/ConvertKit list
2. Add Google Analytics events for each question answered and final tier reached
3. A/B test: Does showing the score in real-time increase or decrease completion?
4. PDF version: Could be generated via Puppeteer from the same HTML with print styles
5. WordPress embed: The form could be embedded as an iFrame on purebrain.ai blog posts

---

**Status**: Complete - file at `/home/jared/projects/AI-CIV/aether/exports/lead-magnet/ai-readiness-assessment.html`
