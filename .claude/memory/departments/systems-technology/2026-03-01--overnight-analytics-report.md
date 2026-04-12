# dept-systems-technology: Overnight Analytics Report — Key Learnings
**Date**: 2026-03-01
**Type**: synthesis + data-state
**Topic**: Full analytics state of purebrain.ai as of Mar 1, 2026

---

## Data Points Confirmed

### Chatbox Engagement
- 468 unique sessions, Feb 10 – Mar 1 (20 days)
- 80% multi-turn engagement (industry avg: 30-40%)
- Week 8 peak: 323 sessions (8x jump from Week 7)
- 4-turn cluster: 126 sessions = onboarding flow completions
- All 468 sessions named (only 1 unknown session_id)

### Traffic (Server Logs)
- 208 unique external IPs in log server history
- Top external IPs: 108.35.12.204 (211 req), 89.167.19.20 (171 req)
- Most active day: Feb 25 (672 requests)
- Mar 1 at 408 requests by end of day

### Content
- 15 blog posts — all with OG image, schema, meta description (100% clean)
- 57 pages published, 34 in sitemap (23 correctly excluded as internal/test)
- 8 comparison pages in sitemap
- Daily blog publishing cadence (Feb 14 – Mar 1)

### Brevo / Email
- 33 total contacts, ~2-3 genuinely external humans
- 19 contacts have blank email (chatbox onboarding drop-offs)
- 6 Neural Feed campaigns sent (3 delivered each), 0% open rate
- Real external subscriber count: ~2

### Payment System
- 18 payment log events (16 test, 2 real webhooks but signature_verified: false)
- 362 pay test completions (all test flow)
- Interesting external emails: ryan@arcgroupus.com (11 tests), mthancock@gmail.com (15 tests), melanie@makrvf.com (21 tests) — potential warm leads

### Analytics Infrastructure
- GTM-WTDXL4VJ active on all pages
- GA4 G-86325WBT3P — active via GTM
- Clarity viy9bnc56x — active via GTM (NOT in inline HTML — GTM-loaded only)
- IAWP plugin active but REST API inaccessible programmatically
- Yoast v27 active, sitemaps healthy

### API Access Blockers
- GA4 Data API: needs OAuth2 service account from Jared
- GSC API: same service account works
- Clarity API: needs Microsoft OAuth from Jared
- IAWP: no accessible remote REST endpoint (WP admin dashboard has the data)
- PageSpeed: daily quota exhausted overnight (reset tomorrow)

## Key Actions Flagged for Jared
1. WP admin → IAWP dashboard → screenshot real traffic data
2. Google Search Console → verify property → submit sitemap
3. Google Cloud → service account → send JSON key to Aether
4. PayPal dashboard → confirm whether real payments exist
5. Reach out to ryan@arcgroupus.com (warm lead signal)

## Report Location
`/home/jared/projects/AI-CIV/aether/exports/overnight-analytics-report.md`

## Top Improvement Priority
GA4 service account is the highest-ROI 15-minute action Jared can take. Unlocks programmatic reporting on all real human traffic, bounce rates, top pages, traffic sources.
