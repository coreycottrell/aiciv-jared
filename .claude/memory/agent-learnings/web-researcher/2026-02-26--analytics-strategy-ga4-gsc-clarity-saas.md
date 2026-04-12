# Scientific Inquiry: Analytics Strategy for SaaS Subscriptions (GA4 + GSC + Clarity)

**Date**: 2026-02-26
**Question**: What is the complete analytics strategy for purebrain.ai using GA4, GSC, and Microsoft Clarity?
**Conclusion**: Comprehensive strategy delivered covering all three platforms with specific event names, funnel setups, audience segments, and review cadences.
**Confidence**: 4 (Strong — cross-validated from multiple authoritative sources, official documentation)

## Key Findings

### GA4 for SaaS
- Mark these as conversions: `signup_completed`, `assessment_completed`, `pricing_page_view`, `calculator_calculated`, `newsletter_signup`
- B2B SaaS buyers require 3–7 touches before converting — GA4 User Lifetime and Path Exploration reports reveal this
- Segment by: assessment abandoners, calculator users, pricing page visitors (no purchase), deep blog readers
- Link GA4 to Google Ads for remarketing — allow 24–48 hours for audience population
- Custom events naming: lowercase_underscores, under 40 characters, action verb first

### Google Search Console
- Queries in position 11–30 with high impressions = easiest ranking wins (update existing content)
- Queries with high impressions + CTR under 2% = rewrite meta titles/descriptions only
- Questions you rank for without a dedicated post = highest-priority new blog topics
- AI Overviews steal clicks — format content with Q as H2, direct 2-sentence answer immediately below
- IndexNow (already on purebrain.ai via plugin) = fastest indexing path for daily posts

### Microsoft Clarity
- Free, no sampling (100% of sessions captured)
- Semantic metrics: rage clicks, dead clicks, quick backs, excessive scrolling, JS errors
- Clarity + GA4 integration lets you filter GA4 audiences by Clarity behavior
- Funnels in Clarity are code-free — build assessment funnel and primary conversion funnel immediately
- WordPress + Elementor: install via official Clarity WordPress plugin; Elementor forms tracked via Conversion Bridge

### Cross-Platform Protocol
- Weekly 45-minute intelligence loop: GA4 numbers → GSC content gaps → Clarity session watch
- When conversion rate drops: GA4 identifies where in funnel, Clarity shows why, GSC shows if organic traffic caused it

## Specific Event Names Used in Report
- `assessment_started`, `assessment_question_completed`, `assessment_completed`, `assessment_result_cta_click`
- `calculator_loaded`, `calculator_calculated`, `calculator_cta_click`
- `blog_scroll_50`, `blog_scroll_90`, `blog_cta_click`, `newsletter_signup`
- `pricing_page_view`, `tier_selected`, `signup_form_started`, `signup_completed`
- `competitor_page_view`, `migration_quiz_started`

## Sources
- https://analytify.io/ga4-metrics-for-saas/
- https://analyzify.com/hub/ga4-guide-for-saas/
- https://martech.org/how-to-optimize-b2b-saas-user-journeys-with-ga4/
- https://learn.microsoft.com/en-us/clarity/insights/semantic-metrics
- https://learn.microsoft.com/en-us/clarity/setup-and-installation/funnels
- https://developers.google.com/search/docs/appearance/core-web-vitals
- https://analytify.io/google-search-console-for-keyword-research/

## Limitations
- PureBrain's actual current traffic volume unknown — KPI targets are best-practice starting points, not calibrated to current baseline
- GA4 audience minimum: 100 users required before Google Ads remarketing can activate
- Some GA4 features (predictive churn, lifetime value) require 28+ days of data to activate
