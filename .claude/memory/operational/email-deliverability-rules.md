# Email Deliverability Rules - LOCKED IN

**Date**: 2026-02-19 (updated from 2026-02-17 initial version)
**Source**: LinkedIn Newsletter Spam Analysis (web-researcher, 2026-02-18) + Jared directive 2026-02-17
**Status**: PERMANENT RULE - Apply to ALL newsletters and blog content
**Full analysis**: `docs/from-telegram/linkedin-newsletter-spam-analysis-2026-02-18.md`

---

## Why These Rules Exist

LinkedIn's email infrastructure carries a damaged sender reputation with Gmail. 45% of all email phishing attempts in 2025 impersonated LinkedIn. Gmail moved from warnings to active rejection of suspicious messages in November 2025. These rules minimize the content-side signals that amplify LinkedIn's infrastructure problem.

This is not about Jared's content quality. It is about shared infrastructure reputation.

---

## RULE 1: Whitelist Block (MANDATORY - Every Issue)

Every LinkedIn newsletter issue MUST include this block ABOVE THE FOLD (before any content):

> "Gmail user? Quick fix: LinkedIn newsletters sometimes end up in spam or trigger a safety warning. This is a known issue with LinkedIn's email system, not specific to this newsletter. To fix it permanently: find this email, click the three dots in the top right, select 'Report not spam' or 'Looks safe,' then add newsletters-noreply@linkedin.com to your Gmail contacts. You'll only need to do this once."

Three template versions for different contexts: `exports/newsletter-whitelist-template.md`

---

## RULE 2: Subject Line Restrictions

Subject lines MUST NOT contain:
- Financial loss language: "costing", "losing", "missing out"
- Conflict framing: pitting CEO vs team, leadership vs employees
- Crisis language: "gap", "crisis", "danger" (in subject lines)
- Implied insider knowledge: "what they don't tell you", "the hidden truth"
- Scarcity urgency: "don't miss", "act now", "limited time"
- AI-as-threat framing combined with urgency
- ALL CAPS words
- Exclamation points
- More than 60 characters (50 preferred)

Subject lines SHOULD use:
- "How to...", "A framework for...", "What changes when..."
- "The difference between...", "Bridging...", "A closer look at..."
- "This week: [specific topic]"

Full swipe file: `exports/newsletter-subject-line-guidelines.md`

---

## RULE 3: Link Density

- Maximum 3 external links per newsletter issue
- No URL shorteners (bit.ly, tinyurl, etc.)
- Descriptive anchor text only (never raw URLs, never "click here")
- No link-heavy footers

---

## RULE 4: Spam Trigger Words

Remove these from all subject lines and body content:

**High-risk**: "Free" (standalone), "Act now", "Limited time", "Don't miss", "Guaranteed", "No obligation", "Risk-free", "Click here", "Buy now", "Urgent", "Danger", "Earn money", "Make money"

**Medium-risk** (use with care): "Revolutionary", "Transform/Transformation" (educational context okay, urgency context not okay), "Exclusive" (okay alone, not paired with scarcity)

---

## RULE 5: Content Structure

- Word count: under 800 words per issue
- Paragraphs: 2-3 sentences maximum
- No ALL CAPS sections in body
- Maximum two exclamation points total in body
- At least two subheadings or bullet sections
- At least one concrete actionable element
- No "secret/insider/hidden" framing

---

## RULE 6: Engagement Element (Required)

Every issue must end with ONE specific question inviting a reply:
> "Hit reply and tell me: [specific question]"

One question only. Replies signal to Gmail that subscribers want the email.

---

## RULE 7: Publishing Frequency

- Maintain weekly OR bi-weekly cadence consistently
- Never publish more than one issue in 48 hours
- Irregular sending spikes trigger spam algorithms

---

## Pre-Publish Checklist

Full 7-gate checklist: `exports/newsletter-publishing-checklist.md`

---

## Application

These rules apply to:
- LinkedIn Newsletters (The PureBrain.ai Pulse)
- Blog posts distributed via email
- Any email campaigns

These rules become less relevant if/when distribution migrates to an owned platform (Beehiiv + custom domain) where SPF/DKIM/DMARC is fully controlled.

---

*Initial version: 2026-02-17 | Expanded: 2026-02-19 | Source: marketing-strategist*
