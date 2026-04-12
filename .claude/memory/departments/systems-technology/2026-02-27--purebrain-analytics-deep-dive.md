# Analytics Deep Dive — purebrain.ai
**Date**: 2026-02-27
**Type**: synthesis
**Agent**: dept-systems-technology

## What Was Done
Full analytics audit of purebrain.ai across all accessible platforms.

## Key Findings (For Future Reference)

### Tracking IDs (Confirmed)
- GTM Container: GTM-WTDXL4VJ (via gtm4wp plugin)
- GA4 Measurement ID: G-86325WBT3P
- Microsoft Clarity ID: viy9bnc56x
- Google Site Verification: S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0

### Critical Gaps Found
1. GA4 has NO event tracking — only pageviews recording. No conversions configured.
2. All security headers missing — can be added via Cloudflare Transform Rules
3. 2 posts missing from blog index: /your-ai-has-no-memory-mine-does/ and /your-next-direct-report-wont-be-human/
4. 1 post missing meta description: /your-ai-has-no-memory-mine-does/
5. 3 posts have no tags: first-90-days, your-ai-has-no-memory, your-next-direct-report
6. 3 posts missing FAQ schema: first-90-days, your-ai-has-no-memory, we-both-wrote-this-post

### Email / Subscriber Status (Feb 27)
- External subscribers: 0 (all internal/test)
- Neural Feed list has 6 contacts — all team members
- Brevo automations configured but sending 0 emails (no audience yet)

### Chatbox Funnel (732 total sessions)
- Name capture rate: 92%
- Email capture rate: 31% (biggest funnel gap)
- Deep engagement (8+ msgs): 51%
- Real external prospects: Michael Hancock (mthancock@gmail.com, multi-firm attorney), Andrew Ryan (ryan@arcgroupus.com, ARC Group)

### Platform Access Constraints
- GA4 dashboard: requires Google OAuth — cannot automate
- Google Search Console: requires Google OAuth — cannot automate
- Microsoft Clarity: requires Microsoft OAuth — cannot automate
- All three have working tracking pixels confirmed via GTM inspection
- SEMRush: WORKS headlessly with Playwright (patterns in browser-vision-tester memory)
- Brevo: WORKS via REST API (BREVO_API_KEY in .env)
- WordPress: WORKS via REST API (Aether credentials in .env)

## Report Location
/home/jared/projects/AI-CIV/aether/to-jared/overnight-reports/analytics-deep-dive-2026-02-27.md

## Site Health Summary (Feb 27)
- Domain age: ~3 weeks old
- Authority Score: 0 (expected)
- Page speed: Excellent (0.2s average, Cloudflare caching all pages)
- Content depth: Exceptional (13 posts, avg 11,000 words each)
- SEMRush site health: 83%
- SEO technical foundation: Solid (HTTPS, sitemaps, canonicals all correct)
