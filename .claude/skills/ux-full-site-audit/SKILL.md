---
name: ux-full-site-audit
version: 1.0.0
category: quality
description: Systematic UX/accessibility audit methodology for web properties using WCAG 2.1 AA, competitive benchmarking, and Impact x Effort prioritization
author: Aether Collective
date: 2026-05-20
tags: [ux, accessibility, wcag, audit, conversion, web]
agents: [ux-specialist, browser-vision-tester, feature-designer]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# UX Full-Site Audit

## Purpose

Conduct a comprehensive UX, accessibility, and conversion audit of a web property. Produces a prioritized issue list (Critical/High/Medium/Low) using Impact x Effort matrix.

## When to Use

- Before a major redesign or relaunch
- After shipping significant new pages/features
- Quarterly site health check
- When conversion rates drop or bounce rates spike
- When evaluating competitive positioning

## Audit Scope (8 Dimensions)

### 1. Visual Design & Information Architecture

- Page hierarchy (H1 → H6 structure)
- Content density and whitespace
- Visual flow and eye tracking patterns
- Consistency across pages (colors, fonts, spacing)
- Brand alignment (logo, colors, typography match brand guide)

### 2. Conversion Friction Analysis

- Form field count (each field beyond 3 costs ~10-15% completion)
- CTA clarity and placement (above fold, contrast ratio)
- Pricing page comprehension (feature grids vs abstract tiers)
- Trust signals (testimonials, security badges, social proof)
- Funnel drop-off points (where do users abandon?)

### 3. Accessibility (WCAG 2.1 AA)

Checklist:
- [ ] Color contrast ≥ 4.5:1 for normal text, ≥ 3:1 for large text
- [ ] All images have meaningful alt text
- [ ] Form inputs have associated labels
- [ ] Focus indicators visible on keyboard navigation
- [ ] Skip navigation link present
- [ ] ARIA landmarks (header, main, nav, footer)
- [ ] No content conveyed by color alone
- [ ] Touch targets ≥ 44x44px on mobile

### 4. Mobile Experience

- Responsive breakpoints (320px, 768px, 1024px, 1440px)
- Touch target sizes (minimum 44x44px)
- Horizontal scroll issues
- Font readability at mobile sizes (≥ 16px body)
- Input zoom prevention (font-size ≥ 16px on inputs)

### 5. Performance Impact

- HTML payload size (target <100KB)
- Inline CSS extraction opportunities
- Image optimization (WebP, lazy loading)
- Core Web Vitals estimation (LCP, FID, CLS)
- Third-party script blocking

### 6. Content Quality

- Hero messaging clarity (what it does in <5 seconds)
- Value proposition specificity (not abstract philosophy)
- Microcopy quality (button text, error messages, empty states)
- Reading level appropriateness for target audience

### 7. Navigation & Site Structure

- Information architecture depth (max 3 clicks to any content)
- Navigation labeling clarity
- Breadcrumbs on deep pages
- Search functionality (if >20 pages)
- 404 page usefulness

### 8. Competitive Benchmarking

- Identify 3 closest competitors
- Compare: pricing page format, hero messaging, feature presentation
- Note patterns all competitors share (industry standard)
- Identify differentiation opportunities

## Prioritization: Impact x Effort Matrix

```
         HIGH IMPACT
              |
    QUICK     |     BIG
    WINS      |     BETS
              |
LOW --------- + --------- HIGH
    EFFORT    |     EFFORT
              |
    FILL-INS  |     MONEY
              |     PITS
         LOW IMPACT
```

### Severity Levels

| Level | Criteria | Timeline |
|-------|----------|----------|
| P1 CRITICAL | Blocks conversion or violates accessibility law | Fix this sprint |
| P2 HIGH | Significant friction or brand inconsistency | Fix within 2 weeks |
| P3 MEDIUM | Suboptimal but functional | Backlog for next cycle |
| P4 LOW | Nice-to-have improvements | Opportunistic |

## Output Format

```markdown
# UX Audit: [Site Name] — [Date]

## Executive Summary
- Overall score: X/10
- Critical issues: N
- High issues: N
- Accessibility violations: N

## P1 CRITICAL Issues
### 1. [Issue Title]
- **What**: Description of the problem
- **Impact**: How it affects users/conversion
- **Fix**: Specific recommendation
- **Effort**: Low/Medium/High

## P2 HIGH Issues
[Same format]

## Competitive Comparison
| Feature | Us | Competitor A | Competitor B |
[comparison table]

## Methodology
- Tools used
- Pages audited
- Standards referenced
```

## Tooling

- **File analysis**: Read tool on HTML/CSS files (primary method)
- **Visual testing**: browser-vision-tester for screenshot comparison
- **Accessibility**: axe-core via browser, or manual WCAG checklist
- **Performance**: Lighthouse scores (if available)
- **Competitive**: web-researcher for competitor site analysis

## Gotchas

1. **Read-only audit**: Never modify production files during audit. Produce recommendations only.
2. **Avoid scope creep**: Audit first, then prioritize, then fix. Don't fix mid-audit.
3. **Test real user paths**: Follow the actual conversion funnel, not just individual pages.
4. **Mobile-first**: Start audit from mobile viewport, then expand to desktop.
5. **Prior audit diff**: Check for regressions from previous audits before starting fresh.

## Cross-CIV Value

Any civilization with a web presence can use this methodology. The 8-dimension framework and Impact x Effort prioritization are universal.
