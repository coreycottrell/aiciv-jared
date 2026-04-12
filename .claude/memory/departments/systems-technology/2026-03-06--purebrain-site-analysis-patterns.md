# PureBrain.ai Site Analysis — Key Patterns
**Date**: 2026-03-06
**Type**: synthesis | audit
**Topic**: Comprehensive site analysis findings and recurring patterns

## Site Inventory (as of 2026-03-06)
- 47 indexed pages, 21 blog posts, 13 competitor comparison pages
- Pricing: Awakened $149 / Partnered $499 / Unified $999
- Tier detail pages exist for Partnered and Unified but NOT Awakened — gap to fill
- 4 separate assessment pages exist — should consolidate to 1

## Critical Issues Found
1. robots.txt is fully open — /wp-admin/ and /wp-login.php not blocked
2. 3 password-protected proposal pages (hunden, php-pos, bloomberg) are in sitemap — should be noindexed
3. /video-test/ is in sitemap — dev page that should be noindexed
4. Pricing tiers not visible on homepage — only "from $149/month" in meta description

## Conversion Gaps
- No risk-reversal (no trial, no guarantee) anywhere on site
- No testimonials visible on homepage or pricing page
- Pricing page (/invitation/) uses "invite-only" framing which may deter intent-driven traffic
- /compare/ page has no pricing shown — visitors comparing want cost info
- 3 slightly different CTA variants: "Awaken Your PURE BRAIN", "Begin Your AI Partnership", "Start Your AI Partnership"

## SEO Strengths
- Yoast SEO v27.1.1 properly configured
- 5-sitemap structure all updated current date
- Strong blog narrative around AI memory and partnership
- 13 comparison pages covering major competitors
- Meta description includes price anchor ($149/month) — good

## A/B Tests Proposed
1. Homepage CTA copy: "Awaken Your PURE BRAIN" vs "See All Plans — From $149/mo"
2. Pricing page framing: Invitation exclusivity vs direct pricing vs trial offer
3. Blog post mid-content CTA at 40% scroll point
4. Social proof on /invitation/ pricing page
5. Assessment page consolidation (4 → 1 canonical URL)

## Top Priority Actions
- robots.txt update (security)
- Pricing tier names on homepage (conversion)
- Noindex dev/proposal pages (SEO cleanup)
- Social proof on pricing page (conversion)
- Assessment page consolidation (SEO + conversion)

## Report File
`/home/jared/projects/AI-CIV/aether/exports/purebrain-site-analysis-2026-03-06.md`
