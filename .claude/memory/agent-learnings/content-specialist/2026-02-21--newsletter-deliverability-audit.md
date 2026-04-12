# content-specialist Learning: Newsletter Deliverability Audit

**Date**: 2026-02-21
**Type**: operational + teaching
**Agent**: content-specialist

---

## Task Summary

Audited all 8 priority actions from the LinkedIn newsletter spam analysis (linkedin-newsletter-spam-analysis-2026-02-18.md) against:
- Current blog posts (posts 565, 480, 381 via WordPress REST API)
- Brevo welcome sequence draft (welcome-sequence-draft-2026-02-20.md)
- Existing newsletter/CTA infrastructure

---

## Key Findings

### Implementation Status Summary

| P# | Action | Status |
|----|--------|--------|
| P1 | Whitelist instruction in newsletter | NOT DONE |
| P2 | Subject line language fix | PARTIAL (Brevo mostly clean, Email 5 has risk, LinkedIn history problematic) |
| P3 | Standalone LinkedIn post | NOT DONE (copy written in audit) |
| P4 | Ask subscribers to add sender to contacts | NOT DONE |
| P5 | Limit links to 2-3 per issue | BLOG COMPLIANT (2 links per post), LinkedIn needs checklist |
| P6 | Reply-invitation question | PARTIAL (4/7 Brevo emails have it, LinkedIn inconsistent) |
| P7 | Beehiiv research | RESEARCHED but may be superseded by Brevo/Neural Feed |
| P8 | Custom domain newsletter | NOT DONE (needs DNS + Jared decision on P7 first) |

### Brevo Welcome Sequence Deliverability

Overall: STRONG - authentic voice, low link density, no spam trigger words.

Specific gaps:
- Email 1: No whitelist/contact-add instruction
- Email 5: Subject lines all contain "cost" or "paying" language (moderate spam risk)
- Emails 2, 4, 5: No reply invitation

### Blog Posts

Compliant with deliverability guidelines:
- 2 links per post (internal only)
- No URL shorteners
- Descriptive anchor text
- No spam trigger words in content (some urgency language in body copy acceptable for blog but should not be copied into email subjects)

---

## Patterns Worth Noting

### Email Subject Line Danger Words (from 2025 research)
- "costing you" / "paying" / "cost" = financial urgency signal
- "gap" / "danger" / "crisis" = conflict/threat framing
- AI topic + urgency = compound spam flag post-November 2025 Gmail enforcement
- Safe alternatives: "what changes when", "a framework for", "how to", specific time/date hooks

### Highest-Leverage Actions (3 things, biggest impact soonest)
1. Publish the LinkedIn post explaining the Gmail issue (Jared does it manually, 5 min)
2. Add whitelist instruction to next LinkedIn newsletter issue
3. Add reply-invitation P.S. to Brevo Emails 2, 4, and 5

### P7 (Beehiiv) Clarification
The Beehiiv research was done before the Brevo/Neural Feed welcome sequence was built. The question of whether we need Beehiiv is now whether Brevo covers the "owned list" need sufficiently. Brevo does not have newsletter-native audience discovery (Beehiiv network). This is a Jared decision, not an autonomous one.

---

## File Location

Full audit at: `/home/jared/projects/AI-CIV/aether/to-jared/newsletter-deliverability-audit.md`

Includes:
- Status for all 8 P-actions
- Ready-to-use copy for P1 (whitelist instruction), P3 (LinkedIn post), P4 (contact-add instruction), P6 (reply P.S. additions)
- Subject line rewrites for Email 5 (P2)
- LinkedIn subject line reframe guide (P2)
- Publishing checklist for link density compliance (P5)
- Agent assignment matrix for full implementation

---

## Memory Search Results Applied

- Applied `2026-02-20--blog-newsletter-deep-analysis.md`: Blog CTA patterns, link structure, voice patterns
- Applied `2026-02-21--blog-newsletter-forward-strategy.md`: FAQ status, content architecture context

---

**END MEMORY**
