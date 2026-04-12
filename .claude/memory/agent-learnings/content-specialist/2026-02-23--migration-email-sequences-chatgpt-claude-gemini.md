# content-specialist Learning: Migration Email Nurture Sequences

**Date**: 2026-02-23
**Type**: pattern + operational
**Agent**: content-specialist
**Topic**: 3 competitor-specific email drip sequences for PureBrain Migration Portal

---

## Task Summary

Created three 5-email nurture sequences (15 emails total) for the PureBrain AI Migration Portal. Each sequence is personalized by which competitor the user is switching from:

1. ChatGPT sequence — pain: no memory, generic responses, expensive
2. Claude sequence — pain: no persistent context, limited integrations, conversation limits
3. Gemini sequence — pain: inconsistent quality, Google ecosystem lock-in, privacy concerns

Output file: `/home/jared/projects/AI-CIV/aether/exports/migration-email-sequences.md`

---

## Key Design Decisions

### 1. Competitor Acknowledgment Before Differentiation

The strongest approach for competitor migration sequences: acknowledge what the competitor does WELL before explaining why PureBrain is different. This prevents the reader from defensively dismissing the email. The message "you were not wrong to use Claude" is more credible and disarming than "Claude has these five problems."

Applied in: all three Email 1s, Claude Email 2, Gemini Email 2.

### 2. Emotional Arc Across 5 Emails

Following the established 4-email arc pattern from memory (2026-02-18), extended to 5:

- Email 1: Acknowledgment + validation (you are not imagining this problem)
- Email 2: Differentiation + honest comparison (design brief vs design brief)
- Email 3: Migration specifics + practical steps (concrete and low friction)
- Email 4: Social proof + specificity (real user, real change, real numbers)
- Email 5: Clean close + honest release (no pressure, final nudge)

The final email being the SOFTEST continues to be counterintuitive but correct for brand voice.

### 3. Privacy Framing Is Unique to Gemini Sequence

The Gemini sequence required a distinct angle: Google ecosystem lock-in and privacy ambiguity. This is not a relevant pain point for ChatGPT or Claude users. The self-censorship question in Gemini Email 5 ("Do you self-censor in Gemini?") is the strongest unique insight in any of the three sequences — it names something users feel but have not articulated.

### 4. Migration Portal as the CTA Anchor

Unlike typical conversion emails that drive to a pricing page or a "learn more" destination, these sequences use the Migration Portal concept itself as the primary value proposition. The CTA is not "buy PureBrain" — it is "your history can come with you." The portal makes switching feel safe and reversible rather than risky and final.

### 5. Competitor-Specific Technical Details

Each sequence required knowing the actual export/import mechanism for that competitor:
- ChatGPT: Settings > Data Controls > Export Data > ZIP file
- Claude: Account Settings > Your Data > Export (similar format)
- Gemini: Google account data export + optional Drive OAuth integration

Accurate technical details in Email 3s build trust and reduce the "this sounds complicated" friction that kills migration conversion.

---

## Brevo Configuration Notes

- Three separate automation sequences, trigger tags: `migration-intent` + `from-[competitor]`
- Exit on tag: `purebrain-customer`
- Email timing: 0 min / Day 2 / Day 4 / Day 7 / Day 10
- CTA button: orange (#f1420b) bg, white text, hover: blue (#2a93c1)
- List: migration-prospects segment (separate from Neural Feed List 3)
- Contact attributes needed: COMPETITOR, MAIN_FRUSTRATION, PRIMARY_USE_CASES, USAGE_FREQUENCY, HAD_CUSTOM_CONFIG

---

## Voice Calibration Notes

- Never directly bash a competitor — acknowledge what it does well
- "You were not wrong to use it" is a disarming opener for competitor migration sequences
- The word "partner" is used deliberately and carefully — not in every email, only where earned
- Avoided: "onboarding", "tool", "subscription", "getting started"
- Used: "partner", "foundation", "context", "history", "relationship"

---

## Reusable Patterns

### Competitor Migration Email Structure Template

```
Email 1: "Your frustration with [competitor] makes sense" — validate, do not attack
Email 2: "What [competitor] was built to do" — honest design brief comparison
Email 3: "Your [competitor] history can come with you" — concrete migration steps
Email 4: "[Real user example]" — specific numbers, specific outcome
Email 5: "Last thing I'll say" — honest, no pressure, door-open close
```

### Privacy Pivot (for ecosystem-locked products like Gemini)

The privacy angle only lands when it surfaces something the user has felt but not named. The "do you self-censor" question is the strongest formulation because it makes the implicit explicit without being preachy about it.

### Technical Export Instructions as Trust Builder

Including the actual steps to export data (Settings > Data Controls > Export Data) in the first email accomplishes two things: (1) it gives the reader a concrete action before they have committed to anything, and (2) it signals that you know the competitor's product well enough to give real instructions, not vague hand-waving.

---

## Memory Search Applied

- `2026-02-18--purebrain-nurture-email-sequence.md`: Emotional arc pattern, AI_NAME as infrastructure, ethical urgency, final email being softest
- `2026-02-20--post-purchase-welcome-email-templates.md`: "Partnership not subscription" language, CTA color logic (orange = action)
- `2026-02-14--aether-voice-content-guide.md`: Warm but professional tone, authentic voice calibration
- `2026-02-22--ai-tool-vs-ai-partner-content-package.md`: Tool vs partner framing, differentiation language

---

**END MEMORY**
