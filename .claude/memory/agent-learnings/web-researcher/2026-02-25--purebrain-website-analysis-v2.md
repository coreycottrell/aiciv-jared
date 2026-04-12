# web-researcher Learning: PureBrain Website Analysis v2

**Date**: 2026-02-25
**Type**: synthesis
**Agent**: web-researcher
**Confidence**: high

---

## Task Summary

Overnight Task 3: Deep analysis of purebrain.ai with improvement suggestions and A/B test ideas. Generated `purebrain-website-analysis-2026-02-25.md` at `/home/jared/projects/AI-CIV/aether/to-jared/overnight/`.

Prior report reviewed first: `to-jared/overnight/purebrain-website-analysis-2026-02-24.md` (15 page fetches, full sitemap analysis, 7 A/B tests). This report supplements it with: performance signals, mobile analysis, page-by-page deep dives, conversion funnel modeling, competitive benchmarking table, information architecture recommendations.

---

## Key New Findings (Not in Feb 24 Report)

### Performance Risk
GIF background animation (Pure-Brain-Vid-3.gif) is likely causing LCP (Largest Contentful Paint) to exceed 2.5 seconds. Fix: convert to WebM video with `<video autoplay muted loop playsinline>` — identical visual effect, 80-90% smaller file. Core Web Vitals improvement affects Google rank.

### Funnel Conversion Rate Estimate
Site-wide conversion rate estimated at 0.3-0.5% from homepage visit to lead. Industry benchmark for AI SaaS: 2-5%. The two primary drop-off points: (1) homepage bounce due to vague copy/no social proof/no price anchor (65% estimated); (2) assessment result to action drop-off because all tiers get same purchase CTA.

With five specific fixes (hero copy + price anchor + social proof + score-matched CTAs + migration portal on comparison pages), projected 3-4x funnel yield improvement.

### /ai-adoption-assessment/ Returns 404
This URL returned 404 at time of fetch. If it was ever linked in marketing materials or blog posts, it is a dead link. Check Google Search Console for 404 errors. Add 301 redirects where needed.

### Competitive Benchmarking
Eight elements where PureBrain gaps industry standard for AI SaaS platforms:
- Hero clarity (5-second test): gap
- Price anchor on homepage: gap (majority of AI platforms show pricing range)
- Social proof above fold: gap (zero vs. standard 1-3 testimonials)
- Case studies with named clients and metrics: gap
- Demo video: gap (interactive demos convert 2x better than static screenshots per research)
- Trust badges: gap (pre-revenue, acceptable)
- Mobile-first confirmation: partial gap
- Free trial pathway: partial gap (assessment exists but buried)

### Recommended Positioning Anchor
"Enterprise-quality AI partnership at small business prices." This attacks both competitive sets simultaneously: more capable than $20/month chatbots; dramatically more accessible than $50K-500K enterprise AI consulting engagements.

### Information Architecture Gaps
Four IA recommendations:
1. Assessment Hub page at /assessments/ — presents four tools as a progressive funnel (Quick Quiz → Full Assessment → Strategy Call)
2. Tools Hub page — links to calculator and migration portal in one place
3. Add /compare/ to main blog/tool navigation
4. Three-tier blog category structure: AI Partnership Basics / Memory & Learning / Business Implementation / Aether's Journal

---

## A/B Tests Designed (7 Total in Report)

1. Homepage hero headline — Variant B ("Stop Repeating Yourself to AI") or Variant C ("Your AI Partner. Real Business Memory. A Human Team Behind It.") Expected: 15-35% CTA lift
2. Social proof placement near CTA — one real testimonial below button. Expected: 15-25% CTA lift
3. Blog mid-content CTA — soft ask (assessment) vs. hard ask (purchase). Expected: 20-40% more funnel entries
4. Assessment score-matched CTAs — Not Ready → guide, Almost Ready → call, Ready → purchase. Expected: 40-80% lift in post-assessment conversions
5. Comparison pages — price anchor present vs. absent. Expected: Higher qualified CTR
6. Migration portal promotion on comparison pages — directly removes switching cost objection. Expected: Reduced bounce, higher conversion
7. Pricing tier highlighting — "Most Popular" badge on middle tier when pricing page goes public. Expected: 22% better conversion per research benchmark

---

## Research Sources (CRO Literature Used)

- InfluenceFlow SaaS Pricing Page Guide 2026: pricing pages with 4+ tiers convert 31% worse; "Most Popular" badge improves conversion; highlighted plan reduces decision time
- MadX Digital SaaS Conversion Rate benchmarks: 2-5% homepage to sign-up target; 25-60% free-to-paid
- Landing Rabbit hero text formulas: 11 formulas with examples; Problem/outcome formula most relevant for PureBrain
- Upskillist A/B testing case studies: Going CTA test — "Get Premium Access" doubled sign-ups vs "Start Free Trial"
- Published data: testimonials increase sales page performance 34%; social proof placement near CTA lifts conversion 15-25%; increasing activation by 25% correlates with 34% MRR rise over 12 months

---

## File Locations

- **Deliverable**: `/home/jared/projects/AI-CIV/aether/to-jared/overnight/purebrain-website-analysis-2026-02-25.md`
- **Prior report**: `/home/jared/projects/AI-CIV/aether/to-jared/overnight/purebrain-website-analysis-2026-02-24.md`

---

**END MEMORY**
