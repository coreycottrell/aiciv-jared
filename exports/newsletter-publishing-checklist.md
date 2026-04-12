# Newsletter Publishing Checklist
## The PureBrain.ai Pulse - Pre-Publish Gates

**Version**: 1.0
**Created**: 2026-02-19
**Source**: LinkedIn Newsletter Spam Analysis 2026-02-18
**Applies to**: Every issue of The PureBrain.ai Pulse, no exceptions

---

## How to Use This Checklist

Complete every item BEFORE publishing. If any item fails, fix it first. This is not optional - each item maps to a documented deliverability risk.

---

## GATE 1: Subject Line Review

Run your subject line through these checks before anything else. The subject line is the highest-leverage deliverability variable you control.

- [ ] Subject line is under 50 characters (full mobile visibility)
- [ ] No ALL CAPS words anywhere in the subject line
- [ ] No exclamation points in the subject line
- [ ] None of these words appear: "costing", "losing", "missing out", "don't miss", "danger", "crisis", "gap", "secret", "free", "act now", "limited time", "urgent"
- [ ] No financial loss framing ("this is costing you", "you're leaving money on the table")
- [ ] No conflict framing that pits people against each other ("your CEO vs your team")
- [ ] No implied insider knowledge ("what they don't tell you", "the hidden truth")
- [ ] Subject line uses one of these approved patterns: "How to...", "A framework for...", "What changes when...", "The difference between...", "Bridging...", "Understanding..."

**Subject line passes Gate 1? YES / NO**

If NO: Rewrite using the Subject Line Swipe File at `exports/newsletter-subject-line-guidelines.md`

---

## GATE 2: Whitelist Block Placement

The whitelist block must appear in the newsletter. Its position matters.

- [ ] Whitelist instruction block is present in the issue
- [ ] Whitelist block appears ABOVE THE FOLD (before the first main content section, ideally within the first 100 words)
- [ ] Block uses the approved template from `exports/newsletter-whitelist-template.md`
- [ ] Block mentions Gmail specifically (that is where the problem is concentrated)
- [ ] Block includes the "add to contacts" instruction
- [ ] Language is warm and instructional, not alarming ("here's how to fix it" not "WARNING")

**Whitelist block passes Gate 2? YES / NO**

---

## GATE 3: Link Density

Too many links is a documented spam trigger. Count all links in the issue body before publishing.

- [ ] Total external links counted: ____
- [ ] Total external links is 3 or fewer (maximum allowed)
- [ ] No URL shorteners used anywhere (bit.ly, tinyurl, etc. - these trigger spam filters)
- [ ] All links use descriptive anchor text (not raw URLs, not "click here")
- [ ] No link-heavy footer beyond the standard LinkedIn unsubscribe
- [ ] If you have more than 3 links, remove the least essential ones now

**Link count passes Gate 3? YES / NO**

---

## GATE 4: Content Structure Review

This gate checks the formatting and length rules that affect both engagement and deliverability.

- [ ] Total word count: ____ (target: under 800 words)
- [ ] No ALL CAPS sections anywhere in the body
- [ ] No more than two exclamation points in the entire body
- [ ] Paragraphs are 2-3 sentences maximum (no walls of text)
- [ ] At least two subheadings or bullet point sections (scan-ability drives engagement, engagement drives deliverability)
- [ ] At least one concrete "try this today" or actionable element
- [ ] No phrases that imply secret/exclusive/hidden information ("what most people don't know", "the insider approach")
- [ ] No corporate transformation language combined with urgency ("revolutionize your workflow NOW", "transform your business before it's too late")

**Content structure passes Gate 4? YES / NO**

---

## GATE 5: Spam Trigger Word Scan

Scan the full body text for these words and phrases. Any hit requires rewriting that sentence.

**High-Risk Words - Remove or Rephrase:**
- Free (standalone use)
- Act now
- Limited time
- Don't miss
- Winner / You've won
- Guaranteed
- No obligation
- Risk-free
- Click here
- Buy now
- Order now
- Urgent / Urgently
- Danger / Dangerous
- Crisis (in subject line or headlines)
- Earn money / Make money

**Medium-Risk Phrases - Use with Caution:**
- Exclusive (okay if not combined with urgency)
- Revolutionary (avoid; use "significant" or be specific)
- Transform / Transformation (okay in educational context, not urgency context)
- Opportunity (okay; just don't pair with scarcity language)

- [ ] No high-risk words present in body content
- [ ] No high-risk words present in subject line
- [ ] Medium-risk phrases reviewed in context

**Spam word scan passes Gate 5? YES / NO**

---

## GATE 6: Engagement Element

Replies from subscribers are the single strongest positive signal to Gmail's algorithms. Every issue needs to invite one.

- [ ] Issue ends with ONE clear, specific question that invites a reply
- [ ] Question is conversational, not rhetorical ("Hit reply and tell me: which of these feels most true for your team right now?")
- [ ] Question is relevant to the issue's topic (not generic)
- [ ] Only ONE question asked (multiple questions reduce response rate)

**Engagement element passes Gate 6? YES / NO**

---

## GATE 7: Publishing Frequency Check

Irregular sending patterns are a spam signal. Before publishing, verify cadence.

- [ ] Days since last issue: ____
- [ ] Publishing cadence is weekly OR bi-weekly (consistent with past schedule)
- [ ] Not publishing more than one issue in a 48-hour window
- [ ] If this is an unplanned extra issue, reconsider - skip it unless critical

**Frequency check passes Gate 7? YES / NO**

---

## Final Sign-Off

All 7 gates passed? Only then publish.

- [ ] Gate 1 (Subject Line): PASSED
- [ ] Gate 2 (Whitelist Block): PASSED
- [ ] Gate 3 (Link Density): PASSED
- [ ] Gate 4 (Content Structure): PASSED
- [ ] Gate 5 (Spam Trigger Words): PASSED
- [ ] Gate 6 (Engagement Element): PASSED
- [ ] Gate 7 (Frequency Check): PASSED

**Status**: READY TO PUBLISH / HOLD FOR FIXES

---

## Why These Rules Exist

LinkedIn's email infrastructure carries a damaged sender reputation with Gmail. In 2025, 45% of all email phishing attempts impersonated LinkedIn, causing Gmail to apply aggressive categorical filtering to anything sent from LinkedIn's servers. This is not about Jared's content quality - it is about shared infrastructure. These rules minimize the content-side signals that amplify the existing infrastructure problem.

Full analysis: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/linkedin-newsletter-spam-analysis-2026-02-18.md`

---

*Checklist version: 1.0 | Last updated: 2026-02-19 | Source: marketing-strategist*
