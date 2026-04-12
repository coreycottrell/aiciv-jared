# marketing-strategist Learning: Newsletter Cross-Promotion System Build

**Date**: 2026-02-24
**Type**: synthesis + operational
**Agent**: marketing-strategist
**Task**: Built complete Newsletter Cross-Promotion System (Initiative 4 from 90-Day Growth Roadmap)

---

## What Was Built

Complete 6-file package at `/home/jared/projects/AI-CIV/aether/exports/newsletter-cross-promo/`:

1. `cross-promo-strategy.md` — Full campaign strategy, 3-tier partnership model, phase architecture, success metrics
2. `target-newsletters.md` — 25+ researched and scored newsletter targets with audience fit ratings, approachability scores, and contact research guidance
3. `swap-proposal-templates.md` — 5 templates (feature swap, shoutout swap, PKM audience, executive audience, follow-up) with subject line testing guide
4. `ad-copy-variants.md` — 5 full variants + 3 short-form variants that partners can paste directly into their newsletters
5. `tracking-system.md` — UTM parameters for all partners, GA4 setup, Brevo tagging instructions, partner performance spreadsheet structure
6. `onboarding-sequence.md` — 2-email cross-promo variant (Emails 1-2 modified, Emails 3-7 standard), Brevo implementation instructions, performance benchmarks

---

## Strategic Insights Captured

### The Three-Tier Partnership Model

**Feature Swap** (5K-100K subscriber newsletters): Write them content, they mention us
**Shoutout Swap** (2K-10K): Mutual paragraph-length recommendations
**Co-Created Campaigns** (established relationships only): Joint series/challenges

Key pattern: NEVER lead with the co-created campaign pitch. Always start smaller and earn trust first.

### The Aether Advantage

The most differentiated pitch available: offer Aether as the guest author, transparently disclosed as AI-written. This:
- Stands out in crowded newsletter writer inboxes
- Demonstrates the product instead of describing it
- Creates natural talking points for the partner writer
- Particularly resonates with PKM/productivity audiences who already understand the value of persistent systems

This angle should be the opening gambit with any newsletter that covers AI, PKM, productivity, or knowledge work. Save standard human-authored pitches for more conservative executive audiences.

### Audience Fit Hierarchy

Best cross-promo audience fits for Neural Feed (in order):

1. **PKM community** (Tiago Forte, Nick Milo, Notion/Obsidian): Pre-sold on persistent systems, highly likely to convert to PureBrain trial. Best guest piece angle: "What persistent AI memory changes about your Second Brain."
2. **AI-for-business newsletters** (AI Breakfast, Mindstream, The AI Report): Direct audience overlap, clearest pitch, easiest to explain the value
3. **Executive/C-suite newsletters**: Highest-value subscribers, slowest to convert, require proof-focused framing
4. **Productivity newsletters** (work smarter, GTD-adjacent): Mid-tier audience fit, good for volume
5. **Technical/developer newsletters**: Low fit, wrong audience for PureBrain's practical positioning

### The Critical Offer: Write Their Copy for Them

When asking for a mention in their newsletter, always offer: "I'll write the copy for you — you just approve it."

This removes the single biggest source of friction for newsletter writers agreeing to swaps. Most newsletter writers are time-constrained. Removing the writing work from their side dramatically increases yes rates.

### Onboarding Variant Psychology

Cross-promo subscribers arrive with different context than organic subscribers:
- They were sent by someone they trust (higher initial trust)
- They may not know PureBrain the product (only the newsletter)
- They are warmer but have a specific expectation set by the referring newsletter

The two-email cross-promo variant addresses this by:
- Email 1: Acknowledging the referring newsletter by name (leverages the referral trust)
- Email 2: Being honest about what Neural Feed is AND isn't (including suggesting alternatives if it's not what they needed)

The "permission to leave" pattern in Email 2 is counterintuitive but effective: readers who stay after being offered an exit are dramatically more engaged than those who stay by default.

---

## Key Technical Decisions

### UTM Parameter Structure

Extended the existing UTM master reference at `config/utm-reference.md` with:
- `utm_source = [partner-slug]` (unique per partner)
- `utm_medium = email`
- `utm_campaign = newsletter-swap`
- `utm_content = [mention-type]`

Partner slug convention: lowercase, hyphens, under 20 characters (e.g., `ai-breakfast`, `bens-bites`, `forte-bsb`)

### Brevo Tagging

Cross-promo subscribers should be tagged in Brevo with:
- `source:newsletter-swap`
- `partner:[partner-slug]`
- `onboarding:cross-promo`

The `onboarding:cross-promo` tag triggers separate automation with the variant Email 1+2, then merges into standard sequence at Email 3.

### Landing Page Variants

Dedicated landing page variants only for partners with 50K+ subscribers (and only AFTER swap is confirmed, not speculatively). Route all others to `purebrain.ai/#awakening` with UTM tracking.

---

## Source Documents Read

- `/home/jared/projects/AI-CIV/aether/docs/from-telegram/90-day-roadmap-months-2-3.md` — Initiative 4 details (lines 636-759)
- `/home/jared/projects/AI-CIV/aether/.claude/memory/pure-technology-knowledge-base.md` — PT/PMG identity, 7 Pillars, philosophy
- `/home/jared/projects/AI-CIV/aether/config/utm-reference.md` — Existing UTM master reference (extended, not duplicated)
- `content-specialist` memory files on Neural Feed voice, onboarding sequence, P.S. additions

---

## Patterns for Future Marketing Work

**Newsletter swap outreach timing**: Wave-based (5-7 per wave) rather than mass-send. Apply learnings from Wave 1 before Wave 2.

**Guest content pitch structure**: Leading with content offer before making the ask. "Here's what I'll give you" before "here's what I want."

**Relationship vs. transaction framing**: The follow-up email with data after a swap executes ("You sent us X subscribers — here's what we sent you") is the most underused step in newsletter partnerships. It converts one-time swaps into ongoing relationships.

**Cross-promo to conversion funnel**: Cross-promo subscribers → Neural Feed open rate target 60%+ (email 1) → standard welcome sequence from email 3 → trial conversion target 2-5% at 90 days.

---

## Output Files

All files at: `/home/jared/projects/AI-CIV/aether/exports/newsletter-cross-promo/`

```
exports/newsletter-cross-promo/
├── cross-promo-strategy.md
├── target-newsletters.md
├── swap-proposal-templates.md
├── ad-copy-variants.md
├── tracking-system.md
└── onboarding-sequence.md
```

---

**END MEMORY ENTRY**
