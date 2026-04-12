# Analytics Implementation Guide - Comprehensive Research

**Date**: 2026-02-24
**Agent**: web-researcher
**Type**: synthesis
**Topic**: Complete GA4 + GSC + Clarity implementation guide for B2B lead generation site (PureBrain.ai)
**Confidence**: high (cross-validated from official docs, practitioner guides, February 2026 sources)

---

## Context

Produced a comprehensive "how to use the tools" analytics guide as distinct from the prior "site audit" reports. This covers GA4 lead funnel configuration, GSC query strategy, Clarity session recording methodology, the unified stack workflow, a weekly review checklist, quick wins, and Month 2-3 advanced tactics.

---

## Key New Findings (Not in Prior Memory)

### GA4 Lead Generation System (Underused Feature)

- GA4 has a DEDICATED lead generation report collection that must be manually enabled: Admin > Reports Library > Lead Generation > Publish
- Six official lead event names in exact sequence: `generate_lead`, `qualify_lead`, `disqualify_lead`, `working_lead`, `close_convert_lead`, `close_unconvert_lead`
- Using these exact names (not custom names) auto-populates 8 audience templates, ready for Google Ads remarketing immediately
- Data retention MUST be changed from 2 months to 14 months in Admin > Data Settings immediately or historical data is lost permanently

### GA4 Predictive Audiences (Month 2-3 Unlock)

- Predictive audiences require 1,000+ users with conversion events in last 28 days to activate
- "Likely 7-day purchasers" and "Likely 7-day churners" are the most valuable for B2B
- Available in GA4 Audiences once threshold is met - no additional setup required

### GSC AI Visibility Proxy Metric (2026 Specific)

- Google AI Overviews now generate "dark traffic" - users see PureBrain in AI answers, trust it, then search brand name directly
- Proxy metric: branded search volume in GSC (queries containing "PureBrain") growing faster than direct traffic in GA4 = AI visibility growing
- Track this monthly starting from week 4 of indexing

### Clarity Custom Tags for Segmented Analysis

- Clarity Custom Tags enable instant filtering of heatmaps and recordings by page type
- Implementation: GTM Custom HTML tag calling `window.clarity("set", "page_type", "value")` with URL trigger
- Tags to create: assessment, blog, product, comparison

### Clarity Conversion Heatmap (Advanced Feature 2026)

- Clarity recently added Conversion Heatmap showing which elements users clicked before converting vs. not converting
- Shows causation not just correlation - highest-value real estate on page
- Requires conversion events to be flowing for 4+ weeks before useful data appears

### GA4-Clarity Integration Setup (Step-by-Step)

1. Clarity Settings > Setup > Google Analytics > Link > Enter GA4 Measurement ID
2. GA4 Admin > Custom Definitions > Custom Dimensions > New: name="Clarity Session URL", scope=Event, parameter=clarityid
3. Wait 4 hours, then GA4 reports show clickable session recording links
- Known limitation: does not support GA4 custom segments; each Clarity project links to ONE GA4 property only

### BigQuery Export for Advanced Analysis

- GA4 free tier includes daily BigQuery export to Google Cloud
- Unlocks: multi-session path analysis, cohort analysis by channel, revenue attribution across months
- Setup: GA4 Admin > Product Links > BigQuery Links

---

## Weekly Review Protocol (Established)

**Weekly (20 min, Monday morning)**:
- GA4 (10 min): WoW comparison, top traffic source, conversion events, top pages, anomalies
- GSC (5 min): clicks trend, quick win queries (4-10 position with 100+ impressions), coverage errors, Core Web Vitals changes
- Clarity (5 min): rage click rate, any page above 5% rage clicks, 3 filtered recordings

**Monthly (60 min)**:
- GA4: conversion rate by source, funnel visualization, audience size, attribution model check
- GSC: impression growth, new queries, gaining/losing positions, Core Web Vitals, rich results errors
- Clarity: site-wide heatmap comparison, 10 recording review, mobile vs. desktop comparison

---

## PureBrain-Specific Custom Events to Implement

Priority 1 (conversion events): assessment_started, assessment_completed, generate_lead, chat_initiated, payment_initiated, purchase

Priority 2 (engagement): blog_scroll_depth (25/50/75/100%), cta_clicked, calculator_used, migration_started, comparison_page_engaged

Priority 3 (capture): newsletter_subscribed, audit_requested

All implemented via GTM-WTDXL4VJ (already confirmed on site). Test each with GTM Preview + GA4 DebugView.

---

## Deliverable

Full implementation guide at: `/home/jared/projects/AI-CIV/aether/to-jared/overnight/analytics-deep-dive-2026-02-24.md`

---

## When to Apply

- Any analytics setup or optimization task for purebrain.ai or future client sites
- When advising on conversion funnel problems (use the GA4 > Clarity workflow described here)
- When setting up custom events for any B2B lead gen site (event taxonomy is transferable)
- When client asks about weekly analytics process (the checklist here is a complete framework)

---

## Sources

- GA4 Lead Generation Reports: https://www.northern.co/blog/new-ga4-lead-generation-reports-explained-smarter-way-track-leads/
- GA4 Cross-Channel 2026: https://www.y77.ai/blogs/ga4-cross-channel-conversion-tracking-2026-setup-guide
- Clarity User Behavior 2026: https://www.bounteous.com/insights/2026/02/11/microsoft-clarity-understanding-user-behavior-beyond-numbers/
- GSC Complete Guide 2026: https://seohq.github.io/google-search-console-guide
- GA4 Actionable Insights 2026: https://almcorp.com/blog/google-analytics-actionable-insights-complete-guide-2026/
- Clarity-GA4 Integration: https://learn.microsoft.com/en-us/clarity/ga-integration/ga4-integration
