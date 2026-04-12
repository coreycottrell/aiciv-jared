# Analytics Stack Research: GA4 + GSC + Clarity for SaaS/Service Sites

**Date**: 2026-02-22
**Agent**: web-researcher
**Type**: synthesis
**Topic**: Complete analytics platform audit for purebrain.ai (GA4, Google Search Console, Microsoft Clarity)
**Confidence**: high (cross-validated from official documentation + practitioner guides)

---

## Context

Conducted comprehensive research to produce an analytics setup guide for purebrain.ai covering three platforms: Google Analytics 4, Google Search Console, and Microsoft Clarity. Focus on lead generation configuration (not e-commerce), conversion tracking, and behavioral analytics for a SaaS/AI service website.

---

## Key Findings

### GA4 Lead Generation Configuration (2026)

- GA4 now has **dedicated Lead Generation reports** (separate from E-Commerce) - enable via Library > Business Objectives > Generate Leads
- Six official lead events in funnel order: `generate_lead`, `qualify_lead`, `disqualify_lead`, `working_lead`, `close_convert_lead`, `close_unconvert_lead`
- **Eight audience templates** auto-created when Lead Gen reports enabled - ready for Google Ads remarketing
- For hybrid sites (lead gen + payment): use Lead Gen config as primary, add e-commerce `purchase` event as secondary
- Enhanced Measurement auto-tracks: scroll (90% threshold only), outbound clicks, page views, video engagement
- For multi-threshold scroll tracking (25/50/75/100%), must use GTM custom trigger
- Custom dimensions take up to 4 hours to populate after creation

### GA4 2026 Best Practices Shift

- **Server-side tagging** becoming standard for data accuracy (third-party cookie deprecation impact)
- **AI search visibility** creates dark traffic: users find you via AI summaries, trust you, then visit directly without organic click showing in GA4
- Solution: Monitor branded search volume in GSC as AI visibility proxy metric
- Quality over quantity: 15-25 well-defined events better than 50+ fuzzy ones
- Quarterly audit required - tracking breaks silently over time

### Google Search Console (2026 Updates)

- 2026 Core Web Vitals update: **INP threshold tightened from 200ms to 150ms** for "Good"
- New metric added: **SVT (Smooth Visual Transitions)** - measures jank in page transitions and late-loading elements
- Quick win formula: Position 4-10 keywords with >100 impressions = low-effort, high-return optimization targets
- High impressions + low CTR = metadata fix only (no content change needed, just title/description rewrite)
- Domain property (not URL Prefix) is the recommended setup - covers all variants automatically
- DNS TXT verification via Cloudflare is most durable verification method

### Microsoft Clarity (2026)

- **Completely free**: no traffic limits, no forced upgrades, all features available
- GDPR/CCPA compliant out of the box; auto-masks sensitive fields
- WordPress plugin: 1-click install, no code required
- Cannot capture Canvas or iFrame content (important for sites with embedded 3D/WebGL)
- GA4 integration enables "Watch Recording" link directly from GA4 user reports
- **Bot detection is ON by default** - properly excludes bot traffic from session counts
- Custom Tags (set via GTM or Clarity API) are essential for filtering recordings by page type
- Action threshold for rage clicks: if >5% of sessions on same element = UX problem, fix immediately

### Analytics Stack Integration Pattern

For maximum insight:
1. GSC (pre-click) → GA4 (post-click behavior) → Clarity (why they behaved that way)
2. GSC links to GA4 via Product links in GA4 Admin
3. Clarity links to GA4 via Clarity Settings > Google Analytics
4. BigQuery export (GA4 + GSC data) → Looker Studio dashboard = full-picture reporting (P3 priority)

### Review Cadence That Works

- **Daily (5 min)**: Sessions, conversions, top source, GSC clicks, one Clarity alert
- **Weekly (15-20 min)**: WoW comparison, funnel drop-off, top content, 3-5 session recordings
- **Monthly (30 min)**: Traffic growth, conversion rate, content ROI, SEO health, UX health, next priorities

### Time Investment Reality Check

- GSC setup (Jared verification + Aether config): 1.5 hours total, 20 min Jared
- GA4 basic setup: 2 hours, 15 min Jared
- GA4 custom events via GTM: 3 additional hours, all Aether
- Clarity: 1 hour, 10 min Jared
- Ongoing: ~3.5 hours/month

---

## When to Apply

- Any analytics setup task for purebrain.ai or future client sites
- When debugging conversion funnel problems (GSC + GA4 + Clarity triangle)
- When identifying SEO quick wins (position 4-10 keyword filter)
- When PureBrain site performance questions arise (Core Web Vitals 2026 thresholds)
- When scoping analytics work for Jared - this research defines what requires him vs what Aether can handle

---

## Sources

- [GA4 Best Practices 2026](https://www.measuremarketing.pro/post/ga4-best-practices-2026)
- [GA4 for SaaS Complete Guide](https://www.polymersearch.com/google-analytics-4-ultimate-guide/chapter-9-google-analytics-4-for-saas-digital-products-complete-guide)
- [GA4 Lead Gen Reports 2025](https://www.northern.co/blog/new-ga4-lead-generation-reports-explained-smarter-way-track-leads/)
- [GA4 Goals and AI Search 2026](https://www.analyticsmates.com/post/ga4-goals-2026-ai-search-signals)
- [GA4 Conversion Tracking 2026](https://influenceflow.io/resources/google-analytics-4-conversion-tracking-complete-guide-for-2026/)
- [GA4 Recommended Events](https://developers.google.com/analytics/devguides/collection/ga4/reference/events)
- [GSC Guide 2026](https://agencydashboard.io/blog/google-search-console-seo)
- [Core Web Vitals 2026 Update](https://www.wirefarm.com/googles-2026-core-web-vitals-update-what-it-means-for-your-business-website.html)
- [Core Web Vitals Official](https://developers.google.com/search/docs/appearance/core-web-vitals)
- [Microsoft Clarity Setup](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-setup)
- [Microsoft Clarity Review](https://www.invespcro.com/blog/microsoft-clarity-review/)
- [Clarity WordPress Plugin](https://wordpress.org/plugins/microsoft-clarity/)
- [GA4 Scroll Depth Tracking](https://www.heatmap.com/blog/ga4-scroll-depth)
- [GA4 Custom Dimensions Guide](https://www.analyticsmania.com/post/a-guide-to-custom-dimensions-in-google-analytics-4/)

## Deliverable

Full audit report at: `/home/jared/projects/AI-CIV/aether/exports/overnight-content/analytics-audit-2026-02-21.md`
