# AI Brain Score Lead Gen System - Complete Spec

**Date**: 2026-02-18
**Type**: synthesis
**Agent**: sales-specialist
**Confidence**: high

---

## Context

Designed a complete, immediately actionable lead generation system for PureBrain.ai. Task required something buildable in 1-2 days, specific, and based on what's working in 2026. Searched memory first - found the LinkedIn "Warm Circle" outbound system already existed (2026-02-17), so designed a differentiated INBOUND system.

## Key Design Decisions

### 1. Interactive Quiz vs Static Lead Magnet

Data point that drove this choice:
- Static PDF lead magnets: baseline opt-in rate
- Interactive quiz/tool: +27-34% higher opt-in rate (5,000-campaign study, 2025)
- Score = social currency = sharing motivation (unique viral mechanic)

**The quiz does what no PDF can: it makes you want to share your result.**

### 2. "AI Brain Score" Positioning

The name connects directly to PureBrain's "awaken" brand positioning:
- Quiz reveals what's dormant in them
- PureBrain awakens it
- Score (0-100) creates self-relevance and urgency
- 4 tiers (Dormant/Flickering/Activating/Awakened) map to PureBrain's language

### 3. Zero New Infrastructure Required

The entire system runs on:
- WordPress (existing) - quiz page
- Google Apps Script (proven pattern) - automation
- Google Sheets (existing) - lead database
- Telegram bot (tools/tg_send.sh already built) - Jared notifications
- Existing PDF (ai-partnership-readiness-assessment.pdf) - email incentive

**Cost to build: $0 in tools.**

### 4. 5 Questions, Not 20

Each question designed to:
(a) Surface a pain point PureBrain solves (context re-entry = 1-2 hrs/week lost)
(b) Create "that's exactly me" recognition
(c) Naturally qualify the lead (D answers = ready for PureBrain)

### 5. Dual CTA on Results Page

Primary: "Start your free awakening" → PureBrain (no friction)
Secondary: "Get my full AI Brain report" → Email capture (incentivized)
Share: Pre-written LinkedIn + Bluesky posts (viral loop)

## System Architecture (High Level)

```
Quiz (/score) → Results page → [CTA to PureBrain] OR [Email capture → PDF + 3-email sequence]
Distribution: LinkedIn (2 posts) + Bluesky + Homepage popup + Chat widget trigger
Automation: Google Apps Script → Sheet + PDF delivery + Telegram notification (51+ scores)
```

## Expected Outcomes (Month 1)

- 500-1,500 quiz completions
- 125-525 emails captured
- 50-150 PureBrain demo/trial requests
- Direct revenue: $396-$1,584 MRR from direct attribution (3% email-to-paid)

## Key Learning

**Diagnosis creates desire faster than any pitch.**

The quiz surfaces the "context re-entry tax" (1-3 hours/week wasted) in the prospect's own words and numbers. By the time they see the PureBrain CTA, they've already told themselves why they need it. Zero selling required.

## Files Created

- `/home/jared/projects/AI-CIV/aether/exports/lead-gen-system-2026-02-18.md` - Complete system spec

## Differentiation from Warm Circle System (2026-02-17)

| Dimension | Warm Circle (LinkedIn) | AI Brain Score |
|-----------|------------------------|----------------|
| Direction | Outbound | Inbound |
| Time investment | 45 min/day ongoing | 2 days to build, then passive |
| Lead quality | Very high (manually warmed) | High (self-qualified by quiz) |
| Scale | Limited by Jared's time | Unlimited (automated) |
| Viral potential | Low | High (share your score) |

**Run both systems simultaneously. They serve different lead pools.**

---

*Second sales-specialist memory entry. System optimized for passive lead generation with existing infrastructure.*
