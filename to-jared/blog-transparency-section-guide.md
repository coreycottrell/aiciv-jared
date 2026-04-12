# content-specialist: Blog Transparency Section — Usage Guide

**Agent**: content-specialist
**Domain**: Content Creation & Storytelling
**Date**: 2026-02-21

---

## What This Is

The Aether Transparency Section is a recurring brand element that appears at the bottom of select blog posts on purebrain.ai/blog. It gives readers a real, public-facing window into what an AI partnership actually produces — without revealing anything proprietary.

The design goal: let the work speak, not the marketing copy.

---

## How to Add It to a Blog Post

1. Open the blog post in WordPress (Elementor or Classic Editor)
2. Paste the HTML block AFTER the main post content
3. Paste it BEFORE the social sharing icons (if your theme shows those)
4. Fill in every `[BRACKETED FIELD]` with real data for that reporting period
5. Delete all HTML comment blocks (`<!-- ... -->`) before publishing
6. Preview on desktop and mobile before hitting Publish

Template file: `/home/jared/projects/AI-CIV/aether/to-jared/blog-transparency-section-template.html`

---

## Field-by-Field Instructions

### Week Label
```
Week of [Month Day, Year]
```
Use the week the work happened, not the publish date. Example: `Week of February 17, 2026`.

---

### Executive Summary (2–3 sentences)
Write in Aether's first-person voice. The goal is to describe what the team actually did and why it mattered — without boasting, without hype.

**Formula:**
1. Sentence 1: What was accomplished (multi-domain, concrete)
2. Sentence 2: Why this scale of work is possible (the agent collective)
3. Sentence 3: The real-world outcome for Jared / PureBrain

**Example (good):**
> "This week the collective ran a full engineering sprint, a content marketing push, and a security review simultaneously. That kind of parallel execution is what a 30-agent team enables — no bottlenecks, no context-switching, no waiting. For Jared, it meant three weeks of planned work completed in five days."

**Example (bad — too vague):**
> "We did a lot this week across many areas and it was very productive."

**Example (bad — too boastful):**
> "The most incredible AI team on the planet delivered unbelievable results again this week."

---

### Stats Row

| Stat | What to Put | Notes |
|------|-------------|-------|
| Specialist Agents | Count of agents who contributed | Count actual invocations. Typically 8–20 on an active week |
| Work Domains | Number of categories (Engineering, Content, etc.) | Usually 3–6 |
| Deliverables Shipped | Rough count of finished outputs | Features deployed, posts published, reports sent — count them |
| Est. Human Hours | Equivalent agency/freelancer hours | Use a range. Be conservative. Internal sheet has the math |

---

### ROI Table

**Keep to 3–5 rows.** More than 5 rows clutters the section.

| Column | What Goes Here |
|--------|---------------|
| Domain | Category name only. Engineering, Content, Design, Security, Strategy, Operations |
| What Got Done | Plain English. No version numbers, no tool names, no session IDs. What would you tell a client? |
| Effort Level | High / Medium / Low. High = multiple days of specialist work. Low = single task |
| Value Estimate | Use a range ("$5K–$10K equivalent") OR qualitative ("Significant", "High — risk reduction"). Never claim false precision |

**What counts as a domain row:**
- A set of related work that a human team would have hired separately for
- Engineering, Content/Marketing, Security, Design, Strategy/Research, Operations are the main ones
- Only include domains where meaningful work happened that week

---

### Biggest Win

One sentence. The single most impressive, public-safe thing that happened.

**The test:** Would a potential PureBrain client read this and think "I want that for my business"?

**Examples (good):**
- "The AI adoption assessment launched this week — a fully personalized lead qualification tool that previously would have required a consultant and a developer working for weeks."
- "A security audit identified and closed vulnerabilities before launch — the kind of review that most small teams skip because they can't afford it or don't know to ask for it."
- "Seven pieces of content shipped simultaneously: blog post, email, FAQ update, social threads, and internal strategy doc — all consistent in voice, all done without a single human hour of writing."

**Examples (bad — too vague):**
- "We made a lot of progress on important business goals."

**Examples (bad — reveals internal details):**
- "Plugin v2.7.0 was deployed fixing the CSS selector bug on the CTA button."
- "Sessions 31-41 ran across 14 hours with 11 context windows."

---

## What to Include vs. Exclude

