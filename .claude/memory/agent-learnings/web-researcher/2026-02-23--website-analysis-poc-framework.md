# Website Analysis POC Framework

**Date**: 2026-02-23
**Agent**: web-researcher
**Type**: technique
**Topic**: Comprehensive website analysis methodology for client marketing product
**Confidence**: high

---

## Context

Conducted first proof-of-concept analysis for the website analysis business Jared is building. Analyzed two test sites:
1. A-C-Gee blog post (sageandweaver-network.netlify.app) - content site
2. DuckDive (duckdive-aiciv.netlify.app) - commercial landing page

---

## Framework That Worked

**6-dimension analysis structure**:
1. First Impressions and UX/UI (visual design, navigation, mobile, UX flow, CTAs)
2. Marketing Analysis (value prop, target audience, content quality, brand, conversion elements, social proof)
3. SEO Analysis (title, meta description, headings, OG tags, schema, internal linking)
4. Technical Analysis (SSL, response codes, HTML quality, page speed, accessibility, analytics)
5. Business Overview (what/who/model, strengths, weaknesses, competitive positioning)
6. Recommendations (5 quick wins, 5 strategic, priority ranking)

**Parallel fetch strategy**: Fetch both sites simultaneously, then do follow-up deep-dive fetches for:
- Parent organization context (who owns this site?)
- Missing technical details (FAQ full text, pricing tables, team bios)
- Competitive landscape

Typically 4-6 WebFetch calls per site for comprehensive coverage.

---

## Key Findings from This Analysis

**Common gaps found in both sites**:
- No meta descriptions
- No Open Graph tags (social share cards blank)
- No analytics tracking
- Missing schema/structured data

**DuckDive critical blockers**:
- Stripe links in test mode (payments would fail)
- Forms log to console.log instead of capturing leads
- No analytics at all

**A-C-Gee blog strength**:
- Exceptional content quality (9/10)
- But zero conversion infrastructure (CTAs, newsletter, social share)

---

## Scoring Template

Use this scoring matrix for client reports:

| Dimension | Score |
|-----------|-------|
| Visual Design | /10 |
| UX / Navigation | /10 |
| Value Proposition | /10 |
| Content Quality | /10 |
| CTAs / Conversion | /10 |
| Social Proof | /10 |
| SEO Infrastructure | /10 |
| Technical Health | /10 |
| Analytics Presence | /10 |
| Production Readiness | /10 |
| **Overall** | **/10** |

---

## What Future Analysis Should Add

For a premium tier offering:
- Google PageSpeed Insights API (Core Web Vitals)
- Ahrefs/SEMrush keyword data (requires API access)
- Browser screenshot capability for visual confirmation
- WCAG 2.1 accessibility audit
- Competitor keyword gap analysis

---

## When to Apply

- Any website analysis request for clients or internal projects
- POC demonstrations showing the value of structured analysis
- Competitive research on competitor sites

---

## Sources

- Sites analyzed: https://sageandweaver-network.netlify.app/acgee-blog/posts/2026-02-22-quack.html
- Sites analyzed: https://duckdive-aiciv.netlify.app/
- Report saved to: /home/jared/projects/AI-CIV/aether/exports/client-marketing/website-analysis/reports/test-analysis-2026-02-23.md
