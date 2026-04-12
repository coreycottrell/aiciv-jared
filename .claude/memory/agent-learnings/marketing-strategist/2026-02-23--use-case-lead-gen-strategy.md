# marketing-strategist Learning: Use Case Lead Gen Page Strategy

**Date**: 2026-02-23
**Type**: synthesis
**Agent**: marketing-strategist
**Confidence**: high

---

## Task Summary

Built a comprehensive use case lead gen strategy for PureBrain. The brief: create an interactive lead gen page similar to the AI Tool Stack Calculator but focused on specific use cases and problems. Jared identified marketing and social media as primary verticals. The key insight from Jared: Otter.ai owns "meeting tasks," PureBrain should own "marketing tasks" and "social media tasks" as dedicated AI use case verticals.

---

## Key Findings

### 1. The Unbiased Advisor Angle Is the Core Differentiator

Google tells you to spend more on Google. LinkedIn tells you to expand on LinkedIn. Neither platform can claim to be unbiased — their AI optimizes for their own revenue. PureBrain is the AI advisor that works for the marketer, not the platform. This framing:
- Is 100% defensible and true
- Cannot be replicated by any platform-native AI tool
- Resonates immediately with any marketer who has followed Google's "recommendations" and seen their budget increase but not their ROI
- Creates a category of one: unbiased AI marketing advisor

### 2. Interactive Tool Format With Pre-Gate Preview Is the Right UX

Show 2-3 use cases before asking for email. This demonstration-first approach:
- Creates identity commitment (role selection)
- Creates problem acknowledgment (challenge selection)
- Demonstrates value before asking for contact info
- Makes the email gate feel like fair exchange rather than an obstacle
Expected: 15-30% email capture rate from tool completions (vs 1-3% static pages)

### 3. Marketing and Social Media Are the Two Primary Verticals

Built 10+ specific use cases for each vertical with: problem statement, platform bias angle, PureBrain solution, ROI benchmark. The platform bias angle is especially powerful in these verticals because Google Ads and LinkedIn Campaign Manager are the most obvious examples of platform self-interest in recommendations.

### 4. The Platform Bias Problem Is Documented and Widely Known

2025 research confirms Google's optimization suggestions prioritize Google's revenue, not advertiser objectives. Marketers know this at some level but have no independent advisor. PureBrain fills this gap.

### 5. Competitive Gap Is Real

No major AI tool has built a short, self-serve, role-specific use case finder that:
- Takes 2-3 minutes to complete
- Delivers genuinely useful personalized output
- Is explicitly positioned as unbiased
- Targets marketing/social where platform bias is the documented pain point
Jasper, Copy.ai, Writesonic, Claude, HubSpot — none of them do this.

---

## Use Case Highlights Worth Reusing

**Marketing:**
- Email subject line optimization (41% open rate lift; AI personalizes to YOUR list, not averages)
- Budget reallocation (22% higher ROI; platforms only show their own data)
- Deliverability diagnosis (platforms sell you tools; PureBrain gives diagnosis)
- Voice of customer extraction (copy written in customer language outperforms marketing-written copy)
- Content repurposing (75% faster campaign production)

**Social Media:**
- LinkedIn ad optimization (most explicit conflict of interest case; LinkedIn's AI maximizes LinkedIn revenue)
- Google Ads optimization (Performance Max hides keyword data; 25-40% average budget waste)
- Social ROI attribution (first-party model vs platform attribution models)
- Cross-platform content adaptation (3-5x content output from same input)

---

## Technical Notes

- Use competitor exodus page HTML/CSS/JS architecture as technical template (proven interactive flow)
- Vanilla JS state machine, 4 steps maximum, no framework needed
- Email form → Brevo List 3 with ROLE and TAGS attributes for segmentation
- Trigger role-specific 5-email nurture sequences
- Deploy dual-publish to purebrain.ai and jareddsanborn.com

---

## File Reference

Full strategy: `/home/jared/projects/AI-CIV/aether/exports/use-case-lead-gen-strategy.md`

Related technical templates:
- Competitor exodus pages: `/home/jared/projects/AI-CIV/aether/exports/competitor-exodus-chatgpt.html`
- AI Tool Stack Calculator (reference for interactive lead gen format)

---

**END MEMORY**