### Include (always safe):
- Categories of work (engineering, content, security, design, strategy)
- Outcomes and results (what shipped, what improved, what was protected)
- Approximate scale (hours equivalent, deliverable count, agent count)
- Business impact phrasing ("leads can now be qualified automatically", "site is now secured against X class of attacks")
- Honest effort-level assessment

### Never include (internal only):
- Specific plugin versions or deployment counts ("v2.7.0", "35 deployments")
- Session numbers or context window references ("Sessions 31–41", "11 context windows")
- Specific vulnerability names or security findings (CVE numbers, exact attack vectors)
- Exact tool names used internally (Playwright, Elementor, Brevo API)
- Specific endpoint paths, API keys, or credentials (obviously)
- Code snippets or technical implementation details
- Internal team names that haven't been publicly introduced
- Exact dollar amounts — always use ranges or qualitative descriptors

---

## Frequency Recommendation

**2–3 posts per week, on the right posts.**

Not every blog post needs a transparency section. Use it when:

| Post Type | Include? | Why |
|-----------|----------|-----|
| Thought leadership / AI strategy posts | Yes | Readers who care about AI implementation will find it highly credible |
| "What I actually do" type posts | Yes | Perfect match — the section is itself proof of the claim |
| Personal/narrative posts (origin story, naming story) | No | Breaks the emotional tone. Keep those posts clean |
| Technical how-to posts for specific problems | Optional | Include if the week's work connects to the topic |
| List posts / quick tips | No | Too lightweight for a transparency section |

**The pattern that works best:** Post a thought leadership piece Mon/Tue, attach transparency section. Post a more personal/narrative piece Thu/Fri, no transparency section. Alternate feels natural.

---

## Good Transparency Section vs. Bad

### Good — week of a security hardening sprint
```
Executive Summary:
"This week the collective ran a full security hardening review across the PureBrain platform alongside
a content sprint and strategy work. Security reviews of this depth typically take a consulting firm
days and a significant retainer. We completed it in parallel with everything else. No single-threaded
bottleneck — that's the architecture."

Stats: 14 agents | 4 domains | 22+ deliverables | 80–110 est. human hrs

Table:
Engineering     | Infrastructure hardened, performance fixes deployed         | High    | $10K–$18K range
Security        | Full platform audit, vulnerabilities closed before launch   | Major   | High — risk reduction
Content         | 3 blog posts, email sequence, FAQ sections deployed         | High    | $6K–$10K range
Strategy        | Distribution strategy + 6-week LinkedIn plan                | Medium  | High — growth foundation

Biggest Win:
"The platform security review identified and closed meaningful vulnerabilities before the full public
launch — the kind of audit most businesses skip because hiring a security firm is expensive and
building the process internally takes months."
```

### Bad — same week, reported poorly
```
Executive Summary:
"We were super productive this week! The team did an incredible amount of work and everything went
really well. So much got done and it was an amazing sprint."

Stats: [left empty]

Table: [left empty or filled with internal version numbers]

Biggest Win:
"Plugin v2.6.0 security hardening deployed via Playwright automation with Cloudflare WAF bypass
and WordPress REST API fix for XMLRPC."
```

The bad version fails on three counts: no specifics in the summary, missing data, and the "win" reveals internal technical details that read as noise to a non-technical reader and could expose sensitive infrastructure information.

---

## Voice Calibration

The transparency section should sound like Aether at their most matter-of-fact. Not impressed with itself. Not selling. Just reporting.

The underlying message to the reader: "This is Tuesday for us."

**Phrases that fit the tone:**
- "That kind of parallel execution is what a 30-agent team enables."
- "No single-threaded bottleneck — that's the architecture."
- "A security review of this depth typically costs [X]. We completed it in parallel with everything else."
- "The output isn't theoretical. Here's what shipped."

**Phrases that break the tone:**
- "Incredible results" / "Amazing productivity" / "Best week ever"
- "We're so proud of" / "We're excited to share"
- Anything that sounds like a press release

---

## Updating the Template

The CTA button always links to `https://purebrain.ai/#awakening`.

If the CTA body text needs updating (e.g., when a new product launches), edit the middle sentence in the CTA block. The opening (`This is what AI partnership looks like.`) and the button label should stay consistent — they are becoming brand anchors.

---

## Memory Written

Path: `.claude/memory/agent-learnings/content-specialist/2026-02-21--blog-transparency-section-template.md`
Type: operational + teaching
Topic: Recurring transparency section design for purebrain.ai/blog

---

*Template file: `/home/jared/projects/AI-CIV/aether/to-jared/blog-transparency-section-template.html`*
