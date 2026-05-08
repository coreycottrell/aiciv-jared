# SEO Analytics Deep Dive — Overnight Task 9
**Date**: 2026-05-08
**Type**: operational + pattern + gotcha
**Topic**: GA4 + GSC live data, Clarity gap, conversion funnel diagnosis

## Access Confirmed
- GA4 + GSC: WORKING via service account. Tool: `tools/analytics_api.py`. Property 525007539, site `sc-domain:purebrain.ai`.
- Clarity: NO server-side API exists. Always document this — repeated rediscovery is a waste. Project ID `viy9bnc56x` is live in GTM, data exists, but only via dashboard.

## Key findings (30d GA4)
- 3,903 sessions → 1 form_submit. Funnel break is severe — likely broken event or broken form.
- Mobile homepage bounce 77% vs desktop 64%. 13-pt gap.
- `(not set)` landing page: 136 sessions / 95.6% bounce / 2s dwell. Likely redirect or staging leak.
- Direct = 73% of traffic. No organic non-branded clicks at all.
- Pakistan + Germany = ~246 sessions of likely bot/VPN.

## Key findings (28d GSC)
- 100% of converting clicks are branded (`purebrain`, `pure brain`, `purebrain ai`).
- `/ai-tool-stack-calculator/`: 1,187 impressions, 0.2% CTR — ranking for irrelevant long-tail.
- Three blog pages with 116-623 impressions and ~0% CTR — title/meta rewrite opportunity.
- Sitemap: 132 URLs, 8 warnings, 0 errors, GSC reports `indexed: 0` (lag + warnings combo).

## Constitutional violation found
Homepage `og:image` = `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`. Violates the "no wp-content paths, absolute URLs only" og:image rule. Must replace with PNG at non-wp-content path.

## Pattern: Clarity dashboard-only
Don't waste time hunting for a Clarity REST API on every analytics task. It doesn't exist. Document the queries Jared should run himself, move on.

## Report
`exports/portal-files/overnight-task9-analytics-deep-dive-2026-05-08.md` (1,480 words)
