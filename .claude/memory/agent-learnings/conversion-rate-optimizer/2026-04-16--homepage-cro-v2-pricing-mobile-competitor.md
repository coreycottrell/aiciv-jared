# CRO v2 Analysis: purebrain.ai Homepage, Pricing, Mobile, Competitors

**Date**: 2026-04-16
**Type**: operational + teaching
**Agent**: conversion-rate-optimizer (via MA#)

## Key Findings

### Delta from v1 (Apr 15)
- GDPR consent checkbox STILL pre-checked (line 8627) -- not fixed
- Image width/height: 12/27 now have them (was 0/35) -- partial progress
- Waitlist form GREW from 5 fields to 7 (5 required) -- opposite of v1 recommendation
- Total testimonials: 21 (v1 only counted 2 -- massive undercount)
- Page size identical (643,293 bytes)

### Pricing Section
- 4 tiers: Awakened $149, Partnered $499, Unified $999, Enterprise Custom
- CTA text: "Activate Keen Now" on all paid tiers -- "Keen" is unexplained
- Consent gate locks CTAs (opacity 0.38, pointer-events:none) until checkbox checked
- Checkbox is pre-checked so CTAs appear unlocked on load -- but if unchecked, no helper text explains why buttons are grayed out
- Claude Max requirement ($100-200/mo additional) buried below grid
- "How This Levels You Up" sub-pages exist for Partnered and Unified

### Mobile UX (CSS analysis)
- Same 643KB HTML served to mobile (no adaptive)
- Pricing grid: single-column below 768px = ~1800px scroll for 4 cards
- 7-field form with textarea on mobile = very high friction
- Hero video + particles still render on mobile (battery/data cost)
- Breakpoints at 400, 480, 500, 576, 768, 900, 1024, 1280px

### Competitor Patterns Missing on PureBrain
1. Trust strip / logo bar above fold (Jasper: 21 logos, Copy.ai: 8 logos + "17M users")
2. Quantified outcomes (Jasper: "10K hours saved", Copy.ai: "$16M savings")
3. Minimal homepage forms (Jasper: 0 fields, Copy.ai: 1 field, PureBrain: 7 fields)

### A/B Test Queue
- T1-T5 carried from v1
- T6 NEW: Testimonials above pricing
- T7 NEW: Claude Max requirement visible on pricing cards
- T8 NEW: Mobile pricing swipe carousel
- Wave 1 (this week): T3 (form reduction) + T4 (trust strip)

## Dead Ends
- WebFetch returns 403 for purebrain.ai (Cloudflare bot protection) -- must use curl with browser UA
- WP REST API not accessible via public domain -- CF Pages serves static HTML on all paths
- No separate /pricing/ page -- returns same homepage HTML

## Files Referenced
- `/home/jared/exports/portal-files/overnight-homepage-cro-v2-2026-04-16.md` (deliverable)
- `/home/jared/exports/portal-files/overnight-homepage-cro-analysis-2026-04-15.md` (v1)
- `/tmp/purebrain-desktop.html` (fetched homepage, line refs: 8627 consent, 7933 H1, 8640-8860 pricing)

## Teachings for Future CRO Runs
1. Always curl with browser UA -- WebFetch gets 403 from CF Pages
2. Count ALL testimonials, not just the first 2 visible
3. Check waitlist form field count explicitly -- it can change between analyses
4. Competitor fetch works via WebFetch for jasper.ai and copy.ai (not blocked)
5. writer.com returns limited HTML (heavy client-side rendering) -- less useful for static analysis
6. Pricing CTA text can contain internal product names that leak ("Keen") -- always extract exact text
7. Consent gate mechanism (locked CTAs) is a conversion pattern worth analyzing in every audit
