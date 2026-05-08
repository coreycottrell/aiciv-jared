# Analytics Audit — 2026-04-15

**Type**: Operational + Teaching
**Agent**: SEO Specialist
**Tools**: `tools/analytics_api.py` (GA4 + GSC), service account auth

## Key Findings

### GA4 (30 days)
- 2,902 sessions, 2,225 users, 65.2% bounce
- 78% direct traffic (likely untagged dark social + returning brand searchers)
- Investor pages are the hidden gem: `/investor-avatar` 29.5% bounce, 15:14 avg session
- `/blog` landing page bounces 95.5% at 3-second duration — broken CTA chain
- **No `form_submit`, `purchase`, `sign_up` events firing** — flying blind on funnel

### GSC (90 days)
- 120 clicks / 2,988 impressions / 4.01% CTR / pos 8.0
- Brand dominates: "purebrain" + "pure brain" = 50/120 clicks (42%)
- **Biggest fire**: `/age-of-ai-agents-next-18-months/` = 320 imp at pos 5.7, 0.3% CTR (title/meta rewrite = 30x lift opportunity)
- Mobile CTR 7.58% vs desktop 3.08% (2.5x) — mobile searchers ready to click
- **WordPress ghost**: 4 old WP sitemaps (www.purebrain.ai/category-, /post-, /sitemap_index, /page-sitemap) still submitted in GSC, erroring. Site is on CF Pages.

## Patterns to Remember

1. **`analytics_api.py` works** — don't rebuild. Import `ga4_report`, `gsc_query`, `gsc_list_sitemaps`, `ga4_parse_rows`, `gsc_parse_rows`.
2. **Service account at** `.credentials/google-drive-service-account.json` has GA4 + GSC scopes provisioned since 2026-03-03.
3. **Clarity is separate auth** — needs `CLARITY_API_TOKEN` in `.env`, Bearer token from Clarity project settings.
4. **Blog CTA source tagged `blog / cta`** has 96% bounce — investigation-worthy.
5. **LinkedIn dual UTM**: `linkedin / jared` (custom, 79% bounce) vs `linkedin.com / referral` (organic, 46% bounce) — Jared's UTM landing page is weaker than default.

## Dead Ends / Gotchas

- `landingPage` dimension returns `(not set)` and empty string for bot/unassigned traffic — treat as noise.
- GSC `ctr` field is decimal (0.157 = 15.7%), not percentage.
- GSC sitemap `indexed: '0'` is a reporting artifact for apex sitemap — real indexing is happening, Google just doesn't populate this field for non-WP sitemaps.

## Report Path

`/home/jared/exports/portal-files/overnight-analytics-insights-2026-04-15.md`
Raw JSON: `/tmp/analytics_raw_2026_04_15.json`

## Action Items Generated

1. Remove 4 WP sitemaps from GSC (keep apex only)
2. Rewrite title+meta: `/age-of-ai-agents-next-18-months/`, `/ai-tool-stack-calculator/`
3. Wire GA4 conversion events (ST# ticket needed)
4. Add Clarity Bearer token to `.env`
5. 301 www.purebrain.ai → apex
6. Audit `/blog` CTA destination
